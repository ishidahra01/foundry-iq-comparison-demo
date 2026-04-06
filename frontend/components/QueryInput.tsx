"use client";

import { useState } from "react";
import { Send, Sparkles } from "lucide-react";

interface QueryInputProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

const SAMPLE_QUERIES = [
  {
    text: "Should we launch this AI feature on April 30? What are the main risks and blockers?",
    category: "Complex Analysis"
  },
  {
    text: "この AI 機能を、日本向け本番環境で来月リリースしてよいか。内部ポリシー、現在の実装状況、予算制約を踏まえて、可否/ブロッカー/次アクションを答えてください",
    category: "Complex (Japanese)"
  },
  {
    text: "Are there any security blockers for the launch?",
    category: "Medium"
  },
  {
    text: "What is the project timeline and budget status?",
    category: "Simple"
  }
];

export default function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [question, setQuestion] = useState("");
  const [showSamples, setShowSamples] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      onSubmit(question.trim());
    }
  };

  const handleSampleClick = (sampleText: string) => {
    setQuestion(sampleText);
    setShowSamples(false);
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
      <form onSubmit={handleSubmit} className="p-4">
        <div className="flex gap-3">
          <div className="flex-1">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your question about the AI feature launch..."
              rows={3}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="flex items-center justify-between mt-3">
          <button
            type="button"
            onClick={() => setShowSamples(!showSamples)}
            className="flex items-center gap-2 px-4 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            Sample Queries
          </button>

          <button
            type="submit"
            disabled={!question.trim() || isLoading}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Comparing...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Compare Agents
              </>
            )}
          </button>
        </div>
      </form>

      {/* Sample Queries Dropdown */}
      {showSamples && (
        <div className="border-t border-slate-200 p-4 space-y-2">
          <p className="text-sm font-medium text-slate-700 mb-3">
            Try these sample queries:
          </p>
          {SAMPLE_QUERIES.map((sample, index) => (
            <button
              key={index}
              onClick={() => handleSampleClick(sample.text)}
              className="w-full text-left p-3 hover:bg-slate-50 rounded-lg transition-colors border border-slate-200"
            >
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm text-slate-700 flex-1">{sample.text}</p>
                <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded whitespace-nowrap">
                  {sample.category}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
