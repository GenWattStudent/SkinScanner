import axios from 'axios'

/**
 * Dev: keep baseURL empty so requests go to the Vite origin (e.g. https://localhost:5173).
 * The browser will show that host in DevTools — Vite still proxies `/api` and `/ws` to the backend.
 *
 * Override with VITE_API_BASE_URL (e.g. direct http://127.0.0.1:8001) if you skip the proxy.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  timeout: 120_000, // 2 min (inference can be slow on CPU)
})

// Normalise error shape from FastAPI
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const msg =
      error?.response?.data?.message ??
      error?.response?.data?.detail ??
      error.message ??
      'Unknown error'
    return Promise.reject(new Error(msg))
  },
)

export default api
