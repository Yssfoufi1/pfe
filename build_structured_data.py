"""Construit data/calendrier_2025_2026.csv et data/filieres.json
a partir des pages-images du Guide de l'etudiant 2025-2026
(pages imprimees 6-7 pour les filieres, 8-9 pour le calendrier).
Les dates sont transcrites telles qu'imprimees; les anomalies sont notees dans 'remarque'.
"""
import csv
import json
from datetime import date, timedelta
from pathlib import Path

OUT_DIR = Path("data")
SRC = "guide_etudiant_2025_2026.pdf"
rows = []


def add(cycle, annee, semestre, type_, libelle, debut, fin, page, remarque=""):
    rows.append({
        "cycle": cycle, "annee": annee, "semestre": semestre, "type": type_,
        "libelle": libelle,
        "date_debut": debut.isoformat() if debut else "",
        "date_fin": fin.isoformat() if fin else "",
        "page_imprimee": page, "remarque": remarque,
    })


def weeks(cycle, annee, sem, first_num, first_monday, n, page):
    """n semaines de cours consecutives, lundi -> samedi."""
    for k in range(n):
        d = first_monday + timedelta(days=7 * k)
        add(cycle, annee, sem, "semaine_cours", f"Semaine S{first_num + k}",
            d, d + timedelta(days=5), page)


D = date
# ---------------- DUT 1ere annee (page imprimee 8) ----------------
c, a = "DUT", 1
add(c, a, "S1", "integration", "Semaine d'integration", D(2025, 9, 15), D(2025, 9, 20), 8)
weeks(c, a, "S1", 1, D(2025, 9, 22), 16, 8)
add(c, a, "S1", "saisie_notes", "Saisie des notes et predeliberations", D(2026, 1, 12), D(2026, 1, 17), 8)
add(c, a, "S1", "rattrapage", "Rattrapages S1", D(2026, 1, 19), D(2026, 1, 24), 8)
add(c, a, "S1", "vacances", "Vacances universitaires (semestre 1)", D(2026, 1, 25), D(2026, 2, 1), 8)

weeks(c, a, "S2", 17, D(2026, 2, 2), 12, 8)
add(c, a, "S2", "semaine_cours", "Semaine S29", D(2026, 4, 27), D(2026, 4, 30), 8,
    "se termine un jeudi (30 avril) comme imprime")
add(c, a, "S2", "vacances", "Vacances universitaires (Fete du travail et printemps)", D(2026, 5, 1), D(2026, 5, 10), 8)
weeks(c, a, "S2", 30, D(2026, 5, 11), 2, 8)
add(c, a, "S2", "semaine_cours", "Semaine S32", D(2026, 5, 25), D(2026, 5, 30), 8,
    "imprime: 'vendredi 30 mai 2025' (annee precedente, probable copier-coller); date de fin a confirmer")
add(c, a, "S2", "saisie_notes", "Saisie des notes et predeliberations", D(2026, 6, 1), D(2026, 6, 13), 8)
add(c, a, "S2", "rattrapage", "Rattrapages S2", D(2026, 6, 15), D(2026, 6, 20), 8,
    "imprime: 'vendredi 20 juin 2025' (annee precedente); date de fin a confirmer")
add(c, a, "S2", "deliberation", "Deliberations finales", D(2026, 6, 29), D(2026, 7, 4), 8)

# ---------------- DUT 2eme annee (page imprimee 8) ----------------
a = 2
add(c, a, "S3", "soutenance_stage_initiation", "Soutenance des stages d'initiation", D(2025, 9, 8), D(2025, 9, 13), 8)
weeks(c, a, "S3", 1, D(2025, 9, 15), 16, 8)
add(c, a, "S3", "saisie_notes", "Saisie des notes et predeliberations", D(2026, 1, 5), D(2026, 1, 14), 8)
add(c, a, "S3", "rattrapage", "Rattrapages S3", D(2026, 1, 15), D(2026, 1, 24), 8)
add(c, a, "S3", "vacances", "Vacances universitaires (semestre 1)", D(2026, 1, 25), D(2026, 2, 1), 8)

