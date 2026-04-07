"""
Client for interacting with Azure AI Projects agents via the Responses API.
Supports both real agents and mock mode for local testing.
"""

import asyncio
import time
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional

from models import AgentResult, Citation, Metrics, TraceEvent
from mock_responses import MockResponseGenerator

try:
    from azure.ai.projects.aio import AIProjectClient
    from azure.identity.aio import DefaultAzureCredential
except ImportError:
    AIProjectClient = None
    DefaultAzureCredential = None


class FoundryAgentClient:
    """Client for Azure AI Projects agents with mock support."""

    def __init__(
        self,
        project_endpoint: Optional[str],
        classic_agent_name: str,
        foundry_iq_agent_name: str,
        mock_mode: bool = False,
    ):
        self.project_endpoint = project_endpoint
        self.classic_agent_name = classic_agent_name
        self.foundry_iq_agent_name = foundry_iq_agent_name
        self.mock_mode = mock_mode or not project_endpoint

        if self.mock_mode:
            print("Running in MOCK MODE - using simulated agent responses")
            self.mock_generator = MockResponseGenerator()
        else:
            print(f"Connected to Azure AI Project: {project_endpoint}")

    async def execute_agent(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AgentResult:
        """Execute an agent and return the full result."""
        if self.mock_mode:
            return await self._execute_mock_agent(agent_type, question, run_id)
        return await self._execute_real_agent(agent_type, question, run_id)

    async def execute_agent_streaming(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AsyncIterator[TraceEvent]:
        """Execute an agent with streaming trace events."""
        if self.mock_mode:
            async for event in self._execute_mock_agent_streaming(agent_type, question, run_id):
                yield event
            return

        async for event in self._execute_real_agent_streaming(agent_type, question, run_id):
            yield event

    async def _execute_mock_agent(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AgentResult:
        """Execute mock agent (for local testing)."""
        start_time = time.time()
        await asyncio.sleep(0.5 if agent_type == "classic-rag" else 1.5)
        result = self.mock_generator.generate_response(agent_type, question, run_id)
        result.metrics.total_time_ms = int((time.time() - start_time) * 1000)
        return result

    async def _execute_mock_agent_streaming(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AsyncIterator[TraceEvent]:
        """Execute mock agent with streaming events."""
        async for event in self.mock_generator.generate_streaming_response(agent_type, question, run_id):
            yield event

    async def _execute_real_agent(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AgentResult:
        """Execute a real Azure AI Projects agent through the Responses API."""
        agent_name = self._resolve_agent_name(agent_type)
        start_time = time.time()

        try:
            self._validate_real_mode_dependencies()

            async with (
                DefaultAzureCredential() as credential,
                AIProjectClient(endpoint=self.project_endpoint, credential=credential) as project_client,
                project_client.get_openai_client() as openai_client,
            ):
                response = await openai_client.responses.create(
                    input=question,
                    extra_body={
                        "agent_reference": {
                            "name": agent_name,
                            "type": "agent_reference",
                        }
                    },
                )

            elapsed_ms = int((time.time() - start_time) * 1000)
            return self._parse_agent_response(agent_type, agent_name, response, elapsed_ms, run_id)
        except Exception as exc:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return AgentResult(
                agent_type=agent_type,
                agent_name=agent_name,
                answer=f"Error executing agent: {exc}",
                citations=[],
                trace_events=[],
                metrics=Metrics(
                    total_time_ms=elapsed_ms,
                    retrieval_count=0,
                    subquery_count=0,
                    tool_calls=0,
                ),
                sources_used=[],
                error=str(exc),
            )

    async def _execute_real_agent_streaming(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AsyncIterator[TraceEvent]:
        """Execute a real Azure AI Projects agent with Responses API streaming."""
        agent_name = self._resolve_agent_name(agent_type)

        try:
            self._validate_real_mode_dependencies()

            async with (
                DefaultAzureCredential() as credential,
                AIProjectClient(endpoint=self.project_endpoint, credential=credential) as project_client,
                project_client.get_openai_client() as openai_client,
            ):
                stream = await openai_client.responses.create(
                    input=question,
                    stream=True,
                    extra_body={
                        "agent_reference": {
                            "name": agent_name,
                            "type": "agent_reference",
                        }
                    },
                )

                answer_started = False
                async for data in stream:
                    event = self._parse_trace_event(agent_type, data, run_id, answer_started)
                    if event:
                        if event.event_type == "answer_synthesis_started":
                            answer_started = True
                        yield event
        except Exception as exc:
            yield TraceEvent(
                timestamp=datetime.utcnow().isoformat(),
                event_type="error",
                status="failed",
                mode=agent_type,
                metadata={"error": str(exc), "run_id": run_id},
            )

    def _resolve_agent_name(self, agent_type: str) -> str:
        return self.classic_agent_name if agent_type == "classic-rag" else self.foundry_iq_agent_name

    def _parse_agent_response(
        self,
        agent_type: str,
        agent_name: str,
        response: Any,
        elapsed_ms: int,
        run_id: str,
    ) -> AgentResult:
        """Parse a Responses API result into AgentResult."""
        citations = self._extract_citations(response)
        return AgentResult(
            agent_type=agent_type,
            agent_name=agent_name,
            answer=self._extract_output_text(response),
            verdict=self._extract_verdict(response),
            citations=citations,
            trace_events=self._build_trace_events_from_response(agent_type, response, run_id),
            metrics=Metrics(
                total_time_ms=elapsed_ms,
                token_usage=self._extract_token_usage(response),
                retrieval_count=self._count_retrievals(response),
                subquery_count=self._count_subqueries(response),
                tool_calls=self._count_tool_calls(response),
            ),
            sources_used=self._extract_sources_used(citations),
            query_plan=self._extract_query_plan(response),
            error=None,
        )

    def _parse_trace_event(
        self,
        agent_type: str,
        data: Any,
        run_id: str,
        answer_started: bool,
    ) -> Optional[TraceEvent]:
        """Map Responses API streaming events to the demo trace model."""
        event_type = getattr(data, "type", None)
        if not event_type:
            return None

        timestamp = datetime.utcnow().isoformat()

        if event_type == "response.created":
            return TraceEvent(
                timestamp=timestamp,
                event_type="task_hypothesis_generated",
                status="completed",
                mode=agent_type,
                metadata={
                    "run_id": run_id,
                    "response_id": getattr(getattr(data, "response", None), "id", None),
                },
            )

        if event_type == "response.output_text.delta" and not answer_started:
            return TraceEvent(
                timestamp=timestamp,
                event_type="answer_synthesis_started",
                status="running",
                mode=agent_type,
                metadata={"run_id": run_id},
            )

        if event_type in {"response.output_item.added", "response.output_item.done"}:
            item = getattr(data, "item", None)
            item_type = getattr(item, "type", None)
            mapped = self._map_output_item_to_trace_event(item_type)
            if not mapped:
                return None

            return TraceEvent(
                timestamp=timestamp,
                event_type=mapped,
                status="completed" if event_type.endswith("done") else "running",
                mode=agent_type,
                metadata={
                    "run_id": run_id,
                    "item_type": item_type,
                    "item": self._serialize_value(item),
                },
            )

        if event_type in {"response.text.done", "response.completed"}:
            final_response = getattr(data, "response", None)
            return TraceEvent(
                timestamp=timestamp,
                event_type="answer_completed",
                status="completed",
                mode=agent_type,
                metadata={
                    "run_id": run_id,
                    "output_text": getattr(final_response, "output_text", getattr(data, "text", None)),
                },
            )

        if event_type == "error":
            return TraceEvent(
                timestamp=timestamp,
                event_type="error",
                status="failed",
                mode=agent_type,
                metadata={"run_id": run_id, "error": self._serialize_value(data)},
            )

        return None

    def _validate_real_mode_dependencies(self) -> None:
        if AIProjectClient is None or DefaultAzureCredential is None:
            raise RuntimeError(
                "Real mode requires azure-ai-projects and azure-identity. "
                "Install backend requirements before using Azure AI Projects integration."
            )
        if not self.project_endpoint:
            raise RuntimeError("AZURE_AI_PROJECT_ENDPOINT is required when MOCK_MODE=false.")

    def _extract_output_items(self, response: Any) -> List[Any]:
        output = getattr(response, "output", None)
        return list(output) if output else []

    def _extract_output_text(self, response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text:
            return output_text

        parts: List[str] = []
        for item in self._extract_output_items(response):
            if getattr(item, "type", None) != "message":
                continue
            for content in getattr(item, "content", []) or []:
                if getattr(content, "type", None) == "output_text" and getattr(content, "text", None):
                    parts.append(content.text)

        return "\n".join(parts).strip()

    def _extract_citations(self, response: Any) -> List[Citation]:
        citations: List[Citation] = []
        for item in self._extract_output_items(response):
            if getattr(item, "type", None) != "message":
                continue
            for content in getattr(item, "content", []) or []:
                for annotation in getattr(content, "annotations", None) or []:
                    citation = self._annotation_to_citation(annotation)
                    if citation:
                        citations.append(citation)
        return citations

    def _annotation_to_citation(self, annotation: Any) -> Optional[Citation]:
        annotation_type = getattr(annotation, "type", None)
        if not annotation_type:
            return None

        document = (
            getattr(annotation, "filename", None)
            or getattr(annotation, "title", None)
            or getattr(annotation, "url", None)
            or getattr(annotation, "file_id", None)
            or annotation_type
        )

        return Citation(
            document=str(document),
            chunk=getattr(annotation, "chunk_id", None) or getattr(annotation, "index", None),
            relevance_score=getattr(annotation, "score", None) or getattr(annotation, "relevance_score", None),
            content=getattr(annotation, "quote", None) or getattr(annotation, "text", None),
        )

    def _extract_token_usage(self, response: Any) -> Optional[Dict[str, int]]:
        usage = getattr(response, "usage", None)
        if not usage:
            return None

        usage_dict = self._serialize_value(usage)
        if not isinstance(usage_dict, dict):
            return None

        normalized: Dict[str, int] = {}
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            value = usage_dict.get(key)
            if isinstance(value, int):
                normalized[key] = value
        return normalized or None

    def _count_retrievals(self, response: Any) -> int:
        return sum(1 for item in self._extract_output_items(response) if getattr(item, "type", None) in self._retrieval_item_types())

    def _count_tool_calls(self, response: Any) -> int:
        return sum(1 for item in self._extract_output_items(response) if getattr(item, "type", None) in self._tool_item_types())

    def _count_subqueries(self, response: Any) -> int:
        query_plan = self._extract_query_plan(response) or {}
        subqueries = query_plan.get("subqueries")
        return len(subqueries) if isinstance(subqueries, list) else 0

    def _extract_sources_used(self, citations: Iterable[Citation]) -> List[str]:
        seen = set()
        sources: List[str] = []
        for citation in citations:
            if citation.document not in seen:
                seen.add(citation.document)
                sources.append(citation.document)
        return sources

    def _extract_query_plan(self, response: Any) -> Optional[Dict[str, Any]]:
        reasoning: List[str] = []
        subqueries: List[str] = []
        tool_sequence: List[str] = []

        for item in self._extract_output_items(response):
            item_type = getattr(item, "type", None)
            if item_type == "reasoning":
                for summary in getattr(item, "summary", None) or []:
                    text = getattr(summary, "text", None)
                    if text:
                        reasoning.append(text)
            elif item_type in self._tool_item_types():
                tool_sequence.append(item_type)
                query = getattr(item, "query", None)
                if query:
                    subqueries.append(str(query))

        if not reasoning and not subqueries and not tool_sequence:
            return None

        return {
            "reasoning": reasoning,
            "subqueries": subqueries,
            "tool_sequence": tool_sequence,
        }

    def _extract_verdict(self, response: Any) -> Optional[str]:
        answer = self._extract_output_text(response).lower()
        if not answer:
            return None
        if "no-go" in answer:
            return "No-Go"
        if "conditional" in answer:
            return "Conditional"
        if "go" in answer:
            return "Go"
        return None

    def _build_trace_events_from_response(self, agent_type: str, response: Any, run_id: str) -> List[TraceEvent]:
        timestamp = datetime.utcnow().isoformat()
        events: List[TraceEvent] = [
            TraceEvent(
                timestamp=timestamp,
                event_type="task_hypothesis_generated",
                status="completed",
                mode=agent_type,
                metadata={"run_id": run_id},
            )
        ]

        output_items = self._extract_output_items(response)
        if any(getattr(item, "type", None) == "reasoning" for item in output_items):
            events.append(
                TraceEvent(
                    timestamp=timestamp,
                    event_type="answer_synthesis_started",
                    status="running",
                    mode=agent_type,
                    metadata={"run_id": run_id},
                )
            )

        for item in output_items:
            item_type = getattr(item, "type", None)
            mapped = self._map_output_item_to_trace_event(item_type)
            if not mapped:
                continue
            events.append(
                TraceEvent(
                    timestamp=timestamp,
                    event_type=mapped,
                    status="completed",
                    mode=agent_type,
                    metadata={
                        "run_id": run_id,
                        "item_type": item_type,
                        "item": self._serialize_value(item),
                    },
                )
            )

        events.append(
            TraceEvent(
                timestamp=timestamp,
                event_type="answer_completed",
                status="completed",
                mode=agent_type,
                metadata={
                    "run_id": run_id,
                    "output_text": self._extract_output_text(response),
                },
            )
        )
        return events

    def _map_output_item_to_trace_event(self, item_type: Optional[str]) -> Optional[str]:
        if not item_type:
            return None
        if item_type in self._retrieval_item_types():
            return "retrieval_completed"
        if item_type in self._tool_item_types():
            return "tool_call_completed"
        if item_type == "reasoning":
            return "task_hypothesis_generated"
        return None

    def _tool_item_types(self) -> set[str]:
        return {
            "file_search_call",
            "web_search_call",
            "bing_grounding_call",
            "azure_ai_search_call",
            "mcp_call",
            "openapi_call",
            "function_call",
            "code_interpreter_call",
            "computer_call",
            "a2a_preview_call",
        }

    def _retrieval_item_types(self) -> set[str]:
        return {
            "file_search_call",
            "web_search_call",
            "bing_grounding_call",
            "azure_ai_search_call",
            "sharepoint_grounding_preview_call",
            "fabric_dataagent_preview_call",
        }

    def _serialize_value(self, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        if isinstance(value, dict):
            return {key: self._serialize_value(item) for key, item in value.items()}
        if hasattr(value, "model_dump"):
            return self._serialize_value(value.model_dump())
        if hasattr(value, "__dict__"):
            return self._serialize_value(vars(value))
        return str(value)
