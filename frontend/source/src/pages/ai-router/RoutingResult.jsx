import { CircleAlert as AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

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

export default function RoutingResult({ routingResult, onCopy, copied }) {
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

  const sortedModels = routingResult.all_probabilities
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
          {/* Selected Model */}
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

          {/* Low Confidence Warning */}
          {isLowConfidence && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-400/10 border border-amber-400/30">
              <AlertCircle className="h-4 w-4 text-amber-400 mt-0.5" />
              <p className="text-sm text-muted-foreground">
                Confidence below 50%. Consider optimizing the prompt for better
                routing.
              </p>
            </div>
          )}

          {/* Top Candidates */}
          {sortedModels.length > 0 && (
            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-widest">
                Top Candidates
              </label>
              <div className="mt-3">
                <ModelRanking
                  models={sortedModels}
                  selectedModel={routingResult.recommended_model}
                />
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
