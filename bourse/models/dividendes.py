"""ModelDividendes : signal dividendes (1 an) depuis métriques de rendement."""
from __future__ import annotations

import os

import numpy as np

from models.base import NeuralNetwork, WEIGHTS_DIR
from models.normalizer import FeatureNormalizer

WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "dividendes.json")

# Features: rendement_pct, payout_ratio, croissance_div_3ans, stabilite_div
_FEATURE_DEFAULTS = [2.0, 50.0, 0.0, 0.5]


def compute_div_features(data: dict) -> dict:
    """Compute derived dividend features from a get_dividend_data() result.

    Adds two keys:
    - croissance_div_3ans : CAGR (%) of dividends over the last 3 years
    - stabilite_div       : fraction of last 3 years with a non-zero dividend
                            (0.0 to 1.0)
    """
    history = data.get("historique_5ans", [])
    croissance = 0.0
    stabilite = 0.0

    if history and len(history) >= 1:
        by_year = sorted(history, key=lambda x: x["year"])
        recent = [h for h in by_year if h["year"] >= by_year[-1]["year"] - 2]

        if len(recent) >= 2:
            first_val = recent[0]["total"]
            last_val = recent[-1]["total"]
            n_years = recent[-1]["year"] - recent[0]["year"]
            if first_val > 0 and n_years > 0:
                croissance = ((last_val / first_val) ** (1.0 / n_years) - 1) * 100
            elif first_val == 0 and last_val > 0:
                croissance = 100.0

        max_year = by_year[-1]["year"]
        years_with_div = sum(
            1
            for h in by_year
            if h["year"] >= max_year - 2 and h["total"] > 0
        )
        stabilite = years_with_div / 3.0

    return {
        **data,
        "croissance_div_3ans": round(croissance, 2),
        "stabilite_div": round(stabilite, 2),
    }


class ModelDividendes:
    """ML model for dividend-focused directional signal (1-year horizon)."""

    def __init__(self):
        self._net: NeuralNetwork | None = None
        self._normalizer: FeatureNormalizer | None = None
        self._medians: list[float] | None = None
        self.trained: bool = False
        self._try_load()

    def _try_load(self) -> None:
        if not os.path.exists(WEIGHTS_PATH):
            return
        try:
            self._net, self._normalizer, self._medians, _, _ = NeuralNetwork.load(
                WEIGHTS_PATH
            )
            self.trained = True
        except Exception:
            self.trained = False

    def extract_features(self, data: dict) -> list[float]:
        """Extract 4 features from a get_dividend_data() dict (auto-enriched)."""
        enriched = compute_div_features(data)
        keys = [
            "rendement_pct",
            "payout_ratio",
            "croissance_div_3ans",
            "stabilite_div",
        ]
        feats: list[float] = []
        for k, default in zip(keys, _FEATURE_DEFAULTS):
            v = enriched.get(k)
            if v is None or v == "N/A":
                feats.append(None)  # type: ignore[arg-type]
            else:
                try:
                    feats.append(float(v))
                except (TypeError, ValueError):
                    feats.append(None)  # type: ignore[arg-type]

        for i, v in enumerate(feats):
            if v is None:
                feats[i] = (
                    self._medians[i]
                    if self._medians is not None
                    else _FEATURE_DEFAULTS[i]
                )
        return feats

    def predict(self, data: dict) -> tuple[list[float], str, float] | None:
        """Returns (probas, signal_str, confidence) or None if not trained."""
        if not self.trained or self._net is None:
            return None
        feats = self.extract_features(data)
        x = np.array(feats, dtype=float)
        if self._normalizer is not None:
            x = self._normalizer.transform(x.reshape(1, -1))[0]
        probas, cls_idx = self._net.predict(x)
        return probas, NeuralNetwork.LABELS[cls_idx], probas[cls_idx]
