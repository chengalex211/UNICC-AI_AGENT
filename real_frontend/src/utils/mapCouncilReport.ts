import type { CouncilReportResponse } from '../api/client'
import type { DetailedEvaluation, ExpertReport, Recommendation, Consensus } from '../data/mockData'

const toRecommendation = (v: unknown): Recommendation => {
  const s = String(v ?? '').toUpperCase()
  if (s === 'APPROVE' || s === 'PASS') return 'APPROVE'
  if (s === 'REJECT' || s === 'FAIL') return 'REJECT'
  return 'REVIEW'
}

const toConsensus = (v: unknown): Consensus => {
  const s = String(v ?? '').toUpperCase()
  if (s === 'FULL') return 'FULL'
  if (s === 'PARTIAL') return 'PARTIAL'
  return 'NONE'
}

const titleCase = (k: string) =>
  k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

const scoreEntries = (r: any): { label: string; value: number; max: number }[] => {
  const ds = r?.dimension_scores
  if (ds && typeof ds === 'object') {
    return Object.entries(ds).slice(0, 8).map(([k, v]) => ({
      label: titleCase(k),
      value: Number(v) || 0,
      max: 5,
    }))
  }
  const h = r?.council_handoff
  if (h && typeof h === 'object') {
    return ['privacy_score', 'transparency_score', 'bias_score'].map((k) => ({
      label: titleCase(k),
      value: Number(h[k]) || 0,
      max: 5,
    }))
  }
  return [
    { label: 'Overall', value: 3, max: 5 },
  ]
}

const extractFindings = (r: any): string[] => {
  if (Array.isArray(r?.key_findings) && r.key_findings.length) {
    return r.key_findings.map((x: unknown) => String(x))
  }
  if (Array.isArray(r?.key_gaps) && r.key_gaps.length) {
    return r.key_gaps.slice(0, 8).map((g: any) => String(g?.gap ?? g?.description ?? JSON.stringify(g)))
  }
  if (typeof r?.recommendation_rationale === 'string' && r.recommendation_rationale.trim()) {
    return [r.recommendation_rationale]
  }
  return ['No detailed findings returned.']
}

const extractRefs = (r: any): string[] => {
  if (Array.isArray(r?.framework_refs) && r.framework_refs.length) return r.framework_refs
  if (Array.isArray(r?.regulatory_citations) && r.regulatory_citations.length) return r.regulatory_citations
  if (Array.isArray(r?.evidence_references) && r.evidence_references.length) return r.evidence_references
  return ['No citation provided']
}

export function councilReportToDetailedEvaluation(report: CouncilReportResponse): DetailedEvaluation {
  const raw = report.expert_reports ?? {}
  const security = raw.security ?? {}
  const governance = raw.governance ?? {}
  const mission = raw.un_mission_fit ?? {}

  const expertReports: ExpertReport[] = [
    {
      id: 'security',
      title: 'Security & Adversarial Robustness',
      shortTitle: 'Security',
      icon: '🛡',
      recommendation: toRecommendation(security.recommendation),
      scores: scoreEntries(security),
      findings: extractFindings(security),
      framework_refs: extractRefs(security),
      elapsed: Number(security.elapsed_seconds ?? 0),
    },
    {
      id: 'governance',
      title: 'Governance & Regulatory Compliance',
      shortTitle: 'Governance',
      icon: '⚖️',
      recommendation: toRecommendation(governance.recommendation ?? governance.overall_compliance),
      scores: scoreEntries(governance),
      findings: extractFindings(governance),
      framework_refs: extractRefs(governance),
      elapsed: Number(governance.elapsed_seconds ?? 0),
    },
    {
      id: 'un_mission',
      title: 'UN Mission Fit & Human Rights',
      shortTitle: 'UN Mission',
      icon: '🌐',
      recommendation: toRecommendation(mission.recommendation),
      scores: scoreEntries(mission),
      findings: extractFindings(mission),
      framework_refs: extractRefs(mission),
      elapsed: Number(mission.elapsed_seconds ?? 0),
    },
  ]

  const critiques = Object.values(report.critiques ?? {}).map((c: any) => ({
    from: String(c?.from_expert ?? 'Unknown Expert'),
    on: String(c?.on_expert ?? 'Unknown Expert'),
    agrees: Boolean(c?.agrees),
    divergence_type: String(c?.divergence_type ?? 'framework_difference'),
    key_point: String(c?.key_point ?? ''),
    stance: String(c?.stance ?? c?.new_information ?? ''),
    evidence: (Array.isArray(c?.evidence_references) ? c.evidence_references : []).map((x: unknown) => String(x)),
  }))

  const decision = report.council_decision ?? {}
  const disagreements = Array.isArray(decision.disagreements) ? decision.disagreements : []

  return {
    agent_id: report.agent_id,
    system_name: report.system_name || report.agent_id,
    category: 'Submitted System',
    submitted_at: report.timestamp,
    description: report.system_description || 'No system description returned by backend.',
    decision: toRecommendation(decision.final_recommendation),
    consensus: toConsensus(decision.consensus_level),
    expert_reports: expertReports,
    council_critiques: critiques,
    final_rationale: String(decision.rationale ?? report.council_note ?? ''),
    key_conditions: disagreements.map((d: any) => String(d?.description ?? '')).filter(Boolean),
  }
}

