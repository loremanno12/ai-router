"""
Punto di ingresso per il Sistema Router AI.
"""
import logging
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

from cache import ModelCache
from config import Config
from ollama_service import check_ollama_health
from training import should_retrain, train_model
from predictor import initialize_semantic_routing
# Use NiceGUI orchestrator instead of the old Gradio UI to avoid importing gradio
import nicegui_app as nicegui_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def _apply_thread_limits(cpu_threads: int) -> None:
    """
    Applica i limiti di thread a PyTorch e alle librerie numeriche.
    Senza questo, SentenceTransformer usa tutti i core disponibili,
    saturando la CPU del container al primo encode.
    """
    try:
        import torch
        try:
            torch.set_num_threads(cpu_threads)
        except Exception as e:
            logger.warning('Could not set torch.set_num_threads: %s', e)
        try:
            torch.set_num_interop_threads(max(1, cpu_threads // 2))
        except Exception as e:
            # set_num_interop_threads may fail if parallel work already started
            logger.warning('Could not set torch.set_num_interop_threads: %s', e)
        logger.info("PyTorch threads requested: %d", cpu_threads)
    except ImportError:
        pass

    # OpenMP / MKL / OpenBLAS — usati da numpy/sklearn
    import os
    thread_str = str(cpu_threads)
    for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(var, thread_str)
    logger.info("Env thread limits applicati: %s", thread_str)


def main() -> None:
    logger.info("=" * 60)
    logger.info("Avvio del Sistema Router AI (Semantic Routing)")
    logger.info("=" * 60)

    config = Config()

    # Applica i limiti PRIMA di qualsiasi import che carichi il modello
    _apply_thread_limits(config.CPU_THREADS)

    model_cache = ModelCache()

    # NUOVO: Inizializza routing semantico (sostituisce training sklearn)
    logger.info("Inizializzazione routing semantico...")
    try:
        initialize_semantic_routing(config)
        logger.info("✓ Routing semantico pronto (embedding similarity + rule boosting)")
    except Exception as e:
        logger.error("Errore inizializzazione routing semantico: %s", e)
        sys.exit(1)

    # Legacy: mantieni per compatibilità, ma non più necessario
    # if should_retrain(config):
    #     logger.info("Addestramento del modello sklearn in corso...")
    #     success, message = train_model(config, model_cache)
    #     if not success:
    #         logger.error("Addestramento fallito: %s", message)
    #         sys.exit(1)
    #     logger.info(message)

    if check_ollama_health(config):
        logger.info("✓ Ollama disponibile")
    else:
        logger.warning("Ollama non disponibile - miglioramento prompt disabilitato")

    logger.info("Avvio NiceGUI orchestrator sulla porta 7860")
    logger.info("=" * 60)

    # Start the NiceGUI-based frontend (serves static build at /frontend)
    nicegui_app.run(7860)


if __name__ in {"__main__", "__mp_main__"}:
    main()
