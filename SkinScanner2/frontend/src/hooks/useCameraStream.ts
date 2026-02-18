import { useCallback, useEffect, useRef, useState } from 'react'
import { getWsBase } from '@/lib/utils'

type StreamMode = 'sender' | 'viewer'
type WsStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'

// ── Sender hook ───────────────────────────────────────────────────────────────

export interface UseCameraSenderReturn {
  status: WsStatus
  startSending: (videoEl: HTMLVideoElement, fps?: number) => void
  stopSending: () => void
}

export function useCameraSender(): UseCameraSenderReturn {
  const wsRef = useRef<WebSocket | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const [status, setStatus] = useState<WsStatus>('idle')

  const stopSending = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    wsRef.current?.close()
    wsRef.current = null
    setStatus('idle')
  }, [])

  const startSending = useCallback(
    (videoEl: HTMLVideoElement, fps = 8) => {
      stopSending()
      const url = `${getWsBase()}/ws/camera/send`
      setStatus('connecting')
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        setStatus('connected')
        intervalRef.current = setInterval(() => {
          if (ws.readyState !== WebSocket.OPEN) return
          const canvas = document.createElement('canvas')
          canvas.width = videoEl.videoWidth || 640
          canvas.height = videoEl.videoHeight || 480
          canvas.getContext('2d')!.drawImage(videoEl, 0, 0)
          canvas.toBlob(
            (blob) => {
              if (blob && ws.readyState === WebSocket.OPEN) {
                blob.arrayBuffer().then((buf) => ws.send(buf))
              }
            },
            'image/jpeg',
            0.7,
          )
        }, 1000 / fps)
      }
      ws.onclose = () => {
        setStatus('disconnected')
        if (intervalRef.current) clearInterval(intervalRef.current)
      }
      ws.onerror = () => setStatus('error')
    },
    [stopSending],
  )

  useEffect(() => () => stopSending(), [stopSending])

  return { status, startSending, stopSending }
}

// ── Viewer hook ───────────────────────────────────────────────────────────────

export interface UseCameraViewerReturn {
  frameUrl: string | null
  status: WsStatus
  connect: () => void
  disconnect: () => void
  captureCurrentFrame: () => File | null
}

export function useCameraViewer(): UseCameraViewerReturn {
  const wsRef = useRef<WebSocket | null>(null)
  const currentBlobRef = useRef<Blob | null>(null)
  const prevUrlRef = useRef<string | null>(null)
  const [frameUrl, setFrameUrl] = useState<string | null>(null)
  const [status, setStatus] = useState<WsStatus>('idle')

  const disconnect = useCallback(() => {
    wsRef.current?.close()
    wsRef.current = null
    setStatus('idle')
  }, [])

  const connect = useCallback(() => {
    disconnect()
    const url = `${getWsBase()}/ws/camera/view`
    setStatus('connecting')
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setStatus('connected')
    ws.onmessage = (e: MessageEvent<Blob | ArrayBuffer>) => {
      const blob = e.data instanceof Blob ? e.data : new Blob([e.data], { type: 'image/jpeg' })
      currentBlobRef.current = blob
      const url = URL.createObjectURL(blob)
      // Revoke previous object URL to avoid memory leaks
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current)
      prevUrlRef.current = url
      setFrameUrl(url)
    }
    ws.onclose = () => setStatus('disconnected')
    ws.onerror = () => setStatus('error')
  }, [disconnect])

  /** Capture the latest received frame as a File for analysis. */
  const captureCurrentFrame = useCallback((): File | null => {
    if (!currentBlobRef.current) return null
    return new File([currentBlobRef.current], 'live-capture.jpg', { type: 'image/jpeg' })
  }, [])

  useEffect(() => () => disconnect(), [disconnect])

  return { frameUrl, status, connect, disconnect, captureCurrentFrame }
}
