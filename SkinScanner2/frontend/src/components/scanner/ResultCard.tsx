import { useState } from 'react'
import { Download, RefreshCw, ScanLine, ChevronDown, ChevronUp } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'
import { RiskBanner } from './RiskBanner'
import { PredictionBars } from './PredictionBars'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import type { AnalyzeResponse, ModelResult } from '@/types/api'
import { cn, formatConfidence } from '@/lib/utils'
import { DISEASE_INFO_MAP } from '@/types/diseaseInfo'

function downloadDataUri(dataUri: string, filename: string) {
  const a = document.createElement('a')
  a.href = dataUri
  a.download = filename
  a.click()
}

const RISK_BORDER: Record<0 | 1 | 2, string> = {
  0: 'border-emerald-500/40',
  1: 'border-amber-500/40',
  2: 'border-red-500/40',
}
const RISK_BG: Record<0 | 1 | 2, string> = {
  0: 'bg-emerald-500/5',
  1: 'bg-amber-500/5',
  2: 'bg-red-500/5',
}
const RISK_TEXT: Record<0 | 1 | 2, string> = {
  0: 'text-emerald-500',
  1: 'text-amber-500',
  2: 'text-red-500',
}
const RISK_DOT: Record<0 | 1 | 2, string> = {
  0: 'bg-emerald-500',
  1: 'bg-amber-500',
  2: 'bg-red-500',
}

interface ResultCardProps {
  result: AnalyzeResponse
  onNewScan: () => void
  onReanalyze?: () => void
}

function ModelCard({ mr, scanId, originalB64, idx }: { mr: ModelResult; scanId: number; originalB64: string; idx: number }) {
  const { language, t } = useAppStore()
  const [expanded, setExpanded] = useState(idx === 0)
  const primary = mr.primary_prediction
  const name = language === 'pl' ? primary.class_pl : primary.class_en
  const desc = language === 'pl' ? primary.description_pl : primary.description_en
  const risk = primary.risk_level as 0 | 1 | 2

  return (
    <Card className={cn('border-l-4 transition-all', RISK_BORDER[risk], RISK_BG[risk])}>
      <CardContent className="p-0">
        {/* Header — always visible */}
        <button
          className="flex w-full items-center gap-3 p-4 text-left hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
          onClick={() => setExpanded(!expanded)}
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-bold text-slate-700 dark:text-slate-200">{mr.model_label}</span>
              <span className={cn('h-2 w-2 rounded-full', RISK_DOT[risk])} />
              <span className={cn('text-sm font-semibold', RISK_TEXT[risk])}>{name}</span>
              <span className="font-mono text-sm text-slate-500 tabular-nums">{formatConfidence(primary.confidence)}</span>
            </div>
          </div>
          {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
        </button>

        {/* Expandable body */}
        {expanded && (
          <div className="px-4 pb-4 space-y-4 border-t border-slate-200/60 dark:border-slate-700/40">
            {/* Heatmap */}
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="space-y-1.5">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{t('showOriginal')}</p>
                <div className="overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-950 aspect-[4/3]">
                  <img src={originalB64} alt={t('original')} className="h-full w-full object-contain" />
                </div>
              </div>
              <div className="space-y-1.5">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Grad-CAM — {mr.model_label}
                </p>
                <div className="overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-950 aspect-[4/3]">
                  <img src={mr.heatmap_base64} alt={`Heatmap ${mr.model_label}`} className="h-full w-full object-contain" />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-xs"
                  onClick={() => downloadDataUri(mr.heatmap_base64, `scan-${scanId}-heatmap-${mr.model_type}.png`)}
                >
                  <Download className="mr-1.5 h-3.5 w-3.5" />
                  {t('downloadHeatmap')}
                </Button>
              </div>
            </div>

            {/* Predictions */}
            <PredictionBars predictions={mr.top_predictions} />

            {desc && (
              <div className="rounded-lg bg-slate-100 p-3 space-y-1 dark:bg-slate-800/60">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{t('description')}</p>
                <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{desc}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function ResultCard({ result, onNewScan, onReanalyze }: ResultCardProps) {
  const { language, t } = useAppStore()
  const consensusInfo = DISEASE_INFO_MAP[result.consensus_class_key]
  const consensusName = consensusInfo
    ? (language === 'pl' ? consensusInfo.pl : consensusInfo.en)
    : result.consensus_class_key

  // Models that agree with consensus
  const agreeing = result.model_results.filter(
    (mr) => mr.primary_prediction.class_key === result.consensus_class_key
  ).length
  const total = result.model_results.length

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Consensus banner */}
      <RiskBanner
        riskLevel={result.consensus_risk_level}
        diagnosisName={consensusName}
      />

      {/* Agreement summary */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {t('consensusTitle')}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                <span className="font-bold">{agreeing}/{total}</span> {t('modelsAgree')}
                {' · '}
                {t('avgConfidence')}: <span className="font-mono font-bold">{formatConfidence(result.consensus_confidence)}</span>
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="text-xs"
              onClick={() => downloadDataUri(result.original_image_base64, `scan-${result.scan_id}-original.png`)}
            >
              <Download className="mr-1.5 h-3.5 w-3.5" />
              {t('downloadImage')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Per-model cards */}
      <div className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {t('perModelResults')}
        </p>
        {result.model_results.map((mr, idx) => (
          <ModelCard
            key={mr.model_type}
            mr={mr}
            scanId={result.scan_id}
            originalB64={result.original_image_base64}
            idx={idx}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        {onReanalyze && (
          <Button className="flex-1 gap-2" onClick={onReanalyze}>
            <ScanLine className="h-4 w-4" />
            {t('reanalyze')}
          </Button>
        )}
        <Button variant="outline" className="flex-1 gap-2" onClick={onNewScan}>
          <RefreshCw className="h-4 w-4" />
          {t('newScan')}
        </Button>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-slate-500 border-t border-slate-200 dark:border-slate-800 pt-3">
        <span>
          {t('modelsUsed')}: {result.model_results.map((mr) => mr.model_label).join(', ')}
        </span>
        <span>ID: #{result.scan_id}</span>
      </div>
    </div>
  )
}
