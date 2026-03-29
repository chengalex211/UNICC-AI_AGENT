import { type FC } from 'react'
import type { Recommendation, Consensus } from '../data/mockData'

export const RecBadge: FC<{ rec: Recommendation; size?: 'sm' | 'md' }> = ({ rec, size = 'md' }) => {
  const map = {
    APPROVE: { cls: 'badge-approve', dot: 'bg-apple-green', label: 'Approve' },
    REVIEW:  { cls: 'badge-review',  dot: 'bg-apple-orange', label: 'Review' },
    REJECT:  { cls: 'badge-reject',  dot: 'bg-apple-red',    label: 'Reject' },
  }
  const { cls, dot, label } = map[rec]
  return (
    <span className={`${cls} ${size === 'sm' ? 'text-[11px] px-2 py-0.5' : ''}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      {label}
    </span>
  )
}

export const ConsensusBadge: FC<{ consensus: Consensus }> = ({ consensus }) => {
  const map = {
    FULL:    { bg: 'bg-blue-50 text-apple-blue border border-blue-100', label: 'Full Consensus' },
    PARTIAL: { bg: 'bg-apple-orange-bg text-apple-orange border border-orange-100', label: 'Partial' },
    NONE:    { bg: 'bg-apple-red-bg text-apple-red border border-red-100', label: 'No Consensus' },
  }
  const { bg, label } = map[consensus]
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${bg}`}>
      {label}
    </span>
  )
}
