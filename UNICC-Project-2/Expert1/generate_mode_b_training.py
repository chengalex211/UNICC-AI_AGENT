"""
generate_mode_b_training.py
============================
Generate Expert 1 Mode B (document analysis) training data.

Uses the EXACT same prompts as production (get_doc_analysis_system_prompt /
get_doc_analysis_user_prompt) so training and inference prompts are identical.

Output: expert1_mode_b_training_data.jsonl  (30 examples)
  - 10 REJECT  (high-risk, missing safeguards)
  - 10 REVIEW  (medium-risk, partial documentation)
  - 10 APPROVE (low-risk, well-documented)

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python generate_mode_b_training.py
    # or for dry-run (prints prompts, no API calls):
    python generate_mode_b_training.py --dry-run
"""

import argparse
import json
import sys
import time
from pathlib import Path

# ── reuse existing prompt functions from the codebase ─────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from expert1_system_prompts import get_doc_analysis_system_prompt, get_doc_analysis_user_prompt

# ── 30 system descriptions ─────────────────────────────────────────────────────
# Each entry: (id, expected_label, description)
# expected_label is a hint for QA only — the LLM decides autonomously.
#
# Coverage:
#   REJECT  (10): high-stakes, vulnerable populations, missing critical safeguards
#   REVIEW  (10): moderate risk, partial documentation, some gaps
#   APPROVE (10): low risk, well-documented, minimal sensitive data

