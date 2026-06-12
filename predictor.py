"""Predizione del modello AI per un dato prompt."""
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from cache import ModelCache
from config import Config
from ollama_service import validate_prompt, improve_prompt_with_ollama
from metrics import Timer
from embedder import Embedder
from similarity import compute_similarity_ranking, normalize_scores
from rules import RulesEngine
from preprocessor import preprocess_prompt

logger = logging.getLogger(__name__)

# Iniettato da api.py al bootstrap dell'app FastAPI
metrics_collector = None

# Nuovi componenti per routing semantico
_embedder = None
_rules_engine = None


def initialize_semantic_routing(config: Config) -> None:
    """
    Inizializza embedder e rules engine.
    Chiamato all'avvio dell'applicazione (vedi main.py).
    """
    global _embedder, _rules_engine

    _embedder = Embedder(
        model_name=config.EMBEDDING_MODEL,
        device=config.EMBEDDING_DEVICE,
        cache_dir=config.MODEL_DIR
    )

    _rules_engine = RulesEngine(rules_path=Path("rules.json"))

    # Warmup: precarica embeddings
    _embedder.warmup(models_path=Path("models.json"))

    logger.info("Semantic routing inizializzato")


def predict_with_pipeline(
    prompt: str,
    config: Config,
    model_cache: ModelCache,
    preproc_mode: str = "off",
    use_improver: bool = False
) -> Dict[str, Any]:
    """
    Pipeline completa: preprocess → routing iniziale → Ollama improvement → routing finale.

    Ordine di esecuzione:
    1. preprocess(prompt, mode) → (cleaned_for_embedding, display_text)
    2. predict_model(cleaned) → routing iniziale con target_model
    3. improve_prompt_with_ollama(display_text, target_model) → improved_prompt
    4. predict_model(improved) → routing finale di conferma

    Args:
        prompt: testo originale dell'utente
        config: configurazione
        model_cache: cache condivisa
        preproc_mode: "off" | "light" | "full"
        use_improver: se True, attiva miglioramento Ollama

    Returns:
        Dict con:
        - success: bool
        - original_prompt: prompt originale
        - preprocessed_prompt: testo pre-processato
        - improved_prompt: testo migliorato da Ollama (o None)
        - initial_routing: risultato routing iniziale
        - final_routing: risultato routing finale (o uguale a initial)
        - routing_changed: True se modello diverso dopo improvement
        - timing: dict con tempo per ogni step
    """
    timing = {}
    result = {
        "success": False,
        "original_prompt": prompt,
        "preprocessed_prompt": None,
        "improved_prompt": None,
        "initial_routing": None,
        "final_routing": None,
        "routing_changed": False,
        "timing": timing,
        "error": None
    }

    try:
        # === STEP 1: Pre-processing ===
        with Timer("Pre-processing") as t_preproc:
            cleaned_for_embedding, display_text = preprocess_prompt(prompt, mode=preproc_mode)
            logger.info(f"[Step 1] Pre-processing ({preproc_mode}): {len(prompt)} → {len(cleaned_for_embedding)} chars")
            result["preprocessed_prompt"] = display_text  # Mostra versione LIGHT

        timing["preprocessing"] = t_preproc.elapsed

        # === STEP 2: Routing iniziale ===
        with Timer("Routing iniziale") as t_routing1:
            initial_result = predict_model(cleaned_for_embedding, config, model_cache)

            if not initial_result.get("success"):
                result["error"] = f"Routing iniziale fallito: {initial_result.get('error')}"
                return result

            target_model = initial_result.get("recommended_model")
            logger.info(f"[Step 2] Routing iniziale: {target_model} (conf={initial_result.get('confidence', 0):.2f})")
            result["initial_routing"] = initial_result

        timing["routing_initial"] = t_routing1.elapsed

        # === STEP 3: Miglioramento Ollama (opzionale) ===
        improved_prompt = None
        if use_improver:
            with Timer("Ollama improvement") as t_ollama:
                ollama_result = improve_prompt_with_ollama(
                    prompt=display_text,  # Usa testo LIGHT (leggibile)
                    config=config,
                    target_model=target_model
                )

                if ollama_result.get("success"):
                    improved_prompt = ollama_result.get("improved_prompt")
                    logger.info(f"[Step 3] Ollama improvement: {len(display_text)} → {len(improved_prompt)} chars")
                    result["improved_prompt"] = improved_prompt
                else:
                    logger.warning(f"[Step 3] Ollama improvement fallito: {ollama_result.get('error')}")
                    # Non fallire pipeline, continua senza improvement

            timing["ollama_improvement"] = t_ollama.elapsed

        # === STEP 4: Routing finale (se improvement attivo e riuscito) ===
        if improved_prompt:
            with Timer("Routing finale") as t_routing2:
                final_result = predict_model(improved_prompt, config, model_cache)

                if final_result.get("success"):
                    final_model = final_result.get("recommended_model")
                    logger.info(f"[Step 4] Routing finale: {final_model} (conf={final_result.get('confidence', 0):.2f})")

                    # Verifica divergenza
                    if final_model != target_model:
                        logger.warning(f"⚠️ Routing cambiato: {target_model} → {final_model}")
                        result["routing_changed"] = True

                    result["final_routing"] = final_result
                else:
                    logger.error(f"Routing finale fallito: {final_result.get('error')}")
                    result["final_routing"] = initial_result  # Fallback

            timing["routing_final"] = t_routing2.elapsed
        else:
            # Se non c'è improvement, routing finale = routing iniziale
            result["final_routing"] = initial_result

        # === SUCCESS ===
        result["success"] = True
        total_time = sum(timing.values())
        timing["total"] = total_time
        logger.info(f"Pipeline completata in {total_time:.2f}s")
        return result

    except Exception as e:
        error_msg = f"Errore pipeline: {str(e)}"
        logger.exception(error_msg)
        result["error"] = error_msg
        return result



