import axios from 'axios'

const api = axios.create({
  baseURL: '',            // relative – Vite proxy handles /api → :8000
  timeout: 120_000,       // 2 min (inference can be slow on CPU)
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
