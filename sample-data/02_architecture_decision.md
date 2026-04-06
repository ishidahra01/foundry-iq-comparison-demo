# Architecture Decision Records

**Document ID:** ADR-2026-001
**Last Updated:** 2026-03-10
**Status:** Approved
**Classification:** Internal

## ADR-001: Azure OpenAI Service Selection

### Status
Approved - 2026-01-15

### Context
Need to select an AI/ML platform for the customer support chatbot feature.

### Decision
Use Azure OpenAI Service with GPT-4 model.

### Rationale
- Enterprise-grade SLA and support
- Data residency in Japan region available
- Integration with existing Azure infrastructure
- Microsoft security and compliance certifications

### Consequences
**Positive:**
- Faster time to market using managed service
- Lower operational overhead
- Built-in content filtering and safety features

**Negative:**
- Dependency on Azure OpenAI service availability
- Model version updates require testing cycles
- Higher cost compared to open-source alternatives

### Technical Details
- **Model:** gpt-4 (version: 0613)
- **Deployment:** Japan East region
- **Capacity:** 120K TPM (tokens per minute)
- **Fallback:** None currently configured

## ADR-002: Vector Database for Knowledge Base

### Status
Approved - 2026-01-20

### Context
Need efficient semantic search capability for customer support knowledge base.

### Decision
Use Azure AI Search with vector search enabled.

### Rationale
- Native integration with Azure OpenAI
- Hybrid search (keyword + semantic)
- Managed service with automatic scaling
- Built-in security features

### Consequences
**Positive:**
- Simplified architecture
- Automatic index optimization
- Multi-language support

**Negative:**
- Cost scales with document count
- Limited customization options
- Vendor lock-in

### Technical Details
- **Service Tier:** Standard S1
- **Index Size:** ~50GB estimated
- **Documents:** ~100,000 support articles
- **Update Frequency:** Daily incremental updates

## ADR-003: Orchestration Layer

### Status
Approved - 2026-02-01

### Context
Need to coordinate between Azure OpenAI, Azure AI Search, and business logic.

### Decision
Use Azure Functions (Python) for orchestration.

### Rationale
- Serverless model for cost efficiency
- Native Azure integration
- Easy scaling and deployment
- Familiar tech stack for team

### Consequences
**Positive:**
- Pay-per-use pricing model
- Auto-scaling capabilities
- Simplified deployment

**Negative:**
- Cold start latency considerations
- Execution time limits
- Debugging complexity

### Technical Details
- **Runtime:** Python 3.11
- **Plan:** Premium EP1 (pre-warmed instances)
- **Timeout:** 230 seconds maximum
- **Memory:** 3.5 GB

## ADR-004: Authentication Method

### Status
Approved - 2026-02-05

### Context
Need secure authentication for customer access to chatbot.

### Decision
Use Azure AD B2C for customer authentication with social login support.

### Rationale
- Unified identity platform
- Social login (Google, Microsoft)
- MFA support built-in
- Compliance with data protection regulations

### Technical Details
- **Flow:** Authorization Code Flow with PKCE
- **Token Lifetime:** Access token 1 hour, refresh token 14 days
- **MFA:** Optional, enabled for high-risk scenarios

## ADR-005: Monitoring and Observability

### Status
Approved - 2026-02-10

### Context
Need comprehensive monitoring for production system.

### Decision
Use Azure Application Insights for telemetry, logging, and alerting.

### Rationale
- Deep integration with Azure services
- Custom metrics and dashboards
- Smart detection and anomaly alerts
- Distributed tracing support

### Technical Details
- **Sampling:** Adaptive sampling at 5 req/sec
- **Retention:** 90 days
- **Custom Events:** LLM call tracing, user interactions
- **Alerts:** Response time, error rate, token consumption

## ADR-006: Content Moderation

### Status
Approved - 2026-02-15

### Context
Need to ensure AI-generated responses are safe and appropriate.

### Decision
Use Azure AI Content Safety service with custom filters.

### Rationale
- Real-time content filtering
- Customizable severity thresholds
- Compliance with content policies
- Multi-modal support (text and images)

### Technical Details
- **Categories Monitored:** Hate, sexual, violence, self-harm
- **Severity Threshold:** Medium and above blocked
- **Custom Blocklists:** Competitor names, restricted topics
- **Performance Impact:** ~50ms average latency

## ADR-007: Data Retention

### Status
Under Review - 2026-03-10

### Context
Need to define conversation data retention policy.

### Decision
**Proposed:** Retain conversation logs for 90 days, PII-redacted logs for 1 year.

### Rationale
- Balance between debugging needs and privacy
- Compliance with GDPR and local regulations
- Support for quality improvement

### Open Questions
- Explicit user consent mechanism?
- Right to deletion implementation?
- Cross-border data transfer restrictions?

### Technical Details
- **Storage:** Azure Cosmos DB
- **Encryption:** At-rest and in-transit
- **Redaction:** Automatic PII detection and masking
- **Deletion:** Automated purge after retention period

## ADR-008: Failover and Disaster Recovery

### Status
Under Review - 2026-03-10

### Context
Need resilience strategy for production failures.

### Decision
**Proposed:** Multi-region deployment with automatic failover.

### Open Issues
- Cost implications of multi-region deployment
- RPO/RTO requirements not finalized
- Testing strategy for failover scenarios

### Technical Details
- **Primary:** Japan East
- **Secondary:** Japan West
- **Failover:** Azure Front Door with health probes
- **Data Sync:** Cosmos DB geo-replication

## Pending Decisions

### PD-001: Model Version Upgrade Strategy
**Status:** Discussion
**Owner:** Technical Lead
**Due Date:** April 1, 2026

Should we auto-upgrade to latest GPT-4 versions or maintain version pinning?

### PD-002: Rate Limiting Strategy
**Status:** Discussion
**Owner:** Platform Team
**Due Date:** April 5, 2026

Define rate limits per user and system-wide safeguards.

## References
- Azure Architecture Center: https://docs.microsoft.com/azure/architecture/
- OpenAI Best Practices: https://platform.openai.com/docs/guides/
- Internal Architecture Review Board: Confluence space

## Document History
- 2026-01-15: ADR-001 approved
- 2026-02-01: ADR-002, ADR-003 approved
- 2026-02-15: ADR-004, ADR-005, ADR-006 approved
- 2026-03-10: ADR-007, ADR-008 under review
