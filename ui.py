"""Interfaccia Gradio – AI Router: tema dark, minimal, premium."""
import html
import logging
from typing import Any, Dict, Tuple

import gradio as gr

from cache import ModelCache
from config import Config
from ollama_service import improve_prompt_with_ollama
from predictor import predict_model

logger = logging.getLogger(__name__)

# ——— Palette & CSS (modern glass dark) ———
ACCENT = "#8b5cf6"       # violet
ACCENT_HOVER = "#a78bfa"
ACCENT_SECONDARY = "#06b6d4"  # cyan
BG_DARK = "#09090b"
BG_CARD = "rgba(24, 24, 28, 0.8)"
BG_INPUT = "rgba(28, 28, 34, 0.6)"
BORDER = "#27272a"
TEXT = "#fafafa"
TEXT_MUTED = "#a1a1aa"
SUCCESS = "#10b981"
ERROR = "#ef4444"

CUSTOM_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
  --accent: {ACCENT};
  --accent-hover: {ACCENT_HOVER};
  --bg-dark: {BG_DARK};
  --bg-card: {BG_CARD};
  --bg-input: {BG_INPUT};
  --border: {BORDER};
  --text: {TEXT};
  --text-muted: {TEXT_MUTED};
}}

* {{ box-sizing: border-box; }}

.gradio-container {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background: linear-gradient(135deg, {BG_DARK} 0%, #0c0c10 50%, #101014 100%) !important;
  color: {TEXT} !important;
  min-height: 100vh;
}}

/* Root blocks */
.contain {{
  max-width: 1100px !important;
  margin: 0 auto !important;
  padding: 0 1.5rem 2rem !important;
}}

/* Header */
.app-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.5rem 0;
  margin-bottom: 2rem;
  position: relative;
}}
.app-header::after {{
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, {ACCENT}40, transparent);
}}
.app-logo {{
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: {TEXT};
  margin: 0;
  background: linear-gradient(135deg, {TEXT} 0%, {ACCENT} 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.app-logo span {{ color: {ACCENT}; }}
.status-pill {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(6,182,212,0.1) 100%);
  border: 1px solid {ACCENT}30;
  color: {TEXT_MUTED};
  backdrop-filter: blur(8px);
}}
.status-pill::before {{
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: {SUCCESS};
  animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.6; transform: scale(0.9); }} }}

/* Cards */
.card {{
  background: linear-gradient(135deg, {BG_CARD} 0%, rgba(20,20,24,0.9) 100%);
  border: 1px solid {BORDER};
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}}
.card-title {{
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: {TEXT_MUTED};
  margin-bottom: 1rem;
  opacity: 0.8;
}}

/* Textarea override */
.gr-box {{
  background: linear-gradient(135deg, {BG_INPUT} 0%, rgba(24,24,30,0.8) 100%) !important;
  border: 1px solid {BORDER} !important;
  border-radius: 12px !important;
  color: {TEXT} !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  backdrop-filter: blur(8px);
}}
.gr-box:hover {{
  border-color: {ACCENT}60 !important;
}}
.gr-box:focus-within {{
  border-color: {ACCENT} !important;
  box-shadow: 0 0 0 3px {ACCENT}25, 0 8px 32px rgba(139,92,246,0.15) !important;
}}
.gr-box textarea {{
  background: transparent !important;
  color: {TEXT} !important;
  line-height: 1.6 !important;
}}
.gr-box .placeholder {{
  color: {TEXT_MUTED} !important;
  opacity: 0.7;
}}

