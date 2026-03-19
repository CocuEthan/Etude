"""ModelLongTerme : signal long terme (6 mois) depuis fondamentaux."""
from __future__ import annotations

import os

import numpy as np

from models.base import NeuralNetwork, WEIGHTS_DIR
from models.normalizer import FeatureNormalizer

WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "long_terme.json")

# Features: pe_ratio, pb_ratio, roe, marge_nette, potentiel_pct
_FEATURE_DEFAULTS = [15.0, 1.5, 10.0, 5.0, 0.0]


class ModelLongTerme:
    """ML model for long-term (6-month) directional signal."""

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
        """Extract 5 features from a get_long_terme_data() dict."""
        keys = ["pe_ratio", "pb_ratio", "roe", "marge_nette", "potentiel_pct"]
        feats: list[float] = []
        for k, default in zip(keys, _FEATURE_DEFAULTS):
            v = data.get(k)
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
