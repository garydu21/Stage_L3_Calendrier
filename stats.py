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