/* Buttons */
.gr-button {{
  font-family: inherit !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  border: none !important;
  letter-spacing: 0.01em;
}}
.gr-button-primary {{
  background: linear-gradient(135deg, {ACCENT} 0%, #7c3aed 100%) !important;
  color: white !important;
  box-shadow: 0 4px 14px {ACCENT}40;
}}
.gr-button-primary:hover {{
  background: linear-gradient(135deg, {ACCENT_HOVER} 0%, #8b5cf6 100%) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px {ACCENT}50;
}}
.gr-button-secondary {{
  background: linear-gradient(135deg, {BG_CARD} 0%, rgba(39,39,42,0.9) 100%) !important;
  color: {TEXT} !important;
  border: 1px solid {BORDER} !important;
  backdrop-filter: blur(8px);
}}
.gr-button-secondary:hover {{
  background: linear-gradient(135deg, {BORDER} 0%, #3f3f46 100%) !important;
  border-color: {TEXT_MUTED}50 !important;
  transform: translateY(-1px);
}}

/* Accordion / blocks */
.gr-form {{
  border: none !important;
  background: transparent !important;
}}
.gr-padded {{
  padding: 0.5rem 0 !important;
}}
footer.gradio-footer {{ display: none !important; }}

/* Progress bars */
.model-bar {{
  height: 8px;
  background: {BORDER};
  border-radius: 4px;
  overflow: hidden;
}}
.model-bar-fill {{
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}}
"""


def _escape(s: str) -> str:
    return html.escape(s) if s else ""


def format_prediction_html(result: Dict[str, Any], config: Config) -> str:
    """Output routing come HTML per tema dark."""
    if not result.get("success"):
        err = _escape(result.get("error", "Unknown error"))
        return f"""
        <div class="card" style="border-color: rgba(248,113,113,0.4);">
          <div class="card-title" style="color: {ERROR};">Routing failed</div>
          <p style="margin:0; color: {TEXT_MUTED};">{err}</p>
        </div>
        """
    model = _escape(str(result["predicted_model"]))
    conf = result["confidence"]
    conf_pct = int(round(conf * 100))
    low_conf = conf < config.CONFIDENCE_THRESHOLD
    # Top N come lista compatta
    probs = result.get("all_probabilities") or {}
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[: config.TOP_N_PREDICTIONS]
    bars = ""
    for i, (m, p) in enumerate(sorted_probs):
        pct = int(round(p * 100))
        bar_w = max(2, pct)
        is_selected = m == result["predicted_model"]
        bar_color = ACCENT if is_selected else BORDER
        bars += f"""
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;">
          <span style="flex:0 0 140px;font-size:0.8125rem;color:{TEXT if is_selected else TEXT_MUTED};font-weight:{'600' if is_selected else '400'};">{_escape(str(m))}</span>
          <div style="flex:1;height:6px;background:{BORDER};border-radius:3px;overflow:hidden;">
            <div style="width:{bar_w}%;height:100%;background:{bar_color};border-radius:3px;transition:width 0.3s ease;"></div>
          </div>
          <span style="font-size:0.8125rem;color:{TEXT_MUTED};width:2.5rem;">{pct}%</span>
        </div>
        """
    reason = "High confidence match." if not low_conf else f"Confidence below {config.CONFIDENCE_THRESHOLD:.0%}. Consider optimizing the prompt for a better fit."
    return f"""
    <div class="card">
      <div class="card-title">Selected model</div>
      <div style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.4rem 0.75rem;background:rgba(99,102,241,0.15);border:1px solid {ACCENT};border-radius:8px;margin-bottom:1rem;">
        <span style="font-weight:600;color:{ACCENT};">{model}</span>
        <span style="font-size:0.8125rem;color:{TEXT_MUTED};">{conf_pct}% confidence</span>
      </div>
      <div class="card-title">Why this model</div>
      <p style="margin:0 0 1rem 0;font-size:0.875rem;color:{TEXT_MUTED};line-height:1.5;">{_escape(reason)}</p>
      <div class="card-title">Top candidates</div>
      <div style="margin-top:0.25rem;">{bars}</div>
    </div>
    """


def format_improvement_html(
    result: Dict[str, Any],
    before_route: Dict[str, Any] | None = None,
    after_route: Dict[str, Any] | None = None,
) -> str:
    """Output optimize prompt come HTML."""
    if not result.get("success"):
        err = _escape(result.get("error", "Unknown error"))
        return f"""
        <div class="card" style="border-color: rgba(248,113,113,0.4);">
          <div class="card-title" style="color: {ERROR};">Optimization failed</div>
          <p style="margin:0;font-size:0.875rem;color:{TEXT_MUTED};">{err}</p>
          <p style="margin:0.5rem 0 0;font-size:0.75rem;color:{TEXT_MUTED};">Ensure Ollama is running and the model is installed.</p>
        </div>
        """
    improved = _escape(result.get("improved_prompt", ""))
    elapsed = result.get("elapsed_time", 0)
    route_details = ""
    if before_route and before_route.get("success"):
        before_model = _escape(str(before_route.get("predicted_model")))
        before_conf = int(round(float(before_route.get("confidence", 0)) * 100))
        route_details += (
            f'<p style="margin:0 0 0.4rem;font-size:0.8rem;color:{TEXT_MUTED};">'
            f'Route before optimization: <span style="color:{TEXT};font-weight:600;">{before_model}</span> ({before_conf}%)'
            f"</p>"
        )
    if after_route and after_route.get("success"):
        after_model = _escape(str(after_route.get("predicted_model")))
        after_conf = int(round(float(after_route.get("confidence", 0)) * 100))
        route_details += (
            f'<p style="margin:0 0 0.75rem;font-size:0.8rem;color:{TEXT_MUTED};">'
            f'Route after optimization: <span style="color:{TEXT};font-weight:600;">{after_model}</span> ({after_conf}%)'
            f"</p>"
        )
    return f"""
    <div class="card" style="border-color: rgba(52,211,153,0.25);">
      <div class="card-title" style="color: {SUCCESS};">Optimized prompt</div>
      <p style="margin:0 0 0.5rem;font-size:0.75rem;color:{TEXT_MUTED};">Generated in {elapsed:.2f}s</p>
      {route_details}
      <div style="background:{BG_INPUT};border:1px solid {BORDER};border-radius:8px;padding:1rem;font-size:0.875rem;line-height:1.6;color:{TEXT};white-space:pre-wrap;">{improved}</div>
    </div>
    """


def create_gradio_interface(config: Config, model_cache: ModelCache) -> gr.Blocks:
    def improve_wrapper(prompt: str) -> Tuple[str, str, gr.update]:
        if not prompt or not prompt.strip():
            return (
                f'<div class="card"><div class="card-title" style="color:{TEXT_MUTED};">Enter a prompt first</div><p style="margin:0;color:{TEXT_MUTED};">Type your request above, then click Optimize Prompt.</p></div>',
                "",
                gr.update(visible=False),
            )
        logger.info("Avvio miglioramento prompt...")
        before_route = predict_model(prompt, config, model_cache)
        target_model = before_route.get("predicted_model") if before_route.get("success") else None
        result = improve_prompt_with_ollama(prompt, config, target_model=target_model)
        improved = result.get("improved_prompt") or ""
        after_route = (
            predict_model(improved, config, model_cache)
            if improved
            else None
        )
        html_out = format_improvement_html(result, before_route, after_route)
        return html_out, improved, gr.update(visible=bool(improved))

    def predict_wrapper(prompt: str) -> str:
        if not prompt or not prompt.strip():
            return f'<div class="card"><div class="card-title" style="color:{TEXT_MUTED};">Enter a prompt</div><p style="margin:0;color:{TEXT_MUTED};">Type your request and click Route to AI.</p></div>'
        result = predict_model(prompt, config, model_cache)
        return format_prediction_html(result, config)

    theme = gr.themes.Base(
        primary_hue="violet",
        secondary_hue="slate",
        neutral_hue="slate",
    ).set(
        body_background_fill=BG_DARK,
        block_background_fill=BG_DARK,
        block_border_color=BORDER,
        block_label_background_fill=BG_CARD,
        block_label_text_color=TEXT_MUTED,
        block_title_text_color=TEXT,
        button_primary_background_fill=ACCENT,
        button_primary_background_fill_hover=ACCENT_HOVER,
        button_primary_text_color=TEXT,
        button_secondary_background_fill=BG_CARD,
        button_secondary_text_color=TEXT,
        input_background_fill=BG_INPUT,
        input_border_color=BORDER,
        input_placeholder_color=TEXT_MUTED,
        body_text_color=TEXT,
    )

    with gr.Blocks(
        title="AI Router",
        theme=theme,
        css=CUSTOM_CSS,
    ) as interface:
        gr.HTML(f"""
        <div class="app-header">
          <h1 class="app-logo">AI <span>Router</span></h1>
          <span class="status-pill">System ready</span>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=3):
                prompt_input = gr.Textbox(
                    label="",
                    placeholder="Paste or type your prompt. Optimize it first for better routing.",
                    lines=6,
                    max_lines=14,
                    show_label=False,
                    elem_classes=["prompt-input"],
                )
                with gr.Row():
                    improve_btn = gr.Button(
                        "Optimize Prompt",
                        variant="secondary",
                        size="lg",
                    )
                    predict_btn = gr.Button(
                        "Route to AI",
                        variant="primary",
                        size="lg",
                    )

                gr.HTML('<div class="card-title" style="margin-top:1.5rem;">Routing result</div>')
                prediction_output = gr.HTML(
                    value=f'<div class="card"><p style="margin:0;color:{TEXT_MUTED};">No result yet. Enter a prompt and click Route to AI.</p></div>',
                    elem_id="prediction-output",
                )

            with gr.Column(scale=1):
                gr.HTML('<div class="card-title">Optimized prompt</div>')
                improvement_output = gr.HTML(
                    value=f'<div class="card"><p style="margin:0;color:{TEXT_MUTED};">Optional. Click Optimize Prompt to refine your text before routing.</p></div>',
                )
                improved_prompt_box = gr.Textbox(
                    label="",
                    placeholder="Optimized text will appear here.",
                    lines=5,
                    max_lines=10,
                    visible=False,
                    show_label=False,
                )
                copy_btn = gr.Button(
                    "Use in prompt",
                    variant="secondary",
                    size="sm",
                    visible=False,
                )

        with gr.Accordion("Examples", open=False):
            gr.Examples(
                examples=[
                    ["Write a Python function to compute Fibonacci numbers"],
                    ["Explain quantum computing in simple terms"],
                    ["Debug this code: print('Hello World')"],
                    ["How do I optimize my database performance?"],
                    ["Create a marketing plan for a new tech product"],
                ],
                inputs=prompt_input,
                label="",
            )

        improve_btn.click(
            fn=improve_wrapper,
            inputs=prompt_input,
            outputs=[improvement_output, improved_prompt_box, copy_btn],
        )
        copy_btn.click(
            fn=lambda x: x,
            inputs=improved_prompt_box,
            outputs=prompt_input,
        )
        predict_btn.click(
            fn=predict_wrapper,
            inputs=prompt_input,
            outputs=prediction_output,
        )
        prompt_input.submit(
            fn=predict_wrapper,
            inputs=prompt_input,
            outputs=prediction_output,
        )

    return interface
