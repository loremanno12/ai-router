import { Copy, Check } from "lucide-react";

export default function OptimizedPrompt({ optimizedPrompt, onCopy, copied }) {
  if (!optimizedPrompt) {
    return (
      <div className="space-y-3">
        <label className="text-sm font-medium text-muted-foreground">Optimized Prompt</label>
        <div className="rounded-xl border border-border p-4 min-h-40 bg-muted/30">
          <p className="text-sm text-muted-foreground italic">
            Optional. Click Optimize Prompt to refine your text before routing.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-emerald-400">Optimized Prompt</label>
        <button
          onClick={() => onCopy(optimizedPrompt)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg bg-muted/40 border border-border hover:border-primary/40 transition-colors"
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
        </button>
      </div>
      <div className="rounded-xl border border-emerald-500/30 p-4 min-h-40 bg-muted/60">
        <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
          {optimizedPrompt}
        </p>
      </div>
    </div>
  );
}
