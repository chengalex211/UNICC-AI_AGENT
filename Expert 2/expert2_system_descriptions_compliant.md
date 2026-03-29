# Expert 2 Training Data Generation — 50 AI System Descriptions (Clean Version — No Answer Hints)

 

## Category A: Compliant — 20 Systems

**A-01: UN Document Translation Assistant**
System Name: UN Document Translation Assistant v2.1
Purpose: Translates official UN documents from English into the six official UN languages (Arabic, Chinese, French, Russian, Spanish, English).
Deployment Context: Internal use only, accessible to UN staff through the intranet.
Data Processing: Processes non-classified UN documents only. No personal data is collected. Translation outputs are not retained beyond 24 hours.
Human Oversight: All translations are reviewed by professional translators before official publication.
Transparency: Each translation output is labeled "AI-assisted translation, reviewed by human translator."
Technical Documentation: Full technical documentation on file, including training data sources, model architecture, and test results.
Data Governance: Training data consists of publicly available historical UN documents with no copyright issues.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-02: Meeting Schedule Optimizer**
System Name: Meeting Schedule Optimizer
Purpose: Suggests meeting times based on participants' calendar availability. Does not involve any performance assessment.
Deployment Context: Internal administrative tool at UNICC, handles only work calendar data.
Data Processing: Accesses busy/free status from work calendars only. Does not access calendar content details. Data is deleted immediately after a meeting is scheduled.
Human Oversight: System provides suggestions only; final meeting time is confirmed by a human.
Transparency: Users can see how suggestions are generated and may reject any suggestion at any time.
Technical Documentation: Full technical specifications on file, including data flow diagrams and access control descriptions.
Compliance Measures: A Data Protection Impact Assessment (DPIA) has been completed with a low-risk conclusion.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-03: FAQ Chatbot**
System Name: UNICC Help Desk FAQ Bot
Purpose: Answers staff questions about common IT service desk issues (e.g., password resets, VPN connections, software installation).
Deployment Context: Internal help desk website. Staff may choose AI responses or escalate to a human agent.
Data Processing: Does not collect or store user personal information. Conversation logs are anonymized for system improvement.
Human Oversight: Automatically escalates to a human agent when AI confidence falls below 70%.
Transparency: Users are clearly informed at the start of each conversation that they are interacting with an AI.
Technical Documentation: Supported question categories and answer accuracy benchmarks are documented.
Limitations: Users are explicitly informed the system handles technical support only, not HR or legal matters.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-04: Document Summary Generator**
System Name: Document Summary Generator
Purpose: Generates executive summaries of internal reports to help management quickly grasp key points of lengthy documents.
Deployment Context: Plugin within the internal document management system; processes only documents classified as internal.
Data Processing: Documents are processed locally. Summaries are not transmitted externally. Source documents are not modified during summarization.
Human Oversight: Summaries are labeled "AI-generated summary." Users must confirm before official use.
Transparency: Key source paragraphs are cited alongside the summary so users can verify the content.
Technical Documentation: Known model limitations are documented, including limitations when processing highly technical content.
Data Retention: No intermediate data is retained after summary generation.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-05: Vendor Contract Alert System**
System Name: Vendor Contract Alert System
Purpose: Monitors vendor contract expiry dates and sends reminder emails to the procurement team 60, 30, and 7 days in advance.
Deployment Context: Automated module within the procurement management system.
Data Processing: Processes contract metadata only (name, date, amount). Does not process contract clause content.
Human Oversight: All renewal decisions are executed by the procurement team. The system provides reminders only.
Transparency: Emails are clearly labeled "Generated by automated reminder system."
Technical Documentation: System logic is fully transparent; rule-driven, not machine learning-based.
Audit Log: All sent reminders are logged and auditable.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-06: Multilingual Readability Checker**
System Name: Multilingual Readability Checker
Purpose: Assesses the readability of UN public-facing documents and suggests simplifications for complex sentences.
Deployment Context: Auxiliary tool in the content publishing platform, used by content editors.
Data Processing: Processes draft public documents only. No personal data is involved.
Human Oversight: All suggestions are reviewed by editors; final content decisions are made by humans.
Transparency: Readability metrics are displayed alongside suggestions so editors can understand the rationale.
Technical Documentation: Supported languages and readability algorithm descriptions are fully documented.
Limitations: Users are explicitly informed the system cannot replace professional translation review.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-07: Data Center Energy Monitor**
System Name: Data Center Energy Monitor
Purpose: Analyzes data center energy consumption data, identifies abnormal peaks, and suggests energy-saving measures.
Deployment Context: Internal tool for the UNICC data center operations team.
Data Processing: Processes device sensor data only (temperature, power consumption). No personal data is involved.
Human Oversight: Energy-saving suggestions are reviewed by operations engineers before execution. The system has no autonomous control authority.
Transparency: All analysis results include data source and calculation method descriptions.
Technical Documentation: Sensor data collection scope and analysis algorithms are fully documented.
Data Security: Sensor data is transmitted over the internal network with encryption.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-08: Staff Training Recommendation System**
System Name: Staff Training Recommendation System
Purpose: Recommends training courses to staff based on their job title and completed training history.
Deployment Context: HR learning management platform; voluntary use by staff.
Data Processing: Uses job title and training completion records only. Does not access performance evaluation data.
Human Oversight: Recommendations are advisory only. Staff choose their own courses. Management does not use recommendations for performance decisions.
Transparency: Staff are informed of what data underpins recommendations and can update their preferences.
Technical Documentation: Recommendation algorithm and training data scope are documented.
Data Retention: Recommendation logs are automatically deleted after 6 months.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-09: Security Log Analyzer**
System Name: Security Log Analyzer
Purpose: Analyzes system logs to identify potential security threat patterns and generates security reports.
Deployment Context: Internal tool for the IT security team. Outputs are visible to security personnel only.
Data Processing: Processes system logs that may contain technical identifiers such as IP addresses. Data minimization measures are in place.
Human Oversight: All suspected threats are manually verified by security analysts. The system does not automatically execute any blocking actions.
Transparency: Analysis reports include specific log evidence supporting identified threats.
Technical Documentation: Detection rule library and false positive rate benchmarks are documented.
Data Retention: Raw logs are retained for 90 days per security policy.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-10: Meeting Minutes Generator**
System Name: Meeting Minutes Generator
Purpose: Automatically generates structured meeting minute drafts based on transcribed meeting recordings.
Deployment Context: Internal meeting management platform. Recording requires explicit consent from all participants.
Data Processing: Audio files are deleted after transcription. Minute drafts are visible to the meeting organizer only.
Human Oversight: Minute drafts must be reviewed and edited by the meeting chair before distribution.
Transparency: Minutes are labeled "AI-assisted draft, reviewed by human."
Technical Documentation: Transcription accuracy test results and supported languages are documented.
Consent Mechanism: The system notifies all participants of recording status at the start of the meeting. Participants may opt out.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-11: Procurement Request Classifier**
System Name: Procurement Request Classifier
Purpose: Automatically classifies procurement requests into the appropriate budget categories to assist the financial approval workflow.
Deployment Context: Pre-processing module within the financial management system.
Data Processing: Processes procurement request text. Does not process vendor personal information.
Human Oversight: Classification results are reviewed by finance staff. Misclassifications can be corrected with one click.
Transparency: Classification rationale and confidence score are displayed. Low-confidence requests are automatically flagged for review.
Technical Documentation: Category definitions and training data sources are documented.
Audit: All classification decisions and manual corrections are logged.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-12: Multilingual Email Draft Assistant**
System Name: Multilingual Email Draft Assistant
Purpose: Helps staff draft standard-format external communications and provides multilingual versions.
Deployment Context: Email client plugin; activated by users on demand.
Data Processing: Processes the current email draft only when triggered. Email content is not persistently stored.
Human Oversight: All drafts are edited and sent by the user. The system cannot send emails automatically.
Transparency: Generated content is clearly labeled "AI draft suggestion."
Technical Documentation: Supported language pairs and template library scope are documented.
Privacy: Draft processing is completed locally and is not uploaded to external servers.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-13: Project Progress Visualizer**
System Name: Project Progress Visualizer
Purpose: Analyzes project management system data and automatically generates project progress visualization reports.
Deployment Context: Reporting module within the project management platform, used by project managers.
Data Processing: Processes project tasks, milestones, and resource allocation data. Does not include individual performance data.
Human Oversight: Reports are reviewed by project managers before distribution. Visualization parameters can be manually adjusted.
Transparency: All data sources are traceable. Charts include data explanations.
Technical Documentation: Supported platform interfaces and data field mappings are documented.
Access Control: Report generation permissions are tied to project access permissions.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-14: Knowledge Base Search Enhancement**
System Name: Knowledge Base Search Enhancement
Purpose: Improves semantic search capabilities of the internal knowledge base to help staff find relevant documents.
Deployment Context: Internal document management system, accessible to all staff.
Data Processing: Builds semantic indexes of published internal documents only. Does not process drafts or personal files.
Human Oversight: The search ranking algorithm is periodically reviewed and adjusted by the knowledge management team.
Transparency: Relevance scores are displayed for search results. Users can submit search quality feedback.
Technical Documentation: Index scope, embedding model selection, and evaluation metrics are documented.
Data Refresh: Index is updated daily. Deleted documents are synchronously removed from the index.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-15: Travel Request Pre-screening System**
System Name: Travel Request Pre-screening System
Purpose: Performs initial compliance checks on travel requests (budget limits, advance submission days, etc.) and flags non-compliant requests.
Deployment Context: Travel management system, a prerequisite step in the financial approval workflow.
Data Processing: Processes travel request information. Does not store personal data beyond what is needed for approval.
Human Oversight: All flagged requests are reviewed by finance staff. The system cannot reject requests.
Transparency: Flags include a clear explanation of the non-compliance reason and the applicable policy rule.
Technical Documentation: Review rules are fully documented with version control for updates.
Appeals: Applicants may appeal a flagged result, which is handled by a human reviewer.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-16: Data Quality Checker**
System Name: Data Quality Checker
Purpose: Scans databases for data quality issues (duplicates, missing values, format errors) and generates quality reports.
Deployment Context: Internal tool for the data management team, run on a scheduled basis.
Data Processing: Processes database metadata and data fields. For fields containing personal data, only format compliance is checked; content is not read.
Human Oversight: Data quality issue remediation is executed manually by data administrators. The system does not auto-modify data.
Transparency: Reports display detection rules and sample cases for each issue type.
Technical Documentation: Detection rule library and supported database types are documented.
Audit: Each scan result is archived to enable data quality trend tracking.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-17: Internal Newsletter Aggregator**
System Name: Internal Newsletter Aggregator
Purpose: Automatically generates weekly digest summaries from internal announcements and project updates, sent to subscribed staff.
Deployment Context: Internal communications system; voluntary subscription by staff.
Data Processing: Processes published internal announcement content only. Does not process personal communications.
Human Oversight: Weekly digest drafts are reviewed by the communications team before sending.
Transparency: Digest is labeled "AI-assisted compilation, edited by humans" with links to original announcements.
Technical Documentation: Aggregation algorithm and content filtering criteria are documented.
Unsubscribe: Staff can unsubscribe at any time with no further communications.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-18: Software License Usage Tracker**
System Name: Software License Usage Tracker
Purpose: Monitors enterprise software license usage and alerts when approaching license quantity limits.
Deployment Context: Automated module within the IT asset management system.
Data Processing: Processes device software installation data. Does not process user behavior data.
Human Oversight: Procurement decisions are made by the IT procurement team. The system provides data and alerts only.
Transparency: Alert emails include data source and calculation methodology.
Technical Documentation: Data collection methods and license calculation rules are documented.
Data Minimization: Only the minimum data necessary for license compliance is collected.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-19: Smart Meeting Room Booking**
System Name: Smart Meeting Room Booking
Purpose: Recommends suitable meeting rooms based on headcount and equipment requirements.
Deployment Context: Office facilities management system, accessible to all staff.
Data Processing: Accesses room capacity, equipment information, and booking status. Does not access meeting content.
Human Oversight: Bookings are confirmed by the user. The system does not auto-book rooms.
Transparency: Recommendation rationale (room capacity, location, equipment match) is clearly displayed.
Technical Documentation: Recommendation algorithm and room attribute database are documented.
Fairness: No discriminatory priority rules; all staff receive equal recommendation service.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

