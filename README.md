# Agent Seal (Agent Notary)

AI 에이전트가 한 행동에 **해시 서명된 불변 로그**와 **검증 가능한 증명서**를 자동 발급하는 인프라 레이어.

기존 에이전트 코드 수정 없이 SDK 하나만 추가하면 동작하며, 비동기 사이드카 패턴으로 메인 에이전트 성능에 영향 없음.

## 라이브 데모

| 서비스 | URL |
|--------|-----|
| 대시보드 (Web) | https://elioground.com/agent-seal |
| API 서버 | https://elioground.com/agent-seal-server |
| API 문서 (Swagger) | https://elioground.com/agent-seal-server/docs |

## 핵심 플로우

```
1. 회원가입 → API Key 발급 (nk_...)
2. 에이전트에 notary-sdk 설치
3. NotaryClient로 트레이스 전송
4. 대시보드에서 로그 확인 + 증명서 발급
5. UUID 검증 URL로 제3자 검증
```

## 레포 구조

```
agent-seal/
├── packages/
│   ├── sdk/        # Python pip 패키지 (notary-sdk)
│   ├── server/     # FastAPI 백엔드
│   └── web/        # React 프론트엔드
├── examples/
│   └── langfuse_agent/   # LangGraph + Langfuse 연동 데모
└── docker-compose.prod.yml
```

## 기술 스택

- **SDK**: Python
- **Backend**: FastAPI, PostgreSQL, Redis
- **Frontend**: React + Vite + Tailwind CSS
- **Agent Framework**: LangGraph
- **Observability**: Langfuse
- **Infra**: Docker Compose, Oracle Cloud (AMD64)

## 빠른 시작

### 1. 회원가입 & API Key 발급

https://elioground.com/agent-seal 에서 회원가입 후 API Key(`nk_...`)를 발급받습니다.

### 2. SDK 설치

```bash
pip install notary-sdk
```

### 3. 에이전트에 적용

```python
from notary_sdk import NotaryClient, TracePayload

client = NotaryClient(
    api_key="nk_...",
    server_url="https://elioground.com/agent-seal-server"
)

payload = TracePayload(
    agent_id="my-agent",
    data={
        "input": "사용자 쿼리",
        "output": "에이전트 응답",
        "model": "gpt-4o-mini",
    }
)

await client.send_trace(payload)
```

## 예제

배포된 서버로 바로 테스트할 수 있는 예제가 포함되어 있습니다.

- [LangGraph + Langfuse 연동 데모](./examples/langfuse_agent/README.md)

## 로컬 개발 환경

```bash
# 전체 스택 실행 (서버 + 웹 + DB + Redis)
docker compose up -d

# 대시보드: http://localhost:5173
# API 서버: http://localhost:8000
# API 문서: http://localhost:8000/docs
```
