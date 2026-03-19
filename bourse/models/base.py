"""NeuralNetwork : 2-layer net (N → 16 ReLU → 3 Softmax), pure numpy.

Labels: 0 = VENDRE, 1 = CONSERVER, 2 = ACHETER

Path resolution works both in dev (project root) and inside a PyInstaller
bundle (_MEIPASS).
"""
from __future__ import annotations

import json
import os

import numpy as np

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
_MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_DIR = os.path.join(_MODELS_DIR, "weights")


class NeuralNetwork:
    """2-layer feed-forward neural network trained with SGD + momentum."""

    LABELS = ["VENDRE", "CONSERVER", "ACHETER"]

    def __init__(self, n_features: int):
        self.n = n_features
        # Xavier initialisation
        self.W1 = np.random.randn(n_features, 16) * np.sqrt(2.0 / n_features)
        self.b1 = np.zeros(16)
        self.W2 = np.random.randn(16, 3) * np.sqrt(2.0 / 16)
        self.b2 = np.zeros(3)

    # ------------------------------------------------------------------
    # Activations
    # ------------------------------------------------------------------
    @staticmethod
    def _relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, x)

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax (log-sum-exp trick)."""
        x = x - np.max(x, axis=-1, keepdims=True)
        e = np.exp(x)
        return e / e.sum(axis=-1, keepdims=True)

    # ------------------------------------------------------------------
    # Forward pass
    # ------------------------------------------------------------------
    def forward(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """X : (n_samples, n_features) or (n_features,).
        Returns (H, probas) where H is hidden activations."""
        X = np.atleast_2d(X)
        H = self._relu(X @ self.W1 + self.b1)
        probas = self._softmax(H @ self.W2 + self.b2)
        return H, probas

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------
    def predict(self, x: np.ndarray) -> tuple[list[float], int]:
        """x : 1-D array → (probas list, class_index)."""
        _, probas = self.forward(np.array(x, dtype=float))
        probas = probas[0]
        return probas.tolist(), int(np.argmax(probas))

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 150,
        lr: float = 0.005,
        batch_size: int = 32,
        momentum: float = 0.9,
        class_weights: np.ndarray | None = None,
        verbose: bool = True,
    ) -> tuple[float, float]:
        """SGD mini-batch with momentum.  Returns (train_acc, val_acc)."""
        n = len(X_train)
        eps = 1e-8

        if class_weights is None:
            class_weights = np.ones(3)

        # Momentum buffers
        vW1 = np.zeros_like(self.W1)
        vb1 = np.zeros_like(self.b1)
        vW2 = np.zeros_like(self.W2)
        vb2 = np.zeros_like(self.b2)

        for epoch in range(epochs):
            idx = np.random.permutation(n)
            X_s, y_s = X_train[idx], y_train[idx]

            for start in range(0, n, batch_size):
                Xb = X_s[start : start + batch_size]
                yb = y_s[start : start + batch_size]
                bs = len(Xb)

                # Forward
                H, probs = self.forward(Xb)

                # One-hot targets
                Y_oh = np.zeros((bs, 3))
                Y_oh[np.arange(bs), yb] = 1.0

                # Weighted cross-entropy gradient
                w = class_weights[yb]  # (bs,)
                dZ2 = (probs - Y_oh) * w[:, None] / bs

                dW2 = H.T @ dZ2
                db2 = dZ2.sum(axis=0)

                dH = dZ2 @ self.W2.T
                dH_relu = dH * (H > 0)

                dW1 = Xb.T @ dH_relu
                db1 = dH_relu.sum(axis=0)

                # Gradient clipping
                for g in (dW1, db1, dW2, db2):
                    np.clip(g, -5.0, 5.0, out=g)

                # SGD + momentum update
                vW1 = momentum * vW1 - lr * dW1
                vb1 = momentum * vb1 - lr * db1
                vW2 = momentum * vW2 - lr * dW2
                vb2 = momentum * vb2 - lr * db2

                self.W1 += vW1
                self.b1 += vb1
                self.W2 += vW2
                self.b2 += vb2

            if verbose and (epoch + 1) % 30 == 0:
                tr = self._accuracy(X_train, y_train)
                va = self._accuracy(X_val, y_val)
                print(
                    f"  Epoch {epoch+1:>3}/{epochs} — "
                    f"train_acc: {tr:.3f}  val_acc: {va:.3f}"
                )

        return self._accuracy(X_train, y_train), self._accuracy(X_val, y_val)

    def _accuracy(self, X: np.ndarray, y: np.ndarray) -> float:
        _, probs = self.forward(X)
        preds = np.argmax(probs, axis=1)
        return float(np.mean(preds == y))

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------
    def save(
        self,
        path: str,
        normalizer=None,
        feature_medians=None,
        training_accuracy: float | None = None,
        validation_accuracy: float | None = None,
    ) -> None:
        data: dict = {
            "W1": self.W1.tolist(),
            "b1": self.b1.tolist(),
            "W2": self.W2.tolist(),
            "b2": self.b2.tolist(),
        }
        if normalizer is not None:
            data["normalizer"] = normalizer.to_dict()
        if feature_medians is not None:
            data["feature_medians"] = [float(v) for v in feature_medians]
        if training_accuracy is not None:
            data["training_accuracy"] = float(training_accuracy)
        if validation_accuracy is not None:
            data["validation_accuracy"] = float(validation_accuracy)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    @classmethod
    def load(cls, path: str):
        """Returns (net, normalizer, feature_medians, train_acc, val_acc).
        normalizer may be None if not stored."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        W1 = np.array(data["W1"])
        n_features = W1.shape[0]

        net = cls.__new__(cls)
        net.n = n_features
        net.W1 = W1
        net.b1 = np.array(data["b1"])
        net.W2 = np.array(data["W2"])
        net.b2 = np.array(data["b2"])

        normalizer = None
        if "normalizer" in data:
            from models.normalizer import FeatureNormalizer
            normalizer = FeatureNormalizer.from_dict(data["normalizer"])

        return (
            net,
            normalizer,
            data.get("feature_medians"),
            data.get("training_accuracy"),
            data.get("validation_accuracy"),
        )
