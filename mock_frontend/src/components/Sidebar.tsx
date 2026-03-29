import { type FC } from 'react'

type Page = 'dashboard' | 'evaluate' | 'results' | 'council' | 'report'

interface Props {
  current: Page
  onChange: (p: Page) => void
}

const nav: { id: Page; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '⬡' },
  { id: 'evaluate', label: 'New Evaluation', icon: '＋' },
  { id: 'results', label: 'Expert Analysis', icon: '◈' },
  { id: 'council', label: 'Council Review', icon: '◉' },
  { id: 'report', label: 'Final Report', icon: '▦' },
]

const Sidebar: FC<Props> = ({ current, onChange }) => (
  <aside className="w-60 shrink-0 flex flex-col h-screen sticky top-0 bg-white border-r border-apple-gray-100">
    {/* Logo */}
    <div className="px-6 pt-8 pb-6">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-apple-blue flex items-center justify-center">
          <span className="text-white text-sm font-bold leading-none">U</span>
        </div>
        <div>
          <div className="text-sm font-bold text-apple-gray-900 leading-tight">UNICC</div>
          <div className="text-[10px] font-medium text-apple-gray-400 leading-tight tracking-wide uppercase">AI Safety Council</div>
        </div>
      </div>
    </div>

    {/* Nav */}
    <nav className="flex-1 px-3 space-y-0.5">
      <div className="section-label px-4 mb-4">Navigation</div>
      {nav.map(item => (
        <button
          key={item.id}
          onClick={() => onChange(item.id)}
          className={`nav-item w-full text-left ${current === item.id ? 'active' : ''}`}
        >
          <span className="text-base w-5 text-center">{item.icon}</span>
          <span>{item.label}</span>
        </button>
      ))}
    </nav>

    {/* Footer */}
    <div className="px-6 pb-6">
      <div className="p-3 rounded-apple bg-apple-gray-50 border border-apple-gray-100">
        <div className="flex items-center gap-2 mb-1">
          <span className="w-1.5 h-1.5 rounded-full bg-apple-green animate-pulse-dot" />
          <span className="text-xs font-semibold text-apple-gray-900">System Online</span>
        </div>
        <p className="text-[11px] text-apple-gray-400 leading-snug">3 Experts · 1 Council<br />44 evaluations completed</p>
      </div>
    </div>
  </aside>
)

export default Sidebar
