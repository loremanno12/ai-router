import { Copy, Check, CircleAlert as AlertCircle } from "lucide-react";

export default function RoutingResult({ routingResult, onCopy, copied }) {
  if (!routingResult) {
    return (
      <div className="rounded-xl border border-border p-4 bg-muted/40">
        <p className="text-sm text-muted-foreground">
          No result yet. Enter a prompt and click Route to AI.
        </p>
      </div>
    );
  }

  if (!routingResult.success) {
    return (
      <div className="rounded-xl border border-border p-4 bg-muted/40">
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <span className="text-sm font-medium text-red-400">Routing failed</span>
        </div>
        <p className="text-sm text-muted-foreground">{routingResult.error}</p>
      </div>
    );
  }

  const confidence = routingResult.confidence || 0;
  const confidencePercent = Math.round(confidence * 100);
  const isLowConfidence = confidence < 0.5;

  const sortedModels = routingResult.all_probabilities
    ? Object.entries(routingResult.all_probabilities)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
    : [];

  return (
    <div className="space-y-4">
      <label className="text-sm font-medium text-muted-foreground">Routing Result</label>

      <div className="rounded-xl border border-border p-5 bg-card space-y-4">
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-widest">
            Selected Model
          </label>
          <div className="mt-2 flex items-center gap-3">
            <div className="px-4 py-2 rounded-lg bg-primary/20 border border-primary text-primary font-medium">
              {routingResult.recommended_model}
            </div>
            <div className="text-sm text-muted-foreground">
              {confidencePercent}% confidence
            </div>
          </div>
        </div>

        {isLowConfidence && (
          <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-400/10 border border-amber-400/30">
            <AlertCircle className="h-4 w-4 text-amber-400 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Confidence below 50%. Consider optimizing the prompt for better routing.
            </p>
          </div>
        )}

        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-widest">
            Top Candidates
          </label>
          <div className="mt-3 space-y-2">
            {sortedModels.map(([model, prob], idx) => {
              const pct = Math.round(prob * 100);
              const isSelected = model === routingResult.recommended_model;

              return (
                <div key={model} className="flex items-center gap-3">
                  <div className="flex-1 flex items-center gap-3">
                    <span className="text-sm text-muted-foreground w-6">
                      {idx + 1}.
                    </span>
                    <span className={`text-sm ${isSelected ? "font-medium text-foreground" : "text-muted-foreground"}`}>
                      {model}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 bg-muted/60 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${isSelected ? "bg-primary" : "bg-muted-foreground/30"}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground w-10">{pct}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
