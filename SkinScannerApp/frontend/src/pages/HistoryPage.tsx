import { HistoryTable } from '@/components/history/HistoryTable'
import { useAppStore } from '@/store/useAppStore'

export default function HistoryPage() {
  const { t } = useAppStore()
  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold">{t('historyTitle')}</h1>
      <HistoryTable />
    </div>
  )
}