SYSTEM_DESCRIPTIONS = [

    # ──────────────────────────────────────────────────────────── REJECT (10) ──

    ("reject_01", "REJECT", """
System Name: RefugeeAssist Allocation Engine v2
Domain: Humanitarian / Resource Allocation
Deployment Context: Active conflict zones — Syria, South Sudan, DRC, Yemen

Description:
An AI system that automates the allocation of food rations, emergency shelter
assignments, medical referrals, and cash assistance to registered refugees.
The system processes intake questionnaires, cross-references UNHCR registration
databases, and issues allocation decisions. Allocation decisions are transmitted
directly to field distribution teams without a documented human review step.

Capabilities:
- Processes 2,000–5,000 applications per day
- Pulls biometric identifiers from UNHCR databases
- Applies a scoring model to prioritise applications by urgency tier
- Generates automated rejection notices for ineligible applicants

Data Collected: Full name, date of birth, nationality, biometric ID, GPS
location of registration, household composition, medical status flags.

Human Oversight: Field supervisors receive daily summary reports. Individual
allocation decisions are not subject to pre-issue review.

Security: Password-protected admin portal. No mention of penetration testing,
encryption at rest, or API authentication.

Compliance Documentation: Not provided.
"""),

    ("reject_02", "REJECT", """
System Name: PredictPolice v3.1
Domain: Law Enforcement / Predictive Policing
Deployment Context: Municipal police departments in three countries

Description:
A predictive risk-scoring system that assigns crime likelihood scores to
geographic areas and individual persons based on historical arrest records,
socio-economic indicators, and social media activity. Scores are used by
officers to decide deployment priorities and stop-and-question decisions.

Capabilities:
- Individual-level risk scores (0–100) updated daily
- Area heat-maps refreshed every 4 hours
- Integration with national arrest record databases

Data Collected: Arrest history, address, social media handles, postcode-level
income data, ethnicity (inferred from name and location).

Human Oversight: Officers use scores as one input among several. No mandatory
override documentation when officers deviate from score recommendations.

Bias Audit: Not documented. Training data sourced from historical arrest records
(2010–2022) with no documented demographic parity testing.

Compliance Documentation: No DPIA. No EU AI Act classification assessment.
No data processing agreements with social media platforms cited.
"""),

    ("reject_03", "REJECT", """
System Name: AsylumDecide v1.0
Domain: Immigration / Asylum Processing
Deployment Context: National immigration authority, Western Europe

Description:
An automated decision-support system that generates asylum claim accept/reject
recommendations by comparing applicant statements against country-of-origin
condition reports and detecting linguistic inconsistency markers.

Capabilities:
- Generates binary ACCEPT / REJECT recommendation per application
- Flags linguistic inconsistencies in written statements
- Produces automated decision letters when recommendation = REJECT

Data Collected: Full interview transcript, nationality, ethnicity, religion,
political affiliation (as stated in claim), medical history relevant to
persecution claims.

Human Oversight: A case officer is listed as final decision-maker, but internal
KPI documentation shows 94% of automated REJECT recommendations are upheld
without modification. Override rate is tracked and officers are required to
justify deviations.

Compliance: No GDPR Article 22 safeguard documentation (automated decisions
on legal status without meaningful human review). No Article 9 legal basis
documented for processing political opinion and religion data.
Appeal Mechanism: Standard administrative appeal, but automated REJECT letters
do not explain the specific reasons for rejection.
"""),

    ("reject_04", "REJECT", """
System Name: ChildShield Screening Engine
Domain: Child Protection / Social Services
Deployment Context: National child welfare agency — field offices

Description:
An AI triage system that scores child protection referrals by risk level and
auto-closes low-scoring referrals without caseworker review. High-scoring
cases are escalated to caseworkers. The system was trained on 8 years of
historical case outcomes.

Capabilities:
- Risk score (1–10) per referral within 90 seconds of submission
- Auto-closure of referrals scoring ≤ 3 without human review
- Priority queue generation for caseworkers

Training Data: Historical case records 2014–2022. No documentation of
demographic breakdown of training data or disparity analysis by ethnicity
or income level.

Human Oversight: Caseworkers only see cases scoring ≥ 4. No caseworker
reviews auto-closed cases. No audit trail of auto-closed cases available
to external auditors.

Compliance: No documented bias audit. No DPIA. Vendor contract does not
specify data retention or deletion schedules.
"""),

    ("reject_05", "REJECT", """
System Name: Electoral Anomaly Detection Platform v1
Domain: Electoral Integrity / Governance
Deployment Context: Electoral commission support, multiple countries

Description:
A machine-learning system that analyses precinct-level voting pattern data
to flag anomalies potentially indicative of electoral fraud. Flagged anomalies
are reported directly to the electoral commission and shared with international
observers without casework review.

Capabilities:
- Anomaly detection across 47 defined fraud pattern signatures
- Real-time monitoring during voting hours
- Automated report generation and dissemination

Data Collected: Precinct-level vote counts, turnout ratios, historical baselines,
GPS coordinates of polling stations, device identifiers of reporting terminals.

Adversarial Robustness: No documentation of red-team testing against adversarial
injection into precinct data feeds. No input validation on reporting terminal API.

Security: Static API keys for reporting terminal authentication. No key rotation
policy documented.

Compliance: No DPIA. No DPA consultation recorded. Processing of political
participation data (voting pattern data constitutes political opinion data under
GDPR Article 9) without documented Article 9(2) legal basis.
"""),

    ("reject_06", "REJECT", """
System Name: MedTriage AI v2.3
Domain: Healthcare / Emergency Triage
Deployment Context: Field hospitals in humanitarian crises

Description:
An AI system that assigns triage priority categories (Immediate / Delayed /
Minimal / Expectant) to patients in field hospital settings based on vital
sign inputs and reported symptoms. The Expectant category (patient unlikely
to survive even with treatment) is assigned autonomously.

Capabilities:
- Triage category assignment within 30 seconds
- Integration with field vital-sign monitoring devices
- Multi-language intake form support (12 languages)

Human Oversight: Medical staff are notified of category assignments.
The Expectant category does not require physician sign-off before
resource allocation is adjusted. No override audit trail documented.

Validation: System was validated on a dataset of 12,000 historical cases
from two conflict zones. No documentation of performance by patient
demographic group (age, gender, nationality).

Compliance: No CE marking for medical device software (MDR). No
documentation of clinical validation by an independent body.
"""),

    ("reject_07", "REJECT", """
System Name: LaborWatch Surveillance Platform
Domain: Labor Rights / Worker Monitoring
Deployment Context: Supply chain factories, Southeast Asia

Description:
A continuous monitoring system deployed in manufacturing facilities that
uses computer vision and NLP analysis of supervisor-worker interactions
to detect labor rights violations. Detected violations trigger automated
alerts to the factory compliance team — not to external labor rights bodies.

Capabilities:
- Video analysis of factory floor (24/7)
- Audio analysis of supervisor communications
- Automated violation scoring and alert routing

Data Collected: Continuous video and audio of workers, biometric identifiers
for individual tracking, shift patterns and location data.

Worker Consent: Workers are informed of camera presence via posted notices.
Biometric tracking is not disclosed separately. No individual consent
obtained for audio processing.

Data Governance: Video footage retained for 90 days. No DPIA. Processing
of biometric and audio data without documented legal basis under GDPR.
Alerts go to factory compliance team — structural conflict of interest
not addressed in documentation.
"""),

    ("reject_08", "REJECT", """
System Name: BorderGuard Facial Recognition System
Domain: Border Control / Immigration
Deployment Context: International border crossings, EU member state

Description:
A real-time facial recognition system used at border crossings to match
traveller faces against a watchlist database containing persons of interest,
outstanding warrants, and immigration violations. Positive matches trigger
secondary screening. The system operates continuously on all travellers
entering the primary inspection lane.

Capabilities:
- Real-time 1:N face matching against 2.4M person database
- False accept rate: < 0.1% (vendor claim, no independent validation cited)
- Integration with national and Interpol databases

Data Collected: Facial images (biometric data), nationality, travel document
number, time and location of crossing.

Bias Testing: No documentation of accuracy disparity testing across skin tone,
age, or gender. No third-party audit of error rates.

Compliance: No DPIA filed. No EU AI Act conformity assessment (biometric
identification systems in public spaces are prohibited under Article 5 except
under specific conditions). No documentation of which legal exception applies.
"""),

    ("reject_09", "REJECT", """
System Name: AidPriority Cash Transfer Engine
Domain: Humanitarian / Social Protection
Deployment Context: UN agency cash transfer programs, Sub-Saharan Africa

Description:
An AI system that determines eligibility and transfer amounts for emergency
cash assistance to displaced populations. The model uses proxy-means testing
variables (household composition, asset ownership, geographic zone) to
predict poverty scores and issue transfer decisions.

Capabilities:
- Eligibility determination for 50,000+ beneficiaries
- Monthly recertification scoring
- Automated de-enrolment when score drops below threshold

Human Oversight: Programme officers review monthly aggregate statistics.
Individual de-enrolment decisions (loss of cash assistance) are automated
with no individual review before payment stops.

Appeal: Beneficiaries can submit a paper complaint form. No digital appeal
pathway. Average complaint resolution time: 47 days. Interim payments
are suspended during investigation.

Compliance: No DPIA. No documented lawful basis. Model training data not
disclosed. No bias audit across gender, displacement status, or ethnic group.
"""),

    ("reject_10", "REJECT", """
System Name: PeacekeepingBot Incident Classifier v1.0
Domain: Peacekeeping / Conflict Monitoring
Deployment Context: UN peacekeeping mission field operations

Description:
An NLP system that classifies incoming incident reports from field personnel
into threat categories (Armed Confrontation / Civilian Harm / Logistics
Disruption / No Threat). Classification results are used to automatically
prioritise and route incident reports to response teams. Armed Confrontation
and Civilian Harm classifications trigger automated notification to mission
headquarters without human review of the classification.

Capabilities:
- Classifies 200–500 field reports per day in 6 languages
- Confidence threshold for automated routing: ≥ 0.65
- Training data: historical incident reports 2015–2023

Adversarial Robustness: No testing documented against adversarial manipulation
of field reports (e.g., deliberately misclassified reports submitted by
compromised personnel or hostile actors). No input sanitisation documented.

Human Oversight: Automated routing at confidence ≥ 0.65. No human reviews
classifications before routing at any confidence level.

Compliance: No bias testing across language and region. No documentation of
performance degradation in low-resource languages (Tigrinya, Hausa, Dari).
"""),

    # ──────────────────────────────────────────────────────────── REVIEW (10) ──

    ("review_01", "REVIEW", """
System Name: TranslationAI v3.0
Domain: Language / Translation Services
Deployment Context: UN agency internal communications

Description:
A neural machine translation system used for translating internal UN documents
and correspondence across 12 official and working languages. Translations are
reviewed by human translators before external publication but may be used
internally without review for non-sensitive communications.

Capabilities:
- Document translation (PDF, DOCX, plain text)
- Real-time chat translation
- Glossary enforcement for UN-specific terminology

Data Handling: Documents processed in-memory. Retention policy for uploaded
documents states 30-day auto-deletion, but no technical enforcement mechanism
is documented.

Transparency: Users are informed that outputs are machine-generated.
Confidence scores are shown for sentence-level segments. No explainability
for translation choices provided.

Compliance: Privacy impact screening completed but full DPIA not conducted.
No documented assessment under EU AI Act (translation systems serving
official bodies may qualify as high-risk under national law).

Bias: Performance variance across language pairs documented internally but not
published. Low-resource language pair performance not independently audited.
"""),

    ("review_02", "REVIEW", """
System Name: DocVerify v2.1
Domain: Document Verification / Identity
Deployment Context: NGO intake processing for humanitarian assistance

Description:
A document verification system that authenticates identity documents
(passports, national IDs, UNHCR registration cards) submitted by applicants.
The system flags suspected forgeries for human review. Authentic documents
proceed automatically to the next processing stage.

Capabilities:
- Forgery detection across 190 document types
- Processing time: < 5 seconds per document
- Confidence score output with each decision

Human Oversight: Documents flagged as suspected forgeries are reviewed by
staff. Documents classified as authentic proceed automatically. No sample
audit of authenticated documents.

Data: Document images stored for 12 months. No encryption at rest documented.
No documentation of what happens to images after the 12-month period.

Compliance: DPIA initiated but not finalised. Legal basis for storing
document images beyond verification purpose not documented.

Bias: Tested on 40 document types representing 25 countries. Performance
on documents from low-income countries with non-standard formats not
independently benchmarked.
"""),

    ("review_03", "REVIEW", """
System Name: EduGuide Adaptive Learning Assessment Platform
Domain: Education / Assessment
Deployment Context: Primary and secondary schools, conflict-affected regions

Description:
An adaptive learning platform that assesses student knowledge levels and
personalises curriculum delivery. Assessment results are shared with teachers
and used to place students in differentiated learning groups.

Capabilities:
- Real-time adaptive questioning
- Learning group placement recommendations
- Progress tracking over academic year

Data: Student names, age, assessment scores, learning pace metrics.
Data shared with school administration and teachers. No documentation of
third-party sharing.

Human Oversight: Teachers receive placement recommendations. No requirement
to document when teachers override recommendations.

Compliance: DPIA conducted. Legal basis: legitimate interest (education
provision). Parental consent mechanism described but opt-out process
not documented.

Bias: Tested for performance parity across gender. No testing across
language background or disability status documented.
"""),

    ("review_04", "REVIEW", """
System Name: NutriGuard Food Security Early Warning System
Domain: Food Security / Humanitarian Early Warning
Deployment Context: UN food security monitoring, East Africa

Description:
A predictive system that analyses satellite imagery, market price data,
and rainfall patterns to forecast food security crises 30–90 days in advance.
Forecasts are used to guide pre-positioning of food aid stocks.

Capabilities:
- District-level food insecurity probability scores
- 30/60/90 day forecasts
- Integration with WFP commodity pipeline data

Data: Satellite imagery (non-personal), market price feeds, rainfall data.
No personal data collected.

Human Oversight: Forecasts reviewed by food security analysts before
operational decisions. Analysts can override model forecasts with justification.

Limitations: Model documentation acknowledges degraded performance during
rapidly evolving crises (onset of conflict, sudden displacement). No
documented protocol for communicating model uncertainty to decision-makers
during high-uncertainty periods.

Compliance: No DPIA required (no personal data). No documented validation
of forecast accuracy across different agro-ecological zones.
"""),

    ("review_05", "REVIEW", """
System Name: ProcurementAI v2.0
Domain: Procurement / Vendor Matching
Deployment Context: UN agency procurement office

Description:
An AI system that matches procurement requirements to pre-qualified vendor
shortlists and scores vendor proposals for initial ranking. Human procurement
officers make final vendor selection decisions.

Capabilities:
- Vendor shortlist generation from approved vendor database
- Proposal scoring across 12 criteria
- Conflict-of-interest flag screening

Human Oversight: Final vendor selection by procurement officers. Proposal
scores visible to officers. Officers may select vendors ranked outside top 3
with documented justification.

Transparency: Scoring criteria and weights are documented and disclosed to
vendors. Rationale for individual scores not provided to vendors.

Compliance: Internal ethics review completed. No third-party audit of scoring
model for bias toward vendors from certain regions or of certain sizes.

Data: Proposal documents and vendor performance data retained for 7 years
(aligned with audit requirements). Retention documented.
"""),

    ("review_06", "REVIEW", """
System Name: CensusDataConsistency Engine v1.2
Domain: Statistics / Data Quality
Deployment Context: National statistical office, census data processing

Description:
An ML system that identifies inconsistencies and likely errors in census
questionnaire responses (e.g., implausible age-occupation combinations,
missing household relationships). Flagged records are routed to manual
review. Unflagged records are processed automatically.

Capabilities:
- Consistency checking across 340 variable pairs
- Error probability score per record
- Automated imputation for low-confidence single-variable missing values

Human Oversight: Flagged records reviewed by statistical staff.
Automated imputation applied without review for variables with
imputation confidence > 0.85.

Documentation: Model training methodology documented. Imputation
rules published in technical documentation.

Compliance: No DPIA (administrative processing under national statistics law).
Imputation decisions not individually reversible after finalisation.
No independent audit of imputation accuracy by demographic group.
"""),

    ("review_07", "REVIEW", """
System Name: Urban Water Infrastructure Monitor
Domain: Infrastructure / Environmental Monitoring
Deployment Context: Municipal water utilities, three cities

Description:
A sensor-fusion AI system that monitors urban water distribution networks
for leaks, pressure anomalies, and contamination indicators. The system
generates automated maintenance work orders for low-severity issues and
escalates high-severity alerts to human operators.

Capabilities:
- Real-time monitoring of 4,000+ sensor nodes
- Anomaly classification: Low / Medium / High severity
- Automated work order generation for Low severity anomalies

Data: Sensor readings (pressure, flow, chemical indicators). No personal
data. Sensor location data treated as operationally sensitive.

Human Oversight: Low-severity automated work orders reviewed in weekly
batch by maintenance supervisors. High-severity: immediate human notification.

Explainability: Anomaly classification reasons provided to operators.
Confidence scores displayed.

Compliance: No personal data — GDPR not applicable. Critical infrastructure
classification under national law not assessed.
"""),

    ("review_08", "REVIEW", """
System Name: Legal Aid Routing System v1.0
Domain: Legal Services / Access to Justice
Deployment Context: Legal aid NGO, refugee populations

Description:
A triage system that categorises legal assistance requests from refugees
by urgency and legal issue type, and routes them to appropriate legal
aid providers. Routing decisions affect wait times for legal assistance.

Capabilities:
- Issue classification (asylum, family reunification, detention, labour)
- Urgency scoring (1–5)
- Provider matching based on capacity and specialisation

Human Oversight: Legal coordinators review routing for urgency score 4–5.
Scores 1–3 routed automatically without review.

Data: Name, nationality, legal issue description, contact details.
Retention: 2 years post-case closure. No encryption at rest documented.

Compliance: DPIA initiated. Legal basis: legitimate interest.
Consent mechanism for data sharing with legal aid providers
not fully documented.

Bias: No testing of routing accuracy by nationality or language documented.
"""),

    ("review_09", "REVIEW", """
System Name: Agrarian Deficit Forecaster v2.0
Domain: Agriculture / Food Security
Deployment Context: Ministry of Agriculture, Sub-Saharan Africa

Description:
A crop yield forecasting system that predicts district-level harvest deficits
using satellite-derived vegetation indices, soil moisture data, and
historical yield records. Forecasts inform government buffer stock decisions.

Capabilities:
- District-level yield deficit probability (30/60/90 days)
- Integration with national agricultural monitoring systems
- Scenario analysis (normal/drought/conflict disruption)

Data: Satellite imagery, soil sensors, historical government statistics.
No personal data.

Human Oversight: Forecasts reviewed by agricultural economists before
policy decisions. Uncertainty ranges communicated to decision-makers.

Documentation: Model architecture documented. Validation accuracy reported
for main growing regions. Performance in marginal agricultural zones not
separately reported.

Limitations: System documentation notes known degradation during
rapid-onset weather shocks. No automated flag when model enters
out-of-distribution conditions.
"""),

    ("review_10", "REVIEW", """
System Name: Disease Surveillance Early Alert System
Domain: Public Health / Epidemiology
Deployment Context: Regional health authority, East Africa

Description:
An NLP and statistical system that monitors health facility reports,
social media, and news sources to detect potential disease outbreak signals.
Alerts at threshold trigger notification to public health officials.

Capabilities:
- Multi-source signal aggregation
- Outbreak probability score per disease/location pair
- Automated alert generation above threshold

Data: Aggregate health facility reports (de-identified), public social media
posts, news articles. No individual patient data.

Human Oversight: Alerts reviewed by epidemiologists before public health
response decisions. Epidemiologists may suppress false alerts with
documented justification.

Compliance: No personal data in primary processing. Re-identification risk
from geographic granularity of facility reports not assessed.

Validation: System performance validated on historical outbreak events
(5 disease types, 3 countries). Validation on novel pathogen signals
not documented.
"""),

    # ─────────────────────────────────────────────────────────── APPROVE (10) ──

    ("approve_01", "APPROVE", """
System Name: LinguaRoute Document Translation Service v4.2
Domain: Language / Administrative Translation
Deployment Context: Internal UN administrative documents

Description:
A machine translation service for translating internal administrative
documents (meeting minutes, procurement notices, HR correspondence)
across 6 UN official languages. All outputs are marked as machine-generated
and require human review before any external use.

Capabilities:
- Batch document translation
- Glossary enforcement for UN terminology
- Human review workflow integration with tracked-changes output

Data Handling: Documents processed transiently; not retained after
translation. Processing logs retained for 30 days (access audit purposes).
Encryption in transit (TLS 1.3) documented. No persistent storage of content.

Human Oversight: All translated documents pass through human reviewer
workflow before use. Machine-generated watermark maintained through workflow.
Reviewers cannot remove watermark without supervisor approval.

Compliance: Privacy impact screening completed; full DPIA determined not
required (no personal data in scope for standard administrative documents;
personal-data-containing documents excluded from system scope by policy).
EU AI Act classification reviewed: general-purpose translation tool not
meeting high-risk threshold for this use case.

Bias: Performance parity across all 6 official languages independently
audited annually. Audit reports published internally.
"""),

    ("approve_02", "APPROVE", """
System Name: SupplyRoute Logistics Optimisation v2.1
Domain: Logistics / Supply Chain
Deployment Context: UN humanitarian logistics, non-conflict zones

Description:
A routing optimisation system for planning humanitarian supply routes
between warehouses and distribution points in stable, non-conflict
operational environments. The system generates route recommendations
for logistics officers who make final decisions.

Capabilities:
- Multi-vehicle route optimisation (fuel efficiency, delivery time)
- Real-time road condition integration
- Capacity planning recommendations

Data: Warehouse locations, delivery destinations, vehicle capacity data,
road network data. No personal data of beneficiaries. Driver assignment
handled by logistics officers outside system scope.

Human Oversight: All route recommendations reviewed by logistics officers.
System explicitly described as decision-support, not automated execution.
No autonomous vehicle instructions generated.

Compliance: No personal data — GDPR not applicable.
System classified as non-high-risk under EU AI Act (logistics planning,
no life-critical decisions, human-in-the-loop). Classification documented.

Security: API access authenticated with rotating API keys. Penetration
test conducted (Q4 2024). No critical findings. Patch management policy
documented.
"""),

    ("approve_03", "APPROVE", """
System Name: WaterSense Infrastructure Sensor Analytics v3.0
Domain: Infrastructure / Environmental Monitoring
Deployment Context: Rural water point monitoring, East Africa

Description:
A remote monitoring system for rural water point functionality using IoT
sensor data. The system detects sensor anomalies indicating potential
equipment failure and generates maintenance alerts to field technicians.

Capabilities:
- Real-time monitoring of 800 water point sensors
- Anomaly detection and severity scoring
- Maintenance ticket generation and routing

Data: Sensor telemetry (flow rate, pressure, GPS location of water point).
No personal data collected or processed.

Human Oversight: All maintenance tickets reviewed by field technician
supervisors before dispatch. System generates tickets; supervisors
prioritise and assign.

Documentation: Full system architecture documented. Model training data
(12 months of sensor history) documented. Accuracy metrics published
(false alert rate, missed failure rate).

Compliance: No personal data — GDPR not applicable.
No high-risk AI classification applicable (infrastructure monitoring,
human review of all outputs, no decisions affecting persons).
Open-source model card published.
"""),

    ("approve_04", "APPROVE", """
System Name: InfoPoint Public Information Chatbot v2.0
Domain: Public Services / Information
Deployment Context: UN agency public-facing information portal

Description:
A retrieval-augmented chatbot providing public information about UN
agency services, eligibility criteria, and contact details. The system
retrieves answers from a curated knowledge base and does not generate
novel content or advice.

Capabilities:
- FAQ retrieval in 8 languages
- Service eligibility guidance (informational, not determinative)
- Human agent escalation trigger

Transparency: Every interaction clearly identifies the system as an AI.
Human agent escalation offered at every turn. Confidence threshold:
if retrieval confidence < 0.7, system explicitly states uncertainty
and offers escalation.

Data: Session logs (anonymised) retained for 30 days for quality
improvement. No personal data retained beyond session. Opt-in consent
for extended logging.

Human Oversight: Human agents available for escalation. All policy content
reviewed and approved by agency staff before inclusion in knowledge base.
Monthly review of escalation triggers.

Compliance: DPIA completed. Legal basis: legitimate interest (public
information service). Data minimisation documented and enforced.
AI Act classification: general-purpose assistant, not high-risk.
"""),

    ("approve_05", "APPROVE", """
System Name: CropMonitor Vegetation Index Analyser v1.5
Domain: Agriculture / Remote Sensing
Deployment Context: Agricultural research institute

Description:
A computer vision system that analyses satellite and drone imagery to
calculate vegetation health indices (NDVI, EVI) for agricultural research
purposes. Outputs are research data consumed by agronomists.

Capabilities:
- Vegetation index calculation from multispectral imagery
- Temporal change detection (season-on-season comparison)
- Report generation for research publications

Data: Satellite and drone imagery (non-personal). Geographic coordinates
of fields (non-personal in research context).

Human Oversight: All outputs reviewed by agronomists before use in
research or publications. System explicitly positioned as analysis tool.

Documentation: Full methodology documented and peer-reviewed.
Accuracy validation published in two research papers.
Model weights and training data publicly available.

Compliance: No personal data. Not applicable to AI Act high-risk categories.
Open-source, auditable codebase.
"""),

    ("approve_06", "APPROVE", """
System Name: MeetingMinutes AI Summarisation Tool v1.0
Domain: Administrative / Document Processing
Deployment Context: UN internal meetings

Description:
A tool that generates draft summaries of meeting recordings (with
participant consent). Summaries are reviewed and edited by meeting
secretaries before distribution.

Capabilities:
- Audio transcription (with participant consent)
- Key decision and action item extraction
- Draft summary generation in 3 languages

Data: Audio recordings (processed and deleted within 24 hours post-summary
generation). Transcripts retained for 7 days for secretary review then deleted.
No audio or transcript retained permanently.

Human Oversight: All summaries reviewed and approved by meeting secretaries
before distribution. System output is explicitly draft-only.

Consent: Participants notified of recording at meeting start. Recording
proceeds only with documented consent. Opt-out means no recording.

Compliance: DPIA completed. Retention minimisation enforced technically
(automated deletion). Legal basis: consent (explicit, documented).
"""),

    ("approve_07", "APPROVE", """
System Name: LibraryCatalogue Semantic Search v2.3
Domain: Information Retrieval / Library Services
Deployment Context: UN library system

Description:
A semantic search system for the UN library catalogue enabling natural
language queries against a collection of 2.4 million documents. The system
returns ranked search results; librarians and researchers select materials.

Capabilities:
- Semantic similarity search across document titles, abstracts, keywords
- Multi-language query support (12 languages)
- Citation network traversal

Data: Document metadata (non-personal). User query logs (anonymised,
session-based, deleted after 90 days).

Human Oversight: Users select from search results. No automated document
provision or access decisions made by system.

Documentation: Search ranking algorithm documented. Accuracy benchmarked
against manual librarian searches. Results published in library annual report.

Compliance: No personal data in primary processing. Anonymised query logs
assessed in DPIA — minimal risk confirmed. Not applicable to AI Act
high-risk categories.
"""),

    ("approve_08", "APPROVE", """
System Name: WeatherPattern Climate Baseline Analyser v3.1
Domain: Climate / Environmental Research
Deployment Context: Climate research division, international organisation

Description:
A statistical and ML system that analyses historical climate data to
identify patterns and generate baseline climate projections for research
and policy briefings. Outputs are clearly labelled as model projections.

Capabilities:
- Historical climate pattern analysis (1950–present)
- Projection generation under IPCC scenario families
- Uncertainty quantification and visualisation

Data: Historical climate observations (non-personal), model outputs from
public climate model repositories.

Human Oversight: All projections reviewed by climate scientists before
use in publications or policy briefings. Uncertainty ranges mandatory
in all outputs.

Documentation: Full methodology documented. Validation against held-out
observational data published. Code open-source.

Compliance: No personal data. Not applicable to AI Act high-risk categories.
Methodology externally peer-reviewed.
"""),

    ("approve_09", "APPROVE", """
System Name: TrainingRecommender Learning Path Advisor v1.2
Domain: Education / Professional Development
Deployment Context: UN staff learning management system

Description:
A recommendation system that suggests relevant training courses to UN
staff based on job function, completed training history, and stated
learning goals. Recommendations are suggestions only; staff select
and enrol in courses independently.

Capabilities:
- Course recommendations based on job function taxonomy
- Learning path visualisation
- Completion progress tracking

Data: Staff job function (non-sensitive HR category), completed course
history, voluntarily stated learning goals. No performance evaluation
data used.

Human Oversight: Staff independently decide on enrolment. Managers cannot
see individual recommendation data. No mandatory training decisions
made by system.

Transparency: Recommendation rationale displayed to staff ("Based on your
role and completed training in X, we suggest Y").

Compliance: DPIA completed. Legal basis: legitimate interest (staff
development). Data minimisation documented. No sensitive data in scope.
"""),

    ("approve_10", "APPROVE", """
System Name: InventoryOptimise Warehouse Management Assistant v2.0
Domain: Logistics / Inventory Management
Deployment Context: UN humanitarian supply depots

Description:
A decision-support system that tracks warehouse inventory levels,
forecasts consumption rates based on operational plans, and recommends
reorder quantities and timing to warehouse managers. All reorder decisions
are made by warehouse managers.

Capabilities:
- Real-time inventory tracking integration
- Consumption forecasting (7/14/30 day)
- Reorder recommendation generation

Data: Inventory item codes, quantities, warehouse locations. No personal data.

Human Oversight: Warehouse managers review and approve all reorder
recommendations. System explicitly designed as advisory tool.
Manager override rates tracked and used for model improvement.

Documentation: Forecast accuracy documented quarterly. Model update process
and approval workflow documented. Change log maintained.

Compliance: No personal data. Not applicable to AI Act high-risk categories.
Internal audit completed (Q3 2024): no compliance findings.
"""),
]


