"use client";

import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  FileText,
  ChevronDown,
  ChevronUp,
  Database,
  Zap,
  TrendingUp,
  GitBranch,
  Network,
  Cpu,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface AgentResultPanelProps {
  result: any;
  agentType: "classic-rag" | "foundry-iq";
  agentLabel: string;
}

const VERDICT_ICONS = {
  Go: CheckCircle2,
  Conditional: AlertTriangle,
  "No-Go": XCircle,
};

const VERDICT_COLORS = {
  Go: "text-green-600 bg-green-50 border-green-200",
  Conditional: "text-yellow-600 bg-yellow-50 border-yellow-200",
  "No-Go": "text-red-600 bg-red-50 border-red-200",
};

export default function AgentResultPanel({
  result,
  agentType,
  agentLabel,
}: AgentResultPanelProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["answer", "plan", "tools"])
  );

  const citations = Array.isArray(result.citations) ? result.citations : [];
  const sourcesUsed = Array.isArray(result.sources_used) ? result.sources_used : [];
  const traceEvents = Array.isArray(result.trace_events) ? result.trace_events : [];
  const queryPlan = result.query_plan ?? null;
  const toolCalls = Array.isArray(queryPlan?.tool_calls) ? queryPlan.tool_calls : [];
  const tokenUsage = normalizeTokenUsage(result.metrics?.token_usage);

  const metricCards = [
    {
      label: "Time",
      value: `${((result.metrics?.total_time_ms ?? 0) / 1000).toFixed(2)}s`,
    },
    ...(sourcesUsed.length > 0
      ? [{ label: "Sources", value: sourcesUsed.length }]
      : []),
    ...(citations.length > 0
      ? [{ label: "Citations", value: citations.length }]
      : []),
    {
      label: "Queries",
      value:
        queryPlan?.decomposed_queries?.length || result.metrics?.subquery_count || 1,
    },
  ];

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  const VerdictIcon = result.verdict ? VERDICT_ICONS[result.verdict as keyof typeof VERDICT_ICONS] : null;
  const verdictColor = result.verdict ? VERDICT_COLORS[result.verdict as keyof typeof VERDICT_COLORS] : "";

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div
        className={`p-4 border-b ${
          agentType === "classic-rag"
            ? "bg-slate-50 border-slate-200"
            : "bg-blue-50 border-blue-200"
        }`}
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-slate-900">{agentLabel}</h3>
          {result.verdict && VerdictIcon && (
            <div
              className={`flex items-center gap-2 px-3 py-1 rounded-full border ${verdictColor}`}
            >
              <VerdictIcon className="w-4 h-4" />
              <span className="text-sm font-medium">{result.verdict}</span>
            </div>
          )}
        </div>

        {/* Metrics */}
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {metricCards.map((card) => (
            <div
              key={card.label}
              className="rounded-lg border border-slate-200 bg-white/70 px-3 py-2 text-center"
            >
              <div className="text-xs text-slate-600 mb-1">{card.label}</div>
              <div className="text-sm font-semibold text-slate-900">{card.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="divide-y divide-slate-200">
        {/* Answer Section */}
        <Section
          title="Answer"
          icon={FileText}
          isExpanded={expandedSections.has("answer")}
          onToggle={() => toggleSection("answer")}
        >
          <div className="prose prose-sm max-w-none prose-slate prose-headings:text-slate-900 prose-strong:text-slate-900 prose-code:text-sky-700">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {result.answer || "No answer returned."}
            </ReactMarkdown>
          </div>
        </Section>

        {queryPlan && hasQueryPlanContent(queryPlan) && (
          <Section
            title="Query Plan"
            icon={GitBranch}
            count={queryPlan.decomposed_queries?.length || undefined}
            isExpanded={expandedSections.has("plan")}
            onToggle={() => toggleSection("plan")}
          >
            <div className="space-y-4">
              {queryPlan.retrieval_strategy && (
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Strategy
                  </div>
                  <div className="mt-1 text-sm font-semibold text-slate-900">
                    {queryPlan.retrieval_strategy}
                  </div>
                </div>
              )}

              {Array.isArray(queryPlan.reasoning) && queryPlan.reasoning.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-700 mb-2">Reasoning</h4>
                  <div className="space-y-2">
                    {queryPlan.reasoning.map((reason: string, index: number) => (
                      <div
                        key={`${reason}-${index}`}
                        className="rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-700"
                      >
                        {reason}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {Array.isArray(queryPlan.decomposed_queries) &&
                queryPlan.decomposed_queries.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-slate-700 mb-2">Decomposed Queries</h4>
                    <div className="space-y-2">
                      {queryPlan.decomposed_queries.map((query: string, index: number) => (
                        <div
                          key={`${query}-${index}`}
                          className="rounded-lg border border-blue-200 bg-blue-50 p-3"
                        >
                          <div className="text-[11px] font-semibold uppercase tracking-wide text-blue-700">
                            Query {index + 1}
                          </div>
                          <div className="mt-1 text-sm text-blue-950">{query}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {Array.isArray(queryPlan.tool_sequence) && queryPlan.tool_sequence.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-700 mb-2">Tool Sequence</h4>
                  <div className="flex flex-wrap gap-2">
                    {queryPlan.tool_sequence.map((tool: string, index: number) => (
                      <span
                        key={`${tool}-${index}`}
                        className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700"
                      >
                        {tool}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Section>
        )}

        {toolCalls.length > 0 && (
          <Section
            title="Tool Execution"
            icon={Network}
            count={toolCalls.length}
            isExpanded={expandedSections.has("tools")}
            onToggle={() => toggleSection("tools")}
          >
            <div className="space-y-4">
              {toolCalls.map((toolCall: any, index: number) => {
                const documents = Array.isArray(toolCall.documents) ? toolCall.documents : [];
                const visibleDocuments = documents.slice(0, 8);
                const remainingDocuments = Math.max(documents.length - visibleDocuments.length, 0);

                return (
                  <div
                    key={`${toolCall.tool_name || toolCall.display_name || "tool"}-${index}`}
                    className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <div className="text-sm font-semibold text-slate-900">
                          {toolCall.tool_name || toolCall.display_name || "Tool Call"}
                        </div>
                        {toolCall.server_label && (
                          <div className="mt-1 font-mono text-xs text-slate-500">
                            {toolCall.server_label}
                          </div>
                        )}
                      </div>
                      <div className="flex gap-2 text-xs">
                        {typeof toolCall.retrieved_count === "number" && (
                          <span className="rounded-full bg-blue-50 px-3 py-1 font-medium text-blue-700">
                            {toolCall.retrieved_count} docs
                          </span>
                        )}
                        {toolCall.item_type && (
                          <span className="rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-600">
                            {toolCall.item_type}
                          </span>
                        )}
                      </div>
                    </div>

                    {Array.isArray(toolCall.queries) && toolCall.queries.length > 0 && (
                      <div className="mt-4">
                        <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                          Invoked With
                        </div>
                        <div className="space-y-2">
                          {toolCall.queries.map((query: string, queryIndex: number) => (
                            <div
                              key={`${query}-${queryIndex}`}
                              className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-950"
                            >
                              {query}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {Array.isArray(toolCall.sources) && toolCall.sources.length > 0 && (
                      <div className="mt-4">
                        <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                          Sources Reached
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {toolCall.sources.map((source: string, sourceIndex: number) => (
                            <span
                              key={`${source}-${sourceIndex}`}
                              className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700"
                            >
                              {source}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {visibleDocuments.length > 0 && (
                      <div className="mt-4 space-y-3">
                        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                          Retrieved Documents
                        </div>
                        {visibleDocuments.map((document: any, documentIndex: number) => (
                          <div
                            key={`${document.uid || document.document || "document"}-${documentIndex}`}
                            className="rounded-lg border border-slate-200 bg-slate-50 p-3"
                          >
                            <div className="text-sm font-medium text-slate-900">
                              {document.document || document.blob_url || document.uid}
                            </div>
                            {document.snippet && (
                              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                                {document.snippet}
                              </p>
                            )}
                          </div>
                        ))}
                        {remainingDocuments > 0 && (
                          <div className="text-xs text-slate-500">
                            {remainingDocuments} more documents omitted from this view.
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </Section>
        )}

        {/* Citations Section */}
        {citations.length > 0 && (
          <Section
            title="Citations"
            icon={Database}
            count={citations.length}
            isExpanded={expandedSections.has("citations")}
            onToggle={() => toggleSection("citations")}
          >
            <div className="space-y-3">
              {citations.map((citation: any, index: number) => (
                <div
                  key={index}
                  className="p-3 bg-slate-50 rounded-lg border border-slate-200"
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="font-mono text-xs text-blue-600">
                      {citation.document}
                    </span>
                    {citation.relevance_score && (
                      <span className="text-xs text-slate-500">
                        {(citation.relevance_score * 100).toFixed(0)}% relevant
                      </span>
                    )}
                  </div>
                  {citation.content && (
                    <p className="text-sm text-slate-600">{citation.content}</p>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Execution Details */}
        <Section
          title="Execution Details"
          icon={Cpu}
          isExpanded={expandedSections.has("execution")}
          onToggle={() => toggleSection("execution")}
        >
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-slate-700 mb-2">
                Performance Metrics
              </h4>
              <div className="grid grid-cols-2 gap-3">
                <MetricItem
                  label="Total Time"
                  value={`${((result.metrics?.total_time_ms ?? 0) / 1000).toFixed(2)}s`}
                />
                <MetricItem
                  label="Retrieval Count"
                  value={result.metrics?.retrieval_count ?? 0}
                />
                <MetricItem
                  label="Tool Calls"
                  value={result.metrics?.tool_calls ?? toolCalls.length}
                />
                <MetricItem
                  label="Queries"
                  value={queryPlan?.decomposed_queries?.length || result.metrics?.subquery_count || 0}
                />
                {tokenUsage && (
                  <>
                    <MetricItem
                      label="Input Tokens"
                      value={tokenUsage.input ?? "-"}
                    />
                    <MetricItem
                      label="Output Tokens"
                      value={tokenUsage.output ?? "-"}
                    />
                    <MetricItem label="Total Tokens" value={tokenUsage.total ?? "-"} />
                  </>
                )}
              </div>
            </div>

            {sourcesUsed.length > 0 && (
              <div>
              <h4 className="text-sm font-medium text-slate-700 mb-2">
                Sources Used
              </h4>
              <div className="space-y-1">
                {sourcesUsed.map((source: string, index: number) => (
                  <div
                    key={index}
                    className="text-xs font-mono text-slate-600 bg-slate-50 px-2 py-1 rounded"
                  >
                    {source}
                  </div>
                ))}
              </div>
              </div>
            )}
          </div>
        </Section>

        {/* Trace Events */}
        <Section
          title="Trace Events"
          icon={TrendingUp}
          count={traceEvents.length}
          isExpanded={expandedSections.has("trace")}
          onToggle={() => toggleSection("trace")}
        >
          <div className="space-y-2">
            {traceEvents.map((event: any, index: number) => (
              <div
                key={index}
                className="flex items-start gap-3 p-2 hover:bg-slate-50 rounded"
              >
                <div className="flex-shrink-0 mt-0.5">
                  <EventStatusIcon status={event.status} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700">
                      {event.event_type.replace(/_/g, " ")}
                    </span>
                    {event.elapsed_ms && (
                      <span className="text-xs text-slate-500">
                        {event.elapsed_ms}ms
                      </span>
                    )}
                  </div>
                  {Object.keys(event.metadata).length > 0 && (
                    <div className="mt-2">{renderTraceMetadata(event.metadata)}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Section>
      </div>
    </div>
  );
}

function Section({
  title,
  icon: Icon,
  count,
  isExpanded,
  onToggle,
  children,
}: {
  title: string;
  icon: any;
  count?: number;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-slate-600" />
          <span className="font-medium text-slate-900">{title}</span>
          {count !== undefined && (
            <span className="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              {count}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>
      {isExpanded && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}

function MetricItem({ label, value }: { label: string; value: any }) {
  return (
    <div className="bg-slate-50 p-2 rounded">
      <div className="text-xs text-slate-600">{label}</div>
      <div className="text-sm font-semibold text-slate-900">{value}</div>
    </div>
  );
}

function EventStatusIcon({ status }: { status: string }) {
  switch (status) {
    case "completed":
      return <CheckCircle2 className="w-4 h-4 text-green-600" />;
    case "failed":
      return <XCircle className="w-4 h-4 text-red-600" />;
    case "running":
      return <Clock className="w-4 h-4 text-blue-600 animate-pulse" />;
    default:
      return <Clock className="w-4 h-4 text-slate-400" />;
  }
}

function normalizeTokenUsage(tokenUsage?: Record<string, number>) {
  if (!tokenUsage) {
    return null;
  }

  const input = tokenUsage.input ?? tokenUsage.input_tokens ?? tokenUsage.prompt_tokens;
  const output = tokenUsage.output ?? tokenUsage.output_tokens ?? tokenUsage.completion_tokens;
  const total = tokenUsage.total ?? tokenUsage.total_tokens ?? ((input ?? 0) + (output ?? 0) || undefined);

  if (input === undefined && output === undefined && total === undefined) {
    return null;
  }

  return { input, output, total };
}

function hasQueryPlanContent(queryPlan: any) {
  return Boolean(
    queryPlan?.retrieval_strategy ||
      (Array.isArray(queryPlan?.reasoning) && queryPlan.reasoning.length > 0) ||
      (Array.isArray(queryPlan?.decomposed_queries) && queryPlan.decomposed_queries.length > 0) ||
      (Array.isArray(queryPlan?.tool_sequence) && queryPlan.tool_sequence.length > 0)
  );
}

function renderTraceMetadata(metadata: Record<string, any>) {
  const queries = Array.isArray(metadata.queries) ? metadata.queries : [];
  const sources = Array.isArray(metadata.sources) ? metadata.sources : [];
  const documents = Array.isArray(metadata.documents) ? metadata.documents.slice(0, 5) : [];
  const reasoning = Array.isArray(metadata.reasoning) ? metadata.reasoning : [];
  const detailEntries = Object.entries(metadata).filter(
    ([key]) => !["run_id", "item_type", "queries", "sources", "documents", "reasoning"].includes(key)
  );

  return (
    <div className="space-y-2 text-xs text-slate-600">
      {(metadata.tool_name || metadata.server_label) && (
        <div className="flex flex-wrap gap-2">
          {metadata.tool_name && (
            <span className="rounded-full bg-slate-100 px-2 py-1 font-medium text-slate-700">
              {metadata.tool_name}
            </span>
          )}
          {metadata.server_label && (
            <span className="rounded-full bg-blue-50 px-2 py-1 font-mono text-blue-700">
              {metadata.server_label}
            </span>
          )}
        </div>
      )}

      {reasoning.length > 0 && (
        <div className="space-y-1">
          {reasoning.map((item: string, index: number) => (
            <div key={`${item}-${index}`} className="rounded bg-slate-50 px-2 py-1 text-slate-700">
              {item}
            </div>
          ))}
        </div>
      )}

      {queries.length > 0 && (
        <div className="space-y-1">
          {queries.map((query: string, index: number) => (
            <div key={`${query}-${index}`} className="rounded bg-blue-50 px-2 py-1 text-blue-800">
              {query}
            </div>
          ))}
        </div>
      )}

      {sources.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {sources.map((source: string, index: number) => (
            <span key={`${source}-${index}`} className="rounded-full bg-slate-100 px-2 py-1 text-slate-700">
              {source}
            </span>
          ))}
        </div>
      )}

      {typeof metadata.retrieved_count === "number" && (
        <div className="font-medium text-slate-700">Retrieved {metadata.retrieved_count} documents</div>
      )}

      {documents.length > 0 && (
        <div className="space-y-2">
          {documents.map((document: any, index: number) => (
            <div key={`${document.uid || document.document || index}`} className="rounded border border-slate-200 bg-slate-50 p-2">
              <div className="font-medium text-slate-800">{document.document || document.blob_url || document.uid}</div>
              {document.snippet && <div className="mt-1 text-slate-600">{document.snippet}</div>}
            </div>
          ))}
        </div>
      )}

      {detailEntries.length > 0 && (
        <div className="rounded border border-slate-200 bg-slate-50 p-2 font-mono text-[11px] text-slate-600">
          {JSON.stringify(Object.fromEntries(detailEntries), null, 2)}
        </div>
      )}
    </div>
  );
}
