/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Optional; when set, axios talks to the backend directly (bypasses Vite proxy). */
  readonly VITE_API_BASE_URL?: string
}
