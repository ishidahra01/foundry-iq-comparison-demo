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
  TrendingUp
} from "lucide-react";

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
    new Set(["answer"])
  );

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

  const VerdictIcon = result.verdict ? VERDICT_ICONS[result.verdict] : null;
  const verdictColor = result.verdict ? VERDICT_COLORS[result.verdict] : "";

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
        <div className="grid grid-cols-4 gap-3">
          <div className="text-center">
            <div className="text-xs text-slate-600 mb-1">Time</div>
            <div className="text-sm font-semibold text-slate-900">
              {(result.metrics.total_time_ms / 1000).toFixed(2)}s
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-slate-600 mb-1">Sources</div>
            <div className="text-sm font-semibold text-slate-900">
              {result.sources_used.length}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-slate-600 mb-1">Citations</div>
            <div className="text-sm font-semibold text-slate-900">
              {result.citations.length}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-slate-600 mb-1">Queries</div>
            <div className="text-sm font-semibold text-slate-900">
              {result.metrics.subquery_count || 1}
            </div>
          </div>
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
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-slate-700 leading-relaxed">
              {result.answer}
            </pre>
          </div>
        </Section>

        {/* Citations Section */}
        {result.citations.length > 0 && (
          <Section
            title="Citations"
            icon={Database}
            count={result.citations.length}
            isExpanded={expandedSections.has("citations")}
            onToggle={() => toggleSection("citations")}
          >
            <div className="space-y-3">
              {result.citations.map((citation: any, index: number) => (
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
          icon={Zap}
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
                  value={`${(result.metrics.total_time_ms / 1000).toFixed(2)}s`}
                />
                <MetricItem
                  label="Retrieval Count"
                  value={result.metrics.retrieval_count}
                />
                {result.metrics.token_usage && (
                  <>
                    <MetricItem
                      label="Input Tokens"
                      value={result.metrics.token_usage.input}
                    />
                    <MetricItem
                      label="Output Tokens"
                      value={result.metrics.token_usage.output}
                    />
                  </>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-slate-700 mb-2">
                Sources Used
              </h4>
              <div className="space-y-1">
                {result.sources_used.map((source: string, index: number) => (
                  <div
                    key={index}
                    className="text-xs font-mono text-slate-600 bg-slate-50 px-2 py-1 rounded"
                  >
                    {source}
                  </div>
                ))}
              </div>
            </div>

            {result.query_plan && (
              <div>
                <h4 className="text-sm font-medium text-slate-700 mb-2">
                  Query Plan
                </h4>
                <div className="text-xs bg-slate-50 p-3 rounded border border-slate-200">
                  <div className="mb-2">
                    <span className="font-medium">Strategy:</span>{" "}
                    {result.query_plan.retrieval_strategy}
                  </div>
                  {result.query_plan.decomposed_queries && (
                    <div>
                      <span className="font-medium">Sub-queries:</span>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        {result.query_plan.decomposed_queries.map(
                          (q: string, i: number) => (
                            <li key={i} className="text-slate-600">
                              {q}
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </Section>

        {/* Trace Events */}
        <Section
          title="Trace Events"
          icon={TrendingUp}
          count={result.trace_events.length}
          isExpanded={expandedSections.has("trace")}
          onToggle={() => toggleSection("trace")}
        >
          <div className="space-y-2">
            {result.trace_events.map((event: any, index: number) => (
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
                    <div className="text-xs text-slate-600 mt-1">
                      {JSON.stringify(event.metadata)}
                    </div>
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