def predict_model(
    prompt: str, config: Config, model_cache: ModelCache
) -> Dict[str, Any]:
    """
    Predice quale modello utilizzare per un dato prompt usando:
    1. Embedding similarity (sentence-transformers)
    2. Rule boosting (rules.json)
    3. Ranking con explainability

    Mantiene la stessa firma e cache dell'originale.
    """
    try:
        is_valid, error_msg = validate_prompt(prompt)
        if not is_valid:
            logger.warning("Prompt non valido: %s", error_msg)
            return {
                "success": False,
                "error": error_msg,
                "recommended_model": None,
                "confidence": None,
            }

        # Cache delle predizioni con chiave composta (per differenziare stati)
        cache_key = prompt
        cached_result = model_cache.prediction_cache.get(cache_key)
        if cached_result:
            logger.info("Risultato da cache per il prompt: %s...", prompt[:50])
            if metrics_collector:
                metrics_collector.record_prediction(
                    0.0,
                    is_cache_hit=True,
                    confidence=cached_result.get("confidence", 0.0),
                )
            return cached_result

        # Verifica che il sistema semantic sia inizializzato
        if _embedder is None or _rules_engine is None:
            error_msg = "Sistema di routing semantico non inizializzato. Chiama initialize_semantic_routing()."
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "recommended_model": None,
                "confidence": None,
            }

        with Timer("Predizione semantica") as timer:
            logger.info("Routing semantico per: %s...", prompt[:50])

            # 1. Calcola embedding del prompt
            prompt_embedding = _embedder.get_prompt_embedding(prompt)

            # 2. Ottieni embeddings dei modelli
            model_embeddings = _embedder.get_model_embeddings(Path("models.json"))

            # 3. Calcola similarity ranking
            similarity_ranking = compute_similarity_ranking(
                prompt_embedding,
                model_embeddings,
                top_k=None  # Tutti i modelli
            )

            # 4. Applica rule boosting
            boosted_ranking, reasons = _rules_engine.apply_boosts(prompt, similarity_ranking)

            # 5. Normalizza punteggi
            normalized_scores = normalize_scores(boosted_ranking)

            # 6. Estrai risultati
            top_model = boosted_ranking[0][0]
            top_score = boosted_ranking[0][1]
            confidence = normalized_scores.get(top_model, 0.0)

            # Costruisci ranking per output (top 3)
            ranking = [
                {"model": model, "score": round(score, 3)}
                for model, score in boosted_ranking[:3]
            ]

            # All probabilities (per retrocompatibilità con UI esistente)
            all_probabilities = {
                model: round(score, 4)
                for model, score in normalized_scores.items()
            }

        result = {
            "success": True,
            "error": None,
            "recommended_model": top_model,  # Nuovo campo
            "predicted_model": top_model,    # Retrocompatibilità
            "confidence": confidence,
            "reasons": reasons,                # Nuovo campo
            "ranking": ranking,                # Nuovo campo
            "all_probabilities": all_probabilities,
        }

        if metrics_collector:
            metrics_collector.record_prediction(
                timer.elapsed,
                is_cache_hit=False,
                confidence=confidence,
                threshold=config.CONFIDENCE_THRESHOLD,
            )

        model_cache.prediction_cache.set(cache_key, result)
        return result

    except Exception as e:
        error_msg = f"Errore durante la predizione semantica: {str(e)}"
        logger.exception(error_msg)
        if metrics_collector:
            metrics_collector.record_prediction(0.0, had_error=True)
        return {
            "success": False,
            "error": error_msg,
            "recommended_model": None,
            "predicted_model": None,
            "confidence": None,
        }


