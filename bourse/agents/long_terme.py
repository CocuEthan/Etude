"""Agent spécialisé analyse Long Terme."""
from __future__ import annotations
import json
from agents.base import GeminiAgentBase
from data.market import get_long_terme_data


class AgentLongTerme(GeminiAgentBase):

    def analyser(self, donnees_portefeuille: list) -> str:
        positions = [p for p in donnees_portefeuille if p.get("role") == "Long terme"]
        if not positions:
            positions = donnees_portefeuille

        if not positions:
            return "Aucune position dans le portefeuille."

        sections = []
        for pos in positions:
            sym = pos.get("symbole", "?")
            data = get_long_terme_data(sym)
            sections.append(f"=== {sym} — {data.get('nom', sym)} ===\n{json.dumps(data, indent=2, ensure_ascii=False)}")

        donnees_str = "\n\n".join(sections)

        prompt = f"""Tu es un analyste fondamental spécialisé en investissement long terme sur Euronext Paris.
Voici les données fondamentales du portefeuille à analyser :

{donnees_str}

Pour CHAQUE action, fournis :
1. Valorisation : P/E et P/B vs secteur (sous-évalué / juste / surévalué ?)
2. Qualité : ROE, marges nettes — commentaire
3. Catalyseurs potentiels 6-12 mois (secteur, macro, company-specific)
4. Recommandation : ACHETER / CONSERVER / ALLÉGER / VENDRE
   - Niveau de conviction : Faible / Moyen / Élevé
   - Fourchette de prix cible à 12 mois

Termine par des SUGGESTIONS DE RÉÉQUILIBRAGE du portefeuille long terme :
- Surpondérations / sous-pondérations sectorielles
- Risques de concentration

Réponds en français, de façon structurée et analytique.
"""
        return self._envoyer_prompt(prompt)
