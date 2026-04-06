# Preview Feature Policy

**Document ID:** PREVIEW-POL-2026-001
**Version:** 1.3
**Last Updated:** 2026-02-28
**Classification:** Internal Use Only
**Owner:** Chief Technology Officer

## 1. Policy Statement

**Azure preview, beta, or experimental features are PROHIBITED in production environments unless explicitly approved through the exception process defined in this document.**

## 2. Purpose

This policy ensures:
- Production stability and reliability
- Predictable support and SLA guarantees
- Compliance with enterprise standards
- Risk management for customer-facing systems

## 3. Scope

This policy applies to:
- All Azure services marked as "Preview", "Beta", or "Experimental"
- Features with limited regional availability
- Services without production SLA
- Any feature marked "subject to change" in official documentation

## 4. Definitions

### 4.1 Preview Service
Any Azure service or feature that:
- Is marked as "Preview" in Azure Portal or documentation
- Lacks production SLA guarantees
- Has "(Preview)" or "(Beta)" in its name
- Is documented as "experimental" or "not recommended for production"

### 4.2 General Availability (GA)
- Service has production SLA
- Full support from Azure support team
- Stable API with backwards compatibility guarantees
- Available in target deployment regions

### 4.3 Production Environment
Any environment serving:
- External customers
- Revenue-generating workloads
- Business-critical operations
- Compliance-regulated data

## 5. Prohibited Preview Features (Examples)

The following are explicitly PROHIBITED without exception approval:

### 5.1 AI/ML Services
- Azure OpenAI Service models marked as preview
- Azure AI Search preview features
- Experimental model versions
- Preview API versions

### 5.2 Data Services
- Cosmos DB preview features
- SQL Database preview tiers or features
- Storage account preview capabilities

### 5.3 Compute Services
- Azure Functions preview runtimes
- Container Apps preview features
- AKS preview features

## 6. Exception Process

### 6.1 When Exception May Be Granted

Exceptions may be considered only when:
- Clear business value with quantified impact
- No GA alternative available
- Acceptable risk mitigation in place
- Limited blast radius (isolated feature)
- Rollback plan documented
- Microsoft confirms preview stability

### 6.2 Exception Request Process

#### Step 1: Initial Assessment
Team Lead assesses:
- Business justification
- Technical alternatives
- Risk evaluation
- Timeline and urgency

#### Step 2: Documentation Preparation
Prepare exception request with:
- Executive summary (1 page)
- Technical justification
- Risk assessment and mitigation
- Rollback and contingency plan
- Impact analysis
- Support plan

#### Step 3: Review and Approval

**Required Approvals:**
1. **Technical Lead** - Technical feasibility
2. **Product Manager** - Business justification
3. **Security Team** - Security implications
4. **CTO** - Final approval

**Review Timeline:**
- Standard: 10 business days
- Expedited: 3 business days (requires VP sponsorship)

#### Step 4: Implementation Requirements

If approved, implementation must include:
- Monitoring and alerting specific to preview feature
- Daily health checks
- Incident response plan
- Regular check-ins with Microsoft support
- Documentation updates

#### Step 5: Exception Review

- Monthly status review required
- Exception automatically expires after 90 days unless renewed
- Transition to GA version within 30 days of GA release

### 6.3 Exception Request Template

```
Preview Feature Exception Request

1. Feature Name:
   [Name of preview service/feature]

2. Business Justification:
   [Why is this feature critical? What problem does it solve?]

3. Alternative Analysis:
   [What GA alternatives were considered? Why are they insufficient?]

4. Risk Assessment:
   [What are the risks? Probability and impact analysis.]

5. Mitigation Strategy:
   [How will risks be mitigated? Monitoring, fallbacks, etc.]

6. Rollback Plan:
   [How quickly can we rollback? What's the procedure?]

7. Support Plan:
   [How will we handle issues? Escalation path?]

8. Timeline:
   [How long do we need the exception? When does feature reach GA?]

9. Blast Radius:
   [What systems/users are affected? How isolated is this feature?]

10. Success Criteria:
    [How will we measure if this preview feature is working?]

Prepared by: [Name, Role]
Date: [Date]
```

