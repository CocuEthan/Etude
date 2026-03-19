"""Agent spécialisé analyse Court Terme (technique)."""
from __future__ import annotations
import json
from agents.base import GeminiAgentBase
from data.market import get_court_terme_data


class AgentCourtTerme(GeminiAgentBase):

    def analyser(self, donnees_portefeuille: list) -> str:
        positions = [p for p in donnees_portefeuille if p.get("role") == "Court terme"]
        if not positions:
            positions = donnees_portefeuille

        if not positions:
            return "Aucune position dans le portefeuille."

        sections = []
        for pos in positions:
            sym = pos.get("symbole", "?")
            data = get_court_terme_data(sym)
            sections.append(f"=== {sym} — {data.get('nom', sym)} ===\n{json.dumps(data, indent=2, ensure_ascii=False)}")

        donnees_str = "\n\n".join(sections)

        prompt = f"""Tu es un trader technique spécialisé sur Euronext Paris, avec une approche court terme (1-4 semaines).
Voici les données techniques du portefeuille à analyser :

{donnees_str}

Pour CHAQUE action, fournis :
1. Signal RSI : suracheté (>70) / neutre / survendu (<30) + interprétation
2. Tendance momentum 5 jours : haussier / baissier / neutre
3. Anomalie de volume : volume anormal (ratio > 1.5 ou < 0.5) — signal ?
4. Position dans le range 52 semaines : opportunité ou résistance ?
5. Recommandation : TENIR / ALLÉGER / RENFORCER / PRENDRE PROFITS / COUPER
   - Niveaux de support et résistance estimés

Termine par un RÉSUMÉ DE MARCHÉ HEBDOMADAIRE :
- Biais général du portefeuille CT (défensif / neutre / offensif)
- Actions à surveiller en priorité cette semaine
- Alertes de risque éventuelles

Réponds en français, de façon concise et opérationnelle.
"""
        return self._envoyer_prompt(prompt)
