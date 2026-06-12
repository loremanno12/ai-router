
import { useState } from "react";
import {
  Header,
  PromptInput,
  OptimizedPrompt,
  RoutingResult,
  RoutingSkeleton,
  ExamplesPanel,
  PipelineControls,
} from "./components";
import { useAIRouter } from "./useAIRouter";

export default function AIRouter() {
  const {
    prompt,
    setPrompt,
    optimizedPrompt,
    routingResult,
    isOptimizing,
    isRouting,
    copied,
    handleOptimize,
    handleRoute,
    handleCopy,
    preprocMode,
    setPreprocMode,
    useImprover,
    setUseImprover,
    ollamaStatus,
  } = useAIRouter();

  const [showExamples, setShowExamples] = useState(false);

  const handleExampleSelect = (examplePrompt) => {
    setPrompt(examplePrompt);
  };

  return (
    <div className="dark min-h-screen bg-background font-inter flex flex-col">
      {/* L'header ora riceve lo stato per mostrare l'indicatore online/offline */}
      <Header ollamaStatus={ollamaStatus} />

      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10 flex flex-col gap-6">
        <PipelineControls
          ollamaStatus={ollamaStatus} // Passato per disabilitare i controlli, non per visualizzazione
          preprocMode={preprocMode}
          setPreprocMode={setPreprocMode}
          useImprover={useImprover}
          setUseImprover={setUseImprover}
        />

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

        {isRouting ? (
          <RoutingSkeleton />
        ) : (
          <RoutingResult
            routingResult={routingResult}
            onCopy={handleCopy}
            copied={copied}
          />
        )}

        <ExamplesPanel
          onSelect={handleExampleSelect}
          showExamples={showExamples}
          setShowExamples={setShowExamples}
        />
      </main>
    </div>
  );
}
