# app.py – Compatible with Gradio 6.x
import gradio as gr
import html
from engine import OllamaClient

# --- CUSTOM_CSS (your existing dark theme) ---------------------------------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root { --accent: #8b5cf6; --accent-hover: #a78bfa; --bg-dark: #09090b; --bg-card: rgba(24, 24, 28, 0.8); --bg-input: rgba(28, 28, 34, 0.6); --border: #27272a; --text: #fafafa; --text-muted: #a1a1aa; }
.gradio-container { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; background: linear-gradient(135deg, #09090b 0%, #0c0c10 50%, #101014 100%) !important; color: #fafafa !important; min-height: 100vh; }
.contain { max-width: 1100px !important; margin: 0 auto !important; padding: 0 1.5rem 2rem !important; }
.app-header { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:1.5rem 0; margin-bottom:2rem; position:relative; }
.app-logo { font-size:1.75rem; font-weight:700; letter-spacing:-0.03em; color:#fafafa; margin:0; background: linear-gradient(135deg, #fafafa 0%, #8b5cf6 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.status-pill { display:inline-flex; align-items:center; gap:0.5rem; padding:0.4rem 0.85rem; border-radius:9999px; font-size:0.8125rem; font-weight:500; background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(6,182,212,0.1) 100%); border:1px solid #8b5cf630; color:#a1a1aa; backdrop-filter: blur(8px); }
.card { background: linear-gradient(135deg, rgba(24,24,28,0.8) 0%, rgba(20,20,24,0.9) 100%); border:1px solid #27272a; border-radius:16px; padding:1.5rem; margin-bottom:1rem; backdrop-filter: blur(12px); box-shadow: 0 4px 24px rgba(0,0,0,0.2); }
.gr-box { background: linear-gradient(135deg, rgba(28,28,34,0.6) 0%, rgba(24,24,30,0.8) 100%) !important; border:1px solid #27272a !important; border-radius:12px !important; color:#fafafa !important; }
.gr-button-primary { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important; color: white !important; box-shadow: 0 4px 14px #8b5cf640; border-radius:10px !important; font-weight:600 !important; }
.gr-button-secondary { background: linear-gradient(135deg, rgba(24,24,28,0.8) 0%, rgba(39,39,42,0.9) 100%) !important; color:#fafafa !important; border:1px solid #27272a !important; border-radius:10px !important; font-weight:600 !important; }
footer.gradio-footer { display:none !important; }
"""

BG_INPUT = "rgba(28, 28, 34, 0.6)"
BORDER = "#27272a"
TEXT_MUTED = "#a1a1aa"
TEXT = "#fafafa"

client = OllamaClient(timeout=120)

# --- Test Ollama availability ----------------------------------------------
try:
    import requests
    requests.get("http://localhost:11434/api/tags", timeout=5)
    OLLAMA_AVAILABLE = True
except:
    OLLAMA_AVAILABLE = False

# --- Helper functions (ui_texts, route_prompt, improve_wrapper, copy_to_input) 
# --- they remain exactly as you had them, but I'll include them for completeness.

def ui_texts(ui_lang):
    if ui_lang == "en":
        return {
            "status": "System ready",
            "prompt_placeholder": "Paste or type your prompt. Optimize it first for better routing.",
            "optimize_btn": "Optimize Prompt",
            "route_btn": "Route to AI",
            "routing_title": "Routing result",
            "no_result": "No result yet. Enter a prompt and click Route to AI.",
            "optimized_title": "Optimized prompt",
            "model_label": "Ollama model",
            "task_label": "Task type",
            "tone_label": "Tone",
            "length_label": "Length",
            "lang_label": "Output language",
            "temp_label": "Temperature",
            "top_p_label": "Top-p",
            "copy_btn": "Use optimized prompt",
            "improvement_placeholder": "Optional. Click Optimize Prompt to refine your text before routing.",
            "task_choices": {"generic":"General", "coding":"Coding", "creative":"Creative", "technical":"Technical", "rewrite":"Rewrite"},
            "tone_choices": {"neutro":"Neutral", "formale":"Formal", "informale":"Informal"},
            "length_choices": {"breve":"Short", "medio":"Medium", "dettagliato":"Detailed"},
            "lang_choices": {"auto":"Auto", "it":"Italian", "en":"English"},
        }
    else:
        return {
            "status": "Sistema pronto",
            "prompt_placeholder": "Incolla o scrivi il tuo prompt. Ottimizzalo prima per un routing migliore.",
            "optimize_btn": "Ottimizza prompt",
            "route_btn": "Instrada verso AI",
            "routing_title": "Risultato routing",
            "no_result": "Nessun risultato. Inserisci un prompt e clicca Instrada verso AI.",
            "optimized_title": "Prompt ottimizzato",
            "model_label": "Modello Ollama",
            "task_label": "Tipo di task",
            "tone_label": "Tono",
            "length_label": "Lunghezza",
            "lang_label": "Lingua del prompt finale",
            "temp_label": "Temperature",
            "top_p_label": "Top-p",
            "copy_btn": "Usa prompt ottimizzato",
            "improvement_placeholder": "Opzionale. Clicca Ottimizza prompt per raffinare il testo prima del routing.",
            "task_choices": {"generic":"Generico", "coding":"Coding", "creative":"Creativo", "technical":"Tecnico", "rewrite":"Riscrittura"},
            "tone_choices": {"neutro":"Neutro", "formale":"Formale", "informale":"Informale"},
            "length_choices": {"breve":"Breve", "medio":"Medio", "dettagliato":"Dettagliato"},
            "lang_choices": {"auto":"Auto", "it":"Italiano", "en":"Inglese"},
        }

def route_prompt(prompt_text: str, ui_lang: str) -> str:
    prompt_lower = prompt_text.lower()
    if any(word in prompt_lower for word in ["code", "python", "javascript", "debug", "funzione", "errore"]):
        category = "Coding / Debug" if ui_lang == "en" else "Coding / Debug"
        suggested_model = "codellama:7b"
    elif any(word in prompt_lower for word in ["creative", "story", "poem", "creativa", "storia", "poesia"]):
        category = "Creative Writing" if ui_lang == "en" else "Scrittura creativa"
        suggested_model = "mixtral:8x7b"
    elif any(word in prompt_lower for word in ["technical", "doc", "documentation", "tecnica", "documentazione"]):
        category = "Technical Documentation" if ui_lang == "en" else "Documentazione tecnica"
        suggested_model = "llama3:8b"
    else:
        category = "General Assistant" if ui_lang == "en" else "Assistente generico"
        suggested_model = "qwen2.5:3b"
    
    if ui_lang == "en":
        return f"""
        <div class="card" style="border-left: 4px solid #8b5cf6;">
            <strong>📋 Category:</strong> {category}<br>
            <strong>🤖 Suggested model:</strong> <code>{suggested_model}</code><br>
            <strong>💡 Next step:</strong> Set the model above and click "Optimize Prompt" for best results.
        </div>
        """
    else:
        return f"""
        <div class="card" style="border-left: 4px solid #8b5cf6;">
            <strong>📋 Categoria:</strong> {category}<br>
            <strong>🤖 Modello suggerito:</strong> <code>{suggested_model}</code><br>
            <strong>💡 Prossimo passo:</strong> Imposta il modello qui sopra e clicca "Ottimizza prompt".
        </div>
        """

def improve_wrapper(ui_lang_val, prompt, model_name_val, task_type_val, tone_val, length_val, target_lang_val, temperature_val, top_p_val):
    if not prompt or not prompt.strip():
        txt = ui_texts(ui_lang_val)
        msg = f'<div class="card"><div class="card-title" style="color:{TEXT_MUTED};">{"Enter a prompt first" if ui_lang_val=="en" else "Inserisci prima un prompt"}</div><p style="margin:0;color:{TEXT_MUTED};">{txt["prompt_placeholder"]}</p></div>'
        return msg, "", gr.update(visible=False)

    if not OLLAMA_AVAILABLE:
        err_msg = "Ollama is not reachable at http://localhost:11434. Please start Ollama." if ui_lang_val=="en" else "Ollama non è raggiungibile su http://localhost:11434. Avvia Ollama."
        err_html = f'<div class="card" style="border-color: rgba(248,113,113,0.4);"><div class="card-title" style="color:#ef4444;">{"Error" if ui_lang_val=="en" else "Errore"}</div><p style="margin:0;color:{TEXT_MUTED};">{err_msg}</p></div>'
        return err_html, "", gr.update(visible=False)

    try:
        improved = client.improve_prompt(
            raw_prompt=prompt,
            task_type=task_type_val,
            tone=tone_val,
            length=length_val,
            target_lang=target_lang_val,
            ui_lang=ui_lang_val,
            model=model_name_val or None,
            temperature=temperature_val,
            top_p=top_p_val,
        )
    except Exception as e:
        err_html = f'<div class="card" style="border-color: rgba(248,113,113,0.4);"><div class="card-title" style="color:#ef4444;">{"Optimization failed" if ui_lang_val=="en" else "Ottimizzazione fallita"}</div><p style="margin:0;color:{TEXT_MUTED};">{html.escape(str(e))}</p></div>'
        return err_html, "", gr.update(visible=False)

    html_out = f"""
    <div class="card" style="border-color: rgba(52,211,153,0.25);">
      <div class="card-title" style="color:#10b981;">{ui_texts(ui_lang_val)['optimized_title']}</div>
      <div style="background:{BG_INPUT};border:1px solid {BORDER};border-radius:8px;padding:1rem;color:{TEXT};white-space:pre-wrap;">{html.escape(improved)}</div>
    </div>
    """
    return html_out, improved, gr.update(visible=True)

def copy_to_input(x):
    return x

# --- Interface creation ----------------------------------------------------
def create_interface():
    # Theme for Gradio 6.x – create a theme object
    theme = gr.themes.Base(primary_hue="violet", secondary_hue="slate", neutral_hue="slate")

    # NOTE: theme and css will be passed to launch() later, not to Blocks()
    with gr.Blocks(title="AI Router + Prompt Improver") as demo:
        ui_lang = gr.Radio(["it", "en"], value="it", label="Lingua interfaccia / UI language")

        # Header
        status_html = gr.HTML(f'<div class="app-header"><h1 class="app-logo">AI <span>Router</span></h1><span class="status-pill">{"System ready" if OLLAMA_AVAILABLE else "Ollama not found"}</span></div>')

        # Prompt input
        prompt_input = gr.Textbox(
            placeholder="Paste or type your prompt...",
            lines=8,
            max_lines=20,
            show_label=False,
            elem_classes=["prompt-input", "gr-box"],
        )

        with gr.Row():
            improve_btn = gr.Button("Optimize Prompt", variant="secondary", size="lg")
            predict_btn = gr.Button("Route to AI", variant="primary", size="lg")

        prediction_output = gr.HTML(f'<div class="card"><p style="margin:0;color:{TEXT_MUTED};">No result yet. Enter a prompt and click Route to AI.</p></div>')

        with gr.Column(scale=1):
            gr.HTML('<div class="card-title">Optimized prompt</div>')
            # Replace gr.Card with a plain gr.Group or just gr.Column with css class
            with gr.Group(elem_classes=["card"]):
                model_name = gr.Textbox(label="Ollama model", value="qwen2.5:3b", placeholder="e.g., qwen2.5:3b")
                task_type = gr.Dropdown(choices=["generic","coding","creative","technical","rewrite"], value="generic", label="Task type")
                tone = gr.Dropdown(choices=["neutro","formale","informale"], value="neutro", label="Tone")
                length = gr.Dropdown(choices=["breve","medio","dettagliato"], value="medio", label="Length")
                target_lang = gr.Dropdown(choices=["auto","it","en"], value="auto", label="Output language")
                temperature = gr.Slider(minimum=0.0, maximum=1.5, value=0.7, step=0.05, label="Temperature")
                top_p = gr.Slider(minimum=0.0, maximum=1.0, value=0.9, step=0.05, label="Top-p")

            improvement_output = gr.HTML(f'<div class="card"><p style="margin:0;color:{TEXT_MUTED};">Optional. Click Optimize Prompt to refine your text before routing.</p></div>')
            improved_prompt_box = gr.Textbox(label="", placeholder="Optimized text will appear here.", lines=6, max_lines=12, visible=False, show_label=False)
            copy_btn = gr.Button("Use optimized prompt", variant="secondary", size="sm", visible=False)

        # --- UI language switching callbacks (simplified) --------------------
        def update_ui_lang(lang):
            txt = ui_texts(lang)
            return [
                gr.update(placeholder=txt["prompt_placeholder"]),
                gr.update(value=txt["optimize_btn"]),
                gr.update(value=txt["route_btn"]),
                gr.update(label=txt["model_label"]),
                gr.update(label=txt["task_label"], choices=list(txt["task_choices"].values())),
                gr.update(label=txt["tone_label"], choices=list(txt["tone_choices"].values())),
                gr.update(label=txt["length_label"], choices=list(txt["length_choices"].values())),
                gr.update(label=txt["lang_label"], choices=list(txt["lang_choices"].values())),
                gr.update(label=txt["temp_label"]),
                gr.update(label=txt["top_p_label"]),
                gr.update(value=txt["copy_btn"]),
                f'<div class="card"><p style="margin:0;color:{TEXT_MUTED};">{txt["improvement_placeholder"]}</p></div>',
                f'<div class="card"><p style="margin:0;color:{TEXT_MUTED};">{txt["no_result"]}</p></div>',
                gr.update(value=txt["status"])  # for status_pill? we need to update HTML
            ]

        # Callback for optimize button
        improve_btn.click(
            fn=improve_wrapper,
            inputs=[ui_lang, prompt_input, model_name, task_type, tone, length, target_lang, temperature, top_p],
            outputs=[improvement_output, improved_prompt_box, copy_btn],
        )
        copy_btn.click(fn=copy_to_input, inputs=improved_prompt_box, outputs=prompt_input)

        # Route button
        def route_wrapper(prompt, lang):
            if not prompt or not prompt.strip():
                return f'<div class="card"><p style="margin:0;color:{TEXT_MUTED};">{"Enter a prompt first" if lang=="en" else "Inserisci prima un prompt"}</p></div>'
            return route_prompt(prompt, lang)

        predict_btn.click(fn=route_wrapper, inputs=[prompt_input, ui_lang], outputs=prediction_output)
        prompt_input.submit(fn=route_wrapper, inputs=[prompt_input, ui_lang], outputs=prediction_output)

    return demo

# --- Launch ----------------------------------------------------------------
if __name__ == "__main__":
    demo = create_interface()
    # Pass theme and css to launch() instead of Blocks()
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Base(primary_hue="violet"), css=CUSTOM_CSS)