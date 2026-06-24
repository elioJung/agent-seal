import { useParams, Link } from 'react-router-dom'
import { useVerify } from '../hooks/useVerify'

type Payload = {
  task_name?: string
  model?: string
  latency_ms?: number
  tags?: string[]
  session_id?: string
  user_id?: string
  langfuse_trace_id?: string
  usage?: {
    input_tokens?: number
    output_tokens?: number
    total_tokens?: number
    total_cost?: number
  }
  input?: string
  output?: string
}

export default function VerifyPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const { data, isLoading, error } = useVerify(uuid ?? '')

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-500 text-sm">검증 중…</p>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-5xl mb-4">✗</div>
          <p className="text-red-600 font-semibold text-lg">증명서를 찾을 수 없습니다</p>
          <code className="block mt-3 text-xs text-gray-400 font-mono break-all max-w-sm">{uuid}</code>
          <Link to="/dashboard" className="mt-6 inline-block text-sm text-indigo-600 hover:underline">
            ← 대시보드로 돌아가기
          </Link>
        </div>
      </div>
    )
  }

  const { certificate, trace } = data
  const payload: Payload = (trace as any).payload ?? {}
  const issuedAt = new Date(certificate.issued_at)
  const createdAt = new Date(trace.created_at)

  return (
    <div className="min-h-screen bg-gray-200 py-10 px-4 print:bg-white print:py-0">
      {/* Document */}
      <div className="max-w-2xl mx-auto bg-white shadow-2xl print:shadow-none">
        {/* Outer border */}
        <div className="p-8 border-4 border-gray-800 m-4">
          {/* Inner decorative border */}
          <div className="border border-amber-700/40 p-8">

            {/* Header */}
            <div className="text-center mb-8">
              <div className="flex justify-center items-center gap-3 mb-3">
                <div className="h-px flex-1 bg-gray-800" />
                <span className="text-3xl">⚖</span>
                <div className="h-px flex-1 bg-gray-800" />
              </div>
              <h1 className="text-2xl font-bold tracking-[0.3em] uppercase text-gray-900">
                Agent Notary
              </h1>
              <p className="text-xs tracking-[0.2em] text-gray-500 mt-1 uppercase">
                AI 에이전트 행동 공증 증명서
              </p>
              <div className="flex justify-center items-center gap-3 mt-3">
                <div className="h-px flex-1 bg-gray-800" />
                <div className="w-1.5 h-1.5 bg-gray-800 rotate-45" />
                <div className="h-px flex-1 bg-gray-800" />
              </div>
            </div>

            {/* Meta row */}
            <div className="flex justify-between text-xs text-gray-500 mb-8 px-1">
              <span>증명서 번호: <span className="font-mono text-gray-700">{certificate.id.slice(0, 18)}…</span></span>
              <span>발급일: <span className="text-gray-700">{issuedAt.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}</span></span>
            </div>

            {/* Intro text */}
            <p className="text-sm text-gray-600 text-center leading-relaxed mb-8 px-4">
              본 증명서는 아래 기재된 AI 에이전트의 행동이 명시된 시각에<br />
              변조 없이 기록되었음을 Agent Notary 시스템이 공증합니다.
            </p>

            {/* Agent Info */}
            <section className="mb-6">
              <h3 className="text-[10px] font-bold tracking-[0.25em] uppercase text-gray-400 border-b border-gray-200 pb-1 mb-3">
                에이전트 정보
              </h3>
              <table className="w-full text-sm">
                <tbody className="divide-y divide-gray-50">
                  <InfoRow label="에이전트 ID" value={trace.agent_id} mono />
                  {payload.task_name && <InfoRow label="작업명" value={payload.task_name} />}
                  <InfoRow
                    label="실행 시각"
                    value={createdAt.toLocaleString('ko-KR', {
                      year: 'numeric', month: 'long', day: 'numeric',
                      hour: '2-digit', minute: '2-digit', second: '2-digit',
                    })}
                  />
                  {payload.latency_ms != null && (
                    <InfoRow label="실행 시간" value={`${payload.latency_ms.toLocaleString()} ms`} />
                  )}
                  {payload.model && <InfoRow label="사용 모델" value={payload.model} mono />}
                  {payload.usage?.total_tokens != null && (
                    <InfoRow label="토큰 사용량" value={`${payload.usage.total_tokens.toLocaleString()} tokens`} />
                  )}
                  {payload.usage?.total_cost != null && (
                    <InfoRow label="비용" value={`$${payload.usage.total_cost.toFixed(6)}`} />
                  )}
                  {payload.session_id && <InfoRow label="세션 ID" value={payload.session_id} mono />}
                  {payload.user_id && <InfoRow label="사용자 ID" value={payload.user_id} />}
                  {payload.tags && payload.tags.length > 0 && (
                    <InfoRow label="태그" value={payload.tags.join(', ')} />
                  )}
                  {payload.langfuse_trace_id && (
                    <InfoRow label="Langfuse Trace" value={payload.langfuse_trace_id} mono />
                  )}
                </tbody>
              </table>
            </section>

            {/* Technical Proof */}
            <section className="mb-8">
              <h3 className="text-[10px] font-bold tracking-[0.25em] uppercase text-gray-400 border-b border-gray-200 pb-1 mb-3">
                검증 정보
              </h3>
              <table className="w-full text-sm">
                <tbody className="divide-y divide-gray-50">
                  <InfoRow label="트레이스 ID" value={trace.id} mono />
                  <InfoRow label="트레이스 해시" value={certificate.hash} mono />
                  <InfoRow label="전자 서명" value={`${certificate.signature.slice(0, 40)}…`} mono />
                </tbody>
              </table>
            </section>

            {/* Bottom: stamp + signature line */}
            <div className="flex justify-between items-end mt-4">
              {/* Signature line */}
              <div className="text-center">
                <div className="w-40 border-b border-gray-400 mb-1" />
                <p className="text-xs text-gray-400">Agent Notary 시스템</p>
              </div>

              {/* Valid stamp */}
              <div className="relative">
                <div className="w-24 h-24 rounded-full border-4 border-green-600 flex flex-col items-center justify-center text-green-600 rotate-[-12deg]">
                  <span className="text-2xl font-bold leading-none">✓</span>
                  <span className="text-[10px] font-bold tracking-widest mt-0.5">VALID</span>
                  <span className="text-[9px] tracking-wider">공증 완료</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-8 pt-4 border-t border-gray-200 text-center">
              <p className="text-[10px] text-gray-400 leading-relaxed">
                본 증명서는 Agent Notary 시스템에 의해 자동 발급되었습니다.<br />
                검증 URL: {window.location.href}
              </p>
            </div>

          </div>
        </div>
      </div>

      {/* Actions (hidden in print) */}
      <div className="max-w-2xl mx-auto mt-4 flex gap-3 justify-center print:hidden">
        <button
          onClick={() => window.print()}
          className="px-4 py-2 bg-gray-800 text-white text-sm rounded hover:bg-gray-700 transition-colors"
        >
          인쇄 / PDF 저장
        </button>
        <Link
          to="/dashboard"
          className="px-4 py-2 bg-white text-gray-700 text-sm rounded border border-gray-300 hover:bg-gray-50 transition-colors"
        >
          ← 대시보드
        </Link>
      </div>
    </div>
  )
}

function InfoRow({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <tr>
      <td className="py-1.5 pr-4 text-gray-500 text-xs w-32 shrink-0 align-top">{label}</td>
      <td className={`py-1.5 text-gray-800 break-all text-xs ${mono ? 'font-mono' : ''}`}>{value}</td>
    </tr>
  )
}
