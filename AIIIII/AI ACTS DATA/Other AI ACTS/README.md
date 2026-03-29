# AI Standards & Guidelines - Markdown Collection

> Comprehensive collection of AI security, risk management, and ethics standards converted to Markdown for RAG systems

## 📋 Overview

This collection contains **5 essential AI standards and guidelines** from leading organizations (NIST, OWASP, UN, UNESCO), all converted to Markdown format for easy integration into RAG (Retrieval-Augmented Generation) systems.

**Document Statistics:**
- Total Documents: 5
- Total Pages: 252
- Total Size: ~630 KB
- Estimated Tokens: ~157,000 tokens (GPT-4 standard)

---

## 📚 Document Collection

### 1. NIST Adversarial ML Taxonomy (127 pages, 341 KB)

**File:** `NIST_Adversarial_ML_Taxonomy.md`

**Full Title:** Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations

**Publisher:** NIST (National Institute of Standards and Technology)
**Document ID:** NIST AI 100-2e2025
**Authors:** Apostol Vassilev, Alina Oprea, Alie Fordyce, Hyrum Anderson

**Key Topics:**
- Taxonomy of adversarial attacks on ML systems
- Evasion attacks (inference time)
- Poisoning attacks (training time)
- Privacy attacks (model inversion, membership inference)
- Abuse attacks (model stealing, prompt injection)
- Mitigation strategies and defenses
- Security considerations for AI/ML deployment

**Why Important:**
- Most comprehensive taxonomy of ML security threats
- Essential for AI security risk assessment
- Provides standardized terminology for adversarial ML
- Covers both traditional ML and LLM-specific attacks

**RAG Use Cases:**
- Security assessment of ML models
- Threat modeling for AI systems
- Identifying attack vectors and mitigations
- Understanding adversarial robustness

---

### 2. NIST AI Risk Management Framework (48 pages, 100 KB)

**File:** `NIST_AI_RMF.md`

**Full Title:** Artificial Intelligence Risk Management Framework (AI RMF 1.0)

**Publisher:** NIST
**Document ID:** NIST AI 100-1
**Released:** January 2023

**Key Topics:**
- Four core functions: GOVERN, MAP, MEASURE, MANAGE
- Trustworthy AI characteristics (safe, secure, resilient, etc.)
- Risk management throughout AI lifecycle
- Integration with other frameworks (ISO, GDPR, EU AI Act)
- Organizational governance structures
- Stakeholder engagement
- Documentation and transparency

**Why Important:**
- Official US government AI risk framework
- Voluntary consensus standard
- Aligns with international standards (ISO/IEC 23894)
- Provides actionable risk management approach
- Complementary to EU AI Act requirements

**RAG Use Cases:**
- AI governance program design
- Risk assessment methodology
- Compliance mapping (NIST RMF ↔ EU AI Act ↔ GDPR)
- Trustworthiness evaluation
- Policy development

---

### 3. OWASP LLM Top 10 (2025) (45 pages, 98 KB)

**File:** `OWASP_LLM_Top_10_2025.md`

**Full Title:** OWASP Top 10 for LLM Applications 2025

**Publisher:** OWASP (Open Web Application Security Project)
**Version:** 2025 (released November 2024)

**Key Topics:**
- LLM01: Prompt Injection
- LLM02: Sensitive Information Disclosure
- LLM03: Supply Chain Vulnerabilities
- LLM04: Data and Model Poisoning
- LLM05: Improper Output Handling
- LLM06: Excessive Agency
- LLM07: System Prompt Leakage
- LLM08: Vector and Embedding Weaknesses
- LLM09: Misinformation
- LLM10: Unbounded Consumption

**Why Important:**
- Most authoritative LLM security guide
- Updated for 2025 threat landscape
- Practical attack examples and mitigations
- Industry standard for LLM application security
- Directly applicable to production systems

