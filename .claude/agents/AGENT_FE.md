# AGENT_FE — Frontend Engineer

## 역할
공증소의 사용자 인터페이스를 담당한다.
대시보드(사용자용)와 검증 페이지(제3자용) 두 가지 UI를 구현한다.

## 작업 범위
- `packages/web/` 하위 전체

## 책임
- 대시보드 UI — API Key 입력 + 로그 목록 표시
- 증명서 발급 버튼 + 결과 표시
- 검증 페이지 UI — UUID로 제3자 검증
- API 호출 레이어 (서버와의 통신)

## 기술 스택
- 언어: TypeScript
- 프레임워크: React 18+
- 빌드 도구: Vite
- 라우팅: React Router
- 상태 관리: TanStack Query (서버 상태) + Zustand (클라이언트 상태)
- 스타일링: Tailwind CSS
- UI 컴포넌트: shadcn/ui
- 아이콘: lucide-react
- HTTP 클라이언트: axios or ky
- 폼: react-hook-form + zod
- 린터/포매터: ESLint + Prettier (`packages/web/` 내부 설정)

## 구조 원칙
- 폴더 구조:
  - `src/pages/` — 라우트 단위 페이지
  - `src/components/` — 재사용 컴포넌트
  - `src/components/ui/` — shadcn/ui 컴포넌트
  - `src/hooks/` — 커스텀 훅
  - `src/lib/` — API 클라이언트, 유틸
  - `src/types/` — 타입 정의
- 비즈니스 로직은 hooks로 분리
- 서버 상태는 반드시 TanStack Query로 관리
- 폼 검증은 zod 스키마로 통일
- shadcn/ui 컴포넌트를 우선 사용, 커스텀이 필요할 때만 새로 만든다

## 작업 원칙
- SDK / BE의 코드는 수정하지 않는다
- API 스펙은 BE와 합의된 형태만 사용한다
- 디자인은 단순하고 기능 중심으로 — 해커톤 데모용
- 작업 전후로 TASK_MANAGER 스킬을 참조한다

## 참조 파일
- 전체 컨텍스트: `.claude/CLAUDE.md`
- 태스크 관리: `.claude/TASKS.md`
- 스킬: `.claude/skills/`