"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime


class SessionCreate(BaseModel):
    """Request to create a new session"""
    name: Optional[str] = None


class TraceEvent(BaseModel):
    """A single trace event from agent execution"""
    timestamp: str
    event_type: Literal[
        "task_hypothesis_generated",
        "tool_call_started",
        "tool_call_completed",
        "retrieval_started",
        "retrieval_completed",
        "answer_synthesis_started",
        "answer_completed",
        "error"
    ]
    status: Literal["pending", "running", "completed", "failed"] = "completed"
    elapsed_ms: Optional[int] = None
    mode: Literal["classic-rag", "foundry-iq"]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    """A citation/reference from the answer"""
    document: str
    chunk: Optional[str] = None
    relevance_score: Optional[float] = None
    content: Optional[str] = None


class Metrics(BaseModel):
    """Metrics for agent execution"""
    total_time_ms: int
    token_usage: Optional[Dict[str, int]] = None
    retrieval_count: int = 0
    subquery_count: int = 0
    tool_calls: int = 0


class AgentResult(BaseModel):
    """Result from a single agent execution"""
    agent_type: Literal["classic-rag", "foundry-iq"]
    agent_name: str
    answer: str
    verdict: Optional[Literal["Go", "Conditional", "No-Go"]] = None
    citations: List[Citation] = Field(default_factory=list)
    trace_events: List[TraceEvent] = Field(default_factory=list)
    metrics: Metrics
    sources_used: List[str] = Field(default_factory=list)
    query_plan: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ComparisonRequest(BaseModel):
    """Request to compare agents"""
    question: str
    session_id: Optional[str] = None


class ComparisonResponse(BaseModel):
    """Response with comparison results"""
    run_id: str
    question: str
    timestamp: str
    classic_rag: AgentResult
    foundry_iq: AgentResult


class EvaluationEvidence(BaseModel):
    """Ground-truth evidence entry for an evaluation sample."""
    document: str
    quote: str


class EvaluationCaseSummary(BaseModel):
    """Summary metadata for an evaluation sample."""
    id: str
    question: str
    line_number: int
    source_file: str
    is_default: bool = False


class EvaluationCase(EvaluationCaseSummary):
    """Full evaluation sample including ground truth and evidence."""
    ideal_answer: str
    evidence: List[EvaluationEvidence] = Field(default_factory=list)


class EvaluatedComparisonRequest(BaseModel):
    """Request to compare agents against a ground-truth evaluation case."""
    question: Optional[str] = None
    session_id: Optional[str] = None
    evaluation_sample_id: Optional[str] = None
    evaluation_jsonl: Optional[str] = None


class AnswerEvaluation(BaseModel):
    """Structured evaluation for a single agent answer."""
    overall_score: int = Field(ge=1, le=5)
    correctness_score: int = Field(ge=1, le=5)
    completeness_score: int = Field(ge=1, le=5)
    evidence_alignment_score: int = Field(ge=1, le=5)
    summary: str
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)


class EvaluationReport(BaseModel):
    """Structured comparison between agent answers and the ground truth."""
    overall_summary: str
    winner: Literal["classic-rag", "foundry-iq", "tie"]
    winner_reason: str
    classic_rag: AnswerEvaluation
    foundry_iq: AnswerEvaluation


class ComparisonEvaluation(BaseModel):
    """Evaluation wrapper with runtime status."""
    status: Literal["completed", "not_configured", "failed"]
    evaluator_model: Optional[str] = None
    report: Optional[EvaluationReport] = None
    error: Optional[str] = None


class EvaluatedComparisonResponse(ComparisonResponse):
    """Comparison response augmented with evaluation context and results."""
    evaluation_case: EvaluationCase
    evaluation: ComparisonEvaluation


class Session(BaseModel):
    """A comparison session"""
    id: str
    name: str
    created_at: str
    runs: List[ComparisonResponse] = Field(default_factory=list)