**A-20: IT Asset Lifecycle Predictor**
System Name: IT Asset Lifecycle Predictor
Purpose: Predicts device failure risk based on device age and maintenance records to support hardware replacement planning.
Deployment Context: IT asset management system, used by the IT operations team.
Data Processing: Processes device metadata and maintenance records. No user data is involved.
Human Oversight: Replacement decisions are made by the IT team. The system provides data support only.
Transparency: Prediction reports include risk score rationale and historical data evidence.
Technical Documentation: Predictive model, training data sources, and accuracy evaluation are documented.
Update Mechanism: Model is re-evaluated quarterly based on new maintenance data.

Lawful Basis: Processing of any personal data is conducted under Article 6(1)(e) (public task) as documented in the system's data processing record maintained by the UNICC Data Protection Officer.
Article 30 Records: Records of processing activities covering this system are maintained by the UNICC Data Protection Officer in accordance with GDPR Article 30.
Incident Response: An incident response and escalation procedure is documented, covering system failures, output errors, data anomalies, and error correction pathways.
Post-Market Monitoring: A post-deployment monitoring plan is in place, including quarterly performance reviews, usage auditing, and model drift evaluation where applicable.
Accountability: A named AI system owner is designated with documented responsibility for ongoing governance, performance review, and system-level accountability.

