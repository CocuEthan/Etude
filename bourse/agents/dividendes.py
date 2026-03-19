"""Agent spécialisé analyse Dividendes."""
from __future__ import annotations
import json
from agents.base import GeminiAgentBase
from data.market import get_dividend_data


class AgentDividendes(GeminiAgentBase):

    def analyser(self, donnees_portefeuille: list) -> str:
        positions = [p for p in donnees_portefeuille if p.get("role") == "Dividendes"]
        if not positions:
            positions = donnees_portefeuille  # fallback: all positions

        if not positions:
            return "Aucune position dans le portefeuille."

        sections = []
        for pos in positions:
            sym = pos.get("symbole", "?")
            data = get_dividend_data(sym)
            sections.append(f"=== {sym} — {data.get('nom', sym)} ===\n{json.dumps(data, indent=2, ensure_ascii=False)}")

        donnees_str = "\n\n".join(sections)

        prompt = f"""Tu es un analyste financier expert en dividendes sur le marché Euronext Paris.
Voici les données de dividendes du portefeuille à analyser :

{donnees_str}

Pour CHAQUE action, fournis :
1. Note de durabilité du dividende /10 (avec justification)
2. Risques principaux (fiscalité, payout élevé, cyclicité sectorielle…)
3. Recommandation : CONSERVER / ALLÉGER / RENFORCER (avec cible de rendement)
4. 1-2 alternatives sur Euronext Paris si le dividende est fragile

Termine par une SYNTHÈSE GLOBALE du portefeuille dividendes :
- Rendement moyen pondéré
- Diversification sectorielle
- Recommandation de rééquilibrage éventuel

Réponds en français, de façon structurée et concise.
"""
        return self._envoyer_prompt(prompt)
