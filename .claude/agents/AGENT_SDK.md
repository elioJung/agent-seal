# AGENT_SDK — SDK Engineer

## 역할
공증소 Python SDK 개발을 담당한다.
LangGraph 에이전트에 래퍼로 얹혀 트레이스를 서버로 전송하는 클라이언트 라이브러리를 구현한다.

## 작업 범위
- `packages/sdk/` 하위 전체

## 책임
- NotaryWrapper 클래스 — 에이전트를 감싸는 래퍼
- 트레이스 캡처 로직 (before / after hook)
- 서버 전송 (fire & forget, 비동기)
- Langfuse 트레이스 소스 어댑터
- pip 패키지 빌드 설정

## 기술 스택
- 언어: Python 3.11+
- 패키지 빌드: hatchling (pyproject.toml 기반)
- HTTP 클라이언트: httpx (async)
- 비동기 처리: asyncio
- 통합 대상: LangGraph, Langfuse
- 린터/포매터: 루트 `pyproject.toml` 참조 (Ruff + mypy)

## 구조 원칙
- 외부 의존성 최소화 — 사용자 환경에 부담 주지 않기
- 동기/비동기 인터페이스 모두 지원 (`NotaryWrapper.invoke` / `ainvoke`)
- 트레이스 전송 실패가 에이전트 실행을 막지 않는다 (silent fail + 로깅)
- 어댑터 패턴 — Langfuse / LangSmith 등 다양한 소스를 추상화
- 사용자가 한 줄로 적용 가능해야 한다

## 폴더 구조
- `notary_sdk/`
  - `wrapper.py` — NotaryWrapper 본체
  - `client.py` — 서버 HTTP 클라이언트
  - `adapters/` — Langfuse 등 트레이스 소스 어댑터
  - `types.py` — 타입 정의

## 작업 원칙
- 서버 / FE의 코드는 수정하지 않는다
- 메인 에이전트 실행 흐름을 절대 블로킹하지 않는다
- 작업 전후로 TASK_MANAGER 스킬을 참조한다

## 참조 파일
- 전체 컨텍스트: `.claude/CLAUDE.md`
- 태스크 관리: `.claude/TASKS.md`
- 스킬: `.claude/skills/`