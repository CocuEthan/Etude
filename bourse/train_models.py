"""Script d'entraînement des modèles ML (court_terme / long_terme / dividendes).

Usage
-----
    python train_models.py                          # all 3 models
    python train_models.py --model court_terme      # one model
    python train_models.py --epochs 200 --lr 0.01  # custom hyperparams
    python train_models.py --tickers AC.PA,BNP.PA  # extra tickers
"""
from __future__ import annotations

import argparse
import os
import sys
import warnings

warnings.filterwarnings("ignore")

# Ensure project root is on the path so 'models' and 'config' are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import yfinance as yf

import config
from models.base import NeuralNetwork, WEIGHTS_DIR
from models.normalizer import FeatureNormalizer
from models.dividendes import compute_div_features

# ---------------------------------------------------------------------------
# Ticker list
# ---------------------------------------------------------------------------
ALL_TICKERS = list(config.LISTE_MARCHE_PARIS)

# ---------------------------------------------------------------------------
# Label generation
# ---------------------------------------------------------------------------
BUY_THRESHOLD = 7.0   # % forward return → BUY (2)
SELL_THRESHOLD = -5.0  # % forward return → SELL (0)
# else HOLD (1)


def _make_label(fwd_ret: float) -> int:
    if fwd_ret >= BUY_THRESHOLD:
        return 2
    if fwd_ret <= SELL_THRESHOLD:
        return 0
    return 1


# ---------------------------------------------------------------------------
# Data fetching helpers
# ---------------------------------------------------------------------------
def fetch_price_history(tickers: list[str]) -> dict[str, object]:
    """Download 3 years of weekly OHLCV for all tickers (single batch call)."""
    print(f"\nTéléchargement historique prix ({len(tickers)} tickers, 3 ans, 1wk)…")
    try:
        raw = yf.download(
            tickers,
            period="3y",
            interval="1wk",
            auto_adjust=True,
            progress=False,
            group_by="ticker",
        )
    except Exception as e:
        print(f"  [WARN] yf.download erreur: {e}")
        raw = None

    cache: dict[str, object] = {}
    for sym in tickers:
        try:
            if len(tickers) == 1:
                df = raw
            else:
                df = raw[sym] if raw is not None else None
            if df is not None and not df.empty:
                df = df.dropna(subset=["Close"])
                if len(df) >= 30:
                    cache[sym] = df
        except Exception:
            pass

    # Fallback: fetch individually for any missing ticker
    missing = [s for s in tickers if s not in cache]
    if missing:
        print(f"  Fetch individuel pour {len(missing)} tickers manquants…")
        for sym in missing:
            try:
                df = yf.Ticker(sym).history(period="3y", interval="1wk")
                if not df.empty and len(df) >= 30:
                    cache[sym] = df
            except Exception:
                pass

    print(f"  {len(cache)}/{len(tickers)} tickers avec données historiques.")
    return cache


def fetch_fundamentals(tickers: list[str]) -> dict[str, dict]:
    """Fetch current fundamentals for long_terme (one call per ticker)."""
    print(f"\nTéléchargement fondamentaux ({len(tickers)} tickers)…")
    cache: dict[str, dict] = {}
    for i, sym in enumerate(tickers, 1):
        try:
            inf = yf.Ticker(sym).info
            pe = inf.get("trailingPE")
            pb = inf.get("priceToBook")
            roe = (inf.get("returnOnEquity") or 0) * 100
            marge = (inf.get("profitMargins") or 0) * 100
            px = inf.get("currentPrice") or 0
            tgt = inf.get("targetMeanPrice") or 0
            pot = ((tgt - px) / px * 100) if tgt and px else 0.0
            cache[sym] = {
                "pe_ratio": float(pe) if pe else None,
                "pb_ratio": float(pb) if pb else None,
                "roe": float(roe),
                "marge_nette": float(marge),
                "potentiel_pct": float(pot),
            }
        except Exception:
            pass
        if i % 10 == 0:
            print(f"  {i}/{len(tickers)} fondamentaux téléchargés…")
    print(f"  {len(cache)}/{len(tickers)} tickers avec fondamentaux.")
    return cache


