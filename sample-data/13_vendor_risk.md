# Vendor & Third-Party Risk Assessment

**Document ID:** VR-2026-013  
**Last Updated:** 2026-03-21  
**Owner:** Procurement & Security  
**Status:** In Review

## Vendors in Scope

- **Translation Provider (US-East)**
  - SLA: 99.5% uptime, P95 latency 800ms
  - Data handling: stores request logs for 30 days in US region
  - Issues: Latency spikes during JP peak hours; DPIA addendum not signed
- **CRM Connector (Multi-tenant)**
  - SLA: 99.9% uptime, P95 500ms
  - Data handling: stores ticket summaries in shared storage (region varies)
  - Issues: Standard contractual clauses (SCC) pending; audit requires region pinning to APAC
- **Monitoring Vendor**
  - SLA: 99.9% uptime
  - Data handling: metrics stored in APAC; logs mirrored to US for analytics
  - Issues: Mirror contains pseudonymized user IDs; legal evaluating risk

## Current Risk Ratings

- Translation Provider: **High** (latency + data residency)
- CRM Connector: **Medium** (contractual & residency controls pending)
- Monitoring Vendor: **Low** (pseudonymization in place, but review open)

## Mitigations & Deadlines

- Translation Provider:
  - Add JP gateway or turn off fallback in production until SLA proven.
  - Retry logic + timeout budget enforcement (see `12_incident_history.md`).
  - Deadline: **2026-04-08** for go/no-go decision.
- CRM Connector:
  - Enable APAC-only storage and append SCC addendum.
  - Deadline: **2026-04-10** to avoid blocking analytics export.
- Monitoring Vendor:
  - Confirm that mirrored logs exclude raw PII.
  - Deadline: **2026-04-05**.

## Launch Implications

- Proceeding with translation provider as-is conflicts with `09_regional_compliance.md`.
- CRM connector contract must be updated before enabling SG failover analytics.
- Vendor readiness is a **gating item** for "green" launch status; otherwise launch is **Conditional Go** with compensating controls.
