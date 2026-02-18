import { NavLink } from 'react-router-dom'
import { ScanLine, History, Video, Info } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/', icon: ScanLine, labelKey: 'navScan' },
  { to: '/history', icon: History, labelKey: 'navHistory' },
  { to: '/live', icon: Video, labelKey: 'navLive' },
  { to: '/info', icon: Info, labelKey: 'navInfo' },
]

export function BottomNav() {
  const t = useAppStore((s) => s.t)

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95 md:hidden">
      <div className="flex h-16">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                cn(
                  'flex flex-1 flex-col items-center justify-center gap-1 text-xs transition-colors',
                  isActive ? 'text-blue-500 dark:text-blue-400' : 'text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300',
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={cn('h-5 w-5', isActive && 'text-blue-500 dark:text-blue-400')} />
                  <span>{t(item.labelKey)}</span>
                </>
              )}
            </NavLink>
          )
        })}
      </div>
    </nav>
  )
}
