import { useState, useEffect, useRef } from 'react'
import { Search, Terminal, FileCode, AlertCircle, Shield, Settings, Info } from 'lucide-react'
import { useAppStore } from '@/stores/appStore'

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const { setActivePage, projects, setSelectedProject, currentAnalysis } = useAppStore()
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  // Handle click outside or Esc key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!isOpen) return null

  const items = [
    { type: 'page',    label: 'Go to Dashboard', icon: Terminal,    action: () => { setActivePage('dashboard'); onClose() } },
    { type: 'page',    label: 'Go to Projects',  icon: FileCode,    action: () => { setActivePage('projects'); onClose() } },
    { type: 'page',    label: 'Go to Analysis',  icon: Shield,      action: () => { setActivePage('analysis'); onClose() } },
    { type: 'page',    label: 'Go to ML Insights',icon: Shield,      action: () => { setActivePage('ml-insights'); onClose() } },
    { type: 'page',    label: 'Go to Settings',  icon: Settings,    action: () => { setActivePage('settings'); onClose() } },
    { type: 'page',    label: 'Go to About',     icon: Info,        action: () => { setActivePage('about'); onClose() } },
    
    // Add projects
    ...projects.map(p => ({
      type: 'project',
      label: `Switch Project: ${p.name}`,
      icon: FileCode,
      action: () => { setSelectedProject(p); setActivePage('dashboard'); onClose() }
    })),
    
    // Add critical issues if analysis available
    ...(currentAnalysis?.top_critical_issues?.map(i => ({
      type: 'issue',
      label: `View Critical: ${i.title} in ${i.filename}`,
      icon: AlertCircle,
      action: () => { setActivePage('analysis'); onClose() }
    })) || [])
  ]

  const filtered = items.filter(item =>
    item.label.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-start justify-center pt-[15vh] p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg bg-surface-900 border border-white/10 rounded-xl overflow-hidden shadow-2xl animate-scale-in"
        onClick={e => e.stopPropagation()}
      >
        {/* Search header */}
        <div className="flex items-center gap-3 px-4 border-b border-white/5 bg-surface-950/40">
          <Search size={16} className="text-slate-500" />
          <input
            ref={inputRef}
            className="w-full bg-transparent py-3.5 text-slate-200 placeholder-slate-500 text-sm focus:outline-none"
            placeholder="Type a command or search items..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <kbd className="text-[10px] bg-surface-800 text-slate-400 px-1.5 py-0.5 rounded-md border border-white/5 font-mono">ESC</kbd>
        </div>

        {/* Results */}
        <div className="max-h-[320px] overflow-y-auto p-2 space-y-0.5">
          {filtered.map((item, idx) => {
            const Icon = item.icon
            return (
              <button
                key={idx}
                onClick={item.action}
                className="w-full text-left flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-primary-600/10 hover:text-primary-300 transition-colors text-xs text-slate-400 font-medium"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <Icon size={14} className="text-slate-500 flex-shrink-0" />
                  <span className="truncate text-slate-300">{item.label}</span>
                </div>
                <span className="text-[10px] text-slate-500 uppercase tracking-widest font-mono">
                  {item.type}
                </span>
              </button>
            )
          })}
          {filtered.length === 0 && (
            <div className="text-center py-8 text-xs text-slate-500 font-medium">
              No commands or items match "{query}"
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
