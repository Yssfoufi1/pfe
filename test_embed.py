import time

from rag_common import EMBED_MODEL, cosine, embed

PHRASES = [
    "A: Quel est le loyer de l'internat ?",
    "B: L'ESTF met a disposition un cadre de vie confortable, moyennant un loyer annuel fixe a 1 140,00 DH.",
    "C: ch7al kaykhles l'internat f l-3am ?",
    "D: Quelle est la recette du tajine aux olives ?",
]

t0 = time.time()
vecs = embed(PHRASES)
print(f"modele={EMBED_MODEL}  dimensions={len(vecs[0])}  temps={time.time() - t0:.1f}s\n")
print("similarite cosinus (plus c'est proche de 1, plus c'est semblable):")
for i in range(len(PHRASES)):
    for j in range(i + 1, len(PHRASES)):
        print(f"  {PHRASES[i][0]} - {PHRASES[j][0]} : {cosine(vecs[i], vecs[j]):.3f}")
print("\nAttendu: A-B et C-B nettement plus hauts que A-D, B-D, C-D.")