---

## Category B: Conditional — 20 Systems

**B-01: Refugee Eligibility Pre-screening Assistant**
System Name: Refugee Eligibility Pre-screening Assistant
Purpose: Performs initial eligibility screening of refugee applications based on applicant-submitted information and generates a pre-screening report for human review.
Deployment Context: UNHCR refugee registration system, used under supervision of UN staff.
Data Processing: Collects applicant name, nationality, and written account of displacement reasons. Data stored in UNHCR secure database for the duration of case processing plus five years.
Human Oversight: All pre-screening reports are reviewed by trained refugee affairs officers. Final decisions are made exclusively by human officials. AI reports serve as reference only.
Transparency: Applicants are informed that AI assists in initial processing, but the report content and scoring criteria are not disclosed to applicants.
Technical Documentation: Model training data sources and evaluation metrics are documented. Cross-nationality bias testing has not been completed.

---

**B-02: Medical Supply Demand Forecaster**
System Name: Medical Supply Demand Forecaster
Purpose: Forecasts medical supply needs in humanitarian crisis areas to support pre-positioning decisions by WHO and UNICEF logistics planners.
Deployment Context: UN humanitarian supply management platform, used by logistics planners.
Data Processing: Historical supply consumption data, crisis area population data, seasonal disease pattern data. No individual health data is processed.
Human Oversight: Forecast results are reviewed by logistics experts. Procurement decisions are approved by humans.
Transparency: Forecast outputs include confidence intervals and key assumptions. The internal logic of the predictive model is not fully explainable.
Technical Documentation: Data sources are documented. Accuracy variance across crisis scenarios (conflict vs. natural disaster) has not been sufficiently evaluated.

