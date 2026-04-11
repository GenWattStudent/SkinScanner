import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'
import { BottomNav } from './BottomNav'
import { SettingsSheet } from './SettingsSheet'

export function Layout() {
  const [settingsOpen, setSettingsOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors">
      <Navbar onSettingsOpen={() => setSettingsOpen(true)} />
      <SettingsSheet open={settingsOpen} onClose={() => setSettingsOpen(false)} />

      {/* Main content with bottom padding for mobile nav */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 pb-24 md:pb-8">
        <Outlet />
      </main>

      <BottomNav />
    </div>
  )
}
