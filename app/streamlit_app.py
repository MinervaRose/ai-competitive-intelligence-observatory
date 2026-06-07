from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from analyse import enrichir_signaux, detecter_themes, generer_briefing_regles
from llm_openai import analyser_signal_openai, generer_briefing_openai, client_available

st.set_page_config(
    page_title="AI Competitive Intelligence Observatory",
    page_icon=None,
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample" / "signaux_veille_demo.csv"

st.markdown(
    """
<style>
:root {
    --ink: #1f2544;
    --indigo: #27235c;
    --violet: #5f4bb6;
    --rose: #d96c9f;
    --rose-soft: #f8e7ef;
    --gold: #d6a84f;
    --paper: #fbf8f5;
    --mist: #f4f1f7;
    --line: #e6dfea;
    --muted: #6f6a7a;
}

.stApp {
    background: linear-gradient(180deg, #fbf8f5 0%, #ffffff 45%, #fbf8f5 100%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}

h1, h2, h3 {
    color: var(--ink);
    letter-spacing: -0.02em;
}

.hero {
    padding: 2rem 2.2rem;
    border-radius: 1.35rem;
    background:
        radial-gradient(circle at 8% 12%, rgba(217,108,159,0.32), transparent 28%),
        radial-gradient(circle at 92% 8%, rgba(214,168,79,0.22), transparent 24%),
        linear-gradient(135deg, #27235c 0%, #312b77 58%, #4d3f91 100%);
    color: white;
    margin-bottom: 1.2rem;
    box-shadow: 0 16px 45px rgba(39, 35, 92, 0.20);
}

.hero .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.74rem;
    font-weight: 800;
    color: rgba(255,255,255,0.72);
    margin-bottom: 0.55rem;
}

.hero h1 {
    color: white;
    font-size: 2.35rem;
    margin: 0 0 0.5rem 0;
}

.hero p {
    color: rgba(255,255,255,0.86);
    font-size: 1.03rem;
    max-width: 860px;
    line-height: 1.55;
}

.badge {
    display: inline-block;
    padding: 0.36rem 0.66rem;
    border-radius: 999px;
    margin: 0.22rem 0.22rem 0.12rem 0;
    font-size: 0.80rem;
    font-weight: 700;
    background: rgba(255,255,255,0.11);
    border: 1px solid rgba(255,255,255,0.22);
    color: rgba(255,255,255,0.92);
}

.notice {
    padding: 0.9rem 1rem;
    border: 1px solid var(--line);
    background: #ffffff;
    border-left: 4px solid var(--rose);
    border-radius: 0.8rem;
    color: var(--muted);
    margin-bottom: 1.25rem;
}

.metric-card {
    padding: 1.05rem 1.15rem;
    border-radius: 1rem;
    background: #ffffff;
    border: 1px solid var(--line);
    box-shadow: 0 8px 25px rgba(39, 35, 92, 0.06);
}
.metric-card .label {
    color: var(--muted);
    font-weight: 700;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.metric-card .value {
    color: var(--ink);
    font-size: 2.15rem;
    font-weight: 850;
    margin-top: 0.2rem;
}
.metric-card .hint {
    color: var(--muted);
    font-size: 0.85rem;
}

.signal-card {
    padding: 1.1rem 1.2rem;
    border-radius: 1rem;
    background: #ffffff;
    border: 1px solid var(--line);
    margin-bottom: 0.85rem;
    box-shadow: 0 8px 25px rgba(39, 35, 92, 0.05);
}
.signal-title {
    color: var(--ink);
    font-size: 1.05rem;
    font-weight: 850;
}
.signal-meta {
    color: var(--muted);
    font-size: 0.86rem;
    margin: 0.25rem 0 0.7rem 0;
}
.pill {
    display: inline-block;
    padding: 0.22rem 0.54rem;
    border-radius: 999px;
    background: var(--mist);
    color: var(--indigo);
    font-weight: 800;
    font-size: 0.76rem;
    margin-right: 0.45rem;
    margin-bottom: 0.3rem;
}
.pill-rose {
    background: var(--rose-soft);
    color: #9b315f;
}
.pill-gold {
    background: #fff4d7;
    color: #8a641e;
}
.pill-green {
    background: #e9f7ef;
    color: #256c45;
}
.scorebar {
    height: 0.52rem;
    background: #eee8f1;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 0.7rem;
}
.scorebar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--rose), var(--violet));
    border-radius: 999px;
}

.panel {
    padding: 1.15rem 1.25rem;
    border-radius: 1rem;
    background: #ffffff;
    border: 1px solid var(--line);
    box-shadow: 0 8px 25px rgba(39, 35, 92, 0.05);
}
.panel-soft {
    padding: 1.15rem 1.25rem;
    border-radius: 1rem;
    background: linear-gradient(135deg, #ffffff 0%, #f8e7ef 100%);
    border: 1px solid var(--line);
}
.section-intro {
    color: var(--muted);
    margin-top: -0.35rem;
    margin-bottom: 1rem;
    font-size: 0.98rem;
}
.small-muted {
    color: var(--muted);
    font-size: 0.90rem;
}
.workflow-step {
    padding: 0.8rem 0.9rem;
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 0.9rem;
    margin-bottom: 0.6rem;
}
.workflow-step strong {
    color: var(--indigo);
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--line);
    padding: 0.85rem 1rem;
    border-radius: 1rem;
    box-shadow: 0 8px 25px rgba(39, 35, 92, 0.04);
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 0.8rem;
    overflow: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

@st.cache_data
def charger_donnees_demo() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

def charger_donnees(fichier):
    if fichier is not None:
        return pd.read_csv(fichier)
    return charger_donnees_demo()

def get_secret_key():
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        return ""

def render_metric(label: str, value: str, hint: str = ""):
    st.markdown(
        f"""
<div class="metric-card">
    <div class="label">{label}</div>
    <div class="value">{value}</div>
    <div class="hint">{hint}</div>
</div>
""",
        unsafe_allow_html=True,
    )

def niveau_badge(score: float) -> tuple[str, str]:
    if score >= 4.05:
        return "Prioritaire", "pill-rose"
    if score >= 3.25:
        return "À traiter", "pill-gold"
    return "À surveiller", ""

def statut_badge(statut: str) -> str:
    statut = str(statut)
    if "Validé" in statut:
        klass = "pill-green"
    elif "vérifier" in statut.lower():
        klass = "pill-rose"
    else:
        klass = "pill-gold"
    return f'<span class="pill {klass}">{statut}</span>'

def render_signal_card(row):
    niveau, klass = niveau_badge(float(row["score_global"]))
    pct = max(0, min(100, float(row["score_global"]) / 5 * 100))
    st.markdown(
        f"""
<div class="signal-card">
    <div class="signal-title">{row['titre']}</div>
    <div class="signal-meta">{row['date']} · {row['source']} · {row['categorie']}</div>
    <span class="pill {klass}">{niveau} · {row['score_global']}/5</span>
    {statut_badge(row['statut_revue'])}
    <div class="scorebar"><div class="scorebar-fill" style="width:{pct}%"></div></div>
    <p style="margin-top:0.85rem;">{row['contenu']}</p>
    <p class="small-muted"><strong>Utilité métier :</strong> {row['contexte_metier']}</p>
</div>
""",
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.header("Configuration")
    fichier = st.file_uploader("Importer un CSV de signaux", type=["csv"])

    st.subheader("Analyse LLM")
    mode_llm = st.toggle("Activer OpenAI", value=False)
    modele = st.text_input("Modèle", value="gpt-4.1-mini")
    cle_saisie = st.text_input(
        "Clé API",
        value="",
        type="password",
        help="Optionnel si OPENAI_API_KEY est déjà définie dans l'environnement ou dans .streamlit/secrets.toml.",
    )
    cle_api = cle_saisie or get_secret_key()

    if mode_llm:
        if client_available(cle_api):
            st.success("OpenAI activé")
        else:
            st.warning("Ajoutez une clé API.")

    st.subheader("Filtres")
    score_min = st.slider("Score minimum", 0.0, 5.0, 0.0, 0.1)

df = charger_donnees(fichier)
df_enrichi = enrichir_signaux(df)

categories = ["Toutes"] + sorted(df_enrichi["categorie"].dropna().unique().tolist())
categorie = st.sidebar.selectbox("Catégorie", categories)

filtre = df_enrichi.copy()
if categorie != "Toutes":
    filtre = filtre[filtre["categorie"] == categorie]
filtre = filtre[filtre["score_global"] >= score_min]

st.markdown(
    """
<div class="hero">
    <div class="eyebrow">Démonstrateur IA pour équipes métiers</div>
    <h1>AI Competitive Intelligence Observatory</h1>
    <p>Transformer une veille dispersée en briefing utile, vérifiable et actionnable grâce à l’IA générative, avec une étape explicite de validation humaine.</p>
    <span class="badge">IA générative appliquée aux métiers</span>
    <span class="badge">Workflows LLM</span>
    <span class="badge">Briefing stratégique</span>
    <span class="badge">Sources vérifiables</span>
    <span class="badge">Validation humaine</span>
    <span class="badge">Gouvernance opérationnelle</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="notice">
Les signaux affichés sont des données de démonstration destinées à illustrer le workflow. 
L’application peut être adaptée à des sources réelles, à des fichiers internes ou à un cas client sectoriel.
</div>
""",
    unsafe_allow_html=True,
)

tab_dashboard, tab_llm, tab_briefing, tab_gouvernance, tab_formation = st.tabs([
    "Vue d'ensemble",
    "Analyse métier par LLM",
    "Briefing",
    "Gouvernance",
    "Usage formation",
])

with tab_dashboard:
    st.subheader("Vue d'ensemble")
    st.markdown('<div class="section-intro">Ce tableau de bord montre ce qui mérite l’attention d’une équipe métier et pourquoi.</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Signaux analysés", str(len(filtre)), "données de démonstration")
    with col2:
        render_metric("Score moyen", f"{round(filtre['score_global'].mean(), 2) if len(filtre) else 0}", "pertinence globale")
    with col3:
        render_metric("À traiter", str(int((filtre["score_global"] >= 3.25).sum()) if len(filtre) else 0), "signaux actionnables")
    with col4:
        render_metric("Sources", str(filtre["source"].nunique() if len(filtre) else 0), "traçabilité")

    st.markdown("### Lecture métier")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("#### Répartition par type de signal")
        cat_counts = filtre["categorie"].value_counts().reset_index()
        cat_counts.columns = ["Catégorie", "Nombre"]
        for _, row in cat_counts.iterrows():
            st.markdown(f"**{row['Catégorie']}**")
            st.progress(int(row["Nombre"]) / max(1, cat_counts["Nombre"].max()))
            st.caption(f"{row['Nombre']} signal(s)")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("#### Scores moyens")
        score_items = [
            ("Pertinence métier", filtre["score_pertinence_metier"].mean() if len(filtre) else 0),
            ("Gouvernance", filtre["score_gouvernance"].mean() if len(filtre) else 0),
            ("Nouveauté", filtre["score_nouveaute"].mean() if len(filtre) else 0),
        ]
        for label, value in score_items:
            st.markdown(f"**{label}**")
            st.progress(float(value) / 5)
            st.caption(f"{value:.2f} / 5")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Signaux à traiter en priorité")
    for _, row in filtre.head(4).iterrows():
        render_signal_card(row)

    with st.expander("Voir la table complète des signaux"):
        colonnes = [
            "date", "source", "categorie", "titre", "score_global", "priorite", "statut_revue"
        ]
        st.dataframe(
            filtre[colonnes],
            use_container_width=True,
            hide_index=True,
            column_config={
                "score_global": st.column_config.ProgressColumn(
                    "score_global",
                    min_value=0,
                    max_value=5,
                    format="%.2f",
                ),
            }
        )

    st.markdown("### Tendances détectées")
    themes = pd.DataFrame(detecter_themes(filtre))
    if not themes.empty:
        st.dataframe(themes, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune tendance détectée avec les filtres actuels.")

with tab_llm:
    st.subheader("Analyse métier par LLM")
    st.markdown('<div class="section-intro">Le modèle transforme un signal brut en lecture métier : résumé, opportunité, risque, action et questions de validation.</div>', unsafe_allow_html=True)

    if filtre.empty:
        st.info("Aucun signal à analyser avec les filtres actuels.")
    else:
        options = {f"{row['date']} · {row['titre']}": i for i, row in filtre.reset_index(drop=True).iterrows()}
        choix = st.selectbox("Choisir un signal", list(options.keys()))
        signal = filtre.reset_index(drop=True).iloc[options[choix]].to_dict()

        col_signal, col_action = st.columns([1, 1])
        with col_signal:
            st.markdown("#### Signal sélectionné")
            st.json(signal, expanded=False)

        with col_action:
            st.markdown("#### Génération de l’analyse")
            st.write("L’analyse produit une synthèse exploitable en atelier métier ou en comité de pilotage.")
            if st.button("Analyser ce signal", disabled=not mode_llm or not client_available(cle_api)):
                with st.spinner("Analyse en cours..."):
                    try:
                        resultat = analyser_signal_openai(signal, api_key=cle_api, model=modele)
                        st.session_state["analyse_signal"] = resultat
                        st.success("Analyse générée")
                    except Exception as exc:
                        st.error(f"Erreur pendant l'analyse : {exc}")

            if not mode_llm:
                st.info("Activez OpenAI dans la barre latérale pour utiliser cette fonctionnalité.")

        if "analyse_signal" in st.session_state:
            res = st.session_state["analyse_signal"]
            st.markdown("#### Résultat structuré")
            c1, c2, c3 = st.columns(3)
            c1.metric("Nouveauté", res.get("score_nouveaute", "—"))
            c2.metric("Pertinence métier", res.get("score_pertinence_metier", "—"))
            c3.metric("Gouvernance", res.get("score_gouvernance", "—"))

            st.markdown(
                f"""
<div class="panel-soft">
<strong>Résumé</strong><br>{res.get("resume_court", "")}<br><br>
<strong>Pourquoi c'est important</strong><br>{res.get("pourquoi_c_est_important", "")}<br><br>
<strong>Opportunité</strong><br>{res.get("opportunite", "")}<br><br>
<strong>Risque ou limite</strong><br>{res.get("risque_ou_limite", "")}<br><br>
<strong>Action recommandée</strong><br>{res.get("action_recommandee", "")}
</div>
""",
                unsafe_allow_html=True,
            )

            questions = res.get("questions_de_validation", [])
            if questions:
                st.markdown("#### Questions de validation humaine")
                for q in questions:
                    st.checkbox(q)

            with st.expander("Voir le JSON complet"):
                st.json(res)

with tab_briefing:
    st.subheader("Briefing stratégique")
    st.markdown('<div class="section-intro">Un livrable court, lisible et réutilisable pour une équipe métier.</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Générer un briefing de démonstration"):
            st.session_state["briefing"] = generer_briefing_regles(filtre if len(filtre) else df_enrichi)
            st.session_state["briefing_mode"] = "Démonstration locale"

    with col_b:
        if st.button("Générer un briefing avec LLM", disabled=not mode_llm or not client_available(cle_api)):
            with st.spinner("Génération du briefing..."):
                try:
                    signaux = (filtre if len(filtre) else df_enrichi).head(10).to_dict(orient="records")
                    st.session_state["briefing"] = generer_briefing_openai(signaux, api_key=cle_api, model=modele)
                    st.session_state["briefing_mode"] = "LLM"
                except Exception as exc:
                    st.error(f"Erreur pendant la génération : {exc}")

    briefing = st.session_state.get("briefing", generer_briefing_regles(filtre if len(filtre) else df_enrichi))
    mode = st.session_state.get("briefing_mode", "Démonstration locale")
    st.caption(f"Mode : {mode}")

    st.download_button(
        "Télécharger le briefing au format Markdown",
        data=briefing,
        file_name="briefing_strategique_ia.md",
        mime="text/markdown",
    )

    st.markdown("---")
    st.markdown(briefing)

with tab_gouvernance:
    st.subheader("Gouvernance du workflow")
    st.markdown('<div class="section-intro">Cette couche montre que le livrable IA reste un brouillon à valider, pas une décision automatique.</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Checklist avant diffusion")
        checks = [
            "Les sources sont visibles et consultables.",
            "Les résumés restent fidèles aux sources.",
            "Les risques et opportunités sont formulés avec prudence.",
            "Les actions recommandées sont réalistes pour l'organisation.",
            "Aucune donnée personnelle, sensible ou confidentielle n'est exposée inutilement.",
            "Le briefing est validé pour diffusion interne.",
        ]
        for check in checks:
            st.checkbox(check)

    with right:
        st.markdown("#### Rôle du réviseur humain")
        st.markdown(
            """
<div class="panel-soft">
Le réviseur humain vérifie les sources, corrige les surinterprétations,
recontextualise les signaux et décide si le briefing peut être partagé.
<br><br>
L’objectif est de rendre le workflow utilisable dans un cadre professionnel :
traçabilité, prudence, responsabilité et amélioration continue.
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("#### Registre léger de gouvernance")
    registre = pd.DataFrame({
        "Élément": [
            "Finalité",
            "Utilisateur cible",
            "Données utilisées",
            "Sortie produite",
            "Rôle de l'humain",
            "Limite principale",
        ],
        "Réponse": [
            "Transformer des signaux de veille en briefing stratégique.",
            "Équipe métier, responsable, consultant ou formateur.",
            "Sources de veille, notes internes non sensibles, articles, annonces publiques.",
            "Synthèse, tendances, risques, opportunités, actions recommandées.",
            "Vérifier, corriger, contextualiser et approuver avant diffusion.",
            "L'IA peut résumer de façon incomplète ou surinterpréter un signal.",
        ],
    })
    st.dataframe(registre, use_container_width=True, hide_index=True)

with tab_formation:
    st.subheader("Usage formation")
    st.markdown(
        """
<div class="panel-soft">
<strong>Objectif atelier</strong><br>
Montrer comment passer d'une veille dispersée à un briefing utile, gouverné et validable.
<br><br>
Ce cas pratique permet de former des professionnels à l’IA générative appliquée aux métiers,
sans rester au niveau d’une démonstration abstraite d’outil.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Déroulé possible")
    etapes = [
        ("Définir le besoin", "Formuler une question métier utile."),
        ("Structurer les sources", "Passer d’informations dispersées à un format exploitable."),
        ("Analyser avec un LLM", "Produire résumé, opportunité, risque et questions de validation."),
        ("Transformer en actions", "Relier la synthèse IA à des décisions concrètes."),
        ("Valider humainement", "Détecter erreurs, surinterprétations et limites."),
        ("Documenter la gouvernance", "Rendre le workflow responsable, explicable et réutilisable."),
    ]
    for titre, objectif in etapes:
        st.markdown(f'<div class="workflow-step"><strong>{titre}</strong><br>{objectif}</div>', unsafe_allow_html=True)

    st.markdown("#### Compétences travaillées")
    st.markdown(
        """
- IA générative appliquée aux métiers
- Workflows LLM
- Synthèse stratégique
- Prompting orienté sortie structurée
- Traçabilité des sources
- Validation humaine
- Gouvernance opérationnelle de l’IA
"""
    )
