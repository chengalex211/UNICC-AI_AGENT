import { type FC, useEffect, useState } from 'react'
import type { EvaluationListItem, KnowledgeStats } from '../api/client'
import { getKnowledgeStats } from '../api/client'
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

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

const decisionColor: Record<string, string> = {
  APPROVE: 'text-apple-green',
  REVIEW:  'text-apple-orange',
  REJECT:  'text-apple-red',
}
const decisionDot: Record<string, string> = {
  APPROVE: 'bg-apple-green',
  REVIEW:  'bg-apple-orange',
  REJECT:  'bg-apple-red',
}

const Dashboard: FC<Props> = ({ onSelect, onNewEvaluation, evaluations }) => {
  const [kbStats, setKbStats] = useState<KnowledgeStats | null>(null)

  useEffect(() => {
    getKnowledgeStats().then(setKbStats).catch(() => {})
  }, [])

  const total    = Math.max(evaluations.length, 1)
  const approved = evaluations.filter(e => e.decision === 'APPROVE').length
  const review   = evaluations.filter(e => e.decision === 'REVIEW').length
  const rejected = evaluations.filter(e => e.decision === 'REJECT').length

  // Per-expert risk signals
  const recCounts = (field: 'rec_security' | 'rec_governance' | 'rec_un_mission') => ({
    APPROVE: evaluations.filter(e => e[field] === 'APPROVE').length,
    REVIEW:  evaluations.filter(e => e[field] === 'REVIEW').length,
    REJECT:  evaluations.filter(e => e[field] === 'REJECT').length,
  })
  const expertSignals = [
    { label: 'Expert 1', sub: 'Security',    counts: recCounts('rec_security') },
    { label: 'Expert 2', sub: 'Governance',  counts: recCounts('rec_governance') },
    { label: 'Expert 3', sub: 'UN Mission',  counts: recCounts('rec_un_mission') },
  ]
  const hasRecs = evaluations.some(e => e.rec_security || e.rec_governance || e.rec_un_mission)

  const recent5 = evaluations.slice(0, 5)

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      {/* Header */}
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

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Evaluated"  value={evaluations.length} sub="AI systems submitted" />
        <StatCard label="Approved"         value={approved}  sub={`${Math.round(approved/total*100)}% of submissions`}  accent="text-apple-green" />
        <StatCard label="Needs Review"     value={review}    sub={`${Math.round(review/total*100)}% of submissions`}    accent="text-apple-orange" />
        <StatCard label="Rejected"         value={rejected}  sub={`${Math.round(rejected/total*100)}% of submissions`}  accent="text-apple-red" />
      </div>

      {/* 3-panel row */}
      <div className="grid grid-cols-3 gap-6">

        {/* Panel 1 — Recent Evaluations */}
        <div className="card p-6 flex flex-col gap-3">
          <p className="section-label">Recent Evaluations</p>
          {recent5.length === 0 ? (
            <p className="text-xs text-apple-gray-400 mt-2">No evaluations yet.</p>
          ) : (
            <div className="space-y-2.5 flex-1">
              {recent5.map(ev => (
                <button
                  key={ev.incident_id}
                  onClick={() => { hapticSelect(); onSelect(ev.incident_id) }}
                  className="w-full flex items-center justify-between gap-2 group text-left
                    hover:bg-apple-gray-50 rounded-apple px-2 py-1.5 -mx-2 transition-colors"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className={`w-2 h-2 rounded-full shrink-0 ${decisionDot[ev.decision] ?? 'bg-apple-gray-300'}`} />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-apple-gray-900 truncate leading-tight">
                        {ev.system_name}
                      </p>
                      <p className="text-[11px] text-apple-gray-400 truncate">{ev.agent_id}</p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end shrink-0 gap-0.5">
                    <span className={`text-xs font-semibold ${decisionColor[ev.decision] ?? ''}`}>
                      {ev.decision}
                    </span>
                    <span className="text-[10px] text-apple-gray-400">{timeAgo(ev.created_at)}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
          {evaluations.length > 5 && (
            <p className="text-[11px] text-apple-gray-400 pt-1 border-t border-apple-gray-100">
              +{evaluations.length - 5} more below
            </p>
          )}
        </div>

        {/* Panel 2 — Expert Risk Signals */}
        <div className="card p-6 flex flex-col gap-3">
          <p className="section-label">Expert Risk Signals</p>
          {!hasRecs ? (
            <p className="text-xs text-apple-gray-400 mt-2">
              Submit evaluations to see per-expert breakdown.
            </p>
          ) : (
            <div className="space-y-4 flex-1">
              {expertSignals.map(ex => {
                const rowTotal = ex.counts.APPROVE + ex.counts.REVIEW + ex.counts.REJECT || 1
                return (
                  <div key={ex.label}>
                    <div className="flex items-baseline justify-between mb-1.5">
                      <div>
                        <span className="text-xs font-semibold text-apple-gray-900">{ex.label}</span>
                        <span className="text-[11px] text-apple-gray-400 ml-1.5">{ex.sub}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px]">
                        <span className="text-apple-green font-semibold">{ex.counts.APPROVE}A</span>
                        <span className="text-apple-orange font-semibold">{ex.counts.REVIEW}R</span>
                        <span className="text-apple-red font-semibold">{ex.counts.REJECT}X</span>
                      </div>
                    </div>
                    {/* Stacked bar */}
                    <div className="flex h-2 rounded-full overflow-hidden bg-apple-gray-100 gap-px">
                      {ex.counts.APPROVE > 0 && (
                        <div className="bg-apple-green h-full transition-all"
                          style={{ width: `${(ex.counts.APPROVE / rowTotal) * 100}%` }} />
                      )}
                      {ex.counts.REVIEW > 0 && (
                        <div className="bg-apple-orange h-full transition-all"
                          style={{ width: `${(ex.counts.REVIEW / rowTotal) * 100}%` }} />
                      )}
                      {ex.counts.REJECT > 0 && (
                        <div className="bg-apple-red h-full transition-all"
                          style={{ width: `${(ex.counts.REJECT / rowTotal) * 100}%` }} />
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
          <div className="mt-auto pt-3 border-t border-apple-gray-100 flex gap-4 text-[11px]">
            {[['#34c759','Approve'],['#ff9500','Review'],['#ff3b30','Reject']].map(([c, l]) => (
              <div key={l} className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ background: c }} />
                <span className="text-apple-gray-500">{l}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Panel 3 — Knowledge Bases */}
        <div className="card p-6 flex flex-col gap-3">
          <p className="section-label">Knowledge Bases</p>
          {kbStats === null ? (
            <div className="flex items-center gap-2 mt-2">
              <div className="w-3.5 h-3.5 border border-apple-blue border-t-transparent rounded-full animate-spin" />
              <span className="text-xs text-apple-gray-400">Loading…</span>
            </div>
          ) : (
            <div className="space-y-3 flex-1">
              {kbStats.experts.map(ex => (
                <div key={ex.key} className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-apple-gray-900 leading-tight">{ex.label}</p>
                    <p className="text-[11px] text-apple-gray-400 truncate">{ex.description}</p>
                  </div>
                  <div className="shrink-0 text-right">
                    <span className={`text-sm font-bold ${ex.doc_count > 0 ? 'text-apple-blue' : 'text-apple-gray-300'}`}>
                      {ex.doc_count.toLocaleString()}
                    </span>
                    <p className="text-[10px] text-apple-gray-400">docs</p>
                  </div>
                </div>
              ))}
            </div>
          )}
          {kbStats !== null && (
            <div className="mt-auto pt-3 border-t border-apple-gray-100 flex items-center justify-between">
              <span className="text-[11px] text-apple-gray-400">Case precedents indexed</span>
              <span className="text-sm font-bold text-apple-gray-900">{kbStats.cases_indexed}</span>
            </div>
          )}
        </div>
      </div>

      {/* Full evaluations table */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-apple-gray-900">All Evaluations</h2>
          <span className="text-xs text-apple-gray-400">{evaluations.length} records</span>
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
