"use client";

import { CheckCircle2, Clock, Search, Zap, FileText } from "lucide-react";

interface ProcessingWindowProps {
  classicEvents: any[];
  foundryIqEvents: any[];
}

const EVENT_ICONS: Record<string, any> = {
  task_hypothesis_generated: Zap,
  tool_call_started: Zap,
  tool_call_completed: Zap,
  retrieval_started: Search,
  retrieval_completed: Search,
  answer_synthesis_started: FileText,
  answer_completed: CheckCircle2,
  error: Clock,
};

const EVENT_COLORS: Record<string, string> = {
  "classic-rag": "border-slate-300 bg-slate-50",
  "foundry-iq": "border-blue-300 bg-blue-50",
};

export default function ProcessingWindow({
  classicEvents,
  foundryIqEvents,
}: ProcessingWindowProps) {
  // Merge and sort events by timestamp
  const allEvents = [
    ...classicEvents.map((e) => ({ ...e, agent: "classic-rag" as const })),
    ...foundryIqEvents.map((e) => ({ ...e, agent: "foundry-iq" as const })),
  ].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  // Calculate relative timestamps
  const startTime = allEvents.length > 0
    ? new Date(allEvents[0].timestamp).getTime()
    : 0;

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
      <div className="p-4 border-b border-slate-200">
        <h3 className="text-lg font-semibold text-slate-900">
          Processing Timeline
        </h3>
        <p className="text-sm text-slate-600 mt-1">
          Real-time execution trace comparing both agents
        </p>
      </div>

      <div className="p-4">
        <div className="space-y-3">
          {allEvents.map((event, index) => {
            const EventIcon = EVENT_ICONS[event.event_type] || Clock;
            const relativeTime = startTime
              ? ((new Date(event.timestamp).getTime() - startTime) / 1000).toFixed(2)
              : "0.00";

            return (
              <div key={index} className="flex items-start gap-3">
                {/* Timeline */}
                <div className="flex flex-col items-center">
                  <div
                    className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${
                      EVENT_COLORS[event.agent]
                    }`}
                  >
                    <EventIcon className="w-4 h-4 text-slate-700" />
                  </div>
                  {index < allEvents.length - 1 && (
                    <div className="w-0.5 h-6 bg-slate-200 my-1" />
                  )}
                </div>

                {/* Event Content */}
                <div className="flex-1 pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-slate-900">
                          {event.event_type.replace(/_/g, " ")}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded ${
                            event.agent === "classic-rag"
                              ? "bg-slate-100 text-slate-700"
                              : "bg-blue-100 text-blue-700"
                          }`}
                        >
                          {event.agent === "classic-rag"
                            ? "Classic RAG"
                            : "Foundry IQ"}
                        </span>
                      </div>

                      {/* Metadata */}
                      {Object.keys(event.metadata).length > 0 && (
                        <div className="mt-2 text-sm text-slate-600">
                          {renderMetadata(event.metadata)}
                        </div>
                      )}
                    </div>

                    {/* Timing */}
                    <div className="text-right">
                      <div className="text-xs text-slate-500">
                        +{relativeTime}s
                      </div>
                      {event.elapsed_ms && (
                        <div className="text-xs text-slate-400 mt-1">
                          ({event.elapsed_ms}ms)
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function renderMetadata(metadata: Record<string, any>) {
  if (Array.isArray(metadata.reasoning) && metadata.reasoning.length > 0) {
    return (
      <div className="space-y-2">
        {metadata.reasoning.map((reason: string, index: number) => (
          <div
            key={`${reason}-${index}`}
            className="rounded border border-slate-200 bg-slate-50 p-2 text-xs text-slate-700"
          >
            {reason}
          </div>
        ))}
      </div>
    );
  }

  if (metadata.query) {
    return (
      <div className="bg-slate-50 p-2 rounded border border-slate-200">
        <span className="text-xs font-medium text-slate-700">Query: </span>
        <span className="text-xs text-slate-600">{metadata.query}</span>
      </div>
    );
  }

  if (metadata.planned_queries && Array.isArray(metadata.planned_queries)) {
    return (
      <div className="bg-blue-50 p-2 rounded border border-blue-200">
        <div className="text-xs font-medium text-blue-900 mb-1">
          Planned Queries:
        </div>
        <ul className="list-disc list-inside space-y-1">
          {metadata.planned_queries.map((q: string, i: number) => (
            <li key={i} className="text-xs text-blue-700">
              {q}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  if (Array.isArray(metadata.queries) && metadata.queries.length > 0) {
    return (
      <div className="space-y-2">
        <div className="text-xs font-medium text-slate-700">Queries</div>
        {metadata.queries.map((query: string, index: number) => (
          <div
            key={`${query}-${index}`}
            className="rounded border border-blue-200 bg-blue-50 p-2 text-xs text-blue-900"
          >
            {query}
          </div>
        ))}
      </div>
    );
  }

  if (metadata.retrieved_count || metadata.total_results || Array.isArray(metadata.sources)) {
    return (
      <div className="space-y-2 text-xs">
        <div className="flex flex-wrap items-center gap-4">
          {metadata.retrieved_count && (
            <span>
              <span className="font-medium">Retrieved:</span>{" "}
              {metadata.retrieved_count}
            </span>
          )}
          {metadata.total_results && (
            <span>
              <span className="font-medium">Total:</span>{" "}
              {metadata.total_results}
            </span>
          )}
          {metadata.subqueries_executed && (
            <span>
              <span className="font-medium">Sub-queries:</span>{" "}
              {metadata.subqueries_executed}
            </span>
          )}
        </div>

        {Array.isArray(metadata.sources) && metadata.sources.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {metadata.sources.map((source: string, index: number) => (
              <span
                key={`${source}-${index}`}
                className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-700"
              >
                {source}
              </span>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (metadata.tool_name) {
    return (
      <div className="space-y-2 text-xs">
        <div>
          <span className="font-medium">Tool:</span> {metadata.tool_name}
          {metadata.server_label && (
            <span className="ml-2 font-mono text-slate-500">{metadata.server_label}</span>
          )}
          {metadata.result_count && (
            <span className="ml-2">({metadata.result_count} results)</span>
          )}
        </div>
        {Array.isArray(metadata.documents) && metadata.documents.length > 0 && (
          <div className="space-y-2">
            {metadata.documents.slice(0, 4).map((document: any, index: number) => (
              <div key={`${document.uid || document.document || index}`} className="rounded border border-slate-200 bg-slate-50 p-2">
                <div className="font-medium text-slate-700">
                  {document.document || document.blob_url || document.uid}
                </div>
                {document.snippet && <div className="mt-1 text-slate-600">{document.snippet}</div>}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Default: show as JSON
  const relevantKeys = Object.keys(metadata).filter(
    (k) => !["hypothesis", "synthesis_approach"].includes(k)
  );
  if (relevantKeys.length > 0) {
    return (
      <div className="text-xs font-mono text-slate-600">
        {JSON.stringify(
          Object.fromEntries(relevantKeys.map((k) => [k, metadata[k]])),
          null,
          2
        )}
      </div>
    );
  }

  return null;
}
