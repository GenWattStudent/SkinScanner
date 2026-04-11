/**
 * ScanPickerDialog – a dialog that lets the user browse scan history
 * and pick a scan to link to a body-map marker.
 *
 * Shows a paginated list of recent scans with thumbnail, diagnosis, risk
 * level and date. Clicking a row fires onSelect(scan_id).
 */

import { useState } from 'react'
import { ChevronLeft, ChevronRight, ImageIcon, Link2, Unlink } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useHistory, historyImageUrl } from '@/api/history'
import { useAppStore } from '@/store/useAppStore'
import { formatDate, formatConfidence, cn } from '@/lib/utils'
import { DISEASE_INFO_MAP } from '@/types/diseaseInfo'

const RISK_BADGE: Record<0 | 1 | 2, 'risk0' | 'risk1' | 'risk2'> = {
  0: 'risk0',
  1: 'risk1',
  2: 'risk2',
}

const RISK_DOT: Record<0 | 1 | 2, string> = {
  0: 'bg-emerald-500',
  1: 'bg-amber-500',
  2: 'bg-red-500',
}

interface ScanPickerDialogProps {
  open: boolean
  currentScanId: number | null
  onSelect: (scanId: number | null) => void
  onClose: () => void
}

export function ScanPickerDialog({
  open,
  currentScanId,
  onSelect,
  onClose,
}: ScanPickerDialogProps) {
  const { language, t } = useAppStore()
  const [page, setPage] = useState(1)
  const limit = 8
  const { data, isLoading } = useHistory(page, limit)

  const totalPages = data ? Math.ceil(data.total / limit) : 1

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-base">{t('bodymapPickScan')}</DialogTitle>
        </DialogHeader>

        {/* Unlink button */}
        {currentScanId != null && (
          <Button
            variant="outline"
            size="sm"
            className="mb-2 gap-1.5 self-start text-xs"
            onClick={() => onSelect(null)}
          >
            <Unlink className="h-3.5 w-3.5" />
            {t('bodymapUnlinkScan')}
          </Button>
        )}

        {/* Scan list */}
        <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
          {isLoading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full rounded-lg" />
            ))
          ) : !data?.items.length ? (
            <div className="flex flex-col items-center gap-3 py-10 text-slate-400">
              <ImageIcon className="h-10 w-10 opacity-30" />
              <p className="text-sm">{t('historyEmpty')}</p>
            </div>
          ) : (
            data.items.map((entry) => {
              const risk = entry.consensus_risk_level as 0 | 1 | 2
              const info = DISEASE_INFO_MAP[entry.consensus_class_key]
              const name = info
                ? language === 'pl' ? info.pl : info.en
                : entry.consensus_class_key
              const isLinked = entry.id === currentScanId
              const imgUrl = entry.image_original_url
                ? historyImageUrl(entry.id, 'original')
                : null

              return (
                <button
                  key={entry.id}
                  onClick={() => onSelect(entry.id)}
                  className={cn(
                    'flex w-full items-center gap-3 rounded-lg border p-2.5 text-left transition-colors',
                    isLinked
                      ? 'border-blue-400 bg-blue-50 dark:border-blue-600 dark:bg-blue-950/40'
                      : 'border-slate-200 bg-white hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800',
                  )}
                >
                  {/* Thumbnail */}
                  <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center overflow-hidden rounded-md bg-slate-100 dark:bg-slate-800">
                    {imgUrl ? (
                      <img
                        src={imgUrl}
                        alt=""
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <ImageIcon className="h-5 w-5 text-slate-400" />
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className={cn('inline-block h-2 w-2 rounded-full flex-shrink-0', RISK_DOT[risk])} />
                      <span className="truncate text-sm font-medium text-slate-700 dark:text-slate-200">
                        {name}
                      </span>
                      {isLinked && (
                        <Link2 className="ml-auto h-3.5 w-3.5 flex-shrink-0 text-blue-500" />
                      )}
                    </div>
                    <div className="mt-0.5 flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                      <span>{formatDate(entry.timestamp)}</span>
                      <span>·</span>
                      <span>{formatConfidence(entry.consensus_confidence)}</span>
                      <Badge variant={RISK_BADGE[risk]} className="ml-auto text-[9px] px-1 py-0">
                        {t(`risk${risk}`)}
                      </Badge>
                    </div>
                  </div>
                </button>
              )
            })
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t pt-3 text-xs text-slate-500">
            <Button
              variant="ghost"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
              {t('prevPage')}
            </Button>
            <span>
              {t('page')} {page} {t('of')} {totalPages}
            </span>
            <Button
              variant="ghost"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              {t('nextPage')}
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
