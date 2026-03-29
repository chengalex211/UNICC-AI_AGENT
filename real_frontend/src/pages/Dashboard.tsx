import { type FC } from 'react'
import type { EvaluationListItem } from '../api/client'
import { RecBadge, ConsensusBadge } from '../components/Badge'
import { hapticSelect } from '../utils/haptic'

interface Props {
  onSelect: (incidentId: string) => void
  onNewEvaluation: () => void
  evaluations: EvaluationListItem[]
}

const StatCard: FC<{ label: string; value: number | string; sub?: string; accent?: string }> = ({ label, value, sub, accent }) => (
  <div className="card p-5 animate-slide-up">
    <p className="text-xs font-semibold text-apple-gray-400 uppercase tracking-wider mb-2">{label}</p>
    <p className={`text-3xl font-bold leading-none mb-1 ${accent ?? 'text-apple-gray-900'}`}>{value}</p>
    {sub && <p className="text-xs text-apple-gray-400">{sub}</p>}
  </div>
)

const DonutRing: FC<{ approve: number; review: number; reject: number; total: number }> = ({ approve, review, reject, total }) => {
  const r = 40
  const circ = 2 * Math.PI * r
  const a = (approve / total) * circ
  const rv = (review / total) * circ
  const rej = (reject / total) * circ
  return (
    <svg viewBox="0 0 100 100" className="w-28 h-28 -rotate-90">
      <circle cx="50" cy="50" r={r} fill="none" stroke="#f5f5f7" strokeWidth="12" />
      <circle cx="50" cy="50" r={r} fill="none" stroke="#34c759" strokeWidth="12"
        strokeDasharray={`${a} ${circ - a}`} strokeLinecap="round" />
      <circle cx="50" cy="50" r={r} fill="none" stroke="#ff9500" strokeWidth="12"
        strokeDasharray={`${rv} ${circ - rv}`} strokeDashoffset={-a} strokeLinecap="round" />
      <circle cx="50" cy="50" r={r} fill="none" stroke="#ff3b30" strokeWidth="12"
        strokeDasharray={`${rej} ${circ - rej}`} strokeDashoffset={-(a + rv)} strokeLinecap="round" />
    </svg>
  )
}

/** Pairwise agreement %: rows where both experts have a non-null rec that matches */
const pairAgreement = (
  rows: { a: string | null | undefined; b: string | null | undefined }[]
): number => {
  const both = rows.filter(r => r.a && r.b)
  if (both.length === 0) return 0
  const agree = both.filter(r => r.a === r.b).length
  return Math.round((agree / both.length) * 100)
}

