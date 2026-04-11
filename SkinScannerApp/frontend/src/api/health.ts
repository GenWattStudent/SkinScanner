import { useQuery } from '@tanstack/react-query'
import api from './client'
import type { HealthCheck, ModelInfo } from '@/types/api'

export async function fetchHealth(): Promise<HealthCheck> {
  const { data } = await api.get<HealthCheck>('/api/v1/health')
  return data
}

export async function fetchModels(): Promise<ModelInfo[]> {
  const { data } = await api.get<ModelInfo[]>('/api/v1/models')
  return data
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: false,
  })
}

export function useModels() {
  return useQuery({
    queryKey: ['models'],
    queryFn: fetchModels,
    staleTime: Infinity,
  })
}
