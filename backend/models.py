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


class Session(BaseModel):
    """A comparison session"""
    id: str
    name: str
    created_at: str
    runs: List[ComparisonResponse] = Field(default_factory=list)
