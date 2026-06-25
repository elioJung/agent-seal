import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { register } from '../lib/api'
import { useTraces, useIssueCertificate } from '../hooks/useTraces'
import type { Certificate } from '../types'

export default function DashboardPage() {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('notary_api_key') || '')
  const [connected, setConnected] = useState(() => !!localStorage.getItem('notary_api_key'))
  const [inputKey, setInputKey] = useState('')
  const [mode, setMode] = useState<'connect' | 'register'>('connect')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [newKey, setNewKey] = useState('')
  const [issuedCert, setIssuedCert] = useState<(Certificate & { verify_url: string }) | null>(null)
  const [page, setPage] = useState(1)
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useTraces(page, connected)
  const issueMutation = useIssueCertificate()

  const registerMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      register(email, password),
    onSuccess: (data) => setNewKey(data.api_key),
  })

  const handleConnect = () => {
    if (!inputKey.trim()) return
    localStorage.setItem('notary_api_key', inputKey.trim())
    setApiKey(inputKey.trim())
    setConnected(true)
    queryClient.invalidateQueries()
  }

  const handleDisconnect = () => {
    localStorage.removeItem('notary_api_key')
    setApiKey('')
    setConnected(false)
    setInputKey('')
    setIssuedCert(null)
  }

  const handleIssue = async (traceId: string) => {
    try {
      const cert = await issueMutation.mutateAsync(traceId)
      setIssuedCert(cert)
    } catch (e: any) {
      alert(e?.response?.data?.detail || '증명서 발급 실패')
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).catch(() => {})
  }

  if (!connected) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold tracking-tight">Agent Notary</h1>
            <p className="mt-2 text-gray-400">AI 에이전트 행동 공증 인프라</p>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setMode('connect')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mode === 'connect'
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                API 키 입력
              </button>
              <button
                onClick={() => setMode('register')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mode === 'register'
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                새 계정 등록
              </button>
            </div>

            {mode === 'connect' ? (
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="nk_..."
                  value={inputKey}
                  onChange={(e) => setInputKey(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleConnect()}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm font-mono placeholder-gray-600 focus:outline-none focus:border-indigo-500"
                />
                <button
                  onClick={handleConnect}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-lg transition-colors"
                >
                  연결
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {newKey ? (
                  <div className="space-y-3">
                    <p className="text-sm text-yellow-400 font-medium">
                      ⚠️ API 키는 지금만 표시됩니다. 반드시 복사해두세요.
                    </p>
                    <div className="bg-gray-800 rounded-lg p-3 flex items-center gap-2">
                      <code className="flex-1 text-xs text-green-400 break-all">{newKey}</code>
                      <button
                        onClick={() => copyToClipboard(newKey)}
                        className="text-gray-400 hover:text-white text-xs shrink-0"
                      >
                        복사
                      </button>
                    </div>
                    <button
                      onClick={() => {
                        setInputKey(newKey)
                        setMode('connect')
                        setNewKey('')
                      }}
                      className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-lg transition-colors"
                    >
                      이 키로 연결하기
                    </button>
                  </div>
                ) : (
                  <>
                    <input
                      type="email"
                      placeholder="이메일"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500"
                    />
                    <input
                      type="password"
                      placeholder="비밀번호"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500"
                    />
                    <button
                      onClick={() => registerMutation.mutate({ email, password })}
                      disabled={registerMutation.isPending}
                      className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-3 rounded-lg transition-colors"
                    >
                      {registerMutation.isPending ? '등록 중...' : '등록'}
                    </button>
                    {registerMutation.isError && (
                      <p className="text-red-400 text-sm text-center">
                        {(registerMutation.error as any)?.response?.data?.detail || '등록 실패'}
                      </p>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">Agent Notary</h1>
          <span className="flex items-center gap-1.5 text-xs text-green-400 bg-green-900/30 border border-green-800 px-2.5 py-1 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            연결됨
          </span>
        </div>
        <div className="flex items-center gap-3">
          <code className="text-xs text-gray-500 font-mono">{apiKey.slice(0, 12)}…</code>
          <button
            onClick={handleDisconnect}
            className="text-xs text-gray-400 hover:text-white transition-colors"
          >
            연결 해제
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Issued cert banner */}
        {issuedCert && (
          <div className="mb-6 bg-green-900/20 border border-green-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-green-400 font-medium text-sm">✓ 증명서 발급 완료</span>
              <button
                onClick={() => setIssuedCert(null)}
                className="text-gray-500 hover:text-white text-xs"
              >
                닫기
              </button>
            </div>
            <div className="grid grid-cols-1 gap-1 text-xs font-mono text-gray-400">
              <div className="flex gap-2">
                <span className="text-gray-600 w-20 shrink-0">ID</span>
                <span className="text-white break-all">{issuedCert.id}</span>
              </div>
              <div className="flex gap-2">
                <span className="text-gray-600 w-20 shrink-0">Hash</span>
                <span className="break-all">{issuedCert.hash}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <a
                href={`${import.meta.env.BASE_URL}verify/${issuedCert.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-indigo-400 hover:text-indigo-300 underline underline-offset-2"
              >
                공증 문서 열기 →
              </a>
              <button
                onClick={() =>
                  copyToClipboard(`${window.location.origin}${import.meta.env.BASE_URL}verify/${issuedCert.id}`)
                }
                className="text-xs text-gray-500 hover:text-white"
              >
                URL 복사
              </button>
            </div>
          </div>
        )}

        {/* Traces table */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
            <h2 className="font-medium">트레이스 로그</h2>
            {data && (
              <span className="text-xs text-gray-500">
                총 {data.total}개
              </span>
            )}
          </div>

          {isLoading && (
            <div className="px-6 py-12 text-center text-gray-500 text-sm">불러오는 중…</div>
          )}

          {error && (
            <div className="px-6 py-12 text-center text-red-400 text-sm">
              {(error as any)?.response?.status === 401
                ? 'API 키가 올바르지 않습니다'
                : '데이터 로드 실패'}
            </div>
          )}

          {data && data.items.length === 0 && (
            <div className="px-6 py-12 text-center text-gray-500 text-sm">
              아직 수신된 트레이스가 없습니다
              <p className="mt-1 text-xs text-gray-600">
                SDK에서 NotaryWrapper를 통해 에이전트를 실행하면 여기에 표시됩니다
              </p>
            </div>
          )}

          {data && data.items.length > 0 && (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 border-b border-gray-800">
                  <th className="text-left px-6 py-3 font-medium">Agent / 작업</th>
                  <th className="text-left px-4 py-3 font-medium">모델 / 시간</th>
                  <th className="text-left px-4 py-3 font-medium">Hash</th>
                  <th className="text-left px-4 py-3 font-medium">생성 시간</th>
                  <th className="text-right px-6 py-3 font-medium">증명서</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((trace) => {
                  const payload = (trace as any).payload ?? {}
                  return (
                    <tr
                      key={trace.id}
                      className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <span className="text-indigo-400 font-mono text-xs">{trace.agent_id}</span>
                        {payload.task_name && (
                          <p className="text-gray-400 text-xs mt-0.5">{payload.task_name}</p>
                        )}
                        {payload.tags && payload.tags.length > 0 && (
                          <div className="flex gap-1 mt-1 flex-wrap">
                            {payload.tags.map((tag: string) => (
                              <span key={tag} className="text-[10px] bg-gray-800 text-gray-500 px-1.5 py-0.5 rounded">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-4 text-xs text-gray-500">
                        {payload.model && <p className="font-mono text-gray-300">{payload.model}</p>}
                        {payload.latency_ms != null && <p>{payload.latency_ms.toLocaleString()} ms</p>}
                        {payload.usage?.total_tokens != null && (
                          <p>{payload.usage.total_tokens.toLocaleString()} tokens</p>
                        )}
                      </td>
                      <td className="px-4 py-4">
                        <code className="text-xs text-gray-400 font-mono">
                          {trace.hash.slice(0, 14)}…
                        </code>
                      </td>
                      <td className="px-4 py-4 text-gray-500 text-xs">
                        {new Date(trace.created_at).toLocaleString('ko-KR')}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleIssue(trace.id)}
                          disabled={issueMutation.isPending}
                          className="text-xs bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-600/40 text-indigo-400 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                        >
                          발급
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}

          {/* Pagination */}
          {data && data.total > data.limit && (
            <div className="px-6 py-4 border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="hover:text-white disabled:opacity-30 transition-colors"
              >
                ← 이전
              </button>
              <span>
                {page} / {Math.ceil(data.total / data.limit)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(data.total / data.limit)}
                className="hover:text-white disabled:opacity-30 transition-colors"
              >
                다음 →
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
