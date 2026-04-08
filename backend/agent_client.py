"""
Client for interacting with Azure AI Projects agents via the Responses API.
"""

import asyncio
import json
import logging
import os
from pathlib import PurePosixPath
import re
import time
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional
from urllib.parse import urlparse

from models import AgentResult, Citation, Metrics, TraceEvent

try:
    from azure.ai.projects.aio import AIProjectClient
    from azure.identity.aio import DefaultAzureCredential
except ImportError:
    AIProjectClient = None
    DefaultAzureCredential = None


logger = logging.getLogger(__name__)


class FoundryAgentClient:
    """Client for Azure AI Projects agents."""

    def __init__(
        self,
        project_endpoint: Optional[str],
        classic_agent_name: str,
        classic_agent_version: Optional[str],
        foundry_iq_agent_name: str,
        foundry_iq_agent_version: Optional[str],
    ):
        self.project_endpoint = project_endpoint
        self.classic_agent_name = classic_agent_name
        self.classic_agent_version = classic_agent_version
        self.foundry_iq_agent_name = foundry_iq_agent_name
        self.foundry_iq_agent_version = foundry_iq_agent_version
        self.debug_logging = os.getenv("AGENT_CLIENT_DEBUG", "false").lower() == "true"
        self.debug_raw_payloads = os.getenv("AGENT_CLIENT_DEBUG_RAW", "false").lower() == "true"
        self.auto_approve_mcp = os.getenv("AGENT_AUTO_APPROVE_MCP", "true").lower() == "true"
        self.response_poll_interval_sec = float(os.getenv("AGENT_RESPONSE_POLL_INTERVAL_SEC", "0.75"))
        self.response_poll_timeout_sec = float(os.getenv("AGENT_RESPONSE_POLL_TIMEOUT_SEC", "45"))

        logger.info("Configured Azure AI Project endpoint: %s", project_endpoint)

    async def execute_agent(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AgentResult:
        """Execute an agent and return the full result."""
        return await self._execute_real_agent(agent_type, question, run_id)

    async def execute_agent_streaming(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AsyncIterator[TraceEvent]:
        """Execute an agent with streaming trace events."""
        async for event in self._execute_real_agent_streaming(agent_type, question, run_id):
            yield event

    async def _execute_real_agent(
        self,
        agent_type: str,
        question: str,
        run_id: str,
    ) -> AgentResult:
        """Execute a real Azure AI Projects agent through the Responses API."""
        agent_name = self._resolve_agent_name(agent_type)
        agent_version = self._resolve_agent_version(agent_type)
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
                    extra_body=self._build_agent_reference_body(agent_name, agent_version),
                )
                response = await self._await_response_completion(
                    openai_client,
                    response,
                    agent_type,
                    agent_name,
                    agent_version,
                    run_id,
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
        agent_version = self._resolve_agent_version(agent_type)

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
                    extra_body=self._build_agent_reference_body(agent_name, agent_version),
                )

                answer_started = False
                async for data in stream:
                    self._log_stream_event(agent_type, agent_name, run_id, data)
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

    def _resolve_agent_version(self, agent_type: str) -> Optional[str]:
        return self.classic_agent_version if agent_type == "classic-rag" else self.foundry_iq_agent_version

    def _parse_agent_response(
        self,
        agent_type: str,
        agent_name: str,
        response: Any,
        elapsed_ms: int,
        run_id: str,
    ) -> AgentResult:
        """Parse a Responses API result into AgentResult."""
        tool_calls = self._extract_tool_calls(response)
        citations = self._merge_citations(
            self._extract_citations_from_annotations(response),
            self._extract_citations_from_tool_calls(tool_calls),
        )
        answer = self._extract_output_text(response)
        error = self._build_response_error(response, answer)
        query_plan = self._extract_query_plan(response, tool_calls)
        return AgentResult(
            agent_type=agent_type,
            agent_name=agent_name,
            answer=answer,
            verdict=self._extract_verdict(response),
            citations=citations,
            trace_events=self._build_trace_events_from_response(agent_type, response, run_id),
            metrics=Metrics(
                total_time_ms=elapsed_ms,
                token_usage=self._extract_token_usage(response),
                retrieval_count=self._count_retrievals(response, tool_calls),
                subquery_count=self._count_subqueries(query_plan),
                tool_calls=len(tool_calls),
            ),
            sources_used=self._extract_sources_used(citations, tool_calls),
            query_plan=query_plan,
            error=error,
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

        if event_type in {
            "response.file_search_call.searching",
            "response.web_search_call.searching",
            "response.mcp_call.in_progress",
            "response.function_call_arguments.delta",
            "response.mcp_call.arguments.delta",
        }:
            return TraceEvent(
                timestamp=timestamp,
                event_type="tool_call_started",
                status="running",
                mode=agent_type,
                metadata={
                    "run_id": run_id,
                    "sdk_event_type": event_type,
                    "event": self._serialize_value(data),
                },
            )

        if event_type in {
            "response.file_search_call.completed",
            "response.web_search_call.completed",
            "response.mcp_call.completed",
            "response.function_call_arguments.done",
            "response.mcp_call.arguments.done",
        }:
            return TraceEvent(
                timestamp=timestamp,
                event_type="tool_call_completed",
                status="completed",
                mode=agent_type,
                metadata={
                    "run_id": run_id,
                    "sdk_event_type": event_type,
                    "event": self._serialize_value(data),
                },
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

        if event_type in {"response.output_text.done", "response.completed"}:
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

        if event_type in {"error", "response.failed", "response.incomplete", "response.mcp_call.failed"}:
            return TraceEvent(
                timestamp=timestamp,
                event_type="error",
                status="failed",
                mode=agent_type,
                metadata={
                    "run_id": run_id,
                    "sdk_event_type": event_type,
                    "error": self._serialize_value(data),
                },
            )

        return None

    def _build_agent_reference_body(self, agent_name: str, agent_version: Optional[str]) -> Dict[str, Any]:
        agent_reference: Dict[str, Any] = {
            "name": agent_name,
            "type": "agent_reference",
        }
        if agent_version:
            agent_reference["version"] = agent_version
        return {"agent_reference": agent_reference}

    async def _await_response_completion(
        self,
        openai_client: Any,
        response: Any,
        agent_type: str,
        agent_name: str,
        agent_version: Optional[str],
        run_id: str,
    ) -> Any:
        self._log_response_snapshot("create", agent_type, agent_name, run_id, response)

        response = await self._resolve_mcp_approval_requests(
            openai_client,
            response,
            agent_type,
            agent_name,
            agent_version,
            run_id,
        )

        status = getattr(response, "status", None)
        response_id = getattr(response, "id", None)
        if self._is_terminal_response_status(status) or not response_id:
            return response

        deadline = time.time() + self.response_poll_timeout_sec
        while time.time() < deadline:
            await asyncio.sleep(self.response_poll_interval_sec)
            response = await openai_client.responses.retrieve(
                response_id,
                extra_body=self._build_agent_reference_body(agent_name, agent_version),
            )
            self._log_response_snapshot("retrieve", agent_type, agent_name, run_id, response)
            response = await self._resolve_mcp_approval_requests(
                openai_client,
                response,
                agent_type,
                agent_name,
                agent_version,
                run_id,
            )

            if self._is_terminal_response_status(getattr(response, "status", None)):
                return response

        raise TimeoutError(
            f"Timed out waiting for agent response {response_id} to complete after "
            f"{self.response_poll_timeout_sec:.1f}s."
        )

    def _is_terminal_response_status(self, status: Optional[str]) -> bool:
        return status in {"completed", "failed", "cancelled", "incomplete"}

    async def _resolve_mcp_approval_requests(
        self,
        openai_client: Any,
        response: Any,
        agent_type: str,
        agent_name: str,
        agent_version: Optional[str],
        run_id: str,
    ) -> Any:
        approval_requests = self._extract_mcp_approval_requests(response)
        if not approval_requests:
            return response

        if not self.auto_approve_mcp:
            logger.warning(
                "MCP approval request requires manual approval: agent_type=%s agent_name=%s run_id=%s requests=%s",
                agent_type,
                agent_name,
                run_id,
                [request.get("id") for request in approval_requests],
            )
            return response

        approvals = [
            {
                "type": "mcp_approval_response",
                "approval_request_id": request["id"],
                "approve": True,
            }
            for request in approval_requests
        ]

        logger.info(
            "Auto-approving MCP requests: agent_type=%s agent_name=%s run_id=%s request_ids=%s",
            agent_type,
            agent_name,
            run_id,
            [request["id"] for request in approval_requests],
        )

        follow_up_response = await openai_client.responses.create(
            input=approvals,
            previous_response_id=getattr(response, "id", None),
            extra_body=self._build_agent_reference_body(agent_name, agent_version),
        )
        self._log_response_snapshot("approve", agent_type, agent_name, run_id, follow_up_response)
        return follow_up_response

    def _extract_mcp_approval_requests(self, response: Any) -> List[Dict[str, Any]]:
        approval_requests: List[Dict[str, Any]] = []
        for item in self._extract_output_items(response):
            if getattr(item, "type", None) != "mcp_approval_request":
                continue

            approval_request = self._serialize_value(item)
            if isinstance(approval_request, dict) and approval_request.get("id"):
                approval_requests.append(approval_request)

        return approval_requests

    def _build_response_error(self, response: Any, answer: str) -> Optional[str]:
        status = getattr(response, "status", None)
        response_error = getattr(response, "error", None)
        incomplete_details = getattr(response, "incomplete_details", None)

        if response_error:
            message = getattr(response_error, "message", None) or str(self._serialize_value(response_error))
            return f"Response status '{status}': {message}" if status else message

        if status in {"failed", "cancelled", "incomplete"}:
            details = self._serialize_value(incomplete_details)
            return f"Response status '{status}' with details: {details}"

        if status == "completed" and not answer:
            item_types = [getattr(item, "type", None) for item in self._extract_output_items(response)]
            return f"Agent completed without a final answer. Output item types: {item_types}"

        return None

    def _log_response_snapshot(
        self,
        stage: str,
        agent_type: str,
        agent_name: str,
        run_id: str,
        response: Any,
    ) -> None:
        if not self.debug_logging:
            return

        snapshot = {
            "stage": stage,
            "agent_type": agent_type,
            "agent_name": agent_name,
            "run_id": run_id,
            "response_id": getattr(response, "id", None),
            "status": getattr(response, "status", None),
            "output_text": self._extract_output_text(response),
            "output_item_types": [getattr(item, "type", None) for item in self._extract_output_items(response)],
            "error": self._serialize_value(getattr(response, "error", None)),
            "incomplete_details": self._serialize_value(getattr(response, "incomplete_details", None)),
        }
        logger.info("Agent response snapshot: %s", snapshot)

        if self.debug_raw_payloads:
            logger.info("Agent response raw payload: %s", self._serialize_value(response))

    def _log_stream_event(self, agent_type: str, agent_name: str, run_id: str, data: Any) -> None:
        if not self.debug_logging:
            return

        event_type = getattr(data, "type", None)
        logger.info(
            "Agent stream event: agent_type=%s agent_name=%s run_id=%s event_type=%s",
            agent_type,
            agent_name,
            run_id,
            event_type,
        )

        if self.debug_raw_payloads:
            logger.info("Agent stream raw payload: %s", self._serialize_value(data))

    def _validate_real_mode_dependencies(self) -> None:
        if AIProjectClient is None or DefaultAzureCredential is None:
            raise RuntimeError(
                "This service requires azure-ai-projects and azure-identity. "
                "Install backend requirements before using Azure AI Projects integration."
            )
        if not self.project_endpoint:
            raise RuntimeError("AZURE_AI_PROJECT_ENDPOINT is required.")

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

    def _extract_citations_from_annotations(self, response: Any) -> List[Citation]:
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

    def _extract_citations_from_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Citation]:
        citations: List[Citation] = []
        for tool_call in tool_calls:
            for document in tool_call.get("documents", []) or []:
                document_name = document.get("document") or document.get("blob_url") or document.get("uid")
                if not document_name:
                    continue
                citations.append(
                    Citation(
                        document=str(document_name),
                        chunk=document.get("uid"),
                        content=document.get("snippet"),
                    )
                )
        return citations

    def _merge_citations(self, *citation_lists: List[Citation]) -> List[Citation]:
        merged: List[Citation] = []
        seen: set[tuple[Optional[str], Optional[str], Optional[str]]] = set()

        for citation_list in citation_lists:
            for citation in citation_list:
                key = (citation.document, citation.chunk, citation.content)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(citation)

        return merged

    def _extract_token_usage(self, response: Any) -> Optional[Dict[str, int]]:
        usage = getattr(response, "usage", None)
        if not usage:
            return None

        usage_dict = self._serialize_value(usage)
        if not isinstance(usage_dict, dict):
            return None

        normalized: Dict[str, int] = {}
        for target_key, candidate_keys in {
            "input": ["input", "input_tokens", "prompt_tokens"],
            "output": ["output", "output_tokens", "completion_tokens"],
            "total": ["total", "total_tokens"],
        }.items():
            for candidate_key in candidate_keys:
                value = usage_dict.get(candidate_key)
                if isinstance(value, int):
                    normalized[target_key] = value
                    break

        if "total" not in normalized and {"input", "output"}.issubset(normalized):
            normalized["total"] = normalized["input"] + normalized["output"]

        return normalized or None

    def _count_retrievals(self, response: Any, tool_calls: List[Dict[str, Any]]) -> int:
        retrieved_count = sum(
            int(tool_call.get("retrieved_count") or 0)
            for tool_call in tool_calls
            if isinstance(tool_call.get("retrieved_count"), int)
        )
        if retrieved_count:
            return retrieved_count

        document_count = sum(len(tool_call.get("documents", []) or []) for tool_call in tool_calls)
        if document_count:
            return document_count

        return sum(1 for item in self._extract_output_items(response) if getattr(item, "type", None) in self._retrieval_item_types())

    def _count_subqueries(self, query_plan: Optional[Dict[str, Any]]) -> int:
        if not query_plan:
            return 0

        subqueries = query_plan.get("decomposed_queries") or query_plan.get("subqueries")
        return len(subqueries) if isinstance(subqueries, list) else 0

    def _extract_sources_used(
        self,
        citations: Iterable[Citation],
        tool_calls: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        seen = set()
        sources: List[str] = []
        for citation in citations:
            if citation.document not in seen:
                seen.add(citation.document)
                sources.append(citation.document)

        for tool_call in tool_calls or []:
            for source in tool_call.get("sources", []) or []:
                if source not in seen:
                    seen.add(source)
                    sources.append(source)

        return sources

    def _extract_query_plan(
        self,
        response: Any,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        reasoning: List[str] = []
        subqueries: List[str] = []
        tool_sequence: List[str] = []
        retrieved_sources: List[str] = []

        for item in self._extract_output_items(response):
            item_type = getattr(item, "type", None)
            if item_type == "reasoning":
                for summary in getattr(item, "summary", None) or []:
                    text = getattr(summary, "text", None)
                    if text:
                        reasoning.append(text)

        for tool_call in tool_calls or []:
            display_name = tool_call.get("display_name") or tool_call.get("tool_name") or tool_call.get("item_type")
            if display_name:
                tool_sequence.append(str(display_name))
            for query in tool_call.get("queries", []) or []:
                if query and query not in subqueries:
                    subqueries.append(str(query))
            for source in tool_call.get("sources", []) or []:
                if source and source not in retrieved_sources:
                    retrieved_sources.append(str(source))

        if not reasoning and not subqueries and not tool_sequence and not retrieved_sources:
            return None

        return {
            "retrieval_strategy": "agentic_tool_routing" if tool_sequence else "single_pass_generation",
            "reasoning": reasoning,
            "decomposed_queries": subqueries,
            "subqueries": subqueries,
            "tool_sequence": tool_sequence,
            "tool_calls": tool_calls or [],
            "retrieved_sources": retrieved_sources,
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
        events: List[TraceEvent] = []

        output_items = self._extract_output_items(response)
        reasoning_items = [item for item in output_items if getattr(item, "type", None) == "reasoning"]
        if reasoning_items:
            for item in reasoning_items:
                events.append(
                    TraceEvent(
                        timestamp=timestamp,
                        event_type="task_hypothesis_generated",
                        status="completed",
                        mode=agent_type,
                        metadata=self._build_output_item_metadata(item, run_id),
                    )
                )
            events.append(
                TraceEvent(
                    timestamp=timestamp,
                    event_type="answer_synthesis_started",
                    status="running",
                    mode=agent_type,
                    metadata={"run_id": run_id},
                )
            )
        else:
            events.append(
                TraceEvent(
                    timestamp=timestamp,
                    event_type="task_hypothesis_generated",
                    status="completed",
                    mode=agent_type,
                    metadata={"run_id": run_id},
                )
            )

        for item in output_items:
            item_type = getattr(item, "type", None)
            mapped = self._map_output_item_to_trace_event(item_type)
            if not mapped or item_type == "reasoning":
                continue
            events.append(
                TraceEvent(
                    timestamp=timestamp,
                    event_type=mapped,
                    status="completed",
                    mode=agent_type,
                    metadata=self._build_output_item_metadata(item, run_id),
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

    def _extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        return [
            self._build_tool_call_details(item)
            for item in self._extract_output_items(response)
            if getattr(item, "type", None) in self._tool_item_types()
        ]

    def _build_tool_call_details(self, item: Any) -> Dict[str, Any]:
        serialized = self._serialize_value(item)
        if not isinstance(serialized, dict):
            serialized = {"raw": serialized}

        item_type = getattr(item, "type", None) or serialized.get("type")
        arguments = self._parse_json_like(serialized.get("arguments"))
        if not isinstance(arguments, dict):
            arguments = {}

        output_details = self._parse_tool_output(serialized.get("output"))
        queries = self._unique_strings(
            [
                *[str(query) for query in arguments.get("queries", []) or [] if query],
                str(arguments["query"]) if arguments.get("query") else "",
                str(serialized["query"]) if serialized.get("query") else "",
            ]
        )

        documents = output_details.get("documents", []) or []
        sources = self._unique_strings(
            [self._source_label_from_document(document) for document in documents]
        )

        return {
            "item_type": item_type,
            "tool_name": str(serialized.get("name") or item_type or "tool_call"),
            "display_name": str(serialized.get("name") or serialized.get("server_label") or item_type or "tool_call"),
            "server_label": serialized.get("server_label"),
            "status": serialized.get("status"),
            "arguments": arguments,
            "raw_arguments": serialized.get("arguments"),
            "queries": queries,
            "retrieved_count": output_details.get("retrieved_count"),
            "documents": documents,
            "sources": sources,
            "output_preview": output_details.get("output_preview"),
        }

    def _build_output_item_metadata(self, item: Any, run_id: str) -> Dict[str, Any]:
        item_type = getattr(item, "type", None)
        metadata: Dict[str, Any] = {
            "run_id": run_id,
            "item_type": item_type,
        }

        if item_type == "reasoning":
            reasoning = [
                summary.text
                for summary in getattr(item, "summary", None) or []
                if getattr(summary, "text", None)
            ]
            metadata["reasoning"] = reasoning
            if reasoning:
                metadata["hypothesis"] = reasoning[0]
            return metadata

        if item_type in self._tool_item_types() or item_type in self._retrieval_item_types():
            tool_details = self._build_tool_call_details(item)
            metadata.update(
                {
                    "tool_name": tool_details.get("tool_name"),
                    "server_label": tool_details.get("server_label"),
                    "queries": tool_details.get("queries", []),
                    "retrieved_count": tool_details.get("retrieved_count"),
                    "sources": tool_details.get("sources", []),
                    "documents": tool_details.get("documents", []),
                    "output_preview": tool_details.get("output_preview"),
                }
            )
            return metadata

        metadata["item"] = self._serialize_value(item)
        return metadata

    def _parse_tool_output(self, output: Any) -> Dict[str, Any]:
        if isinstance(output, str):
            retrieved_count = self._parse_retrieved_count(output)
            documents = self._parse_retrieved_documents(output)
            if retrieved_count is not None or documents:
                return {
                    "retrieved_count": retrieved_count,
                    "documents": documents,
                    "output_preview": self._truncate_text(output, 280),
                }
            return {"output_preview": self._truncate_text(output, 280)}

        if isinstance(output, dict):
            return {"output_preview": self._truncate_text(json.dumps(output), 280)}

        return {}

    def _parse_retrieved_count(self, output_text: str) -> Optional[int]:
        match = re.search(r"Retrieved\s+(\d+)\s+documents", output_text, flags=re.IGNORECASE)
        if not match:
            return None
        return int(match.group(1))

    def _parse_retrieved_documents(self, output_text: str) -> List[Dict[str, Any]]:
        matches = re.finditer(
            r"【[^】]+†source】\s*(\{.*?\})(?=\s*【[^】]+†source】|\s*Visible:|\s*$)",
            output_text,
            flags=re.DOTALL,
        )
        documents: List[Dict[str, Any]] = []

        for match in matches:
            payload = match.group(1).strip()
            try:
                document = json.loads(payload)
            except json.JSONDecodeError:
                continue
            documents.append(self._normalize_retrieved_document(document))

        return documents

    def _normalize_retrieved_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "uid": document.get("uid"),
            "blob_url": document.get("blob_url"),
            "document": self._source_label_from_document(document),
            "snippet": self._truncate_text(document.get("snippet"), 320),
        }

    def _source_label_from_document(self, document: Dict[str, Any]) -> str:
        blob_url = document.get("blob_url") if isinstance(document, dict) else None
        if isinstance(blob_url, str) and blob_url:
            parsed = urlparse(blob_url)
            if parsed.path:
                name = PurePosixPath(parsed.path).name
                if name:
                    return name

        if isinstance(document, dict):
            for key in ("document", "title", "filename", "uid"):
                value = document.get(key)
                if isinstance(value, str) and value:
                    return value

        return "unknown-source"

    def _parse_json_like(self, value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return value
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def _unique_strings(self, values: Iterable[str]) -> List[str]:
        seen = set()
        result: List[str] = []
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result

    def _truncate_text(self, value: Any, max_length: int) -> Optional[str]:
        if not isinstance(value, str) or not value:
            return None
        text = value.strip()
        if len(text) <= max_length:
            return text
        return f"{text[: max_length - 3].rstrip()}..."

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
