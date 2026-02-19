/**
 * MarkerPin – a single pin rendered inside the body-map SVG.
 *
 * Props
 * ─────
 * - x, y          : normalised 0–1 coordinates
 * - isSelected     : highlight ring when active
 * - riskLevel      : colour-code (0=green, 1=amber, 2=red), null if no linked scan
 * - hasLinkedScan  : true when a scan is linked – shows a small camera icon
 * - label          : optional short text shown on hover (SVG title)
 * - onClick        : fires when the user taps the pin
 */

import { BODY_VIEWBOX } from './BodySilhouette'

const RISK_COLORS: Record<number, string> = {
  0: '#22c55e', // green-500
  1: '#f59e0b', // amber-500
  2: '#ef4444', // red-500
}
const DEFAULT_COLOR = '#3b82f6' // blue-500

interface MarkerPinProps {
  x: number
  y: number
  isSelected: boolean
  riskLevel?: number | null
  hasLinkedScan?: boolean
  label?: string
  onClick: () => void
}

export function MarkerPin({ x, y, isSelected, riskLevel, hasLinkedScan, label, onClick }: MarkerPinProps) {
  const cx = x * BODY_VIEWBOX.width
  const cy = y * BODY_VIEWBOX.height
  const fill = riskLevel != null ? (RISK_COLORS[riskLevel] ?? DEFAULT_COLOR) : DEFAULT_COLOR

  return (
    <g
      style={{ cursor: 'pointer' }}
      onClick={(e) => {
        e.stopPropagation()
        onClick()
      }}
    >
      {label && <title>{label}</title>}

      {/* selection ring */}
      {isSelected && (
        <circle cx={cx} cy={cy} r={10} fill="none" stroke={fill} strokeWidth={2} opacity={0.5}>
          <animate attributeName="r" values="10;14;10" dur="1.2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.5;0.2;0.5" dur="1.2s" repeatCount="indefinite" />
        </circle>
      )}
      {/* drop-shadow */}
      <circle cx={cx} cy={cy + 1} r={6} fill="black" opacity={0.15} />
      {/* main circle */}
      <circle cx={cx} cy={cy} r={6} fill={fill} stroke="white" strokeWidth={2} />

      {/* Camera icon indicator when a scan is linked */}
      {hasLinkedScan && (
        <g transform={`translate(${cx + 5}, ${cy - 8})`}>
          <circle r="4.5" fill="white" stroke={fill} strokeWidth="1" />
          <rect x="-2.5" y="-1.5" width="5" height="3.5" rx="0.5" fill={fill} />
          <circle r="1" fill="white" />
        </g>
      )}
    </g>
  )
}
