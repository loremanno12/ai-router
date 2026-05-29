import React, { useState } from "react";
import Header from "./ai-router/Header";
import PromptInput from "./ai-router/PromptInput";
import OptimizedPrompt from "./ai-router/OptimizedPrompt";
import RoutingResult from "./ai-router/RoutingResult";
import ExamplesPanel from "./ai-router/ExamplesPanel";
import { optimizePrompt, routePrompt } from "./ai-router/api";

export default function AIRouter() {
  const [prompt, setPrompt] = useState("");
  const [optimizedPrompt, setOptimizedPrompt] = useState("");
  const [routingResult, setRoutingResult] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isRouting, setIsRouting] = useState(false);
  const [showExamples, setShowExamples] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleOptimize = async () => {
    if (!prompt.trim()) return;
    setIsOptimizing(true);
    const result = await optimizePrompt(prompt);
    setOptimizedPrompt(result);
    setIsOptimizing(false);
  };

  const handleRoute = async () => {
    const activePrompt = optimizedPrompt || prompt;
    if (!activePrompt.trim()) return;
    setIsRouting(true);
    const result = await routePrompt(activePrompt);
    setRoutingResult(result);
    setIsRouting(false);
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExampleSelect = (examplePrompt) => {
    setPrompt(examplePrompt);
    setOptimizedPrompt("");
    setRoutingResult(null);
  };

  return (
    <div className="min-h-screen bg-background font-inter flex flex-col">
      <Header />

      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10 flex flex-col gap-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="md:col-span-3">
            <PromptInput
              prompt={prompt}
              setPrompt={setPrompt}
              onOptimize={handleOptimize}
              onRoute={handleRoute}
              isOptimizing={isOptimizing}
              isRouting={isRouting}
              optimizedPrompt={optimizedPrompt}
            />
          </div>
          <div className="md:col-span-2">
            <OptimizedPrompt
              optimizedPrompt={optimizedPrompt}
              onCopy={handleCopy}
              copied={copied}
            />
          </div>
        </div>

        <RoutingResult
          routingResult={routingResult}
          onCopy={handleCopy}
          copied={copied}
        />

        <ExamplesPanel
          onSelect={handleExampleSelect}
          showExamples={showExamples}
          setShowExamples={setShowExamples}
        />
      </main>
    </div>
  );
}
