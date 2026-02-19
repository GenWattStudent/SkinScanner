import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './client'
import type {
  Patient,
  PatientCreate,
  PatientList,
  PatientUpdate,
} from '@/types/api'

const PATIENTS_KEY = ['patients'] as const

// ── Fetch all ─────────────────────────────────────────────────────────────────

async function fetchPatients(): Promise<PatientList> {
  const { data } = await api.get<PatientList>('/api/v1/patients')
  return data
}

export function usePatients() {
  return useQuery({
    queryKey: PATIENTS_KEY,
    queryFn: fetchPatients,
  })
}

// ── Create ────────────────────────────────────────────────────────────────────

async function createPatient(payload: PatientCreate): Promise<Patient> {
  const { data } = await api.post<Patient>('/api/v1/patients', payload)
  return data
}

export function useCreatePatient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createPatient,
    onSuccess: () => qc.invalidateQueries({ queryKey: PATIENTS_KEY }),
  })
}

// ── Update ────────────────────────────────────────────────────────────────────

async function updatePatient({
  id,
  ...payload
}: PatientUpdate & { id: number }): Promise<Patient> {
  const { data } = await api.patch<Patient>(`/api/v1/patients/${id}`, payload)
  return data
}

export function useUpdatePatient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updatePatient,
    onSuccess: () => qc.invalidateQueries({ queryKey: PATIENTS_KEY }),
  })
}

// ── Delete ────────────────────────────────────────────────────────────────────

async function deletePatient(id: number): Promise<void> {
  await api.delete(`/api/v1/patients/${id}`)
}

export function useDeletePatient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deletePatient,
    onSuccess: () => qc.invalidateQueries({ queryKey: PATIENTS_KEY }),
  })
}
