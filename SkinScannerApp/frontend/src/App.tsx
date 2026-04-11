import { Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { Layout } from '@/components/layout/Layout'
import { Skeleton } from '@/components/ui/skeleton'

const ScannerPage = lazy(() => import('@/pages/ScannerPage'))
const HistoryPage = lazy(() => import('@/pages/HistoryPage'))
const LiveCameraPage = lazy(() => import('@/pages/LiveCameraPage'))
const BodyMapPage = lazy(() => import('@/pages/BodyMapPage'))
const InfoPage = lazy(() => import('@/pages/InfoPage'))

function PageFallback() {
  return (
    <div className="mx-auto max-w-2xl space-y-4 px-4 py-8">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-64 w-full" />
      <Skeleton className="h-12 w-full" />
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route
          path="/"
          element={
            <Suspense fallback={<PageFallback />}>
              <ScannerPage />
            </Suspense>
          }
        />
        <Route
          path="/history"
          element={
            <Suspense fallback={<PageFallback />}>
              <HistoryPage />
            </Suspense>
          }
        />
        <Route
          path="/live"
          element={
            <Suspense fallback={<PageFallback />}>
              <LiveCameraPage />
            </Suspense>
          }
        />
        <Route
          path="/bodymap"
          element={
            <Suspense fallback={<PageFallback />}>
              <BodyMapPage />
            </Suspense>
          }
        />
        <Route
          path="/info"
          element={
            <Suspense fallback={<PageFallback />}>
              <InfoPage />
            </Suspense>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
