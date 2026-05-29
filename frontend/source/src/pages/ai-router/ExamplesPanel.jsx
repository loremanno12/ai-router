import { ChevronDown, Code, FileText, Lightbulb, TrendingUp, PenTool } from "lucide-react";

const EXAMPLES = [
  {
    icon: Code,
    prompt: "Write a Python function to compute Fibonacci numbers",
  },
  {
    icon: Lightbulb,
    prompt: "Explain quantum computing in simple terms",
  },
  {
    icon: Code,
    prompt: "Debug this code: print('Hello World')",
  },
  {
    icon: TrendingUp,
    prompt: "How do I optimize my database performance?",
  },
  {
    icon: PenTool,
    prompt: "Create a marketing plan for a new tech product",
  },
];

export default function ExamplesPanel({ onSelect, showExamples, setShowExamples }) {
  return (
    <div className="rounded-xl border border-border overflow-hidden">
      <button
        onClick={() => setShowExamples(!showExamples)}
        className="w-full px-4 py-3 flex items-center justify-between bg-muted/40 hover:bg-muted transition-colors"
      >
        <span className="text-sm font-medium text-foreground">Examples</span>
        <ChevronDown
          className={`h-4 w-4 text-muted-foreground transition-transform ${showExamples ? "rotate-180" : ""}`}
        />
      </button>

      {showExamples && (
        <div className="p-4 space-y-2 border-t border-border bg-card">
          {EXAMPLES.map(({ icon: Icon, prompt }, idx) => (
            <button
              key={idx}
              onClick={() => onSelect(prompt)}
              className="w-full p-3 rounded-lg bg-muted/30 border border-border hover:border-primary/40 text-left transition-all group flex items-start gap-3"
            >
              <Icon className="h-4 w-4 text-muted-foreground group-hover:text-primary/80 mt-0.5 transition-colors" />
              <span className="text-sm text-foreground line-clamp-2">{prompt}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
