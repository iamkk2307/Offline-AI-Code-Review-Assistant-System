import { useState, useEffect } from 'react'
import { GitCompare, TrendingUp, TrendingDown, ArrowRight, Activity } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAppStore } from '@/stores/appStore'
import { PageHeader, EmptyState, LoadingShimmer } from '@/components/common'
import api from '@/services/api'
import type { AnalysisSummary } from '@/types'

export default function Comparison() {
  const { selectedProject, analysisHistory, setAnalysisHistory } = useAppStore()
  const [loading, setLoading] = useState(false)
  
  const [leftId, setLeftId] = useState<string>('')
  const [rightId, setRightId] = useState<string>('')
  
  const [comparisonResult, setComparisonResult] = useState<any>(null)

  useEffect(() => {
    if (selectedProject && analysisHistory.length === 0) {
      setLoading(true)
      api.analysis.history(selectedProject.id)
        .then(setAnalysisHistory)
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [selectedProject])

  const runCompare = async () => {
    if (!leftId || !rightId) {
      toast.error("Please select two different scans to compare.")
      return
    }
    setLoading(true)
    try {
      const left = await api.analysis.result(Number(leftId))
      const right = await api.analysis.result(Number(rightId))
      
      const diffScore = right.scores.overall - left.scores.overall
      const diffIssues = (right.file_results.reduce((a: number, b: any) => a + b.issues.length, 0)) -
                         (left.file_results.reduce((a: number, b: any) => a + b.issues.length, 0))
                         
      setComparisonResult({
        leftDate: new Date(left.created_at).toLocaleDateString(),
        rightDate: new Date(right.created_at).toLocaleDateString(),
        leftScore: left.scores.overall,
        rightScore: right.scores.overall,
        diffScore,
        diffIssues,
        leftFiles: left.file_results.length,
        rightFiles: right.file_results.length,
        leftIssues: left.file_results.reduce((a: number, b: any) => a + b.issues.length, 0),
        rightIssues: right.file_results.reduce((a: number, b: any) => a + b.issues.length, 0),
      })
      toast.success("Scans compared!")
    } catch (e: any) {
      toast.error("Comparison failed: " + e.message)
    } finally {
      setLoading(false)
    }
  }

  if (!selectedProject) {
    return (
      <div className="animate-slide-up">
        <PageHeader title="Compare Scans" subtitle="Track changes over time" />
        <EmptyState
          icon={<GitCompare size={48} />}
          title="No Project Selected"
          description="Open a project workspace to perform comparative analysis."
        />
      </div>
    )
  }

  return (
    <div className="animate-slide-up">
      <PageHeader
        title="Project Comparison"
        subtitle={`Compare code health between runs for ${selectedProject.name}`}
      />

      <div className="p-6 space-y-6">
        {/* Selector Header */}
        <div className="glass-card p-5 flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-[10px] text-slate-500 uppercase tracking-widest mb-1.5 font-bold">Base Scan (Older)</label>
            <select
              value={leftId}
              onChange={e => setLeftId(e.target.value)}
              className="input bg-surface-900 border-white/5"
            >
              <option value="">Select scan...</option>
              {analysisHistory.map(run => (
                <option key={run.id} value={run.id}>
                  Scan #{run.id} — {new Date(run.created_at).toLocaleDateString()} (Score: {Math.round(run.overall_score)})
                </option>
              ))}
            </select>
          </div>

          <ArrowRight size={16} className="text-slate-500 mt-4 hidden md:block" />

          <div className="flex-1 min-w-[200px]">
            <label className="block text-[10px] text-slate-500 uppercase tracking-widest mb-1.5 font-bold">Target Scan (Newer)</label>
            <select
              value={rightId}
              onChange={e => setRightId(e.target.value)}
              className="input bg-surface-900 border-white/5"
            >
              <option value="">Select scan...</option>
              {analysisHistory.map(run => (
                <option key={run.id} value={run.id}>
                  Scan #{run.id} — {new Date(run.created_at).toLocaleDateString()} (Score: {Math.round(run.overall_score)})
                </option>
              ))}
            </select>
          </div>

          <button onClick={runCompare} className="btn-primary mt-4 whitespace-nowrap">
            <GitCompare size={14} /> Compare Scans
          </button>
        </div>

        {loading && <LoadingShimmer rows={2} height="h-28" />}

        {/* Diff Results Grid */}
        {!loading && comparisonResult && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-scale-in">
            {/* Score Comparison */}
            <div className="glass-card p-5 text-center">
              <h4 className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-4">Overall Score Delta</h4>
              <div className="flex justify-center items-baseline gap-2 mb-2">
                <span className="text-3xl font-bold text-slate-300">{Math.round(comparisonResult.leftScore)}</span>
                <ArrowRight size={12} className="text-slate-500" />
                <span className="text-4xl font-extrabold text-slate-100">{Math.round(comparisonResult.rightScore)}</span>
              </div>
              <div className={`flex items-center justify-center gap-1 text-xs font-semibold ${
                comparisonResult.diffScore >= 0 ? 'text-emerald-400' : 'text-red-400'
              }`}>
                {comparisonResult.diffScore >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {comparisonResult.diffScore >= 0 ? '+' : ''}{comparisonResult.diffScore.toFixed(1)} delta
              </div>
            </div>

            {/* Total Issues Comparison */}
            <div className="glass-card p-5 text-center">
              <h4 className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-4">Total Issues Delta</h4>
              <div className="flex justify-center items-baseline gap-2 mb-2">
                <span className="text-3xl font-bold text-slate-300">{comparisonResult.leftIssues}</span>
                <ArrowRight size={12} className="text-slate-500" />
                <span className="text-4xl font-extrabold text-slate-100">{comparisonResult.rightIssues}</span>
              </div>
              <div className={`flex items-center justify-center gap-1 text-xs font-semibold ${
                comparisonResult.diffIssues <= 0 ? 'text-emerald-400' : 'text-red-400'
              }`}>
                {comparisonResult.diffIssues <= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {comparisonResult.diffIssues > 0 ? '+' : ''}{comparisonResult.diffIssues} issues delta
              </div>
            </div>

            {/* Files Analyzed Delta */}
            <div className="glass-card p-5 text-center">
              <h4 className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-4">Files Scanned</h4>
              <div className="flex justify-center items-baseline gap-2 mb-2">
                <span className="text-3xl font-bold text-slate-300">{comparisonResult.leftFiles}</span>
                <ArrowRight size={12} className="text-slate-500" />
                <span className="text-4xl font-extrabold text-slate-100">{comparisonResult.rightFiles}</span>
              </div>
              <div className="text-xs text-slate-400 font-semibold">
                Change: {comparisonResult.rightFiles - comparisonResult.leftFiles > 0 ? '+' : ''}
                {comparisonResult.rightFiles - comparisonResult.leftFiles} files
              </div>
            </div>
          </div>
        )}

        {!loading && !comparisonResult && (
          <EmptyState
            icon={<GitCompare size={48} />}
            title="Ready to Compare"
            description="Select two scans from the dropdown lists above to see comparative health trends."
          />
        )}
      </div>
    </div>
  )
}
