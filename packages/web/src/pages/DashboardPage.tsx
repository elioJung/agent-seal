export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="text-center space-y-4">
        <div className="text-5xl font-bold tracking-tight">Agent Notary</div>
        <p className="text-gray-400 text-lg">AI 에이전트 행동 공증 인프라</p>
        <div className="mt-8 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-900/40 border border-green-700 text-green-400 text-sm">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          서버 연결됨 — Phase 2 구현 예정
        </div>
      </div>
    </div>
  )
}
