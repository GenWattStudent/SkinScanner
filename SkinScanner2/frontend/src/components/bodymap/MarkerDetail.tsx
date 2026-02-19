/**
 * MarkerDetail – side-panel showing info about the selected body-map marker.
 *
 * Allows editing label / notes, linking to a scan (with preview), and deleting.
 * Fetches the linked scan directly by ID so it always resolves correctly.
 * Clicking the scan preview opens a full-screen ImageModal (same as in History).
 */

import { useState, useEffect } from 'react'
import type { BodyMapMarker } from '@/types/api'
import { useAppStore } from '@/store/useAppStore'
import { useUpdateMarker, useDeleteMarker } from '@/api/bodymap'
import { historyImageUrl, useHistoryEntry } from '@/api/history'
import { ScanPickerDialog } from './ScanPickerDialog'
import { ImageModal } from '@/components/history/ImageModal'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Trash2, Save, X, Link2, ImageIcon, Eye } from 'lucide-react'
import { formatDate, formatConfidence } from '@/lib/utils'
import { DISEASE_INFO_MAP } from '@/types/diseaseInfo'

const RISK_BADGE: Record<0 | 1 | 2, 'risk0' | 'risk1' | 'risk2'> = {
  0: 'risk0',
  1: 'risk1',
  2: 'risk2',
}

interface MarkerDetailProps {
  marker: BodyMapMarker
  onClose: () => void
}

export function MarkerDetail({ marker, onClose }: MarkerDetailProps) {
  const { language, t } = useAppStore()
  const updateMutation = useUpdateMarker()
  const deleteMutation = useDeleteMarker()

  const [label, setLabel] = useState(marker.label)
  const [notes, setNotes] = useState(marker.notes ?? '')
  const [pickerOpen, setPickerOpen] = useState(false)
  const [scanModalOpen, setScanModalOpen] = useState(false)

  // Fetch the linked scan directly by ID (always correct, no batch dependency)
  const { data: linkedScan, isLoading: scanLoading } = useHistoryEntry(marker.scan_id ?? null)

  // Sync when selected marker changes
  useEffect(() => {
    setLabel(marker.label)
    setNotes(marker.notes ?? '')
  }, [marker.id, marker.label, marker.notes])

  const handleSave = () => {
    updateMutation.mutate({ id: marker.id, label, notes: notes || null })
  }

  const handleDelete = () => {
    if (window.confirm(t('bodymapDeleteConfirm'))) {
      deleteMutation.mutate(marker.id, { onSuccess: onClose })
    }
  }

  const handleLinkScan = (scanId: number | null) => {
    updateMutation.mutate({ id: marker.id, scan_id: scanId })
    setPickerOpen(false)
  }

  const createdAt = new Date(marker.created_at).toLocaleDateString()

  // Linked scan info
  const scanInfo = linkedScan
    ? DISEASE_INFO_MAP[linkedScan.consensus_class_key]
    : null
  const scanName = scanInfo
    ? language === 'pl' ? scanInfo.pl : scanInfo.en
    : linkedScan?.consensus_class_key ?? null

  return (
    <>
      <div className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">
            {t('bodymapMarkerDetail')}
          </h3>
          <button
            onClick={onClose}
            className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Coordinates */}
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {t('bodymapView')}: <span className="font-medium capitalize">{marker.view}</span>
          {' · '}
          X: {(marker.x * 100).toFixed(1)}%  Y: {(marker.y * 100).toFixed(1)}%
          {' · '}
          {createdAt}
        </p>

        {/* Label */}
        <div className="space-y-1.5">
          <Label htmlFor="marker-label" className="text-xs">{t('bodymapLabel')}</Label>
          <Input
            id="marker-label"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder={t('bodymapLabelPlaceholder')}
            maxLength={200}
            className="h-8 text-sm"
          />
        </div>

        {/* Notes */}
        <div className="space-y-1.5">
          <Label htmlFor="marker-notes" className="text-xs">{t('bodymapNotes')}</Label>
          <textarea
            id="marker-notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder={t('bodymapNotesPlaceholder')}
            rows={3}
            className="w-full rounded-md border border-slate-200 bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:placeholder:text-slate-500"
          />
        </div>

        {/* ── Linked scan section ──────────────────────────────────────── */}
        <div className="space-y-2">
          <Label className="text-xs">{t('bodymapLinkedScan')}</Label>

          {marker.scan_id && scanLoading ? (
            <Skeleton className="h-16 w-full rounded-lg" />
          ) : linkedScan ? (
            <button
              type="button"
              onClick={() => setScanModalOpen(true)}
              className="flex w-full items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 p-2 text-left transition-colors hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800/50 dark:hover:bg-slate-800"
            >
              {/* Thumbnail */}
              <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center overflow-hidden rounded-md bg-slate-200 dark:bg-slate-700">
                {linkedScan.image_original_url ? (
                  <img
                    src={historyImageUrl(linkedScan.id, 'original')}
                    alt=""
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <ImageIcon className="h-5 w-5 text-slate-400" />
                )}
              </div>
              {/* Scan info */}
              <div className="flex-1 min-w-0">
                <p className="truncate text-sm font-medium text-slate-700 dark:text-slate-200">
                  {scanName}
                </p>
                <div className="mt-0.5 flex items-center gap-1.5 text-xs text-slate-500">
                  <span>{formatDate(linkedScan.timestamp)}</span>
                  <span>·</span>
                  <span>{formatConfidence(linkedScan.consensus_confidence)}</span>
                </div>
                <Badge
                  variant={RISK_BADGE[linkedScan.consensus_risk_level]}
                  className="mt-1 text-[9px] px-1.5 py-0"
                >
                  {t(`risk${linkedScan.consensus_risk_level}`)}
                </Badge>
              </div>
              {/* View hint */}
              <Eye className="h-4 w-4 flex-shrink-0 text-slate-400" />
            </button>
          ) : (
            <p className="text-xs italic text-slate-400 dark:text-slate-500">
              {t('bodymapNoLinkedScan')}
            </p>
          )}

          <Button
            variant="outline"
            size="sm"
            className="w-full gap-1.5 text-xs"
            onClick={() => setPickerOpen(true)}
          >
            <Link2 className="h-3.5 w-3.5" />
            {marker.scan_id ? t('bodymapChangeScan') : t('bodymapLinkScan')}
          </Button>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="flex-1 gap-1.5"
          >
            <Save className="h-3.5 w-3.5" />
            {t('bodymapSave')}
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="gap-1.5"
          >
            <Trash2 className="h-3.5 w-3.5" />
            {t('delete')}
          </Button>
        </div>
      </div>

      {/* Scan picker dialog */}
      <ScanPickerDialog
        open={pickerOpen}
        currentScanId={marker.scan_id}
        onSelect={handleLinkScan}
        onClose={() => setPickerOpen(false)}
      />

      {/* Full scan detail modal (same as in History) */}
      <ImageModal
        entry={scanModalOpen ? linkedScan ?? null : null}
        onClose={() => setScanModalOpen(false)}
      />
    </>
  )
}
