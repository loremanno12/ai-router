"""
Rule boosting per AI Router.

Le regole sono definite in rules.json (modificabile senza toccare codice).
Per ogni regola:
- patterns: regex da matchare nel prompt
- models: modelli da boostare
- boost_factor: incremento del punteggio (0.0-1.0)
- reason: motivo leggibile (per explainability)
"""
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class RuleBoost:
    """Rappresenta una singola regola di boost."""

    def __init__(
        self,
        name: str,
        models: List[str],
        patterns: List[str],
        boost_factor: float,
        reason: str
    ):
        self.name = name
        self.models = models
        self.patterns = [re.compile(p) for p in patterns]
        self.boost_factor = boost_factor
        self.reason = reason

    def matches(self, prompt: str) -> bool:
        """Verifica se il prompt matcha almeno un pattern."""
        for pattern in self.patterns:
            if pattern.search(prompt):
                return True
        return False


class RulesEngine:
    """
    Motore di regole per boosting.

    Carica da rules.json e applica boost ai punteggi.
    """

    def __init__(self, rules_path: Path = Path("rules.json")):
        self.rules_path = rules_path
        self.rules: List[RuleBoost] = []
        self._load_rules()

    def _load_rules(self) -> None:
        """Carica regole da rules.json."""
        if not self.rules_path.exists():
            logger.warning(f"File regole non trovato: {self.rules_path}")
            return

        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)

            for rule_dict in rules_data:
                rule = RuleBoost(
                    name=rule_dict['name'],
                    models=rule_dict['models'],
                    patterns=rule_dict['patterns'],
                    boost_factor=rule_dict['boost_factor'],
                    reason=rule_dict['reason']
                )
                self.rules.append(rule)

            logger.info(f"Caricate {len(self.rules)} regole di boost")

        except Exception as e:
            logger.error(f"Errore caricamento regole: {e}")

    def apply_boosts(
        self,
        prompt: str,
        scores: List[Tuple[str, float]]
    ) -> Tuple[List[Tuple[str, float]], List[str]]:
        """
        Applica boost alle regole che matchano.

        Args:
            prompt: testo del prompt
            scores: lista [(model_id, score), ...]

        Returns:
            (boosted_scores, reasons)
            - boosted_scores: lista con punteggi boostati
            - reasons: lista di motivi per explainability
        """
        # Converti in dict per manipolazione
        score_dict = {model: score for model, score in scores}
        reasons = set()

        # Applica ogni regola
        for rule in self.rules:
            if rule.matches(prompt):
                # Aggiungi motivo
                reasons.add(rule.reason)

                # Boost modelli
                for model_id in rule.models:
                    if model_id in score_dict:
                        old_score = score_dict[model_id]
                        new_score = min(1.0, old_score + rule.boost_factor)
                        score_dict[model_id] = new_score
                        logger.debug(
                            f"Boost {rule.name}: {model_id} {old_score:.3f} -> {new_score:.3f}"
                        )

        # Riordina dopo boost
        boosted_scores = sorted(
            score_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return boosted_scores, list(reasons)

    def get_matching_rules(self, prompt: str) -> List[str]:
        """
        Restituisce nomi delle regole che matchano (per debug).

        Args:
            prompt: testo del prompt

        Returns:
            Lista di nomi di regole
        """
        matching = []
        for rule in self.rules:
            if rule.matches(prompt):
                matching.append(rule.name)
        return matching


def load_rules(rules_path: Path = Path("rules.json")) -> RulesEngine:
    """Factory per creare RulesEngine."""
    return RulesEngine(rules_path)
