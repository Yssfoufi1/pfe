"""Test de fumee de la GENERATION (necessite Ollama) : l'assistant repond-il avec le bon fait ?

Pourquoi : le 2026-10-19 `ask` a renvoye seulement "(18)" a "Quel est le loyer annuel de l'internat ?"
apres un changement de prompt, et aucun test automatique ne l'a detecte.
Ce script pose quelques questions et verifie, pour chaque reponse :
  - elle contient le fait attendu (expression reguliere) ;
  - elle est une vraie reponse (au moins 8 lettres), pas un simple "(18)".
Ce n'est PAS l'evaluation de fidelite de la phase 4 de la roadmap : c'est un garde-fou contre les regressions.

Usage (depuis la racine du depot) :  py -m evaluation.smoke_generation
"""
import re
import time

from src.app.ask import answer

CASES = [
    ("FR", "Quel est le loyer annuel de l'internat ?", r"1[\s,.]?140", "loyer internat"),
    ("FR", "Quels sont les horaires d'ouverture de la bibliothèque ?", r"9\s?h(\s?00)?.{0,25}16\s?h", "horaires bibliothèque"),
    ("FR", "Combien de livres peut-on emprunter à la bibliothèque ?", r"\b5\b|cinq", "livres empruntables"),
    ("FR", "Dans quel délai faut-il justifier une absence à un contrôle ?", r"48", "délai absence"),
    ("FR", "Quelles sont les conditions d'éligibilité à l'AMO ?", r"30\s?ans", "AMO"),
    ("FR", "Combien de crédits faut-il pour obtenir le DUT ?", r"120", "crédits DUT"),
    ("EN", "How much is the yearly rent for the dormitory?", r"1[\s,.]?140", "rent (EN)"),
    ("EN", "How many books can I borrow from the library?", r"\b5\b|five", "books (EN)"),
    ("DAR_LAT", "ch7al kaykhles talib f l-dakhiliya f l-3am ?", r"1[\s,.]?140", "loyer (arabizi, réponse en français)"),
]


def is_real_answer(text: str) -> bool:
    return len(re.findall(r"[A-Za-zÀ-ÿ]", text)) >= 8


def main():
    ok_count = 0
    times = []
    t0 = time.time()
    for lang, q, pattern, label in CASES:
        t1 = time.time()
        text, _ = answer(q)
        secs = time.time() - t1
        times.append(secs)
        fact = bool(re.search(pattern, text, flags=re.I | re.S))
        real = is_real_answer(text)
        good = fact and real
        ok_count += good
        print(f"[{'OK' if good else 'ECHEC'}] {lang:<8} {label:<38} fait: {'oui' if fact else 'NON'}  vraie reponse: {'oui' if real else 'NON'}  ({secs:.0f}s)")
        if not good:
            print("        reponse:", " ".join(text.split())[:200])
    times.sort()
    print(f"\nRESULTAT: {ok_count}/{len(CASES)}   (temps total {time.time() - t0:.0f}s ; par question : min {times[0]:.0f}s, mediane {times[len(times) // 2]:.0f}s, max {times[-1]:.0f}s)")


if __name__ == "__main__":
    main()
