import { type FC } from 'react'
import { type DetailedEvaluation } from '../data/mockData'
import { RecBadge, ConsensusBadge } from '../components/Badge'
import { hapticButton } from '../utils/haptic'

export type ReportStep = 'overview' | 'experts' | 'council' | 'final'

const STEPS: { id: ReportStep; label: string; short: string }[] = [
  { id: 'overview', label: 'Overview', short: 'Summary' },
  { id: 'experts', label: 'Expert Analysis', short: 'Experts' },
  { id: 'council', label: 'Council Review', short: 'Council' },
  { id: 'final', label: 'Final Report', short: 'Final' },
]

interface Props {
  eval: DetailedEvaluation
  currentStep: ReportStep
  onStep: (step: ReportStep) => void
  /** Expert 1 report from the backend (optional, only present after a live submission) */
  expert1Report?: Record<string, any>
  onViewFull?: () => void
}

const LIVE_ATTACK_ERROR_MESSAGES: Record<string, { title: string; detail: string }> = {
  unreachable: {
    title: 'Project not running',
    detail: 'The target URL was unreachable. Start the project server and re-submit to enable live attack testing.',
  },
  server_error: {
    title: 'Target server error (HTTP 5xx)',
    detail: 'The target is running but returning server errors. Check the project\'s API key or service configuration.',
  },
  auth_error: {
    title: 'Invalid or missing API key',
    detail: 'The target returned HTTP 401/403. Verify the project\'s API key is correctly configured and restart the server.',
  },
  unknown: {
    title: 'Live attack could not proceed',
    detail: 'An unexpected error occurred before the live attack began. The evaluation fell back to document analysis.',
  },
}

const recMap = (r: string) => (r === 'PASS' || r === 'APPROVE' ? 'APPROVE' : r === 'FAIL' || r === 'REJECT' ? 'REJECT' : 'REVIEW')

