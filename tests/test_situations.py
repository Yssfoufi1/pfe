"""Teste si le SLM (Qwen) sait trancher une situation d'etudiant avec les regles du guide (p. 11).
Verite terrain = rules.py (verifie sur les 6 exemples du guide).

Usage:
  py -m tests.test_situations              contexte "oracle": on donne a Qwen les 2 chunks de regles (p. 11)
                                     -> mesure son RAISONNEMENT, sans l'effet de la recherche
  py -m tests.test_situations --pipeline   recherche normale (ask.py) -> mesure recherche + raisonnement
Chaque question demande de finir par 'VERDICT: X' pour pouvoir corriger automatiquement."""
import json
import re
import sys
import time
import unicodedata

from src.app.ask import SYSTEM_PROMPT, LANG_RULES, answer, build_messages
from src.common.rag_common import chat
from src.app.rules import module_status, year_decision

MODULE_TOKENS = {"VALIDE": "VALIDE", "RATTRAPAGE": "RATTRAPAGE", "NON_VALIDE_SANS_RATTRAPAGE": "NON VALIDE"}
YEAR_TOKENS = {"ADMIS": "ADMIS", "AJOURNE": "AJOURNE", "DEROGATION_POSSIBLE": "JURY"}
MODULE_ASK = "Termine par une ligne exacte « VERDICT: X » où X est UN SEUL de ces mots : VALIDÉ, RATTRAPAGE, NON VALIDÉ."
YEAR_ASK = ("Termine par une ligne exacte « VERDICT: X » où X est UN SEUL de ces mots : ADMIS, AJOURNÉ, "
            "JURY (si la décision dépend du jury / d'une dérogation).")


def fmt(x):
    return f"{x:g}".replace(".", ",")


def module_case(sid, name, elements, avg):
    els = ", ".join(f"{n} = {fmt(v)}" for n, v in elements)
    q = (f"Dans le module {name}, mes notes sont : {els}. La moyenne de mon module est {fmt(avg)}. "
         f"Est-ce que mon module est validé ? {MODULE_ASK}")
    return {"id": sid, "kind": "module", "question": q,
            "expected": MODULE_TOKENS[module_status(avg, [v for _, v in elements])[0]]}


def year_case(sid, modules, annual_avg):
    parts = []
    for name, avg, els in modules:
        parts.append(f"{name} : {fmt(avg)}" + (f" (Cours {fmt(els[0])}, TP {fmt(els[1])})" if els else ""))
    q = ("Voici mes notes finales de l'année : " + " ; ".join(parts) +
         f". Ma moyenne annuelle est {fmt(annual_avg)}. Est-ce que je suis admis ou ajourné ? {YEAR_ASK}")
    res = year_decision([(avg, els) for _, avg, els in modules], annual_avg)
    return {"id": sid, "kind": "year", "question": q, "expected": YEAR_TOKENS[res["decision"]]}


CASES = [
    module_case("M1", "Informatique", [("Cours", 6), ("TP", 16)], 11),
    module_case("M2", "Réseaux", [("Cours", 4), ("TP", 18)], 11),
    module_case("M3", "Introduction au droit", [("Cours", 3)], 3),
    module_case("M4", "Bases de données", [("Cours", 7), ("TP", 11)], 9),
    module_case("M5", "Statistiques", [("Cours", 5), ("TP", 15)], 10),
    year_case("Y1", [("Module 1", 11, None), ("Module 3", 14, None), ("Module 11", 8, None),
                     ("Module 12", 10, None), ("Module 14", 16, None)], 11.20),
    year_case("Y2", [("Module 1", 8, (4, 12)), ("Module 3", 14, None), ("Module 11", 6, None),
                     ("Module 12", 10, None), ("Module 14", 16, None)], 9.60),
    year_case("Y3", [("Module 1", 11, None), ("Module 3", 14, None), ("Module 11", 6, None),
                     ("Module 12", 10, None), ("Module 14", 16, None)], 10.95),
    year_case("Y4", [("Module 1", 9, None), ("Module 2", 10, None), ("Module 3", 10.5, None)], 9.8),
    year_case("Y5", [("Module 1", 12, None), ("Module 2", 7.5, None), ("Module 3", 15, None),
                     ("Module 4", 10, None)], 11.1),
    year_case("Y6", [("Module 1", 6, None), ("Module 2", 5, None), ("Module 3", 6.5, None),
                     ("Module 4", 17, None), ("Module 5", 18, None)], 10.5),
]


def norm(s):
    s = unicodedata.normalize("NFKD", s.upper())
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip()


def parse_verdict(text):
    found = re.findall(r"VERDICT\s*:\s*([^\n.]+)", text, flags=re.I)
    return norm(found[-1]) if found else "(aucun)"


def oracle_hits():
    wanted = ("guide2526-p11-1", "guide2526-p11-2")
    hits = []
    for line in open("data/chunks/chunks.jsonl", encoding="utf-8"):
        c = json.loads(line)
        if c["id"] in wanted:
            hits.append({"context": c["context"], "text": c["text"], "page": c["printed_page"], "score": 1.0})
    return hits


def run_case(case, pipeline):
    if pipeline:
        text, hits = answer(case["question"])
        retrieved = [h["id"] for h in hits]
        return text, retrieved
    messages = build_messages(case["question"], oracle_hits(), "fr")
    return chat(messages, temperature=0.0), ["oracle"]


def main():
    pipeline = "--pipeline" in sys.argv
    mode = "pipeline (recherche normale)" if pipeline else "oracle (regles p. 11 fournies)"
    print(f"Mode: {mode}\n")
    score = {"module": [0, 0], "year": [0, 0]}
    t0 = time.time()
    for case in CASES:
        text, retrieved = run_case(case, pipeline)
        got = parse_verdict(text)
        good = got == norm(case["expected"])
        score[case["kind"]][0] += good
        score[case["kind"]][1] += 1
        print(f"[{case['id']}] attendu: {case['expected']:<10} obtenu: {got:<10} {'OK' if good else 'ECHEC'}"
              + (f"   chunks: {retrieved}" if pipeline else ""))
        if not good:
            print("     reponse:", " ".join(text.split())[:260])
    print(f"\nRESULTAT  modules: {score['module'][0]}/{score['module'][1]}   annee: {score['year'][0]}/{score['year'][1]}"
          f"   (temps {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
