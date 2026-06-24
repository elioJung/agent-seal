# Agent Notary — Task List

> 이 파일은 Claude가 CLAUDE.md를 기반으로 생성한다.
> 최초 생성: 2026-06-24

## 진행 중
_없음_

## 백로그

### 4단계 — 운영 배포 (Production)

> **의존성**: 3단계 개발 검증 완전 통과 후 진행한다.

#### 인프라 (담당: AGENT_BE)
- [ ] `docker-compose.prod.yml` 작성 — 볼륨 영속화, 헬스체크, restart 정책
- [ ] Nginx 서브도메인 라우팅 설정 (api.도메인, app.도메인)
- [ ] 운영 환경변수 분리 (`.env.prod`, 시크릿 관리)
- [ ] Oracle Free Tier 서버 SSH 배포 확인

#### GitHub Actions CI/CD (담당: AGENT_BE)
- [ ] `.github/workflows/deploy.yml` — main 브랜치 push 시 자동 배포
  - Docker 이미지 빌드 (ARM64 cross-compile)
  - Docker Hub 또는 GHCR 이미지 푸시
  - Oracle 서버 SSH → docker-compose pull & up
- [ ] GitHub Secrets 설정 문서화
  - `ORACLE_HOST`, `ORACLE_USER`, `ORACLE_SSH_KEY`
  - `DOCKER_USERNAME`, `DOCKER_TOKEN` (또는 `GHCR_TOKEN`)
  - 운영 환경변수 시크릿 목록

#### SDK (담당: AGENT_SDK)
- [ ] SDK `README.md` 작성 + PyPI 배포 준비 (`pip install notary-sdk`)

---

## 완료

### 3단계 — 개발 환경 검증 ✅ 2026-06-24

- [x] 전체 시나리오 수동 검증 — 가입 → API Key 발급 → SDK 트레이스 전송 → 대시보드 조회 → 증명서 발급 → 검증 URL 접근 (test_e2e.py + 수동 확인)
- [x] Langfuse 4.x 연동 데모 에이전트 실행 검증 — gpt-4o-mini 실제 호출 + Langfuse 트레이스 + Notary 공증 전체 플로우 확인

### 2단계 — 서비스 (기능 구현) — SDK ✅ 2026-06-24

- [x] LangGraph + Langfuse 4.x 연동 데모 에이전트 작성 (`examples/langfuse_agent/`)
- [x] `pip install -e ../../packages/sdk` 로컬 설치 검증

### 1단계 — 코어 (인프라 기반) ✅ 2026-06-24

- [x] 루트 `pyproject.toml` 작성 — Ruff + mypy 공통 설정 (담당: AGENT_BE)
- [x] `docker-compose.yml` 기본 뼈대 — db / redis / server / web (담당: AGENT_BE)
- [x] `.env.example` 작성 (담당: AGENT_BE)
- [x] FastAPI 프로젝트 구조 초기화 — `api/` `service/` `repository/` `worker/` (담당: AGENT_BE)
- [x] PostgreSQL 스키마 설계 및 Alembic 초기 마이그레이션 — users, api_keys, traces, certificates (담당: AGENT_BE)
- [x] Pydantic Settings 환경변수 관리 (담당: AGENT_BE)
- [x] API 라우터 뼈대 — auth / traces / certificates / verify (stub) (담당: AGENT_BE)
- [x] DB + Redis 연결 초기화 (lifespan) (담당: AGENT_BE)
- [x] `packages/sdk/` 구조 초기화 — types, client, wrapper, adapters (담당: AGENT_SDK)
- [x] NotaryWrapper 본체 구현 (invoke / ainvoke, fire & forget) (담당: AGENT_SDK)
- [x] Langfuse 어댑터 구현 (담당: AGENT_SDK)
- [x] Vite + React 18 + TypeScript 프로젝트 초기화 (담당: AGENT_FE)
- [x] Tailwind CSS 설정 (담당: AGENT_FE)
- [x] React Router 라우팅 설정 (담당: AGENT_FE)
- [x] API 클라이언트 레이어 + 타입 정의 (담당: AGENT_FE)

### 2단계 — 서비스 (기능 구현) ✅ 2026-06-24

#### Backend (packages/server)
- [x] 사용자 가입 엔드포인트 구현 — `POST /v1/auth/register` (담당: AGENT_BE)
- [x] 로그인 엔드포인트 구현 — `POST /v1/auth/login` (JWT 발급) (담당: AGENT_BE)
- [x] API Key 인증 미들웨어 구현 — DB 조회 + is_active 검증 (담당: AGENT_BE)
- [x] 트레이스 수신 구현 — API Key 검증 → SHA-256 해시 → Redis Streams 발행 (담당: AGENT_BE)
- [x] 공증 워커 구현 — Redis 큐 소비 → DB 저장 (비동기 백그라운드 태스크) (담당: AGENT_BE)
- [x] 트레이스 목록 조회 API 구현 — `GET /v1/traces` (페이지네이션) (담당: AGENT_BE)
- [x] 증명서 발급 API 구현 — `POST /v1/certificates/{trace_id}` (HMAC-SHA256 서명) (담당: AGENT_BE)
- [x] Verify API 구현 — `GET /v1/verify/{cert_id}` (인증 없이 공개) (담당: AGENT_BE)
- [x] bcrypt passlib→direct 교체 — bcrypt 4.x 호환성 수정 (담당: AGENT_BE)
- [x] Docker dev 환경 HMR 폴링 설정 (담당: AGENT_BE)

#### Frontend (packages/web)
- [x] 대시보드 페이지 — API Key 입력 폼 + TanStack Query로 트레이스 로그 목록 (담당: AGENT_FE)
- [x] 증명서 발급 UI — 행별 발급 버튼 + 결과 배너 (담당: AGENT_FE)
- [x] 검증 페이지 — UUID 기반 제3자 검증 결과 표시 (담당: AGENT_FE)
- [x] Vite 폴링 HMR 설정 (담당: AGENT_FE)

## 블로커
_아직 없음_
