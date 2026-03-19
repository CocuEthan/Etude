"""Min-max feature normalizer using p1/p99 percentiles."""
from __future__ import annotations

import numpy as np


class FeatureNormalizer:
    """Clips to [p1, p99] then scales to [0, 1]."""

    def __init__(self):
        self.mins: np.ndarray | None = None
        self.maxs: np.ndarray | None = None

    def fit(self, X: np.ndarray) -> "FeatureNormalizer":
        X = np.array(X, dtype=float)
        self.mins = np.percentile(X, 1, axis=0)
        self.maxs = np.percentile(X, 99, axis=0)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.array(X, dtype=float)
        rng = self.maxs - self.mins
        rng[rng == 0] = 1.0  # avoid division by zero
        return np.clip((X - self.mins) / rng, 0.0, 1.0)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)

    def to_dict(self) -> dict:
        return {
            "mins": self.mins.tolist(),
            "maxs": self.maxs.tolist(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FeatureNormalizer":
        n = cls()
        n.mins = np.array(d["mins"])
        n.maxs = np.array(d["maxs"])
        return n
