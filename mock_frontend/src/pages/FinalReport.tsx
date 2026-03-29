import { type FC, useState } from 'react'
import { detailedEval } from '../data/mockData'
import { RecBadge, ConsensusBadge } from '../components/Badge'

const FinalReport: FC = () => {
  const [copied, setCopied] = useState(false)
  const { system_name, agent_id, category, decision, consensus, expert_reports,
          final_rationale, key_conditions, submitted_at } = detailedEval

  const date = new Date(submitted_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })

  const handleCopy = () => {
    navigator.clipboard.writeText(final_rationale)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="p-8 space-y-6 animate-fade-in max-w-4xl">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-apple-gray-900 mb-1">Final Report</h1>
          <p className="text-sm text-apple-gray-400">UNICC AI Safety Council · Official Assessment</p>
        </div>
        <button className="btn-secondary text-xs">↓ Export PDF</button>
      </div>

      {/* Report card */}
      <div className="card overflow-hidden">
        {/* Report header bar */}
        <div className={`px-6 py-4 flex items-center justify-between
          ${decision === 'REJECT' ? 'bg-apple-red-bg border-b border-red-100'
          : decision === 'REVIEW' ? 'bg-apple-orange-bg border-b border-orange-100'
          : 'bg-apple-green-bg border-b border-green-100'}`}>
          <div>
            <p className="text-xs font-semibold text-apple-gray-400 uppercase tracking-wider">Official Decision</p>
            <h2 className="text-xl font-bold text-apple-gray-900 mt-0.5">{system_name}</h2>
            <p className="text-xs text-apple-gray-500 mt-0.5">{agent_id} · {category}</p>
          </div>
          <div className="text-right space-y-1.5">
            <div className="flex items-center justify-end gap-2">
              <RecBadge rec={decision} />
              <ConsensusBadge consensus={consensus} />
            </div>
            <p className="text-[11px] text-apple-gray-400">{date}</p>
          </div>
        </div>

        {/* Expert votes */}
        <div className="px-6 py-4 border-b border-apple-gray-100">
          <p className="section-label">Expert Votes</p>
          <div className="flex gap-6">
            {expert_reports.map(r => (
              <div key={r.id} className="flex items-center gap-2.5">
                <span className="text-lg">{r.icon}</span>
                <div>
                  <p className="text-[11px] text-apple-gray-400">{r.shortTitle}</p>
                  <RecBadge rec={r.recommendation} size="sm" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Council rationale */}
        <div className="px-6 py-5 border-b border-apple-gray-100">
          <div className="flex items-center justify-between mb-3">
            <p className="section-label mb-0">Council Rationale</p>
            <button
              onClick={handleCopy}
              className="text-[11px] text-apple-blue hover:underline"
            >
              {copied ? '✓ Copied' : 'Copy'}
            </button>
          </div>
          <p className="text-sm text-apple-gray-700 leading-relaxed">{final_rationale}</p>
        </div>

        {/* Conditions */}
        {key_conditions.length > 0 && (
          <div className="px-6 py-5">
            <p className="section-label">
              {decision === 'REJECT' ? 'Conditions for Re-submission' : 'Required Actions Before Deployment'}
            </p>
            <div className="space-y-2.5 mt-1">
              {key_conditions.map((cond, i) => (
                <div key={i} className="flex gap-3 items-start p-3 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
                  <span className="w-5 h-5 rounded-full bg-apple-blue-light text-apple-blue text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <p className="text-xs text-apple-gray-700 leading-relaxed">{cond}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Score summary */}
      <div className="card p-6">
        <p className="section-label">Aggregate Dimension Scores</p>
        <div className="grid grid-cols-3 gap-6 mt-2">
          {expert_reports.map(report => (
            <div key={report.id}>
              <div className="flex items-center gap-2 mb-3">
                <span>{report.icon}</span>
                <span className="text-xs font-semibold text-apple-gray-700">{report.shortTitle}</span>
              </div>
              <div className="space-y-2">
                {report.scores.map(s => {
                  const pct = (s.value / s.max) * 100
                  const color = pct >= 80 ? 'bg-apple-green' : pct >= 50 ? 'bg-apple-blue' : pct >= 30 ? 'bg-apple-orange' : 'bg-apple-red'
                  return (
                    <div key={s.label}>
                      <div className="flex justify-between mb-1">
                        <span className="text-[11px] text-apple-gray-500">{s.label}</span>
                        <span className="text-[11px] font-semibold text-apple-gray-700">{s.value}/{s.max}</span>
                      </div>
                      <div className="score-bar">
                        <div className={`score-fill ${color}`} style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer note */}
      <div className="p-4 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
        <p className="text-[11px] text-apple-gray-400 leading-relaxed text-center">
          This assessment was generated by the UNICC AI Safety Council system (Expert 1: Security Adversarial ·
          Expert 2: Governance & Compliance · Expert 3: UN Mission Fit). All findings are based on automated
          analysis and should be reviewed by qualified human evaluators before acting on any decision.
        </p>
      </div>
    </div>
  )
}

export default FinalReport