def fetch_dividend_data(tickers: list[str]) -> dict[str, dict]:
    """Fetch current dividend metrics (yield, payout, history)."""
    print(f"\nTéléchargement données dividendes ({len(tickers)} tickers)…")
    cache: dict[str, dict] = {}
    for i, sym in enumerate(tickers, 1):
        try:
            inf = yf.Ticker(sym).info
            px = inf.get("currentPrice") or 0
            rate = inf.get("dividendRate") or 0
            yld = (rate / px * 100) if rate and px else 0.0
            payout_raw = inf.get("payoutRatio")
            payout = round(payout_raw * 100, 1) if payout_raw else 50.0

            history: list[dict] = []
            try:
                divs = yf.Ticker(sym).dividends
                if not divs.empty:
                    divs.index = divs.index.tz_localize(None)
                    from datetime import datetime
                    cutoff = datetime(datetime.now().year - 5, 1, 1)
                    recent = divs[divs.index >= cutoff]
                    by_year = recent.groupby(recent.index.year).sum()
                    history = [
                        {"year": int(y), "total": round(float(v), 4)}
                        for y, v in by_year.items()
                    ]
            except Exception:
                pass

            cache[sym] = {
                "rendement_pct": round(yld, 2),
                "payout_ratio": payout,
                "historique_5ans": history,
            }
        except Exception:
            pass
        if i % 10 == 0:
            print(f"  {i}/{len(tickers)} dividendes téléchargés…")
    print(f"  {len(cache)}/{len(tickers)} tickers avec données dividendes.")
    return cache


# ---------------------------------------------------------------------------
# Dataset builders
# ---------------------------------------------------------------------------
def build_court_terme_dataset(
    tickers: list[str], hist_cache: dict
) -> tuple[np.ndarray, np.ndarray]:
    """4 features per sample: rsi_14, momentum_5j_pct, ratio_volume, position_52s_pct."""
    HORIZON = 3  # weeks forward
    X_list, y_list = [], []

    for sym in tickers:
        df = hist_cache.get(sym)
        if df is None:
            continue
        close = df["Close"].values.astype(float)
        volume = df["Volume"].values.astype(float)
        n = len(close)
        if n < 20 + HORIZON:
            continue

        for i in range(14, n - HORIZON):
            # RSI(14)
            deltas = np.diff(close[i - 14 : i + 1])
            gains = np.where(deltas > 0, deltas, 0.0)
            losses = np.where(deltas < 0, -deltas, 0.0)
            avg_g = gains.mean()
            avg_l = losses.mean()
            rsi = 100.0 if avg_l == 0 else 100.0 - 100.0 / (1.0 + avg_g / avg_l)

            # 5-week momentum
            mom = (
                (close[i] - close[i - 5]) / close[i - 5] * 100
                if i >= 5 and close[i - 5] > 0
                else 0.0
            )

            # Volume ratio vs 20-week average
            if i >= 20:
                vol_avg = volume[i - 20 : i].mean()
                vol_ratio = volume[i] / vol_avg if vol_avg > 0 else 1.0
            else:
                vol_ratio = 1.0

            # 52-week range position
            start52 = max(0, i - 52)
            hi52 = close[start52 : i + 1].max()
            lo52 = close[start52 : i + 1].min()
            pos52 = (
                (close[i] - lo52) / (hi52 - lo52) * 100
                if hi52 > lo52
                else 50.0
            )

            feats = [rsi, mom, vol_ratio, pos52]
            if any(not np.isfinite(f) for f in feats):
                continue

            fwd_ret = (close[i + HORIZON] - close[i]) / close[i] * 100
            if not np.isfinite(fwd_ret):
                continue

            X_list.append(feats)
            y_list.append(_make_label(fwd_ret))

    if not X_list:
        return np.empty((0, 4)), np.empty(0, dtype=int)
    return np.array(X_list, dtype=float), np.array(y_list, dtype=int)


