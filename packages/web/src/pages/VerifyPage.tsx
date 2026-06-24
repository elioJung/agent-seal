import { useParams, Link } from 'react-router-dom'
import { useVerify } from '../hooks/useVerify'

export default function VerifyPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const { data, isLoading, error } = useVerify(uuid ?? '')

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center p-4">
      <div className="w-full max-w-xl">
        <div className="text-center mb-8">
          <Link to="/dashboard" className="text-sm text-gray-500 hover:text-white transition-colors">
            ← 대시보드
          </Link>
          <h1 className="text-3xl font-bold mt-4">증명서 검증</h1>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          {isLoading && (
            <div className="px-6 py-16 text-center text-gray-500 text-sm">검증 중…</div>
          )}

          {error && (
            <div className="px-6 py-16 text-center">
              <div className="text-4xl mb-4">✗</div>
              <p className="text-red-400 font-medium">증명서를 찾을 수 없습니다</p>
              <code className="block mt-3 text-xs text-gray-600 font-mono break-all">{uuid}</code>
            </div>
          )}

          {data && (
            <>
              <div className="px-6 py-5 border-b border-gray-800 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-green-900/40 border border-green-700 flex items-center justify-center text-green-400 text-sm">
                  ✓
                </div>
                <div>
                  <p className="font-medium text-green-400">유효한 증명서</p>
                  <p className="text-xs text-gray-500">
                    {new Date(data.certificate.issued_at).toLocaleString('ko-KR')} 발급
                  </p>
                </div>
              </div>

              <div className="px-6 py-5 space-y-4">
                <section>
                  <h3 className="text-xs text-gray-500 uppercase tracking-wider mb-3">
                    증명서
                  </h3>
                  <div className="space-y-2 text-xs font-mono">
                    <Row label="ID" value={data.certificate.id} />
                    <Row label="Hash" value={data.certificate.hash} />
                    <Row label="Signature" value={data.certificate.signature} truncate />
                  </div>
                </section>

                <div className="border-t border-gray-800" />

                <section>
                  <h3 className="text-xs text-gray-500 uppercase tracking-wider mb-3">
                    원본 트레이스
                  </h3>
                  <div className="space-y-2 text-xs font-mono">
                    <Row label="Trace ID" value={data.trace.id} />
                    <Row label="Agent" value={data.trace.agent_id} mono={false} />
                    <Row label="Hash" value={data.trace.hash} />
                    <Row
                      label="기록 시각"
                      value={new Date(data.trace.created_at).toLocaleString('ko-KR')}
                      mono={false}
                    />
                  </div>
                </section>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function Row({
  label,
  value,
  truncate = false,
  mono = true,
}: {
  label: string
  value: string
  truncate?: boolean
  mono?: boolean
}) {
  return (
    <div className="flex gap-3">
      <span className="text-gray-600 w-24 shrink-0">{label}</span>
      <span className={`break-all ${mono ? 'text-gray-300' : 'text-white'}`}>
        {truncate ? `${value.slice(0, 40)}…` : value}
      </span>
    </div>
  )
}
