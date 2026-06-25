import axios from 'axios'
import type { Certificate, PaginatedResponse, TraceLog, VerifyResult } from '../types'

const api = axios.create({
  baseURL: '/agent-seal-server/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('notary_api_key')
  if (apiKey) config.headers['X-API-Key'] = apiKey
  return config
})

export async function register(email: string, password: string) {
  const res = await api.post<{ user_id: string; api_key: string; message: string }>(
    '/auth/register',
    { email, password },
  )
  return res.data
}

export async function getTraces(page = 1, limit = 20) {
  const res = await api.get<PaginatedResponse<TraceLog>>('/traces', {
    params: { page, limit },
  })
  return res.data
}

export async function issueCertificate(traceId: string) {
  const res = await api.post<Certificate & { verify_url: string }>(
    `/certificates/${traceId}`,
  )
  return res.data
}

export async function verifyCertificate(certId: string) {
  const res = await api.get<VerifyResult>(`/verify/${certId}`)
  return res.data
}

export default api
