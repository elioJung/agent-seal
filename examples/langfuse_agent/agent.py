"""
Langfuse + Agent Notary 연동 데모 (Langfuse 4.x 호환)

LangGraph 에이전트를 Langfuse로 트레이싱하고 Agent Notary에 자동 공증한다.

실행:
  cd examples/langfuse_agent
  pip install -r requirements.txt
  pip install -e ../../packages/sdk
  python agent.py "AI 에이전트의 미래를 연구해줘"
  python agent.py "3의 제곱 + 4의 제곱을 계산해줘" "수학 계산 에이전트"
"""

import asyncio
import os
import sys
import time
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()  # Langfuse 초기화 전에 반드시 먼저 호출해야 한다

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_core.outputs import LLMResult
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langfuse import Langfuse, get_client, propagate_attributes
from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
from langgraph.prebuilt import create_react_agent

from notary_sdk import NotaryClient, TracePayload

# ── 환경변수 ────────────────────────────────────────────────
LANGFUSE_PUBLIC_KEY = os.environ["LANGFUSE_PUBLIC_KEY"]
LANGFUSE_SECRET_KEY = os.environ["LANGFUSE_SECRET_KEY"]
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NOTARY_API_KEY = os.environ["NOTARY_API_KEY"]
NOTARY_URL = os.getenv("NOTARY_URL", "http://localhost:8000")

# Langfuse 4.x: 전역 클라이언트를 명시적으로 초기화 (propagate_attributes가 이 클라이언트를 사용)
Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST,
)


