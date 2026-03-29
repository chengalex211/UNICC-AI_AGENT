import { type FC, useState } from 'react'
import { detailedEval, type DetailedEvaluation } from '../data/mockData'
import { RecBadge } from '../components/Badge'
import { hapticSelect } from '../utils/haptic'

const expertColor: Record<string, string> = {
  'Security Expert':    'bg-rose-50 border-rose-200 text-rose-600',
  'Governance Expert':  'bg-violet-50 border-violet-200 text-violet-600',
  'UN Mission Expert':  'bg-sky-50 border-sky-200 text-sky-600',
}

interface Props { evaluation?: DetailedEvaluation | null }

const CouncilReview: FC<Props> = ({ evaluation }) => {
  const eval_ = evaluation ?? detailedEval
  const [expanded, setExpanded] = useState<number | null>(0)
  const { council_critiques } = eval_

  return (
    <div className="p-8 space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-apple-gray-900 mb-1">Council Review</h1>
        <p className="text-sm text-apple-gray-400">Cross-expert critique and arbitration · {eval_.system_name}</p>
      </div>

      {/* Deliberation flow */}
      <div className="card p-6">
        <p className="section-label">Deliberation Flow</p>
        <div className="flex items-start gap-4 mt-2">
          {[
            { label: 'Expert Reports', sub: '3 independent assessments', icon: '◈', done: true },
            { label: 'Cross-Critique', sub: `${council_critiques.length} critiques filed`, icon: '⇌', done: true },
            { label: 'Council Synthesis', sub: 'Disagreements resolved', icon: '◉', done: true },
            { label: 'Final Decision', sub: `${eval_.decision} issued`, icon: '✓', done: true },
          ].map((step, i) => (
            <div key={i} className="flex items-start gap-3 flex-1">
              <div className={`mt-0.5 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0
                ${step.done ? 'bg-apple-blue text-white' : 'bg-apple-gray-200 text-apple-gray-500'}`}>
                {step.icon}
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-apple-gray-900">{step.label}</p>
                <p className="text-xs text-apple-gray-400">{step.sub}</p>
              </div>
              {i < 3 && <div className="w-6 h-px bg-apple-gray-200 mt-3 mx-1 shrink-0" />}
            </div>
          ))}
        </div>
      </div>

      {/* Expert summary matrix */}
      <div className="card p-6">
        <p className="section-label">Expert Recommendation Matrix</p>
        <div className="grid grid-cols-3 gap-4 mt-2">
          {eval_.expert_reports.map(r => (
            <div key={r.id} className="flex items-center justify-between p-3 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
              <div className="flex items-center gap-2">
                <span>{r.icon}</span>
                <span className="text-xs font-semibold text-apple-gray-700">{r.shortTitle}</span>
              </div>
              <RecBadge rec={r.recommendation} size="sm" />
            </div>
          ))}
        </div>
      </div>

      {/* Critiques */}
      <div>
        <h2 className="text-base font-semibold text-apple-gray-900 mb-3">
          Cross-Expert Critiques
          <span className="ml-2 text-xs font-normal text-apple-gray-400">{council_critiques.length} filed</span>
        </h2>
        <div className="space-y-3">
          {council_critiques.map((critique, i) => {
            const isOpen = expanded === i
            const fromColor = expertColor[critique.from] ?? 'bg-gray-50 border-gray-200 text-gray-600'
            const onColor = expertColor[critique.on] ?? 'bg-gray-50 border-gray-200 text-gray-600'
            return (
              <div key={i} className="card overflow-hidden">
                {/* Header row */}
                <button
                  className="w-full text-left px-5 py-4 flex items-center gap-4 hover:bg-apple-gray-50 transition-colors"
                  onClick={() => { hapticSelect(); setExpanded(isOpen ? null : i) }}
                >
                  <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border ${fromColor}`}>
                    {critique.from}
                  </span>
                  <span className="text-xs text-apple-gray-400">on</span>
                  <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border ${onColor}`}>
                    {critique.on}
                  </span>
                  <div className="flex-1" />
                  <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${critique.agrees ? 'bg-apple-green-bg text-apple-green' : 'bg-apple-red-bg text-apple-red'}`}>
                    {critique.agrees ? 'Agrees' : 'Disagrees'}
                  </span>
                  <span className="text-xs text-apple-gray-400 ml-2">
                    {isOpen ? '▲' : '▼'}
                  </span>
                </button>

                {/* Key point preview */}
                <div className="px-5 pb-3 border-t border-apple-gray-50">
                  <p className="text-xs text-apple-gray-500 italic pt-2">"{critique.key_point}"</p>
                </div>

                {/* Expanded detail */}
                {isOpen && (
                  <div className="px-5 pb-5 space-y-4 border-t border-apple-gray-100 pt-4 animate-slide-up">
                    <div>
                      <p className="text-[11px] font-semibold text-apple-gray-400 uppercase tracking-wider mb-1.5">Divergence Type</p>
                      <span className="px-3 py-1 rounded-full bg-apple-gray-100 text-xs font-semibold text-apple-gray-600">
                        {critique.divergence_type.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <div>
                      <p className="text-[11px] font-semibold text-apple-gray-400 uppercase tracking-wider mb-1.5">Stance</p>
                      <p className="text-sm text-apple-gray-700 leading-relaxed">{critique.stance}</p>
                    </div>
                    <div>
                      <p className="text-[11px] font-semibold text-apple-gray-400 uppercase tracking-wider mb-2">Evidence References</p>
                      <div className="space-y-1.5">
                        {critique.evidence.map((ev, j) => (
                          <div key={j} className="flex items-start gap-2 px-3 py-2 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
                            <span className="text-apple-blue text-[10px] mt-0.5">§</span>
                            <span className="text-xs text-apple-gray-600">{ev}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default CouncilReview
