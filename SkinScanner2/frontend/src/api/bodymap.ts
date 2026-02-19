import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './client'
import type {
  BodyMapMarker,
  BodyMapMarkerCreate,
  BodyMapMarkerList,
  BodyMapMarkerUpdate,
} from '@/types/api'

const MARKERS_KEY = 'bodymap-markers' as const

// ── Fetch all for a patient ───────────────────────────────────────────────────

async function fetchMarkers(patientId: number): Promise<BodyMapMarkerList> {
  const { data } = await api.get<BodyMapMarkerList>('/api/v1/bodymap/markers', {
    params: { patient_id: patientId },
  })
  return data
}

export function useBodyMapMarkers(patientId: number | null) {
  return useQuery({
    queryKey: [MARKERS_KEY, patientId],
    queryFn: () => fetchMarkers(patientId!),
    enabled: patientId !== null,
  })
}

// ── Create ────────────────────────────────────────────────────────────────────

async function createMarker(payload: BodyMapMarkerCreate): Promise<BodyMapMarker> {
  const { data } = await api.post<BodyMapMarker>('/api/v1/bodymap/markers', payload)
  return data
}

export function useCreateMarker() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createMarker,
    onSuccess: () => qc.invalidateQueries({ queryKey: [MARKERS_KEY] }),
  })
}

// ── Update ────────────────────────────────────────────────────────────────────

async function updateMarker({
  id,
  ...payload
}: BodyMapMarkerUpdate & { id: number }): Promise<BodyMapMarker> {
  const { data } = await api.patch<BodyMapMarker>(
    `/api/v1/bodymap/markers/${id}`,
    payload,
  )
  return data
}

export function useUpdateMarker() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updateMarker,
    onSuccess: () => qc.invalidateQueries({ queryKey: [MARKERS_KEY] }),
  })
}

// ── Delete ────────────────────────────────────────────────────────────────────

async function deleteMarker(id: number): Promise<void> {
  await api.delete(`/api/v1/bodymap/markers/${id}`)
}

export function useDeleteMarker() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteMarker,
    onSuccess: () => qc.invalidateQueries({ queryKey: [MARKERS_KEY] }),
  })
}
