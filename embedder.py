"""
Embedder per AI Router con sentence-transformers e cache su disco.

Pattern: simile a ModelCache esistente, ma specializzato per:
- Embedding dei prompt (get_prompt_embedding)
- Embedding dei modelli (get_model_embeddings)
- Cache su disk che si aggiorna solo se models.json cambia
"""
import hashlib
import json
import logging
from pathlib import Path
from threading import Lock
from typing import List, Dict, Optional

from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

# Default embedding model (multilingue per italiano, CPU-optimized)
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbedderCache:
    """
    Cache su disco per gli embedding dei modelli.

    Si aggiorna SOLO se:
    1. Il file non esiste
    2. models.json è stato modificato (hash diverso)

    Formato file:
    {
        "models_hash": "...",
        "embedding_model": "...",
        "embeddings": {
            "model_id": [0.1, 0.2, ...],
            ...
        }
    }
    """

    def __init__(self, cache_dir: Path = Path("models")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "model_embeddings.json"
        self._lock = Lock()

    def _get_models_hash(self, models_path: Path) -> str:
        """Calcola hash SHA256 di models.json."""
        if not models_path.exists():
            return ""
        content = models_path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    def load(self, models_path: Path, embedding_model_name: str) -> Optional[Dict[str, List[float]]]:
        """
        Carica embeddings dalla cache se valido.

        Returns None se:
        - Cache non esiste
        - models.json cambiato
        - embedding model diverso
        """
        with self._lock:
            if not self.cache_file.exists():
                logger.debug("Cache embedding non trovata")
                return None

            try:
                with open(self.cache_file, 'r') as f:
                    cached = json.load(f)

                current_hash = self._get_models_hash(models_path)
                cached_hash = cached.get("models_hash", "")
                cached_model = cached.get("embedding_model", "")

                if current_hash != cached_hash:
                    logger.info("models.json modificato, cache embedding invalidata")
                    return None

                if cached_model != embedding_model_name:
                    logger.info(f"Modello embedding cambiato: {cached_model} -> {embedding_model_name}")
                    return None

                logger.info("Cache embedding valida, caricamento da disco")
                return cached.get("embeddings", {})

            except Exception as e:
                logger.warning(f"Errore caricamento cache embedding: {e}")
                return None

    def save(self, models_path: Path, embedding_model_name: str, embeddings: Dict[str, np.ndarray]) -> None:
        """Salva embeddings su disco."""
        with self._lock:
            try:
                # Converti numpy array in liste per JSON
                embeddings_serializable = {
                    model_id: emb.tolist() for model_id, emb in embeddings.items()
                }

                data = {
                    "models_hash": self._get_models_hash(models_path),
                    "embedding_model": embedding_model_name,
                    "embeddings": embeddings_serializable
                }

                with open(self.cache_file, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info(f"Cache embedding salvata: {len(embeddings)} modelli")

            except Exception as e:
                logger.error(f"Errore salvataggio cache embedding: {e}")


class Embedder:
    """
    Gestisce embedding di prompt e modelli con cache.

    Integrato con ModelCache esistente (riutilizza sentence-transformers).
    """

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        device: str = "cpu",
        cache_dir: Path = Path("models")
    ):
        self.model_name = model_name
        self.device = device
        self._model: Optional[SentenceTransformer] = None
        self._cache = EmbedderCache(cache_dir)
        self._model_embeddings: Optional[Dict[str, np.ndarray]] = None
        self._lock = Lock()

    def _load_model(self) -> SentenceTransformer:
        """Carica sentence-transformer se non già caricato."""
        with self._lock:
            if self._model is None:
                logger.info(f"Caricamento modello embedding: {self.model_name} (device={self.device})")
                self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def get_prompt_embedding(self, prompt: str) -> np.ndarray:
        """
        Calcola embedding per un singolo prompt.

        Returns:
            np.ndarray shape (embedding_dim,)
        """
        model = self._load_model()
        embedding = model.encode(
            prompt,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding

    def get_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Calcola embeddings per batch di testi.

        Returns:
            np.ndarray shape (batch_size, embedding_dim)
        """
        model = self._load_model()
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings

    def get_model_embeddings(
        self,
        models_path: Path = Path("models.json"),
        force_reload: bool = False
    ) -> Dict[str, np.ndarray]:
        """
        Ottiene embedding per tutti i modelli (con cache).

        Per ogni modello, crea un testo descrittivo combinando:
        - description
        - keywords
        - strengths

        Returns:
            Dict[model_id, embedding_array]
        """
        if not force_reload and self._model_embeddings is not None:
            return self._model_embeddings

        # Prova a caricare da cache
        cached = self._cache.load(models_path, self.model_name)
        if cached is not None:
            # Converti liste in numpy arrays
            self._model_embeddings = {
                model_id: np.array(emb, dtype=np.float32)
                for model_id, emb in cached.items()
            }
            return self._model_embeddings

        # Carica models.json e calcola embeddings
        if not models_path.exists():
            raise FileNotFoundError(f"File modelli non trovato: {models_path}")

        with open(models_path, 'r', encoding='utf-8') as f:
            models_data = json.load(f)

        # Crea testi descrittivi per embedding
        model_texts = {}
        for model in models_data:
            model_id = model['id']
            # Combina description + keywords + strengths per embedding ricco
            text_parts = [model.get('description', '')]

            keywords = model.get('keywords', [])
            if keywords:
                text_parts.append("Keywords: " + ", ".join(keywords[:10]))

            strengths = model.get('strengths', [])
            if strengths:
                text_parts.append("Strengths: " + ", ".join(strengths[:5]))

            model_texts[model_id] = " ".join(text_parts)

        # Calcola embeddings in batch
        model_ids = list(model_texts.keys())
        texts = [model_texts[mid] for mid in model_ids]

        logger.info(f"Calcolo embedding per {len(texts)} modelli...")
        embeddings = self.get_batch_embeddings(texts)

        # Costruisci dict
        self._model_embeddings = {
            model_id: emb for model_id, emb in zip(model_ids, embeddings)
        }

        # Salva in cache
        self._cache.save(models_path, self.model_name, self._model_embeddings)

        return self._model_embeddings

    def warmup(self, models_path: Path = Path("models.json")) -> None:
        """
        Precarica modello e embeddings (chiamato all'avvio).

        Utile per evitare latenza al primo prompt.
        """
        logger.info("Warmup embedder...")
        self._load_model()
        self.get_model_embeddings(models_path)
        logger.info("Embedder pronto")


def get_embedder(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    device: str = "cpu",
    cache_dir: Path = Path("models")
) -> Embedder:
    """
    Factory function per ottenere embedder singleton.

    Integrabile con ModelCache esistente.
    """
    return Embedder(model_name=model_name, device=device, cache_dir=cache_dir)
