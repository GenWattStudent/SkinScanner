import { useCallback, useEffect, useRef, useState } from 'react'

export interface CameraDevice {
  deviceId: string
  label: string
}

export interface UseCameraReturn {
  videoRef: React.RefObject<HTMLVideoElement>
  stream: MediaStream | null
  devices: CameraDevice[]
  selectedDevice: string
  isStarting: boolean
  error: string | null
  selectDevice: (deviceId: string) => void
  startCamera: (deviceId?: string) => Promise<void>
  stopCamera: () => void
  capture: () => Promise<File>
}

export function useCamera(): UseCameraReturn {
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [devices, setDevices] = useState<CameraDevice[]>([])
  const [selectedDevice, setSelectedDevice] = useState<string>('')
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Enumerate all video input devices
  const enumerateDevices = useCallback(async () => {
    try {
      const all = await navigator.mediaDevices.enumerateDevices()
      const cameras = all
        .filter((d) => d.kind === 'videoinput')
        .map((d, i) => ({
          deviceId: d.deviceId,
          label: d.label || `Camera ${i + 1}`,
        }))
      setDevices(cameras)
      if (cameras.length > 0 && !selectedDevice) {
        setSelectedDevice(cameras[0].deviceId)
      }
    } catch {
      // Ignore – might not have permission yet
    }
  }, [selectedDevice])

  useEffect(() => {
    enumerateDevices()
    navigator.mediaDevices.addEventListener('devicechange', enumerateDevices)
    return () => navigator.mediaDevices.removeEventListener('devicechange', enumerateDevices)
  }, [enumerateDevices])

  const startCamera = useCallback(
    async (deviceId?: string) => {
      setIsStarting(true)
      setError(null)
      try {
        // Stop previous stream
        streamRef.current?.getTracks().forEach((t) => t.stop())

        const id = deviceId ?? selectedDevice
        const constraints: MediaStreamConstraints = {
          video: id
            ? { deviceId: { exact: id }, width: { ideal: 1920 }, height: { ideal: 1080 } }
            : {
                facingMode: { ideal: 'environment' },
                width: { min: 640, ideal: 1920, max: 4096 },
                height: { min: 480, ideal: 1080, max: 4096 },
              },
          audio: false,
        }
        const newStream = await navigator.mediaDevices.getUserMedia(constraints)
        streamRef.current = newStream
        setStream(newStream)
        if (videoRef.current) {
          videoRef.current.srcObject = newStream
          await videoRef.current.play()
        }
        // Now enumerate with labels (need permission first)
        await enumerateDevices()
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : 'Camera access denied')
      } finally {
        setIsStarting(false)
      }
    },
    [selectedDevice, enumerateDevices],
  )

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    setStream(null)
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
  }, [])

  /** Capture a still JPEG frame from the current video stream. */
  const capture = useCallback((): Promise<File> => {
    const video = videoRef.current
    if (!video) return Promise.reject(new Error('No video element'))
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d')!.drawImage(video, 0, 0)
    return new Promise((resolve, reject) =>
      canvas.toBlob(
        (blob) => {
          if (!blob) return reject(new Error('Capture failed'))
          resolve(new File([blob], 'camera.jpg', { type: 'image/jpeg' }))
        },
        'image/jpeg',
        0.92,
      ),
    )
  }, [])

  // Cleanup on unmount
  useEffect(() => () => stopCamera(), [stopCamera])

  return {
    videoRef,
    stream,
    devices,
    selectedDevice,
    isStarting,
    error,
    selectDevice: setSelectedDevice,
    startCamera,
    stopCamera,
    capture,
  }
}
