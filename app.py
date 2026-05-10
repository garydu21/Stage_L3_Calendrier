import streamlit as st
from render_console import *
from stats import *
from export import *
import os
import io
from associations import charger_associations, sauvegarder_associations, DEPARTEMENTS

os.makedirs("data", exist_ok=True)

st.title("Analyse des Calendriers - ADE")

fichiers_data = [f for f in os.listdir("data") if f.endswith(".ics")]

choix = st.radio("Source du fichier", ["Importer un fichier", "Choisir dans data/"])

if choix == "Importer un fichier":
    fichier = st.file_uploader("Importer un fichier .ics", type="ics")
    if fichier is None:
        st.info("Importe un fichier .ics pour commencer")
        st.stop()

    chemin_save = os.path.join("data", fichier.name)
    if not os.path.exists(chemin_save):
        with open(chemin_save, "wb") as f:
            f.write(fichier.getvalue())
        st.success(f"Fichier sauvegardé dans data/")
    else:
        st.info(f"Fichier déjà présent dans data/")
else:
    if not fichiers_data:
        st.warning("Aucun fichier dans le dossier data/")
        st.stop()
    nom = st.selectbox("Choisir un fichier", fichiers_data)
    fichier = os.path.join("data", nom)

evenements = init(fichier)
df = creer_dataframe(evenements)
fichier_filiere = est_fichier_filiere(df)

with st.sidebar:
    st.header("📥 Export Excel")
    buffer = io.BytesIO()
    exporter_excel(df, buffer)
    buffer.seek(0)
    nom_export = os.path.splitext(os.path.basename(fichier if isinstance(fichier, str) else fichier.name))[0] + "_stats.xlsx"
    st.download_button(
        label="Télécharger l'Excel",
        data=buffer,
        file_name=nom_export,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.divider()
    st.header("👁️ Affichage")

    show_donnees       = st.checkbox("Données brutes",             value=False)
    show_resume        = st.checkbox("Résumé global",              value=False)
    if fichier_filiere:
        show_etudiant  = st.checkbox("Étudiant modèle",            value=False)
    show_stats_prof    = st.checkbox("Stats par prof",             value=False)
    show_stats_filiere = st.checkbox("Stats par filière",          value=False)
    if not fichier_filiere:
        show_assoc     = st.checkbox("Associations départements",  value=False)
        show_depart    = st.checkbox("Stats par département",      value=False)
    show_type          = st.checkbox("Par type de séance",         value=False)
    show_mois          = st.checkbox("Par mois",                   value=False)
    show_semaine       = st.checkbox("Par semaine",                value=False)
    show_croisement    = st.checkbox("Croisement prof × filière",  value=False)
    show_repartition   = st.checkbox("Répartition CM/TD/TP",       value=False)
    show_graphiques    = st.checkbox("Graphiques",                 value=False)

# ── Contenu principal ─────────────────────────────────────────
st.success(f"{len(df)} événements chargés")

if show_donnees:
    cols_affichees = ["date", "heure_debut", "heure_fin", "duree_h",
                      "salle", "matiere", "prof", "filiere", "type_seance", "is_cours"]
    st.dataframe(df[cols_affichees])

if show_resume:
    st.header("📋 Résumé global")
    st.dataframe(resume_global(df))

if fichier_filiere and show_etudiant:
    result, groupe_td, groupe_tp = heures_etudiant_modele(df)
    st.header(f"🎓 Étudiant modèle (Groupe-{groupe_td} TD / Groupe-{groupe_tp} TP)")
    st.dataframe(result)

if show_stats_prof:
    st.header("📊 Stats par prof")
    st.dataframe(stats_par_prof(df))

if show_stats_filiere:
    st.header("🎓 Stats par filière")
    st.dataframe(stats_par_filiere(df))

if not fichier_filiere:
    if show_assoc:
        st.header("🏫 Association filières → départements")
        filieres = get_filieres_uniques(df)
        associations = charger_associations()

        with st.form("form_departements"):
            for filiere in filieres:
                val_actuelle = associations.get(filiere, DEPARTEMENTS[0])
                associations[filiere] = st.selectbox(
                    f"{filiere}",
                    DEPARTEMENTS,
                    index=DEPARTEMENTS.index(val_actuelle) if val_actuelle in DEPARTEMENTS else 0
                )
            if st.form_submit_button("💾 Sauvegarder"):
                sauvegarder_associations(associations)
                st.success("Associations sauvegardées !")

    if show_depart:
        associations_actuelles = charger_associations()
        if associations_actuelles:
            st.header("🏫 Stats par département")
            st.subheader("Heures par département")
            st.bar_chart(heures_par_departement(df, associations_actuelles))
            st.subheader("Enseignants par département")
            st.bar_chart(enseignants_par_departement(df, associations_actuelles))

if show_type:
    st.header("📚 Par type de séance")
    st.dataframe(heures_par_type(df))

if show_mois:
    st.header("📅 Par mois")
    st.dataframe(heures_par_mois(df))

if show_semaine:
    st.header("📆 Par semaine")
    st.dataframe(heures_par_semaine(df))

if show_croisement:
    st.header("👨‍🏫 Croisement prof × filière")
    st.dataframe(croisement_prof_filiere(df))

if show_repartition:
    st.header("📋 Répartition CM/TD/TP par filière")
    st.dataframe(repartition_type_par_filiere(df))

if show_graphiques:
    st.header("📊 Graphiques")
    st.subheader("Heures par prof")
    st.bar_chart(heures_par_prof(df))
    st.subheader("Heures par filière")
    st.bar_chart(heures_par_filiere(df))
    st.subheader("Heures par mois")
    st.bar_chart(heures_par_mois(df))