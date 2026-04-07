# Regional Compliance & Data Residency Requirements

**Document ID:** CMP-2026-009  
**Last Updated:** 2026-03-18  
**Owner:** Compliance Office  
**Status:** In Review

## Scope

- Applicable regions: Japan (primary), Singapore (failover), EU (analytics mirror)
- Data types: chat transcripts, user profile metadata, model telemetry, logs
- Systems covered: AI chatbot, Azure AI Search index, monitoring stack, ticketing integration

## Data Residency Rules

- **Japan:** Primary storage required for PII and transcripts. Local processing only for production traffic. Cross-region export prohibited without masking.
- **Singapore:** Allowed for warm standby, but PII must be tokenized before replication. Failover must disable raw log shipping.
- **EU:** Analytics mirror allowed only with irreversible aggregation. No customer identifiers may leave Japan.
- **Encryption:** At-rest with customer-managed keys (CMK) for JP and SG. EU analytics may use platform-managed keys if data is anonymized.

## Logging & Retention

- Application Insights currently retains 90 days of logs; policy requires **45-day cap** for PII-bearing events.
- Query logs from Azure AI Search must be truncated to remove user identifiers before export.
- Chat transcripts must be redacted prior to being used for model evaluation.
- **Open gap:** Log export pipeline still writes full transcripts to a shared storage account in East US (non-compliant).

## Access Controls

- Role-based access for JP region is configured; **SG roles not mapped** for failover.
- Just-in-time access required for production support; currently enabled only in JP.
- Audit trail must include tool calls and retrieval sources; not enabled for the analytics mirror.

## Third-Party Data Transfer

- Translation fallback uses an external API hosted in US-East. Data residency review **pending**; must route through JP gateway or disable for production.
- CRM integration exports ticket summaries daily to vendor-managed storage; DPIA addendum **not signed**.
- Legal requires signed SCC (Standard Contractual Clauses) before any EU analytics export.

## Upcoming Audits & Deadlines

- JP compliance spot check: **2026-04-05**
- SG failover tabletop: **2026-04-10**
- DPIA completion for CRM vendor: **2026-04-08**
- Updated logging retention validation: **2026-04-07**

## Outstanding Actions

1. Disable East US log export and reconfigure to JP storage with redaction.
2. Complete SG access mapping and failover data-tokenization test.
3. Secure DPIA sign-off for CRM vendor and SCC for EU analytics.
4. Decide on translation fallback: gateway in JP or feature toggle off.

## Implications for Launch

- Launch may proceed **only if** JP storage and logging gaps are closed and SG failover does not replicate raw PII.
- Analytics mirror must be aggregation-only by launch date or be disabled.