weeks(c, a, "S4", 17, D(2026, 2, 2), 7, 8)
add(c, a, "S4", "saisie_notes", "Saisie des notes et predeliberations", D(2026, 3, 23), D(2026, 3, 28), 8)
add(c, a, "S4", "rattrapage", "Rattrapage des modules M5 et M6 (2eme A)", D(2026, 3, 30), D(2026, 4, 4), 8)
add(c, a, "S4", "soutenance_pfe", "Soutenance des PFEs", D(2026, 4, 6), D(2026, 4, 11), 8)
add(c, a, "S4", "stage_technique", "Stage technique (8 semaines)", D(2026, 4, 13), D(2026, 6, 6), 8)
add(c, a, "S4", "soutenance_stage", "Soutenance des stages techniques", D(2026, 6, 8), D(2026, 6, 13), 8)
add(c, a, "S4", "deliberation", "Deliberations finales", D(2026, 6, 22), D(2026, 6, 27), 8)

# ---------------- Bachelor DBT (page imprimee 9) ----------------
c, a = "DBT", 1
weeks(c, a, "S5", 1, D(2025, 10, 13), 12, 9)
add(c, a, "S5", "semaine_cours", "Semaine S13", D(2026, 1, 5), D(2026, 1, 14), 9, "se termine un mercredi comme imprime")
add(c, a, "S5", "semaine_cours", "Semaine S14", D(2026, 1, 15), D(2026, 1, 24), 9, "commence un jeudi comme imprime")
add(c, a, "S5", "vacances", "Vacances universitaires (semestre 1)", D(2026, 1, 25), D(2026, 2, 1), 9)
add(c, a, "S5", "saisie_notes", "Saisie des notes, predeliberations et rattrapages S5", D(2026, 2, 2), D(2026, 2, 7), 9)

weeks(c, a, "S6", 15, D(2026, 2, 9), 8, 9)
add(c, a, "S6", "saisie_notes", "Saisie des notes et predeliberations", D(2026, 4, 6), D(2026, 4, 11), 9)
add(c, a, "S6", "stage_technique", "Stage technique", D(2026, 4, 6), D(2026, 6, 13), 9,
    "le guide (page 10) annonce 12 semaines, ce calendrier donne ~10 semaines")
add(c, a, "S6", "soutenance_stage", "Soutenance des stages techniques", D(2026, 6, 15), D(2026, 6, 20), 9)
add(c, a, "S6", "deliberation", "Deliberations finales", D(2026, 6, 22), D(2026, 6, 27), 9)

# ---------------- Jours feries (page imprimee 9) ----------------
ALL = "TOUS"
add(ALL, "", "", "jour_ferie", "Aid al Mawlid (12 et 13 rabie 1er 1447)", None, None, 9, "dates hegiriennes seulement")
add(ALL, "", "", "jour_ferie", "Marche verte", D(2025, 11, 6), D(2025, 11, 6), 9,
    "imprime: 'Jeudi 06 Novembre 2026'; annee corrigee en 2025 (jeudi 6 nov 2025)")
add(ALL, "", "", "jour_ferie", "Fete de l'independance", D(2025, 11, 18), D(2025, 11, 18), 9,
    "imprime: 'Mardi 18 Novembre 2026'; annee corrigee en 2025 (mardi 18 nov 2025)")