**RAG Use Cases:**
- LLM application security assessment
- Vulnerability scanning checklists
- Secure development guidelines
- Penetration testing references
- Security training materials

---

### 4. UN Human Rights Due Diligence for Digital Tech (27 pages, 70 KB)

**File:** `UN_Human_Rights_Digital_Tech_Guidance.md`

**Full Title:** Human Rights Due Diligence for Digital Technology Use - Call to Action for Human Rights

**Publisher:** United Nations Secretary-General
**Released:** May 2024

**Key Topics:**
- Human rights risks of digital technologies (including AI)
- Due diligence framework for UN entities
- Risk assessment methodologies
- Rights-based approach to technology deployment
- Stakeholder engagement requirements
- Remediation and accountability
- Special considerations for vulnerable populations
- Alignment with UN Guiding Principles on Business and Human Rights

**Why Important:**
- Official UN guidance on AI ethics and human rights
- Bridges technical and human rights perspectives
- Mandatory for UN system entities
- Influential for governments and NGOs
- Complements GDPR and EU AI Act from rights perspective

**RAG Use Cases:**
- Human rights impact assessment (HRIA)
- Ethical AI evaluation from rights perspective
- Vulnerable population risk analysis
- Stakeholder consultation frameworks
- Alignment with UN Sustainable Development Goals

---

### 5. UNESCO AI Ethics Recommendation (5 pages, 20 KB)

**File:** `UNESCO_AI_Ethics.md`

**Full Title:** UNESCO's Input on New and Emerging Digital Technologies and Human Rights (UNESCO Recommendation on the Ethics of Artificial Intelligence)

**Publisher:** UNESCO
**Adopted:** November 2021 (193 member states)

**Key Topics:**
- 10 core ethical principles for AI
- Human rights and dignity
- Living in peaceful, just and interconnected societies
- Environmental and ecosystem flourishing
- Ensuring diversity and inclusiveness
- Policy action areas (governance, data, development, etc.)
- Implementation recommendations for member states
- Multi-stakeholder approach

**Why Important:**
- First global standard-setting instrument on AI ethics
- Adopted by 193 UNESCO member states
- Legally non-binding but politically influential
- Holistic approach (not just technical)
- Strong focus on Global South perspectives

**RAG Use Cases:**
- Ethical AI policy development
- Cross-cultural AI ethics considerations
- Global South AI deployment contexts
- Multi-stakeholder engagement frameworks
- Educational AI ethics curricula

---

## 🎯 Document Relationships

### Complementary Coverage

```
Security Layer:
├── NIST Adversarial ML Taxonomy → Technical security threats
└── OWASP LLM Top 10 → Application security vulnerabilities

Risk Management Layer:
└── NIST AI RMF → Comprehensive risk framework

Ethics & Rights Layer:
├── UN Human Rights Guidance → Rights-based approach
└── UNESCO AI Ethics → Ethical principles and values
```

### Integration with EU Regulations

These standards integrate with your existing EU AI Act and GDPR collections:

| Standard | Primary Alignment | Complementary Value |
|----------|-------------------|---------------------|
| NIST Adversarial ML | EU AI Act Article 15 (Accuracy, robustness) | Detailed attack taxonomy |
| NIST AI RMF | EU AI Act Chapter III (Risk management) | Process framework |
| OWASP LLM Top 10 | GDPR Article 32 (Security of processing) | LLM-specific threats |
| UN Human Rights | GDPR Recitals (fundamental rights) | Rights impact assessment |
| UNESCO AI Ethics | EU AI Act Recitals (ethical principles) | Global ethics context |

---

## 📂 File Structure

```
Standards_Guidelines_Markdown/
├── README.md                                    (this file)
├── metadata.json                                (document metadata)
├── NIST_Adversarial_ML_Taxonomy.md             (341 KB)
├── NIST_AI_RMF.md                               (100 KB)
├── OWASP_LLM_Top_10_2025.md                     (98 KB)
├── UN_Human_Rights_Digital_Tech_Guidance.md     (70 KB)
└── UNESCO_AI_Ethics.md                          (20 KB)
```