const ReportOverview: FC<Props> = ({ eval: ev, currentStep, onStep, expert1Report, onViewFull }) => {
  const date = new Date(ev.submitted_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })

  return (
    <div className="p-8 space-y-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-apple-gray-900 mb-1">Report</h1>
          <p className="text-sm text-apple-gray-400">{ev.system_name} · {ev.category}</p>
        </div>
        {onViewFull && (
          <button
            onClick={() => { hapticButton(); onViewFull() }}
            className="flex items-center gap-2 px-4 py-2 rounded-apple-lg bg-apple-blue text-white text-xs font-semibold hover:opacity-90 transition-opacity shadow-sm"
          >
            <span>🗂</span>
            View Full Report
          </button>
        )}
      </div>

      {/* Expert 1 live attack results (only shown after a live submission) */}
      {expert1Report && (() => {
        const errorCode = expert1Report.live_attack_error_code as string | undefined
        const errorMsg  = expert1Report.live_attack_error  as string | undefined
        const errInfo   = errorCode ? (LIVE_ATTACK_ERROR_MESSAGES[errorCode] ?? LIVE_ATTACK_ERROR_MESSAGES.unknown) : null
        const isLive    = !errorCode && expert1Report.analysis_mode === 'live_attack'

        return (
          <div className="space-y-3">
            {/* ── Error banner (scenario A / B) ───────────────────────── */}
            {errInfo && (
              <div className="card p-4 border-2 border-apple-red/30 bg-red-50">
                <div className="flex items-start gap-3">
                  <span className="text-apple-red text-lg leading-none mt-0.5">⚠</span>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-apple-red">{errInfo.title}</p>
                    <p className="text-xs text-apple-gray-600 mt-0.5">{errInfo.detail}</p>
                    {errorMsg && (
                      <details className="mt-2">
                        <summary className="text-[11px] text-apple-gray-400 cursor-pointer select-none">
                          Technical details
                        </summary>
                        <p className="text-[11px] text-apple-gray-500 mt-1 font-mono break-all">
                          {errorMsg.slice(0, 300)}{errorMsg.length > 300 ? '…' : ''}
                        </p>
                      </details>
                    )}
                    <p className="text-[11px] text-apple-gray-400 mt-2 italic">
                      Live attack was skipped — results below are from document analysis.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* ── Normal results card ──────────────────────────────────── */}
            <div className={`card p-6 border-2 ${isLive ? 'border-apple-blue/20 bg-apple-blue-light/30' : 'border-apple-gray-100'}`}>
              <p className="section-label">
                Expert 1 {isLive ? 'Live Attack Results (API)' : 'Security Assessment (API)'}
              </p>
              <div className="flex flex-wrap items-center gap-3 mt-2">
                {expert1Report.recommendation != null && (
                  <RecBadge rec={recMap(expert1Report.recommendation)} />
                )}
                {expert1Report.risk_tier != null && (
                  <span className="px-3 py-1 rounded-full text-xs font-semibold bg-apple-gray-100 text-apple-gray-700">
                    Risk: {expert1Report.risk_tier}
                  </span>
                )}
                {expert1Report.session_id != null && (
                  <span className="text-[11px] text-apple-gray-400">Session: {String(expert1Report.session_id).slice(0, 20)}…</span>
                )}
              </div>
              {isLive && Array.isArray(expert1Report.test_coverage?.attack_techniques_tested) && expert1Report.test_coverage!.attack_techniques_tested!.length > 0 && (
                <p className="text-xs text-apple-gray-600 mt-3">
                  Attack techniques tested: {expert1Report.test_coverage!.attack_techniques_tested!.length}
                </p>
              )}
              {Array.isArray(expert1Report.key_findings) && expert1Report.key_findings!.length > 0 && (
                <ul className="mt-3 space-y-1.5">
                  {expert1Report.key_findings!.slice(0, 5).map((f: unknown, i: number) => (
                    <li key={i} className="text-xs text-apple-gray-700 flex gap-2">
                      <span className="text-apple-red shrink-0">•</span>
                      <span>{String(f)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )
      })()}

      {/* Summary card */}
      <div className="card p-6">
        <p className="section-label">Assessment Summary</p>
        <div className="flex flex-wrap items-center gap-4 mt-3">
          <RecBadge rec={ev.decision} />
          <ConsensusBadge consensus={ev.consensus} />
          <span className="text-xs text-apple-gray-400">{date}</span>
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          {ev.expert_reports.map(r => (
            <div key={r.id} className="flex items-center gap-2 px-3 py-2 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
              <span>{r.icon}</span>
              <span className="text-xs font-medium text-apple-gray-700">{r.shortTitle}</span>
              <RecBadge rec={r.recommendation} size="sm" />
            </div>
          ))}
        </div>
        <p className="text-sm text-apple-gray-600 mt-4 leading-relaxed line-clamp-3">{ev.final_rationale}</p>
      </div>

      {/* Step navigation — clear order */}
      <div className="card p-6">
        <p className="section-label">View full report</p>
        <p className="text-sm text-apple-gray-500 mb-4">Follow the evaluation flow in order.</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {STEPS.map((s, i) => {
            const active = currentStep === s.id
            const isOverview = s.id === 'overview'
            return (
              <button
                key={s.id}
                onClick={() => {
                  hapticButton()
                  onStep(s.id)
                }}
                className={`text-left p-4 rounded-apple-lg border-2 transition-all duration-200
                  ${active ? 'border-apple-blue bg-apple-blue-light' : 'border-apple-gray-100 bg-white hover:border-apple-gray-200 hover:bg-apple-gray-50'}`}
              >
                <span className="text-xs font-semibold text-apple-gray-400">Step {i + 1}</span>
                <p className="text-sm font-semibold text-apple-gray-900 mt-1">{s.label}</p>
                {!isOverview && (
                  <span className="text-[11px] text-apple-gray-400 mt-0.5 inline-block">View details →</span>
                )}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ReportOverview
export { STEPS as REPORT_STEPS }
