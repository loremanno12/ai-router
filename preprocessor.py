"""
Pre-processing opzionale del prompt per AI Router.

Modalità:
- OFF: testo invariato
- LIGHT: fix encoding (ftfy) + spazi multipli + punteggiatura eccessiva (NO minuscolo)
- FULL: LIGHT + minuscolo + rimozione caratteri speciali (solo per embedding interno)

Rende sempre due versioni:
1. cleaned_for_embedding: testo pulito (LIGHT o FULL)
2. display_text: testo leggibile ( sempre LIGHT)

Mai altera il senso del prompt (no grammar checker).
"""
import logging
import re
from typing import Tuple

try:
    import ftfy
    FTFY_AVAILABLE = True
except ImportError:
    FTFY_AVAILABLE = False

logger = logging.getLogger(__name__)


def preprocess_prompt(text: str, mode: str = "off") -> Tuple[str, str]:
    """
    Pre-processa il prompt secondo la modalità scelta.

    Args:
        text: prompt originale
        mode: "off" | "light" | "full"

    Returns:
        (cleaned_for_embedding, display_text)
        - cleaned_for_embedding: testo per routing (LIGHT o FULL se mode="full")
        - display_text: testo leggibile ( sempre LIGHT)
    """
    if not text:
        return "", ""

    if mode == "off":
        # Nessuna modifica
        return text, text

    # Step 1: fix encoding (ftfy)
    if FTFY_AVAILABLE:
        try:
            cleaned = ftfy.fix_text(text)
        except Exception as e:
            logger.warning(f"ftfy fix_text failed: {e}")
            cleaned = text
    else:
        cleaned = text
        logger.debug("ftfy not available, skipping encoding fix")

    # Step 2: rimuovi spazi multipli
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Step 3: normalizza newline (massimo 2 consecutivi)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Step 4: rimuovi spazi prima di punteggiatura
    cleaned = re.sub(r"\s+([.,;:!?])", r"\1", cleaned)

    # Step 5: rimuovi punteggiatura eccessiva (max 3 ripetizioni)
    cleaned = re.sub(r"([.,;:!?])\1{2,}", r"\1\1", cleaned)

    # LIGHT: questo è il display_text (leggibile, no minuscolo)
    display_text = cleaned.strip()

    # FULL: LIGHT + minuscolo + rimozione caratteri speciali
    if mode == "full":
        cleaned_full = display_text.lower()

        # Rimuovi caratteri speciali ma mantieni lettere, numeri, punteggiatura base
        # Mantieni: lettere accentate, numeri, spazi, punteggiatura base
        cleaned_full = re.sub(r"[^\w\sàèéìòù.,;:!?]", "", cleaned_full, flags=re.UNICODE)
        cleaned_full = re.sub(r"\s+", " ", cleaned_full).strip()

        return cleaned_full, display_text

    # Modalità LIGHT o default
    return display_text, display_text


# Test rapido se eseguito direttamente
if __name__ == "__main__":
    test_prompts = [
        # Prompt con typo, spazi multipli, encoding errato
        "Scrivi  un   codice Python per  l'API!!  Test: â€™encodingâ€™",
        "Analizza  questo...problema    di   matematica???",
        "Ciao!!!   Come va???",
        "Spiega   la   teoria    della    relatività,,,,",
    ]

    print("=" * 70)
    print("TEST PREPROCESSOR")
    print("=" * 70)

    for prompt in test_prompts:
        print(f"\nPROMPT ORIGINALE: {prompt!r}")
        print(f"{'-' * 70}")

        # Modalità OFF
        cleaned_off, display_off = preprocess_prompt(prompt, mode="off")
        print(f"OFF   cleaned: {cleaned_off!r}")
        print(f"OFF   display: {display_off!r}")

        # Modalità LIGHT
        cleaned_light, display_light = preprocess_prompt(prompt, mode="light")
        print(f"LIGHT cleaned: {cleaned_light!r}")
        print(f"LIGHT display: {display_light!r}")

        # Modalità FULL
        cleaned_full, display_full = preprocess_prompt(prompt, mode="full")
        print(f"FULL  cleaned: {cleaned_full!r}")
        print(f"FULL  display: {display_full!r}")

        print("=" * 70)
