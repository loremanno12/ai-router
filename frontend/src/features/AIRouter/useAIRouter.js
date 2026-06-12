
import { useState, useCallback, useEffect } from "react";

// --- Bridge NiceGUI per comunicazione con backend ---
// Usa window.__ai_router_request__ e window.addEventListener('ai:response')
let requestIdCounter = 0;

const sendRequest = (action, payload) => {
  return new Promise((resolve, reject) => {
    const requestId = ++requestIdCounter;
    
    // Set request on parent window
    if (window.parent && window.parent.__ai_router_request__ !== undefined) {
      window.parent.__ai_router_request__ = { id: requestId, action, payload };
    } else if (window.__ai_router_request__ !== undefined) {
      window.__ai_router_request__ = { id: requestId, action, payload };
    } else {
      reject(new Error("Bridge not available"));
      return;
    }

    // Listen for response
    const handleResponse = (event) => {
      if (event.detail && event.detail.id === requestId) {
        window.removeEventListener('ai:response', handleResponse);
        resolve(event.detail.payload);
      }
    };

    window.addEventListener('ai:response', handleResponse);

    // Timeout after 30 seconds
    setTimeout(() => {
      window.removeEventListener('ai:response', handleResponse);
      reject(new Error("Request timeout"));
    }, 30000);
  });
};

const checkOllamaHealth = async () => {
  try {
    // Ollama health check is done by backend, we just need to check if bridge is available
    if (window.parent && window.parent.__ai_router_request__ !== undefined) {
      return "online";
    } else if (window.__ai_router_request__ !== undefined) {
      return "online";
    }
    return "offline";
  } catch (error) {
    return "offline";
  }
};

const optimizePrompt = async (prompt) => {
  const result = await sendRequest('optimize', { prompt });
  return result.optimized_prompt;
};

const routePrompt = async (prompt, settings) => {
  return await sendRequest('route', { prompt, ...settings });
};


// --- Custom Hook ---
export function useAIRouter() {
  const [prompt, setPrompt] = useState("");
  const [optimizedPrompt, setOptimizedPrompt] = useState("");
  const [routingResult, setRoutingResult] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isRouting, setIsRouting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [preprocMode, setPreprocMode] = useState("off");
  const [useImprover, setUseImprover] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState("unknown");

  useEffect(() => {
    const checkStatus = async () => {
      const status = await checkOllamaHealth();
      setOllamaStatus(status);
    };
    checkStatus();
  }, []);

  const handleOptimize = useCallback(async () => {
    if (!prompt.trim()) return;
    setIsOptimizing(true);
    setRoutingResult(null);
    try {
      const result = await optimizePrompt(prompt);
      setOptimizedPrompt(result);
    } catch (error) {
      // Potremmo impostare uno stato di errore qui
    } finally {
      setIsOptimizing(false);
    }
  }, [prompt]);

  const handleRoute = useCallback(async () => {
    const activePrompt = optimizedPrompt || prompt;
    if (!activePrompt.trim()) return;
    setIsRouting(true);
    try {
      const result = await routePrompt(activePrompt, {
        preproc_mode: preprocMode,
        use_improver: useImprover,
      });
      setRoutingResult(result);
    } catch (error) {
      setRoutingResult({ success: false, error: error.message });
    } finally {
      setIsRouting(false);
    }
  }, [prompt, optimizedPrompt, preprocMode, useImprover]);

  const handleCopy = useCallback((text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, []);

  // La selezione dell'esempio ora modifica solo il prompt
  useEffect(() => {
      setOptimizedPrompt("");
      setRoutingResult(null);
  }, [prompt]);


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
    // Esportiamo anche gli stati e i setter per la UI della pipeline
    preprocMode,
    setPreprocMode,
    useImprover,
    setUseImprover,
    ollamaStatus,
  };
}
