# Sample Data for AI Feature Launch Decision

This directory contains sample documentation for a realistic **Go/No-Go Launch Advisor** scenario used to demonstrate the comparison between Classic RAG and Foundry IQ.

## Scenario Context

An organization is planning to launch an AI-powered customer support feature to production in Japan region by April 30, 2026. The decision involves:

- Internal policies and procedures
- Technical readiness
- Budget constraints
- Security and compliance requirements
- Timeline pressures
- Open issues and risks

## Files Overview

### 01_project_overview.md
- **Purpose:** High-level project context, timeline, scope
- **Key Points:**
  - April 30, 2026 target launch date
  - AI customer support chatbot using Azure OpenAI
  - Japan region deployment
  - Multiple pending items before launch

### 02_architecture_decision.md
- **Purpose:** Technical decisions and architecture choices
- **Key Points:**
  - ADR for Azure OpenAI Service, GPT-4 model selection
  - Vector database decisions (Azure AI Search)
  - Some decisions approved, some under review
  - Preview feature considerations

### 03_security_policy.md
- **Purpose:** Security requirements and compliance checklist
- **Key Points:**
  - Mandatory security controls (authentication, encryption, PII redaction)
  - Production deployment requirements
  - Several items ⏳ pending completion
  - Preview features explicitly prohibited without exception

### 04_preview_feature_policy.md
- **Purpose:** Policy on using Azure preview/beta features
- **Key Points:**
  - **Preview features PROHIBITED in production** (default policy)
  - Exception process defined
  - GPT-4 Turbo exception request **DENIED** (case study)
  - Must use GA (Generally Available) features only

### 05_budget_guardrail.md
- **Purpose:** Budget constraints and cost management
- **Key Points:**
  - Monthly budget: $25,000 (OpEx)
  - Current estimate: $27,400/month (**9.6% over budget**)
  - Cost optimization plan to bring under budget
  - Budget approval conditional on implementing optimizations

### 06_rollout_plan.md
- **Purpose:** Phased rollout strategy and timeline
- **Key Points:**
  - Phased approach: Internal Beta → Limited Beta → Soft Launch → GA
  - **🔴 BLOCKER:** Security assessment timeline conflict
  - Several open issues that may impact April 30 launch
  - Risk assessment and contingency plans

### 07_open_issues.md
- **Purpose:** Known problems and blockers
- **Key Points:**
  - 2 critical blockers (PII redaction, rate limiting)
  - 3 medium-priority issues in progress
  - Current assessment: **🟡 YELLOW (Conditional Go)**
  - Some issues can launch with workarounds

### 08_exception_process.md
- **Purpose:** How to request policy exceptions
- **Key Points:**
  - Formal approval process for policy deviations
  - Examples of approved and denied exceptions
  - GPT-4 Turbo exception **DENIED** case study
  - High bar for preview feature exceptions

### 09_regional_compliance.md
- **Purpose:** Data residency, cross-border transfer, and logging rules
- **Key Points:**
  - JP primary storage required; SG failover must tokenize PII
  - East US log export is non-compliant and must be disabled
  - Translation vendor in US requires gateway or shutdown

### 10_resiliency_plan.md
- **Purpose:** SLOs, load testing, DR and failover readiness
- **Key Points:**
  - Capacity gap: need 3 search replicas before launch
  - SG failover automation incomplete; cache cold-start risk
  - Chaos test revealed stale data during ingest spikes

### 11_customer_feedback.md
- **Purpose:** Pilot CSAT results and qualitative findings
- **Key Points:**
  - CSAT 3.6/5 with gaps in policy grounding and outage comms
  - Missing postmortems and regional updates hurt answer quality
  - Action items for style guidance and cached outage scripts

### 12_incident_history.md
- **Purpose:** Postmortems and open remediation items
- **Key Points:**
  - Recent incidents: stale search results, log export leak, translation failures
  - Critical actions due before launch (log export fix, ingest throttling)
  - Launch blocked if residency fixes slip past April 7

### 13_vendor_risk.md
- **Purpose:** Third-party dependencies and contract status
- **Key Points:**
  - Translation provider and CRM connector have residency/SLA gaps
  - SCC/DPIA sign-offs pending; decisions due early April
  - Vendor readiness is gating for a green launch

## Expected Query Behavior

