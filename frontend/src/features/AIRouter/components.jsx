
import { useState, useEffect, useRef } from "react";
import {
  ChevronDown, Code, FileText, Lightbulb, TrendingUp, PenTool,
  Copy, Check, Sparkles, Zap, CircleAlert as AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";


export const Header = ({ ollamaStatus }) => {
  const isOllamaOnline = ollamaStatus === 'online';
  return (
    <header className="px-6 py-5 border-b border-border/80">
      <div className="flex items-center justify-between">
        <h1 className="text-[1.75rem] font-bold tracking-tighter bg-gradient-to-br from-white to-[#8b5cf6] bg-clip-text text-transparent">
          AI Router
        </h1>
        <div className={cn(
          "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border border-border/60 bg-muted/40 backdrop-blur-sm"
        )}>
          <span className={cn(
            "h-2 w-2 rounded-full",
            isOllamaOnline ? "bg-green-500 animate-pulse" : "bg-red-500"
          )}></span>
          <span>
            {isOllamaOnline ? "System ready" : "Ollama is Offline"}
          </span>
        </div>
      </div>
    </header>
  );
};


export const PipelineControls = ({ preprocMode, setPreprocMode, useImprover, setUseImprover, ollamaStatus }) => {
  const isOllamaOnline = ollamaStatus === 'online';

  // Stato per la geometria dello slider animato
  const [sliderStyle, setSliderStyle] = useState({ left: 0, width: 0 });
  const tabsRef = useRef({});

  // Mappa delle icone per simulare lo stile DeepSeek (Instant, Expert, Vision)
  const modeIcons = {
    off: Zap,         // Simile a "Instant" (Veloce/Lampo)
    light: Lightbulb, // Simile a "Expert" (Intelligente/Lampadina)
    full: Sparkles,   // Simile a "Vision/Full capabilities" (Scintille)
  };

  // CORRETTO: Gestisce sia il cambio stato che il ridimensionamento della finestra
  useEffect(() => {
    const updateSlider = () => {
      const activeTab = tabsRef.current[preprocMode];
      if (activeTab) {
        setSliderStyle({
          left: activeTab.offsetLeft,
          width: activeTab.offsetWidth,
        });
      }
    };

    // Esegui al caricamento e al cambio di modalità
    updateSlider();

    // Ascolta il ridimensionamento della finestra per evitare che la pillola si sfasino
    window.addEventListener("resize", updateSlider);
    return () => window.removeEventListener("resize", updateSlider);
  }, [preprocMode]);

  return (
    <div className="flex flex-row items-center justify-between gap-4">
      <div className="flex flex-row items-center gap-4">
        
        {/* CONTENITORE TOGGLE (Stile DeepSeek: Ultra-scuro, bordi finissimi) */}
        <div className="inline-flex rounded-full border border-neutral-800 bg-[#0f0f11] p-1 gap-1 relative items-center overflow-hidden isolation-isolate">
          
          {/* La pillola azzurra che scivola con effetto elastico */}
          <div 
            className={cn(
              "absolute top-1 bottom-1 rounded-full z-0 transition-all duration-300",
              "bg-[#8b5cf6] shadow-[0_0_14px_rgba(139,92,246,0.3)]",
              "ease-[cubic-bezier(0.25,1,0.5,1)]"
            )}
            style={{
              left: `${sliderStyle.left}px`,
              width: `${sliderStyle.width}px`,
            }}
          />
          
          {['off', 'light', 'full'].map((mode) => {
            const Icon = modeIcons[mode];
            const isActive = preprocMode === mode;
            return (
              <button
                key={mode}
                ref={(el) => (tabsRef.current[mode] = el)}
                onClick={() => setPreprocMode(mode)}
                className={cn(
                  "px-4 py-1.5 text-xs font-medium rounded-full relative z-10 transition-colors duration-200",
                  "flex items-center gap-1.5 capitalize tracking-wide select-none",
                  isActive
                    ? "text-white-400 font-semibold"
                    : "text-neutral-400 hover:text-neutral-200"
                )}
              >
                {Icon && <Icon className={cn("h-3.5 w-3.5 transition-transform", isActive && "scale-110 text-white-400")} />}
                <span>{mode}</span>
              </button>
            );
          })}
        </div>

        {/* Pulsante IMPROVER (Aggiornato in stile pillola scura coerente) */}
        <div className="flex items-center gap-2">
          {isOllamaOnline ? (
            <button
              onClick={() => setUseImprover(!useImprover)}
              className={cn(
                "px-4 py-1.5 text-xs font-medium rounded-full border transition-all duration-200 uppercase tracking-wider select-none",
                useImprover
                  ? "bg-purple-500/10 border-purple-500/40 text-purple-400 shadow-[0_0_12px_rgba(139,92,246,0.15)]"
                  : "bg-transparent border-neutral-800 text-neutral-400 hover:text-neutral-200"
              )}
            >
              Improver: {useImprover ? 'ON' : 'OFF'}
            </button>
          ) : (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border border-red-500/30 bg-red-500/15 text-red-400">
              <span className="h-1.5 w-1.5 rounded-full bg-red-400"></span>
              Offline
            </div>
          )}
        </div>
      </div>

      <div className="text-xs text-muted-foreground font-mono bg-muted/20 px-2.5 py-1 rounded-md border border-border/40">
        Pre-processing: {preprocMode.toUpperCase()} | Improver: {useImprover ? 'ON' : 'OFF'}
      </div>
    </div>
  );
};



// --- Da ExamplesPanel.jsx ---
const EXAMPLES = [
  { icon: Code, prompt: "Write a Python function to compute Fibonacci numbers", category: "Code" },
  { icon: Lightbulb, prompt: "Explain quantum computing in simple terms", category: "Concepts" },
  { icon: FileText, prompt: "Debug this code: print('Hello World')", category: "Debugging" },
  { icon: TrendingUp, prompt: "How do I optimize my database performance?", category: "Optimization" },
  { icon: PenTool, prompt: "Create a marketing plan for a new tech product", category: "Creative" },
];

function ExampleButton({ icon: Icon, prompt, category, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full p-3 rounded-md bg-muted/30 border border-border hover:border-primary/40 text-left transition-all group flex items-start gap-3"
    >
      <Icon className="h-4 w-4 text-muted-foreground group-hover:text-primary/80 mt-0.5 transition-colors flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground mb-1">{category}</p>
        <p className="text-sm text-foreground line-clamp-2">{prompt}</p>
      </div>
    </button>
  );
}

export const ExamplesPanel = ({ onSelect, showExamples, setShowExamples }) => {
  return (
    <div className="rounded-xl border border-border overflow-hidden">
      <button
        onClick={() => setShowExamples(!showExamples)}
        className="w-full px-4 py-3 flex items-center justify-between bg-muted/40 hover:bg-muted transition-colors"
      >
        <span className="text-sm font-medium text-foreground">Examples</span>
        <ChevronDown
          className={cn(
            "h-4 w-4 text-muted-foreground transition-transform",
            showExamples && "rotate-180"
          )}
        />
      </button>
      {showExamples && (
        <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-2 border-t border-border bg-card">
          {EXAMPLES.map((example, idx) => (
            <ExampleButton
              key={idx}
              {...example}
              onClick={() => onSelect(example.prompt)}
            />
          ))}
        </div>
      )}
    </div>
  );
};


// --- Da OptimizedPrompt.jsx ---
export const OptimizedPrompt = ({ optimizedPrompt, onCopy, copied }) => {
  if (!optimizedPrompt) {
    return (
      <div className="space-y-3">
        <label className="text-sm font-medium text-muted-foreground">
          Optimized Prompt
        </label>
        <Card className="min-h-40 bg-muted/30">
          <p className="text-sm text-muted-foreground italic">
            Optional. Click Optimize Prompt to refine your text before routing.
          </p>
        </Card>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-emerald-400">
          Optimized Prompt
        </label>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onCopy(optimizedPrompt)}
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Use in prompt</span>
            </>
          )}
        </Button>
      </div>
      <Card className="min-h-40 bg-muted/60 border-emerald-500/30">
        <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
          {optimizedPrompt}
        </p>
      </Card>
    </div>
  );
};

