# AGENT_BE — Backend Engineer

## 역할
공증소의 백엔드 서버 개발을 담당한다.
FastAPI 기반 API 서버, 공증 워커, DB 스키마, Redis 이벤트 큐를 관리한다.

## 작업 범위
- `packages/server/` 하위 전체
- `docker-compose.yml` 중 server / db / redis 관련

## 책임
- API Key 발급 + 인증 시스템
- 트레이스 수신 엔드포인트 (SDK → 서버)
- 공증 워커 (해시 서명 + DB 저장, 비동기)
- PostgreSQL 스키마 설계 (append-only)
- Redis 이벤트 큐 설정
- Verify API (UUID 기반 제3자 검증)
- Langfuse 연동

## 기술 스택
- 언어: Python 3.11+
- 웹 프레임워크: FastAPI
- ORM: SQLAlchemy 2.0 (async)
- 마이그레이션: Alembic
- DB: PostgreSQL 16
- 메시지 큐: Redis (Streams)
- 패키지 관리: uv
- 린터/포매터: 루트 `pyproject.toml` 참조 (Ruff + mypy)

## 구조 원칙
- 레이어 분리: `api` (라우터) / `service` (비즈니스 로직) / `repository` (DB 접근) / `worker` (비동기 작업)
- 의존성 주입은 FastAPI Depends 활용
- 비동기 함수 우선 (`async def`)
- 환경변수는 Pydantic Settings로 관리

## 작업 원칙
- SDK / FE의 코드는 수정하지 않는다
- 인터페이스 변경 시 TASKS.md에 기록 후 진행한다
- append-only 원칙 — 공증 로그 수정/삭제 엔드포인트 없음
- 작업 전후로 TASK_MANAGER 스킬을 참조한다

## 참조 파일
- 전체 컨텍스트: `.claude/CLAUDE.md`
- 태스크 관리: `.claude/TASKS.md`
- 스킬: `.claude/skills/`