### Example Question
> "この AI 機能を、日本向け本番環境で来月リリースしてよいか。内部ポリシー、現在の実装状況、予算制約、最新の公式ドキュメント変更を踏まえて、可否 / ブロッカー / 次アクション を答えてください"
>
> (English: "Should we launch this AI feature in production for Japan next month? Considering internal policies, current implementation status, budget constraints, and latest official documentation changes, provide Go/No-Go recommendation, blockers, and next actions.")

### Classic RAG Agent (Expected Behavior)
- Retrieves relevant documents based on keyword matching
- May miss nuanced connections between documents
- Likely provides surface-level answer
- May not synthesize cross-document implications
- Example: "Some issues are pending, but most items are complete"

### Foundry IQ Agent (Expected Behavior)
- Breaks down the question into sub-queries:
  - "Are there any security policy blockers?"
  - "Is the budget approved?"
  - "What is the status of preview features?"
  - "Are there any critical open issues?"
- Retrieves and synthesizes information across multiple documents
- Identifies key blocker: **Security assessment not completed**
- Recognizes timeline conflict in rollout plan
- Provides nuanced answer with context:
  - **Conditional Go** recommendation
  - Lists specific blockers with resolution timelines
  - Highlights preview feature policy compliance (GPT-4 GA approved)
  - Notes budget overrun with mitigation plan
  - Provides actionable next steps

## Testing the Difference

Use this data to test and demonstrate:

1. **Answer Quality:** Foundry IQ should provide more comprehensive analysis
2. **Citation Accuracy:** Foundry IQ should cite multiple relevant sections
3. **Query Decomposition:** Foundry IQ shows internal reasoning steps
4. **Cross-Document Synthesis:** Foundry IQ connects information across files
5. **Nuance Detection:** Foundry IQ catches "Conditional Go" vs simple "Go/No-Go"

> Note: With the extended documents (09-13), the corpus now exceeds 50 chunks. A single-shot AI Search retrieval that caps at 50 will miss residency, incident, and vendor risk details, while Foundry IQ's decomposition can hop across those sources.

## Intentional Complexity

This data set includes:

- ✅ **Contradictions:** Some documents show optimism, others show blockers
- ✅ **Temporal dependencies:** Dates and timelines that need sequencing
- ✅ **Cross-references:** Documents reference each other
- ✅ **Status variations:** ✅ completed, ⏳ pending, 🔴 blocking
- ✅ **Nuanced decisions:** Not simple yes/no answers
- ✅ **Multiple stakeholders:** Different approval requirements
- ✅ **Policy layering:** Preview policy impacts architecture decisions

## Data Quality Notes

This is **synthetic demonstration data** designed to:
- Represent realistic enterprise decision-making
- Showcase Foundry IQ capabilities
- Demonstrate the value of agentic retrieval
- Provide measurable comparison points

**Not for production use.** This is demo/test data only.

## Indexing Instructions

For **Azure AI Search**:
1. Create an index with text and vector search capabilities
2. Index each .md file as a separate document
3. Use text-embedding-ada-002 or equivalent for vector embeddings
4. Enable semantic ranking if available

For **Foundry IQ Knowledge Base**:
1. Create a knowledge base with these documents as sources
2. Configure for agentic retrieval mode
3. Enable query decomposition and multi-step retrieval
4. Test with sample queries to validate behavior

## Sample Queries for Testing

### Simple Query (Both Should Handle Well)
- "What is the project timeline?"
- "What is the monthly budget?"

### Medium Complexity (Foundry IQ Advantage)
- "Are there any security blockers for the launch?"
- "What preview features are being used?"

### High Complexity (Foundry IQ Significant Advantage)
- "Should we launch on April 30? What are the risks?"
- "この AI 機能をリリースすべきか？ポリシーと予算の観点から評価してください"
- "What are the dependencies between security assessment, internal beta, and the launch date?"
- "Can we enable SG failover without violating data residency, and what vendor contracts block this?"
- "What incidents and customer feedback must be addressed before launch to avoid another stale-data event?"
- "Which launch blockers remain when combining security, regional compliance, vendor risk, and SLO gaps?"
- "請求・障害・コンプライアンスを含めて、APACローンチの可否を判断し、根拠となる資料の場所を教えてください。"

## Version History

- 2026-03-28: Initial sample data set created
- 2026-04-07: Added regional compliance, resiliency, customer feedback, incident, and vendor risk docs to create >50-chunk corpus for contrast testing
- Represents state as of late March 2026 (pre-launch)
