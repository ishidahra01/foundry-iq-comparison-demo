"use client";

import { useState } from "react";
import ComparisonView from "@/components/ComparisonView";
import QueryInput from "@/components/QueryInput";
import { Search } from "lucide-react";

export default function Home() {
  const [currentRun, setCurrentRun] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleQuerySubmit = async (question: string) => {
    setIsLoading(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/compare`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch comparison");
      }

      const data = await response.json();
      setCurrentRun(data);
    } catch (error) {
      console.error("Error fetching comparison:", error);
      alert("Failed to fetch comparison. Please ensure the backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg">
              <Search className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                Foundry IQ Comparison Demo
              </h1>
              <p className="text-sm text-slate-600">
                Compare Classic RAG vs Foundry IQ Agentic Retrieval
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Query Input */}
        <div className="mb-8">
          <QueryInput onSubmit={handleQuerySubmit} isLoading={isLoading} />
        </div>

        {/* Comparison View */}
        {currentRun ? (
          <ComparisonView data={currentRun} />
        ) : (
          <div className="bg-white rounded-lg border border-slate-200 p-12 text-center">
            <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-slate-700 mb-2">
              Ready to Compare
            </h2>
            <p className="text-slate-500">
              Enter a question above to see the comparison between Classic RAG and Foundry IQ
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-slate-600">
          <p>
            Foundry IQ Comparison Demo · Built with Next.js and FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}
