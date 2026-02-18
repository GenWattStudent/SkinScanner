import { useMutation } from '@tanstack/react-query'
import api from './client'
import type { AnalyzeResponse } from '@/types/api'

export interface AnalyzeParams {
  file: File | Blob
  crop_factor: number
}

export async function analyzeImage(params: AnalyzeParams): Promise<AnalyzeResponse> {
  const form = new FormData()
  form.append('file', params.file, 'image.jpg')
  form.append('crop_factor', String(params.crop_factor))
  const { data } = await api.post<AnalyzeResponse>('/api/v1/analyze', form)
  return data
}

export function useAnalyzeMutation() {
  return useMutation({ mutationFn: analyzeImage })
}
