import { useCallback, useRef, useState } from 'react'
import { UploadCloud, ImageIcon } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'

interface ImageUploadProps {
  onImageSelected: (file: File, previewUrl: string) => void
}

export function ImageUpload({ onImageSelected }: ImageUploadProps) {
  const t = useAppStore((s) => s.t)
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const processFile = useCallback(
    (file: File) => {
      if (!file.type.startsWith('image/')) return
      const url = URL.createObjectURL(file)
      onImageSelected(file, url)
    },
    [onImageSelected],
  )

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) processFile(file)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) processFile(file)
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => inputRef.current?.click()}
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={cn(
        'flex flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed p-12 text-center transition-all cursor-pointer select-none',
        isDragging
          ? 'border-blue-500 bg-blue-500/5'
          : 'border-slate-300 bg-slate-50 hover:border-slate-400 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900/50 dark:hover:border-slate-600 dark:hover:bg-slate-900',
      )}
    >
      <div
        className={cn(
          'flex h-16 w-16 items-center justify-center rounded-full transition-colors',
          isDragging ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400',
        )}
      >
        {isDragging ? (
          <ImageIcon className="h-8 w-8" />
        ) : (
          <UploadCloud className="h-8 w-8" />
        )}
      </div>
      <div>
        <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{t('dropzone')}</p>
        <p className="mt-1 text-xs text-slate-500">{t('dropzoneHint')}</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleChange}
      />
    </div>
  )
}
