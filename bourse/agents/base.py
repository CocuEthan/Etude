"""Base class for all Gemini AI agents."""
from __future__ import annotations

import config


class GeminiAgentBase:
    MODEL_NAME = "gemini-1.5-flash"
    TEMPERATURE = 0.3

    def __init__(self):
        self._model = None

    def _get_model(self):
        """Lazy init — reads API key at call time so it can be set from UI."""
        if self._model is not None:
            return self._model

        key = config.GEMINI_API_KEY
        if not key:
            raise ValueError(
                "Clé API Gemini non configurée.\n"
                "Allez dans Paramètres → Clé API Gemini pour la saisir."
            )

        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            self._model = genai.GenerativeModel(
                self.MODEL_NAME,
                generation_config={"temperature": self.TEMPERATURE},
            )
        except ImportError:
            raise ValueError(
                "Le module google-generativeai n'est pas installé.\n"
                "Exécutez : pip install google-generativeai"
            )
        return self._model

    def _envoyer_prompt(self, prompt: str) -> str:
        try:
            model = self._get_model()
            response = model.generate_content(prompt)
            return response.text
        except ValueError as e:
            return f"[CONFIGURATION] {e}"
        except Exception as e:
            return f"[ERREUR API] {e}"

    def analyser(self, donnees_portefeuille: list) -> str:
        raise NotImplementedError
