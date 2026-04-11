/**
 * BodyMapPage – main page that composes the body diagram, view toggle,
 * marker list, and detail panel.
 *
 * Each body map belongs to a specific patient.  The patient selector at the
 * top lets the user create/switch patients.  Markers are loaded per-patient.
 */

import { useState, useCallback, useMemo } from 'react'
import type { BodyMapView, HistoryEntry } from '@/types/api'
import { useAppStore } from '@/store/useAppStore'
import { useBodyMapMarkers, useCreateMarker } from '@/api/bodymap'
import { useHistory } from '@/api/history'
import { PatientSelector } from '@/components/bodymap/PatientSelector'
import { BodyDiagram } from '@/components/bodymap/BodyDiagram'
import { MarkerDetail } from '@/components/bodymap/MarkerDetail'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { RotateCcw } from 'lucide-react'

export default function BodyMapPage() {
  const t = useAppStore((s) => s.t)

  // ── Patient state ───────────────────────────────────────────────────────
  const [patientId, setPatientId] = useState<number | null>(null)

  const { data, isLoading } = useBodyMapMarkers(patientId)
  const createMutation = useCreateMarker()

  // Fetch enough history to resolve linked scan risk-colours on pins
  const { data: historyData } = useHistory(1, 200)

  const [view, setView] = useState<BodyMapView>('front')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const markers = data?.items ?? []
  const selectedMarker = markers.find((m) => m.id === selectedId) ?? null

  // Build a map: scan_id → HistoryEntry for pin risk-colour lookup
  const linkedScans = useMemo(() => {
    const map = new Map<number, HistoryEntry>()
    if (historyData?.items) {
      for (const entry of historyData.items) {
        map.set(entry.id, entry)
      }
    }
    return map
  }, [historyData])

  // Called when the user clicks empty space on the SVG
  const handleAddMarker = useCallback(
    (x: number, y: number) => {
      if (patientId === null) return
      createMutation.mutate(
        { x, y, view, label: '', patient_id: patientId },
        {
          onSuccess: (created) => setSelectedId(created.id),
        },
      )
    },
    [view, patientId, createMutation],
  )

  const handleSelectMarker = useCallback((id: number) => {
    setSelectedId((prev) => (prev === id ? null : id))
  }, [])

  // Reset selection when patient changes
  const handlePatientChange = useCallback((id: number | null) => {
    setPatientId(id)
    setSelectedId(null)
  }, [])

  const frontCount = markers.filter((m) => m.view === 'front').length
  const backCount = markers.filter((m) => m.view === 'back').length

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold">{t('bodymapTitle')}</h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {t('bodymapDesc')}
            </p>
          </div>

          {/* View toggle */}
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant={view === 'front' ? 'default' : 'outline'}
              onClick={() => setView('front')}
              className="gap-1.5"
              disabled={!patientId}
            >
              {t('bodymapFront')}
              {frontCount > 0 && (
                <Badge variant="secondary" className="ml-1 text-[10px] px-1.5 py-0">
                  {frontCount}
                </Badge>
              )}
            </Button>
            <Button
              size="sm"
              variant={view === 'back' ? 'default' : 'outline'}
              onClick={() => setView('back')}
              className="gap-1.5"
              disabled={!patientId}
            >
              {t('bodymapBack')}
              {backCount > 0 && (
                <Badge variant="secondary" className="ml-1 text-[10px] px-1.5 py-0">
                  {backCount}
                </Badge>
              )}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setView((v) => (v === 'front' ? 'back' : 'front'))}
              title={t('bodymapFlip')}
              disabled={!patientId}
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Patient selector */}
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
            {t('patientLabel')}:
          </span>
          <PatientSelector selectedId={patientId} onSelect={handlePatientChange} />
        </div>
      </div>

      {/* No patient selected state */}
      {!patientId ? (
        <div className="flex h-80 items-center justify-center rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {t('patientSelectPrompt')}
          </p>
        </div>
      ) : isLoading ? (
        <div className="flex gap-6">
          <Skeleton className="h-[520px] w-full max-w-xs" />
          <Skeleton className="h-64 w-full" />
        </div>
      ) : (
        <div className="flex flex-col gap-6 lg:flex-row">
          {/* Diagram */}
          <div className="flex-1 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900/50">
            <BodyDiagram
              view={view}
              markers={markers}
              selectedId={selectedId}
              linkedScans={linkedScans}
              onAddMarker={handleAddMarker}
              onSelectMarker={handleSelectMarker}
            />
            <p className="mt-2 text-center text-xs text-slate-400 dark:text-slate-500">
              {t('bodymapClickToAdd')}
            </p>
          </div>

          {/* Detail panel / empty state */}
          <div className="w-full lg:w-80">
            {selectedMarker ? (
              <MarkerDetail
                marker={selectedMarker}
                onClose={() => setSelectedId(null)}
              />
            ) : (
              <div className="flex h-full flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 p-6 text-center dark:border-slate-700">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {markers.length === 0
                    ? t('bodymapEmpty')
                    : t('bodymapSelectMarker')}
                </p>
              </div>
            )}

            {/* Marker count summary */}
            {markers.length > 0 && (
              <p className="mt-3 text-center text-xs text-slate-400">
                {t('bodymapTotalMarkers')}: {markers.length}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
