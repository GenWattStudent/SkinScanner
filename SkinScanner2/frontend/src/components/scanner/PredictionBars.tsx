import { cn, formatConfidence } from '@/lib/utils'
import { useAppStore } from '@/store/useAppStore'
import { Progress } from '@/components/ui/progress'
import type { ClassPrediction } from '@/types/api'

const BAR_COLORS: Record<0 | 1 | 2, string> = {
  0: 'bg-emerald-500',
  1: 'bg-amber-500',
  2: 'bg-red-500',
}

interface PredictionBarsProps {
  predictions: ClassPrediction[]
}

export function PredictionBars({ predictions }: PredictionBarsProps) {
  const { language, t } = useAppStore()

  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        {t('topPredictions')}
      </p>
      {predictions.map((pred, i) => {
        const name = language === 'pl' ? pred.class_pl : pred.class_en
        const pct = pred.confidence * 100
        const barColor = BAR_COLORS[pred.risk_level]
        return (
          <div key={pred.class_key} className={cn('space-y-1.5', i === 0 && 'pb-3 border-b border-slate-200 dark:border-slate-800')}>
            <div className="flex items-center justify-between gap-2">
              <span className={cn('text-sm font-medium', i === 0 ? 'text-slate-900 dark:text-slate-100' : 'text-slate-500 dark:text-slate-400')}>
                {name}
              </span>
              <span className={cn('font-mono text-sm font-bold tabular-nums', i === 0 ? 'text-slate-900 dark:text-slate-100' : 'text-slate-500 dark:text-slate-400')}>
                {formatConfidence(pred.confidence)}
              </span>
            </div>
            <Progress
              value={pct}
              className="h-2"
              indicatorClassName={barColor}
            />
          </div>
        )
      })}
    </div>
  )
}
