import { NavLink } from 'react-router-dom'
import { ScanLine, History, Video, Settings, Info } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'

interface NavItem {
  to: string
  icon: React.ReactNode
  labelKey: string
}

const navItems: NavItem[] = [
  { to: '/', icon: <ScanLine className="h-5 w-5" />, labelKey: 'navScan' },
  { to: '/history', icon: <History className="h-5 w-5" />, labelKey: 'navHistory' },
  { to: '/live', icon: <Video className="h-5 w-5" />, labelKey: 'navLive' },
  { to: '/info', icon: <Info className="h-5 w-5" />, labelKey: 'navInfo' },
]

interface NavbarProps {
  onSettingsOpen: () => void
}

export function Navbar({ onSettingsOpen }: NavbarProps) {
  const t = useAppStore((s) => s.t)

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/75 dark:border-slate-800 dark:bg-slate-950/90 dark:supports-[backdrop-filter]:bg-slate-950/75">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-2.5">
          <span className="text-2xl">🩺</span>
          <span className="text-lg font-bold tracking-tight">
            {t('appName')}
          </span>
        </NavLink>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100'
                    : 'text-slate-500 hover:bg-slate-100/60 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-slate-200',
                )
              }
            >
              {item.icon}
              {t(item.labelKey)}
            </NavLink>
          ))}
        </nav>

        {/* Settings button */}
        <button
          onClick={onSettingsOpen}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Settings"
        >
          <Settings className="h-5 w-5" />
        </button>
      </div>
    </header>
  )
}
