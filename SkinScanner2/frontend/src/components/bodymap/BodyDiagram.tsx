/**
 * BodyDiagram – interactive SVG canvas where users can place and select markers.
 *
 * Responsibilities (Single Responsibility):
 * - Render the body silhouette for the active view (front/back)
 * - Render existing markers as <MarkerPin> coloured by linked scan risk
 * - Translate click coordinates → normalised 0–1 and call onAddMarker
 * - Call onSelectMarker when a pin is tapped
 */

import { useCallback, useRef } from 'react'
import type { BodyMapMarker, BodyMapView, HistoryEntry } from '@/types/api'
import { FrontSilhouette, BackSilhouette, BODY_VIEWBOX } from './BodySilhouette'
import { MarkerPin } from './MarkerPin'

interface BodyDiagramProps {
  view: BodyMapView
  markers: BodyMapMarker[]
  selectedId: number | null
  /** Map of scan_id → HistoryEntry for linked scans (risk colour + tooltip) */
  linkedScans: Map<number, HistoryEntry>
  onAddMarker: (x: number, y: number) => void
  onSelectMarker: (id: number) => void
}

export function BodyDiagram({
  view,
  markers,
  selectedId,
  linkedScans,
  onAddMarker,
  onSelectMarker,
}: BodyDiagramProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  const handleClick = useCallback(
    (e: React.MouseEvent<SVGSVGElement>) => {
      const svg = svgRef.current
      if (!svg) return

      const rect = svg.getBoundingClientRect()
      const scaleX = BODY_VIEWBOX.width / rect.width
      const scaleY = BODY_VIEWBOX.height / rect.height
      const vbX = (e.clientX - rect.left) * scaleX
      const vbY = (e.clientY - rect.top) * scaleY

      const nx = Math.min(1, Math.max(0, vbX / BODY_VIEWBOX.width))
      const ny = Math.min(1, Math.max(0, vbY / BODY_VIEWBOX.height))

      onAddMarker(nx, ny)
    },
    [onAddMarker],
  )

  const filteredMarkers = markers.filter((m) => m.view === view)

  return (
    <svg
      ref={svgRef}
      viewBox={`0 0 ${BODY_VIEWBOX.width} ${BODY_VIEWBOX.height}`}
      className="mx-auto h-full max-h-[520px] w-auto select-none text-slate-700 dark:text-slate-300"
      onClick={handleClick}
    >
      {/* Grid lines for spatial reference */}
      <defs>
        <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="currentColor" strokeWidth="0.3" opacity="0.15" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />

      {/* Silhouette */}
      {view === 'front' ? <FrontSilhouette /> : <BackSilhouette />}

      {/* Markers */}
      {filteredMarkers.map((m) => {
        const linked = m.scan_id != null ? linkedScans.get(m.scan_id) : undefined
        return (
          <MarkerPin
            key={m.id}
            x={m.x}
            y={m.y}
            isSelected={m.id === selectedId}
            riskLevel={linked ? linked.consensus_risk_level : null}
            hasLinkedScan={m.scan_id != null}
            label={m.label || undefined}
            onClick={() => onSelectMarker(m.id)}
          />
        )
      })}
    </svg>
  )
}