const Dashboard: FC<Props> = ({ onSelect, onNewEvaluation, evaluations }) => {
  const total = Math.max(evaluations.length, 1)
  const approved = evaluations.filter(e => e.decision === 'APPROVE').length
  const review = evaluations.filter(e => e.decision === 'REVIEW').length
  const rejected = evaluations.filter(e => e.decision === 'REJECT').length
  const fullConsensus = evaluations.filter(e => e.consensus === 'FULL').length
  const partialConsensus = evaluations.filter(e => e.consensus === 'PARTIAL').length
  const splitConsensus = evaluations.filter(e => e.consensus === 'SPLIT').length

  // Pairwise expert agreement — uses real rec_* columns from the API
  const hasExpertRecs = evaluations.some(e => e.rec_security || e.rec_governance || e.rec_un_mission)
  const e1e2 = pairAgreement(evaluations.map(e => ({ a: e.rec_security,   b: e.rec_governance })))
  const e2e3 = pairAgreement(evaluations.map(e => ({ a: e.rec_governance, b: e.rec_un_mission })))
  const e1e3 = pairAgreement(evaluations.map(e => ({ a: e.rec_security,   b: e.rec_un_mission })))
  const triAll = pairAgreement(
    evaluations.map(e => ({
      a: (e.rec_security && e.rec_governance && e.rec_security === e.rec_governance) ? e.rec_security : null,
      b: e.rec_un_mission,
    }))
  )

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      {/* Header + primary CTA */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-apple-gray-900 mb-1">Overview</h1>
          <p className="text-sm text-apple-gray-400">AI System Safety Evaluation Dashboard · UNICC Council</p>
        </div>
        <button
          onClick={() => { hapticSelect(); onNewEvaluation() }}
          className="btn-primary shrink-0"
        >
          ＋ New Evaluation
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Evaluated" value={total} sub="AI systems submitted" />
        <StatCard label="Approved" value={approved} sub={`${Math.round(approved/total*100)}% of submissions`} accent="text-apple-green" />
        <StatCard label="Needs Review" value={review} sub={`${Math.round(review/total*100)}% of submissions`} accent="text-apple-orange" />
        <StatCard label="Rejected" value={rejected} sub={`${Math.round(rejected/total*100)}% of submissions`} accent="text-apple-red" />
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Donut chart */}
        <div className="card p-6 flex flex-col items-center justify-center col-span-1">
          <p className="section-label w-full text-center">Decision Distribution</p>
          <div className="relative">
            <DonutRing approve={approved} review={review} reject={rejected} total={total} />
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-xl font-bold text-apple-gray-900">{total}</span>
              <span className="text-[10px] text-apple-gray-400">total</span>
            </div>
          </div>
          <div className="flex gap-4 mt-4">
            {[['#34c759','Approve'],['#ff9500','Review'],['#ff3b30','Reject']].map(([c,l]) => (
              <div key={l} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ background: c }} />
                <span className="text-[11px] text-apple-gray-500">{l}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Consensus + avg time */}
        <div className="card p-6 col-span-1 flex flex-col justify-between">
          <p className="section-label">Council Consensus</p>
          <div className="space-y-4 flex-1">
            {[
              { label: 'Full Consensus', value: fullConsensus, color: 'bg-apple-blue', total },
              { label: 'Partial Consensus', value: partialConsensus, color: 'bg-apple-orange', total },
              { label: 'No Consensus', value: splitConsensus, color: 'bg-apple-red', total },
            ].map(row => (
              <div key={row.label}>
                <div className="flex justify-between mb-1.5">
                  <span className="text-xs text-apple-gray-600">{row.label}</span>
                  <span className="text-xs font-semibold text-apple-gray-900">{row.value}</span>
                </div>
                <div className="score-bar">
                  <div className={`score-fill ${row.color}`} style={{ width: `${(row.value / total) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-5 pt-4 border-t border-apple-gray-100">
            <p className="text-xs text-apple-gray-400 mb-0.5">Recent Incidents</p>
            <p className="text-2xl font-bold text-apple-gray-900">{evaluations.length}</p>
          </div>
        </div>

        {/* Expert agreement matrix */}
        <div className="card p-6 col-span-1">
          <p className="section-label">Expert Alignment</p>
          {!hasExpertRecs ? (
            <p className="text-xs text-apple-gray-400 mt-3">
              No expert-level data yet — submit evaluations to populate.
            </p>
          ) : (
            <div className="space-y-3 mt-1">
              {[
                { label: 'Security × Governance', pct: e1e2 },
                { label: 'Governance × UN Mission', pct: e2e3 },
                { label: 'Security × UN Mission', pct: e1e3 },
                { label: 'Full Tri-Agreement', pct: triAll },
              ].map(row => (
                <div key={row.label}>
                  <div className="flex justify-between mb-1">
                    <span className="text-xs text-apple-gray-600">{row.label}</span>
                    <span className="text-xs font-semibold text-apple-gray-900">{row.pct}%</span>
                  </div>
                  <div className="score-bar">
                    <div
                      className={`score-fill ${row.pct >= 75 ? 'bg-apple-green' : row.pct >= 60 ? 'bg-apple-blue' : 'bg-apple-orange'}`}
                      style={{ width: `${row.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent evaluations */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-apple-gray-900">Recent Evaluations</h2>
          <span className="text-xs text-apple-gray-400">{evaluations.length} shown</span>
        </div>
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-apple-gray-100">
                {['System', 'Incident ID', 'Decision', 'Consensus', 'Updated'].map(h => (
                  <th key={h} className="px-5 py-3 text-left text-[11px] font-semibold text-apple-gray-400 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {evaluations.map((ev, i) => (
                <tr
                  key={ev.incident_id}
                  onClick={() => { hapticSelect(); onSelect(ev.incident_id) }}
                  className={`border-b border-apple-gray-50 hover:bg-apple-gray-50 cursor-pointer transition-colors ${i === evaluations.length - 1 ? 'border-none' : ''}`}
                >
                  <td className="px-5 py-3.5">
                    <span className="font-semibold text-apple-gray-900">{ev.system_name}</span>
                    <br /><span className="text-[11px] text-apple-gray-400">{ev.agent_id}</span>
                  </td>
                  <td className="px-5 py-3.5 text-apple-gray-500 text-xs">{ev.incident_id}</td>
                  <td className="px-5 py-3.5"><RecBadge rec={ev.decision} /></td>
                  <td className="px-5 py-3.5"><ConsensusBadge consensus={ev.consensus === 'SPLIT' ? 'NONE' : (ev.consensus ?? 'PARTIAL')} /></td>
                  <td className="px-5 py-3.5 text-xs text-apple-gray-400">{new Date(ev.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
