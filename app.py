import streamlit as st
from render_console import *
from stats import *
from export import *
import os

st.title("Analyse des Calendrier - ADE")

# Fichiers déjà présents dans data/
fichiers_data = [f for f in os.listdir("data") if f.endswith(".ics")]

choix = st.radio("Source du fichier", ["Importer un fichier", "Choisir dans data/"])

if choix == "Importer un fichier":
    fichier = st.file_uploader("Importer un fichier .ics", type="ics")
    if fichier is None:
        st.info("Importe un fichier .ics pour commencer")
        st.stop()

    # Sauvegarde dans data/ si pas déjà présent
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

st.success(f"{len(df)} événements chargés")
cols_affichees = ["date", "heure_debut", "heure_fin", "duree_h",
                  "salle", "matiere", "prof", "filiere", "type_seance", "is_cours"]
st.dataframe(df[cols_affichees])

with st.sidebar:
    st.header("📥 Export Excel")
    if st.button("Exporter en Excel"):
        os.makedirs("export", exist_ok=True)
        nom_export = os.path.splitext(os.path.basename(fichier if isinstance(fichier, str) else fichier.name))[0] + "_stats.xlsx"
        chemin_export = os.path.join("export", nom_export)
        exporter_excel(df, chemin_export)
        st.success(f"Exporté : {chemin_export}")

st.header("📋 Résumé global")
st.dataframe(resume_global(df))

st.header("📊 Stats par prof")
st.dataframe(stats_par_prof(df))

st.header("🎓 Stats par filière")
st.dataframe(stats_par_filiere(df))

st.header("📚 Par type de séance")
st.dataframe(heures_par_type(df))

st.header("📅 Par mois")
st.dataframe(heures_par_mois(df))

st.header("📆 Par semaine")
st.dataframe(heures_par_semaine(df))

st.header("👨‍🏫 Croisement prof × filière")
st.dataframe(croisement_prof_filiere(df))

st.header("📋 Répartition CM/TD/TP par filière")
st.dataframe(repartition_type_par_filiere(df))

st.header("📊 Graphiques")

st.subheader("Heures par prof")
st.bar_chart(heures_par_prof(df))

st.subheader("Heures par filière")
st.bar_chart(heures_par_filiere(df))

st.subheader("Heures par mois")
st.dataframe(heures_par_mois(df))
st.bar_chart(heures_par_mois(df))