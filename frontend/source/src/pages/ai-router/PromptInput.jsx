import { Sparkles, Zap } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";

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
          variant="secondary"
          onClick={onOptimize}
          disabled={!prompt.trim() || isOptimizing || isRouting}
          isLoading={isOptimizing}
          className="flex-1"
        >
          {!isOptimizing && <Sparkles className="h-4 w-4" />}
          <span>{isOptimizing ? "Optimizing..." : "Optimize Prompt"}</span>
        </Button>

        <Button
          onClick={onRoute}
          disabled={!(optimizedPrompt || prompt).trim() || isRouting || isOptimizing}
          isLoading={isRouting}
          className="flex-1"
        >
          {!isRouting && <Zap className="h-4 w-4" />}
          <span>{isRouting ? "Routing..." : "Route to AI"}</span>
        </Button>
      </div>
    </div>
  );
}
