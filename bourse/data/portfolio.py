import json
import os
import tempfile
from datetime import datetime
import config


def charger_donnees() -> dict:
    """Load portfolio JSON and auto-migrate entries missing 'role'."""
    path = config.FICHIER_DONNEES
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"portefeuille": [], "historique": []}
    else:
        data = {"portefeuille": [], "historique": []}

    # Migration: inject default role for old entries
    for item in data.get("portefeuille", []):
        if "role" not in item:
            item["role"] = "Court terme"

    return data


def sauvegarder_donnees(donnees: dict) -> None:
    """Atomic write to prevent data loss on crash."""
    path = config.FICHIER_DONNEES
    dir_ = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def ajouter_position(donnees: dict, item: dict) -> None:
    """Append a new position; ensures 'role' field is present."""
    if "role" not in item:
        item["role"] = "Court terme"
    donnees["portefeuille"].append(item)


def supprimer_position(donnees: dict, index: int) -> dict:
    """Remove position at *index* and return the removed item."""
    return donnees["portefeuille"].pop(index)


def modifier_position(donnees: dict, index: int, champs: dict) -> None:
    """Patch any fields in the position at *index*."""
    donnees["portefeuille"][index].update(champs)


def trouver_index(donnees: dict, symbole: str, nom: str, prix_achat: float) -> int:
    """Return first matching index or -1."""
    for i, item in enumerate(donnees["portefeuille"]):
        if (
            item.get("symbole") == symbole
            or item.get("nom", item.get("symbole")) == nom
        ) and str(item.get("prix_achat")) in str(prix_achat):
            return i
    return -1


def enregistrer_vente(donnees: dict, index: int, prix_vente: float, frais_vente: float) -> dict:
    """Move position to historique and return the historique entry."""
    act = donnees["portefeuille"][index]
    cout = (act["qte"] * act["prix_achat"]) + act["frais_achat"]
    net_v = (act["qte"] * prix_vente) - frais_vente
    g_act = net_v - cout
    g_div = act.get("dividendes_gagnes", 0.0)

    entry = {
        "date_vente": datetime.now().strftime("%Y-%m-%d"),
        "symbole": act.get("symbole", ""),
        "nom": act.get("nom", act.get("symbole", "")),
        "role": act.get("role", "Court terme"),
        "qte": act["qte"],
        "prix_achat": act["prix_achat"],
        "prix_vente": prix_vente,
        "dividendes_encaisses": g_div,
        "frais_total": round(act["frais_achat"] + frais_vente, 2),
        "gain_action_net": round(g_act, 2),
        "gain_total": round(g_act + g_div, 2),
    }
    donnees["historique"].append(entry)
    donnees["portefeuille"].pop(index)
    return entry