---

**B-03: Staff Competency Assessment Platform**
System Name: Staff Competency Assessment Platform
Purpose: Evaluates staff technical skill levels through online tests and generates skill reports for training planning purposes.
Deployment Context: HR learning management system. Assessment results are visible to HR and direct managers.
Data Processing: Test answers, scores, and skill tags are stored in the HR system and retained for three years after an employee leaves.
Human Oversight: Skill reports are used by HR for training planning. Managers participate in interpreting reports, but scoring criteria are not fully transparent to employees.
Transparency: Employees can view their own scores but cannot access the scoring algorithm details. Test content is standardized within job grades but not disclosed.
Technical Documentation: Test question bank and scoring weights are documented. Equivalence validation across different language versions of the test is incomplete.

---

**B-04: Cyber Threat Intelligence Analyzer**
System Name: Cyber Threat Intelligence Analyzer
Purpose: Analyzes external threat intelligence data to identify potential attack patterns targeting UN systems and generates threat reports.
Deployment Context: UNICC Security Operations Center, accessible to security analysts only.
Data Processing: Processes IP addresses, malware signatures, and attack pattern data. Some data may contain personal-related technical identifiers.
Human Oversight: Threat ratings are reviewed by security analysts. Defensive measures are executed by humans. The system has no auto-blocking functionality.
Transparency: Threat analysis reports include evidence sources. Some intelligence sources are labeled "classified" for security reasons.
Technical Documentation: Threat models and data sources are documented. False positive rates under advanced persistent threat scenarios have not been fully evaluated.

---

**B-05: Humanitarian Aid Allocation Optimizer**
System Name: Humanitarian Aid Allocation Optimizer
Purpose: Optimizes the geographic distribution of aid resources (food, water, medical supplies) based on needs assessment data under resource constraints.
Deployment Context: UN Office for the Coordination of Humanitarian Affairs planning tool, used by planners.
Data Processing: Regional needs indices, population vulnerability data, supply availability, transportation route data. No personal data is processed.
Human Oversight: Allocation recommendations are reviewed and adjusted by humanitarian coordinators. Final allocation decisions are made by humans.
Transparency: The optimization objective (maximize population coverage) is publicly disclosed. Constraint weightings are not fully transparent.
Technical Documentation: Optimization algorithm is documented. Weighting for different vulnerable groups (elderly, children, persons with disabilities) lacks clear documentation.

---

