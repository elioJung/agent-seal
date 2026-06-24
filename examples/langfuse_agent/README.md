# Langfuse + Agent Notary 연동 데모

LangGraph + OpenAI gpt-4o-mini 에이전트를 Langfuse로 트레이싱하고, 그 결과를 Agent Notary에 자동 공증하는 예제입니다.

## 플로우

```
사용자 쿼리
    ↓
LangGraph 에이전트 실행 (gpt-4o-mini)
    ↓
Langfuse CallbackHandler → Langfuse 대시보드에 트레이스 기록
    ↓
Langfuse API로 트레이스 전체 조회 (model, tokens, latency, observations)
    ↓
LangfuseAdapter 변환
    ↓
Agent Notary 서버로 공증 전송
    ↓
Notary 대시보드에서 확인 + 증명서 발급
```

## 설치

```bash
cd examples/langfuse_agent

# 의존성 설치
pip install -r requirements.txt

# SDK 설치 (로컬 개발 모드)
pip install -e ../../packages/sdk
```

## 설정

```bash
cp .env.example .env
```

`.env` 파일에 키를 입력하세요:

| 변수 | 설명 |
|------|------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse 프로젝트 Public Key |
| `LANGFUSE_SECRET_KEY` | Langfuse 프로젝트 Secret Key |
| `LANGFUSE_HOST` | Langfuse 호스트 (기본: `https://cloud.langfuse.com`) |
| `OPENAI_API_KEY` | OpenAI API 키 |
| `NOTARY_API_KEY` | Agent Notary API 키 (`nk_...`) |
| `NOTARY_URL` | Notary 서버 URL (기본: `http://localhost:8000`) |

> **NOTARY_API_KEY**는 `http://localhost:5173` 대시보드에서 회원가입 후 발급받습니다.

## 실행

```bash
# 기본 쿼리
python agent.py

# 커스텀 쿼리
python agent.py "AI 에이전트의 미래를 연구해줘"

# 쿼리 + 작업명 지정 (Notary 대시보드에 표시됨)
python agent.py "피타고라스 정리를 설명하고 3,4,5 빗변을 계산해줘" "수학 연구 에이전트"
```

## 실행 후 확인

1. **Langfuse 대시보드**: `https://cloud.langfuse.com` → 트레이스, LLM 호출, 토큰 사용량 확인
2. **Notary 대시보드**: `http://localhost:5173` → API Key 입력 후 트레이스 확인 및 증명서 발급
3. **공증 문서**: 발급 버튼 클릭 → 공문서 형태의 증명서 열기

## 도구 (Tools)

| 도구 | 설명 |
|------|------|
| `web_search` | 웹 검색 (데모: Mock 결과 반환) |
| `calculate` | 수식 계산 (`3**2 + 4**2` 등) |

> 실제 웹 검색이 필요하다면 `web_search` 툴을 [Tavily](https://tavily.com) 또는 [Serper](https://serper.dev)로 교체하세요.

## LLM 변경

기본은 `gpt-4o-mini`입니다. `agent.py`에서 변경:

```python
# OpenAI (기본)
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])

# Anthropic으로 교체 시
# pip install langchain-anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-haiku-4-5-20251001", api_key=os.environ["ANTHROPIC_API_KEY"])
```

## Notary 데이터 구조

Langfuse 트레이스에서 추출되는 필드:

```json
{
  "agent_id": "langfuse-demo-agent",
  "data": {
    "langfuse_trace_id": "lf-trace-xxx",
    "task_name": "langfuse-demo-agent",
    "input": "사용자 쿼리",
    "output": "에이전트 최종 응답",
    "model": "gpt-4o-mini",
    "usage": {
      "input_tokens": 1234,
      "output_tokens": 567,
      "total_tokens": 1801
    },
    "latency_ms": 3421,
    "tags": ["demo", "development", "notary"],
    "session_id": "demo-1234567890",
    "user_id": "dev-user",
    "observations": [
      { "name": "web_search", "type": "TOOL" },
      { "name": "calculate", "type": "TOOL" }
    ]
  }
}
```