## 7. Recent Exception Requests

### 7.1 GPT-4 Turbo (DENIED)

**Request Date:** 2026-03-05
**Requestor:** AI Platform Team
**Status:** DENIED
**Decision Date:** 2026-03-08

**Justification Provided:**
- Faster response times (claimed 2x improvement)
- Lower token costs
- Better reasoning for complex queries

**Denial Reasons:**
1. GPT-4 (GA) already approved and deployed
2. Performance improvement not quantified with production data
3. Cost savings marginal (~15% estimated)
4. GPT-4 Turbo expected GA in Q2 2026
5. Launch timeline does not justify preview risk

**Alternative Approved:**
Continue with GPT-4 (GA) version 0613. Re-evaluate GPT-4 Turbo after GA release.

**Lessons Learned:**
- Performance claims must be validated with production-like testing
- Cost savings alone insufficient justification
- Wait for GA when launch timeline permits

### 7.2 Azure AI Search Semantic Ranker (APPROVED with conditions)

**Request Date:** 2026-01-15
**Requestor:** Search Platform Team
**Status:** APPROVED (with conditions)
**Approval Date:** 2026-01-22

**Note:** Semantic Ranker reached GA on 2026-02-01. Exception no longer needed.

## 8. Monitoring and Compliance

### 8.1 Automated Detection
- Azure Policy configured to alert on preview resource deployment
- Monthly scan of all production resources
- Automated compliance reports to CTO

### 8.2 Violations
Discovery of unauthorized preview features results in:
1. Immediate notification to CTO and CISO
2. Mandatory risk assessment
3. Expedited remediation or exception request
4. Incident review and lessons learned

## 9. Preview Feature Evaluation

### 9.1 Development and Testing
Preview features **MAY** be used in:
- Development environments
- Testing environments
- Internal demo environments
- Proof-of-concept projects

### 9.2 Best Practices for Evaluation
When evaluating preview features in non-production:
- Document findings and limitations
- Test edge cases and failure scenarios
- Establish baseline metrics
- Prepare GA migration plan
- Share learnings with engineering team

## 10. GA Transition Process

When a preview feature reaches GA:
1. Review existing implementations
2. Update to GA version within 30 days
3. Validate functionality post-upgrade
4. Update documentation
5. Close any open exceptions

## 11. Frequently Asked Questions

### Q: Can I use a preview feature if it's the only option?
**A:** You must go through the exception process. Consider if the feature is truly required or if launch can wait for GA.

### Q: What if Microsoft recommends a preview feature?
**A:** Microsoft recommendations don't override our policy. Submit exception request with Microsoft's recommendation as supporting evidence.

### Q: Can I use a preview API version if the service is GA?
**A:** No. Preview API versions are subject to this policy even if the underlying service is GA.

### Q: What about features in "public preview" vs "private preview"?
**A:** Both are subject to this policy. Public preview may have slightly lower risk but still requires exception approval.

### Q: How do I check if a feature is preview or GA?
**A:** Check:
1. Azure Portal (look for "Preview" label)
2. Official Azure documentation
3. Azure Service Health dashboard
4. SLA documentation (no SLA = preview)

## 12. Related Policies

- Security Policy: `03_security_policy.md`
- Exception Process: `08_exception_process.md`
- Architecture Decision Records: `02_architecture_decision.md`

## 13. Contact Information

- **Policy Owner:** CTO Office - cto@company.com
- **Exception Requests:** engineering-governance@company.com
- **Questions:** Ask in #engineering-policy Slack channel

## Document History

- 2025-08-01: Version 1.0 - Initial policy
- 2025-11-15: Version 1.1 - Added exception process details
- 2026-01-30: Version 1.2 - Added recent exception examples
- 2026-02-28: Version 1.3 - Updated with GPT-4 Turbo denial case study
