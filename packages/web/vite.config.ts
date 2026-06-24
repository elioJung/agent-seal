import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/v1': {
        // Docker 네트워크 내에서 server 컨테이너로 프록시
        target: 'http://server:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://server:8000',
        changeOrigin: true,
      },
    },
  },
})
