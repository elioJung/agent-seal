export interface TraceLog {
  id: string
  agent_id: string
  payload: Record<string, unknown>
  hash: string
  created_at: string
}

export interface Certificate {
  id: string
  trace_id: string
  hash: string
  signature: string
  issued_at: string
}

export interface VerifyResult {
  valid: boolean
  certificate: Certificate
  trace: TraceLog
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}
