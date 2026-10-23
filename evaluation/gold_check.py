"""Verification HORS LIGNE du jeu de questions de reference (evaluation/gold/guide_questions.csv).

1) Chaque question vise un chunk qui existe ET le fait attendu (expression reguliere) figure bien dans le texte de ce chunk :
   la bonne reponse vient donc du DOCUMENT, jamais d'un modele.
2) Carte de couverture : quels chunks / pages ont des questions, lesquels n'en ont pas encore.

Usage (racine du depot) :  py -m evaluation.gold_check
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

CHUNKS_PATH = Path("data/chunks/chunks.jsonl")
GOLD_PATH = Path("evaluation/gold/guide_questions.csv")


def fact_ok(regex: str, text: str) -> bool:
    """Toutes les parties separees par ' && ' doivent correspondre."""
    return all(re.search(p.strip(), text, flags=re.I | re.S) for p in regex.split(" && "))


def load_chunks():
    return {c["id"]: c for c in map(json.loads, CHUNKS_PATH.open(encoding="utf-8"))}


def load_gold():
    with GOLD_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    chunks, gold = load_chunks(), load_gold()
    problems = 0
    print(f"{len(gold)} questions de reference, {len(chunks)} chunks\n1) Le fait attendu est-il dans le chunk vise ?")
    for g in gold:
        c = chunks.get(g["chunk_id"])
        if c is None:
            print(f"  PROBLEME {g['id']}: chunk introuvable {g['chunk_id']}")
            problems += 1
        elif not fact_ok(g["fact_regex"], c["text"]):
            print(f"  PROBLEME {g['id']}: le fait attendu n'est PAS dans {g['chunk_id']}  ({g['fact_regex']})")
            problems += 1
        elif int(g["page"]) != c["printed_page"]:
            print(f"  PROBLEME {g['id']}: page {g['page']} != page du chunk {c['printed_page']}")
            problems += 1
    print("  aucun probleme" if not problems else f"  {problems} probleme(s)")

    per_chunk = defaultdict(int)
    for g in gold:
        per_chunk[g["chunk_id"]] += 1
    print("\n2) Couverture par page imprimee (chunks avec au moins une question / chunks de la page)")
    pages = defaultdict(list)
    for c in chunks.values():
        pages[c["printed_page"]].append(c["id"])
    covered = 0
    for p in sorted(pages):
        ids = pages[p]
        n = sum(1 for i in ids if per_chunk[i])
        covered += n
        missing = [i for i in ids if not per_chunk[i]]
        print(f"  p.{p:<3} {n}/{len(ids)}" + (f"   sans question : {', '.join(m.split('-', 1)[1] for m in missing)}" if missing else "   complet"))
    print(f"\nTOTAL : {covered}/{len(chunks)} chunks couverts par au moins une question ; {len(gold)} questions")
    print("RESULTAT:", "coherent" if not problems else "a corriger")


if __name__ == "__main__":
    main()
