from __future__ import annotations

from typing import Dict, List
import pandas as pd

CATEGORIE_WEIGHTS = {
    "Gouvernance / conformité": 1.20,
    "Recherche appliquée": 1.05,
    "Annonce fournisseur": 1.00,
    "Modèles / outils": 0.95,
    "Signal marché": 1.10,
    "Signal interne": 1.20,
    "Cas métier": 1.25,
}

MOTS_CLES = {
    "métier": 0.45,
    "cas d’usage": 0.45,
    "workflow": 0.45,
    "workflows": 0.45,
    "automatisation": 0.40,
    "supervision": 0.40,
    "humaine": 0.35,
    "gouvernance": 0.40,
    "conformité": 0.38,
    "données personnelles": 0.38,
    "RAG": 0.35,
    "évaluation": 0.32,
    "fidélité": 0.32,
    "décision": 0.35,
    "reporting": 0.32,
    "clients": 0.30,
    "RH": 0.30,
    "marketing": 0.30,
    "support": 0.30,
    "formation": 0.35,
    "assistants": 0.30,
    "outils": 0.22,
}

def texte_ligne(row: pd.Series) -> str:
    champs = ["titre", "contenu", "contexte_metier"]
    return " ".join(str(row.get(c, "")) for c in champs if pd.notna(row.get(c, "")))

def scorer_signal(row: pd.Series) -> Dict[str, float]:
    texte = texte_ligne(row)
    texte_lower = texte.lower()

    poids_categorie = CATEGORIE_WEIGHTS.get(row.get("categorie", ""), 1.0)
    score_mots = 0.0
    for mot, poids in MOTS_CLES.items():
        if mot.lower() in texte_lower:
            score_mots += poids

    presence_source = 0.25 if str(row.get("url", "")).strip() else 0.0
    presence_contexte = 0.35 if len(str(row.get("contexte_metier", "")).strip()) > 40 else 0.0
    statut = str(row.get("statut_revue", "")).lower()
    besoin_revue = 0.20 if ("revoir" in statut or "vérifier" in statut) else 0.0

    nouveaute = min(5.0, 2.55 + score_mots * 0.75 + poids_categorie * 0.35)
    pertinence = min(5.0, 2.85 + score_mots * 0.65 + presence_contexte + poids_categorie * 0.45)
    gouvernance = min(5.0, 2.45 + presence_source + besoin_revue + sum(
        p for m, p in MOTS_CLES.items()
        if m.lower() in texte_lower and m.lower() in [
            "gouvernance", "conformité", "données personnelles",
            "supervision", "humaine", "évaluation", "fidélité", "rag"
        ]
    ) * 0.95)

    score_global = round(nouveaute * 0.25 + pertinence * 0.45 + gouvernance * 0.30, 2)

    return {
        "score_nouveaute": round(nouveaute, 2),
        "score_pertinence_metier": round(pertinence, 2),
        "score_gouvernance": round(gouvernance, 2),
        "score_global": score_global,
    }

