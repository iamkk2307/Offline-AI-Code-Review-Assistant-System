import { useState, useEffect, useRef } from 'react'
import { Play, StopCircle, FileCode, AlertTriangle, ChevronDown, ChevronUp, Brain, Info, ShieldAlert, CheckCircle } from 'lucide-react'
import clsx from 'clsx'
import toast from 'react-hot-toast'
import { useAppStore } from '@/stores/appStore'
import { PageHeader, SeverityBadge, EmptyState, LoadingShimmer } from '@/components/common'
import api from '@/services/api'
import type { AnalysisJob, FileReviewResult, Issue } from '@/types'
import { getDetailedExplanation } from '@/services/ruleExplainer'

export default function Analysis() {
  const { selectedProject, currentAnalysis, setCurrentAnalysis, isAnalyzing, setIsAnalyzing, setCurrentJob } = useAppStore()
  const [job, setJob] = useState<AnalysisJob | null>(null)
  
  const [activeFileIndex, setActiveFileIndex] = useState<number | null>(null)
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null)
  const [severityFilter, setSeverityFilter] = useState<string>('ALL')
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const startAnalysis = async () => {
    if (!selectedProject) { toast.error('Select a project first'); return }
    setIsAnalyzing(true)
    setComparisonResult(null)
    try {
      const { job_id } = await api.analysis.start(selectedProject.id)
      pollRef.current = setInterval(async () => {
        const status = await api.analysis.status(job_id)
        setJob(status)
        setCurrentJob(status)
        if (status.status === 'completed') {
          clearInterval(pollRef.current!)
          setIsAnalyzing(false)
          if (status.result_id) {
            const result = await api.analysis.result(status.result_id)
            setCurrentAnalysis(result)
            setActiveFileIndex(0)
            toast.success('Analysis complete!')
          }
        } else if (status.status === 'failed') {
          clearInterval(pollRef.current!)
          setIsAnalyzing(false)
          toast.error('Analysis failed: ' + status.error)
        }
      }, 1000)
    } catch (e: any) {
      setIsAnalyzing(false)
      toast.error(e.message)
    }
  }

  const setComparisonResult = (val: null) => {}

  useEffect(() => () => { if (pollRef.current) clearInterval(pollRef.current) }, [])

  const fileResults = currentAnalysis?.file_results || []
  const severities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']

  const filteredFiles = fileResults.filter(fr => {
    if (severityFilter === 'ALL') return fr.issues.length > 0 || fr.error
    return fr.issues.some(i => i.severity === severityFilter)
  })

  // Select first file automatically if result available
  useEffect(() => {
    if (filteredFiles.length > 0 && activeFileIndex === null) {
      setActiveFileIndex(0)
    }
  }, [filteredFiles, activeFileIndex])

  const activeFile = activeFileIndex !== null && filteredFiles[activeFileIndex] ? filteredFiles[activeFileIndex] : null

  return (
    <div className="flex flex-col h-full overflow-hidden animate-slide-up">
      <PageHeader
        title="Analysis"
        subtitle={selectedProject ? selectedProject.name : 'No project selected'}
        actions={
          selectedProject && (
            <button
              onClick={startAnalysis}
              disabled={isAnalyzing}
              className={isAnalyzing ? 'btn-secondary' : 'btn-primary'}
            >
              {isAnalyzing
                ? <><StopCircle size={14} className="animate-pulse" /> Scanning...</>
                : <><Play size={14} /> Start Scan</>
              }
            </button>
          )
        }
      />

      {/* Main split area */}
      <div className="flex-1 flex min-h-0 divide-x divide-slate-200 dark:divide-white/5">
        {/* Left Side: Files list */}
        <div className="w-1/4 min-w-[200px] flex flex-col bg-slate-50 dark:bg-surface-950">
          <div className="p-3 border-b border-slate-200 dark:border-white/5 flex flex-wrap gap-1.5 items-center">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold w-full mb-1">Filter Severity:</span>
            {severities.map(s => (
              <button
                key={s}
                onClick={() => { setSeverityFilter(s); setActiveFileIndex(0); setSelectedIssue(null) }}
                className={clsx(
                  'text-[9px] px-2 py-1 rounded font-bold uppercase tracking-wider',
                  severityFilter === s
                    ? 'bg-primary-600 text-white shadow'
                    : 'bg-slate-200 dark:bg-surface-800 text-slate-500 dark:text-slate-400 hover:text-slate-200'
                )}
              >
                {s}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {filteredFiles.map((fr, idx) => (
              <button
                key={fr.file_path}
                onClick={() => { setActiveFileIndex(idx); setSelectedIssue(null) }}
                className={clsx(
                  'w-full text-left p-2.5 rounded-lg flex items-center justify-between gap-2 border transition-all text-xs font-semibold',
                  activeFileIndex === idx
                    ? 'bg-primary-50 dark:bg-primary-600/10 border-primary-500/30 text-primary-600 dark:text-primary-300'
                    : 'bg-transparent border-transparent text-slate-600 dark:text-slate-400 hover:bg-slate-200/40 dark:hover:bg-surface-800'
                )}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <FileCode size={14} className="text-slate-500 flex-shrink-0" />
                  <div className="truncate font-mono">{fr.filename}</div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {fr.issue_summary.critical > 0 && <span className="text-[9px] font-bold text-red-500">C</span>}
                  {fr.issue_summary.high > 0 && <span className="text-[9px] font-bold text-orange-500">H</span>}
                  <span className="text-[10px] text-slate-500 font-bold">{fr.issues.length}</span>
                </div>
              </button>
            ))}
            {filteredFiles.length === 0 && !isAnalyzing && (
              <div className="text-center py-8 text-xs text-slate-500">
                No issues detected! 🎉
              </div>
            )}
          </div>
        </div>

        {/* Center: Main File Scan details and issue rows list */}
        <div className="flex-1 flex flex-col min-w-0 p-6 overflow-y-auto space-y-4">
          {/* Progress Bar (if active) */}
          {isAnalyzing && job && (
            <div className="glass-card p-5 border border-primary-500/20 animate-scale-in">
              <div className="flex items-center justify-between mb-3 text-xs">
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {job.status === 'collecting_files' ? 'Collecting project files...' :
                   job.status === 'running' ? `Inference analysis engine scanning...` :
                   job.status === 'saving' ? 'Persisting issues database...' : job.status}
                </span>
                <span className="font-black text-primary-500">{job.progress}%</span>
              </div>
              <div className="progress-bar mb-2">
                <div
                  className="progress-bar-fill bg-primary-500"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
              {job.current_file && (
                <div className="text-[10px] text-slate-500 font-mono truncate">
                  Scan: {job.processed_files}/{job.total_files} — {job.current_file}
                </div>
              )}
            </div>
          )}

          {!selectedProject && (
            <EmptyState
              icon={<FileCode size={48} />}
              title="No Project Selected"
              description="Open a project workspace to analyze files."
            />
          )}

          {/* Selected File Details & issues list */}
          {selectedProject && !isAnalyzing && activeFile && (
            <div className="space-y-4 animate-scale-in">
              {/* File Title card */}
              <div className="glass-card p-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 font-mono flex items-center gap-2">
                    <FileCode size={16} /> {activeFile.filename}
                  </h3>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    Path: {activeFile.file_path} · Language: {activeFile.language}
                  </div>
                </div>
                <div className="text-right">
                  <div className={clsx('text-xl font-black',
                    (activeFile.scores?.overall ?? 0) >= 85 ? 'text-emerald-500' :
                    (activeFile.scores?.overall ?? 0) >= 70 ? 'text-lime-500' : 'text-red-500'
                  )}>
                    {Math.round(activeFile.scores?.overall ?? 0)}
                  </div>
                  <div className="text-[8px] text-slate-500 uppercase tracking-widest font-bold">Health Score</div>
                </div>
              </div>

              {/* List of issues in file */}
              <div className="space-y-2">
                {activeFile.issues.map((issue, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedIssue(issue)}
                    className={clsx(
                      'issue-card p-4 transition-all duration-200 cursor-pointer border',
                      selectedIssue === issue ? 'border-primary-500/50 bg-primary-500/5' : 'border-transparent',
                      issue.severity.toLowerCase()
                    )}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <SeverityBadge severity={issue.severity} size="sm" />
                          <span className="text-xs font-bold text-slate-700 dark:text-slate-200">{issue.title}</span>
                        </div>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">{issue.description}</p>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">Line {issue.line_number}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Issue detail drawer */}
        <div className="w-1/3 min-w-[320px] p-6 bg-slate-100 dark:bg-surface-900/60 overflow-y-auto space-y-4 border-l border-slate-200 dark:border-white/5">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest border-b border-slate-200 dark:border-white/5 pb-2 flex items-center gap-2">
            <Info size={12} /> Detailed Code Guide
          </h3>

          {selectedIssue ? (() => {
            const expl = getDetailedExplanation(selectedIssue, activeFile?.language || 'generic')
            return (
              <div className="space-y-4 animate-scale-in text-xs">
                {/* Header */}
                <div>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <SeverityBadge severity={selectedIssue.severity} size="sm" />
                    <span className="bg-slate-200 dark:bg-surface-800 text-[10px] text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                      C: {expl.confidence}
                    </span>
                    <span className="bg-slate-200 dark:bg-surface-800 text-[10px] text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                      Diff: {expl.difficulty}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mt-2">{selectedIssue.title}</h4>
                  <div className="text-[10px] text-slate-500 mt-1 uppercase tracking-widest font-mono">
                    Category: {selectedIssue.category} | Language: {activeFile?.language}
                  </div>
                </div>

                {/* Explanation */}
                <div className="space-y-2 border-t border-slate-200 dark:border-white/5 pt-3">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-0.5">Why Detected:</span>
                    <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{expl.detectedWhy}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-0.5">Dangerous Impact:</span>
                    <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{expl.dangerousWhy}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-0.5">Real-World Consequence:</span>
                    <p className="text-slate-600 dark:text-slate-300 leading-relaxed font-medium text-amber-600 dark:text-amber-400">{expl.consequences}</p>
                  </div>
                </div>

                {/* Side by Side Diff */}
                <div className="space-y-3 border-t border-slate-200 dark:border-white/5 pt-3">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block">Proposed Refactoring Comparison:</span>
                  
                  <div className="space-y-1">
                    <div className="text-[9px] text-red-500 dark:text-red-400 font-bold uppercase tracking-widest">Current Code (Line {selectedIssue.line_number}):</div>
                    <pre className="bg-red-500/10 border border-red-500/20 p-2.5 rounded-lg font-mono text-[10px] text-red-600 dark:text-red-400 overflow-x-auto">
                      {selectedIssue.code_snippet || '// Original code segment'}
                    </pre>
                  </div>

                  <div className="space-y-1">
                    <div className="text-[9px] text-emerald-500 dark:text-emerald-400 font-bold uppercase tracking-widest">Improved Code:</div>
                    <pre className="bg-emerald-500/10 border border-emerald-500/20 p-2.5 rounded-lg font-mono text-[10px] text-emerald-600 dark:text-emerald-400 overflow-x-auto">
                      {expl.improvedCode}
                    </pre>
                  </div>
                </div>

                {/* Change details & standards */}
                <div className="space-y-2 border-t border-slate-200 dark:border-white/5 pt-3">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-0.5">Changes Made:</span>
                    <p className="text-slate-600 dark:text-slate-300">{expl.changesMade}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-0.5">Standards & Best Practices:</span>
                    <p className="text-slate-600 dark:text-slate-300 font-semibold">{expl.standards}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-0.5">Additional Improvements:</span>
                    <p className="text-slate-600 dark:text-slate-300 italic">{expl.additional}</p>
                  </div>
                </div>
              </div>
            )
          })() : (
            <div className="text-center py-20 text-slate-500 text-xs font-medium">
              Select an issue from the central column to inspect details and code suggestions.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
