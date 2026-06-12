"""
Calcolo similarità tra embedding per AI Router.

Funzione principale: compute_similarity_ranking
Input: prompt embedding + model embeddings
Output: lista ordinata [model_id, score]
"""
import logging
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calcola cosine similarity tra due vettori.

    Args:
        vec1: primo vettore (embedding_dim,)
        vec2: secondo vettore (embedding_dim,)

    Returns:
        similarity score in [0, 1]
    """
    # Normalizzazione già fatta in sentence-transformers, ma per sicurezza
    vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-9)
    vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-9)

    similarity = np.dot(vec1_norm, vec2_norm)

    # Clamp in [0, 1] per evitare numeri negativi per arrotondamenti
    return float(np.clip(similarity, 0.0, 1.0))


def compute_similarity_ranking(
    prompt_embedding: np.ndarray,
    model_embeddings: Dict[str, np.ndarray],
    top_k: int = None
) -> List[Tuple[str, float]]:
    """
    Ranking dei modelli basato su similarità con il prompt.

    Args:
        prompt_embedding: embedding del prompt (embedding_dim,)
        model_embeddings: dict {model_id: embedding}
        top_k: numero massimo di risultati (None = tutti)

    Returns:
        Lista ordinata [(model_id, score), ...] decrescente per score
    """
    similarities = []

    for model_id, model_emb in model_embeddings.items():
        score = cosine_similarity(prompt_embedding, model_emb)
        similarities.append((model_id, score))

    # Ordina per score decrescente
    similarities.sort(key=lambda x: x[1], reverse=True)

    if top_k is not None:
        similarities = similarities[:top_k]

    logger.debug(f"Top model: {similarities[0][0]} (score={similarities[0][1]:.3f})")

    return similarities


def normalize_scores(scores: List[Tuple[str, float]]) -> Dict[str, float]:
    """
    Normalizza i punteggi in [0, 1] con softmax-like scaling.

    Args:
        scores: lista [(model_id, score), ...]

    Returns:
        Dict {model_id: normalized_score}
    """
    if not scores:
        return {}

    # Estrai valori
    values = np.array([s[1] for s in scores])

    # Softmax-like normalization per rendere le differenze più evidenti
    # Formula: exp(score) / sum(exp(all_scores))
    exp_values = np.exp(values)
    normalized = exp_values / np.sum(exp_values)

    # Ricostruisci dict
    return {
        model_id: float(norm_score)
        for (model_id, _), norm_score in zip(scores, normalized)
    }


def get_top_candidates(
    prompt_embedding: np.ndarray,
    model_embeddings: Dict[str, np.ndarray],
    top_n: int = 3
) -> List[Dict[str, any]]:
    """
    Ottiene i top N candidati con metadati.

    Args:
        prompt_embedding: embedding del prompt
        model_embeddings: embeddings dei modelli
        top_n: numero di candidati da restituire

    Returns:
        Lista [{model: str, score: float, rank: int}, ...]
    """
    ranking = compute_similarity_ranking(prompt_embedding, model_embeddings, top_k=top_n)

    candidates = []
    for rank, (model_id, score) in enumerate(ranking, start=1):
        candidates.append({
            "model": model_id,
            "score": round(score, 3),
            "rank": rank
        })

    return candidates
