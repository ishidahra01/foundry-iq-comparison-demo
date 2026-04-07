# Resiliency, Capacity, and SLA Readiness

**Document ID:** OPS-2026-010  
**Last Updated:** 2026-03-20  
**Owner:** SRE Team  
**Status:** Active with Open Risks

## Service Level Objectives

- Availability SLO: **99.9% monthly** (error budget: 43.2 minutes/month)
- Latency SLO: P95 < 3.5s for JP users, P95 < 4.2s during SG failover
- Data freshness: search index lag < 15 minutes for new tickets

## Load & Failure Testing

- March 18 load test: sustained 900 RPS, P95 latency 3.1s (pass)
- Spike test at 1,400 RPS caused vector search timeout and retries; effective P95 6.4s (fail)
- Chaos test (index partition restart) showed **10-minute stale results** before recovery
- Azure AI Search replica count: 2 (JP). Runbook requires 3 for launch; cost impact +$1,800/month.

## Dependencies & DR

- Primary: Azure AI Search (JP), Azure OpenAI (JP), App Service (JP)
- DR: App Service + Search in SG configured, but **index replication not automated**; manual steps take ~45 minutes.
- Redis caching for embeddings is **single region**; during SG failover cache is cold, increasing latency.
- Azure Function that refreshes rollup dashboards is tied to JP Event Hub namespace; cross-region failover path untested.

## Monitoring & Alerting

- Synthetic probes cover JP only; SG endpoints not monitored.
- Alert thresholds tuned for P95 latency in JP; no runbooks for SG latency profiles.
- Incident communication runbook references legacy Teams channels; needs update to new on-call rotation.

## Open Risks & Actions

- **Capacity Risk:** Need 3 replicas for Azure AI Search before April 20 to hit SLO during launch week.
- **Failover Risk:** SG playbook missing automation; create infra-as-code and rehearse by **2026-04-12**.
- **Data Freshness Risk:** Index refresh job occasionally lags 25 minutes during heavy ingest; root cause under investigation.
- **Chaos Test Follow-Up:** Improve retry/backoff in API layer to avoid cascading timeouts.

## Launch Readiness Assessment

- Current status: **🟡 At Risk** due to DR gaps and capacity shortfall.
- Go decision requires: replica scale-up, SG automation rehearsal, cache warmup strategy, and updated runbooks.
