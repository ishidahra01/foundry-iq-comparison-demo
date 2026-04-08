"""
Foundry IQ Comparison Demo - Backend API
Provides endpoints for comparing Classic RAG vs Foundry IQ Agent responses
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

from agent_client import FoundryAgentClient
from evaluator import EvaluationService
from models import (
    ComparisonRequest,
    ComparisonResponse,
    AgentResult,
    TraceEvent,
    SessionCreate,
    Session,
    EvaluatedComparisonRequest,
    EvaluatedComparisonResponse,
)

load_dotenv()

app = FastAPI(
    title="Foundry IQ Comparison Demo API",
    description="Compare Classic RAG vs Foundry IQ Agent responses",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis or similar in production)
sessions: Dict[str, Session] = {}

# Agent client
legacy_foundry_endpoint = os.getenv("FOUNDRY_AGENT_ENDPOINT")
if legacy_foundry_endpoint and not os.getenv("AZURE_AI_PROJECT_ENDPOINT"):
    print(
        "FOUNDRY_AGENT_ENDPOINT is deprecated for Azure AI Projects 2.x. "
        "Set AZURE_AI_PROJECT_ENDPOINT instead."
    )

agent_client = FoundryAgentClient(
    project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    classic_agent_name=os.getenv("CLASSIC_RAG_AGENT_NAME", "classic-rag-agent"),
    classic_agent_version=os.getenv("CLASSIC_RAG_AGENT_VERSION"),
    foundry_iq_agent_name=os.getenv("FOUNDRY_IQ_AGENT_NAME", "foundry-iq-agent"),
    foundry_iq_agent_version=os.getenv("FOUNDRY_IQ_AGENT_VERSION"),
)

evaluation_service = EvaluationService(
    project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "azure_ai_project_endpoint_configured": bool(os.getenv("AZURE_AI_PROJECT_ENDPOINT"))
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Foundry IQ Comparison Demo API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "sessions": "/sessions",
            "compare": "/compare",
            "evaluation_cases": "/evaluation/cases",
            "compare_evaluate": "/compare/evaluate",
            "websocket": "/ws/compare/{session_id}"
        }
    }


@app.post("/sessions", response_model=Session)
async def create_session(session_data: SessionCreate):
    """Create a new comparison session"""
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        name=session_data.name or f"Session {len(sessions) + 1}",
        created_at=datetime.utcnow().isoformat(),
        runs=[]
    )
    sessions[session_id] = session
    return session


@app.get("/sessions", response_model=List[Session])
async def list_sessions():
    """List all sessions"""
    return list(sessions.values())


@app.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    del sessions[session_id]
    return {"message": "Session deleted successfully"}


@app.post("/compare", response_model=ComparisonResponse)
async def compare_agents(request: ComparisonRequest):
    """
    Compare Classic RAG and Foundry IQ agents (synchronous endpoint)
    For real-time updates, use the WebSocket endpoint instead
    """
    response = await _run_comparison(request.question, request.session_id)

    return response


@app.get("/evaluation/cases")
async def list_evaluation_cases():
    """List available JSONL-backed evaluation samples."""
    return {
        "cases": [case.model_dump() for case in evaluation_service.list_sample_cases()]
    }


@app.post("/compare/evaluate", response_model=EvaluatedComparisonResponse)
async def compare_and_evaluate(request: EvaluatedComparisonRequest):
    """Compare both agents and evaluate them against a ground-truth JSONL case."""
    evaluation_case = evaluation_service.resolve_case(
        sample_id=request.evaluation_sample_id,
        raw_jsonl=request.evaluation_jsonl,
    )

    comparison = await _run_comparison(
        evaluation_case.question,
        request.session_id,
    )

    evaluation = await evaluation_service.evaluate_answers(
        evaluation_case,
        comparison.classic_rag,
        comparison.foundry_iq,
    )

    return EvaluatedComparisonResponse(
        **comparison.model_dump(),
        evaluation_case=evaluation_case,
        evaluation=evaluation,
    )


async def _run_comparison(question: str, session_id: Optional[str] = None) -> ComparisonResponse:
    run_id = str(uuid.uuid4())

    classic_task = asyncio.create_task(
        agent_client.execute_agent("classic-rag", question, run_id)
    )
    foundry_iq_task = asyncio.create_task(
        agent_client.execute_agent("foundry-iq", question, run_id)
    )

    classic_result, foundry_iq_result = await asyncio.gather(
        classic_task, foundry_iq_task
    )

    response = ComparisonResponse(
        run_id=run_id,
        question=question,
        timestamp=datetime.utcnow().isoformat(),
        classic_rag=classic_result,
        foundry_iq=foundry_iq_result
    )

    # Store in session if session_id provided
    if session_id and session_id in sessions:
        sessions[session_id].runs.append(response)

    return response


@app.websocket("/ws/compare/{session_id}")
async def websocket_compare(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time agent comparison with streaming events
    """
    await websocket.accept()

    # Verify session exists
    if session_id not in sessions:
        await websocket.send_json({
            "type": "error",
            "message": f"Session {session_id} not found"
        })
        await websocket.close()
        return

    try:
        while True:
            # Receive question from client
            data = await websocket.receive_json()
            question = data.get("question")

            if not question:
                await websocket.send_json({
                    "type": "error",
                    "message": "Question is required"
                })
                continue

            run_id = str(uuid.uuid4())

            # Send start event
            await websocket.send_json({
                "type": "run.started",
                "run_id": run_id,
                "question": question,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Execute both agents with streaming
            async def stream_agent_events(agent_type: str):
                """Stream events from agent execution"""
                async for event in agent_client.execute_agent_streaming(
                    agent_type, question, run_id
                ):
                    await websocket.send_json({
                        "type": "agent.event",
                        "agent_type": agent_type,
                        "run_id": run_id,
                        "event": event.dict()
                    })

            # Run both agents concurrently
            await asyncio.gather(
                stream_agent_events("classic-rag"),
                stream_agent_events("foundry-iq")
            )

            # Send completion event
            await websocket.send_json({
                "type": "run.completed",
                "run_id": run_id,
                "timestamp": datetime.utcnow().isoformat()
            })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close()


@app.get("/sample-queries")
async def get_sample_queries():
    """Get sample queries for testing"""
    return {
        "queries": [
            {
                "id": "simple-1",
                "category": "Simple",
                "text": "What is the project timeline?",
                "description": "Basic factual query"
            },
            {
                "id": "simple-2",
                "category": "Simple",
                "text": "What is the monthly budget for this project?",
                "description": "Simple budget lookup"
            },
            {
                "id": "medium-1",
                "category": "Medium",
                "text": "Are there any security blockers for the launch?",
                "description": "Requires synthesis across security documents"
            },
            {
                "id": "medium-2",
                "category": "Medium",
                "text": "What preview features are being used in this project?",
                "description": "Requires understanding policy implications"
            },
            {
                "id": "complex-1",
                "category": "Complex",
                "text": "Should we launch this AI feature on April 30? What are the main risks and blockers?",
                "description": "Requires comprehensive analysis across multiple documents"
            },
            {
                "id": "complex-2",
                "category": "Complex",
                "text": "この AI 機能を、日本向け本番環境で来月リリースしてよいか。内部ポリシー、現在の実装状況、予算制約を踏まえて、可否/ブロッカー/次アクションを答えてください",
                "description": "Go/No-Go decision with multi-faceted analysis (Japanese)"
            },
            {
                "id": "complex-3",
                "category": "Complex",
                "text": "What are the dependencies between the security assessment, internal beta phase, and the planned launch date?",
                "description": "Temporal and dependency analysis"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", "8000"))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
