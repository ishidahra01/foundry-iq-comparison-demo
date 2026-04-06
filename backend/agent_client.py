"""
Client for interacting with Foundry Agent Service
Supports both real agents and mock mode for local testing
"""

import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime
from models import AgentResult, TraceEvent, Citation, Metrics
from mock_responses import MockResponseGenerator


class FoundryAgentClient:
    """Client for Foundry Agent Service with mock support"""

    def __init__(
        self,
        endpoint: Optional[str],
        api_key: Optional[str],
        classic_agent_name: str,
        foundry_iq_agent_name: str,
        mock_mode: bool = False
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.classic_agent_name = classic_agent_name
        self.foundry_iq_agent_name = foundry_iq_agent_name
        self.mock_mode = mock_mode or not (endpoint and api_key)

        if self.mock_mode:
            print("⚠️  Running in MOCK MODE - using simulated agent responses")
            self.mock_generator = MockResponseGenerator()
        else:
            print(f"✓ Connected to Foundry Agent Service: {endpoint}")

    async def execute_agent(
        self,
        agent_type: str,
        question: str,
        run_id: str
    ) -> AgentResult:
        """
        Execute an agent and return the full result
        """
        if self.mock_mode:
            return await self._execute_mock_agent(agent_type, question, run_id)
        else:
            return await self._execute_real_agent(agent_type, question, run_id)

    async def execute_agent_streaming(
        self,
        agent_type: str,
        question: str,
        run_id: str
    ) -> AsyncIterator[TraceEvent]:
        """
        Execute an agent with streaming trace events
        """
        if self.mock_mode:
            async for event in self._execute_mock_agent_streaming(agent_type, question, run_id):
                yield event
        else:
            async for event in self._execute_real_agent_streaming(agent_type, question, run_id):
                yield event

    async def _execute_mock_agent(
        self,
        agent_type: str,
        question: str,
        run_id: str
    ) -> AgentResult:
        """Execute mock agent (for local testing)"""
        start_time = time.time()

        # Simulate network delay
        await asyncio.sleep(0.5 if agent_type == "classic-rag" else 1.5)

        # Generate mock response
        result = self.mock_generator.generate_response(agent_type, question, run_id)

        # Calculate elapsed time
        elapsed_ms = int((time.time() - start_time) * 1000)
        result.metrics.total_time_ms = elapsed_ms

        return result

    async def _execute_mock_agent_streaming(
        self,
        agent_type: str,
        question: str,
        run_id: str
    ) -> AsyncIterator[TraceEvent]:
        """Execute mock agent with streaming events"""
        async for event in self.mock_generator.generate_streaming_response(
            agent_type, question, run_id
        ):
            yield event

    async def _execute_real_agent(
        self,
        agent_type: str,
        question: str,
        run_id: str
    ) -> AgentResult:
        """
        Execute real Foundry Agent

        Note: This is a placeholder implementation.
        Replace with actual Foundry Agent Service API calls.
        """
        agent_name = (
            self.classic_agent_name if agent_type == "classic-rag"
            else self.foundry_iq_agent_name
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "agent_name": agent_name,
            "query": question,
            "run_id": run_id,
            "include_trace": True
        }

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoint}/execute",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Agent execution failed: {error_text}")

                    data = await response.json()
                    elapsed_ms = int((time.time() - start_time) * 1000)

                    # Parse response (adjust based on actual Foundry Agent API)
                    return self._parse_agent_response(
                        agent_type, agent_name, data, elapsed_ms
                    )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return AgentResult(
                agent_type=agent_type,
                agent_name=agent_name,
                answer=f"Error executing agent: {str(e)}",
                citations=[],
                trace_events=[],
                metrics=Metrics(
                    total_time_ms=elapsed_ms,
                    retrieval_count=0,
                    subquery_count=0,
                    tool_calls=0
                ),
                sources_used=[],
                error=str(e)
            )

    async def _execute_real_agent_streaming(
        self,
        agent_type: str,
        question: str,
        run_id: str
    ) -> AsyncIterator[TraceEvent]:
        """
        Execute real Foundry Agent with streaming

        Note: This is a placeholder implementation.
        Replace with actual Foundry Agent Service streaming API.
        """
        agent_name = (
            self.classic_agent_name if agent_type == "classic-rag"
            else self.foundry_iq_agent_name
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream"
        }

        payload = {
            "agent_name": agent_name,
            "query": question,
            "run_id": run_id,
            "stream": True
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoint}/execute/stream",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                event = self._parse_trace_event(
                                    agent_type, data
                                )
                                if event:
                                    yield event
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            # Yield error event
            yield TraceEvent(
                timestamp=datetime.utcnow().isoformat(),
                event_type="error",
                status="failed",
                mode=agent_type,
                metadata={"error": str(e)}
            )

    def _parse_agent_response(
        self,
        agent_type: str,
        agent_name: str,
        data: Dict[str, Any],
        elapsed_ms: int
    ) -> AgentResult:
        """
        Parse Foundry Agent response into AgentResult

        Adjust this based on actual Foundry Agent API response format
        """
        # Example parsing - adjust based on actual API
        return AgentResult(
            agent_type=agent_type,
            agent_name=agent_name,
            answer=data.get("answer", ""),
            verdict=data.get("verdict"),
            citations=[
                Citation(
                    document=c.get("document", ""),
                    chunk=c.get("chunk"),
                    relevance_score=c.get("relevance_score"),
                    content=c.get("content")
                )
                for c in data.get("citations", [])
            ],
            trace_events=[
                TraceEvent(
                    timestamp=e.get("timestamp", datetime.utcnow().isoformat()),
                    event_type=e.get("event_type", "tool_call_completed"),
                    status=e.get("status", "completed"),
                    elapsed_ms=e.get("elapsed_ms"),
                    mode=agent_type,
                    metadata=e.get("metadata", {})
                )
                for e in data.get("trace_events", [])
            ],
            metrics=Metrics(
                total_time_ms=elapsed_ms,
                token_usage=data.get("token_usage"),
                retrieval_count=data.get("retrieval_count", 0),
                subquery_count=data.get("subquery_count", 0),
                tool_calls=data.get("tool_calls", 0)
            ),
            sources_used=data.get("sources_used", []),
            query_plan=data.get("query_plan"),
            error=data.get("error")
        )

    def _parse_trace_event(
        self,
        agent_type: str,
        data: Dict[str, Any]
    ) -> Optional[TraceEvent]:
        """
        Parse streaming trace event

        Adjust based on actual Foundry Agent streaming format
        """
        if not data.get("event_type"):
            return None

        return TraceEvent(
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            event_type=data.get("event_type"),
            status=data.get("status", "completed"),
            elapsed_ms=data.get("elapsed_ms"),
            mode=agent_type,
            metadata=data.get("metadata", {})
        )
