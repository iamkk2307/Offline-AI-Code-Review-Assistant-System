import clsx from 'clsx'
import type { Severity } from '@/types'

interface ScoreCardProps {
  label: string
  score: number
  size?: 'sm' | 'md' | 'lg'
  showBar?: boolean
}

export function getScoreColor(score: number): string {
  if (score >= 85) return 'score-excellent'
  if (score >= 70) return 'score-good'
  if (score >= 55) return 'score-fair'
  return 'score-poor'
}

export function getScoreLabel(score: number): string {
  if (score >= 85) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 55) return 'Fair'
  if (score >= 40) return 'Poor'
  return 'Critical'
}

export function getScoreBg(score: number): string {
  if (score >= 85) return 'bg-emerald-500'
  if (score >= 70) return 'bg-lime-500'
  if (score >= 55) return 'bg-amber-500'
  return 'bg-red-500'
}

export function ScoreCard({ label, score, size = 'md', showBar = false }: ScoreCardProps) {
  const rounded = Math.round(score * 10) / 10
  const colorClass = getScoreColor(rounded)
  const fontSize = { sm: 'text-2xl', md: 'text-4xl', lg: 'text-5xl' }[size]

  return (
    <div className="stat-card animate-scale-in">
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">{label}</div>
      <div className={clsx('font-bold tabular-nums', fontSize, colorClass)}>
        {rounded}
      </div>
      <div className={clsx('text-xs mt-1', colorClass, 'opacity-80')}>
        {getScoreLabel(rounded)}
      </div>
      {showBar && (
        <div className="progress-bar mt-3">
          <div
            className={clsx('progress-bar-fill', getScoreBg(rounded))}
            style={{ width: `${Math.min(100, Math.max(0, rounded))}%` }}
          />
        </div>
      )}
    </div>
  )
}

interface SeverityBadgeProps {
  severity: Severity
  size?: 'sm' | 'md'
}

const SEVERITY_CONFIG: Record<Severity, { label: string; className: string }> = {
  CRITICAL: { label: 'Critical', className: 'badge-critical' },
  HIGH:     { label: 'High',     className: 'badge-high' },
  MEDIUM:   { label: 'Medium',   className: 'badge-medium' },
  LOW:      { label: 'Low',      className: 'badge-low' },
  INFO:     { label: 'Info',     className: 'badge-info' },
}

export function SeverityBadge({ severity, size = 'md' }: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.INFO
  return (
    <span className={clsx(
      'inline-flex items-center rounded-lg font-semibold uppercase tracking-wider',
      config.className,
      size === 'sm' ? 'text-[10px] px-2 py-0.5' : 'text-xs px-2.5 py-1'
    )}>
      {config.label}
    </span>
  )
}

interface StatRowProps {
  label: string
  value: string | number
  valueClass?: string
}

export function StatRow({ label, value, valueClass }: StatRowProps) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
      <span className="text-sm text-slate-400">{label}</span>
      <span className={clsx('text-sm font-medium text-slate-200', valueClass)}>{value}</span>
    </div>
  )
}

export function LoadingShimmer({ rows = 3, height = 'h-20' }: { rows?: number; height?: string }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className={clsx('shimmer rounded-xl', height)} />
      ))}
    </div>
  )
}

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
      {icon && <div className="text-slate-600 mb-4">{icon}</div>}
      <h3 className="text-lg font-semibold text-slate-300 mb-2">{title}</h3>
      {description && <p className="text-sm text-slate-500 max-w-sm mb-6">{description}</p>}
      {action}
    </div>
  )
}

interface PageHeaderProps {
  title: string
  subtitle?: string
  actions?: React.ReactNode
}

export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className="page-header">
      <div>
        <h1 className="text-lg font-bold text-slate-100">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}
