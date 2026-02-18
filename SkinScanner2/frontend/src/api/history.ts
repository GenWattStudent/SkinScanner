import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './client'
import type { HistoryEntry, HistoryList } from '@/types/api'

// ── Fetch list ────────────────────────────────────────────────────────────────

export async function fetchHistory(page = 1, limit = 15): Promise<HistoryList> {
  const { data } = await api.get<HistoryList>('/api/v1/history', {
    params: { page, limit },
  })
  return data
}

export function useHistory(page = 1, limit = 15) {
  return useQuery({
    queryKey: ['history', page, limit],
    queryFn: () => fetchHistory(page, limit),
  })
}

// ── Fetch single ──────────────────────────────────────────────────────────────

export async function fetchHistoryEntry(id: number): Promise<HistoryEntry> {
  const { data } = await api.get<HistoryEntry>(`/api/v1/history/${id}`)
  return data
}

// ── Delete ────────────────────────────────────────────────────────────────────

export async function deleteHistoryEntry(id: number): Promise<void> {
  await api.delete(`/api/v1/history/${id}`)
}

export function useDeleteHistory() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteHistoryEntry,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['history'] }),
  })
}

// ── Image URL helper ──────────────────────────────────────────────────────────

/** Absolute URL for the original image served by the backend. */
export function historyImageUrl(entryId: number, kind: 'original'): string {
  return `/api/v1/history/${entryId}/image/${kind}`
}

/** Absolute URL for a per-model heatmap served by the backend. */
export function historyHeatmapUrl(entryId: number, modelType: string): string {
  return `/api/v1/history/${entryId}/image/heatmap/${modelType}`
}
