import { useParams } from 'react-router-dom'

export default function VerifyPage() {
  const { uuid } = useParams<{ uuid: string }>()

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="text-center space-y-3">
        <div className="text-3xl font-bold">증명서 검증</div>
        <p className="text-gray-400 font-mono text-sm break-all max-w-md">{uuid}</p>
        <p className="text-gray-600 text-sm">Phase 2 구현 예정</p>
      </div>
    </div>
  )
}
