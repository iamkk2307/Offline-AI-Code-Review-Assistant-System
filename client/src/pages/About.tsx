import { Cpu, Shield, Zap, Code2, Brain, Database, ExternalLink } from 'lucide-react'
import { PageHeader } from '@/components/common'

const TECH_STACK = [
  { icon: <Cpu size={18} />,      label: 'Electron',       desc: 'Desktop shell' },
  { icon: <Code2 size={18} />,    label: 'React + TypeScript', desc: 'UI framework' },
  { icon: <Zap size={18} />,      label: 'Python Flask',   desc: 'Backend API' },
  { icon: <Brain size={18} />,    label: 'Scikit-learn + XGBoost', desc: 'ML models' },
  { icon: <Database size={18} />, label: 'SQLite',         desc: 'Local database' },
  { icon: <Shield size={18} />,   label: '100% Offline',   desc: 'No cloud, no API keys' },
]

const FEATURES = [
  '13 supported programming languages',
  '6 pre-trained ML models (no internet needed)',
  '50+ code metrics extracted per file',
  'Weighted Code Health Score algorithm',
  'Static analysis: security, performance, maintainability',
  'Plugin-based language architecture',
  'PDF, HTML, Markdown, JSON, CSV reports',
  'Parallel analysis with progress tracking',
  'Under 500MB memory usage',
  'Works on laptops with no GPU',
]

const ML_MODELS = [
  { name: 'Bug Detector',            algo: 'Random Forest',           type: 'Classification' },
  { name: 'Security Risk',           algo: 'XGBoost',                 type: 'Classification' },
  { name: 'Severity Classifier',     algo: 'Support Vector Machine',  type: 'Classification' },
  { name: 'Code Quality Scorer',     algo: 'Gradient Boosting',       type: 'Regression' },
  { name: 'Maintainability Scorer',  algo: 'Random Forest',           type: 'Regression' },
  { name: 'Readability Scorer',      algo: 'Gradient Boosting',       type: 'Regression' },
]

export default function About() {
  return (
    <div className="animate-slide-up">
      <PageHeader title="About" subtitle="Offline ML-Based Code Review Assistant" />
      <div className="p-6 space-y-6">
        {/* Hero */}
        <div className="glass-card p-8 text-center">
          <div className="w-16 h-16 rounded-2xl bg-primary-600 flex items-center justify-center mx-auto mb-4 shadow-glow-primary">
            <Cpu size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold gradient-text mb-2">Code Review Assistant</h1>
          <p className="text-slate-400 text-sm max-w-lg mx-auto">
            A production-quality desktop application that performs intelligent code reviews using
            pre-trained Machine Learning models and static analysis — completely offline.
          </p>
          <div className="flex items-center justify-center gap-4 mt-4 text-xs text-slate-500">
            <span>Version 1.0.0</span>
            <span>·</span>
            <span>No cloud. No API keys. No internet.</span>
          </div>
        </div>

        {/* Tech Stack */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Technology Stack</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {TECH_STACK.map(({ icon, label, desc }) => (
              <div key={label} className="bg-surface-800/50 rounded-xl p-3 flex items-center gap-3">
                <div className="text-primary-400 flex-shrink-0">{icon}</div>
                <div>
                  <div className="text-sm font-medium text-slate-300">{label}</div>
                  <div className="text-xs text-slate-500">{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ML Models */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">ML Models</h2>
          <div className="space-y-2">
            {ML_MODELS.map(({ name, algo, type }) => (
              <div key={name} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                <div className="flex items-center gap-2">
                  <Brain size={14} className="text-primary-400" />
                  <span className="text-sm text-slate-300">{name}</span>
                </div>
                <div className="flex items-center gap-2 text-right">
                  <span className="text-xs text-slate-500">{algo}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${type === 'Classification' ? 'bg-blue-500/15 text-blue-400' : 'bg-purple-500/15 text-purple-400'}`}>
                    {type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Features */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {FEATURES.map(f => (
              <div key={f} className="flex items-center gap-2 text-sm text-slate-400">
                <span className="text-emerald-400 flex-shrink-0">✓</span> {f}
              </div>
            ))}
          </div>
        </div>

        {/* Health Score Formula */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Health Score Formula</h2>
          <div className="code-block text-xs">
            Overall = (Quality × 0.30) + (Security × 0.25) + (Maintainability × 0.20) + (Performance × 0.15) + (Readability × 0.10)
          </div>
        </div>
      </div>
    </div>
  )
}
