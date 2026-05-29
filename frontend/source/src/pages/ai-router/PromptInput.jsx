import { Loader as Loader2, Sparkles, Zap } from "lucide-react";

export default function PromptInput({
  prompt,
  setPrompt,
  onOptimize,
  onRoute,
  isOptimizing,
  isRouting,
  optimizedPrompt,
}) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground">Your Prompt</label>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Paste or type your prompt. Optimize it first for better routing."
        className="w-full min-h-40 p-4 rounded-xl bg-muted/40 border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 resize-none transition-all"
        disabled={isOptimizing || isRouting}
      />
      <div className="flex gap-3">
        <button
          onClick={onOptimize}
          disabled={!prompt.trim() || isOptimizing || isRouting}
          className="flex-1 px-4 py-2.5 rounded-lg bg-secondary/60 border border-border text-foreground hover:bg-secondary/80 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isOptimizing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Optimizing...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              <span>Optimize Prompt</span>
            </>
          )}
        </button>
        <button
          onClick={onRoute}
          disabled={!(optimizedPrompt || prompt).trim() || isRouting || isOptimizing}
          className="flex-1 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isRouting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Routing...</span>
            </>
          ) : (
            <>
              <Zap className="h-4 w-4" />
              <span>Route to AI</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