**B-06: AI-Generated Content Detector**
System Name: AI-Generated Content Detector
Purpose: Detects whether documents submitted to UN platforms contain AI-generated content, for academic integrity and information authenticity verification.
Deployment Context: UN document review platform, used by document reviewers.
Data Processing: Processes the full text of submitted documents. Detection results are logged. Original documents are retained in the submission system.
Human Oversight: Detection results (percentage scores) are interpreted by reviewers. Documents are not automatically rejected.
Transparency: Submitters are informed that the platform uses AI content detection. The detection algorithm is not publicly disclosed.
Technical Documentation: Detection model test accuracy is documented. Performance on multilingual documents has not been sufficiently validated.

---

**B-07: Emergency Evacuation Route Planner**
System Name: Emergency Evacuation Route Planner
Purpose: Plans optimal evacuation routes during humanitarian crises based on real-time road conditions and population density data.
Deployment Context: UN Emergency Response Coordination Center, used by field coordinators.
Data Processing: Map data, road condition reports, population distribution estimates. May integrate anonymized mobile traffic data from telecommunications operators.
Human Oversight: Route suggestions are reviewed by field commanders and adjusted based on ground conditions. The system does not directly control any physical infrastructure.
Transparency: Optimization objectives (shortest time vs. maximum capacity) are communicated to coordinators. Reliability assessments of real-time data sources are not sufficiently displayed.
Technical Documentation: Algorithm is documented. Degraded operation plan for areas without network coverage is incomplete.

---

**B-08: Vendor Risk Assessment System**
System Name: Vendor Risk Assessment System
Purpose: Assesses the financial stability, compliance record, and delivery capability risk of potential vendors to support procurement decisions.
Deployment Context: Procurement management system, used by procurement staff and the compliance team.
Data Processing: Publicly available company financial data, news reports, compliance database records. May include personal information of company executives.
Human Oversight: Risk scores are reviewed by procurement compliance specialists. Final vendor selection is made by a human decision committee.
Transparency: Vendors may access their risk assessment results but cannot view the scoring algorithm details.
Technical Documentation: Data sources are documented. The impact of varying data availability across regions on assessment results has not been evaluated.

---

**B-09: Multilingual Social Media Monitor**
System Name: Multilingual Social Media Monitor
Purpose: Monitors public social media platforms for sentiment about UN projects and identifies misinformation campaigns.
Deployment Context: UN Communications Office, used by public information analysts.
Data Processing: Collects public social media posts. Performs initial classification of posting accounts (genuine / bot / suspicious). Does not process non-public personal data.
Human Oversight: Misinformation flags are reviewed by communications analysts. Counter-measures are decided by humans.
Transparency: Monitoring reports include data sources. The account classification algorithm is not publicly disclosed.
Technical Documentation: Monitoring keywords and data collection scope are documented. Detection accuracy variance across languages has not been sufficiently evaluated.

---

**B-10: Food Security Early Warning System**
System Name: Food Security Early Warning System
Purpose: Integrates meteorological data, crop yield forecasts, and market price data to predict food crisis risk zones 3–6 months ahead.
Deployment Context: FAO analytics platform, used by policy analysts.
Data Processing: Satellite remote sensing data, weather station data, market price reports, historical food crisis data.
Human Oversight: Warning reports are reviewed by food security experts. Policy recommendations are formulated by humans.
Transparency: Warning level criteria (Low / Medium / High / Emergency) are publicly disclosed. Weights for different data sources are not disclosed.
Technical Documentation: Predictive model is documented. Quantification of prediction uncertainty for data-scarce regions (parts of sub-Saharan Africa) is insufficient.

---

**B-11: Children's Educational Content Filter**
System Name: Children's Educational Content Filter
Purpose: Filters content inappropriate for children on the online learning platform for UN children's education programs.
Deployment Context: UNICEF online learning platform, serving users aged 6–17.
Data Processing: Scans user-generated content (Q&A, comments). Content scan records are anonymized. Children's user data receives additional protection.
Human Oversight: Filtered content is sampled and reviewed by content moderators. A channel for handling complaints is in place.
Transparency: Guardians are informed that the platform uses content filtering. The full list of filtering criteria is not publicly disclosed.
Technical Documentation: Filter categories and test results are documented. Consistency of content judgment standards across multi-cultural contexts has not been sufficiently validated.

---

**B-12: Post-Disaster Needs Assessment Automation**
System Name: Post-Disaster Needs Assessment Automation
Purpose: Processes post-disaster needs assessment reports submitted by field staff and automatically aggregates affected population and needs data.
Deployment Context: UN Humanitarian Data Platform, used by assessment coordinators.
Data Processing: Processes field reports that may contain anonymized information about affected individuals. Data is output in aggregated form after integration.
Human Oversight: Aggregated data is reviewed by coordinators. Data anomalies trigger manual investigation.
Transparency: Aggregate reports describe data sources and collection methods. The specific implementation of the data merging algorithm is not disclosed.
Technical Documentation: Supported report formats and data field mappings are documented. Handling logic for poor-quality reports is not sufficiently explained.

