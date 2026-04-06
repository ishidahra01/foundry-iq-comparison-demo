# Exception Process

**Document ID:** EXC-PROC-2026-001
**Version:** 1.0
**Last Updated:** 2026-02-15
**Classification:** Internal
**Owner:** CTO Office / CISO Office

## 1. Overview

This document defines the process for requesting and approving exceptions to company policies, specifically:
- Security Policy (`03_security_policy.md`)
- Preview Feature Policy (`04_preview_feature_policy.md`)
- Architecture Standards
- Compliance Requirements

## 2. When to Request an Exception

Exceptions should be requested when:
- Policy compliance is not possible within project constraints
- Business value significantly outweighs policy risk
- Compensating controls can adequately mitigate risk
- Temporary deviation is necessary with a remediation plan

Exceptions should NOT be requested for:
- Convenience or ease of implementation
- Avoiding standard processes
- Permanent policy changes (use policy review process instead)

## 3. Exception Types

### 3.1 Type A: Security Policy Exception

**Examples:**
- Use of preview security features
- Temporary reduction in security controls
- Deviation from encryption standards
- Modified authentication requirements

**Approval Authority:** CISO (or designated security lead)
**Maximum Duration:** 90 days
**Review Frequency:** Monthly

### 3.2 Type B: Preview Feature Exception

**Examples:**
- Use of Azure preview services in production
- Beta API versions
- Experimental features

**Approval Authority:** CTO
**Maximum Duration:** 90 days or until GA (whichever comes first)
**Review Frequency:** Bi-weekly

### 3.3 Type C: Compliance Exception

**Examples:**
- Temporary data residency deviation
- Modified retention policies
- Adjusted audit requirements

**Approval Authority:** Chief Compliance Officer + Legal
**Maximum Duration:** 60 days
**Review Frequency:** Weekly

### 3.4 Type D: Budget Exception

**Examples:**
- Cost overruns
- Unplanned infrastructure expenses
- Emergency spending

**Approval Authority:** CFO (or VP for < $20,000)
**Maximum Duration:** Per project or fiscal quarter
**Review Frequency:** Monthly

## 4. Exception Request Process

### Step 1: Pre-Filing Assessment

Before filing formal exception request:
1. Consult with relevant policy owner
2. Explore alternative solutions
3. Assess feasibility of compensating controls
4. Estimate impact and cost

**Outcome:** Decision to proceed with formal request or find alternative

### Step 2: Exception Request Preparation

Required components:

#### Executive Summary (1 paragraph)
- What policy/requirement needs exception
- Why exception is necessary
- Proposed duration
- High-level risk assessment

#### Detailed Justification (1-2 pages)
- Business context and objectives
- Technical rationale
- Why policy compliance is not feasible
- Alternative solutions considered and rejected
- Timeline and urgency

#### Risk Assessment

**Risk Identification:**
- List all identified risks
- Probability (Low / Medium / High)
- Impact (Low / Medium / High)
- Overall risk score

**Risk Matrix:**
```
              Low Impact    Medium Impact    High Impact
High Prob     Medium        High             Critical
Medium Prob   Low           Medium           High
Low Prob      Low           Low              Medium
```

#### Compensating Controls
For each identified risk, describe:
- Proposed compensating control
- How it mitigates the risk
- Verification method
- Responsible party

#### Remediation Plan
- Path to policy compliance
- Timeline with milestones
- Resource requirements
- Success criteria

#### Impact Analysis
- Affected systems and users
- Blast radius if failure occurs
- Monitoring and detection capabilities
- Rollback procedures

### Step 3: Review and Approval

#### Review Timeline
- **Standard:** 10 business days
- **Expedited:** 3 business days (requires executive sponsor)
- **Emergency:** 24 hours (requires CTO/CISO approval)

#### Approval Workflow

**1. Initial Review** (2-3 days)
- Technical Lead: Technical feasibility
- Security Team: Security implications (if applicable)
- Finance: Budget impact (if applicable)

**2. Risk Assessment Review** (2-3 days)
- Policy owner evaluates risk assessment
- May request additional information or compensating controls

**3. Executive Approval** (3-5 days)
- CTO, CISO, or CFO (depending on exception type)
- May involve multiple approvers for complex cases

**4. Documentation and Notification** (1 day)
- Exception logged in tracking system
- Stakeholders notified
- Monitoring plan activated

#### Approval Decision Matrix

| Risk Score | Business Value | Compensating Controls | Decision |
|------------|----------------|-----------------------|----------|
| Low | Any | N/A | Likely Approve |
| Medium | High | Strong | Likely Approve |
| Medium | Medium | Strong | Case-by-case |
| Medium | Low | Strong | Likely Deny |
| High | Critical | Exceptional | Case-by-case |
| High | High | Partial | Likely Deny |
| Critical | Any | Any | Deny (policy change required) |

