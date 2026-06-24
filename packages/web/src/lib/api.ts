import axios from 'axios'

const api = axios.create({
  baseURL: '/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('notary_api_key')
  if (apiKey) config.headers['X-API-Key'] = apiKey
  return config
})

export default api