def enrichir_signaux(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    colonnes_scores = [
        "score_nouveaute",
        "score_pertinence_metier",
        "score_gouvernance",
        "score_global",
        "priorite",
    ]
    df = df.drop(columns=[c for c in colonnes_scores if c in df.columns], errors="ignore")

    scores = df.apply(scorer_signal, axis=1, result_type="expand")
    df = pd.concat([df, scores], axis=1)

    df["priorite"] = pd.cut(
        df["score_global"],
        bins=[0, 3.25, 4.05, 5.1],
        labels=["À surveiller", "À traiter", "Prioritaire"],
        include_lowest=True,
    )
    return df.sort_values(["score_global", "date"], ascending=[False, False])

def detecter_themes(df: pd.DataFrame) -> List[Dict[str, str]]:
    if df.empty:
        return []
    corpus = " ".join(
        df[["titre", "contenu", "contexte_metier"]]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    ).lower()

    candidats = [
        ("Cas d’usage métiers de l’IA générative", ["marketing", "rh", "support", "juridique", "métier", "reporting", "clients"]),
        ("Workflows LLM et automatisation encadrée", ["workflow", "workflows", "automatisation", "outils", "assistants"]),
        ("Supervision humaine et qualité des décisions", ["supervision", "humaine", "décision", "validation", "contrôle"]),
        ("Gouvernance, données et conformité", ["gouvernance", "conformité", "données personnelles", "documentation", "transparence"]),
        ("Fiabilité des réponses et traçabilité des sources", ["rag", "source", "sources", "fidélité", "citation", "fiable"]),
    ]

    themes = []
    for theme, mots in candidats:
        hits = sum(1 for mot in mots if mot in corpus)
        if hits:
            themes.append({
                "thème": theme,
                "intensité": "Forte" if hits >= 3 else "Moyenne",
                "lecture_métier": explication_theme(theme),
            })
    return themes[:5]

def explication_theme(theme: str) -> str:
    explications = {
        "Cas d’usage métiers de l’IA générative": "Les équipes ont besoin d’exemples directement reliés à leurs tâches : RH, marketing, support, juridique, reporting ou veille.",
        "Workflows LLM et automatisation encadrée": "La valeur vient moins du prompt isolé que de processus réutilisables, documentés et reliés à des objectifs métiers.",
        "Supervision humaine et qualité des décisions": "Les sorties IA doivent rester des propositions à vérifier, contextualiser et valider par un humain responsable.",
        "Gouvernance, données et conformité": "Les usages doivent intégrer dès le départ les questions de données, de documentation, de limites et de responsabilités.",
        "Fiabilité des réponses et traçabilité des sources": "Un briefing professionnel doit pouvoir montrer d’où vient l’information et ce qui doit être vérifié.",
    }
    return explications.get(theme, "")

def generer_briefing_regles(df: pd.DataFrame) -> str:
    enrichi = enrichir_signaux(df)
    top = enrichi.head(5)
    themes = detecter_themes(enrichi)

    lignes = []
    lignes.append("# Briefing stratégique IA")
    lignes.append("")
    lignes.append("## À retenir cette semaine")
    lignes.append(
        "Les signaux analysés montrent une demande claire pour des usages IA concrets, reliés aux métiers et encadrés par une validation humaine. "
        "Les cas les plus utiles ne sont pas des démonstrations générales d’outils, mais des workflows simples : synthétiser, prioriser, préparer une décision, documenter et vérifier."
    )
    lignes.append("")
    lignes.append("## Signaux à traiter")
    for _, row in top.iterrows():
        lignes.append(f"### {row['titre']}")
        lignes.append(f"Source : {row['source']} | Catégorie : {row['categorie']} | Niveau : {row['priorite']} | Score : {row['score_global']}/5")
        lignes.append(f"- Ce que cela dit : {row['contenu']}")
        lignes.append(f"- Implication métier : {row['contexte_metier']}")
        lignes.append("- Action recommandée : transformer ce signal en cas d’usage testable ou en point de discussion avec les équipes concernées.")
        lignes.append("- Point de contrôle : vérifier la source, les limites et le niveau de risque avant diffusion ou déploiement.")
        lignes.append("")
    lignes.append("## Tendances utiles pour une équipe métier")
    for t in themes:
        lignes.append(f"- **{t['thème']}** : {t['lecture_métier']}")
    lignes.append("")
    lignes.append("## Questions pour cadrer l’usage IA")
    lignes.append("- Quel problème métier cherche-t-on réellement à résoudre ?")
    lignes.append("- Quelles sources sont fiables et lesquelles doivent être vérifiées ?")
    lignes.append("- À quel moment l’humain doit-il valider ou corriger la sortie IA ?")
    lignes.append("- Quelles données ne doivent pas être envoyées dans l’outil ?")
    lignes.append("- Comment documenter les limites du workflow pour éviter les usages abusifs ?")
    lignes.append("")
    lignes.append("## Notes de gouvernance")
    lignes.append("- Les synthèses IA doivent rester des brouillons analytiques.")
    lignes.append("- Les sources doivent être visibles et vérifiables.")
    lignes.append("- Les décisions sensibles doivent rester humaines.")
    lignes.append("- Les données personnelles ou confidentielles doivent être exclues ou strictement encadrées.")
    lignes.append("- Le statut de revue humaine doit être documenté.")
    return "\n".join(lignes)