---

**B-13: UN Staff Travel Security Assessment**
System Name: UN Staff Travel Security Assessment
Purpose: Assesses the security risk level of destinations for UN staff travel and generates security briefings.
Deployment Context: UN security management system, used by travel-planning staff and security managers.
Data Processing: Destination security incident database, political stability indices, real-time conflict monitoring data.
Human Oversight: Security ratings are reviewed by security managers. High-risk missions require Security Council approval.
Transparency: Security briefings include information sources and assessment timestamp. Some intelligence sources are labeled "classified."
Technical Documentation: Risk rating model is documented. Integration methodology for emerging threats (e.g., cybersecurity risks) is insufficiently described.

---

**B-14: UN Language Learning Personalization Engine**
System Name: UN Language Learning Personalization Engine
Purpose: Provides personalized learning paths for users of the UN language learning platform, adjusting content difficulty based on progress and error patterns.
Deployment Context: UN staff language training platform; voluntary participation.
Data Processing: Learning progress, test results, and time-on-task data, linked to employee accounts.
Human Oversight: The personalization algorithm is periodically reviewed by language education experts. No per-user human oversight is in place.
Transparency: Users are informed that personalization is based on their learning data. Users can view their own data but cannot see the algorithm logic.
Technical Documentation: Personalization algorithm and data usage description are documented. Systematic bias across learners with different native language backgrounds has not been evaluated.

---

**B-15: UN Donation Transparency Report Generator**
System Name: UN Donation Transparency Report Generator
Purpose: Automatically generates fund flow and utilization reports for UN projects for donor review.
Deployment Context: UN financial transparency platform. Generated reports are accessible to donors and the public.
Data Processing: Financial transaction data, project expenditure records, beneficiary statistics (anonymized aggregate data).
Human Oversight: Report drafts are reviewed by finance officers. Sections involving sensitive data require additional approval.
Transparency: Report generation methodology is publicly disclosed and data sources are traceable. Some country-level operational data is redacted for security reasons.
Technical Documentation: Report templates and data aggregation rules are documented. Consistency of exchange rate handling across different currencies has not been sufficiently validated.

---

**B-16: Public Health Data Analytics Platform**
System Name: Public Health Data Analytics Platform
Purpose: Analyzes public health data submitted by member states to identify disease outbreak trends and support WHO policy recommendations.
Deployment Context: WHO internal analytics platform, used by epidemiological analysts.
Data Processing: Aggregated national health statistics, potentially including data disaggregated by age, sex, and region. No individual patient data is processed.
Human Oversight: Trend analysis results are interpreted by epidemiologists. Policy recommendations are formulated by expert committees.
Transparency: Analytical methods are published in WHO technical reports. The internal logic of the real-time analytical model is not publicly disclosed.
Technical Documentation: Data sources and analysis methods are documented. Consistency of processing across member states with varying data quality is insufficiently described.

---

**B-17: UN Internal Complaint Management System**
System Name: UN Internal Complaint Management System
Purpose: Performs initial classification of internal complaints, routes them to the appropriate handling department, and generates case tracking reports.
Deployment Context: UN Ombudsman's Office, handles internal staff complaints.
Data Processing: Complaint content, complainant information, and information about parties involved. High confidentiality requirements apply.
Human Oversight: All routing decisions are confirmed by a mediator. AI provides initial classification suggestions only.
Transparency: Complainants are informed that AI assists in classification. Classification rationale is not explained in detail to complainants.
Technical Documentation: Classification categories and routing rules are documented. Fairness evaluation across different types of complaints is missing.

---

**B-18: UN Procurement Market Price Analyzer**
System Name: UN Procurement Market Price Analyzer
Purpose: Analyzes market price data to provide procurement staff with reasonable price range references and identify abnormal quotations.
Deployment Context: Procurement management system, used by procurement analysts.
Data Processing: Historical procurement price data, market quotation data, vendor bid information.
Human Oversight: Flagged abnormal quotations are reviewed by procurement analysts. Final price negotiations are conducted by humans.
Transparency: The basis for price range calculations (data sources, time range) is explained to procurement staff.
Technical Documentation: Price analysis model and data update frequency are documented. Limitations for categories with scarce regional market data are not sufficiently described.

---

