import { ShieldCheck, Eye, AlertTriangle, Cpu, Flame, Radio, ZoomIn, Info } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAppStore } from '@/store/useAppStore'

const models = [
  { key: 'infoMobilenet', name: 'MobileNetV3', icon: '⚡' },
  { key: 'infoResnet', name: 'ResNet-50', icon: '🎯' },
  { key: 'infoCustomcnn', name: 'Custom CNN', icon: '🔬' },
  { key: 'infoVit', name: 'Vision Transformer (ViT)', icon: '🧠' },
]

const risks = [
  { level: 0 as const, variant: 'risk0' as const, icon: ShieldCheck, color: 'text-emerald-600 dark:text-emerald-400' },
  { level: 1 as const, variant: 'risk1' as const, icon: Eye, color: 'text-amber-600 dark:text-amber-400' },
  { level: 2 as const, variant: 'risk2' as const, icon: AlertTriangle, color: 'text-red-600 dark:text-red-400' },
]

export default function InfoPage() {
  const { t } = useAppStore()

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 space-y-10">
      {/* Title */}
      <div className="space-y-3">
        <h1 className="flex items-center gap-3 text-3xl font-bold">
          <Info className="h-8 w-8 text-blue-500" />
          {t('infoTitle')}
        </h1>
        <p className="text-base leading-relaxed text-slate-600 dark:text-slate-400">
          {t('infoIntro')}
        </p>
      </div>

      {/* Models */}
      <section className="space-y-4">
        <h2 className="flex items-center gap-2 text-xl font-semibold">
          <Cpu className="h-5 w-5 text-blue-500" />
          {t('infoModelsTitle')}
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">{t('infoModelsDesc')}</p>
        <div className="grid gap-3 sm:grid-cols-2">
          {models.map((m) => (
            <Card key={m.key}>
              <CardContent className="p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{m.icon}</span>
                  <h3 className="font-semibold">{m.name}</h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400">{t(m.key)}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Heatmap */}
      <section className="space-y-3">
        <h2 className="flex items-center gap-2 text-xl font-semibold">
          <Flame className="h-5 w-5 text-orange-500" />
          {t('infoHeatmapTitle')}
        </h2>
        <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
          {t('infoHeatmapDesc')}
        </p>
      </section>

      {/* Risk levels */}
      <section className="space-y-4">
        <h2 className="flex items-center gap-2 text-xl font-semibold">
          <ShieldCheck className="h-5 w-5 text-emerald-500" />
          {t('infoRiskTitle')}
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">{t('infoRiskDesc')}</p>
        <div className="space-y-3">
          {risks.map((r) => {
            const Icon = r.icon
            return (
              <div key={r.level} className="flex items-start gap-3 rounded-xl border border-slate-200 p-4 bg-white dark:border-slate-800 dark:bg-slate-900">
                <Icon className={`h-5 w-5 mt-0.5 ${r.color}`} />
                <div className="space-y-1">
                  <Badge variant={r.variant}>{t(`risk${r.level}`)}</Badge>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{t(`risk${r.level}sub`)}</p>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Live Camera */}
      <section className="space-y-4">
        <h2 className="flex items-center gap-2 text-xl font-semibold">
          <Radio className="h-5 w-5 text-purple-500" />
          {t('infoLiveTitle')}
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">{t('infoLiveDesc')}</p>

        <div className="grid gap-3 sm:grid-cols-2">
          <Card>
            <CardContent className="p-4 space-y-2">
              <h3 className="font-semibold flex items-center gap-2">📱 {t('sender')}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">{t('infoSenderDesc')}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 space-y-2">
              <h3 className="font-semibold flex items-center gap-2">🖥️ {t('viewer')}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">{t('infoViewerDesc')}</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Crop */}
      <section className="space-y-3">
        <h2 className="flex items-center gap-2 text-xl font-semibold">
          <ZoomIn className="h-5 w-5 text-blue-500" />
          {t('infoCropTitle')}
        </h2>
        <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
          {t('infoCropDesc')}
        </p>
      </section>

      {/* Disclaimer */}
      <Card className="border-amber-500/40 bg-amber-500/5">
        <CardContent className="p-5 space-y-2">
          <h2 className="text-lg font-semibold text-amber-600 dark:text-amber-400">
            {t('infoDisclaimerTitle')}
          </h2>
          <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
            {t('infoDisclaimer')}
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
