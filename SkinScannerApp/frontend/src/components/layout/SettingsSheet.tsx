import { X, Languages, Cpu, Server, Sun, Moon, Monitor } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'
import { useHealth, useModels } from '@/api/health'
import { Label } from '@/components/ui/label'
import type { Language, Theme } from '@/types/api'
import { cn } from '@/lib/utils'

interface SettingsSheetProps {
  open: boolean
  onClose: () => void
}

const themeOptions: { value: Theme; icon: typeof Sun; labelKey: string }[] = [
  { value: 'system', icon: Monitor, labelKey: 'themeSystem' },
  { value: 'light', icon: Sun, labelKey: 'themeLight' },
  { value: 'dark', icon: Moon, labelKey: 'themeDark' },
]

export function SettingsSheet({ open, onClose }: SettingsSheetProps) {
  const { language, theme, setLanguage, setTheme, t } =
    useAppStore()
  const { data: health } = useHealth()
  const { data: models } = useModels()

  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/40 dark:bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Sheet */}
      <aside className="fixed right-0 top-0 z-50 flex h-full w-full max-w-sm flex-col border-l border-slate-200 bg-white shadow-2xl animate-slide-up dark:border-slate-800 dark:bg-slate-950">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 px-6 py-4">
          <h2 className="text-lg font-semibold">{t('settings')}</h2>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-8">
          {/* Theme */}
          <div className="space-y-3">
            <Label className="flex items-center gap-2 text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              <Sun className="h-4 w-4" />
              {t('theme')}
            </Label>
            <div className="flex gap-2">
              {themeOptions.map(({ value, icon: Icon, labelKey }) => (
                <button
                  key={value}
                  onClick={() => setTheme(value)}
                  className={cn(
                    'flex flex-1 items-center justify-center gap-1.5 rounded-lg border py-2 text-sm font-medium transition-colors',
                    theme === value
                      ? 'border-blue-500 bg-blue-500/10 text-blue-600 dark:text-blue-400'
                      : 'border-slate-200 bg-slate-50 text-slate-500 hover:text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:text-slate-200',
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {t(labelKey)}
                </button>
              ))}
            </div>
          </div>

          {/* Language */}
          <div className="space-y-3">
            <Label className="flex items-center gap-2 text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              <Languages className="h-4 w-4" />
              {t('language')}
            </Label>
            <div className="flex gap-2">
              {(['pl', 'en'] as Language[]).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setLanguage(lang)}
                  className={cn(
                    'flex-1 rounded-lg border py-2 text-sm font-medium transition-colors',
                    language === lang
                      ? 'border-blue-500 bg-blue-500/10 text-blue-600 dark:text-blue-400'
                      : 'border-slate-200 bg-slate-50 text-slate-500 hover:text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:text-slate-200',
                  )}
                >
                  {lang === 'pl' ? '🇵🇱 Polski' : '🇬🇧 English'}
                </button>
              ))}
            </div>
          </div>

          {/* Models info */}
          <div className="space-y-3">
            <Label className="flex items-center gap-2 text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              <Cpu className="h-4 w-4" />
              {t('model')}
            </Label>
            <div className="rounded-lg border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800 p-3 space-y-2">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {t('allModels')}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {(
                  models ?? [
                    { model_type: 'mobilenet', label: 'MobileNetV3', available: true },
                    { model_type: 'resnet50', label: 'ResNet-50', available: true },
                    { model_type: 'customcnn', label: 'Custom CNN', available: true },
                    { model_type: 'vit', label: 'Vision Transformer', available: true },
                  ]
                ).map((m) => (
                  <span
                    key={m.model_type}
                    className={cn(
                      'rounded-full px-2.5 py-1 text-xs font-medium',
                      m.available
                        ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                        : 'bg-slate-200 text-slate-400 dark:bg-slate-700 dark:text-slate-500',
                    )}
                  >
                    {m.label}
                    {!m.available && ' ✕'}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer: backend status */}
        <div className="border-t border-slate-200 dark:border-slate-800 px-6 py-4">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Server className="h-3.5 w-3.5 flex-shrink-0" />
            <div className="flex flex-col gap-0.5 min-w-0">
              {health ? (
                <>
                  <span className="font-medium text-slate-700 dark:text-slate-300">
                    {health.gpu_name
                      ? health.gpu_name
                      : 'CPU'}
                    {health.gpu_memory_gb ? ` · ${health.gpu_memory_gb} GB` : ''}
                  </span>
                  <span className="text-slate-400">
                    {health.models_loaded.length} model{health.models_loaded.length !== 1 ? 's' : ''} loaded
                  </span>
                </>
              ) : (
                <span>Backend offline</span>
              )}
            </div>
            <div className="ml-auto flex flex-col items-end gap-1">
              <span
                className={cn(
                  'h-2 w-2 rounded-full flex-shrink-0',
                  health ? 'bg-emerald-500' : 'bg-red-500',
                )}
              />
              {health && (
                <span
                  className={cn(
                    'rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase',
                    health.device === 'cuda'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400'
                      : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400',
                  )}
                >
                  {health.device === 'cuda' ? '⚡ GPU' : 'CPU'}
                </span>
              )}
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
