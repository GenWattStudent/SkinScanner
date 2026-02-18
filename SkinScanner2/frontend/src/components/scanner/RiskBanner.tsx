import { cn } from '@/lib/utils'
import { useAppStore } from '@/store/useAppStore'
import { ShieldCheck, Eye, AlertTriangle } from 'lucide-react'

const RISK_CONFIG = {
  0: {
    icon: ShieldCheck,
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    text: 'text-emerald-400',
    iconBg: 'bg-emerald-500/20',
    labelKey: 'risk0',
    subKey: 'risk0sub',
  },
  1: {
    icon: Eye,
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    text: 'text-amber-400',
    iconBg: 'bg-amber-500/20',
    labelKey: 'risk1',
    subKey: 'risk1sub',
  },
  2: {
    icon: AlertTriangle,
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    text: 'text-red-400',
    iconBg: 'bg-red-500/20',
    labelKey: 'risk2',
    subKey: 'risk2sub',
  },
} as const

interface RiskBannerProps {
  riskLevel: 0 | 1 | 2
  diagnosisName: string
  className?: string
}

export function RiskBanner({ riskLevel, diagnosisName, className }: RiskBannerProps) {
  const t = useAppStore((s) => s.t)
  const config = RISK_CONFIG[riskLevel]
  const Icon = config.icon

  return (
    <div
      className={cn(
        'flex items-start gap-4 rounded-xl border p-4',
        config.bg,
        config.border,
        className,
      )}
    >
      <div className={cn('flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full', config.iconBg)}>
        <Icon className={cn('h-5 w-5', config.text)} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={cn('text-lg font-bold', config.text)}>{diagnosisName}</span>
        </div>
        <p className={cn('text-sm font-medium mt-0.5', config.text)}>{t(config.labelKey)}</p>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{t(config.subKey)}</p>
      </div>
    </div>
  )
}
