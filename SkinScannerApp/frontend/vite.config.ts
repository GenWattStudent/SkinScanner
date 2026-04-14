import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // When something else already uses :8000 (e.g. Django), set e.g. VITE_DEV_API_PROXY=http://127.0.0.1:8001 in .env.local
  const apiProxyTarget = env.VITE_DEV_API_PROXY || 'http://127.0.0.1:8000'
  const wsProxyTarget = apiProxyTarget.replace(/^http/, 'ws')

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: '0.0.0.0', // Listen on all network interfaces
      port: 5173,
      allowedHosts: [
        'localhost',
        '.trycloudflare.com',           // pozwala na wszystkie subdomeny trycloudflare
        // jeśli chcesz tylko konkretny adres, możesz wpisać go tutaj zamiast .trycloudflare.com
      ],
      proxy: {
        '/api': {
          target: apiProxyTarget,
          changeOrigin: true,
        },
        '/ws': {
          target: wsProxyTarget,
          ws: true,
          changeOrigin: true,
        },
      },
    },
  }
})
