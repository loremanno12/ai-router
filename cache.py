"""Cache per i modelli del Router AI."""
import hashlib
import pickle
import logging
import time
from collections import OrderedDict
from threading import Lock
from pathlib import Path
from typing import Optional

from sentence_transformers import SentenceTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


class PredictionCache:
    """Cache LRU thread-safe per predizioni con TTL."""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, tuple] = OrderedDict()
        self._lock = Lock()  # FIX: OrderedDict non è thread-safe

    def _get_key(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()

    def get(self, prompt: str) -> Optional[dict]:
        key = self._get_key(prompt)
        with self._lock:
            if key in self.cache:
                result, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    self.cache.move_to_end(key)
                    logger.debug("Cache hit per prompt")
                    return result
                del self.cache[key]
        return None

    def set(self, prompt: str, result: dict) -> None:
        key = self._get_key(prompt)
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = (result, time.time())
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self.cache.clear()


class ModelCache:
    """
    Cache per i modelli caricati.

    FIX: Il pattern double-checked locking originale non era atomico —
    tra il primo check e l'acquisizione del lock un altro thread poteva
    già aver caricato il modello, causando un secondo caricamento in parallelo
    (pesante in RAM e CPU). Ora il lock protegge l'intera operazione di load.
    """

    def __init__(self):
        self._embedding_model: Optional[SentenceTransformer] = None
        self._embedding_model_name: Optional[str] = None
        self._embedding_device: Optional[str] = None
        self._classifier: Optional[MLPClassifier] = None
        self._label_encoder: Optional[LabelEncoder] = None
        self._lock = Lock()
        self.prediction_cache = PredictionCache()

    def get_embedding_model(self, model_name: str, device: str = "cpu") -> SentenceTransformer:
        with self._lock:
            if (
                self._embedding_model is None
                or self._embedding_model_name != model_name
                or self._embedding_device != device
            ):
                logger.info("Caricamento modello embedding: %s (device=%s)", model_name, device)
                self._embedding_model = SentenceTransformer(model_name, device=device)
                self._embedding_model_name = model_name
                self._embedding_device = device
        return self._embedding_model

    def get_classifier(self, path: Path) -> Optional[MLPClassifier]:
        with self._lock:
            if self._classifier is None and path.exists():
                logger.info("Caricamento classificatore da: %s", path)
                with open(path, "rb") as f:
                    self._classifier = pickle.load(f)
        return self._classifier

    def get_label_encoder(self, path: Path) -> Optional[LabelEncoder]:
        with self._lock:
            if self._label_encoder is None and path.exists():
                logger.info("Caricamento label encoder da: %s", path)
                with open(path, "rb") as f:
                    self._label_encoder = pickle.load(f)
        return self._label_encoder

    def set_classifier(self, classifier: MLPClassifier) -> None:
        with self._lock:
            self._classifier = classifier

    def set_label_encoder(self, encoder: LabelEncoder) -> None:
        with self._lock:
            self._label_encoder = encoder

    def clear(self) -> None:
        with self._lock:
            self._embedding_model = None
            self._classifier = None
            self._label_encoder = None
