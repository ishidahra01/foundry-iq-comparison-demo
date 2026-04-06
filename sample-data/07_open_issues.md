# Open Issues Tracker

**Document ID:** ISSUES-2026-001
**Last Updated:** 2026-03-28
**Classification:** Internal
**Owner:** Technical Lead

## Active Issues

### Issue #1: PII Redaction in Application Logs [HIGH]

**Status:** 🔴 Open
**Priority:** High
**Created:** 2026-03-15
**Target Resolution:** April 8, 2026
**Owner:** Backend Team

**Description:**
Customer personally identifiable information (PII) is currently being logged in plain text in Application Insights logs. This violates our security policy requirement for PII redaction.

**Impact:**
- Security policy non-compliance
- Potential GDPR violation
- Blocker for production launch approval

**Root Cause:**
- Automatic logging of request/response bodies
- No PII detection middleware implemented

**Current Status:**
- Solution designed (middleware-based redaction)
- Implementation in progress (60% complete)
- Testing planned for April 6-7

**Resolution Plan:**
1. Implement PII detection middleware (regex + ML-based)
2. Configure Application Insights with custom sanitization
3. Audit existing logs and purge if necessary
4. Add automated tests for PII redaction

**Dependencies:**
- None

**Risks:**
- Could delay launch if not completed by April 8
- May impact debugging capabilities (trade-off)

**Discussion:**
- Engineering team: Proposing allowlist approach for specific log entries
- Security team: Requiring opt-in explicit logging only
- **Decision needed:** Balance between security and observability

---

### Issue #2: Rate Limiting Configuration Not Finalized [HIGH]

**Status:** 🔴 Open
**Priority:** High
**Created:** 2026-03-10
**Target Resolution:** April 5, 2026
**Owner:** Platform Team

**Description:**
Rate limiting strategy defined but not fully configured in production environment. Current limits are development-level only.

**Impact:**
- Cost overrun risk (unconstrained usage)
- Abuse vulnerability
- Security policy non-compliance

**Current Status:**
- Rate limits defined in spec
- Azure API Management not yet configured
- Application-level limits not implemented

**Resolution Plan:**
1. Configure APIM rate limiting policies
2. Implement application-level circuit breakers
3. Create monitoring dashboard for rate limit hits
4. Document user-facing error messages

**Rate Limit Specification:**
- Per user: 100 requests/hour
- Per IP: 200 requests/hour
- System-wide: 120K TPM (hard limit via Azure OpenAI quota)
- Burst allowance: 20 requests in 1 minute

**Dependencies:**
- APIM instance provisioning (in progress)

**Risks:**
- User experience impact if limits too aggressive
- Cost impact if limits too lenient

---

### Issue #3: Disaster Recovery Drill Failed [MEDIUM]

**Status:** ⚠️ In Progress
**Priority:** Medium
**Created:** 2026-03-22
**Target Resolution:** April 7, 2026
**Owner:** DevOps Team

**Description:**
Initial disaster recovery drill on March 21 did not complete successfully. Failover to secondary region took 45 minutes instead of target 15 minutes.

**Impact:**
- Does not meet business continuity requirements
- Increased downtime risk
- Confidence issue for stakeholders

**Root Cause Analysis:**
- Manual steps not documented in runbook
- DNS propagation delay not accounted for
- Database replication lag (5 minutes)
- Missing automation scripts

**Current Status:**
- Runbook updated with detailed steps
- Automation scripts created for DNS update
- Second drill scheduled for April 6

**Resolution Plan:**
1. Complete runbook automation
2. Pre-configure DNS records with lower TTL
3. Re-run disaster recovery drill
4. Document lessons learned

**Dependencies:**
- Azure DNS configuration changes (requires approval)

**Metrics:**
- Target RTO: 15 minutes
- Target RPO: 5 minutes
- Current actual: 45 minutes RTO, 5 minutes RPO

---

### Issue #4: Multi-Factor Authentication Not Enforced for Admins [MEDIUM]

**Status:** ⚠️ In Progress
**Priority:** Medium
**Created:** 2026-03-18
**Target Resolution:** April 10, 2026
**Owner:** Identity Team

**Description:**
MFA is configured but not enforced for admin accounts accessing production environment.

**Impact:**
- Security policy non-compliance
- Elevated risk of account compromise
- Audit finding

**Current Status:**
- Azure AD conditional access policy created
- Testing in progress with staging environment
- Rollout planned for April 8

**Resolution Plan:**
1. Test MFA enforcement in staging (April 5-6)
2. Communicate to admin users (April 7)
3. Enable enforcement in production (April 8)
4. Monitor for any access issues

**User Impact:**
- ~15 admin users need to enroll in MFA
- Minor inconvenience during initial setup

**Dependencies:**
- None

---

### Issue #5: Integration Test Coverage Gap [MEDIUM]

**Status:** ⚠️ In Progress
**Priority:** Medium
**Created:** 2026-03-12
**Target Resolution:** April 9, 2026
**Owner:** QA Team

**Description:**
End-to-end integration tests cover only 65% of critical user flows. Target is 90% coverage.

**Impact:**
- Risk of undetected integration bugs
- Lower confidence in production readiness
- Potential quality issues at launch

**Gap Analysis:**
- ✅ Basic conversation flow: Covered
- ✅ Authentication flow: Covered
- ⚠️ Error handling: Partial coverage (40%)
- ⚠️ Edge cases: Partial coverage (30%)
- ❌ Concurrent user scenarios: Not covered
- ❌ Rate limiting behavior: Not covered

