import { ChevronDown, Code, FileText, Lightbulb, TrendingUp, PenTool } from "lucide-react";
import { cn } from "@/lib/utils";

const EXAMPLES = [
  {
    icon: Code,
    prompt: "Write a Python function to compute Fibonacci numbers",
    category: "Code",
  },
  {
    icon: Lightbulb,
    prompt: "Explain quantum computing in simple terms",
    category: "Concepts",
  },
  {
    icon: FileText,
    prompt: "Debug this code: print('Hello World')",
    category: "Debugging",
  },
  {
    icon: TrendingUp,
    prompt: "How do I optimize my database performance?",
    category: "Optimization",
  },
  {
    icon: PenTool,
    prompt: "Create a marketing plan for a new tech product",
    category: "Creative",
  },
];

function ExampleButton({ icon: Icon, prompt, category, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full p-3 rounded-lg bg-muted/30 border border-border hover:border-primary/40 text-left transition-all group flex items-start gap-3"
    >
      <Icon className="h-4 w-4 text-muted-foreground group-hover:text-primary/80 mt-0.5 transition-colors flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground mb-1">{category}</p>
        <p className="text-sm text-foreground line-clamp-2">{prompt}</p>
      </div>
    </button>
  );
}

export default function ExamplesPanel({ onSelect, showExamples, setShowExamples }) {
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
}
