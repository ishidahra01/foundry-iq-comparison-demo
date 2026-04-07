# Customer Feedback & Beta Findings

**Document ID:** CSAT-2026-011  
**Last Updated:** 2026-03-22  
**Owner:** Customer Success  
**Status:** Draft

## Pilot Overview

- Internal beta with 120 JP users and 40 SG users (remote workers).
- Use cases: password reset, billing questions, subscription upgrades, outage status inquiries.
- Channels: web widget, mobile in-app help, email deflection.

## Satisfaction Metrics

- Overall CSAT: **3.6 / 5.0** (target 4.2).
- Containment (no human handoff): **58%** (target 70%).
- Top drivers of dissatisfaction:
  - Inconsistent tone between Japanese and English responses.
  - Limited recall of recent outage notices.
  - Slow answers during peak hours; users abandon after ~5 seconds.

## Quality Observations

- Japanese responses occasionally mix polite and casual forms; requires style guardrails.
- Sensitive topics (billing disputes) sometimes return generic answers that miss contractual wording.
- Retrieval gaps for **regional policy updates** and **postmortems**; users receive outdated guidance.
- Positive note: identity verification flow works reliably; no reported auth failures.

## Escalation Analysis

- 42% of escalations mention "need human confirmation of outage or maintenance".
- 25% cite "answer not grounded in policy" (often due to missing regional compliance content).
- 12% cite "response too slow"; correlated with vector search spikes during load testing.

## Action Items

- Add high-signal content: latest postmortems, regional compliance FAQs, and DR runbooks.
- Create style guide for Japanese honorific consistency; integrate as prompt instruction.
- Cache high-volume outage notices and maintenance calendar to reduce search load.
- Re-evaluate redirect thresholds: escalate after 2 uncertain answers instead of 3.

## Launch Implications

- Proceeding without new content will keep CSAT below target.
- Failover day communications must include up-to-date outage scripts and SG-specific disclaimers.
- Success metric for launch: CSAT >= 4.0 within 30 days after content refresh and style tuning.
