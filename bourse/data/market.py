"""All yfinance and Yahoo Finance search calls."""
from __future__ import annotations

import requests
import yfinance as yf
from datetime import datetime
import config


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
def rechercher_ticker_yahoo(query: str, prefer_france: bool = True):
    """Return (symbol, name) from Yahoo Finance search, or (None, None)."""
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": query, "quotesCount": 5, "newsCount": 0}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        quotes = data.get("quotes", [])
        if not quotes:
            return None, None
        if prefer_france:
            for q in quotes:
                if q.get("symbol", "").endswith(".PA"):
                    return q.get("symbol"), q.get("shortname", query)
        return quotes[0].get("symbol"), quotes[0].get("shortname", query)
    except Exception:
        return None, None


# ---------------------------------------------------------------------------
# Price & dividends
# ---------------------------------------------------------------------------
def get_current_price(symbole: str) -> float:
    try:
        inf = yf.Ticker(symbole).info
        return float(inf.get("currentPrice", 0) or 0)
    except Exception:
        return 0.0


def calculer_dividendes_cumules(symbole: str, date_achat_str: str, qte: int) -> float:
    try:
        ticker = yf.Ticker(symbole)
        divs = ticker.dividends
        if divs.empty:
            return 0.0
        divs.index = divs.index.tz_localize(None)
        date_achat = datetime.strptime(date_achat_str, "%Y-%m-%d")
        return round(divs[divs.index >= date_achat].sum() * qte, 2)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Full info
# ---------------------------------------------------------------------------
def get_info_complet(symbole: str) -> dict:
    try:
        return yf.Ticker(symbole).info or {}
    except Exception:
        return {}


def get_esg_score(symbole: str) -> str:
    try:
        tkr = yf.Ticker(symbole)
        sus = tkr.sustainability
        if sus is not None:
            return str(sus.loc["totalEsg", "esgScores"])
    except Exception:
        pass
    return "N/A"


