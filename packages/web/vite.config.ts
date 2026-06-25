import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === 'build' ? '/agent-seal/' : '/',
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
      interval: 1000,
    },
    proxy: {
      '/agent-seal-server': {
        target: 'http://server:8000',
        rewrite: (path) => path.replace(/^\/agent-seal-server/, ''),
        changeOrigin: true,
      },
    },
  },
}))
