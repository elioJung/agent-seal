"""
Langfuse + Agent Notary 연동 데모

LangGraph 에이전트를 실행하고 Langfuse 트레이스를 자동으로 Notary에 공증한다.

실행:
  cd examples/langfuse_agent
  pip install -r requirements.txt
  pip install -e ../../packages/sdk
  cp .env.example .env   # 키 입력 후
  python agent.py "AI 에이전트의 미래를 연구해줘"
  python agent.py "피타고라스 정리를 설명하고 3,4,5 삼각형의 빗변을 계산해줘" "수학 연구"
"""

import asyncio
import os
import sys
import time

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langgraph.prebuilt import create_react_agent

from notary_sdk import NotaryClient, TracePayload
from notary_sdk.adapters.langfuse import LangfuseAdapter

load_dotenv()

# ── 환경변수 로드 ──────────────────────────────────────────
LANGFUSE_PUBLIC_KEY = os.environ["LANGFUSE_PUBLIC_KEY"]
LANGFUSE_SECRET_KEY = os.environ["LANGFUSE_SECRET_KEY"]
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
NOTARY_API_KEY = os.environ["NOTARY_API_KEY"]
NOTARY_URL = os.getenv("NOTARY_URL", "http://localhost:8000")


# ── 도구 정의 ──────────────────────────────────────────────
@tool
def web_search(query: str) -> str:
    """Search the web for information on a topic."""
    # 데모용 Mock — 실제 환경에서는 Tavily/Serper 등으로 교체
    return (
        f"[검색 결과: '{query}']\n"
        "- 최신 연구에 따르면 이 분야는 빠르게 발전하고 있습니다.\n"
        "- 주요 동향: 멀티모달 AI, 자율 에이전트, 추론 모델의 부상.\n"
        "- 2026년 기준 산업 내 AI 도입률은 전년 대비 42% 증가했습니다."
    )


@tool
def calculate(expression: str) -> str:
    """Evaluate a safe mathematical expression. Example: '3**2 + 4**2'"""
    allowed = set("0123456789+-*/().**% ")
    if not all(c in allowed for c in expression):
        return "허용되지 않는 문자가 포함되어 있습니다."
    try:
        result = eval(expression, {"__builtins__": {}, "abs": abs, "round": round})
        return str(result)
    except Exception as e:
        return f"계산 오류: {e}"


# ── 에이전트 빌드 ───────────────────────────────────────────
llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    api_key=ANTHROPIC_API_KEY,
    temperature=0,
)
agent_graph = create_react_agent(llm, [web_search, calculate])


# ── Notary 전송 ─────────────────────────────────────────────
async def send_to_notary(langfuse_trace_id: str, agent_name: str) -> None:
    langfuse_client = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST,
    )

    print("  Langfuse API에서 트레이스 조회 중...")
    try:
        lf_trace = langfuse_client.get_trace(langfuse_trace_id)
    except Exception as e:
        print(f"  [!!] Langfuse 트레이스 조회 실패: {e}")
        return

    adapter = LangfuseAdapter()
    converted = adapter.convert(lf_trace)
    # agent_id는 LangGraph graph 이름 대신 사용자 지정값 사용
    converted["agent_id"] = agent_name

    notary_client = NotaryClient(api_key=NOTARY_API_KEY, server_url=NOTARY_URL)
    payload = TracePayload(agent_id=converted["agent_id"], data=converted["data"])
    await notary_client.send_trace(payload)


# ── 메인 실행 ───────────────────────────────────────────────
async def run(query: str, task_name: str | None = None) -> str:
    agent_name = task_name or "langfuse-demo-agent"
    session_id = f"demo-{int(time.time())}"

    langfuse_handler = CallbackHandler(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST,
        trace_name=agent_name,
        session_id=session_id,
        tags=["demo", "development", "notary"],
        user_id="dev-user",
        metadata={"env": "development", "notary_url": NOTARY_URL},
    )

    print(f"\n{'='*55}")
    print(f"  Agent: {agent_name}")
    print(f"  Query: {query[:60]}")
    print(f"{'='*55}")

    # 에이전트 실행
    print("\n[1/4] 에이전트 실행 중...")
    result = await agent_graph.ainvoke(
        {"messages": [HumanMessage(content=query)]},
        config={"callbacks": [langfuse_handler]},
    )
    output = result["messages"][-1].content
    print(f"  완료: {output[:120]}...")

    # Langfuse flush (비동기 전송 완료 대기)
    print("\n[2/4] Langfuse 트레이스 전송 중...")
    langfuse_handler.flush()
    await asyncio.sleep(3)  # Langfuse 서버 처리 대기

    trace_id = langfuse_handler.get_trace_id()
    if not trace_id:
        print("  [!!] Langfuse trace_id를 얻지 못했습니다. flush 후 재시도...")
        await asyncio.sleep(3)
        trace_id = langfuse_handler.get_trace_id()

    if trace_id:
        print(f"  Langfuse trace_id: {trace_id}")
        print(f"  Langfuse 대시보드: {LANGFUSE_HOST}/trace/{trace_id}")
    else:
        print("  [!!] trace_id 없음 — Notary 전송을 건너뜁니다.")
        return output

    # Notary로 공증 전송
    print("\n[3/4] Agent Notary로 공증 전송 중...")
    await asyncio.sleep(2)  # Langfuse API에 trace 반영 대기
    await send_to_notary(trace_id, agent_name)
    print("  전송 완료!")

    print(f"\n[4/4] 완료!")
    print(f"  Agent Notary 대시보드: {NOTARY_URL.replace('8000', '5173') if '8000' in NOTARY_URL else NOTARY_URL}")
    print(f"  API Key로 로그인 후 트레이스 및 증명서 확인 가능\n")

    return output


if __name__ == "__main__":
    _query = sys.argv[1] if len(sys.argv) > 1 else "AI 에이전트 기술의 현재 트렌드를 조사하고 핵심을 요약해줘"
    _task_name = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(run(_query, _task_name))
