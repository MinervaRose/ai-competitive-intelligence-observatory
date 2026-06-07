from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional

SYSTEM_PROMPT = """
Tu es un analyste de veille IA pour une formation professionnelle.
Tu aides des équipes métiers à transformer des signaux de veille en synthèses utiles, prudentes et exploitables.
Tu dois rester factuel, signaler les limites, éviter les affirmations non vérifiées et rappeler la nécessité d'une validation humaine.
Réponds en français professionnel.
"""

def _get_api_key(api_key: Optional[str] = None) -> Optional[str]:
    if api_key and api_key.strip():
        return api_key.strip()
    return os.getenv("OPENAI_API_KEY")

def _extract_json(text: str) -> Dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))

def client_available(api_key: Optional[str] = None) -> bool:
    return bool(_get_api_key(api_key))

def analyser_signal_openai(signal: Dict, api_key: Optional[str] = None, model: str = "gpt-4.1-mini") -> Dict:
    key = _get_api_key(api_key)
    if not key:
        raise RuntimeError("Aucune clé API OpenAI disponible.")

    from openai import OpenAI

    client = OpenAI(api_key=key)

    prompt = f"""
Analyse le signal de veille suivant pour une équipe métier.

Signal :
{json.dumps(signal, ensure_ascii=False, indent=2)}

Retourne exclusivement un JSON valide avec les clés suivantes :
- resume_court : résumé en 2 phrases maximum
- pourquoi_c_est_important : intérêt métier en 1 à 2 phrases
- opportunite : opportunité concrète
- risque_ou_limite : risque, limite ou point de vigilance
- action_recommandee : action réaliste pour une équipe ou un décideur
- questions_de_validation : liste de 3 questions à vérifier humainement
- score_nouveaute : nombre de 1 à 5
- score_pertinence_metier : nombre de 1 à 5
- score_gouvernance : nombre de 1 à 5
- justification_score : justification courte
"""

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=prompt,
    )

    return _extract_json(response.output_text)

def generer_briefing_openai(signaux: List[Dict], api_key: Optional[str] = None, model: str = "gpt-4.1-mini") -> str:
    key = _get_api_key(api_key)
    if not key:
        raise RuntimeError("Aucune clé API OpenAI disponible.")

    from openai import OpenAI

    client = OpenAI(api_key=key)

    prompt = f"""
Tu vas produire un briefing stratégique hebdomadaire en français à partir de signaux de veille.

Objectif :
- aider une équipe métier ou dirigeante à comprendre les signaux importants
- transformer la veille en opportunités, risques et actions
- conserver un ton professionnel, prudent et exploitable
- rappeler les limites et la validation humaine

Signaux :
{json.dumps(signaux, ensure_ascii=False, indent=2)}

Structure obligatoire en Markdown :
# AI Competitive Intelligence Observatory
## Briefing stratégique hebdomadaire

### Synthèse exécutive
3 à 5 phrases.

### Les 5 signaux à retenir
Pour chaque signal :
- titre
- pourquoi c'est important
- opportunité
- risque ou limite
- action recommandée

### Tendances émergentes
3 à 5 tendances.

### Questions à poser en comité métier
5 questions.

### Points de gouvernance et validation humaine
Liste courte, concrète.

### Sources utilisées
Liste des sources avec URL quand disponible.
"""

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=prompt,
    )
    return response.output_text
