import { useEffect, useRef } from 'react'
import { Camera, RotateCcw, SwitchCamera, AlertCircle, Loader2 } from 'lucide-react'
import { useCamera } from '@/hooks/useCamera'
import { useAppStore } from '@/store/useAppStore'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface CameraCaptureProps {
  onCapture: (file: File, previewUrl: string) => void
}

export function CameraCapture({ onCapture }: CameraCaptureProps) {
  const t = useAppStore((s) => s.t)
  const { videoRef, stream, devices, selectedDevice, isStarting, error, selectDevice, startCamera, stopCamera, capture } =
    useCamera()
  const started = useRef(false)

  // Auto-start on mount
  useEffect(() => {
    if (!started.current) {
      started.current = true
      startCamera()
    }
    return () => stopCamera()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleCapture = async () => {
    try {
      const file = await capture()
      const url = URL.createObjectURL(file)
      onCapture(file, url)
    } catch {
      // handled by error state
    }
  }

  const handleDeviceChange = (deviceId: string) => {
    selectDevice(deviceId)
    startCamera(deviceId)
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Video preview */}
      <div className="relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-900 aspect-[4/3]">
        {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="h-full w-full object-cover"
        />
        {!stream && !isStarting && !error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-100 dark:bg-slate-900">
            <Camera className="h-12 w-12 text-slate-600" />
            <p className="text-sm text-slate-500">{t('noCamera')}</p>
          </div>
        )}
        {isStarting && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-100 dark:bg-slate-900">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-100 dark:bg-slate-900 p-4">
            <AlertCircle className="h-10 w-10 text-red-400" />
            <p className="text-center text-sm text-red-400">{t('cameraPermissionDenied')}</p>
            <Button variant="outline" size="sm" onClick={() => startCamera()}>
              <RotateCcw className="h-4 w-4" />
              {t('retry')}
            </Button>
          </div>
        )}
      </div>

      {/* Camera selector (shown when >1 camera) */}
      {devices.length > 1 && (
        <Select value={selectedDevice} onValueChange={handleDeviceChange}>
          <SelectTrigger>
            <SwitchCamera className="h-4 w-4 text-slate-400" />
            <SelectValue placeholder={t('selectCamera')} />
          </SelectTrigger>
          <SelectContent>
            {devices.map((d) => (
              <SelectItem key={d.deviceId} value={d.deviceId}>
                {d.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {/* Capture button */}
      <Button
        onClick={handleCapture}
        disabled={!stream || isStarting}
        size="lg"
        className="w-full"
      >
        <Camera className="h-5 w-5" />
        {t('capturePhoto')}
      </Button>
    </div>
  )
}
