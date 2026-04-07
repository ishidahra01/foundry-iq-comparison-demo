# Incident History & Open Action Items

**Document ID:** IR-2026-012  
**Last Updated:** 2026-03-19  
**Owner:** SRE / Security  
**Status:** Active

## Recent Incidents

### IR-2026-0312: Search Index Latency Spike
- Date: 2026-03-12
- Impact: 18-minute period where responses returned stale data
- Root Cause: Background ingest job saturated vector search partitions
- Status: **Action Items Open**

### IR-2026-0315: Log Export Leak
- Date: 2026-03-15
- Impact: Unredacted chat transcripts exported to East US storage account
- Root Cause: Legacy export pipeline bypassed new redaction step
- Status: **Containment done**, backlog for permanent fix

### IR-2026-0317: Translation Fallback Error
- Date: 2026-03-17
- Impact: 4% of sessions failed when translation vendor endpoint throttled
- Root Cause: Missing retry/backoff; dependency hosted in US region
- Status: **Retry logic pending**, vendor SLA under review

## Open Action Items

| Item | Owner | Due | Status | Notes |
| --- | --- | --- | --- | --- |
| Automate search throttling during ingest windows | SRE | 2026-04-06 | In Progress | Tied to load-test risk in `10_resiliency_plan.md` |
| Replace East US log export with JP storage | Security | 2026-04-07 | Not Started | Must align with `09_regional_compliance.md` |
| Implement translation fallback retry + JP gateway | Platform | 2026-04-08 | Not Started | Dependency on vendor contract review |
| Add incident summaries to knowledge base | Product | 2026-04-05 | In Progress | Needed to close CSAT gap in `11_customer_feedback.md` |

## Lessons Learned

- Need coordinated change window for ingest vs query load; schedule being drafted.
- Must validate data residency on **every** export path, not just main pipeline.
- Knowledge base must include incident summaries; current omissions cause user confusion.
- Vendor placement (US) creates latency and compliance exposure during spikes.

## Launch Readiness Impact

- Launch is **blocked** if log export fix slips past April 7.
- DR exercises must include ingestion throttling plan to prevent stale data.
- Adding postmortem content improves grounding for outage-related questions.
