/**
 * PatientSelector – dropdown + inline create/edit for choosing the active patient.
 *
 * Shows a select dropdown with existing patients.  The user can also type a new
 * patient name and create one on the fly.
 */

import { useState } from 'react'
import type { Patient } from '@/types/api'
import { useAppStore } from '@/store/useAppStore'
import { usePatients, useCreatePatient, useDeletePatient, useUpdatePatient } from '@/api/patient'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { UserPlus, Pencil, Trash2 } from 'lucide-react'

interface PatientSelectorProps {
  selectedId: number | null
  onSelect: (id: number | null) => void
}

export function PatientSelector({ selectedId, onSelect }: PatientSelectorProps) {
  const t = useAppStore((s) => s.t)
  const { data, isLoading } = usePatients()
  const createMutation = useCreatePatient()
  const updateMutation = useUpdatePatient()
  const deleteMutation = useDeletePatient()

  const patients = data?.items ?? []

  const [dialogMode, setDialogMode] = useState<'create' | 'edit' | null>(null)
  const [editPatient, setEditPatient] = useState<Patient | null>(null)
  const [name, setName] = useState('')
  const [notes, setNotes] = useState('')

  const openCreate = () => {
    setName('')
    setNotes('')
    setDialogMode('create')
  }

  const openEdit = () => {
    const patient = patients.find((p) => p.id === selectedId)
    if (!patient) return
    setEditPatient(patient)
    setName(patient.name)
    setNotes(patient.notes ?? '')
    setDialogMode('edit')
  }

  const handleSubmit = () => {
    if (!name.trim()) return
    if (dialogMode === 'create') {
      createMutation.mutate(
        { name: name.trim(), notes: notes.trim() || null },
        {
          onSuccess: (created) => {
            onSelect(created.id)
            setDialogMode(null)
          },
        },
      )
    } else if (dialogMode === 'edit' && editPatient) {
      updateMutation.mutate(
        { id: editPatient.id, name: name.trim(), notes: notes.trim() || null },
        { onSuccess: () => setDialogMode(null) },
      )
    }
  }

  const handleDelete = () => {
    if (!selectedId) return
    if (window.confirm(t('patientDeleteConfirm'))) {
      deleteMutation.mutate(selectedId, {
        onSuccess: () => {
          onSelect(null)
        },
      })
    }
  }

  return (
    <div className="flex items-center gap-2">
      {/* Select dropdown */}
      <Select
        value={selectedId?.toString() ?? ''}
        onValueChange={(val) => onSelect(val ? Number(val) : null)}
        disabled={isLoading}
      >
        <SelectTrigger className="h-9 w-56 text-sm">
          <SelectValue placeholder={t('patientSelect')} />
        </SelectTrigger>
        <SelectContent>
          {patients.map((p) => (
            <SelectItem key={p.id} value={p.id.toString()}>
              <span className="flex items-center gap-2">
                {p.name}
                {p.marker_count > 0 && (
                  <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                    {p.marker_count}
                  </Badge>
                )}
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Quick actions */}
      <Button size="sm" variant="outline" onClick={openCreate} title={t('patientAdd')}>
        <UserPlus className="h-4 w-4" />
      </Button>
      {selectedId && (
        <>
          <Button size="sm" variant="ghost" onClick={openEdit} title={t('patientEdit')}>
            <Pencil className="h-3.5 w-3.5" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={handleDelete}
            className="text-red-500 hover:text-red-600"
            title={t('patientDelete')}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </>
      )}

      {/* Create / Edit dialog */}
      <Dialog open={dialogMode !== null} onOpenChange={(open) => !open && setDialogMode(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {dialogMode === 'create' ? t('patientAdd') : t('patientEdit')}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="patient-name" className="text-xs">
                {t('patientName')}
              </Label>
              <Input
                id="patient-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={t('patientNamePlaceholder')}
                maxLength={200}
                autoFocus
                className="h-9"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="patient-notes" className="text-xs">
                {t('patientNotes')}
              </Label>
              <textarea
                id="patient-notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder={t('patientNotesPlaceholder')}
                rows={3}
                className="w-full rounded-md border border-slate-200 bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:placeholder:text-slate-500"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDialogMode(null)}
            >
              {t('cancel')}
            </Button>
            <Button
              size="sm"
              onClick={handleSubmit}
              disabled={!name.trim() || createMutation.isPending || updateMutation.isPending}
            >
              {dialogMode === 'create' ? t('patientAdd') : t('bodymapSave')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
