import { useState } from 'react'
import { FileText, Download, RefreshCw, File, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAppStore } from '@/stores/appStore'
import { PageHeader, EmptyState } from '@/components/common'
import api from '@/services/api'

const FORMATS = [
  { id: 'html',     label: 'HTML Dashboard Report', desc: 'Standalone offline HTML package containing local static assets and charts.',  icon: '🌐' },
  { id: 'pdf',      label: 'PDF Document Report',   desc: 'Executive summary document suitable for printing or sharing.',              icon: '📄' },
  { id: 'markdown', label: 'Markdown Readme Log',   desc: 'GitHub-compatible markdown document outlining code health tables.',         icon: '📝' },
  { id: 'json',     label: 'JSON Data Stream',      desc: 'Raw parsed AST statistics and model metrics for external tool ingestion.',  icon: '🔧' },
  { id: 'csv',      label: 'CSV Violation Spreadsheet', desc: 'Flat table listing of all issues found, formatted for spreadsheet tools.', icon: '📊' },
]

export default function Reports() {
  const { currentAnalysis } = useAppStore()
  const [generating, setGenerating] = useState<string | null>(null)
  const [generated, setGenerated] = useState<Record<string, string>>({})

  const handleGenerate = async (format: string) => {
    if (!currentAnalysis) { toast.error('No analysis available. Run an analysis first.'); return }
    setGenerating(format)
    try {
      const result = await api.reports.generate(currentAnalysis.id, format)
      setGenerated(prev => ({ ...prev, [format]: result.file_path }))
      toast.success(`${format.toUpperCase()} report generated!`)
    } catch (e: any) {
      toast.error('Failed to generate report: ' + e.message)
    } finally {
      setGenerating(null)
    }
  }

  if (!currentAnalysis) {
    return (
      <div className="animate-slide-up">
        <PageHeader title="Reports" subtitle="Generate analysis reports in multiple formats" />
        <div className="p-6">
          <EmptyState
            icon={<FileText size={48} />}
            title="No Analysis Available"
            description="Run an analysis first, then generate reports in PDF, HTML, Markdown, JSON, or CSV format."
          />
        </div>
      </div>
    )
  }

  return (
    <div className="animate-slide-up h-full overflow-y-auto">
      <PageHeader title="Reports" subtitle="Generate and export analysis reports" />
      <div className="p-6 space-y-4">
        {/* Info card */}
        <div className="glass-card p-4 flex items-center justify-between gap-3 text-xs border border-emerald-500/20 bg-emerald-500/5">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-slate-600 dark:text-slate-300 font-semibold">
              Analysis Results Cache Available: {currentAnalysis.total_files} files, {currentAnalysis.issue_summary.total} issues detected.
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FORMATS.map(({ id, label, desc, icon }) => (
            <div key={id} className="glass-card p-5 flex flex-col justify-between hover:border-slate-300 dark:hover:border-white/10 transition-all duration-200 min-h-[200px]">
              <div>
                <div className="text-3xl mb-3">{icon}</div>
                <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200 mb-1">{label}</h3>
                <p className="text-[11px] text-slate-500 leading-relaxed mb-4">{desc}</p>
              </div>

              <div className="space-y-2.5">
                <div className="flex gap-2">
                  <button
                    onClick={() => handleGenerate(id)}
                    disabled={!!generating}
                    className="btn-primary flex-1 justify-center py-2 text-xs"
                  >
                    {generating === id ? (
                      <><RefreshCw size={12} className="animate-spin" /> Generating...</>
                    ) : (
                      <><File size={12} /> Generate</>
                    )}
                  </button>
                  {generated[id] && (
                    <button
                      className="btn-secondary px-2.5 py-2 text-xs"
                      title="Open reports directory folder"
                      onClick={() => toast.success("Saved: " + generated[id])}
                    >
                      <Download size={12} />
                    </button>
                  )}
                </div>
                {generated[id] && (
                  <div className="text-[9px] text-emerald-500 font-mono truncate flex items-center gap-1">
                    <span>✓</span>
                    <span className="truncate">{generated[id].split(/[/\\]/).pop()}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