### Step 4: Exception Implementation

If approved:

**1. Exception Agreement**
- Signed by requestor and approver
- Includes all conditions and requirements
- Specifies review schedule and expiration

**2. Monitoring Setup**
- Define KPIs and metrics
- Configure alerts and dashboards
- Establish incident response procedures

**3. Communication**
- Notify relevant teams
- Update documentation
- Log in central exception register

**4. Periodic Review**
- Scheduled check-ins (frequency based on exception type)
- Status updates
- Verify compensating controls
- Adjust as needed

### Step 5: Exception Closure

Exception closes when:
- **Expired:** Maximum duration reached
- **Resolved:** Policy compliance achieved
- **Revoked:** Risk no longer acceptable
- **Superseded:** Policy changed

**Closure Process:**
1. Verify remediation completed (if applicable)
2. Conduct lessons learned session
3. Update exception log with outcome
4. Archive documentation

## 5. Exception Request Template

```markdown
# Exception Request: [Brief Title]

## 1. Executive Summary
[1 paragraph summary]

**Exception Type:** [Security / Preview Feature / Compliance / Budget]
**Requested Duration:** [X days/months]
**Overall Risk:** [Low / Medium / High / Critical]
**Business Impact if Denied:** [Brief description]

## 2. Requester Information
- **Name:** [Your name]
- **Role:** [Your role]
- **Team:** [Your team]
- **Project:** [Project name]
- **Date:** [YYYY-MM-DD]

## 3. Policy/Requirement Requiring Exception
**Policy Name:** [Policy name and section]
**Requirement:** [Specific requirement text]

## 4. Justification

### Business Context
[Why is this project important? What are the business objectives?]

### Technical Rationale
[Why is exception necessary from a technical perspective?]

### Why Policy Compliance Not Feasible
[Specific reasons policy cannot be met]

### Alternatives Considered
1. **Alternative 1:** [Description]
   - Why rejected: [Reason]

2. **Alternative 2:** [Description]
   - Why rejected: [Reason]

## 5. Risk Assessment

### Identified Risks

#### Risk 1: [Risk name]
- **Probability:** [Low / Medium / High]
- **Impact:** [Low / Medium / High]
- **Risk Score:** [Low / Medium / High / Critical]
- **Description:** [Detailed description]

#### Risk 2: [Risk name]
[Repeat for each risk]

### Overall Risk Rating
[Low / Medium / High / Critical]

## 6. Compensating Controls

### For Risk 1: [Risk name]
- **Control:** [Description of compensating control]
- **Mitigation:** [How it reduces the risk]
- **Verification:** [How to verify it's working]
- **Owner:** [Responsible person]

[Repeat for each risk]

## 7. Remediation Plan

### Path to Compliance
[How will we achieve policy compliance?]

### Timeline
- **Milestone 1:** [Description] - [Date]
- **Milestone 2:** [Description] - [Date]
- **Final Compliance:** [Date]

### Resource Requirements
[People, budget, tools needed]

### Success Criteria
[How will we know we're compliant?]

## 8. Impact Analysis

### Affected Systems
[List of systems affected]

### Affected Users
[Number and type of users affected]

### Blast Radius
[What happens if things go wrong?]

### Monitoring
[How will we monitor the exception?]

### Rollback Plan
[How to rollback if needed]

## 9. Review Schedule

**Proposed Review Frequency:** [Weekly / Bi-weekly / Monthly]
**Key Metrics to Track:** [List metrics]

## 10. Sign-off

**Requestor:**
- Name: [Name]
- Signature: _______________
- Date: _______________

**Technical Lead:**
- Name: [Name]
- Approval: [ ] Yes [ ] No
- Signature: _______________
- Date: _______________

**Policy Owner:**
- Name: [Name]
- Approval: [ ] Yes [ ] No
- Signature: _______________
- Date: _______________

**Approver (CTO/CISO/CFO/CCO):**
- Name: [Name]
- Approval: [ ] Yes [ ] No [ ] Conditional
- Conditions (if applicable): [Description]
- Signature: _______________
- Date: _______________
```

## 6. Active Exceptions Register

(See separate secure document for active exceptions)

**Public Summary:**
- Total Active Exceptions: [Count updated monthly]
- By Type: Security (X), Preview Feature (Y), Compliance (Z), Budget (W)
- Average Duration: [X days]
- On-time Closure Rate: [X%]

## 7. Exception Metrics and Reporting

### Key Metrics

**Volume Metrics:**
- Exceptions requested per quarter
- Approval rate
- Denial rate
- Average review time

**Quality Metrics:**
- On-time closure rate
- Extensions requested
- Incidents related to exceptions
- Revocations due to risk

**Risk Metrics:**
- Distribution by risk level
- Average risk score
- Incidents caused by exceptions

### Reporting Cadence

