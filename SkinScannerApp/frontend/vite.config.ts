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
    plugins: [react(), basicSsl()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      https: true,
      host: '0.0.0.0',
      port: 5173,
      allowedHosts: true,
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
