import json
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_SETTINGS_PATH = os.path.join(_BASE_DIR, "settings.json")

# Data file: use dist/ when the exe is running, project root otherwise
if os.path.isdir(os.path.join(_BASE_DIR, "dist")):
    FICHIER_DONNEES = os.path.join(_BASE_DIR, "dist", "mon_portefeuille.json")
else:
    FICHIER_DONNEES = os.path.join(_BASE_DIR, "mon_portefeuille.json")

# ---------------------------------------------------------------------------
# Settings (read once at import time)
# ---------------------------------------------------------------------------
def _load_settings() -> dict:
    if os.path.exists(_SETTINGS_PATH):
        try:
            with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

_settings = _load_settings()

GEMINI_API_KEY: str = _settings.get("gemini_api_key", "")
DEFAULT_THEME: str = _settings.get("theme", "darkly")


def save_settings(new_values: dict) -> None:
    """Merge *new_values* into settings.json and update module-level variables."""
    global GEMINI_API_KEY, DEFAULT_THEME
    current = _load_settings()
    current.update(new_values)
    with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=4)
    if "gemini_api_key" in new_values:
        GEMINI_API_KEY = new_values["gemini_api_key"]
    if "theme" in new_values:
        DEFAULT_THEME = new_values["theme"]


# ---------------------------------------------------------------------------
# Stock roles
# ---------------------------------------------------------------------------
ROLES = ["Court terme", "Long terme", "Dividendes"]
ROLE_BADGES = {
    "Court terme": "📈 CT",
    "Long terme": "🏦 LT",
    "Dividendes": "💰 DIV",
}

# ---------------------------------------------------------------------------
# Market list (CAC 40 + SBF 120 principaux)
# ---------------------------------------------------------------------------
LISTE_MARCHE_PARIS = [
    "AC.PA", "AI.PA", "AIR.PA", "MT.PA", "ATO.PA", "CS.PA", "BNP.PA", "EN.PA", "CAP.PA", "CA.PA",
    "ACA.PA", "BN.PA", "DSY.PA", "ENGI.PA", "EL.PA", "ERF.PA", "RMS.PA", "KER.PA", "LR.PA",
    "OR.PA", "MC.PA", "ML.PA", "ORA.PA", "RI.PA", "PUB.PA", "RNO.PA", "SAF.PA", "SGO.PA",
    "SAN.PA", "SU.PA", "GLE.PA", "STLAM.PA", "STM.PA", "TEP.PA", "HO.PA", "TTE.PA", "URW.PA",
    "VIE.PA", "DG.PA", "VIV.PA", "WLN.PA", "TFI.PA", "FDR.PA", "FR.PA", "NK.PA", "DIM.PA",
    "RUI.PA", "SK.PA", "SW.PA", "VLA.PA", "VIRP.PA",
]

# ---------------------------------------------------------------------------
# Helpers (ESG + analyst recommendation)
# ---------------------------------------------------------------------------
def get_esg_text(score) -> str:
    if score == "N/A" or score is None:
        return "N/A"
    try:
        s = float(score)
        if s < 10:
            return f"{s} - Négligeable"
        elif s < 20:
            return f"{s} - Faible"
        elif s < 30:
            return f"{s} - Moyen"
        elif s < 40:
            return f"{s} - Élevé"
        else:
            return f"{s} - Sévère"
    except Exception:
        return str(score)


def get_reco_text(key) -> str:
    mapping = {
        "strong_buy": "ACHETER FORT",
        "buy": "ACHETER",
        "hold": "CONSERVER",
        "underperform": "ALLÉGER",
        "sell": "VENDRE",
        "none": "-",
    }
    return mapping.get(str(key).lower(), str(key).upper())
