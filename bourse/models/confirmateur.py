"""Confirmateur : agrège signal ML et opinion LLM → verdict final."""
from __future__ import annotations

_SIGNAL_TO_INT = {"VENDRE": 0, "CONSERVER": 1, "ACHETER": 2}


def parse_llm_signal(text: str, symbole: str | None = None) -> str:
    """Extracts BUY/HOLD/SELL signal from an LLM response.

    If *symbole* is given the function first narrows its search to the
    ``=== SYM ===`` section of the text (multi-ticker responses).

    Returns one of: ``"ACHETER"``, ``"CONSERVER"``, ``"VENDRE"``,
    ``"UNKNOWN"``.
    """
    if not text:
        return "UNKNOWN"

    # Narrow to the symbol section when the response covers multiple tickers
    section = text
    if symbole:
        marker = f"=== {symbole.upper()}"
        idx = text.upper().find(marker)
        if idx != -1:
            next_idx = text.upper().find("===", idx + len(marker))
            section = text[idx:next_idx] if next_idx != -1 else text[idx:]

    upper = section.upper()

    # Ordered from most specific to most general
    keywords = [
        ("ACHETER FORT", "ACHETER"),
        ("RENFORCER", "ACHETER"),
        ("ACHETER", "ACHETER"),
        ("PRENDRE PROFITS", "VENDRE"),
        ("COUPER", "VENDRE"),
        ("ALLÉGER", "VENDRE"),
        ("ALLEGER", "VENDRE"),
        ("VENDRE", "VENDRE"),
        ("VENTE", "VENDRE"),
        ("TENIR", "CONSERVER"),
        ("CONSERVER", "CONSERVER"),
        ("NEUTRE", "CONSERVER"),
        ("HOLD", "CONSERVER"),
        ("BUY", "ACHETER"),
        ("SELL", "VENDRE"),
    ]

    for keyword, signal in keywords:
        if keyword in upper:
            return signal
    return "UNKNOWN"


class Confirmateur:
    """Agrège le signal ML et l'opinion LLM pour produire un verdict final.

    Usage::

        c = Confirmateur("court_terme")
        result = c.evaluer("MC.PA", data, llm_text)
        # result["statut"] → "CONFIRMÉ ✓" | "LLM PRIORITAIRE" | …
    """

    def __init__(self, model_type: str):
        """*model_type* : ``'court_terme'``, ``'long_terme'``, ``'dividendes'``."""
        self.model_type = model_type
        self._model = self._load_model(model_type)

    def _load_model(self, model_type: str):
        try:
            if model_type == "court_terme":
                from models.court_terme import ModelCourtTerme
                return ModelCourtTerme()
            if model_type == "long_terme":
                from models.long_terme import ModelLongTerme
                return ModelLongTerme()
            if model_type == "dividendes":
                from models.dividendes import ModelDividendes
                return ModelDividendes()
        except Exception:
            pass
        return None

    def evaluer(self, symbole: str, donnees: dict, llm_response: str) -> dict:
        """Retourne un dict avec les clés :

        - ``model_probas``    : list[float] ou None
        - ``model_signal``    : str ou None  (ACHETER/CONSERVER/VENDRE)
        - ``model_confiance`` : float ou None
        - ``llm_signal``      : str  (ACHETER/CONSERVER/VENDRE/UNKNOWN)
        - ``verdict``         : str  (signal retenu)
        - ``statut``          : str  (label UI)
        - ``modele_entraine`` : bool
        """
        llm_signal = parse_llm_signal(llm_response, symbole)

        # --- model not available ------------------------------------------
        if self._model is None or not self._model.trained:
            return {
                "model_probas": None,
                "model_signal": None,
                "model_confiance": None,
                "llm_signal": llm_signal,
                "verdict": llm_signal if llm_signal != "UNKNOWN" else "CONSERVER",
                "statut": "NON ENTRAÎNÉ",
                "modele_entraine": False,
            }

        # --- ML prediction ------------------------------------------------
        result = self._model.predict(donnees)
        if result is None:
            return {
                "model_probas": None,
                "model_signal": None,
                "model_confiance": None,
                "llm_signal": llm_signal,
                "verdict": llm_signal if llm_signal != "UNKNOWN" else "CONSERVER",
                "statut": "NON ENTRAÎNÉ",
                "modele_entraine": False,
            }

        probas, model_signal, confidence = result

        # --- LLM unreadable -----------------------------------------------
        if llm_signal == "UNKNOWN":
            return {
                "model_probas": probas,
                "model_signal": model_signal,
                "model_confiance": confidence,
                "llm_signal": llm_signal,
                "verdict": model_signal,
                "statut": "ML SEUL",
                "modele_entraine": True,
            }

        # --- Agrégation ---------------------------------------------------
        ms_int = _SIGNAL_TO_INT.get(model_signal, 1)
        ls_int = _SIGNAL_TO_INT.get(llm_signal, 1)
        diff = abs(ms_int - ls_int)

        if diff == 0:
            statut = "CONFIRMÉ ✓" if confidence >= 0.65 else "CONFIRMÉ (faible)"
            verdict = model_signal
        elif diff == 1:
            # Adjacent signals → LLM takes priority
            verdict = llm_signal
            statut = "LLM PRIORITAIRE"
        else:
            # Polar conflict (BUY vs SELL) → neutral
            verdict = "CONSERVER"
            statut = "CONFLIT ⚠"

        return {
            "model_probas": probas,
            "model_signal": model_signal,
            "model_confiance": confidence,
            "llm_signal": llm_signal,
            "verdict": verdict,
            "statut": statut,
            "modele_entraine": True,
        }
