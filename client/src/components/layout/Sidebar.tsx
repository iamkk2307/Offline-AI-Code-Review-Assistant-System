import {
  LayoutDashboard, FolderOpen, Search, FileText,
  Settings, Info, ChevronLeft, ChevronRight, Cpu,
  Brain, History, GitCompare
} from 'lucide-react'
import clsx from 'clsx'
import { useAppStore } from '@/stores/appStore'

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'projects',  label: 'Projects',  icon: FolderOpen },
  { id: 'analysis',  label: 'Analysis',  icon: Search },
  { id: 'settings',  label: 'Settings',  icon: Settings },
] as const

export default function Sidebar() {
  const { activePage, setActivePage, sidebarCollapsed, setSidebarCollapsed } = useAppStore()

  return (
    <aside
      className={clsx(
        'flex flex-col bg-slate-100 dark:bg-surface-900 border-r border-slate-200 dark:border-white/5 transition-all duration-300 flex-shrink-0 select-none',
        sidebarCollapsed ? 'w-12' : 'w-52'
      )}
    >
      {/* Header Logo */}
      <div className={clsx(
        'flex items-center gap-2.5 p-3.5 border-b border-slate-200 dark:border-white/5',
        sidebarCollapsed ? 'justify-center' : 'px-4'
      )}>
        <div className="w-6 h-6 rounded-lg bg-primary-600 flex items-center justify-center flex-shrink-0">
          <Cpu size={12} className="text-white" />
        </div>
        {!sidebarCollapsed && (
          <div className="animate-fade-in font-bold text-xs text-slate-800 dark:text-slate-200">
            ML Scan
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-3 space-y-0.5 overflow-y-auto">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
          const isActive = activePage === id
          return (
            <button
              key={id}
              onClick={() => setActivePage(id)}
              className={clsx(
                'nav-item w-[calc(100%-8px)] mx-1 py-2 px-2.5 rounded-lg flex items-center gap-2.5 text-left text-xs font-semibold',
                isActive ? 'bg-primary-50 dark:bg-primary-600/10 text-primary-600 dark:text-primary-300 font-bold border-l-2 border-primary-500 rounded-l-none' : 'text-slate-500 dark:text-slate-400',
                sidebarCollapsed ? 'justify-center border-l-0 rounded-lg' : ''
              )}
              title={sidebarCollapsed ? label : undefined}
            >
              <Icon size={14} className="flex-shrink-0" />
              {!sidebarCollapsed && (
                <span className="animate-fade-in truncate">{label}</span>
              )}
            </button>
          )
        })}
      </nav>

      {/* Collapse Action Button */}
      <button
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="flex items-center justify-center h-8 border-t border-slate-200 dark:border-white/5 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 hover:bg-slate-200/50 dark:hover:bg-surface-800 transition-colors"
      >
        {sidebarCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>
    </aside>
  )
}
