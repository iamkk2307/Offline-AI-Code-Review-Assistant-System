import { useEffect, useState } from 'react'
import { Toaster } from 'react-hot-toast'
import { Search, ShieldAlert, Cpu, Heart, CheckCircle, Database } from 'lucide-react'
import Sidebar from '@/components/layout/Sidebar'
import Dashboard from '@/pages/Dashboard'
import Projects from '@/pages/Projects'
import Analysis from '@/pages/Analysis'
import Settings from '@/pages/Settings'
import CommandPalette from '@/components/layout/CommandPalette'
import { useAppStore } from '@/stores/appStore'
import api from '@/services/api'

export default function App() {
  const { activePage, setServerOnline, serverOnline, selectedProject, settings, setServerCwd } = useAppStore()
  const [isPaletteOpen, setIsPaletteOpen] = useState(false)

  // Apply theme classes dynamically
  useEffect(() => {
    const root = window.document.documentElement
    const theme = settings.theme

    const applyTheme = (t: 'dark' | 'light') => {
      if (t === 'dark') {
        root.classList.add('dark')
        root.classList.remove('light')
      } else {
        root.classList.add('light')
        root.classList.remove('dark')
      }
    }

    if (theme === 'auto') {
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      applyTheme(systemPrefersDark ? 'dark' : 'light')

      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const listener = (e: MediaQueryListEvent) => {
        applyTheme(e.matches ? 'dark' : 'light')
      }
      mediaQuery.addEventListener('change', listener)
      return () => mediaQuery.removeEventListener('change', listener)
    } else {
      applyTheme(theme)
    }
  }, [settings.theme])

  // Poll server health on mount
  useEffect(() => {
    const check = async () => {
      try {
        const res = await api.health()
        setServerOnline(true)
        if (res.cwd) setServerCwd(res.cwd)
      } catch {
        setServerOnline(false)
      }
    }
    check()
    const interval = setInterval(check, 10000)
    return () => clearInterval(interval)
  }, [setServerOnline, setServerCwd])

  // Keyboard shortcut listener (Ctrl+P / Cmd+P)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault()
        setIsPaletteOpen(prev => !prev)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':    return <Dashboard />
      case 'projects':     return <Projects />
      case 'analysis':     return <Analysis />
      case 'settings':     return <Settings />
      default:             return <Dashboard />
    }
  }

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-50 dark:bg-surface-950 text-slate-800 dark:text-slate-100 transition-colors duration-200">
      {/* ── Top Toolbar ────────────────────────────────────────── */}
      <header className="h-11 flex-shrink-0 bg-slate-100 dark:bg-surface-900 border-b border-slate-200 dark:border-white/5 flex items-center justify-between px-4 text-xs select-none">
        <div className="flex items-center gap-4">
          <div className="font-semibold text-slate-900 dark:text-slate-200 flex items-center gap-1.5">
            <ShieldAlert size={14} className="text-primary-500" />
            Code Review Assistant
          </div>
          {selectedProject && (
            <span className="bg-slate-200 dark:bg-surface-800 text-[10px] text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full border border-slate-300/30 dark:border-white/5 font-semibold">
              Project: {selectedProject.name}
            </span>
          )}
        </div>

        {/* Global Search command trigger */}
        <button
          onClick={() => setIsPaletteOpen(true)}
          className="flex items-center gap-2 px-3 py-1 bg-white dark:bg-surface-950 border border-slate-200 dark:border-white/10 rounded-lg text-slate-400 hover:text-slate-200 hover:border-slate-300 w-64 text-left transition-all"
        >
          <Search size={12} />
          <span className="flex-1 text-[10px] truncate">Search commands or files...</span>
          <kbd className="text-[9px] bg-slate-100 dark:bg-surface-800 px-1 py-0.5 rounded border border-slate-200 dark:border-white/5 font-mono">Ctrl+P</kbd>
        </button>

        <div className="flex items-center gap-3">
          <span className="text-[10px] text-slate-500 font-mono">v1.0.0</span>
        </div>
      </header>

      {/* ── Main Container ──────────────────────────────────────── */}
      <div className="flex flex-1 min-h-0">
        <Sidebar />
        <main className="main-content flex-1 bg-slate-50 dark:bg-surface-950">
          <div className="animate-fade-in h-full">
            {renderPage()}
          </div>
        </main>
      </div>

      {/* ── Bottom Status Bar ───────────────────────────────────── */}
      <footer className="h-6 flex-shrink-0 bg-slate-100 dark:bg-surface-900 border-t border-slate-200 dark:border-white/5 flex items-center justify-between px-4 text-[10px] text-slate-500 dark:text-slate-400 select-none">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 font-medium">
            <span className={`w-1.5 h-1.5 rounded-full ${serverOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
            {serverOnline ? 'Local Engine Connected' : 'Engine Disconnected'}
          </div>
          <span>·</span>
          <div>Max scanning threads: {settings.max_workers || 4}</div>
        </div>

        <div className="flex items-center gap-4 font-mono">
          <div className="flex items-center gap-1"><Database size={11} /> SQLite Connected</div>
          <div className="flex items-center gap-1"><Cpu size={11} /> RAM &lt; 500 MB Budget</div>
          <div className="flex items-center gap-1 text-primary-500"><Heart size={11} /> Safe & Offline</div>
        </div>
      </footer>

      {/* Spotlight Command Palette Modal */}
      <CommandPalette isOpen={isPaletteOpen} onClose={() => setIsPaletteOpen(false)} />

      {/* Toaster Notification Provider */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: settings.theme === 'light' ? '#ffffff' : '#1e293b',
            color: settings.theme === 'light' ? '#1e293b' : '#e2e8f0',
            border: '1px solid rgba(0,0,0,0.05)',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 500,
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#1e293b' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#1e293b' } },
        }}
      />
    </div>
  )
}
