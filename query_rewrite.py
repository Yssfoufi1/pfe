"""Expansion de requete: ajoute des mots-cles francais aux mots darija reconnus
(data/darija_lexicon.csv). Pas de LLM: deterministe, rapide, et tu peux enrichir le CSV.

Usage: py query_rewrite.py "ch7al kaykhles talib f l-dakhiliya ?"
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

LEXICON_PATH = Path("data/darija_lexicon.csv")
MIN_SUBSTRING_LEN = 5   # cle >= 5 caracteres: on cherche a l'interieur du mot (l-maktaba, فالداخلية)
_AR_DIACRITICS = re.compile("[\u064b-\u065f\u0670\u0640]")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = _AR_DIACRITICS.sub("", text)
    for a in "أإآٱ":
        text = text.replace(a, "ا")
    return text.replace("ى", "ي").replace("ة", "ه")


def tokenize(text: str):
    return re.findall(r"[0-9a-z\u0600-\u06ff\u0750-\u077f]+", normalize(text))


def load_lexicon(path: Path = LEXICON_PATH):
    entries = []
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                key = normalize(row["variante"]).strip()
                if key:
                    entries.append((key, row["francais"].strip()))
    return entries


_LEXICON = load_lexicon()


def expand_query(question: str):
    """Retourne (requete_etendue, mots_reconnus)."""
    tokens = tokenize(question)
    terms, matched = [], []
    for key, fr in _LEXICON:
        hit = any((key in t) if len(key) >= MIN_SUBSTRING_LEN else (key == t) for t in tokens)
        if hit:
            matched.append(key)
            for w in fr.split():
                if w not in terms:
                    terms.append(w)
    if not terms:
        return question, []
    return f"{question} {' '.join(terms)}", matched


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Usage: py query_rewrite.py "question"')
    exp, matched = expand_query(sys.argv[1])
    print("mots reconnus :", matched or "aucun")
    print("requete etendue:", exp)
