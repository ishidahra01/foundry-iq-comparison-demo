"use client";

import { useState } from "react";
import AgentResultPanel from "./AgentResultPanel";
import ProcessingWindow from "./ProcessingWindow";
import { GitCompare, Activity } from "lucide-react";

interface ComparisonViewProps {
  data: any;
}

export default function ComparisonView({ data }: ComparisonViewProps) {
  const [activeTab, setActiveTab] = useState<"comparison" | "timeline">("comparison");

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
      ) : (
        <ProcessingWindow
          classicEvents={data.classic_rag.trace_events}
          foundryIqEvents={data.foundry_iq.trace_events}
        />
      )}
    </div>
  );
}
