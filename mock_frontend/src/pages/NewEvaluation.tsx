import { type FC, useState } from 'react'

interface Props {
  onSubmit: () => void
}

const CATEGORIES = [
  'Humanitarian Aid', 'Peacekeeping', 'Child Protection', 'Labor Rights',
  'Governance', 'Language & Translation', 'Healthcare', 'Education', 'Other',
]

const DEPLOY_ZONES = [
  'Active Conflict Zone', 'Post-Conflict Zone', 'Development Context',
  'UN Headquarters', 'Field Office', 'Global/Multi-Region',
]

const NewEvaluation: FC<Props> = ({ onSubmit }) => {
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    system_name: '', agent_id: '', category: '', deploy_zone: '',
    description: '', capabilities: '', data_sources: '', human_oversight: '',
  })

  const handleSubmit = () => {
    setLoading(true)
    setTimeout(() => { setLoading(false); onSubmit() }, 2200)
  }

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  const canProceed1 = form.system_name && form.agent_id && form.category && form.deploy_zone
  const canProceed2 = form.description && form.capabilities

  return (
    <div className="p-8 max-w-3xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-apple-gray-900 mb-1">New Evaluation</h1>
        <p className="text-sm text-apple-gray-400">Submit an AI system for safety assessment by the UNICC Council</p>
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        {(['System Info', 'Capabilities', 'Review & Submit'] as const).map((label, i) => {
          const s = (i + 1) as 1 | 2 | 3
          const done = step > s
          const active = step === s
          return (
            <div key={label} className="flex items-center gap-2">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold transition-all
                ${done ? 'bg-apple-green text-white' : active ? 'bg-apple-blue text-white' : 'bg-apple-gray-200 text-apple-gray-500'}`}>
                {done ? '✓' : s}
              </div>
              <span className={`text-xs font-medium ${active ? 'text-apple-gray-900' : 'text-apple-gray-400'}`}>{label}</span>
              {i < 2 && <div className="w-8 h-px bg-apple-gray-200 mx-1" />}
            </div>
          )
        })}
      </div>

      <div className="card p-7 space-y-6">
        {/* Step 1 */}
        {step === 1 && (
          <div className="space-y-5 animate-slide-up">
            <div>
              <p className="section-label">System Identification</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-apple-gray-600 mb-1.5">System Name *</label>
                  <input className="input-field" placeholder="e.g. RefugeeAssist v2" value={form.system_name} onChange={set('system_name')} />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-apple-gray-600 mb-1.5">Agent ID *</label>
                  <input className="input-field" placeholder="e.g. refugee-assist-v2" value={form.agent_id} onChange={set('agent_id')} />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-apple-gray-600 mb-1.5">Category *</label>
                <select className="input-field" value={form.category} onChange={set('category')}>
                  <option value="">Select category</option>
                  {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-apple-gray-600 mb-1.5">Deployment Zone *</label>
                <select className="input-field" value={form.deploy_zone} onChange={set('deploy_zone')}>
                  <option value="">Select zone</option>
                  {DEPLOY_ZONES.map(z => <option key={z}>{z}</option>)}
                </select>
              </div>
            </div>

            <div className="p-4 rounded-apple bg-apple-blue-light border border-blue-100">
              <div className="flex gap-2.5">
                <span className="text-blue-500 text-base mt-0.5">ℹ</span>
                <p className="text-xs text-apple-blue leading-relaxed">
                  Systems deployed in <strong>Active or Post-Conflict Zones</strong> automatically qualify as High-Risk under EU AI Act Annex III and will receive additional security scrutiny.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Step 2 */}
        {step === 2 && (
          <div className="space-y-5 animate-slide-up">
            <div>
              <label className="block text-xs font-semibold text-apple-gray-600 mb-1.5">System Description *</label>
              <textarea
                className="input-field resize-none h-28"
                placeholder="Describe what this AI system does, its primary functions, and how it makes decisions..."
                value={form.description}
                onChange={set('description')}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-apple-gray-600 mb-1.5">Key Capabilities *</label>
              <textarea
                className="input-field resize-none h-20"
                placeholder="List the main capabilities: e.g. automated allocation, biometric matching, natural language processing..."
                value={form.capabilities}
                onChange={set('capabilities')}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-apple-gray-600 mb-1.5">Data Sources</label>
                <textarea
                  className="input-field resize-none h-20"
                  placeholder="Describe data inputs: databases, APIs, user-provided data..."
                  value={form.data_sources}
                  onChange={set('data_sources')}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-apple-gray-600 mb-1.5">Human Oversight</label>
                <textarea
                  className="input-field resize-none h-20"
                  placeholder="Describe any human review processes, appeal mechanisms, override capabilities..."
                  value={form.human_oversight}
                  onChange={set('human_oversight')}
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 3 */}
        {step === 3 && (
          <div className="space-y-5 animate-slide-up">
            <p className="section-label">Review Submission</p>
            <div className="space-y-3">
              {[
                ['System Name', form.system_name],
                ['Agent ID', form.agent_id],
                ['Category', form.category],
                ['Deployment Zone', form.deploy_zone],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-2.5 border-b border-apple-gray-100">
                  <span className="text-xs text-apple-gray-400">{k}</span>
                  <span className="text-sm font-semibold text-apple-gray-900">{v}</span>
                </div>
              ))}
            </div>
            <div className="p-4 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
              <p className="text-xs font-semibold text-apple-gray-600 mb-2">Description</p>
              <p className="text-sm text-apple-gray-700 leading-relaxed">{form.description}</p>
            </div>

            <div className="p-4 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
              <p className="text-xs font-semibold text-apple-gray-600 mb-3">Evaluation Pipeline</p>
              <div className="flex items-center gap-2">
                {['Expert 1\nSecurity', 'Expert 2\nGovernance', 'Expert 3\nUN Mission', 'Council\nReview', 'Final\nReport'].map((label, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="text-center">
                      <div className="w-9 h-9 rounded-full border-2 border-apple-blue bg-apple-blue-light flex items-center justify-center text-apple-blue text-xs font-bold">
                        {i + 1}
                      </div>
                      <p className="text-[10px] text-apple-gray-400 mt-1 whitespace-pre-line leading-tight">{label}</p>
                    </div>
                    {i < 4 && <div className="w-5 h-px bg-apple-gray-200 mt-[-14px]" />}
                  </div>
                ))}
              </div>
            </div>

            {loading && (
              <div className="flex flex-col items-center py-6 gap-3">
                <div className="w-8 h-8 border-2 border-apple-blue border-t-transparent rounded-full animate-spin" />
                <p className="text-sm text-apple-gray-500">Submitting to evaluation pipeline…</p>
              </div>
            )}
          </div>
        )}

        {/* Navigation */}
        {!loading && (
          <div className="flex justify-between pt-2 border-t border-apple-gray-100">
            {step > 1
              ? <button className="btn-secondary" onClick={() => setStep(s => (s - 1) as 1 | 2 | 3)}>Back</button>
              : <div />
            }
            {step < 3
              ? (
                <button
                  className={`btn-primary ${(step === 1 ? !canProceed1 : !canProceed2) ? 'opacity-40 pointer-events-none' : ''}`}
                  onClick={() => setStep(s => (s + 1) as 1 | 2 | 3)}
                >
                  Continue
                </button>
              )
              : (
                <button className="btn-primary" onClick={handleSubmit}>
                  Submit for Evaluation →
                </button>
              )
            }
          </div>
        )}
      </div>
    </div>
  )
}

export default NewEvaluation
