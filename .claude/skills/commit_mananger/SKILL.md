# Skill: Commit Manager

## 목적
모든 에이전트는 작업 완료 시 일관된 커밋 컨벤션을 따른다.
Udacity Git Commit Message Style Guide를 기반으로 한다.

## 커밋 기준
- 기능 단위로 커밋한다 — 한 커밋은 하나의 논리적 변경만 포함
- 컴파일/테스트가 통과하는 상태에서만 커밋한다
- 여러 패키지에 걸친 변경은 패키지별로 나눠서 커밋한다

## 커밋 메시지 형식

```
<type>: <subject>

<body>

<footer>
```

### Type
- `feat` — 새로운 기능 추가
- `fix` — 버그 수정
- `docs` — 문서 변경
- `style` — 코드 포맷팅, 세미콜론 등 (로직 변경 없음)
- `refactor` — 리팩토링 (기능 변경 없음)
- `test` — 테스트 추가/수정
- `chore` — 빌드, 패키지 매니저 설정 등

### Subject
- 50자 이내
- 명령형 현재 시제 ("add" not "added" or "adds")
- 첫 글자 소문자
- 마침표 없음

### Body (선택)
- 72자에서 줄바꿈
- "어떻게"가 아니라 "무엇을, 왜"를 설명
- 본문과 제목은 빈 줄로 구분

### Footer (선택)
- 이슈 트래커 ID 참조: `Closes #123`
- Breaking change: `BREAKING CHANGE: ...`

## 예시

```
feat: add API key generation endpoint

implement POST /api/keys endpoint for issuing new API keys.
keys are generated using cryptographic random and stored as
hashed values in the database.

Closes #12
```

```
fix: prevent duplicate trace ingestion

trace ID was not being checked before insertion, causing
duplicates when SDK retried failed requests.
```

```
chore: add ruff and mypy to pre-commit
```

## 스코프 표기 (선택)
패키지 범위를 명시하고 싶을 때:

```
feat(sdk): add Langfuse adapter
fix(server): handle expired API keys correctly
docs(web): update README with setup instructions
```

## 작업 흐름
1. 작업 완료 후 변경 사항 확인 (`git status`, `git diff`)
2. 논리적 단위로 stage (`git add -p` 권장)
3. 커밋 메시지 작성 시 위 규칙 준수
4. TASKS.md 업데이트도 별도 커밋으로 분리: `docs: update TASKS.md`

## 파일 경로
- 이 스킬: `.claude/skills/COMMIT_MANAGER.md`