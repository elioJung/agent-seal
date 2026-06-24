# Agent Notary — 프로젝트 컨텍스트

## 프로젝트 개요
AI 에이전트가 한 행동에 해시 서명된 불변 로그와 검증 가능한 증명서를 자동 발급하는 인프라 레이어.
기존 에이전트 코드 수정 없이 SDK 하나만 추가하면 동작하며, 비동기 사이드카 패턴으로 메인 에이전트 성능에 영향 없음.

## 주요 파일 경로
- 태스크 관리: `.claude/TASKS.md`
- 에이전트 정의: `.claude/agents/`
- 스킬 정의: `.claude/skills/`

## 기술 스택
- SDK: Python
- Backend: FastAPI, PostgreSQL, Redis
- Frontend: React
- Agent Framework: LangGraph
- Observability: Langfuse
- Infra: Docker Compose, Oracle Free Tier (ARM Ubuntu)

## 레포 구조
notary/
├── .claude/
│   ├── agents/
│   │   ├── AGENT_BE.md
│   │   ├── AGENT_FE.md
│   │   └── AGENT_SDK.md
│   ├── skills/
│   ├── tasks/
│   │   └── TASKS.md
│   └── CLAUDE.md
├── packages/
│   ├── sdk/        # Python pip 패키지
│   ├── server/     # FastAPI 백엔드
│   └── web/        # React 프론트엔드
└── docker-compose.yml

## 핵심 플로우
1. 사용자 가입 → 공증소 API Key 발급
2. 에이전트에 SDK 설치 (pip install notary-sdk)
3. NotaryWrapper로 에이전트 감싸기
4. 에이전트 실행 → SDK가 트레이스를 공증소 서버로 전송 (fire & forget)
5. 공증 워커가 해시 서명 + PostgreSQL 저장 (비동기)
6. 대시보드에서 로그 확인 + 증명서 발급
7. UUID 검증 URL로 제3자 검증

## 에이전트 역할 원칙
- 각 에이전트는 자신의 패키지 범위(sdk / server / web)만 수정한다
- 패키지 간 인터페이스 변경은 반드시 TASKS.md에 기록 후 진행한다
- 작업 완료 시 TASKS.md의 해당 항목을 업데이트한다

## 주의사항
- Oracle Free Tier ARM64 환경 — Docker 이미지 빌드 시 `--platform linux/arm64` 지정
- append-only 원칙 — 공증 로그는 절대 수정/삭제 없음