import { useState, useCallback } from 'react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Loader2, ScanLine, ScanSearch } from 'lucide-react'
import { ImageUpload } from '@/components/scanner/ImageUpload'
import { CameraCapture } from '@/components/scanner/CameraCapture'
import { ImageCropper } from '@/components/scanner/ImageCropper'
import { ResultCard } from '@/components/scanner/ResultCard'
import { useAnalyzeMutation } from '@/api/analyze'
import { useAppStore } from '@/store/useAppStore'
import type { AnalyzeResponse } from '@/types/api'

export default function ScannerPage() {
  const { t } = useAppStore()
  const [originalFile, setOriginalFile] = useState<File | null>(null)
  const [originalPreview, setOriginalPreview] = useState<string | null>(null)
  const [croppedFile, setCroppedFile] = useState<File | null>(null)
  const [croppedPreview, setCroppedPreview] = useState<string | null>(null)
  const [showCropper, setShowCropper] = useState(false)
  const [autoFocus, setAutoFocus] = useState(false)
  const [result, setResult] = useState<AnalyzeResponse | null>(null)

  const { mutate, isPending } = useAnalyzeMutation()

  // Handle initial file selection (from upload or camera)
  const handleFile = useCallback((f: File, url: string) => {
    setOriginalFile(f)
    setOriginalPreview(url)
    setCroppedFile(null)
    setCroppedPreview(null)
    setAutoFocus(false)
    setResult(null)
    setShowCropper(true) // Show cropper after selection
  }, [])

  // Handle crop completion
  const handleCropComplete = useCallback((f: File, url: string) => {
    setCroppedFile(f)
    setCroppedPreview(url)
    setShowCropper(false)
  }, [])

  // Handle crop cancel - use original file
  const handleCropCancel = useCallback(() => {
    setCroppedFile(originalFile)
    setCroppedPreview(originalPreview)
    setShowCropper(false)
  }, [originalFile, originalPreview])

  /** Only clear the image entirely */
  const handleNewImage = useCallback(() => {
    setOriginalFile(null)
    setOriginalPreview(null)
    setCroppedFile(null)
    setCroppedPreview(null)
    setAutoFocus(false)
    setResult(null)
    setShowCropper(false)
  }, [])

  /** Keep the current image, clear result so user can pick new model & re-scan */
  const handleReanalyze = useCallback(() => {
    setResult(null)
  }, [])

  const handleAnalyze = () => {
    const fileToAnalyze = croppedFile || originalFile
    if (!fileToAnalyze) return
    // crop_factor = 0 because cropping already done on frontend
    mutate(
      { file: fileToAnalyze, crop_factor: 0, auto_focus: autoFocus },
      { onSuccess: (data) => setResult(data) },
    )
  }

  /* ── Result view ─────────────────────────────────────── */
  if (result)
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <ResultCard
          result={result}
          onNewScan={handleNewImage}
          onReanalyze={handleReanalyze}
        />
      </div>
    )

  /* ── Input view ──────────────────────────────────────── */
  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold">{t('scannerTitle')}</h1>

      {/* Show cropper if image selected and not yet cropped */}
      {showCropper && originalPreview ? (
        <ImageCropper
          imageUrl={originalPreview}
          onCropComplete={handleCropComplete}
          onCancel={handleCropCancel}
        />
      ) : !croppedPreview ? (
        /* Show upload/camera tabs when no image */
        <Tabs defaultValue="upload">
          <TabsList className="mb-6 w-full grid grid-cols-2 border border-slate-200 dark:border-slate-800">
            <TabsTrigger value="upload">{t('uploadTab')}</TabsTrigger>
            <TabsTrigger value="camera">{t('cameraTab')}</TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <ImageUpload onImageSelected={handleFile} />
          </TabsContent>
          <TabsContent value="camera">
            <CameraCapture onCapture={handleFile} />
          </TabsContent>
        </Tabs>
      ) : (
        /* Show cropped preview and analyze button */
        <div className="space-y-4">
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
            <img src={croppedPreview} alt="preview" className="w-full max-h-96 object-contain" />
          </div>

          {/* Clear & Zoom toggle with hint */}
          <div
            className={`flex items-center justify-between rounded-lg border px-4 py-2.5 transition-colors cursor-pointer select-none ${
              autoFocus
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40'
                : 'border-slate-200 dark:border-slate-700'
            }`}
            onClick={() => setAutoFocus((v) => !v)}
            role="button"
            aria-pressed={autoFocus}
          >
            <div className="flex items-center gap-2">
              <ScanSearch className={`h-5 w-5 ${autoFocus ? 'text-blue-500' : 'text-slate-400'}`} />
              <div>
                <p className={`text-sm font-medium ${autoFocus ? 'text-blue-600 dark:text-blue-400' : ''}`}>
                  {t('clearAndZoom')}
                </p>
                <p className="text-xs text-slate-500">{t('clearAndZoomHint')}</p>
              </div>
            </div>
            <div className={`h-5 w-9 rounded-full transition-colors ${
              autoFocus ? 'bg-blue-500' : 'bg-slate-300 dark:bg-slate-600'
            }`}>
              <div className={`mt-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${
                autoFocus ? 'translate-x-4.5 ml-0.5' : 'ml-0.5'
              }`} />
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => setShowCropper(true)}
            >
              {t('reanalyze')} Crop
            </Button>
            <Button
              className="flex-1 gap-2"
              size="lg"
              disabled={isPending}
              onClick={handleAnalyze}
            >
              {isPending ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  {t('analyzing')}
                </>
              ) : (
                <>
                  <ScanLine className="h-5 w-5" />
                  {t('analyze')}
                </>
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
