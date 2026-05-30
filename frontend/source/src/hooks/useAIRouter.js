import { useState, useCallback } from "react";
import { optimizePrompt, routePrompt } from "@/pages/ai-router/api";

/**
 * Custom hook for managing AI Router state and operations
 */
export function useAIRouter() {
  const [prompt, setPrompt] = useState("");
  const [optimizedPrompt, setOptimizedPrompt] = useState("");
  const [routingResult, setRoutingResult] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isRouting, setIsRouting] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleOptimize = useCallback(async () => {
    if (!prompt.trim()) return;

    setIsOptimizing(true);
    try {
      const result = await optimizePrompt(prompt);
      setOptimizedPrompt(result);
    } catch (error) {
      console.error("Optimization failed:", error);
    } finally {
      setIsOptimizing(false);
    }
  }, [prompt]);

  const handleRoute = useCallback(async () => {
    const activePrompt = optimizedPrompt || prompt;
    if (!activePrompt.trim()) return;

    setIsRouting(true);
    try {
      const result = await routePrompt(activePrompt);
      setRoutingResult(result);
    } catch (error) {
      console.error("Routing failed:", error);
    } finally {
      setIsRouting(false);
    }
  }, [prompt, optimizedPrompt]);

  const handleCopy = useCallback((text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, []);

  const handleExampleSelect = useCallback((examplePrompt) => {
    setPrompt(examplePrompt);
    setOptimizedPrompt("");
    setRoutingResult(null);
  }, []);

  const reset = useCallback(() => {
    setPrompt("");
    setOptimizedPrompt("");
    setRoutingResult(null);
    setCopied(false);
  }, []);

  return {
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
    handleExampleSelect,
    reset,
  };
}