// --- Da PromptInput.jsx ---
export const PromptInput = ({ prompt, setPrompt, onOptimize, onRoute, isOptimizing, isRouting, optimizedPrompt }) => {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground">
        Your Prompt
      </label>
      <Textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Paste or type your prompt. Optimize it first for better routing."
        disabled={isOptimizing || isRouting}
      />
      <div className="flex gap-3">
        <Button
          variant={!prompt.trim() ? "ghost" : "secondary"}
          onClick={onOptimize}
          disabled={!prompt.trim() || isOptimizing || isRouting}
          isLoading={isOptimizing}
          className="flex-1 rounded-xl"
        >
          {!isOptimizing && <Sparkles className="h-4 w-4" />}
          <span>{isOptimizing ? "Optimizing..." : "Optimize Prompt"}</span>
        </Button>
        <Button
          onClick={onRoute}
          disabled={!(optimizedPrompt || prompt).trim() || isRouting || isOptimizing}
          isLoading={isRouting}
          className="flex-1 rounded-xl"
        >
          {!isRouting && <Zap className="h-4 w-4" />}
          <span>{isRouting ? "Routing..." : "Route to AI"}</span>
        </Button>
      </div>
    </div>
  );
};

// --- Da RoutingResult.jsx ---
function ProgressBar({ value, isSelected }) {
  return (
    <div className="h-2 w-24 bg-muted/60 rounded-full overflow-hidden">
      <div
        className={cn(
          "h-full rounded-full transition-all",
          isSelected ? "bg-primary" : "bg-muted-foreground/30"
        )}
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

function ModelRanking({ models, selectedModel }) {
  return (
    <div className="space-y-2">
      {models.map(([model, probability], index) => {
        const percentage = Math.round(probability * 100);
        const isSelected = model === selectedModel;
        return (
          <div key={model} className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground w-6">
              {index + 1}.
            </span>
            <span
              className={cn(
                "text-sm flex-1",
                isSelected
                  ? "font-medium text-foreground"
                  : "text-muted-foreground"
              )}
            >
              {model}
            </span>
            <ProgressBar value={percentage} isSelected={isSelected} />
            <span className="text-xs text-muted-foreground w-10">
              {percentage}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

export const RoutingResult = ({ routingResult, onCopy, copied }) => {
  if (!routingResult) {
    return (
      <Card className="bg-muted/40">
        <p className="text-sm text-muted-foreground">
          No result yet. Enter a prompt and click Route to AI.
        </p>
      </Card>
    );
  }
  if (!routingResult.success) {
    return (
      <Card className="bg-muted/40">
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <span className="text-sm font-medium text-red-400">
            Routing failed
          </span>
        </div>
        <p className="text-sm text-muted-foreground">
          {routingResult.error}
        </p>
      </Card>
    );
  }
  const confidence = routingResult.confidence || 0;
  const confidencePercent = Math.round(confidence * 100);
  const isLowConfidence = confidence < 0.5;
  const rankingItems = routingResult.ranking
    ? routingResult.ranking.map((item) => [item.model, item.score])
    : routingResult.all_probabilities
      ? Object.entries(routingResult.all_probabilities)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
      : [];
  return (
    <div className="space-y-4">
      <label className="text-sm font-medium text-muted-foreground">
        Routing Result
      </label>
      <Card>
        <div className="space-y-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-widest">
              Selected Model
            </label>
            <div className="mt-2 flex items-center gap-3">
              <div className="px-4 py-2 rounded-md bg-primary/20 border border-primary text-primary font-medium">
                {routingResult.recommended_model}
              </div>
              <div className="text-sm text-muted-foreground">
                {confidencePercent}% confidence
              </div>
            </div>
          </div>
          {routingResult.reasons && routingResult.reasons.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {routingResult.reasons.map((reason, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded text-xs bg-primary/10 text-primary border border-primary/20"
                >
                  {reason}
                </span>
              ))}
            </div>
          )}
          {isLowConfidence && (
            <div className="flex items-start gap-2 p-3 rounded-md bg-amber-400/10 border border-amber-400/30">
              <AlertCircle className="h-4 w-4 text-amber-400 mt-0.5" />
              <p className="text-sm text-muted-foreground">
                Confidence below 50%. Consider optimizing the prompt for better
                routing.
              </p>
            </div>
          )}
          {rankingItems.length > 0 && (
            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-widest">
                Top Candidates
              </label>
              <div className="mt-3">
                <ModelRanking
                  models={rankingItems}
                  selectedModel={routingResult.recommended_model}
                />
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

// --- Da RoutingSkeleton.jsx ---
export const RoutingSkeleton = () => {
  return (
    <div className="space-y-3 animate-pulse">
      <div className="h-4 bg-muted/30 rounded w-1/4"></div>
      <div className="p-4 rounded-md border border-border bg-card">
        <div className="flex items-center justify-between mb-3">
          <div className="h-6 bg-muted/30 rounded w-1/3"></div>
          <div className="h-4 bg-muted/30 rounded w-20"></div>
        </div>
        <div className="space-y-2">
          <div className="h-2 bg-muted/30 rounded-full w-full"></div>
          <div className="flex justify-between">
            <div className="h-3 bg-muted/30 rounded w-16"></div>
            <div className="h-3 bg-muted/30 rounded w-12"></div>
          </div>
        </div>
        <div className="mt-4 space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="h-4 bg-muted/30 rounded w-8"></div>
              <div className="h-3 bg-muted/30 rounded flex-1"></div>
              <div className="h-4 bg-muted/30 rounded w-16"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};