**B-19: Press Release Content Review Assistant**
System Name: Press Release Content Review Assistant
Purpose: Checks press release content for factual consistency and alignment with UN policy positions prior to publication.
Deployment Context: UN Department of Global Communications, used by public affairs staff.
Data Processing: Press release drafts and the UN official policy positions document database.
Human Oversight: Review results and suggestions are reviewed by communications officers. All edits are made by humans.
Transparency: When flagging inconsistencies, the referenced policy document is cited. The completeness and currency of the policy position database are not sufficiently communicated.
Technical Documentation: Policy document library scope and update mechanism are documented. Handling logic for ambiguous policy positions is not adequately described.

---

**B-20: UN Project Performance Evaluation Assistant**
System Name: UN Project Performance Evaluation Assistant
Purpose: Analyzes project reporting data, generates performance indicator scores, and supports project evaluation committee decisions.
Deployment Context: UN project management platform. Evaluation results are used by project committees.
Data Processing: Project KPI data, budget execution data, beneficiary report data.
Human Oversight: Performance scores are reviewed by the evaluation committee. Renewal decisions are made exclusively by humans.
Transparency: Scoring dimensions and weights are communicated to project teams. How the algorithm handles incomplete data is not explained.
Technical Documentation: Evaluation dimensions and data sources are documented. The impact of poor-quality project reports on scoring is not sufficiently described.

---

## Category C: Non-Compliant — 10 Systems

**C-01: Automated Recruitment Screening System (No Human Oversight)**
System Name: Automated Recruitment Screening System
Purpose: Automatically scores and ranks job applicants, decides which candidates advance to the next interview round, and sends rejection or invitation emails with no human review at any stage.
Deployment Context: HR system processes all incoming job applications automatically. Results are sent directly as rejection/invitation emails under the HR department's name.
Data Processing: Collects full resume text including name, age, educational background, and work history. No data retention limit is defined.
Human Oversight: None. The system sends hiring decisions automatically. Human staff become involved only after a candidate formally complains.
Transparency: Candidates are not informed of the AI system's existence. Emails are presented as sent by the HR department.
Technical Documentation: No formal technical documentation. System is built on a commercial black-box API. Scoring rationale cannot be explained or audited.

---

**C-02: Biometric Access Control System (No Exemption Basis)**
System Name: Biometric Access Control System
Purpose: Uses facial recognition technology at the entrance of UN office buildings to verify identity and record visitors, including real-time identification of visitors in publicly accessible areas.
Deployment Context: UN headquarters building, including parts of the facility open to the general public.
Data Processing: Collects facial images of all individuals entering the premises, compares them against a database, and flags and retains images of unmatched individuals.
Human Oversight: The system automatically denies entry to unmatched individuals. Security personnel intervene only when the system raises an alert.
Transparency: A small notice is posted at the building entrance but does not clearly explain data retention policies or purposes of use.
Technical Documentation: Vendor provides basic installation documentation. No detailed information on accuracy rates, bias testing, or data retention policies is available.

---

**C-03: Employee Sentiment Monitoring System**
System Name: Employee Sentiment Monitoring System
Purpose: Analyzes the emotional tone of employees' internal communications (emails, instant messages) and generates departmental sentiment reports to alert management about "low morale" teams.
Deployment Context: HR system operates without employees' knowledge. Reports are accessible to senior management only.
Data Processing: Continuously scans employee work communications. Data is retained indefinitely and linked to employee records.
Human Oversight: No periodic human review. The system automatically generates reports that management uses as the basis for personnel decisions.
Transparency: Employees are unaware of the system's existence. No mention is made in the employee handbook.
Technical Documentation: Commercially procured system with no available technical documentation. Sentiment analysis accuracy cannot be assessed.

---

**C-04: Humanitarian Microloan Auto-Approval System**
System Name: Humanitarian Microloan Auto-Approval System
Purpose: Automatically approves or rejects microloan applications from refugees and displaced persons with no human review.
Deployment Context: UNHCR economic empowerment program; fully automated approval.
Data Processing: Applicant personal information, refugee status, historical repayment records (if available), and social network data (obtained via mobile phone).
Human Oversight: None. All loan decisions are made automatically. Applicants receive system-generated result notifications.
Transparency: Applicants are not informed that an AI makes the decision. Notification letters state only "Your application has been processed."
Technical Documentation: Based on a third-party credit scoring API. No algorithmic documentation is available to the UN. Scoring fairness cannot be verified.

---

