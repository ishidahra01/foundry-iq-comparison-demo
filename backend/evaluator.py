"""
Evaluation helpers for comparing agent outputs against JSONL ground-truth cases.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from models import (
    AgentResult,
    ComparisonEvaluation,
    EvaluationCase,
    EvaluationCaseSummary,
    EvaluationEvidence,
    EvaluationReport,
)

try:
    from azure.ai.projects.aio import AIProjectClient
    from azure.identity.aio import DefaultAzureCredential
except ImportError:
    AIProjectClient = None
    DefaultAzureCredential = None


logger = logging.getLogger(__name__)


EVALUATION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "overall_summary",
        "winner",
        "winner_reason",
        "classic_rag",
        "foundry_iq",
    ],
    "properties": {
        "overall_summary": {"type": "string"},
        "winner": {"type": "string", "enum": ["classic-rag", "foundry-iq", "tie"]},
        "winner_reason": {"type": "string"},
        "classic_rag": {"$ref": "#/$defs/answerEvaluation"},
        "foundry_iq": {"$ref": "#/$defs/answerEvaluation"},
    },
    "$defs": {
        "answerEvaluation": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "overall_score",
                "correctness_score",
                "completeness_score",
                "evidence_alignment_score",
                "summary",
                "strengths",
                "gaps",
                "unsupported_claims",
            ],
            "properties": {
                "overall_score": {"type": "integer", "minimum": 1, "maximum": 5},
                "correctness_score": {"type": "integer", "minimum": 1, "maximum": 5},
                "completeness_score": {"type": "integer", "minimum": 1, "maximum": 5},
                "evidence_alignment_score": {"type": "integer", "minimum": 1, "maximum": 5},
                "summary": {"type": "string"},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "gaps": {"type": "array", "items": {"type": "string"}},
                "unsupported_claims": {"type": "array", "items": {"type": "string"}},
            },
        }
    },
}


class EvaluationService:
    """Loads evaluation samples and evaluates comparison outputs using a Foundry-hosted model."""

    def __init__(self, project_endpoint: Optional[str], mock_mode: bool = False):
        self.project_endpoint = project_endpoint
        self.mock_mode = mock_mode
        self.evaluator_model = os.getenv("EVALUATION_MODEL") or os.getenv("EVALUATION_MODEL_DEPLOYMENT")
        self.sample_file = self._resolve_sample_file()

    def list_sample_cases(self) -> List[EvaluationCaseSummary]:
        cases = self._load_cases_from_file(self.sample_file)
        return [
            EvaluationCaseSummary(
                id=case.id,
                question=case.question,
                line_number=case.line_number,
                source_file=case.source_file,
                is_default=case.is_default,
            )
            for case in cases
        ]

    def resolve_case(self, sample_id: Optional[str] = None, raw_jsonl: Optional[str] = None) -> EvaluationCase:
        if raw_jsonl and raw_jsonl.strip():
            return self._parse_first_jsonl_case(raw_jsonl)

        cases = self._load_cases_from_file(self.sample_file)
        if sample_id:
            for case in cases:
                if case.id == sample_id:
                    return case
            raise ValueError(f"Evaluation sample '{sample_id}' was not found")

        default_case = next((case for case in cases if case.is_default), None)
        if default_case:
            return default_case

        raise ValueError("No evaluation case available")

    async def evaluate_answers(
        self,
        evaluation_case: EvaluationCase,
        classic_result: AgentResult,
        foundry_result: AgentResult,
    ) -> ComparisonEvaluation:
        if self.mock_mode:
            return self._build_mock_evaluation(evaluation_case, classic_result, foundry_result)

        if not self.evaluator_model:
            return ComparisonEvaluation(
                status="not_configured",
                error="EVALUATION_MODEL is not set. Configure a Foundry deployment name for LLM-based evaluation.",
            )

        if AIProjectClient is None or DefaultAzureCredential is None:
            return ComparisonEvaluation(
                status="failed",
                evaluator_model=self.evaluator_model,
                error="azure-ai-projects and azure-identity are required for LLM-based evaluation.",
            )

        if not self.project_endpoint:
            return ComparisonEvaluation(
                status="failed",
                evaluator_model=self.evaluator_model,
                error="AZURE_AI_PROJECT_ENDPOINT is required for LLM-based evaluation.",
            )

        prompt = self._build_evaluation_prompt(evaluation_case, classic_result, foundry_result)

        try:
            async with (
                DefaultAzureCredential() as credential,
                AIProjectClient(endpoint=self.project_endpoint, credential=credential) as project_client,
                project_client.get_openai_client() as openai_client,
            ):
                response = await openai_client.responses.create(
                    model=self.evaluator_model,
                    input=prompt,
                    temperature=0,
                    max_output_tokens=1800,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "comparison_evaluation",
                            "strict": True,
                            "description": "Evaluation report comparing Classic RAG and Foundry IQ answers against the ground truth.",
                            "schema": EVALUATION_SCHEMA,
                        },
                        "verbosity": "low",
                    },
                )

            output_text = getattr(response, "output_text", None)
            if not output_text:
                raise ValueError("Evaluator response did not contain output_text")

            payload = json.loads(output_text)
            report = EvaluationReport.model_validate(payload)
            return ComparisonEvaluation(
                status="completed",
                evaluator_model=self.evaluator_model,
                report=report,
            )
        except Exception as exc:
            logger.exception("Evaluation failed")
            return ComparisonEvaluation(
                status="failed",
                evaluator_model=self.evaluator_model,
                error=str(exc),
            )

    def _resolve_sample_file(self) -> Path:
        return Path(__file__).resolve().parents[1] / "sample-data" / "zava-sample" / "agentic_retrieval_eval_10.jsonl"

    def _load_cases_from_file(self, file_path: Path) -> List[EvaluationCase]:
        if not file_path.exists():
            raise FileNotFoundError(f"Evaluation sample file not found: {file_path}")

        cases: List[EvaluationCase] = []
        with file_path.open("r", encoding="utf-8") as handle:
            for index, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                cases.append(
                    EvaluationCase(
                        id=payload["id"],
                        question=payload["question"],
                        ideal_answer=payload["ideal_answer"],
                        evidence=[EvaluationEvidence(**item) for item in payload.get("evidence", [])],
                        line_number=index,
                        source_file=str(file_path.name),
                        is_default=payload["id"] == "zava_agentic_004",
                    )
                )
        return cases

    def _parse_first_jsonl_case(self, raw_jsonl: str) -> EvaluationCase:
        for index, line in enumerate(raw_jsonl.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            return EvaluationCase(
                id=payload.get("id", "pasted_case"),
                question=payload["question"],
                ideal_answer=payload["ideal_answer"],
                evidence=[EvaluationEvidence(**item) for item in payload.get("evidence", [])],
                line_number=index,
                source_file="pasted-jsonl",
                is_default=False,
            )
        raise ValueError("No valid JSONL row found in evaluation_jsonl")

    def _build_evaluation_prompt(
        self,
        evaluation_case: EvaluationCase,
        classic_result: AgentResult,
        foundry_result: AgentResult,
    ) -> str:
        payload = {
            "question": evaluation_case.question,
            "ground_truth": {
                "ideal_answer": evaluation_case.ideal_answer,
                "evidence": [item.model_dump() for item in evaluation_case.evidence],
            },
            "answers": {
                "classic_rag": {
                    "answer": classic_result.answer,
                    "sources_used": classic_result.sources_used,
                    "citations": [citation.model_dump() for citation in classic_result.citations],
                },
                "foundry_iq": {
                    "answer": foundry_result.answer,
                    "sources_used": foundry_result.sources_used,
                    "citations": [citation.model_dump() for citation in foundry_result.citations],
                },
            },
        }

        return (
            "You are evaluating two RAG-style answers against a ground-truth answer and evidence. "
            "Score each answer on correctness, completeness, and evidence alignment from 1 to 5. "
            "Be strict, concise, and focus on factual agreement with the ground truth. "
            "Write every natural-language field in the same language used by the ground-truth question and ideal answer. "
            "This includes overall_summary, winner_reason, summary, strengths, gaps, and unsupported_claims. "
            "Return only the structured JSON requested by the schema.\n\n"
            f"Evaluation payload:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )

    def _build_mock_evaluation(
        self,
        evaluation_case: EvaluationCase,
        classic_result: AgentResult,
        foundry_result: AgentResult,
    ) -> ComparisonEvaluation:
        report = EvaluationReport(
            overall_summary="Mock evaluation mode is active. Scores are placeholder values and should be replaced by a Foundry-hosted evaluator model for real assessment.",
            winner="foundry-iq",
            winner_reason="Mock mode defaults to Foundry IQ as the stronger answer to keep the evaluation UI testable.",
            classic_rag={
                "overall_score": 3,
                "correctness_score": 3,
                "completeness_score": 2,
                "evidence_alignment_score": 3,
                "summary": "Mock evaluation placeholder for Classic RAG.",
                "strengths": ["UI wiring test only"],
                "gaps": ["Replace with real evaluator model for meaningful scoring"],
                "unsupported_claims": [],
            },
            foundry_iq={
                "overall_score": 4,
                "correctness_score": 4,
                "completeness_score": 4,
                "evidence_alignment_score": 4,
                "summary": "Mock evaluation placeholder for Foundry IQ.",
                "strengths": ["UI wiring test only"],
                "gaps": ["Replace with real evaluator model for meaningful scoring"],
                "unsupported_claims": [],
            },
        )
        return ComparisonEvaluation(
            status="completed",
            evaluator_model="mock-evaluator",
            report=report,
        )