import { Copy, Check } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function OptimizedPrompt({ optimizedPrompt, onCopy, copied }) {
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
}
