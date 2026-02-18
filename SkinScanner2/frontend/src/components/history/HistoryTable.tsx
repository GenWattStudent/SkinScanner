import { useState } from 'react'
import { Trash2, ImageIcon, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import { useHistory, useDeleteHistory } from '@/api/history'
import { useAppStore } from '@/store/useAppStore'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { ImageModal } from './ImageModal'
import { cn, formatDate, formatConfidence } from '@/lib/utils'
import { DISEASE_INFO_MAP } from '@/types/diseaseInfo'
import type { HistoryEntry } from '@/types/api'

const RISK_ROW: Record<0 | 1 | 2, string> = {
  0: 'border-l-2 border-l-emerald-500/60',
  1: 'border-l-2 border-l-amber-500/60',
  2: 'border-l-2 border-l-red-500/60',
}
const RISK_TEXT: Record<0 | 1 | 2, string> = {
  0: 'text-emerald-400',
  1: 'text-amber-400',
  2: 'text-red-400',
}
const RISK_DOT: Record<0 | 1 | 2, string> = {
  0: 'bg-emerald-500',
  1: 'bg-amber-500',
  2: 'bg-red-500',
}

export function HistoryTable() {
  const { language, t } = useAppStore()
  const [page, setPage] = useState(1)
  const [modalEntry, setModalEntry] = useState<HistoryEntry | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null)
  const limit = 12

  const { data, isLoading, isError } = useHistory(page, limit)
  const { mutate: deleteEntry, isPending: isDeleting } = useDeleteHistory()

  const totalPages = data ? Math.ceil(data.total / limit) : 1

  if (isLoading)
    return (
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full rounded-xl" />
        ))}
      </div>
    )

  if (isError)
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-slate-500">
        <p>{t('error')}</p>
      </div>
    )

  if (!data?.items.length)
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-slate-500">
        <ImageIcon className="h-12 w-12 opacity-30" />
        <p>{t('historyEmpty')}</p>
      </div>
    )

  return (
    <>
      {/* Table header – desktop */}
      <div className="hidden md:grid grid-cols-[1fr_140px_80px_120px_120px_80px] gap-4 px-4 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
        <span>{t('date')}</span>
        <span>{t('diagnosis')}</span>
        <span>{t('confidence')}</span>
        <span>{t('tableRisk') ?? 'Risk'}</span>
        <span>{t('modelsUsed')}</span>
        <span></span>
      </div>

      <div className="space-y-2">
        {data.items.map((entry) => {
          const risk = entry.consensus_risk_level as 0 | 1 | 2
          const info = DISEASE_INFO_MAP[entry.consensus_class_key]
          const name = info
            ? (language === 'pl' ? info.pl : info.en)
            : entry.consensus_class_key
          const modelCount = entry.model_results.length

          return (
            <div
              key={entry.id}
              className={cn(
                'group flex flex-col gap-2 rounded-xl bg-white p-4 transition-colors hover:bg-slate-50 dark:bg-slate-900 dark:hover:bg-slate-800/80 md:grid md:grid-cols-[1fr_140px_80px_120px_120px_80px] md:items-center md:gap-4',
                RISK_ROW[risk],
              )}
            >
              {/* Date */}
              <span className="text-sm text-slate-600 dark:text-slate-300">{formatDate(entry.timestamp)}</span>

              {/* Diagnosis (consensus) */}
              <span className={cn('text-sm font-semibold', RISK_TEXT[risk])}>{name}</span>

              {/* Confidence */}
              <span className="font-mono text-sm text-slate-600 dark:text-slate-300">
                {formatConfidence(entry.consensus_confidence)}
              </span>

              {/* Risk */}
              <div className="flex items-center gap-2">
                <span className={cn('h-2 w-2 rounded-full', RISK_DOT[risk])} />
                <span className={cn('text-xs', RISK_TEXT[risk])}>
                  {t(`risk${risk}`)}
                </span>
              </div>

              {/* Models */}
              <span className="text-xs text-slate-500">
                {modelCount} {modelCount === 1 ? 'model' : (language === 'pl' ? 'modele' : 'models')}
              </span>

              {/* Actions */}
              <div className="flex items-center gap-1 md:justify-end">
                {entry.image_original_url && (
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setModalEntry(entry)}
                    title={t('viewImages')}
                  >
                    <ImageIcon className="h-4 w-4" />
                  </Button>
                )}
                {confirmDelete === entry.id ? (
                  <div className="flex gap-1">
                    <Button
                      variant="destructive"
                      size="icon-sm"
                      disabled={isDeleting}
                      onClick={() => {
                        deleteEntry(entry.id)
                        setConfirmDelete(null)
                      }}
                    >
                      {isDeleting ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <Trash2 className="h-3 w-3" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => setConfirmDelete(null)}
                    >
                      ✕
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    className="opacity-0 transition-opacity group-hover:opacity-100"
                    onClick={() => setConfirmDelete(entry.id)}
                    title={t('delete')}
                  >
                    <Trash2 className="h-4 w-4 text-red-400" />
                  </Button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-3">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
            {t('prevPage')}
          </Button>
          <span className="text-sm text-slate-400">
            {t('page')} {page} {t('of')} {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            {t('nextPage')}
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Image modal */}
      <ImageModal entry={modalEntry} onClose={() => setModalEntry(null)} />
    </>
  )
}