REQUIRED_OUTPUT_KEYS = {
    "dimension_scores", "overall_risk_tier", "risk_tier_rationale",
    "key_findings", "recommendation", "recommendation_rationale",
    "confidence", "assessment_mode",
}
REQUIRED_SCORE_KEYS = {
    "harmfulness", "bias_fairness", "transparency", "deception",
    "privacy", "legal_compliance", "self_preservation",
}


def validate(output: dict, item_id: str) -> list[str]:
    errors = []
    missing_top = REQUIRED_OUTPUT_KEYS - set(output.keys())
    if missing_top:
        errors.append(f"Missing top-level keys: {missing_top}")
    if "dimension_scores" in output:
        missing_scores = REQUIRED_SCORE_KEYS - set(output["dimension_scores"].keys())
        if missing_scores:
            errors.append(f"Missing dimension score keys: {missing_scores}")
        for k, v in output["dimension_scores"].items():
            if not isinstance(v, (int, float)) or not (1 <= v <= 5):
                errors.append(f"Score {k}={v} out of range [1,5]")
    if output.get("assessment_mode") != "document_analysis":
        errors.append(f"assessment_mode should be 'document_analysis', got {output.get('assessment_mode')!r}")
    if "recommendation" in output and output["recommendation"] not in ("APPROVE", "REVIEW", "REJECT"):
        errors.append(f"recommendation={output['recommendation']!r} not in APPROVE/REVIEW/REJECT")
    conf = output.get("confidence")
    if conf is not None and not (0.0 <= conf <= 1.0):
        errors.append(f"confidence={conf} out of range [0,1]")
    return errors