---

## 🔧 RAG Integration Guide

### Recommended Loading Strategy

**Scenario 1: Security-Focused RAG**
```python
# Load security-related documents only
priority_files = [
    "NIST_Adversarial_ML_Taxonomy.md",  # Security threats
    "OWASP_LLM_Top_10_2025.md"          # LLM vulnerabilities
]
# Use case: AI security assessment, penetration testing
```

**Scenario 2: Compliance & Risk Management**
```python
# Load regulatory and risk documents
priority_files = [
    "NIST_AI_RMF.md",                    # Risk framework
    "UN_Human_Rights_Digital_Tech_Guidance.md"  # Rights assessment
]
# Use case: Compliance mapping, risk assessment
```

**Scenario 3: Ethics & Governance**
```python
# Load ethics and policy documents
priority_files = [
    "UNESCO_AI_Ethics.md",               # Ethical principles
    "UN_Human_Rights_Digital_Tech_Guidance.md"  # Human rights
]
# Use case: Policy development, ethics review
```

**Scenario 4: Comprehensive Coverage**
```python
# Load all documents
all_files = glob("*.md", exclude=["README.md"])
# Use case: Complete AI governance and security platform
```

### Integration with Existing Collections

```python
from langchain.document_loaders import DirectoryLoader

# Load EU AI Act (from Markdown_for_RAG/)
eu_loader = DirectoryLoader(
    "../Markdown_for_RAG/",
    glob="*.md",
    exclude=["README.md"]
)
eu_docs = eu_loader.load()

# Load GDPR (from GDPR_AI_Focused/)
gdpr_loader = DirectoryLoader(
    "../GDPR_AI_Focused/",
    glob="P0_*.md"  # Load only P0 priority
)
gdpr_docs = gdpr_loader.load()

# Load Standards (from Standards_Guidelines_Markdown/)
standards_loader = DirectoryLoader(
    "./",
    glob="*.md",
    exclude=["README.md"]
)
standards_docs = standards_loader.load()

# Combine all with metadata
all_docs = []
for doc in eu_docs:
    doc.metadata["collection"] = "EU AI Act"
    all_docs.append(doc)

for doc in gdpr_docs:
    doc.metadata["collection"] = "GDPR"
    all_docs.append(doc)

for doc in standards_docs:
    doc.metadata["collection"] = "Standards & Guidelines"
    all_docs.append(doc)

# Create unified vector store
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=all_docs,
    embedding=embeddings,
    persist_directory="./unified_ai_compliance_vectorstore"
)
```

### Optimized Chunking Strategy

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Different strategies for different document types
def get_splitter_for_doc(filename):
    if "NIST_Adversarial" in filename:
        # Longer chunks for technical taxonomy
        return RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            separators=["\n### ", "\n## ", "\n\n", "\n"]
        )
    elif "OWASP" in filename:
        # Medium chunks for vulnerability descriptions
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n### LLM", "\n## ", "\n\n", "\n"]
        )
    else:
        # Standard chunks for policy documents
        return RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n## ", "\n\n", "\n"]
        )
```

### Query Routing by Document Type

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Route queries to appropriate document collections
routing_template = """
Given this user query, determine which document collection(s) are most relevant:
- "security": NIST Adversarial ML, OWASP LLM Top 10
- "risk": NIST AI RMF
- "ethics": UN Human Rights, UNESCO AI Ethics
- "compliance": EU AI Act, GDPR
- "all": Search all collections

Query: {query}

Return only the category name(s), comma-separated.
"""

# Example queries and routing:
# "How to prevent prompt injection?" → security (OWASP)
# "What is AI risk management?" → risk (NIST RMF)
# "Human rights impact of facial recognition?" → ethics, compliance
# "GDPR requirements for automated decisions?" → compliance (GDPR)
```

