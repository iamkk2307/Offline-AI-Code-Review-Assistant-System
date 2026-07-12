import { useEffect, useState } from 'react'
import {
  Activity, Shield, Zap, Cpu, TrendingUp, AlertTriangle,
  FileCode, FolderOpen, Clock, ChevronRight, BarChart2, ShieldAlert
} from 'lucide-react'
import clsx from 'clsx'
import { useAppStore } from '@/stores/appStore'
import { ScoreCard, PageHeader, LoadingShimmer, EmptyState } from '@/components/common'
import { ScoresRadar, LanguageDonut, IssueBarChart } from '@/components/charts/Charts'
import api from '@/services/api'

export default function Dashboard() {
  const { selectedProject, currentAnalysis, setCurrentAnalysis, setActivePage } = useAppStore()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (selectedProject && !currentAnalysis) {
      setLoading(true)
      api.analysis.latest(selectedProject.id)
        .then(setCurrentAnalysis)
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [selectedProject])

  const analysis = currentAnalysis
  const scores   = analysis?.scores
  const issues   = analysis?.issue_summary

  // Calculate circular gauge parameters
  const scoreVal = scores?.overall ? Math.round(scores.overall) : 0
  const strokeDashoffset = 251.2 - (251.2 * scoreVal) / 100

  const getRatingLabel = (score: number) => {
    if (score >= 85) return { text: 'Excellent', color: 'text-emerald-500' }
    if (score >= 70) return { text: 'Good', color: 'text-lime-500' }
    if (score >= 55) return { text: 'Fair', color: 'text-amber-500' }
    return { text: 'Critical', color: 'text-red-500' }
  }
  const rating = getRatingLabel(scoreVal)

  return (
    <div className="animate-slide-up h-full overflow-y-auto">
      <PageHeader
        title="Dashboard"
        subtitle={selectedProject ? `Project: ${selectedProject.name}` : 'Select a project to begin'}
        actions={
          selectedProject && (
            <button onClick={() => setActivePage('analysis')} className="btn-primary">
              <Zap size={14} /> Scan Project
            </button>
          )
        }
      />

      <div className="p-6 space-y-6">
        {/* No project selected */}
        {!selectedProject && (
          <EmptyState
            icon={<FolderOpen size={48} />}
            title="No Project Selected"
            description="Open a project folder to start analyzing your code quality, security, and maintainability."
            action={
              <button onClick={() => setActivePage('projects')} className="btn-primary">
                <FolderOpen size={14} /> Open Project
              </button>
            }
          />
        )}

        {/* Loading */}
        {selectedProject && loading && (
          <LoadingShimmer rows={4} height="h-24" />
        )}

        {/* No analysis yet */}
        {selectedProject && !loading && !analysis && (
          <EmptyState
            icon={<Activity size={48} />}
            title="No Analysis Yet"
            description="Run an analysis to see detailed code quality metrics, security issues, and recommendations."
            action={
              <button onClick={() => setActivePage('analysis')} className="btn-primary">
                <Zap size={14} /> Start Analysis
              </button>
            }
          />
        )}

        {/* Analysis Results */}
        {analysis && scores && (
          <>
            {/* Top Row: Circular Health Gauge + Stats Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Circular health gauge card */}
              <div className="glass-card p-6 flex flex-col items-center justify-center text-center col-span-1 min-h-[220px]">
                <h4 className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-4">Overall Code Health</h4>
                
                <div className="relative score-gauge w-28 h-28 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="40" stroke="rgba(255,255,255,0.05)" strokeWidth="8" fill="transparent" />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      className="transition-all duration-1000 ease-out"
                      stroke={scoreVal >= 85 ? '#10b981' : scoreVal >= 70 ? '#84cc16' : scoreVal >= 55 ? '#f59e0b' : '#ef4444'}
                      strokeWidth="8"
                      strokeDasharray="251.2"
                      strokeDashoffset={strokeDashoffset}
                      strokeLinecap="round"
                      fill="transparent"
                    />
                  </svg>
                  <div className="absolute text-center">
                    <span className="text-3xl font-black tabular-nums">{scoreVal}</span>
                    <span className="text-[10px] block text-slate-500 mt-0.5">/ 100</span>
                  </div>
                </div>

                <div className={clsx('text-xs font-bold mt-4 uppercase tracking-widest', rating.color)}>
                  Rating: {rating.text}
                </div>
              </div>

              {/* Metrics scoring panels */}
              <div className="lg:col-span-2 grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricPanel icon={<Shield size={16} />} title="Security Score" value={scores.security} />
                <MetricPanel icon={<Cpu size={16} />} title="Code Quality" value={scores.quality} />
                <MetricPanel icon={<TrendingUp size={16} />} title="Maintainability" value={scores.maintainability} />
                <MetricPanel icon={<Zap size={16} />} title="Performance" value={scores.performance} />
              </div>
            </div>

            {/* Score Metrics row */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              <ScoreCard label="Readability"     score={scores.readability}     showBar />
              <ScoreCard label="Quality"         score={scores.quality}         showBar />
              <ScoreCard label="Security"        score={scores.security}        showBar />
              <ScoreCard label="Maintainability" score={scores.maintainability} showBar />
              <ScoreCard label="Performance"     score={scores.performance}     showBar />
              <ScoreCard label="Overall Health"  score={scores.overall}         showBar />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Radar */}
              <div className="glass-card p-5 lg:col-span-1">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-1.5">
                  <BarChart2 size={12} /> Score Breakdown
                </h3>
                <div className="h-60">
                  <ScoresRadar scores={scores} />
                </div>
              </div>

              {/* Language Donut */}
              <div className="glass-card p-5 lg:col-span-1">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-1.5">
                  <FileCode size={12} /> Language Mix
                </h3>
                <div className="h-60">
                  {analysis.language_distribution && Object.keys(analysis.language_distribution).length > 0 ? (
                    <LanguageDonut distribution={analysis.language_distribution} />
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-500 text-sm">No data</div>
                  )}
                </div>
              </div>

              {/* Issue Bar */}
              <div className="glass-card p-5 lg:col-span-1">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-1.5">
                  <ShieldAlert size={12} /> Issues Mix
                </h3>
                <div className="h-60">
                  {issues && <IssueBarChart summary={issues} />}
                </div>
              </div>
            </div>

            {/* Issue Summary + Problematic files list */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Issue summary list */}
              {issues && (
                <div className="glass-card p-5">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Rule Violation Counts</h3>
                  <div className="space-y-3">
                    {[
                      { label: 'Critical', key: 'critical', color: 'bg-red-500' },
                      { label: 'High',     key: 'high',     color: 'bg-orange-500' },
                      { label: 'Medium',   key: 'medium',   color: 'bg-yellow-500' },
                      { label: 'Low',      key: 'low',      color: 'bg-green-500' },
                      { label: 'Info',     key: 'info',     color: 'bg-blue-500' },
                    ].map(({ label, key, color }) => (
                      <div key={key} className="flex items-center gap-3">
                        <div className={clsx('w-2 h-2 rounded-full flex-shrink-0', color)} />
                        <span className="text-xs text-slate-400 w-16">{label}</span>
                        <div className="flex-1 progress-bar">
                          <div
                            className={clsx('progress-bar-fill', color)}
                            style={{ width: `${Math.min(100, ((issues[key as keyof typeof issues] as number) / Math.max(issues.total, 1)) * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold text-slate-200 w-8 text-right">
                          {issues[key as keyof typeof issues]}
                        </span>
                      </div>
                    ))}
                    <div className="pt-2 border-t border-white/5 flex justify-between text-xs font-bold">
                      <span className="text-slate-400">Total Scanned Issues</span>
                      <span className="text-slate-200">{issues.total}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Problematic files */}
              <div className="glass-card p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Problematic Files</h3>
                  <button onClick={() => setActivePage('analysis')} className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-0.5">
                    Scan Detail <ChevronRight size={12} />
                  </button>
                </div>
                <div className="space-y-2">
                  {analysis.most_problematic_files?.slice(0, 5).map((file, i) => (
                    <div key={i} className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-slate-200/50 dark:hover:bg-surface-800 transition-colors">
                      <FileCode size={14} className="text-slate-500 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-semibold text-slate-700 dark:text-slate-300 truncate font-mono">{file.filename}</div>
                        <div className="text-[10px] text-slate-500">{file.language}</div>
                      </div>
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        {file.issue_summary.critical > 0 && (
                          <span className="text-[10px] font-bold text-red-500 bg-red-500/10 px-1.5 py-0.5 rounded border border-red-500/20">{file.issue_summary.critical}C</span>
                        )}
                        {file.issue_summary.high > 0 && (
                          <span className="text-[10px] font-bold text-orange-500 bg-orange-500/10 px-1.5 py-0.5 rounded border border-orange-500/20">{file.issue_summary.high}H</span>
                        )}
                      </div>
                    </div>
                  ))}
                  {(!analysis.most_problematic_files || analysis.most_problematic_files.length === 0) && (
                    <div className="text-center py-4 text-slate-500 text-sm">No issues found! 🎉</div>
                  )}
                </div>
              </div>
            </div>

            {/* Analysis Stats Footer row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="glass-card p-4 flex items-center gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-primary-500/15 border border-primary-500/20 flex items-center justify-center text-primary-400">
                  <FileCode size={16} />
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-800 dark:text-slate-200">{analysis.total_files}</div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Total Scanned Files</div>
                </div>
              </div>

              <div className="glass-card p-4 flex items-center gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-amber-500/15 border border-amber-500/20 flex items-center justify-center text-amber-400">
                  <AlertTriangle size={16} />
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-800 dark:text-slate-200">{issues?.total ?? 0}</div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Violations Detected</div>
                </div>
              </div>

              <div className="glass-card p-4 flex items-center gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-blue-500/15 border border-blue-500/20 flex items-center justify-center text-blue-400">
                  <Clock size={16} />
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-800 dark:text-slate-200">{Math.round(analysis.duration_seconds)}s</div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Scan Execution Time</div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function MetricPanel({ icon, title, value }: { icon: React.ReactNode; title: string; value: number }) {
  const color = value >= 85 ? 'text-emerald-500' : value >= 70 ? 'text-lime-500' : value >= 55 ? 'text-amber-500' : 'text-red-500'
  return (
    <div className="glass-card p-5 flex flex-col justify-between min-h-[100px] hover:border-slate-300 dark:hover:border-white/10 transition-all duration-200">
      <div className="flex items-center justify-between">
        <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">{title}</span>
        <div className={clsx('flex-shrink-0', color)}>{icon}</div>
      </div>
      <div>
        <div className={clsx('text-3xl font-extrabold tabular-nums', color)}>{Math.round(value)}</div>
      </div>
    </div>
  )
}
