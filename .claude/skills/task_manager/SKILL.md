# Skill: Task Manager

## 목적
모든 에이전트는 작업 시작 전, 진행 중, 완료 시 TASKS.md를 업데이트한다.
TASKS.md는 프로젝트의 단일 진실 공급원(Single Source of Truth)이다.

## 파일 경로
- TASKS.md: `.claude/TASKS.md`

## 규칙
1. 작업 시작 전 — TASKS.md를 읽고 다음 작업을 확인한다
2. 작업 시작 시 — 해당 항목을 "진행 중"으로 이동한다
3. 작업 완료 시 — 해당 항목을 "완료"로 이동하고 완료 날짜를 기록한다
4. 새 작업 발견 시 — 백로그에 추가한다
5. 블로커 발생 시 — 해당 항목에 🚧 표시 후 이유를 한 줄 기록한다

## 태스크 최초 생성
TASKS.md의 백로그가 비어있을 경우:
1. CLAUDE.md의 핵심 플로우와 기술 스택을 분석한다
2. 단계별(코어 / 서비스 / 배포)로 태스크를 도출한다
3. 각 태스크에 담당 에이전트(BE / FE / SDK)를 명시한다
4. 의존성이 있는 태스크는 순서를 고려해 정렬한다
5. 생성 후 사용자에게 확인을 요청한다

## TASKS.md 형식

```markdown
# Agent Notary — Task List

## 진행 중
- [ ] 작업명 (담당: AGENT_BE) (시작: YYYY-MM-DD)

## 백로그

### 1단계 — 코어
- [ ] 작업명

### 2단계 — 서비스
- [ ] 작업명

### 3단계 — 배포
- [ ] 작업명

## 완료
- [x] 작업명 (담당: AGENT_BE) (완료: YYYY-MM-DD)

## 블로커
- 🚧 작업명 — 이유
```

## 에이전트별 작업 범위
- AGENT_SDK: packages/sdk
- AGENT_BE: packages/server
- AGENT_FE: packages/web

## 호출 시점
모든 에이전트는 작업 전후로 반드시 이 스킬을 참조한다.