def format_prediction_output(result: Dict[str, Any], config: Config) -> str:
    """
    Formatta il risultato della predizione per la visualizzazione.
    Aggiornato per mostrare reasons e ranking.
    """
    if not result["success"]:
        return f"❌ **Errore:** {result['error']}"

    # Usa 'recommended_model' se presente, altrimenti 'predicted_model'
    model = result.get("recommended_model") or result.get("predicted_model")
    confidence = result.get("confidence", 0.0)

    output = f"### 🎯 Modello Consigliato\n\n"
    output += f"**{model}**\n\n"
    output += f"📊 Confidenza: **{confidence:.1%}**\n\n"

    # Mostra reasons (nuovo campo)
    if result.get("reasons"):
        output += "#### 💡 Motivi della scelta\n\n"
        for reason in result["reasons"]:
            output += f"- {reason}\n"
        output += "\n"

    # Mostra ranking (nuovo campo)
    if result.get("ranking"):
        output += "---\n\n"
        output += "### 📈 Top 3 Modelli\n\n"

        for i, item in enumerate(result["ranking"][:3], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            bar_length = int(item["score"] * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            output += f"{medal} **{item['model']}**\n"
            output += f"`{bar}` {item['score']:.1%}\n\n"

    # Legacy: all_probabilities
    elif result.get("all_probabilities"):
        output += "---\n\n"
        output += "### 📈 Top 3 Modelli\n\n"

        sorted_probs = sorted(
            result["all_probabilities"].items(), key=lambda x: x[1], reverse=True
        )[: config.TOP_N_PREDICTIONS]

        for i, (model_name, prob) in enumerate(sorted_probs, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            bar_length = int(prob * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            output += f"{medal} **{model_name}**\n"
            output += f"`{bar}` {prob:.1%}\n\n"

    if confidence < config.CONFIDENCE_THRESHOLD:
        output += "\n---\n\n"
        output += f"⚠️ **Attenzione:** Confidenza sotto la soglia del {config.CONFIDENCE_THRESHOLD:.0%}. "
        output += "Considera di migliorare il prompt per risultati più accurati.\n"

    return output
