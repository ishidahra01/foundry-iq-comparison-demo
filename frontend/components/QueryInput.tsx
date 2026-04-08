"use client";

import { useEffect, useState } from "react";
import { Send, Sparkles, FlaskConical, ClipboardPaste } from "lucide-react";

interface QueryInputProps {
  onSubmit: (submission: QuerySubmission) => void;
  isLoading: boolean;
}

interface QuerySubmission {
  question: string;
  mode: "compare" | "evaluate";
  evaluationSampleId?: string;
  evaluationJsonl?: string;
}

interface EvaluationCaseSummary {
  id: string;
  question: string;
  line_number: number;
  source_file: string;
  is_default: boolean;
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
  const [evaluationCases, setEvaluationCases] = useState<EvaluationCaseSummary[]>([]);
  const [pastedJsonl, setPastedJsonl] = useState("");
  const [inputError, setInputError] = useState<string | null>(null);

  useEffect(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

    const loadEvaluationCases = async () => {
      try {
        const response = await fetch(`${backendUrl}/evaluation/cases`);
        if (!response.ok) {
          return;
        }

        const data = await response.json();
        setEvaluationCases(Array.isArray(data.cases) ? data.cases : []);
      } catch (error) {
        console.error("Failed to load evaluation cases", error);
      }
    };

    void loadEvaluationCases();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      setInputError(null);
      onSubmit({ question: question.trim(), mode: "compare" });
    }
  };

  const handleSampleClick = (sampleText: string) => {
    setQuestion(sampleText);
    setShowSamples(false);
  };

  const handleEvaluationSampleRun = (evaluationCase: EvaluationCaseSummary) => {
    if (isLoading) {
      return;
    }

    setInputError(null);
    setQuestion(evaluationCase.question);
    onSubmit({
      question: evaluationCase.question,
      mode: "evaluate",
      evaluationSampleId: evaluationCase.id,
    });
  };

  const handlePastedEvaluationRun = () => {
    if (isLoading) {
      return;
    }

    try {
      const parsed = parseFirstJsonlRow(pastedJsonl);
      setQuestion(parsed.question);
      setInputError(null);
      onSubmit({
        question: parsed.question,
        mode: "evaluate",
        evaluationJsonl: pastedJsonl,
      });
    } catch (error) {
      setInputError(error instanceof Error ? error.message : "Failed to parse JSONL input.");
    }
  };

  const defaultEvaluationCase = evaluationCases.find((item) => item.is_default) ?? evaluationCases[0];

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

      <div className="border-t border-slate-200 p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Evaluation Dataset</h3>
            <p className="mt-1 text-sm text-slate-600">
              Run the current comparison flow against a JSONL ground-truth sample, then evaluate Classic RAG and Foundry IQ answers on the server.
            </p>
          </div>
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            JSONL + LLM Eval
          </span>
        </div>

        <div className="mt-4 grid gap-4 xl:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-800">
              <FlaskConical className="h-4 w-4 text-blue-600" />
              Sample Case
            </div>

            {defaultEvaluationCase ? (
              <div className="mt-3 rounded-lg border border-blue-200 bg-white p-3">
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                  <span className="rounded-full bg-blue-100 px-2 py-1 font-medium text-blue-700">
                    {defaultEvaluationCase.id}
                  </span>
                  <span>
                    {defaultEvaluationCase.source_file} line {defaultEvaluationCase.line_number}
                  </span>
                </div>
                <p className="mt-3 text-sm text-slate-700">{defaultEvaluationCase.question}</p>
                <button
                  type="button"
                  onClick={() => handleEvaluationSampleRun(defaultEvaluationCase)}
                  disabled={isLoading}
                  className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
                >
                  <FlaskConical className="h-4 w-4" />
                  Run Sample Evaluation
                </button>
              </div>
            ) : (
              <div className="mt-3 rounded-lg border border-dashed border-slate-300 bg-white p-3 text-sm text-slate-500">
                Evaluation sample metadata could not be loaded.
              </div>
            )}
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-800">
              <ClipboardPaste className="h-4 w-4 text-blue-600" />
              Paste JSONL Row
            </div>
            <textarea
              value={pastedJsonl}
              onChange={(e) => setPastedJsonl(e.target.value)}
              placeholder='Paste one or more JSONL rows with "question", "ideal_answer", and "evidence".'
              rows={8}
              className="mt-3 w-full rounded-lg border border-slate-300 bg-white px-3 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
              disabled={isLoading}
            />
            <div className="mt-3 flex items-center justify-between gap-3">
              <p className="text-xs text-slate-500">
                The first valid JSONL row is used to populate the input and trigger evaluation.
              </p>
              <button
                type="button"
                onClick={handlePastedEvaluationRun}
                disabled={!pastedJsonl.trim() || isLoading}
                className="inline-flex items-center gap-2 rounded-lg border border-blue-200 bg-white px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50 disabled:border-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed"
              >
                <ClipboardPaste className="h-4 w-4" />
                Run Pasted Evaluation
              </button>
            </div>
            {inputError && (
              <div className="mt-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {inputError}
              </div>
            )}
          </div>
        </div>
      </div>

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

function parseFirstJsonlRow(rawJsonl: string) {
  const lines = rawJsonl.split(/\r?\n/);

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }

    const payload = JSON.parse(trimmed);
    if (!payload.question || !payload.ideal_answer) {
      throw new Error('JSONL row must include both "question" and "ideal_answer" fields.');
    }

    return payload as { question: string; ideal_answer: string };
  }

  throw new Error("No valid JSONL row found.");
}