**Current Status:**
- Additional test scenarios identified
- Test automation in progress
- Target: 85% coverage by April 9 (revised from 90%)

**Resolution Plan:**
1. Prioritize P0/P1 scenarios (covers 85%)
2. Automated test development (April 5-8)
3. Execute full test suite (April 9)
4. Defer P2 scenarios to post-launch

**Dependencies:**
- Test environment stability (currently stable)

---

### Issue #6: SIEM Integration Not Completed [LOW]

**Status:** 🔵 Open
**Priority:** Low
**Created:** 2026-02-28
**Target Resolution:** May 15, 2026 (Post-launch)
**Owner:** Security Operations

**Description:**
Application Insights logs not yet integrated with corporate SIEM system (Splunk).

**Impact:**
- Delayed security event detection
- Manual log review required
- Non-compliance with logging policy (waiver obtained)

**Current Status:**
- Integration design approved
- Not started (deprioritized for launch)
- Waiver approved until May 31

**Resolution Plan:**
- Post-launch priority
- Estimated 2 weeks effort
- Target: May 15 completion

**Workaround:**
- Security team has direct access to Application Insights
- Critical alerts forwarded via email/Teams

**Dependencies:**
- SIEM team bandwidth (Q2 backlog)

---

## Resolved Issues

### Issue #7: Load Testing Revealed Performance Bottleneck [RESOLVED]

**Status:** ✅ Resolved
**Priority:** High
**Resolution Date:** 2026-03-18
**Owner:** Backend Team

**Description:**
Load testing at 5,000 concurrent users showed response time degradation (p95 = 8 seconds).

**Resolution:**
- Upgraded Azure Functions to Premium EP1 plan
- Implemented connection pooling
- Optimized database queries
- Added caching layer

**Verification:**
- Re-tested at 10,000 concurrent users
- p95 response time: 2.1 seconds ✅
- p99 response time: 3.8 seconds ✅

---

### Issue #8: Japanese Tokenization Issues [RESOLVED]

**Status:** ✅ Resolved
**Priority:** Medium
**Resolution Date:** 2026-03-20
**Owner:** AI/ML Team

**Description:**
GPT-4 tokenization inefficient for Japanese text, resulting in higher than expected token costs.

**Resolution:**
- Optimized prompts to reduce token usage
- Implemented prompt caching for common patterns
- Added preprocessing to remove unnecessary formatting

**Impact:**
- Token usage reduced by 18% for Japanese text
- Cost savings: ~$2,000/month

---

### Issue #9: Content Filter False Positives [RESOLVED]

**Status:** ✅ Resolved
**Priority:** High
**Resolution Date:** 2026-03-08
**Owner:** AI/ML Team

**Description:**
Azure AI Content Safety blocking legitimate customer support queries (false positive rate 8%).

**Resolution:**
- Adjusted severity thresholds (Medium → Medium-High)
- Added custom allowlist for industry terms
- Implemented appeal mechanism for blocked content

**Verification:**
- False positive rate reduced to < 1%
- Zero false negatives in test dataset

---

## Issue Metrics

### By Status
- 🔴 Open: 2
- ⚠️ In Progress: 3
- 🔵 Deferred: 1
- ✅ Resolved: 3

### By Priority
- High: 2 open, 2 resolved
- Medium: 3 in progress, 1 resolved
- Low: 1 deferred

### Aging Report
- > 14 days: 3 issues
- 7-14 days: 4 issues
- < 7 days: 2 issues

### Burndown
- Week of Mar 11: 8 open issues
- Week of Mar 18: 7 open issues
- Week of Mar 25: 6 open issues
- Target Apr 8: 2 open issues (acceptable for launch)

## Launch Blockers Assessment

### Critical Blockers (Must Fix Before Launch)
1. ✅ ~~Load testing performance~~ → RESOLVED
2. ✅ ~~Content filter false positives~~ → RESOLVED
3. ⏳ PII redaction in logs → **IN PROGRESS** (due Apr 8)
4. ⏳ Rate limiting configuration → **IN PROGRESS** (due Apr 5)

### Non-Critical (Can Launch With Workarounds)
1. ⚠️ Disaster recovery RTO (workaround: accept 45min RTO initially)
2. ⚠️ MFA enforcement (workaround: monitoring + enforcement post-launch)
3. ⚠️ Integration test coverage (workaround: 85% vs 90% target acceptable)
4. ✅ SIEM integration (workaround: direct log access, waiver approved)

### Assessment Summary
**Current launch readiness: 🟡 YELLOW (Conditional Go)**

- 2 critical blockers in progress, both on track for resolution
- 4 non-critical issues with acceptable workarounds
- No showstopper issues currently identified

**Recommendation:**
- Proceed with launch preparation
- Daily check-ins on Issues #1 and #2
- Re-assess on April 8 for final Go/No-Go decision

## Issue Review Cadence

### Daily Stand-up (During Launch Prep)
- Review P0/P1 issues
- Update status
- Identify new blockers

### Weekly Issue Review
- Full issue backlog review
- Prioritization adjustments
- Stakeholder communication

### Post-Launch
- Reduce to weekly cadence
- Focus on technical debt and optimizations

## Contact Information

**Issue Triage:**
- Slack: #launch-issues
- Email: launch-team@company.com
- War Room: Daily 9:00 AM JST

**Escalation:**
- Technical Lead (immediate issues)
- Product Manager (priority decisions)
- CTO (launch blockers)

## Document History

- 2026-03-15: Initial issue tracker created
- 2026-03-22: Added DR drill failure
- 2026-03-28: Updated status and metrics