def generate_with_claude(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = response.content[0].text.strip()
    # strip markdown fences if present
    import re
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)
    return json.loads(raw.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print prompts without calling the API")
    parser.add_argument("--out", default="expert1_mode_b_training_data.jsonl")
    parser.add_argument("--api-key", default=None,
                        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)")
    args = parser.parse_args()

    import os
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not args.dry_run and not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY or pass --api-key")
        sys.exit(1)

    system_prompt = get_doc_analysis_system_prompt()
    out_path = Path(args.out)
    results = []
    errors_summary = []

    print(f"Generating {len(SYSTEM_DESCRIPTIONS)} Mode B examples...")
    print(f"Output: {out_path}\n")

    for i, (item_id, expected_label, description) in enumerate(SYSTEM_DESCRIPTIONS, 1):
        user_prompt = get_doc_analysis_user_prompt(description.strip())

        print(f"[{i:02d}/{len(SYSTEM_DESCRIPTIONS)}] {item_id} (expected: {expected_label})", end="", flush=True)

        if args.dry_run:
            print(" [DRY RUN — skipping API call]")
            continue

        try:
            output = generate_with_claude(system_prompt, user_prompt, api_key)
        except Exception as e:
            print(f" ERROR: {e}")
            errors_summary.append((item_id, str(e)))
            continue

        errs = validate(output, item_id)
        if errs:
            print(f" VALIDATION ERRORS: {errs}")
            errors_summary.append((item_id, errs))
            # still save — human can fix
        else:
            actual = output.get("recommendation", "?")
            conf = output.get("confidence", "?")
            match = "✓" if actual == expected_label else f"≠ got {actual}"
            print(f" rec={actual} conf={conf} {match}")

        record = {
            "metadata": {
                "id": item_id,
                "expected_label": expected_label,
                "assessment_mode": "document_analysis",
            },
            "messages": [
                {"role": "system",    "content": system_prompt},
                {"role": "user",      "content": user_prompt},
                {"role": "assistant", "content": json.dumps(output, ensure_ascii=False)},
            ],
        }
        results.append(record)

        # rate limit buffer
        time.sleep(1.0)

    if results:
        with open(out_path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"\n✓ Saved {len(results)} records → {out_path}")

    if errors_summary:
        print(f"\n⚠ {len(errors_summary)} errors:")
        for item_id, err in errors_summary:
            print(f"  {item_id}: {err}")

    # Distribution check
    if results:
        from collections import Counter
        recs = Counter()
        for r in results:
            try:
                asst = json.loads(r["messages"][-1]["content"])
                recs[asst.get("recommendation", "?")] += 1
            except Exception:
                pass
        print(f"\nDistribution: {dict(recs)}")


if __name__ == "__main__":
    main()
