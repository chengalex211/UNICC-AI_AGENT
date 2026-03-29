import { type FC, useState } from 'react'
import { detailedEval, type ExpertReport } from '../data/mockData'
import { RecBadge } from '../components/Badge'

const ScoreRow: FC<{ label: string; value: number; max: number }> = ({ label, value, max }) => {
  const pct = (value / max) * 100
  const color = pct >= 80 ? 'bg-apple-green' : pct >= 50 ? 'bg-apple-blue' : pct >= 30 ? 'bg-apple-orange' : 'bg-apple-red'
  return (
    <div>
      <div className="flex justify-between mb-1.5">
        <span className="text-xs text-apple-gray-600">{label}</span>
        <span className="text-xs font-bold text-apple-gray-900">{value}/{max}</span>
      </div>
      <div className="score-bar">
        <div className={`score-fill ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

const ExpertCard: FC<{ report: ExpertReport; active: boolean; onClick: () => void }> = ({ report, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full text-left p-4 rounded-apple-lg border-2 transition-all duration-200
      ${active ? 'border-apple-blue bg-apple-blue-light' : 'border-apple-gray-100 bg-white hover:border-apple-gray-200'}`}
  >
    <div className="flex items-center justify-between mb-2">
      <span className="text-xl">{report.icon}</span>
      <RecBadge rec={report.recommendation} size="sm" />
    </div>
    <p className="text-sm font-semibold text-apple-gray-900 leading-snug mb-0.5">{report.title}</p>
    <p className="text-[11px] text-apple-gray-400">{report.elapsed}s elapsed</p>
  </button>
)

const ExpertAnalysis: FC = () => {
  const [activeId, setActiveId] = useState<ExpertReport['id']>('security')
  const active = detailedEval.expert_reports.find(r => r.id === activeId)!

  return (
    <div className="p-8 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-apple-gray-900 mb-1">Expert Analysis</h1>
          <p className="text-sm text-apple-gray-400">{detailedEval.system_name} · {detailedEval.category}</p>
        </div>
        <RecBadge rec={detailedEval.decision} />
      </div>

      {/* System description */}
      <div className="card p-5">
        <p className="section-label">System Under Evaluation</p>
        <p className="text-sm text-apple-gray-700 leading-relaxed">{detailedEval.description}</p>
      </div>

      {/* Expert selector */}
      <div className="grid grid-cols-3 gap-3">
        {detailedEval.expert_reports.map(r => (
          <ExpertCard key={r.id} report={r} active={activeId === r.id} onClick={() => setActiveId(r.id)} />
        ))}
      </div>

      {/* Active expert detail */}
      <div className="card p-6 animate-slide-up" key={activeId}>
        <div className="flex items-center gap-3 mb-6">
          <span className="text-2xl">{active.icon}</span>
          <div>
            <h2 className="text-base font-bold text-apple-gray-900">{active.title}</h2>
            <div className="flex items-center gap-2 mt-0.5">
              <RecBadge rec={active.recommendation} />
              <span className="text-xs text-apple-gray-400">· {active.elapsed}s</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-8">
          {/* Scores */}
          <div>
            <p className="section-label">Dimension Scores</p>
            <div className="space-y-3.5">
              {active.scores.map(s => <ScoreRow key={s.label} {...s} />)}
            </div>
          </div>

          {/* Findings + refs */}
          <div className="space-y-6">
            <div>
              <p className="section-label">Key Findings</p>
              <ul className="space-y-2.5">
                {active.findings.map((f, i) => (
                  <li key={i} className="flex gap-2.5">
                    <span className="w-4 h-4 rounded-full bg-apple-red-bg text-apple-red text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">!</span>
                    <p className="text-xs text-apple-gray-700 leading-relaxed">{f}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="section-label">Regulatory References</p>
              <div className="space-y-1.5">
                {active.framework_refs.map((ref, i) => (
                  <div key={i} className="flex items-center gap-2 px-3 py-2 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
                    <span className="text-apple-blue text-[10px]">§</span>
                    <span className="text-xs text-apple-gray-600">{ref}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExpertAnalysis
