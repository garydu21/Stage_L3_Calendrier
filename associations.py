import json
import os

FICHIER_JSON = "associations.json"
DEPARTEMENTS = ["STS", "ALL", "SHS", "DEG", "STAPS", "ISIS", "DE-DU", "Autre"]

def charger_associations():
    if os.path.exists(FICHIER_JSON):
        with open(FICHIER_JSON, "r") as f:
            return json.load(f)
    return {}

def sauvegarder_associations(associations):
    with open(FICHIER_JSON, "w") as f:
        json.dump(associations, f, indent=2)