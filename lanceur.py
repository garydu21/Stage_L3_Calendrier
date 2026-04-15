from render_console import*
from stats import*
from export import*
import os

if __name__ == "__main__":
    chemin = file_path()
    evenements = init(chemin)
    df = creer_dataframe(evenements)

    print(heures_etudiant_modele(df))

    nom_sortie = os.path.splitext(os.path.basename(chemin))[0] + "_stats.xlsx"
    exporter_excel(df, nom_sortie)