**Monthly:**
- Exception summary report to CTO, CISO, CFO
- Trend analysis
- Aging report (exceptions > 60 days)

**Quarterly:**
- Board-level summary
- Policy effectiveness review
- Process improvement recommendations

## 8. Example Decisions

### Example 1: GPT-4 Turbo Preview Exception Request - DENIED

**Request Date:** March 5, 2026
**Requestor:** AI Platform Team
**Type:** Preview Feature Exception

**Summary:**
Team requested exception to use GPT-4 Turbo (preview) instead of GPT-4 (GA) for customer support chatbot.

**Justification:**
- Claimed 2x faster responses
- 15% cost savings
- Better reasoning

**Risk Assessment:**
- Overall Risk: Medium
- Main concerns: No production SLA, potential breaking changes

**Decision:** DENIED

**Rationale:**
1. GPT-4 (GA) meets all functional requirements
2. Performance claims not validated with production data
3. Cost savings marginal (~$2,000/month)
4. GPT-4 Turbo expected GA in Q2 2026
5. Launch timeline (April 30) allows waiting for GA

**Alternative:** Use GPT-4 (GA), re-evaluate GPT-4 Turbo after GA release

**Lessons Learned:**
- Quantify performance claims before requesting exception
- Cost savings alone insufficient for preview feature approval
- Wait for GA when timeline permits

### Example 2: Semantic Ranker Preview Exception - APPROVED (then CLOSED)

**Request Date:** January 15, 2026
**Requestor:** Search Platform Team
**Type:** Preview Feature Exception
**Status:** Closed (feature reached GA)

**Summary:**
Team requested exception to use Azure AI Search Semantic Ranker (preview) for improved search relevance.

**Justification:**
- Significant improvement in search quality (30% better relevance)
- No GA alternative with comparable quality
- Microsoft indicated GA expected Q1 2026

**Risk Assessment:**
- Overall Risk: Medium-Low
- Compensating Controls: Fallback to keyword search, isolated feature

**Decision:** APPROVED (with conditions)

**Conditions:**
1. Implement fallback to keyword search
2. Monitor Microsoft's GA roadmap weekly
3. Migrate to GA version within 30 days of release
4. Monthly risk review

**Outcome:**
- Feature reached GA on February 1, 2026
- Migration completed February 15, 2026
- Exception closed successfully

**Lessons Learned:**
- Preview exceptions acceptable when:
  - No GA alternative
  - Clear path to GA
  - Strong compensating controls

### Example 3: PII Redaction Delay Exception - APPROVED (current)

**Request Date:** March 28, 2026
**Requestor:** Backend Team
**Type:** Security Policy Exception
**Status:** Active

**Summary:**
PII redaction in logs not completed by target date (April 8). Requesting 14-day extension to April 22.

**Justification:**
- Implementation more complex than estimated
- Requires ML-based detection, not just regex
- Alternative: Delay launch by 2 weeks

**Risk Assessment:**
- Overall Risk: Medium
- Impact: Potential GDPR violation if breach occurs

**Compensating Controls:**
1. Restrict log access to security-cleared personnel only
2. Automated alerts on PII patterns in logs
3. Manual log review and redaction for any security incidents
4. Accelerated implementation schedule

**Decision:** APPROVED (conditional)

**Conditions:**
1. Daily progress updates to CISO
2. Interim manual redaction process for any incidents
3. No extension beyond April 22 (hard deadline)
4. Launch delayed if not ready by April 22

**Review Schedule:** Daily

**Status:** In progress, on track for April 15 completion (1 week early)

## 9. Frequently Asked Questions

**Q: How long does exception approval take?**
A: Standard: 10 business days. Expedited: 3 business days (requires sponsor). Emergency: 24 hours (CTO/CISO).

**Q: Can I implement before approval?**
A: No. Implementation before approval is policy violation.

**Q: What if my exception is denied?**
A: You can: (1) Revise and resubmit, (2) Escalate to next level, or (3) Find alternative solution.

**Q: Can exceptions be extended?**
A: Yes, but requires new approval with updated risk assessment. Maximum 2 extensions typically allowed.

**Q: What happens if I violate a policy without exception?**
A: Depends on severity. May range from incident investigation to disciplinary action. Always file exception request if needed.

**Q: Who can request an exception?**
A: Anyone, but request must be endorsed by team lead and relevant stakeholders.

## 10. Contact Information

**Exception Process Questions:**
- Email: engineering-governance@company.com
- Slack: #policy-exceptions

**Policy Owners:**
- Security Policy: CISO Office
- Preview Features: CTO Office
- Compliance: Chief Compliance Officer
- Budget: CFO Office

**Emergency Approval:**
- CTO Emergency Line: [phone]
- CISO Emergency Line: [phone]

## Document History

- 2026-02-15: Version 1.0 - Initial document