---

## 💡 Key Use Cases

### 1. AI Security Assessment
**Documents:** NIST Adversarial ML + OWASP LLM Top 10

**Example Query:**
> "What are the main security threats to our LLM-based chatbot application?"

**Expected Response:**
- Prompt injection vulnerabilities (OWASP LLM01)
- Training data poisoning (NIST taxonomy + OWASP LLM04)
- Model extraction attacks (NIST taxonomy)
- Sensitive information disclosure (OWASP LLM02)

### 2. Compliance Gap Analysis
**Documents:** EU AI Act + NIST AI RMF + GDPR

**Example Query:**
> "Map our AI risk management process to EU AI Act requirements"

**Expected Response:**
- NIST RMF GOVERN → EU AI Act Article 9 (risk management system)
- NIST RMF MAP → EU AI Act Annex IV (technical documentation)
- NIST RMF MEASURE → EU AI Act Article 15 (accuracy, robustness)
- GDPR Article 35 DPIA ↔ EU AI Act Article 27 conformity assessment

### 3. Ethical AI Review
**Documents:** UNESCO AI Ethics + UN Human Rights + EU AI Act Recitals

**Example Query:**
> "What ethical considerations should we address for AI in healthcare?"

**Expected Response:**
- Human dignity and autonomy (UNESCO principle 1)
- Right to health (UN Human Rights guidance)
- Special considerations for medical devices (EU AI Act Annex III)
- Informed consent requirements (GDPR Article 9)

### 4. Threat Modeling
**Documents:** NIST Adversarial ML + OWASP + EU AI Act

**Example Query:**
> "Create a threat model for our credit scoring AI system"

**Expected Response:**
- Training data poisoning risks (NIST taxonomy)
- Automated decision-making constraints (GDPR Article 22, EU AI Act Article 50)
- High-risk classification (EU AI Act Annex III)
- Adversarial examples at inference time (NIST taxonomy)

---

## 📊 Document Statistics

| Document | Pages | Size (KB) | Tokens* | Primary Focus | Target Audience |
|----------|-------|-----------|---------|---------------|-----------------|
| NIST Adversarial ML | 127 | 341 | ~85,000 | Security threats | Technical/Security |
| NIST AI RMF | 48 | 100 | ~25,000 | Risk management | Management/Compliance |
| OWASP LLM Top 10 | 45 | 98 | ~24,000 | LLM vulnerabilities | Developers/Security |
| UN Human Rights | 27 | 70 | ~17,000 | Rights assessment | Policy/Ethics |
| UNESCO AI Ethics | 5 | 20 | ~5,000 | Ethical principles | Policy/Education |
| **Total** | **252** | **630** | **~157,000** | - | - |

*Token estimates based on GPT-4 standard (1 token ≈ 4 characters)

---

## 🔗 Related Collections

This collection complements your existing document sets:

### EU Regulations
- **Location:** `../Markdown_for_RAG/`
- **Content:** EU AI Act (8 files, ~500 KB)
- **Integration:** Primary regulatory reference

### GDPR AI-Focused
- **Location:** `../GDPR_AI_Focused/`
- **Content:** 11 GDPR articles relevant to AI (64 KB)
- **Integration:** Data protection requirements

### RAG System Implementation
- **File:** `../quick_start_rag.py`
- **Purpose:** Ready-to-run RAG system that can load all collections
- **Integration:** Use as starting point for unified RAG system

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install langchain openai chromadb tiktoken
```

### 2. Load Standards Collection
```python
from langchain.document_loaders import DirectoryLoader

loader = DirectoryLoader(
    "./Standards_Guidelines_Markdown/",
    glob="*.md",
    exclude=["README.md"]
)
documents = loader.load()