add(ALL, "", "", "jour_ferie", "1er jour de l'an", D(2026, 1, 1), D(2026, 1, 1), 9)
add(ALL, "", "", "jour_ferie", "Presentation du manifeste de l'independance", D(2026, 1, 11), D(2026, 1, 11), 9)
add(ALL, "", "", "jour_ferie", "1er jour de l'an Amazigh", D(2026, 1, 14), D(2026, 1, 14), 9)
add(ALL, "", "", "jour_ferie", "Aid al Fitr (29 ramadan 1447 au 02 chaoual 1447)", None, None, 9, "dates hegiriennes seulement")
add(ALL, "", "", "jour_ferie", "Fete du travail et vacances du printemps", D(2026, 5, 1), D(2026, 5, 10), 9)
add(ALL, "", "", "jour_ferie", "Aid Al Adha (09 au 12 Di Al Hijja 1447)", None, None, 9, "dates hegiriennes seulement")
add(ALL, "", "", "jour_ferie", "1er Moharram 1448", None, None, 9, "date hegirienne seulement")
add(ALL, "", "", "jour_ferie", "Vacances du semestre 1", D(2026, 1, 25), D(2026, 2, 1), 9,
    "la liste des jours feries imprime 'dimanche 24' mais les calendriers indiquent dimanche 25 janvier")

OUT_DIR.mkdir(exist_ok=True)
fields = ["cycle", "annee", "semestre", "type", "libelle", "date_debut", "date_fin", "page_imprimee", "remarque"]
with (OUT_DIR / "calendrier_2025_2026.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

# ---------------- Filieres (pages imprimees 6-7) ----------------
filieres = {
    "annee_universitaire": "2025-2026", "source": SRC, "pages_imprimees": [6, 7],
    "departements": [
        {"code": "GMPMI", "nom": "Genie Mecanique, Productique et Maintenance Industrielle", "filieres": [
            {"diplome": "DUT", "nom": "Genie Mecanique et Productique", "code": "GMP"},
            {"diplome": "DUT", "nom": "Genie Industriel et Maintenance", "code": "GIM"},
            {"diplome": "DBT", "nom": "Production Industrielle Mecatronique", "code": "PIM"}]},
        {"code": "GESI", "nom": "Genie Electrique et Systemes Intelligents", "filieres": [
            {"diplome": "DUT", "nom": "Genie Electrique", "code": "GE"},
            {"diplome": "DUT", "nom": "Systemes Embarques", "code": "SE"},
            {"diplome": "DUT", "nom": "Gestion Reseaux et Securite", "code": "GRS"},
            {"diplome": "DBT", "nom": "Genie Electrique et Systemes Embarques", "code": "GESE"},
            {"diplome": "DBT", "nom": "Cybersecurite des Systemes Intelligents Connectes", "code": "CSIC"}]},
        {"code": "GI", "nom": "Genie Informatique", "filieres": [
            {"diplome": "DUT", "nom": "Ingenierie Logicielle", "code": None},
            {"diplome": "DUT", "nom": "Ingenierie des Donnees", "code": None},
            {"diplome": "DBT", "nom": "Genie Logiciel", "code": None},
            {"diplome": "DBT", "nom": "Sciences des Donnees et Intelligence Artificielle", "code": "SDIA"}]},
        {"code": "STG", "nom": "Sciences et Techniques de la Gestion", "filieres": [
            {"diplome": "DUT", "nom": "Gestion des Ressources Humaines", "code": "GRH"},
            {"diplome": "DUT", "nom": "Techniques de Gestion Commerciale", "code": "TGC"},
            {"diplome": "DUT", "nom": "Gestion Logistique et Transport", "code": "GLT"},
            {"diplome": "DUT", "nom": "Techniques de Management", "code": "TM"},
            {"diplome": "DBT", "nom": "Chaine Logistique Globale", "code": "CLG"}]},
        {"code": "GP", "nom": "Genie des Procedes", "filieres": [
            {"diplome": "DUT", "nom": "Genie des Procedes", "code": None},
            {"diplome": "DUT", "nom": "Agroalimentaire et Bioprocedes", "code": None},
            {"diplome": "DUT", "nom": "Genie Thermique et Energie", "code": None}]},
    ],
}
(OUT_DIR / "filieres.json").write_text(json.dumps(filieres, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(rows)} lignes -> data/calendrier_2025_2026.csv ; filieres -> data/filieres.json")