def build_long_terme_dataset(
    tickers: list[str], hist_cache: dict, fund_cache: dict
) -> tuple[np.ndarray, np.ndarray]:
    """5 features: pe_ratio, pb_ratio, roe, marge_nette, potentiel_pct.

    Note: fundamentals are current-snapshot only (look-ahead bias assumed).
    """
    HORIZON = 24  # weeks forward (~6 months)
    X_list, y_list = [], []

    for sym in tickers:
        df = hist_cache.get(sym)
        fund = fund_cache.get(sym)
        if df is None or fund is None:
            continue

        close = df["Close"].values.astype(float)
        n = len(close)
        if n < HORIZON + 1:
            continue

        pe = fund["pe_ratio"] if fund["pe_ratio"] is not None else 15.0
        pb = fund["pb_ratio"] if fund["pb_ratio"] is not None else 1.5
        roe = fund["roe"]
        marge = fund["marge_nette"]
        pot = fund["potentiel_pct"]

        feats_static = [pe, pb, roe, marge, pot]
        if any(not np.isfinite(f) for f in feats_static):
            continue

        for i in range(0, n - HORIZON):
            if close[i] <= 0:
                continue
            fwd_ret = (close[i + HORIZON] - close[i]) / close[i] * 100
            if not np.isfinite(fwd_ret):
                continue
            X_list.append(feats_static)
            y_list.append(_make_label(fwd_ret))

    if not X_list:
        return np.empty((0, 5)), np.empty(0, dtype=int)
    return np.array(X_list, dtype=float), np.array(y_list, dtype=int)


def build_dividendes_dataset(
    tickers: list[str], hist_cache: dict, div_cache: dict
) -> tuple[np.ndarray, np.ndarray]:
    """4 features: rendement_pct, payout_ratio, croissance_div_3ans, stabilite_div."""
    HORIZON = 52  # weeks forward (~1 year)
    X_list, y_list = [], []

    for sym in tickers:
        df = hist_cache.get(sym)
        div_data = div_cache.get(sym)
        if df is None or div_data is None:
            continue

        close = df["Close"].values.astype(float)
        n = len(close)
        if n < HORIZON + 1:
            continue

        enriched = compute_div_features(div_data)
        rend = enriched.get("rendement_pct", 0.0) or 0.0
        payout = enriched.get("payout_ratio", 50.0) or 50.0
        croissance = enriched.get("croissance_div_3ans", 0.0) or 0.0
        stabilite = enriched.get("stabilite_div", 0.0) or 0.0

        feats_static = [float(rend), float(payout), float(croissance), float(stabilite)]
        if any(not np.isfinite(f) for f in feats_static):
            continue

        for i in range(0, n - HORIZON):
            if close[i] <= 0:
                continue
            fwd_ret = (close[i + HORIZON] - close[i]) / close[i] * 100
            if not np.isfinite(fwd_ret):
                continue
            X_list.append(feats_static)
            y_list.append(_make_label(fwd_ret))

    if not X_list:
        return np.empty((0, 4)), np.empty(0, dtype=int)
    return np.array(X_list, dtype=float), np.array(y_list, dtype=int)


# ---------------------------------------------------------------------------
# Training helper
# ---------------------------------------------------------------------------
def compute_class_weights(y: np.ndarray) -> np.ndarray:
    """Inverse-frequency class weights for imbalanced labels."""
    weights = np.ones(3)
    for cls in range(3):
        n_cls = (y == cls).sum()
        if n_cls > 0:
            weights[cls] = len(y) / (3 * n_cls)
    return weights