# ---------------------------------------------------------------------------
# Market scanner
# ---------------------------------------------------------------------------
def scanner_marche_item(sym: str) -> dict | None:
    try:
        inf = yf.Ticker(sym).info
        nom = inf.get("shortName", sym)
        sec = inf.get("sector", "Autre")
        px = inf.get("currentPrice", 0) or 0
        tgt = inf.get("targetMeanPrice", 0) or 0
        rate = inf.get("dividendRate", 0) or 0
        pot = ((tgt - px) / px) * 100 if tgt and px else 0
        yld = (rate / px) * 100 if rate and px else 0
        reco_key = inf.get("recommendationKey", "none")
        txt_reco = config.get_reco_text(reco_key)

        txt_esg = "N/A"
        try:
            tkr = yf.Ticker(sym)
            if tkr.sustainability is not None:
                sc = tkr.sustainability.loc["totalEsg", "esgScores"]
                txt_esg = config.get_esg_text(sc)
        except Exception:
            pass

        return {
            "Symbole": sym,
            "Nom": nom,
            "Secteur": sec,
            "Prix": round(px, 2),
            "Obj_3M": round(tgt, 2) if tgt else "-",
            "Potentiel": round(pot, 2),
            "Rend.": round(yld, 2),
            "Avis": txt_reco,
            "ESG": txt_esg,
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# AI agent data collectors
# ---------------------------------------------------------------------------
def get_dividend_data(symbole: str) -> dict:
    """Collect dividend-focused metrics for AgentDividendes."""
    try:
        inf = yf.Ticker(symbole).info
        px = inf.get("currentPrice", 0) or 0
        rate = inf.get("dividendRate", 0) or 0
        yld = (rate / px) * 100 if rate and px else 0
        payout = inf.get("payoutRatio", None)

        # 5-year dividend history
        history = []
        try:
            divs = yf.Ticker(symbole).dividends
            if not divs.empty:
                divs.index = divs.index.tz_localize(None)
                cutoff = datetime(datetime.now().year - 5, 1, 1)
                recent = divs[divs.index >= cutoff]
                # Group by year
                by_year = recent.groupby(recent.index.year).sum()
                history = [{"year": int(y), "total": round(float(v), 4)} for y, v in by_year.items()]
        except Exception:
            pass

        return {
            "symbole": symbole,
            "nom": inf.get("shortName", symbole),
            "prix": px,
            "rendement_pct": round(yld, 2),
            "dividende_annuel": rate,
            "payout_ratio": round(payout * 100, 1) if payout else "N/A",
            "secteur": inf.get("sector", "N/A"),
            "historique_5ans": history,
        }
    except Exception:
        return {"symbole": symbole, "erreur": "données indisponibles"}


def get_long_terme_data(symbole: str) -> dict:
    """Collect fundamental metrics for AgentLongTerme."""
    try:
        inf = yf.Ticker(symbole).info
        px = inf.get("currentPrice", 0) or 0
        tgt = inf.get("targetMeanPrice", 0) or 0
        pot = ((tgt - px) / px) * 100 if tgt and px else 0

        esg = "N/A"
        try:
            tkr = yf.Ticker(symbole)
            if tkr.sustainability is not None:
                esg = config.get_esg_text(tkr.sustainability.loc["totalEsg", "esgScores"])
        except Exception:
            pass

        return {
            "symbole": symbole,
            "nom": inf.get("shortName", symbole),
            "prix": px,
            "pe_ratio": inf.get("trailingPE", "N/A"),
            "pb_ratio": inf.get("priceToBook", "N/A"),
            "roe": round((inf.get("returnOnEquity", 0) or 0) * 100, 2),
            "marge_nette": round((inf.get("profitMargins", 0) or 0) * 100, 2),
            "objectif_analyste": tgt,
            "potentiel_pct": round(pot, 2),
            "recommandation": config.get_reco_text(inf.get("recommendationKey", "none")),
            "secteur": inf.get("sector", "N/A"),
            "esg": esg,
            "beta": inf.get("beta", "N/A"),
        }
    except Exception:
        return {"symbole": symbole, "erreur": "données indisponibles"}


def get_court_terme_data(symbole: str) -> dict:
    """Collect technical metrics for AgentCourtTerme."""
    try:
        inf = yf.Ticker(symbole).info
        px = inf.get("currentPrice", 0) or 0

        # Fetch ~3 months of daily data for RSI + momentum
        hist = yf.Ticker(symbole).history(period="3mo")

        rsi = "N/A"
        momentum_5d = "N/A"
        volume_ratio = "N/A"
        pos_52w = "N/A"

        if not hist.empty and len(hist) >= 15:
            close = hist["Close"]

            # RSI(14)
            delta = close.diff()
            gain = delta.clip(lower=0)
            loss = (-delta).clip(lower=0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss.replace(0, float("nan"))
            rsi_series = 100 - (100 / (1 + rs))
            rsi = round(float(rsi_series.iloc[-1]), 1)

            # 5-day momentum
            if len(close) >= 6:
                mom = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100
                momentum_5d = round(float(mom), 2)

            # Volume ratio (last day vs 20-day avg)
            vol = hist["Volume"]
            if len(vol) >= 20:
                vol_ratio = vol.iloc[-1] / vol.rolling(20).mean().iloc[-1]
                volume_ratio = round(float(vol_ratio), 2)

        # 52-week high/low position
        low52 = inf.get("fiftyTwoWeekLow", 0) or 0
        high52 = inf.get("fiftyTwoWeekHigh", 0) or 0
        if high52 > low52 > 0 and px:
            pos_52w = round((px - low52) / (high52 - low52) * 100, 1)

        return {
            "symbole": symbole,
            "nom": inf.get("shortName", symbole),
            "prix": px,
            "rsi_14": rsi,
            "momentum_5j_pct": momentum_5d,
            "ratio_volume": volume_ratio,
            "position_52s_pct": pos_52w,
            "plus_haut_52s": high52,
            "plus_bas_52s": low52,
            "secteur": inf.get("sector", "N/A"),
        }
    except Exception:
        return {"symbole": symbole, "erreur": "données indisponibles"}
