"""Teste Atlas-Chat avec les garde-fous (darija_pipeline.py).
Usage: py -m tests.test_darija_model [nom_du_modele]     (defaut: atlas-chat-2b)
Pour chaque reponse francaise: darija (lettres arabes), arabizi, et 2 verifications automatiques:
  - ar_ok  : toutes les balises (chiffres, termes proteges) sont revenues exactement une fois
  - lat_ok : idem + le texte est bien en lettres latines
Le jugement sur le naturel de la darija, c'est toi qui le fais."""
import sys
import time

from src.experimental import darija_pipeline as dp

MODEL = sys.argv[1] if len(sys.argv) > 1 else "atlas-chat-2b"

FR_ANSWERS = [
    "Le loyer annuel de l'internat est de 1 140,00 DH (p. 17).",
    "La bibliothèque est ouverte de 9h00 à 16h00 du lundi au vendredi. Tu peux emprunter 5 ouvrages maximum, à rendre dans un délai de 15 jours (p. 14).",
    "La justification de l'absence doit être déposée à l'infirmerie de l'école dans un délai de 48 heures à partir du début de l'absence (p. 12).",
    "Pour l'AMO, il faut être inscrit à l'EST, avoir moins de 30 ans et ne pas bénéficier d'une autre couverture médicale de base (p. 14).",
]


def main():
    glossary = dp.load_glossary()
    n_ar = n_lat = 0
    t0 = time.time()
    for i, fr in enumerate(FR_ANSWERS, 1):
        r = dp.to_darija(fr, MODEL, glossary)
        n_ar += r["ar_ok"]
        n_lat += r["lat_ok"]
        print(f"\n[{i}] FR       : {fr}")
        print(f"    protege  : {r['protected']}")
        print(f"    DARIJA   : {r['ar']}   (ar_ok: {'oui' if r['ar_ok'] else 'NON'})")
        print(f"    ARABIZI  : {r['lat']}   (lat_ok: {'oui' if r['lat_ok'] else 'NON'})")
    n = len(FR_ANSWERS)
    print(f"\nRESULTAT: ar_ok {n_ar}/{n}, lat_ok {n_lat}/{n}   (temps total {time.time() - t0:.0f}s, modele {MODEL})")


if __name__ == "__main__":
    main()