def train_one_model(
    name: str,
    X: np.ndarray,
    y: np.ndarray,
    weights_path: str,
    epochs: int,
    lr: float,
) -> dict:
    """Split, normalise, train, save.  Returns summary dict."""
    n = len(X)
    if n < 50:
        print(f"  [SKIP] {name}: seulement {n} échantillons, entraînement annulé.")
        return {"model": name, "n_samples": n, "train_acc": None, "val_acc": None,
                "path": None}

    # Shuffle + split 80/20
    idx = np.random.permutation(n)
    split = int(n * 0.8)
    tr_idx, va_idx = idx[:split], idx[split:]
    X_tr, y_tr = X[tr_idx], y[tr_idx]
    X_va, y_va = X[va_idx], y[va_idx]

    # Normalise
    norm = FeatureNormalizer().fit(X_tr)
    X_tr_n = norm.transform(X_tr)
    X_va_n = norm.transform(X_va)

    # Feature medians (for imputation at inference time)
    medians = np.median(X_tr, axis=0).tolist()

    # Class weights
    cw = compute_class_weights(y_tr)

    # Train
    n_features = X.shape[1]
    net = NeuralNetwork(n_features)
    print(f"\n--- Entraînement {name} ({n} échantillons, {n_features} features) ---")
    train_acc, val_acc = net.train(
        X_tr_n, y_tr, X_va_n, y_va,
        epochs=epochs, lr=lr, class_weights=cw,
    )

    # Save
    net.save(
        weights_path,
        normalizer=norm,
        feature_medians=medians,
        training_accuracy=train_acc,
        validation_accuracy=val_acc,
    )
    print(
        f"  → train_acc={train_acc:.3f}  val_acc={val_acc:.3f}  "
        f"sauvegardé: {weights_path}"
    )
    return {
        "model": name,
        "n_samples": n,
        "train_acc": train_acc,
        "val_acc": val_acc,
        "path": weights_path,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Entraîne les modèles ML bourse.")
    parser.add_argument(
        "--model",
        choices=["court_terme", "long_terme", "dividendes"],
        default=None,
        help="Modèle à entraîner (défaut: tous les 3)",
    )
    parser.add_argument("--epochs", type=int, default=150)
    parser.add_argument("--lr", type=float, default=0.005)
    parser.add_argument(
        "--tickers",
        type=str,
        default="",
        help="Tickers supplémentaires séparés par des virgules (ex: AC.PA,BNP.PA)",
    )
    args = parser.parse_args()

    models_to_train = (
        [args.model] if args.model else ["court_terme", "long_terme", "dividendes"]
    )

    tickers = list(ALL_TICKERS)
    if args.tickers:
        extra = [t.strip() for t in args.tickers.split(",") if t.strip()]
        tickers = list(dict.fromkeys(tickers + extra))  # deduplicate, preserve order

    print(f"Tickers : {len(tickers)}")
    print(f"Modèles : {models_to_train}")
    print(f"Epochs  : {args.epochs}  LR : {args.lr}")

    np.random.seed(42)

    # --- Fetch data (shared where possible) ---------------------------------
    hist_cache = fetch_price_history(tickers)

    fund_cache: dict = {}
    div_cache: dict = {}

    if "long_terme" in models_to_train:
        fund_cache = fetch_fundamentals(tickers)

    if "dividendes" in models_to_train:
        div_cache = fetch_dividend_data(tickers)

    # --- Train --------------------------------------------------------------
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    results = []

    if "court_terme" in models_to_train:
        X, y = build_court_terme_dataset(tickers, hist_cache)
        path = os.path.join(WEIGHTS_DIR, "court_terme.json")
        results.append(train_one_model("court_terme", X, y, path, args.epochs, args.lr))

    if "long_terme" in models_to_train:
        X, y = build_long_terme_dataset(tickers, hist_cache, fund_cache)
        path = os.path.join(WEIGHTS_DIR, "long_terme.json")
        results.append(train_one_model("long_terme", X, y, path, args.epochs, args.lr))

    if "dividendes" in models_to_train:
        X, y = build_dividendes_dataset(tickers, hist_cache, div_cache)
        path = os.path.join(WEIGHTS_DIR, "dividendes.json")
        results.append(train_one_model("dividendes", X, y, path, args.epochs, args.lr))

    # --- Summary ------------------------------------------------------------
    print("\n" + "=" * 65)
    print(f"{'Modèle':<14} {'Samples':>8} {'Train Acc':>10} {'Val Acc':>10}  Fichier")
    print("-" * 65)
    for r in results:
        tacc = f"{r['train_acc']:.3f}" if r["train_acc"] is not None else "  N/A"
        vacc = f"{r['val_acc']:.3f}" if r["val_acc"] is not None else "  N/A"
        fname = os.path.basename(r["path"]) if r["path"] else "—"
        print(f"{r['model']:<14} {r['n_samples']:>8} {tacc:>10} {vacc:>10}  {fname}")
    print("=" * 65)


if __name__ == "__main__":
    main()
