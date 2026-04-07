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

        answer = """Based on the top-ranked documents (AI Search cap at 50 chunks), here is a summary:

- Launch is planned for April 30, 2026 in the Japan region, using Azure OpenAI and Azure AI Search.
- Budget is estimated at $27,400/month vs $25,000 budgeted (about 9.6% over). Cost optimization is proposed but not yet reflected.
- Security assessment is still pending and conflicts with the rollout plan dates.
- Rollout remains phased: Internal Beta → Limited Beta → Soft Launch → GA.

Data residency, vendor risk, and resiliency details were not present in the retrieved set, so risk coverage may be incomplete."""

        citations = [
            Citation(
                document="01_project_overview.md",
                relevance_score=0.82,
                content="Production Launch: April 30, 2026"
            ),
            Citation(
                document="05_budget_guardrail.md",
                relevance_score=0.76,
                content="Total OpEx/month: $25,000 budgeted, $27,400 estimated"
            ),
            Citation(
                document="06_rollout_plan.md",
                relevance_score=0.70,
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
                    "retrieved_count": 50,
                    "top_sources": [
                        "01_project_overview.md",
                        "05_budget_guardrail.md",
                        "06_rollout_plan.md"
                    ],
                    "note": "Hit AI Search top-50 limit; compliance/resiliency docs may be missing"
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
                retrieval_count=50,
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

        answer = """**Launch Decision: CONDITIONAL GO — block until residency/DR/vendor gaps are closed**

**What I checked (6 sub-queries):**
- Security & policy
- Budget status
- Regional compliance (JP primary, SG failover, EU analytics)
- Resiliency/DR readiness
- Incident history + customer feedback
- Vendor/contract risk

**Critical Blockers:**
1) **Data residency & logging** (🔴) — East US log export still enabled; SG failover lacks tokenization; translation vendor in US without gateway. Due: April 7-8. (09, 12, 13)
2) **Resiliency/DR gaps** (🔴) — Need 3x Search replicas, SG failover automation, cache warmup; chaos test showed stale data after ingest spikes. Due: April 12. (10, 12)
3) **Vendor contracts** (🔴) — Translation SLA & DPIA pending; CRM SCC not signed. Must decide before enabling SG failover analytics. (13)

**Important Risks:**
- **Incidents & CSAT:** Stale-data and translation outages unresolved; customer feedback calls out missing outage/postmortem content. (11, 12)
- **Budget:** Still ~$2.4k/month over; optimization needed but not blocking launch if controls land. (05)
- **Timeline linkage:** Security assessment overlaps with Internal Beta; keep April 2 decision checkpoint. (06, 03)

**Recommendation:** Conditional Go **only after** (a) US log export disabled + SG tokenization validated, (b) DR automation rehearsal completed, (c) translation vendor gated or replaced, (d) incident/postmortem content added to KB.

**Next Actions (owner/due):**
- Disable US log export and retarget to JP with redaction (Security, 4/7).
- Scale Search to 3 replicas and rehearse SG automation with cache warmup (SRE, 4/12).
- Decide on translation fallback: JP gateway or off by default; sign DPIA/SCC (Procurement, 4/8-4/10).
- Publish incident summaries + outage scripts to KB to close CSAT gap (Product, 4/5)."""

        citations = [
            Citation(
                document="09_regional_compliance.md",
                chunk="Logging & Retention",
                relevance_score=0.96,
                content="Open gap: log export still writes full transcripts to East US; SG failover must tokenize PII"
            ),
            Citation(
                document="10_resiliency_plan.md",
                chunk="Load & Failure Testing",
                relevance_score=0.92,
                content="Chaos test showed 10-minute stale results; need 3 Search replicas and DR automation"
            ),
            Citation(
                document="12_incident_history.md",
                chunk="Open Action Items",
                relevance_score=0.90,
                content="Replace East US log export; automate throttling during ingest; translation retry pending"
            ),
            Citation(
                document="13_vendor_risk.md",
                chunk="Mitigations & Deadlines",
                relevance_score=0.88,
                content="Translation provider high risk; DPIA/SCC pending; decision required before SG analytics"
            ),
            Citation(
                document="11_customer_feedback.md",
                chunk="Escalation Analysis",
                relevance_score=0.86,
                content="Escalations cite missing outage/postmortem content and slow answers during spikes"
            ),
            Citation(
                document="05_budget_guardrail.md",
                chunk="Section 2.2 - OpEx Monthly",
                relevance_score=0.80,
                content="Total OpEx/month: $25,000 budgeted, $27,400 current estimate, +$2,400 variance"
            ),
            Citation(
                document="06_rollout_plan.md",
                chunk="Phase 1: Internal Beta",
                relevance_score=0.78,
                content="Security assessment timeline overlaps with Internal Beta start; needs reschedule or waiver"
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
                        "Regional compliance and data residency",
                        "Resiliency / failover readiness",
                        "Incident history and customer feedback",
                        "Vendor contract and DPIA status"
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
                    "subqueries_executed": 6,
                    "total_results": 82,
                    "sources": [
                        "09_regional_compliance.md",
                        "10_resiliency_plan.md",
                        "12_incident_history.md",
                        "13_vendor_risk.md",
                        "11_customer_feedback.md",
                        "05_budget_guardrail.md"
                    ]
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
                timestamp=self._timestamp(640),
                event_type="tool_call_started",
                status="completed",
                elapsed_ms=20,
                mode="foundry-iq",
                metadata={
                    "tool_name": "vendor_contract_checker",
                    "query": "Translation and CRM contract residency terms"
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(820),
                event_type="tool_call_completed",
                status="completed",
                elapsed_ms=180,
                mode="foundry-iq",
                metadata={
                    "tool_name": "vendor_contract_checker",
                    "result_count": 2
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(860),
                event_type="answer_synthesis_started",
                status="completed",
                elapsed_ms=30,
                mode="foundry-iq",
                metadata={
                    "synthesis_approach": "Multi-dimensional analysis with risk prioritization"
                }
            ),
            TraceEvent(
                timestamp=self._timestamp(3000),
                event_type="answer_completed",
                status="completed",
                elapsed_ms=2140,
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
                retrieval_count=82,
                subquery_count=6,
                tool_calls=2
            ),
            sources_used=[
                "09_regional_compliance.md",
                "10_resiliency_plan.md",
                "12_incident_history.md",
                "13_vendor_risk.md",
                "11_customer_feedback.md",
                "05_budget_guardrail.md",
                "06_rollout_plan.md",
                "03_security_policy.md"
            ],
            query_plan={
                "original_query": question,
                "decomposed_queries": [
                    "What are the security and policy blockers?",
                    "Is the budget approved and by how much are we over?",
                    "Are we compliant with JP/SG/EU data residency requirements?",
                    "Is resiliency/DR ready for launch and failover?",
                    "What incidents and customer feedback must we address?",
                    "Which vendor contracts or SLAs block SG failover?"
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
                metadata={
                    "retrieved_count": 50,
                    "note": "AI Search top-50 cap hit"
                }
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
                metadata={"planned_queries": 6}
            )),
            (0.4, TraceEvent(
                timestamp=self._timestamp(350),
                event_type="retrieval_completed",
                status="completed",
                elapsed_ms=230,
                mode="foundry-iq",
                metadata={"subqueries_executed": 6, "total_results": 82}
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
                timestamp=self._timestamp(640),
                event_type="tool_call_started",
                status="running",
                mode="foundry-iq",
                metadata={"tool_name": "vendor_contract_checker"}
            )),
            (0.4, TraceEvent(
                timestamp=self._timestamp(820),
                event_type="tool_call_completed",
                status="completed",
                elapsed_ms=180,
                mode="foundry-iq",
                metadata={"tool_name": "vendor_contract_checker", "result_count": 2}
            )),
            (0.2, TraceEvent(
                timestamp=self._timestamp(860),
                event_type="answer_synthesis_started",
                status="running",
                mode="foundry-iq",
                metadata={}
            )),
            (1.5, TraceEvent(
                timestamp=self._timestamp(3000),
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
