import { useMutation } from '@tanstack/react-query'
import api from './client'
import type { AnalyzeResponse } from '@/types/api'

export interface AnalyzeParams {
  file: File | Blob
  crop_factor: number
  auto_focus?: boolean
}

export async function analyzeImage(params: AnalyzeParams): Promise<AnalyzeResponse> {
  const form = new FormData()
  form.append('file', params.file, 'image.jpg')
  form.append('crop_factor', String(params.crop_factor))
  form.append('auto_focus', String(Boolean(params.auto_focus)))
  const { data } = await api.post<AnalyzeResponse>('/api/v1/analyze', form)
  return data
}

export function useAnalyzeMutation() {
  return useMutation({ mutationFn: analyzeImage })
}
