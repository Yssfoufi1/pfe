import json

chunks = [json.loads(l) for l in open("data/chunks.jsonl", encoding="utf-8")]

print("1) Chunks tres courts (< 80 caracteres):")
short = [c for c in chunks if c["n_chars"] < 80]
for c in short:
    print(f"   {c['id']:<22} {c['n_chars']:>3} car. | {c['context']} | {c['text']!r}")
if not short:
    print("   aucun")

print("\n1b) Sous-sections suspectes (ne commencent pas par une majuscule):")
sus = [c for c in chunks if c["subsection"] and not c["subsection"][:1].isupper()]
for c in sus:
    print(f"   {c['id']}: {c['subsection']!r}")
if not sus:
    print("   aucune")

print("\n2) Faits qui doivent rester ENSEMBLE dans un meme chunk:")
FACTS = [
    ("validation module", ["moyenne ≥ 10", "en dessous de 5"], 11),
    ("rattrapage module", ["moyenne est ≥ 4", "maximale obtenable au rattrapage = 10/20", "< 7/20"], 11),
    ("validation annee", ["moyenne générale des modules est ≥ 10/20", "moyenne < 7/20"], 11),
    ("derogation", ["maximum de 2 modules", "chef d’établissement"], 11),
    ("exemple admis 11,20", ["Moyenne Annuelle : 11,20", "08,00 Par Compensation"], 11),
    ("exemple ajourne 09,60", ["Moyenne Annuelle : 09,60", "06,00 Non Validé"], 11),
    ("exemple 10,95", ["Moyenne Annuelle : 10,95", "dérogation ou Ajourné"], 11),
    ("absence 48h", ["48 heures", "infirmerie"], 12),
    ("consultation copies", ["sept jours ouvrables", "coordonnateur de filière"], 12),
    ("points de jury", ["0,2 point", "maximum de 2 points", "cumulables"], 12),
    ("DUT credits", ["120 crédits", "28 modules"], 10),
    ("acces S3", ["validation de l’ensemble des modules des semestres 1 et 2", "stage d’initiation"], 10),
    ("DBT credits", ["60 crédits", "14 modules"], 10),
    ("bibliotheque", ["9h00 à 16h00", "5 ouvrages maximum", "15 jours"], 14),
    ("AMO", ["moins de 30 ans", "RAMED"], 14),
    ("internat loyer", ["1 140,00 DH"], 17),
    ("internat conditions", ["en dehors de la ville de Fès"], 17),
    ("infirmerie horaires", ["10h00 à 16h00", "lundi au vendredi"], 15),
    ("inscription pieces", ["Attestation originale du baccalauréat", "Quatre photos d’identité", "Code Massar"], 13),
    ("contacts scolarite", ["Service de la Scolarité", "Bâtiment B"], 5),
    ("club NEXUS", ["NEXUS", "KAOUTAR HANDOUZ", "0719366255", "conférences"], 19),
    ("club CULTISIO", ["CULTISIO", "OUMAIMA IDRISSI", "0773389061"], 19),
    ("exemples annee", ["Moyenne Annuelle : 11,20", "Admis"], 11),
    ("numerotation salles", ["G = lettre du bâtiment", "3 = salle de l'étage"], 4),
]
bad = 0
for name, needles, page in FACTS:
    hits = [c for c in chunks if c["printed_page"] == page and all(n in " ".join(c["text"].split()) for n in needles)]
    status = "OK " if hits else "ECHEC"
    if not hits:
        bad += 1
    where = hits[0]["id"] if hits else "-"
    print(f"   {status} {name:<24} p.{page:<3} {where}")
print(f"\nRESULTAT: {len(FACTS) - bad}/{len(FACTS)} faits intacts")

print("\n3) Apercu de 4 chunks:")
for cid in ("guide2526-p11-1", "guide2526-p11-3", "guide2526-p17-1", "guide2526-p19-1"):
    for c in chunks:
        if c["id"] == cid:
            print(f"\n--- {c['id']} ({c['n_chars']} car.)\n{c['context']}\n{c['text'][:420]}")
