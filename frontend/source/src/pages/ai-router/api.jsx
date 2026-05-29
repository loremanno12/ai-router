// Bridge layer: prefer in-iframe → parent messaging via globals + CustomEvents
// Fallback: simple REST fetch when not embedded.

const API_BASE_URL = "https://your-backend.com"; // fallback only

function _sendToParent(action, payload, timeout = 30000) {
  if (typeof window === 'undefined' || !window.parent || window.parent === window) {
    return Promise.reject(new Error('no-parent'));
  }

  const id = 'req_' + Math.random().toString(36).slice(2, 9);

  return new Promise((resolve, reject) => {
    let finished = false;

    function cleanup() {
      try { window.parent.removeEventListener('ai:response', onResp); } catch (e) {}
      finished = true;
    }

    function onResp() {
      try {
        const resp = window.parent.__ai_router_response__ || null;
        if (resp && resp.id === id) {
          cleanup();
          resolve(resp.payload);
        }
      } catch (e) {
        cleanup();
        reject(e);
      }
    }

    window.parent.addEventListener('ai:response', onResp);

    // publish request for parent to pick up
    try {
      window.parent.__ai_router_request__ = { id, action, payload };
      // notify parent that a request is available
      if (typeof window.parent.dispatchEvent === 'function') {
        window.parent.dispatchEvent(new CustomEvent('ai:request'));
      } else if (typeof window.parent.postMessage === 'function') {
        window.parent.postMessage({ __ai_router_request__: true }, '*');
      }
    } catch (e) {
      cleanup();
      return reject(e);
    }

    const to = setTimeout(() => {
      if (finished) return;
      cleanup();
      reject(new Error('timeout'));
    }, timeout);
  });
}

// Optimize the user's prompt.
// Returns: string (the optimized prompt text)
export async function optimizePrompt(prompt) {
  // try parent bridge first
  try {
    const payload = await _sendToParent('optimize', { prompt });
    // support different shapes returned by backend shim
    return payload.optimized_prompt || payload.improved_prompt || payload.optimized || payload;
  } catch (e) {
    // fallback to REST
  }

  const res = await fetch(`${API_BASE_URL}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  const data = await res.json();
  return data.optimized_prompt || data.improved_prompt;
}

// Route the prompt to the best AI model and return a response.
// Returns: { recommended_model, reason, confidence, task_type, answer }
export async function routePrompt(prompt) {
  try {
    const payload = await _sendToParent('route', { prompt });
    return {
      recommended_model: payload.recommended_model || payload.predicted_model,
      reason: payload.reason || payload.explanation || null,
      confidence: payload.confidence,
      task_type: payload.task_type || null,
      answer: payload.answer || payload,
    };
  } catch (e) {
    // fallback to REST
  }

  const res = await fetch(`${API_BASE_URL}/route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  const data = await res.json();
  return {
    recommended_model: data.recommended_model,
    reason: data.reason,
    confidence: data.confidence,
    task_type: data.task_type,
    answer: data.answer,
  };
}
