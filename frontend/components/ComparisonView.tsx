"use client";

import { useState } from "react";
import AgentResultPanel from "./AgentResultPanel";
import ProcessingWindow from "./ProcessingWindow";
import {
  GitCompare,
  Activity,
  GitBranch,
  Network,
  Database,
  FileSearch,
  ClipboardCheck,
  Trophy,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";

interface ComparisonViewProps {
  data: any;
}

export default function ComparisonView({ data }: ComparisonViewProps) {
  const [activeTab, setActiveTab] = useState<"comparison" | "timeline">("comparison");
  const classicQueries = getQueryCount(data.classic_rag);
  const foundryQueries = getQueryCount(data.foundry_iq);
  const classicSources = getSourceCount(data.classic_rag);
  const foundrySources = getSourceCount(data.foundry_iq);
  const classicTools = getToolCount(data.classic_rag);
  const foundryTools = getToolCount(data.foundry_iq);
  const classicRetrievals = data.classic_rag?.metrics?.retrieval_count ?? 0;
  const foundryRetrievals = data.foundry_iq?.metrics?.retrieval_count ?? 0;

  return (
    <div className="space-y-6">
      {/* Question Display */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
        <h2 className="text-sm font-medium text-slate-500 mb-2">Question</h2>
        <p className="text-lg text-slate-900">{data.question}</p>
        <div className="flex items-center gap-4 mt-4 text-sm text-slate-600">
          <span>Run ID: {data.run_id}</span>
          <span>•</span>
          <span>{new Date(data.timestamp).toLocaleString()}</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-slate-200">
        <button
          onClick={() => setActiveTab("comparison")}
          className={`flex items-center gap-2 px-4 py-3 font-medium border-b-2 transition-colors ${
            activeTab === "comparison"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-600 hover:text-slate-900"
          }`}
        >
          <GitCompare className="w-4 h-4" />
          Side-by-Side Comparison
        </button>
        <button
          onClick={() => setActiveTab("timeline")}
          className={`flex items-center gap-2 px-4 py-3 font-medium border-b-2 transition-colors ${
            activeTab === "timeline"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-600 hover:text-slate-900"
          }`}
        >
          <Activity className="w-4 h-4" />
          Processing Timeline
        </button>
      </div>

      {/* Content */}
      {activeTab === "comparison" ? (
        <div className="space-y-6">
          {data.evaluation_case && (
            <section className="rounded-xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-white p-6 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">
                    Ground Truth Evaluation
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">
                    Sample-backed answer assessment using a Foundry-hosted evaluator model over Entra authentication.
                  </p>
                </div>
                <div className="rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs font-medium text-emerald-700">
                  {data.evaluation_case.id}
                </div>
              </div>

              <div className="mt-5 grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                  <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                    <ClipboardCheck className="h-4 w-4 text-emerald-600" />
                    Ground Truth
                  </div>
                  <div className="mt-3 text-sm text-slate-700">
                    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                      {data.evaluation_case.question}
                    </div>
                    <div className="mt-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 leading-relaxed text-emerald-950">
                      {data.evaluation_case.ideal_answer}
                    </div>
                  </div>

                  {Array.isArray(data.evaluation_case.evidence) && data.evaluation_case.evidence.length > 0 && (
                    <div className="mt-4">
                      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Evidence
                      </div>
                      <div className="mt-2 space-y-2">
                        {data.evaluation_case.evidence.map((item: any, index: number) => (
                          <div
                            key={`${item.document}-${index}`}
                            className="rounded-lg border border-slate-200 bg-slate-50 p-3"
                          >
                            <div className="text-xs font-medium text-slate-500">{item.document}</div>
                            <div className="mt-1 text-sm leading-relaxed text-slate-700">{item.quote}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <EvaluationPanel evaluation={data.evaluation} />
                </div>
              </div>
            </section>
          )}

          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">
                  Agentic Retrieval Differences
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  Deterministic comparison of how each system searched, routed tools, and gathered evidence.
                </p>
              </div>
              <div className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                Foundry IQ vs Classic RAG
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <DifferenceCard
                title="Query Expansion"
                icon={GitBranch}
                classicValue={classicQueries}
                foundryValue={foundryQueries}
                deltaLabel={formatDelta(foundryQueries - classicQueries, "more planned")}
                description="How many distinct search intents were executed."
              />
              <DifferenceCard
                title="Tool Routing"
                icon={Network}
                classicValue={classicTools}
                foundryValue={foundryTools}
                deltaLabel={formatDelta(foundryTools - classicTools, "more tool runs")}
                description="How often the system invoked retrieval or external tools."
              />
              <DifferenceCard
                title="Source Reach"
                icon={Database}
                classicValue={classicSources}
                foundryValue={foundrySources}
                deltaLabel={formatDelta(foundrySources - classicSources, "more sources")}
                description="Unique sources referenced in the returned result."
              />
              <DifferenceCard
                title="Evidence Volume"
                icon={FileSearch}
                classicValue={classicRetrievals}
                foundryValue={foundryRetrievals}
                deltaLabel={formatDelta(foundryRetrievals - classicRetrievals, "more retrieved docs")}
                description="Retrieved documents or result items inspected during execution."
              />
            </div>
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AgentResultPanel
              result={data.classic_rag}
              agentType="classic-rag"
              agentLabel="Classic RAG"
            />
            <AgentResultPanel
              result={data.foundry_iq}
              agentType="foundry-iq"
              agentLabel="Foundry IQ"
            />
          </div>
        </div>
      ) : (
        <ProcessingWindow
          classicEvents={data.classic_rag.trace_events}
          foundryIqEvents={data.foundry_iq.trace_events}
        />
      )}
    </div>
  );
}

function EvaluationPanel({ evaluation }: { evaluation: any }) {
  if (!evaluation) {
    return null;
  }

  if (evaluation.status !== "completed" || !evaluation.report) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        <div className="flex items-center gap-2 font-semibold">
          <AlertTriangle className="h-4 w-4" />
          Evaluation unavailable
        </div>
        <div className="mt-2 leading-relaxed">
          {evaluation.error || "The evaluation result was not available for this run."}
        </div>
      </div>
    );
  }

  const report = evaluation.report;

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <Trophy className="h-4 w-4 text-amber-500" />
          Evaluation Summary
        </div>
        <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm leading-relaxed text-slate-700">
          {report.overall_summary}
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
          <span className="rounded-full bg-emerald-50 px-3 py-1 font-medium text-emerald-700">
            Winner: {report.winner === "foundry-iq" ? "Foundry IQ" : report.winner === "classic-rag" ? "Classic RAG" : "Tie"}
          </span>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">
            Evaluator: {evaluation.evaluator_model || "unknown"}
          </span>
        </div>
        <div className="mt-3 text-sm text-slate-600">{report.winner_reason}</div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <AnswerEvaluationCard
          title="Classic RAG"
          tone="slate"
          evaluation={report.classic_rag}
        />
        <AnswerEvaluationCard
          title="Foundry IQ"
          tone="blue"
          evaluation={report.foundry_iq}
        />
      </div>
    </div>
  );
}

function AnswerEvaluationCard({
  title,
  tone,
  evaluation,
}: {
  title: string;
  tone: "slate" | "blue";
  evaluation: any;
}) {
  const toneClass =
    tone === "blue"
      ? {
          panel: "border-blue-200 bg-blue-50",
          badge: "bg-blue-100 text-blue-700",
        }
      : {
          panel: "border-slate-200 bg-slate-50",
          badge: "bg-slate-200 text-slate-700",
        };

  return (
    <div className={`rounded-xl border p-4 shadow-sm ${toneClass.panel}`}>
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <ShieldCheck className="h-4 w-4" />
          {title}
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${toneClass.badge}`}>
          Overall {evaluation.overall_score}/5
        </span>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-3">
        <ScoreBox label="Correctness" value={evaluation.correctness_score} />
        <ScoreBox label="Completeness" value={evaluation.completeness_score} />
        <ScoreBox label="Evidence" value={evaluation.evidence_alignment_score} />
      </div>

      <div className="mt-4 rounded-lg border border-white/70 bg-white/80 p-3 text-sm leading-relaxed text-slate-700">
        {evaluation.summary}
      </div>

      {evaluation.strengths?.length > 0 && (
        <div className="mt-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Strengths</div>
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {evaluation.strengths.map((item: string, index: number) => (
              <li key={`${title}-strength-${index}`}>• {item}</li>
            ))}
          </ul>
        </div>
      )}

      {evaluation.gaps?.length > 0 && (
        <div className="mt-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Gaps</div>
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {evaluation.gaps.map((item: string, index: number) => (
              <li key={`${title}-gap-${index}`}>• {item}</li>
            ))}
          </ul>
        </div>
      )}

      {evaluation.unsupported_claims?.length > 0 && (
        <div className="mt-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Unsupported Claims</div>
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {evaluation.unsupported_claims.map((item: string, index: number) => (
              <li key={`${title}-unsupported-${index}`}>• {item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ScoreBox({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-center">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-slate-900">{value}/5</div>
    </div>
  );
}

function DifferenceCard({
  title,
  icon: Icon,
  classicValue,
  foundryValue,
  deltaLabel,
  description,
}: {
  title: string;
  icon: any;
  classicValue: number;
  foundryValue: number;
  deltaLabel: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">{title}</div>
          <div className="mt-1 text-xs text-slate-500">{description}</div>
        </div>
        <div className="rounded-full bg-white p-2 shadow-sm">
          <Icon className="h-4 w-4 text-blue-600" />
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <MetricPill label="Classic" value={classicValue} tone="slate" />
        <MetricPill label="Foundry IQ" value={foundryValue} tone="blue" />
      </div>

      <div className="mt-3 text-xs font-medium text-blue-700">{deltaLabel}</div>
    </div>
  );
}

function MetricPill({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "slate" | "blue";
}) {
  const toneClass =
    tone === "blue"
      ? "border-blue-200 bg-blue-50 text-blue-900"
      : "border-slate-200 bg-white text-slate-900";

  return (
    <div className={`rounded-lg border px-3 py-2 ${toneClass}`}>
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold">{value}</div>
    </div>
  );
}

function getQueryCount(result: any) {
  return (
    result?.query_plan?.decomposed_queries?.length ??
    result?.metrics?.subquery_count ??
    (result?.answer ? 1 : 0)
  );
}

function getSourceCount(result: any) {
  return Array.isArray(result?.sources_used) ? result.sources_used.length : 0;
}

function getToolCount(result: any) {
  return (
    result?.query_plan?.tool_calls?.length ??
    result?.metrics?.tool_calls ??
    0
  );
}

function formatDelta(delta: number, label: string) {
  if (delta > 0) {
    return `+${delta} ${label}`;
  }
  if (delta < 0) {
    return `${delta} ${label}`;
  }
  return `0 ${label}`;
}
