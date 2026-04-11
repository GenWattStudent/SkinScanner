import { useState, useCallback, useRef, useEffect } from 'react'
import { ZoomIn, Check, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { useAppStore } from '@/store/useAppStore'

interface ImageCropperProps {
  imageUrl: string
  onCropComplete: (croppedFile: File, croppedUrl: string) => void
  onCancel: () => void
}

export function ImageCropper({ imageUrl, onCropComplete, onCancel }: ImageCropperProps) {
  const t = useAppStore((s) => s.t)
  const [cropFactor, setCropFactor] = useState(0)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)

  // Load and draw image
  useEffect(() => {
    const img = new Image()
    img.onload = () => {
      if (imgRef.current) {
        imgRef.current = img
        drawCropped(cropFactor)
      }
    }
    img.src = imageUrl
    imgRef.current = img
  }, [imageUrl])

  const drawCropped = useCallback((factor: number) => {
    const canvas = canvasRef.current
    const img = imgRef.current
    if (!canvas || !img || !img.complete) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Calculate crop dimensions
    const cropPx = Math.floor(Math.min(img.width, img.height) * factor)
    const sx = cropPx
    const sy = cropPx
    const sWidth = img.width - 2 * cropPx
    const sHeight = img.height - 2 * cropPx

    // Set canvas size to cropped size
    canvas.width = sWidth
    canvas.height = sHeight

    // Draw cropped image
    ctx.drawImage(img, sx, sy, sWidth, sHeight, 0, 0, sWidth, sHeight)
  }, [])

  useEffect(() => {
    drawCropped(cropFactor)
  }, [cropFactor, drawCropped])

  const handleApply = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    canvas.toBlob(
      (blob) => {
        if (!blob) return
        const croppedFile = new File([blob], 'cropped.jpg', { type: 'image/jpeg' })
        const croppedUrl = URL.createObjectURL(blob)
        onCropComplete(croppedFile, croppedUrl)
      },
      'image/jpeg',
      0.92,
    )
  }, [onCropComplete])

  return (
    <div className="space-y-4">
      {/* Preview */}
      <div className="relative overflow-hidden rounded-xl border-2 border-blue-500 bg-slate-50 dark:bg-slate-900">
        <canvas
          ref={canvasRef}
          className="w-full max-h-96 object-contain"
        />
        {cropFactor > 0 && (
          <span className="absolute top-2 right-2 rounded-md bg-blue-500 px-2 py-1 text-xs font-medium text-white backdrop-blur">
            Crop {Math.round(cropFactor * 100)}%
          </span>
        )}
      </div>

      {/* Crop slider */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm font-medium">
            <ZoomIn className="h-4 w-4" />
            {t('cropFactor')}
          </label>
          <span className="font-mono text-sm text-blue-500">
            {Math.round(cropFactor * 100)}%
          </span>
        </div>
        <Slider
          min={0}
          max={0.4}
          step={0.01}
          value={[cropFactor]}
          onValueChange={([v]) => setCropFactor(v)}
        />
        <p className="text-xs text-slate-500">{t('cropFactorHint')}</p>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          variant="outline"
          className="flex-1"
          onClick={onCancel}
        >
          <X className="h-4 w-4 mr-1.5" />
          {t('cancel')}
        </Button>
        <Button
          className="flex-1"
          onClick={handleApply}
        >
          <Check className="h-4 w-4 mr-1.5" />
          {t('apply')}
        </Button>
      </div>
    </div>
  )
}
