"""
Mock response generator for local testing without Azure connectivity
"""

import asyncio
import random
from typing import AsyncIterator
from datetime import datetime, timedelta
from models import AgentResult, TraceEvent, Citation, Metrics


class MockResponseGenerator:
    """Generate realistic mock responses for agent comparison testing"""

    def __init__(self):
        self.base_time = datetime.utcnow()

    def generate_response(
        self,
        agent_type: str,
        question: str,
        run_id: str
    ) -> AgentResult:
        """Generate a complete mock agent response"""

        if agent_type == "classic-rag":
            return self._generate_classic_rag_response(question, run_id)
        else:
            return self._generate_foundry_iq_response(question, run_id)

    async def generate_streaming_response(
        self,
        agent_type: str,
        question: str,
        run_id: str
    ) -> AsyncIterator[TraceEvent]:
        """Generate streaming mock trace events"""

        if agent_type == "classic-rag":
            async for event in self._generate_classic_rag_events(question, run_id):
                yield event
        else:
            async for event in self._generate_foundry_iq_events(question, run_id):
                yield event

    def _generate_classic_rag_response(
        self,
        question: str,
        run_id: str
    ) -> AgentResult:
        """Generate Classic RAG mock response"""

        answer = """Based on the project documentation, here is what I found:

The AI customer support feature is planned for launch on April 30, 2026 in the Japan region. The project uses Azure OpenAI Service with GPT-4 and Azure AI Search for the knowledge base.

Current status shows most items are completed, including core development, authentication, and basic testing. However, there are some pending items including security assessment and penetration testing.

The monthly budget is $25,000 but current estimates show $27,400/month, which is approximately 9.6% over budget. Cost optimization strategies have been proposed.

The rollout plan includes multiple phases: Internal Beta, Limited Beta, Soft Launch, and General Availability. Some technical details and open issues are mentioned in the documentation."""

        citations = [
            Citation(
                document="01_project_overview.md",
                relevance_score=0.85,
                content="Production Launch: April 30, 2026"
            ),
            Citation(
                document="05_budget_guardrail.md",
                relevance_score=0.78,
                content="Total OpEx/month: $25,000 budgeted, $27,400 estimated"
            ),
            Citation(
                document="06_rollout_plan.md",
                relevance_score=0.72,
                content="Phase 4: General Availability (April 30)"
            )
        ]

        trace_events = [
            TraceEvent(
                timestamp=self._timestamp(0),
                event_type="retrieval_started",
                status="completed",
                elapsed_ms=50,
                mode="classic-rag",
                metadata={"query": question}
            ),
            TraceEvent(
                timestamp=self._timestamp(150),
                event_type="retrieval_completed",
                status="completed",
                elapsed_ms=150,
                mode="classic-rag",
                metadata={
                    "retrieved_count": 12,
                    "top_sources": ["01_project_overview.md", "05_budget_guardrail.md"]
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(200),
                event_type="answer_synthesis_started",
                status="completed",
                elapsed_ms=50,
                mode="classic-rag",
                metadata={}
            ),
            TraceEvent(
                timestamp=self._timestamp(1200),
                event_type="answer_completed",
                status="completed",
                elapsed_ms=1000,
                mode="classic-rag",
                metadata={"answer_length": len(answer)}
            )
        ]

        return AgentResult(
            agent_type="classic-rag",
            agent_name="classic-rag-agent",
            answer=answer,
            verdict="Conditional",
            citations=citations,
            trace_events=trace_events,
            metrics=Metrics(
                total_time_ms=1250,
                token_usage={"input": 850, "output": 420},
                retrieval_count=12,
                subquery_count=1,
                tool_calls=1
            ),
            sources_used=[
                "01_project_overview.md",
                "05_budget_guardrail.md",
                "06_rollout_plan.md"
            ]
        )

    def _generate_foundry_iq_response(
        self,
        question: str,
        run_id: str
    ) -> AgentResult:
        """Generate Foundry IQ mock response (more comprehensive)"""

        answer = """**Launch Decision: CONDITIONAL GO with Critical Blockers**

**Overall Assessment:**
Based on comprehensive analysis across project documentation, internal policies, budget constraints, and current implementation status, I recommend a **Conditional Go** for the April 30, 2026 launch, contingent on resolving two critical blockers.

**Critical Blockers (Must Resolve Before Launch):**

1. **Security Assessment Timeline Conflict** 🔴
   - Security assessment scheduled April 10-15 conflicts with Internal Beta start date (also April 10)
   - Impact: Cannot proceed with Internal Beta without security sign-off
   - Resolution Options: (A) Delay Phase 1 to April 16, (B) Expedite assessment to April 6-9
   - Decision deadline: April 2, 2026

2. **PII Redaction Not Implemented** 🔴
   - Customer PII currently logged in plain text in Application Insights
   - Violation of security policy requirement
   - Status: Implementation 60% complete, testing April 6-7
   - Target resolution: April 8, 2026

**Budget Status:** ⚠️ OVER BUDGET
- Allocated: $25,000/month
- Current estimate: $27,400/month (+9.6% overrun)
- Primary driver: Azure OpenAI costs ($18,000/month vs $15,000 budgeted)
- Mitigation: Cost optimization plan approved, expected savings $5,400/month
- Finance approval: Conditional (requires optimization implementation by May 31)

**Policy Compliance:**
- ✅ Preview Feature Policy: COMPLIANT - Using GPT-4 (GA version)
  - Note: GPT-4 Turbo exception request was DENIED on March 8, 2026
- ⏳ Security Policy: PARTIAL - 2 critical items pending (PII redaction, rate limiting)
- ⏳ Compliance Requirements: Under review

**Open Issues Summary:**
- 🔴 Critical: 2 blockers (PII redaction, rate limiting configuration)
- ⚠️ High Priority: 3 issues in progress (DR drill failure, MFA enforcement, test coverage)
- Current status: **🟡 YELLOW (Conditional Go)**

**Key Dependencies:**
The security assessment completion is a dependency for starting Internal Beta. The rollout plan shows Internal Beta must complete successfully before proceeding to Limited Beta (April 16-22), which must complete before Soft Launch (April 23-28), culminating in GA on April 30.

**Recommendation:**
**CONDITIONAL GO** - Approve launch preparation to continue, subject to:
1. Resolution of both critical blockers by April 8
2. Successful security assessment by April 15
3. Daily status reviews until blockers cleared
4. Re-assess on April 8 for final Go/No-Go decision

**Next Actions:**
1. **Immediate (by April 2):** Decide on security assessment timeline conflict resolution
2. **By April 5:** Complete rate limiting configuration
3. **By April 8:** Complete PII redaction implementation
4. **By April 15:** Complete security assessment with no critical findings
5. **April 8:** Final Go/No-Go decision point"""

        citations = [
            Citation(
                document="03_security_policy.md",
                chunk="Section 7.2 - Current Status",
                relevance_score=0.95,
                content="Blocking Items: Security assessment not completed, PII redaction in logs not implemented"
            ),
            Citation(
                document="06_rollout_plan.md",
                chunk="Phase 1: Internal Beta",
                relevance_score=0.93,
                content="🔴 BLOCKER: Security assessment timeline conflict - scheduled April 10-15, conflicting with Internal Beta"
            ),
            Citation(
                document="05_budget_guardrail.md",
                chunk="Section 2.2 - OpEx Monthly",
                relevance_score=0.91,
                content="Total OpEx/month: $25,000 budgeted, $27,400 current estimate, +$2,400 variance (🔴 9.6% over)"
            ),
            Citation(
                document="04_preview_feature_policy.md",
                chunk="Section 7.1 - GPT-4 Turbo (DENIED)",
                relevance_score=0.88,
                content="Request Date: 2026-03-05, Status: DENIED. Alternative Approved: GPT-4 (GA) version 0613"
            ),
            Citation(
                document="07_open_issues.md",
                chunk="Issue #1: PII Redaction",
                relevance_score=0.90,
                content="Status: Open, Priority: High, Target Resolution: April 8, Current Status: 60% complete"
            ),
            Citation(
                document="07_open_issues.md",
                chunk="Launch Blockers Assessment",
                relevance_score=0.89,
                content="Current launch readiness: 🟡 YELLOW (Conditional Go). 2 critical blockers in progress"
            ),
            Citation(
                document="02_architecture_decision.md",
                chunk="ADR-001: Azure OpenAI Service Selection",
                relevance_score=0.75,
                content="Model: gpt-4 (version: 0613), Deployment: Japan East region, Capacity: 120K TPM"
            )
        ]

        trace_events = [
            TraceEvent(
                timestamp=self._timestamp(0),
                event_type="task_hypothesis_generated",
                status="completed",
                elapsed_ms=100,
                mode="foundry-iq",
                metadata={
                    "hypothesis": "Need to analyze launch readiness across multiple dimensions: security, budget, policy compliance, and open issues"
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(120),
                event_type="retrieval_started",
                status="completed",
                elapsed_ms=20,
                mode="foundry-iq",
                metadata={
                    "planned_queries": [
                        "Security blockers and assessment status",
                        "Budget constraints and current spending",
                        "Preview feature policy compliance",
                        "Critical open issues affecting launch",
                        "Rollout timeline and dependencies"
                    ]
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(350),
                event_type="retrieval_completed",
                status="completed",
                elapsed_ms=230,
                mode="foundry-iq",
                metadata={
                    "subqueries_executed": 5,
                    "total_results": 28,
                    "sources": ["03_security_policy.md", "06_rollout_plan.md", "05_budget_guardrail.md", "04_preview_feature_policy.md", "07_open_issues.md"]
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(380),
                event_type="tool_call_started",
                status="completed",
                elapsed_ms=30,
                mode="foundry-iq",
                metadata={
                    "tool_name": "foundry_iq_knowledge_base",
                    "query": "PII redaction implementation status"
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(620),
                event_type="tool_call_completed",
                status="completed",
                elapsed_ms=240,
                mode="foundry-iq",
                metadata={
                    "tool_name": "foundry_iq_knowledge_base",
                    "result_count": 3
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(650),
                event_type="answer_synthesis_started",
                status="completed",
                elapsed_ms=30,
                mode="foundry-iq",
                metadata={
                    "synthesis_approach": "Multi-dimensional analysis with risk prioritization"
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(2800),
                event_type="answer_completed",
                status="completed",
                elapsed_ms=2150,
                mode="foundry-iq",
                metadata={"answer_length": len(answer), "verdict": "Conditional"}
            )
        ]

        return AgentResult(
            agent_type="foundry-iq",
            agent_name="foundry-iq-agent",
            answer=answer,
            verdict="Conditional",
            citations=citations,
            trace_events=trace_events,
            metrics=Metrics(
                total_time_ms=2850,
                token_usage={"input": 2450, "output": 920},
                retrieval_count=28,
                subquery_count=5,
                tool_calls=3
            ),
            sources_used=[
                "03_security_policy.md",
                "06_rollout_plan.md",
                "05_budget_guardrail.md",
                "04_preview_feature_policy.md",
                "07_open_issues.md",
                "02_architecture_decision.md",
                "01_project_overview.md"
            ],
            query_plan={
                "original_query": question,
                "decomposed_queries": [
                    "What are the security blockers?",
                    "Is the budget approved?",
                    "Are we using any preview features?",
                    "What critical issues are open?",
                    "What are the timeline dependencies?"
                ],
                "retrieval_strategy": "multi-step_with_synthesis"
            }
        )

    async def _generate_classic_rag_events(
        self,
        question: str,
        run_id: str
    ) -> AsyncIterator[TraceEvent]:
        """Generate streaming events for Classic RAG"""

        events = [
            (0.1, TraceEvent(
                timestamp=self._timestamp(0),
                event_type="retrieval_started",
                status="running",
                mode="classic-rag",
                metadata={"query": question}
            )),
            (0.3, TraceEvent(
                timestamp=self._timestamp(150),
                event_type="retrieval_completed",
                status="completed",
                elapsed_ms=150,
                mode="classic-rag",
                metadata={"retrieved_count": 12}
            )),
            (0.2, TraceEvent(
                timestamp=self._timestamp(200),
                event_type="answer_synthesis_started",
                status="running",
                mode="classic-rag",
                metadata={}
            )),
            (0.8, TraceEvent(
                timestamp=self._timestamp(1200),
                event_type="answer_completed",
                status="completed",
                elapsed_ms=1000,
                mode="classic-rag",
                metadata={}
            ))
        ]

        for delay, event in events:
            await asyncio.sleep(delay)
            yield event

    async def _generate_foundry_iq_events(
        self,
        question: str,
        run_id: str
    ) -> AsyncIterator[TraceEvent]:
        """Generate streaming events for Foundry IQ (more complex)"""

        events = [
            (0.1, TraceEvent(
                timestamp=self._timestamp(0),
                event_type="task_hypothesis_generated",
                status="completed",
                elapsed_ms=100,
                mode="foundry-iq",
                metadata={"hypothesis": "Multi-dimensional launch analysis required"}
            )),
            (0.1, TraceEvent(
                timestamp=self._timestamp(120),
                event_type="retrieval_started",
                status="running",
                mode="foundry-iq",
                metadata={"planned_queries": 5}
            )),
            (0.4, TraceEvent(
                timestamp=self._timestamp(350),
                event_type="retrieval_completed",
                status="completed",
                elapsed_ms=230,
                mode="foundry-iq",
                metadata={"subqueries_executed": 5, "total_results": 28}
            )),
            (0.1, TraceEvent(
                timestamp=self._timestamp(380),
                event_type="tool_call_started",
                status="running",
                mode="foundry-iq",
                metadata={"tool_name": "foundry_iq_knowledge_base"}
            )),
            (0.3, TraceEvent(
                timestamp=self._timestamp(620),
                event_type="tool_call_completed",
                status="completed",
                elapsed_ms=240,
                mode="foundry-iq",
                metadata={"tool_name": "foundry_iq_knowledge_base", "result_count": 3}
            )),
            (0.1, TraceEvent(
                timestamp=self._timestamp(650),
                event_type="answer_synthesis_started",
                status="running",
                mode="foundry-iq",
                metadata={}
            )),
            (1.5, TraceEvent(
                timestamp=self._timestamp(2800),
                event_type="answer_completed",
                status="completed",
                elapsed_ms=2150,
                mode="foundry-iq",
                metadata={"verdict": "Conditional"}
            ))
        ]

        for delay, event in events:
            await asyncio.sleep(delay)
            yield event

    def _timestamp(self, offset_ms: int) -> str:
        """Generate timestamp with offset"""
        return (self.base_time + timedelta(milliseconds=offset_ms)).isoformat()