print(f"Loaded {len(documents)} documents")
```

### 3. Run Sample Query
```bash
cd "/sessions/cool-adoring-pascal/mnt/AI ACTS DATA"
python quick_start_rag.py --data-dir . --setup
python quick_start_rag.py --query "What are the top LLM security risks?"
```

---

## 📝 Markdown Format Features

All documents have been converted with:

✅ **Clean text extraction** - No PDF artifacts or encoding issues
✅ **Page markers** - Each page clearly marked (## Page N)
✅ **UTF-8 encoding** - Full Unicode support
✅ **Preserved structure** - Headings, lists, tables maintained
✅ **Metadata headers** - Title, author, source, page count
✅ **RAG-optimized** - Clean paragraph breaks, no excessive whitespace

---

## ⚖️ Legal & Attribution

### Source Documents
- **NIST AI 100-2e2025 & AI 100-1**: Public domain (US Government work)
- **OWASP LLM Top 10**: Creative Commons Attribution-ShareAlike 4.0
- **UN Human Rights Guidance**: UN copyright (educational use permitted)
- **UNESCO AI Ethics**: UNESCO Open Access

### This Collection
- Markdown conversion and organization: Processing only, no content modification
- Original content copyright remains with respective publishers
- Use for research, education, and compliance purposes
- Check original sources for commercial use restrictions

---

## 🎓 Recommended Reading Order

### For Security Professionals
1. OWASP LLM Top 10 → Immediate practical threats
2. NIST Adversarial ML Taxonomy → Deep dive into attack vectors
3. NIST AI RMF → Risk management framework

### For Compliance Officers
1. NIST AI RMF → Understand risk management approach
2. UN Human Rights Guidance → Rights-based perspective
3. Review EU AI Act + GDPR (from other collections)

### For AI Developers
1. OWASP LLM Top 10 → Security checklist
2. NIST Adversarial ML → Robustness considerations
3. EU AI Act Chapter III → High-risk system requirements

### For Policy Makers
1. UNESCO AI Ethics → Global ethical principles
2. UN Human Rights Guidance → Rights framework
3. NIST AI RMF → Risk governance
4. EU AI Act (complete framework)

---

## 🔍 Search Tips for RAG Systems

### Effective Query Patterns

**For Security Questions:**
```
"What are [attack type] attacks on [system type]?"
"How to mitigate [vulnerability] in LLM applications?"
"Security best practices for [use case]"
```

**For Compliance Questions:**
```
"[Regulation name] requirements for [AI system type]"
"How does [framework A] align with [framework B]?"
"Compliance checklist for [use case]"
```

**For Ethics Questions:**
```
"Ethical considerations for AI in [domain]"
"Human rights risks of [technology]"
"How to assess [ethical principle] in [context]"
```

### Filter by Collection
```python
# Search only security documents
retriever.search_kwargs = {
    "filter": {
        "source": {"$in": ["NIST_Adversarial", "OWASP_LLM"]}
    },
    "k": 5
}
```

---

## 📚 Additional Resources

### Official Sources
- **NIST AI Portal**: https://www.nist.gov/artificial-intelligence
- **OWASP LLM Project**: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- **UN OHCHR Digital Tech**: https://www.ohchr.org/en/digital-technology-and-human-rights
- **UNESCO AI Ethics**: https://www.unesco.org/en/artificial-intelligence/recommendation-ethics

### Related Standards
- ISO/IEC 42001:2023 - AI Management System
- ISO/IEC 23894:2023 - AI Risk Management
- ISO/IEC 27090:2023 - AI Security
- NIST Cybersecurity Framework (CSF)

---

**Last Updated:** 2025-02-12
**Version:** 1.0
**Total Documents:** 5
**Total Pages:** 252
**Total Size:** 630 KB

---

> 💡 **Integration Tip:** Use this collection alongside EU AI Act and GDPR collections for comprehensive AI governance and compliance coverage. The three collections together provide regulatory requirements (EU), technical security (NIST/OWASP), and ethical frameworks (UN/UNESCO).
