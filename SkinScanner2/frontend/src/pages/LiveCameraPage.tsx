import { useState, useCallback } from 'react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Loader2, Radio, Eye, Camera, ScanLine } from 'lucide-react'
import { useCamera } from '@/hooks/useCamera'
import { useCameraSender, useCameraViewer } from '@/hooks/useCameraStream'
import { useAnalyzeMutation } from '@/api/analyze'
import { ResultCard } from '@/components/scanner/ResultCard'
import { useAppStore } from '@/store/useAppStore'
import type { AnalyzeResponse } from '@/types/api'

/* ─── Sender panel ──────────────────────────────────────────────── */
function SenderPanel() {
  const { t } = useAppStore()
  const {
    videoRef,
    devices,
    selectedDevice,
    isStarting,
    stream,
    selectDevice,
    startCamera,
    stopCamera,
    capture,
  } = useCamera()

  const { status: wsStatus, startSending, stopSending } = useCameraSender()
  const isSending = wsStatus === 'connected'
  const isStreaming = !!stream

  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const { mutate, isPending } = useAnalyzeMutation()

  const handleCapture = useCallback(async () => {
    const file = await capture()
    mutate(
      { file, crop_factor: 0 },
      { onSuccess: (data) => setResult(data) },
    )
  }, [capture, mutate])

  const handleToggleSend = useCallback(() => {
    if (!videoRef.current) return
    if (isSending) {
      stopSending()
    } else {
      startSending(videoRef.current)
    }
  }, [isSending, videoRef, startSending, stopSending])

  if (result)
    return (
      <ResultCard result={result} onNewScan={() => { setResult(null); startCamera() }} />
    )

  return (
    <div className="space-y-4">
      {/* Device selector */}
      {devices.length > 1 && (
        <select
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
          value={selectedDevice}
          onChange={(e) => selectDevice(e.target.value)}
        >
          {devices.map((d) => (
            <option key={d.deviceId} value={d.deviceId}>
              {d.label || d.deviceId}
            </option>
          ))}
        </select>
      )}

      {/* Video */}
      <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
        <video ref={videoRef} autoPlay playsInline muted className="w-full max-h-72 object-cover" />
        {!isStreaming && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-500 text-sm">
            {t('cameraOff')}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-2">
        {!isStreaming ? (
          <Button className="flex-1 gap-2" disabled={isStarting} onClick={() => startCamera()}>
            <Camera className="h-4 w-4" />
            {t('startCamera')}
          </Button>
        ) : (
          <Button variant="outline" className="flex-1 gap-2" onClick={stopCamera}>
            {t('stopCamera')}
          </Button>
        )}

        {isStreaming && (
          <>
            <Button
              variant={isSending ? 'destructive' : 'secondary'}
              className="flex-1 gap-2"
              onClick={handleToggleSend}
            >
              <Radio className="h-4 w-4" />
              {isSending ? t('stopStream') : t('startStream')}
            </Button>
            <Button
              className="flex-1 gap-2"
              disabled={isPending}
              onClick={handleCapture}
            >
              {isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <ScanLine className="h-4 w-4" />
              )}
              {t('captureAnalyze')}
            </Button>
          </>
        )}
      </div>
    </div>
  )
}

/* ─── Viewer panel ──────────────────────────────────────────────── */
function ViewerPanel() {
  const { t } = useAppStore()
  const { frameUrl, status, captureCurrentFrame, connect, disconnect } = useCameraViewer()
  const isConnected = status === 'connected'

  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const { mutate, isPending } = useAnalyzeMutation()

  const handleCapture = () => {
    const file = captureCurrentFrame()
    if (!file) return
    mutate(
      { file, crop_factor: 0 },
      { onSuccess: (data) => setResult(data) },
    )
  }

  if (result)
    return (
      <ResultCard result={result} onNewScan={() => setResult(null)} />
    )

  return (
    <div className="space-y-4">
      <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
        {frameUrl ? (
          <img src={frameUrl} alt="live frame" className="w-full max-h-72 object-cover" />
        ) : (
          <div className="flex h-48 items-center justify-center text-slate-500 text-sm">
            {isConnected ? t('waitingFrames') : t('notConnected')}
          </div>
        )}
        {isConnected && (
          <span className="absolute top-2 right-2 flex items-center gap-1 rounded-full bg-white/80 px-2 py-0.5 text-xs text-emerald-600 dark:bg-slate-900/80 dark:text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            LIVE
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {!isConnected ? (
          <Button className="flex-1 gap-2" onClick={connect}>
            <Eye className="h-4 w-4" />
            {t('connectViewer')}
          </Button>
        ) : (
          <Button variant="outline" className="flex-1 gap-2" onClick={disconnect}>
            {t('disconnectViewer')}
          </Button>
        )}
        {frameUrl && (
          <Button
            className="flex-1 gap-2"
            disabled={isPending}
            onClick={handleCapture}
          >
            {isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ScanLine className="h-4 w-4" />
            )}
            {t('captureAnalyze')}
          </Button>
        )}
      </div>
    </div>
  )
}

/* ─── Page ──────────────────────────────────────────────────────── */
export default function LiveCameraPage() {
  const { t } = useAppStore()
  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold">{t('liveTitle')}</h1>
      <Tabs defaultValue="sender">
        <TabsList className="mb-6 w-full grid grid-cols-2 border border-slate-200 dark:border-slate-800">
          <TabsTrigger value="sender" className="gap-2">
            <Radio className="h-4 w-4" />
            {t('sender')}
          </TabsTrigger>
          <TabsTrigger value="viewer" className="gap-2">
            <Eye className="h-4 w-4" />
            {t('viewer')}
          </TabsTrigger>
        </TabsList>
        <TabsContent value="sender">
          <SenderPanel />
        </TabsContent>
        <TabsContent value="viewer">
          <ViewerPanel />
        </TabsContent>
      </Tabs>
    </div>
  )
}