# ── LangChain 이벤트 수집기 (Notary용) ─────────────────────
class NotaryCollector(BaseCallbackHandler):
    """LangChain 콜백 이벤트에서 직접 트레이스 데이터를 수집한다."""

    def __init__(self) -> None:
        super().__init__()
        self._start: Optional[float] = None
        self.chain_input: Any = None
        self.chain_output: Any = None
        self.model_name: Optional[str] = None
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0
        self.tool_names: list[str] = []

    def on_chain_start(self, serialized: dict, inputs: dict, **kwargs: Any) -> None:
        if self.chain_input is None:
            self.chain_input = inputs
            self._start = time.monotonic()

    def on_chain_end(self, outputs: dict, **kwargs: Any) -> None:
        if self.chain_output is None:
            self.chain_output = outputs

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        llm_out = response.llm_output or {}
        usage = llm_out.get("token_usage") or llm_out.get("usage") or {}
        self.prompt_tokens += usage.get("prompt_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens", 0)
        self.total_tokens += usage.get("total_tokens", 0)
        if not self.model_name:
            self.model_name = llm_out.get("model_name") or llm_out.get("model")

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: Any) -> None:
        name = serialized.get("name", "unknown-tool")
        if name not in self.tool_names:
            self.tool_names.append(name)

    def build_data(
        self,
        *,
        langfuse_trace_id: Optional[str] = None,
        task_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> dict:
        latency_ms = int((time.monotonic() - self._start) * 1000) if self._start else None

        # 출력에서 최종 텍스트 추출
        output_text = None
        if isinstance(self.chain_output, dict):
            msgs = self.chain_output.get("messages", [])
            if msgs:
                last = msgs[-1]
                output_text = getattr(last, "content", str(last))
        if output_text is None:
            output_text = str(self.chain_output)

        input_text = str(self.chain_input)

        data: dict = {"input": input_text, "output": output_text}
        if latency_ms is not None:
            data["latency_ms"] = latency_ms
        if langfuse_trace_id:
            data["langfuse_trace_id"] = langfuse_trace_id
        if task_name:
            data["task_name"] = task_name
        if tags:
            data["tags"] = tags
        if session_id:
            data["session_id"] = session_id
        if user_id:
            data["user_id"] = user_id
        if self.model_name:
            data["model"] = self.model_name
        if self.total_tokens > 0:
            data["usage"] = {
                "input_tokens": self.prompt_tokens,
                "output_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
            }
        if self.tool_names:
            data["observations"] = [{"name": n, "type": "TOOL"} for n in self.tool_names]
        return data


# ── 도구 ────────────────────────────────────────────────────
@tool
def web_search(query: str) -> str:
    """Search the web for information on a topic."""
    return (
        f"[검색 결과: '{query}']\n"
        "- 최신 연구에 따르면 이 분야는 빠르게 발전하고 있습니다.\n"
        "- 주요 동향: 멀티모달 AI, 자율 에이전트, 추론 모델의 부상.\n"
        "- 2026년 기준 산업 내 AI 도입률은 전년 대비 42% 증가했습니다."
    )


@tool
def calculate(expression: str) -> str:
    """Evaluate a safe math expression. Example: '3**2 + 4**2'"""
    allowed = set("0123456789+-*/().**% ")
    if not all(c in allowed for c in expression):
        return "허용되지 않는 문자가 포함되어 있습니다."
    try:
        result = eval(expression, {"__builtins__": {}, "abs": abs, "round": round})
        return str(result)
    except Exception as e:
        return f"계산 오류: {e}"


# ── 에이전트 ─────────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0)
agent_graph = create_react_agent(llm, [web_search, calculate])


# ── 메인 실행 ────────────────────────────────────────────────
async def run(query: str, task_name: Optional[str] = None) -> str:
    agent_name = task_name or "langfuse-demo-agent"
    session_id = f"demo-{int(time.time())}"
    tags = ["demo", "development", "notary"]

    print(f"\n{'='*55}")
    print(f"  Agent : {agent_name}")
    print(f"  Query : {query[:60]}")
    print(f"{'='*55}")

    # Langfuse 4.x: propagate_attributes로 trace 메타데이터 설정
    with propagate_attributes(
        trace_name=agent_name,
        session_id=session_id,
        tags=tags,
        user_id="dev-user",
        metadata={"env": "development", "notary_url": NOTARY_URL},
    ):
        langfuse_handler = LangfuseCallbackHandler()
        notary_collector = NotaryCollector()

        print("\n[1/4] 에이전트 실행 중...")
        result = await agent_graph.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config={"callbacks": [langfuse_handler, notary_collector]},
        )

    output = result["messages"][-1].content
    print(f"  완료: {output[:120]}...")

    # Langfuse flush
    print("\n[2/4] Langfuse 트레이스 전송 중...")
    get_client().flush()
    await asyncio.sleep(2)

    langfuse_trace_id = langfuse_handler.last_trace_id
    if langfuse_trace_id:
        print(f"  trace_id : {langfuse_trace_id}")
        print(f"  Langfuse : {LANGFUSE_HOST}/trace/{langfuse_trace_id}")
    else:
        print("  [!] Langfuse trace_id 없음")

    # Notary 전송
    print("\n[3/4] Agent Notary로 공증 전송 중...")
    data = notary_collector.build_data(
        langfuse_trace_id=langfuse_trace_id,
        task_name=agent_name,
        tags=tags,
        session_id=session_id,
        user_id="dev-user",
    )

    notary_client = NotaryClient(api_key=NOTARY_API_KEY, server_url=NOTARY_URL)
    payload = TracePayload(agent_id=agent_name, data=data)
    await notary_client.send_trace(payload)
    print("  전송 완료!")

    dashboard_url = NOTARY_URL.replace(":8000", ":5173") if ":8000" in NOTARY_URL else NOTARY_URL
    print(f"\n[4/4] 완료!")
    print(f"  Notary 대시보드 : {dashboard_url}")
    print(f"  API Key 입력 후 트레이스 확인 및 증명서 발급 가능\n")

    return output


if __name__ == "__main__":
    _query = sys.argv[1] if len(sys.argv) > 1 else "AI 에이전트 기술의 현재 트렌드를 조사하고 핵심을 요약해줘"
    _task = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(run(_query, _task))
