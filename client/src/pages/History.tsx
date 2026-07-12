import { useEffect, useState } from 'react'
import { Calendar, Shield, Cpu, Clock, History as HistIcon, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAppStore } from '@/stores/appStore'
import { PageHeader, EmptyState, LoadingShimmer } from '@/components/common'
import api from '@/services/api'
import type { AnalysisSummary } from '@/types'

export default function History() {
  const { selectedProject, analysisHistory, setAnalysisHistory, setCurrentAnalysis } = useAppStore()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (selectedProject) {
      setLoading(true)
      api.analysis.history(selectedProject.id)
        .then(setAnalysisHistory)
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [selectedProject])

  const selectHistory = async (id: number) => {
    try {
      const result = await api.analysis.result(id)
      setCurrentAnalysis(result)
      toast.success("Loaded history snapshot from " + new Date(result.created_at).toLocaleDateString())
    } catch (e: any) {
      toast.error("Failed to load: " + e.message)
    }
  }

  if (!selectedProject) {
    return (
      <div className="animate-slide-up">
        <PageHeader title="Analysis History" subtitle="Scans log timeline" />
        <EmptyState
          icon={<HistIcon size={48} />}
          title="No Project Selected"
          description="Open a project workspace to inspect historic runs."
        />
      </div>
    )
  }

  return (
    <div className="animate-slide-up">
      <PageHeader
        title="History"
        subtitle={`Historical scans timeline for ${selectedProject.name}`}
      />

      <div className="p-6 space-y-6">
        {loading && <LoadingShimmer rows={3} height="h-20" />}

        {!loading && analysisHistory.length === 0 && (
          <EmptyState
            icon={<HistIcon size={48} />}
            title="No Scans Logged"
            description="Run your first analysis project scan to populate the timeline logs."
          />
        )}

        {!loading && analysisHistory.length > 0 && (
          <div className="relative border-l border-white/5 pl-6 ml-3 space-y-6">
            {analysisHistory.map((run) => (
              <div
                key={run.id}
                onClick={() => selectHistory(run.id)}
                className="relative glass-card p-5 hover:border-primary-500/20 transition-all cursor-pointer animate-scale-in"
              >
                {/* Timeline node */}
                <div className="absolute w-3 h-3 bg-primary-500 rounded-full -left-[31px] top-6 border-2 border-surface-950" />
                
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div>
                    <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                      <Calendar size={12} /> {new Date(run.created_at).toLocaleString()}
                      <span>·</span>
                      <Clock size={12} /> {Math.round(run.duration_seconds)}s scan
                    </div>
                    <h3 className="font-semibold text-slate-200 text-sm">
                      Scan ID #{run.id} — {run.total_files} files analyzed
                    </h3>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className={`text-xl font-bold ${
                        run.overall_score >= 85 ? 'text-emerald-400' :
                        run.overall_score >= 70 ? 'text-lime-400' :
                        run.overall_score >= 55 ? 'text-amber-400' : 'text-red-400'
                      }`}>
                        {Math.round(run.overall_score)}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-widest">Health Score</div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-xl font-bold text-red-400">
                        {run.critical_issues}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-widest">Critical</div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-xl font-bold text-slate-300">
                        {run.total_issues}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-widest">Total Issues</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
