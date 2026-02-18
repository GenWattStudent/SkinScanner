import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Language, ModelType, Theme } from '@/types/api'
import { t as translate } from '@/i18n/translations'

/** Detect browser language – if Polish → 'pl', otherwise 'en' */
function detectLanguage(): Language {
  const lang = navigator.language || (navigator as { userLanguage?: string }).userLanguage || 'en'
  return lang.toLowerCase().startsWith('pl') ? 'pl' : 'en'
}

/** Resolve effective theme based on system preference */
function resolveTheme(theme: Theme): 'light' | 'dark' {
  if (theme !== 'system') return theme
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/** Apply the `dark` class to <html> and update meta theme-color */
function applyTheme(theme: Theme) {
  const resolved = resolveTheme(theme)
  document.documentElement.classList.toggle('dark', resolved === 'dark')
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) meta.setAttribute('content', resolved === 'dark' ? '#020617' : '#f8fafc')
}

interface AppState {
  language: Language
  modelType: ModelType
  cropFactor: number
  theme: Theme

  setLanguage: (lang: Language) => void
  setModelType: (model: ModelType) => void
  setCropFactor: (factor: number) => void
  setTheme: (theme: Theme) => void

  /** Shorthand translate using current language */
  t: (key: string) => string
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      language: detectLanguage(),
      modelType: 'mobilenet',
      cropFactor: 0,
      theme: 'system',

      setLanguage: (language) => set({ language }),
      setModelType: (modelType) => set({ modelType }),
      setCropFactor: (cropFactor) => set({ cropFactor }),
      setTheme: (theme) => {
        applyTheme(theme)
        set({ theme })
      },

      t: (key: string) => translate(get().language, key),
    }),
    {
      name: 'skinscanner-settings',
      partialize: (state) => ({
        language: state.language,
        modelType: state.modelType,
        cropFactor: state.cropFactor,
        theme: state.theme,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) applyTheme(state.theme)
      },
    },
  ),
)

// Also apply on initial load (before rehydration picks up)
applyTheme(useAppStore.getState().theme)

// Listen for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  const { theme } = useAppStore.getState()
  if (theme === 'system') applyTheme('system')
})
