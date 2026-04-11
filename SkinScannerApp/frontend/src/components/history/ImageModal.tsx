import { Download, X } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { historyImageUrl } from '@/api/history'
import { useAppStore } from '@/store/useAppStore'
import { formatConfidence, formatDate, cn } from '@/lib/utils'
import { DISEASE_INFO_MAP } from '@/types/diseaseInfo'
import type { HistoryEntry } from '@/types/api'

interface Props {
  entry: HistoryEntry | null
  onClose: () => void
}

const RISK_BADGE: Record<0 | 1 | 2, 'risk0' | 'risk1' | 'risk2'> = {
  0: 'risk0',
  1: 'risk1',
  2: 'risk2',
}

const RISK_TEXT: Record<0 | 1 | 2, string> = {
  0: 'text-emerald-500',
  1: 'text-amber-500',
  2: 'text-red-500',
}

export function ImageModal({ entry, onClose }: Props) {
  const { language, t } = useAppStore()

  if (!entry) return null

  const info = DISEASE_INFO_MAP[entry.consensus_class_key]
  const name = info
    ? (language === 'pl' ? info.pl : info.en)
    : entry.consensus_class_key
  const originalUrl = historyImageUrl(entry.id, 'original')

  const handleDownloadOriginal = () => {
    const a = document.createElement('a')
    a.href = originalUrl
    a.download = `skinscanner_${entry.id}_original.png`
    a.click()
  }

  const handleDownloadHeatmap = (modelType: string) => {
    const mr = entry.model_results.find((m) => m.model_type === modelType)
    if (!mr?.image_heatmap_url) return
    const a = document.createElement('a')
    a.href = mr.image_heatmap_url
    a.download = `skinscanner_${entry.id}_heatmap_${modelType}.png`
    a.click()
  }

  return (
    <Dialog open={!!entry} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-5xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <DialogHeader className="flex-shrink-0">
          <div className="flex items-start justify-between gap-3">
            <DialogTitle className="flex flex-wrap items-center gap-3 flex-1">
              <span className="text-lg">{name}</span>
              <Badge variant={RISK_BADGE[entry.consensus_risk_level]}>
                {t(`risk${entry.consensus_risk_level}`)}
              </Badge>
              <span className="ml-auto text-xs font-normal text-slate-500">
                {formatDate(entry.timestamp)}
              </span>
            </DialogTitle>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 flex-shrink-0"
              onClick={onClose}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto min-h-0 space-y-4">
          {/* Consensus meta row */}
          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
            <span>
              {t('consensus')}: <strong className="text-slate-700 dark:text-slate-200">{name}</strong>
            </span>
            <span>
              {t('confidence')}: <strong className="text-slate-700 dark:text-slate-200">{formatConfidence(entry.consensus_confidence)}</strong>
            </span>
            <span>
              {t('modelsUsed')}: <strong className="text-slate-700 dark:text-slate-200">{entry.model_results.length}</strong>
            </span>
          </div>

          {/* Original image */}
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              {t('original')}
            </p>
            <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
              <img
                src={originalUrl}
                alt={`${name} – original`}
                className="w-full object-contain max-h-[40vh]"
              />
            </div>
            <Button
              variant="outline"
              size="sm"
              className="w-full text-xs"
              onClick={handleDownloadOriginal}
            >
              <Download className="mr-1.5 h-3.5 w-3.5" />
              {t('downloadImage')}
            </Button>
          </div>

          {/* Per-model heatmaps grid */}
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              {t('perModelResults')}
            </p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {entry.model_results.map((mr) => {
                const mrInfo = DISEASE_INFO_MAP[mr.class_key]
                const mrName = mrInfo
                  ? (language === 'pl' ? mrInfo.pl : mrInfo.en)
                  : mr.class_key
                const risk = mr.risk_level as 0 | 1 | 2

                return (
                  <div key={mr.model_type} className="space-y-2 rounded-lg border border-slate-200 dark:border-slate-800 p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-700 dark:text-slate-200">{mr.model_label}</span>
                      <Badge variant={RISK_BADGE[risk]} className="text-[10px]">
                        {formatConfidence(mr.confidence)}
                      </Badge>
                    </div>
                    <p className={cn('text-sm font-semibold', RISK_TEXT[risk])}>{mrName}</p>
                    {mr.image_heatmap_url && (
                      <>
                        <div className="overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-950 aspect-[4/3]">
                          <img
                            src={mr.image_heatmap_url}
                            alt={`Heatmap – ${mr.model_label}`}
                            className="w-full h-full object-contain"
                          />
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full text-xs"
                          onClick={() => handleDownloadHeatmap(mr.model_type)}
                        >
                          <Download className="mr-1.5 h-3.5 w-3.5" />
                          {t('downloadHeatmap')}
                        </Button>
                      </>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Footer close button */}
        <div className="flex-shrink-0 border-t border-slate-200 dark:border-slate-800 pt-4">
          <Button variant="outline" className="w-full" onClick={onClose}>
            <X className="mr-1.5 h-4 w-4" />
            {t('close')}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
