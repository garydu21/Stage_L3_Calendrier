import re

import pandas as pd

def creer_dataframe(evenements):
    df = pd.DataFrame(evenements)
    return df

def heures_par_prof(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    return df.groupby("prof")["duree_h"].sum().sort_values(ascending=False)

def heures_par_filiere(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    return df.groupby("filiere")["duree_h"].sum().sort_values(ascending=False)

def heures_par_type(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    return df.groupby("type_seance")["duree_h"].sum().sort_values(ascending=False)

def stats_par_prof(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    return df.groupby("prof").agg(
        nb_seances   = ("duree_h", "count"),
        heures_total = ("duree_h", "sum")
    ).sort_values("heures_total", ascending=False)

def stats_par_filiere(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    return df.groupby("filiere").agg(
        nb_seances   = ("duree_h", "count"),
        heures_total = ("duree_h", "sum")
    ).sort_values("heures_total", ascending=False)

def heures_par_mois(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    df = df.copy()
    df["mois"] = pd.to_datetime(df["date"]).dt.month

    result = df.groupby("mois")["duree_h"].sum().sort_index()

    noms_mois = {1:"Janvier", 2:"Février", 3:"Mars", 4:"Avril",
                 5:"Mai", 6:"Juin", 7:"Juillet", 8:"Août",
                 9:"Septembre", 10:"Octobre", 11:"Novembre", 12:"Décembre"}
    result.index = result.index.map(noms_mois)

    return result

def heures_par_semaine(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    df = df.copy()
    df["semaine"] = pd.to_datetime(df["date"]).dt.isocalendar().week.astype(int)

    return df.groupby("semaine")["duree_h"].sum().sort_index()

def croisement_prof_filiere(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    return df.groupby(["prof", "filiere"])["duree_h"].sum().unstack(fill_value=0)

def repartition_type_par_filiere(df, cours_seulement=True):
    if cours_seulement:
        df = df[df["is_cours"] == True]

    return df.groupby(["filiere", "type_seance"])["duree_h"].sum().unstack(fill_value=0)

def resume_global(df):
    cours = df[df["is_cours"] == True]

    return pd.DataFrame([{
        "Total séances":          len(df),
        "Total cours":            len(cours),
        "Total réservations":     len(df) - len(cours),
        "Total heures cours":     cours["duree_h"].sum(),
        "Nombre de profs":        cours["prof"].nunique(),
        "Nombre de filières":     cours["filiere"].nunique(),
        "Période du":             str(df["date"].min()),
        "Période au":             str(df["date"].max()),
    }]).T.rename(columns={0: "Valeur"}).astype(str)

def est_fichier_filiere(df):
    return df[df["is_cours"] == True]["filiere"].nunique() <= 3

def heures_etudiant_modele(df):
    cours = df[df["is_cours"] == True]

    # Trouve le premier groupe TD disponible
    groupe_td = "01"
    for s in cours[cours["type_seance"] == "TD"]["summary_raw"]:
        m = re.search(r"Groupe[-\s](\d+)", s, re.IGNORECASE)
        if m:
            groupe_td = m.group(1).zfill(2)  # "1" → "01"
            break

    # Trouve le premier groupe TP disponible
    groupe_tp = "A"
    for s in cours[cours["type_seance"] == "TP"]["summary_raw"]:
        m = re.search(r"Groupe[-\s]([A-Z])", s, re.IGNORECASE)
        if m:
            groupe_tp = m.group(1).upper()
            break

    # Trouve le premier groupe anglais disponible
    groupe_anglais = None
    for s in cours[cours["filiere"] == "Anglais"]["summary_raw"]:
        m = re.search(r"Groupe-(\d+)", s, re.IGNORECASE)
        if m:
            groupe_anglais = m.group(1)
            break

    def est_pour_etudiant(row):
        summary = row["summary_raw"].upper()
        type_s  = row["type_seance"]

        if type_s == "CM":
            return True
        elif type_s == "TD":
            if "LV" in summary and groupe_anglais:
                return f"GROUPE-{groupe_anglais}" in summary.replace(" ", "-")
            return f"GROUPE-{groupe_td}" in summary.replace(" ", "-")
        elif type_s == "TP":
            return f"GROUPE-{groupe_tp}" in summary.replace(" ", "-")
        return False

    df_etudiant = cours.copy()
    df_etudiant = df_etudiant[df_etudiant.apply(est_pour_etudiant, axis=1)]

    result = df_etudiant.groupby("matiere").agg(
        types_seance = ("type_seance", lambda x: ", ".join(sorted(x.unique()))),
        nb_seances   = ("duree_h", "count"),
        heures_total = ("duree_h", "sum")
    ).sort_values("heures_total", ascending=False)

    result.loc["TOTAL"] = ["", result["nb_seances"].sum(), result["heures_total"].sum()]

    return result, groupe_td, groupe_tp

