import pandas as pd
from stats import *

def exporter_excel(df, chemin_sortie):
    with pd.ExcelWriter(chemin_sortie, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Données brutes")
        resume_global(df).to_excel(writer, sheet_name="Résumé")
        stats_par_prof(df).to_excel(writer, sheet_name="Par prof")
        stats_par_filiere(df).to_excel(writer, sheet_name="Par filière")
        heures_par_mois(df).to_excel(writer, sheet_name="Par mois")
        heures_par_semaine(df).to_excel(writer, sheet_name="Par semaine")
        croisement_prof_filiere(df).to_excel(writer, sheet_name="Prof x Filière")
        repartition_type_par_filiere(df).to_excel(writer, sheet_name="Type par filière")