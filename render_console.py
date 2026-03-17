from icalendar import Calendar
import pandas as pd
import re

FILIERES = {
    "INF": "Informatique",
    "MAT": "Mathématiques",
    "SV":  "Sciences de la Vie",
    "PC":  "Physique-Chimie",
    "PSY": "Psychologie",
    "ALL": "Lettres / Arts",
    "LET": "Lettres",
    "L":   "Anglais",
    "ECO": "Économie",
    "AGIL": "Gestion de projet",
}

def file_path():
    lien_fichier = int(input("1) Choix fichier Salle EL107 --------- 2) Choix fichier L1\n"))

    while lien_fichier != 1 and lien_fichier != 2:
        print("Le fichier choix n'existe pas (choix possible : 1 ou 2)")
        lien_fichier = int(input("1) Choix fichier Salle EL107 --------- 2) Choix fichier L1\n"))

    if lien_fichier == 1:
        return "data/ADECal_EL107_Année complète 2425.ics"
    else:
        return "data/ADECal_L1_une_semaine.ics"

def init(file_path):
    evenements = [] # Liste de dictionnaires
    """evenements = [
    {"prof": "GLEIZES Benoît", "filiere": "INF", "duree_h": 2.0, "date": ...},
    {"prof": "MONTAUT Thierry", "filiere": "MAT", "duree_h": 2.0, "date": ...},
    ]"""

    if hasattr(file_path, "read"):  # objet fichier Streamlit
        file_path.seek(0)
        cal = Calendar.from_ical(file_path.read())
    else:  # chemin string classique
        with open(file_path, "rb") as f:
            cal = Calendar.from_ical(f.read())

    for event in cal.walk("VEVENT"):

        dt_start = event.get("DTSTART").dt  # le .dt -> retourne en objet datetime
        dt_end = event.get("DTEND").dt

        duree = dt_end - dt_start
        duree_heures = duree.total_seconds() / 3600


        lignes = str(event.get("DESCRIPTION")).strip().split("\n")
        lignes = [l.strip() for l in lignes if l.strip()]
        lignes = [l for l in lignes if not l.startswith("(Exporté")]

        matiere = lignes[0] if len(lignes) >= 1 else "Inconnue"

        prof = "Non renseigné"
        for ligne in reversed(lignes):
            if est_un_prof(ligne):
                prof = ligne
                break

        match = re.search(r"-([A-Z]+)\d", str(event.get("SUMMARY")))
        filiere = FILIERES.get(match.group(1), match.group(1)) if match else "Inconnue"

        match_type = re.match(r"^(CM|TD|TP|DS|CC)", str(event.get("SUMMARY")))
        type_seance = match_type.group(1) if match_type else "Autre"

        is_cours = bool(re.match(r"^(CM|TD|TP|DS|CC)-[A-Z]+\d", str(event.get("SUMMARY"))))

        evenements.append({
                "summary_raw": str(event.get("SUMMARY")),
                "description_raw": str(event.get("DESCRIPTION")),
                "date": dt_start.date(),
                "heure_debut": dt_start.strftime("%H:%M"),
                "heure_fin": dt_end.strftime("%H:%M"),
                "duree_h": duree_heures,
                "salle": str(event.get("LOCATION")),
                "matiere": matiere,
                "prof":    prof,
                "filiere": filiere,
                "type_seance": type_seance,
                "is_cours": is_cours,
        })

    return evenements

def est_un_prof(ligne):
    return bool(re.match(r"^[A-ZÀÂÉÈÊËÎÏÔÙÛÜÇ][a-zA-ZÀ-ÿ\s\-]+$", ligne)) and not re.search(r"\d", ligne)