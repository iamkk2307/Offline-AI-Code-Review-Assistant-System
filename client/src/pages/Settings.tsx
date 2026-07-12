import { useState, useEffect } from 'react'
import { Save, RefreshCw, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAppStore } from '@/stores/appStore'
import { PageHeader } from '@/components/common'
import api from '@/services/api'
import type { AppSettings } from '@/types'

export default function Settings() {
  const { settings, setSettings } = useAppStore()
  const [local, setLocal] = useState<AppSettings>(settings)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.settings.get().then(s => { setLocal(s); setSettings(s) }).catch(() => {})
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      const saved = await api.settings.update(local)
      setSettings(saved)
      toast.success('Settings saved!')
    } catch (e: any) {
      toast.error(e.message)
    } finally {
      setSaving(false)
    }
  }

  const handleReset = async () => {
    if (!confirm('Reset all settings to defaults?')) return
    try {
      const defaults = await api.settings.reset()
      setLocal(defaults); setSettings(defaults)
      toast.success('Settings reset to defaults')
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  const field = (key: keyof AppSettings, label: string, type: string = 'text', options?: string[]) => (
    <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-0">
      <div>
        <div className="text-sm font-medium text-slate-300">{label}</div>
      </div>
      <div className="ml-4 w-48">
        {type === 'select' ? (
          <select
            className="input text-sm py-1.5"
            value={String(local[key])}
            onChange={e => setLocal(p => ({ ...p, [key]: e.target.value }))}
          >
            {options?.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        ) : type === 'checkbox' ? (
          <label className="flex items-center gap-2 cursor-pointer">
            <div
              onClick={() => setLocal(p => ({ ...p, [key]: !p[key] }))}
              className={`w-10 h-5 rounded-full transition-colors cursor-pointer ${local[key] ? 'bg-primary-600' : 'bg-surface-700'}`}
            >
              <div className={`w-4 h-4 bg-white rounded-full m-0.5 transition-transform ${local[key] ? 'translate-x-5' : 'translate-x-0'}`} />
            </div>
          </label>
        ) : type === 'number' ? (
          <input
            type="number"
            className="input text-sm py-1.5"
            value={Number(local[key])}
            min={1} max={16}
            onChange={e => setLocal(p => ({ ...p, [key]: parseInt(e.target.value) }))}
          />
        ) : (
          <input
            type="text"
            className="input text-sm py-1.5"
            value={String(local[key])}
            onChange={e => setLocal(p => ({ ...p, [key]: e.target.value }))}
          />
        )}
      </div>
    </div>
  )

  return (
    <div className="animate-slide-up">
      <PageHeader
        title="Settings"
        subtitle="Configure application preferences"
        actions={
          <div className="flex gap-2">
            <button onClick={handleReset} className="btn-secondary"><RotateCcw size={14} /> Reset</button>
            <button onClick={handleSave} disabled={saving} className="btn-primary">
              {saving ? <RefreshCw size={14} className="animate-spin" /> : <Save size={14} />} Save
            </button>
          </div>
        }
      />
      <div className="p-6 space-y-4">
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Appearance</h2>
          {field('theme', 'Theme', 'select', ['dark', 'light', 'auto'])}
        </div>
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Analysis</h2>
          {field('max_workers', 'Max Worker Threads', 'number')}
          {field('auto_save', 'Auto-save Results', 'checkbox')}
          {field('analysis_on_open', 'Analyze on Project Open', 'checkbox')}
          {field('show_info_issues', 'Show Info Issues', 'checkbox')}
        </div>
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Reports</h2>
          {field('default_report_format', 'Default Format', 'select', ['html', 'pdf', 'markdown', 'json', 'csv'])}
          {field('report_output_dir', 'Report Output Directory', 'text')}
        </div>
      </div>
    </div>
  )
}