**C-05: AI-Powered "UN Official" Chatbot**
System Name: AI-Powered UN Official Chatbot
Purpose: Conducts initial communications with member state diplomats in the name of a specific UN official. The AI impersonates the official's identity. Member state representatives are not aware they are communicating with an AI.
Deployment Context: Diplomatic communications platform, disguised as a real-time communication channel with an actual official.
Data Processing: All diplomatic communications are stored, linked to member state accounts, and transmitted to third-party servers for processing.
Human Oversight: The actual official receives a weekly summary and does not review AI conversations in real time.
Transparency: None. The system actively deceives the other party into believing they are communicating with a real human official.
Technical Documentation: No formal documentation. A rapidly deployed proof-of-concept project with no security assessment.

---

**C-06: Real-Time Child Online Behavior Monitoring System**
System Name: Child Online Behavior Monitoring System
Purpose: Monitors all child users' behavior in real time on UNICEF's online learning platform (mouse movements, keystroke speed, attention drift), generates learner profiles, and sells these to third-party educational companies.
Deployment Context: UNICEF online education platform; users are children aged 6–17.
Data Processing: Collects detailed behavioral data and learner profiles, which are transmitted to and stored on commercial partner servers for commercial purposes.
Human Oversight: Data sharing is fully automated with no human review of sharing decisions.
Transparency: Guardian-facing disclosures mention "improving the learning experience" only. Data sales are not disclosed.
Technical Documentation: No documentation on the scope of data sharing or security measures.

---

**C-07: Predictive Policing AI for UN Peacekeeping**
System Name: Predictive Policing AI for UN Peacekeeping
Purpose: Uses historical conflict data in peacekeeping mission areas to predict "high-risk individuals," generates surveillance lists, and authorizes peacekeeping forces to conduct preventive detention of listed individuals.
Deployment Context: UN peacekeeping mission areas, integrated with mission security forces.
Data Processing: Collects individual ethnicity, religion, social connections, and historical records. Generates risk scores linked to individual identities.
Human Oversight: List generation is automated. Detention actions based on system scores are carried out by frontline security personnel with no independent review mechanism.
Transparency: Monitored individuals are unaware. Lists are not publicly disclosed. Algorithm logic is secret.
Technical Documentation: Vendor claims system effectiveness. No independent verification. No accuracy rate or false positive rate data.

---

**C-08: Asylum Application Auto-Rejection System**
System Name: Asylum Application Auto-Rejection System
Purpose: Automatically rejects asylum applications algorithmically assessed as "non-credible," with no human review. Rejection decisions are sent directly to applicants.
Deployment Context: Refugee registration processing system; handles all asylum applications.
Data Processing: Applicant narrative text, nationality, and entry route. NLP is used to analyze "credibility." Decisions directly affect individual asylum rights.
Human Oversight: No human involvement in rejection decisions. Applicants are informed "the application does not meet requirements" with no explanation provided.
Transparency: Applicants are unaware that an AI made the decision. The reason for rejection cannot be ascertained.
Technical Documentation: Algorithm purchased from a commercial vendor. The UN has no access to the algorithm's internal logic.

---

**C-09: Employee Attrition Prediction System (Discriminatory Features)**
System Name: Employee Attrition Prediction System
Purpose: Predicts which employees are at risk of leaving. The model is trained on employee marital status, age, and whether they have children, and is used to decide which employees receive promotions and training opportunities.
Deployment Context: HR system; prediction results directly affect the allocation of career development opportunities.
Data Processing: Employee personal information (marital status, age, children, spouse employment status), work performance data, and social media data (obtained via API).
Human Oversight: Promotion recommendations are auto-generated. HR only approves; no independent evaluation of individual employees takes place.
Transparency: Employees are unaware that personal life information is used to make career decisions.
Technical Documentation: Model feature importance analysis shows marital status and age are significant predictors. No discrimination impact assessment has been conducted.

---

**C-10: Whistleblower De-anonymization System**
System Name: Whistleblower De-anonymization System
Purpose: Attempts to identify the true identity of anonymous whistleblowers through writing style analysis and behavioral profiling, and provides management with a list of "suspected whistleblowers."
Deployment Context: UN internal audit and compliance system; authorized by senior management.
Data Processing: All employees' historical documents, reports, and emails are used to build writing style fingerprints, which are then compared against anonymous report content.
Human Oversight: System generates a suspect list. Subsequent actions are decided by management with no independent oversight.
Transparency: Employees are unaware that their historical writing is used to build identification profiles. The "anonymity" promised by the reporting channel does not actually exist.
Technical Documentation: Technical methodology is classified. No accuracy evaluation is available. False positives may cause serious harm to innocent employees.

---

 