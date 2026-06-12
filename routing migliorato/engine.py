# engine.py
"""
Engine unificato per Prompt Improver:
- OllamaClient: chiamate a Ollama (http://localhost:11434/api/generate)
- Prompt templates: system prompt che cambia con la lingua UI
- ftfy cleanup finale
Requisiti: requests, ftfy
"""

from typing import Optional
import requests
from ftfy import fix_text

# --- Prompt templates -------------------------------------------------------

def get_task_label(task_key: str, ui_lang: str = "it") -> str:
    labels_it = {
        "generic": "assistente generico",
        "coding": "coding e debug",
        "creative": "scrittura creativa",
        "technical": "scrittura tecnica / documentazione",
        "rewrite": "riscrittura / traduzione",
    }
    labels_en = {
        "generic": "general assistant",
        "coding": "coding and debugging",
        "creative": "creative writing",
        "technical": "technical writing / documentation",
        "rewrite": "rewriting / paraphrasing / translation",
    }
    return labels_en.get(task_key, task_key) if ui_lang == "en" else labels_it.get(task_key, task_key)

def _length_description(length: str, ui_lang: str) -> str:
    """Traduce la lunghezza in una descrizione per il modello."""
    if ui_lang == "en":
        return {
            "breve": "very short (1-2 sentences, max 50 words)",
            "medio": "medium (3-5 sentences, 50-150 words)",
            "dettagliato": "detailed (one or more paragraphs, 150+ words)"
        }.get(length, length)
    else:
        return {
            "breve": "molto breve (1-2 frasi, max 50 parole)",
            "medio": "medio (3-5 frasi, 50-150 parole)",
            "dettagliato": "dettagliato (uno o più paragrafi, 150+ parole)"
        }.get(length, length)

def build_system_prompt(task_type: str, tone: str, length: str, target_lang: str, ui_lang: str = "it") -> str:
    """
    System prompt che istruisce il modello a comportarsi come Prompt Engineer.
    Il testo è volutamente conciso: il modello deve restituire SOLO il prompt migliorato.
    """
    # Gestione di "auto" per target_lang
    if target_lang == "auto":
        target_lang = "English" if ui_lang == "en" else "italiano"
    
    length_desc = _length_description(length, ui_lang)
    
    if ui_lang == "en":
        return (
            "You are an expert Prompt Engineer and writing assistant.\n\n"
            "Your job:\n"
            "1. Take the user's raw prompt.\n"
            "2. Clarify, structure, and expand it so it becomes unambiguous and explicit about goals, constraints, and style.\n"
            f"3. Adapt it for: {get_task_label(task_type, 'en')}.\n"
            f"4. Respect Tone: {tone}; Length: {length_desc}; Output language: {target_lang}.\n\n"
            "Return ONLY the improved prompt, without explanations, notes, or extra text."
        )
    return (
        "Sei un Prompt Engineer esperto e assistente di scrittura.\n\n"
        "Il tuo compito:\n"
        "1. Prendere il prompt grezzo dell'utente.\n"
        "2. Riscriverlo in modo chiaro, strutturato (obiettivo, contesto, vincoli, formato output) e non ambiguo.\n"
        f"3. Adattarlo a: {get_task_label(task_type, 'it')}.\n"
        f"4. Rispettare Tono: {tone}; Lunghezza: {length_desc}; Lingua output: {target_lang}.\n\n"
        "Restituisci SOLO il prompt migliorato, senza spiegazioni, note o testo aggiuntivo."
    )

def build_full_prompt(raw_prompt: str, task_type: str, tone: str, length: str, target_lang: str, ui_lang: str = "it") -> str:
    system = build_system_prompt(task_type, tone, length, target_lang, ui_lang)
    if ui_lang == "en":
        return f"{system}\n\nUser raw prompt:\n{raw_prompt}\n"
    return f"{system}\n\nPrompt grezzo dell'utente:\n{raw_prompt}\n"

# --- Ollama client ---------------------------------------------------------

class OllamaClient:
    """
    Minimal Ollama client per chiamare l'endpoint /api/generate in locale.
    - base_url: es. http://localhost:11434
    - default_model: stringa modello (campo libero in UI)
    - timeout: 120s come richiesto
    """

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "qwen2.5:3b", timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = int(timeout)

    def _call_ollama(self, model: str, prompt: str, temperature: float = 0.7, top_p: float = 0.9) -> str:
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": float(temperature), "top_p": float(top_p)},
        }
        url = f"{self.base_url}/api/generate"
        resp = requests.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("response") or data.get("text") or data.get("output") or ""
        return text

    def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7, top_p: float = 0.9) -> str:
        raw = self._call_ollama(model or self.default_model, prompt, temperature, top_p)
        cleaned = fix_text(raw)
        return cleaned.strip()

    def improve_prompt(
        self,
        raw_prompt: str,
        task_type: str = "generic",
        tone: str = "neutro",
        length: str = "medio",
        target_lang: str = "auto",
        ui_lang: str = "it",
        model: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Costruisce il prompt completo (system + user) e lo invia al modello.
        Restituisce il testo pulito (ftfy) prodotto dal modello.
        """
        full_prompt = build_full_prompt(
            raw_prompt=raw_prompt.strip(),
            task_type=task_type,
            tone=tone,
            length=length,
            target_lang=target_lang,
            ui_lang=ui_lang,
        )
        return self.generate(prompt=full_prompt, model=model, temperature=temperature, top_p=top_p)