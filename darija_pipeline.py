"""Traduction francais -> darija (lettres arabes puis arabizi) avec garde-fous.

Probleme constate avec Atlas-Chat-2B : darija fluide mais pas toujours fidele
(infirmerie -> pharmacie, emprunter -> produire, "p." -> "partie").
Solution : on PROTEGE ce qui ne doit pas changer avant de traduire :
  - les chiffres, heures et montants      -> [[N1]], [[N2]]...
  - les termes du glossaire (data/glossaire_fr_darija.csv) -> [[T1]]...
  - la citation de page "(p. 17)"         -> retiree puis rajoutee telle quelle
Apres traduction on VERIFIE que chaque balise est revenue exactement une fois;
sinon le resultat est marque 'ok=False' et l'appelant doit repondre en francais.
Puis on remplace les balises par la forme darija choisie dans le glossaire.
"""
import csv
import re
from pathlib import Path

from rag_common import chat

GLOSSARY_PATH = Path("data/glossaire_fr_darija.csv")
ARTICLE = r"(?:(?:l'|l’|la |le |les |de la |du |des |d'|un |une )\s*)?"
_CITATION = re.compile(r"\s*\((?:p\.|pp\.)\s*([\d,\s\-]+)\)\s*\.?\s*$")
_NUMBER = re.compile(r"\d{1,2}h\d{2}|\d+(?:[ \u00a0]\d{3})*(?:[.,]\d+)?(?:\s?DH)?")
_TAG = re.compile(r"\[\[\s*([TN]\d+)\s*\]\]", re.I)
_ARABIC = re.compile("[\u0600-\u06ff]")

TO_DARIJA = ("ترجم الجواب التالي إلى الدارجة المغربية. العلامات بحال [[T1]] و[[N1]] خليها بحال ما هي "
             "بلا ما تبدلها ولا تحيدها. جاوب غير بالترجمة.\n\nالجواب:\n{text}")
TO_ARABIZI = ("كتب هاد النص بالحروف اللاتينية بحال ما كيكتبو المغاربة فالواتساب (عربيزي): "
              "3 = ع، 7 = ح، 9 = ق، 5 = خ. العلامات بحال [[T1]] و[[N1]] خليها بحال ما هي. "
              "جاوب غير بالنص المكتوب.\n\nالنص:\n{text}")
# exemples few-shot (arabe -> arabizi): a corriger par un locuteur natif
FEWSHOT = [
    ("[[T1]] مفتوحة من [[N1]] حتى [[N2]].", "[[T1]] mftou7a men [[N1]] hta [[N2]]."),
    ("خاصك تكون مسجل فـ [[T1]] وتكون عندك قل من [[N1]] عام.", "khassek tkoun msajjel f [[T1]] w tkoun 3andek 9ell mn [[N1]] 3am."),
    ("شحال كيخلص الطالب فـ [[T1]]؟", "ch7al kaykhles talib f [[T1]] ?"),
]


def load_glossary(path: Path = GLOSSARY_PATH):
    with path.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["fr"].strip()]
    return sorted(rows, key=lambda r: len(r["fr"]), reverse=True)      # termes longs d'abord


def protect(text: str, glossary):
    """Retourne (texte_avec_balises, {balise: (valeur_originale, ligne_glossaire|None)}, pages)."""
    pages = ""
    m = _CITATION.search(text)
    if m:
        pages = " ".join(m.group(1).split())
        text = text[:m.start()].rstrip() + "."
    tags = {}
    counter = {"N": 0, "T": 0}

    def new_tag(kind, value, row=None):
        counter[kind] += 1
        tag = f"{kind}{counter[kind]}"
        tags[tag] = (value, row)
        return f"[[{tag}]]"

    text = _NUMBER.sub(lambda mm: new_tag("N", mm.group(0)), text)        # chiffres d'abord
    for row in glossary:
        # sigles (AMO, DUT, EST...) : casse exacte, sinon "EST" attrape le verbe francais "est"
        flags = 0 if row["fr"].isupper() else re.I
        pat = re.compile(r"(?<!\w)" + ARTICLE + re.escape(row["fr"]) + r"(?!\w)", flags)
        text = pat.sub(lambda mm, row=row: new_tag("T", mm.group(0), row), text)
    return text, tags, pages


def normalize_tags(text: str) -> str:
    return _TAG.sub(lambda m: f"[[{m.group(1).upper()}]]", text)


def tags_ok(text: str, tags) -> bool:
    found = [m.group(1).upper() for m in _TAG.finditer(text)]
    return sorted(found) == sorted(tags.keys())


def restore(text: str, tags, script: str, pages: str = "") -> str:
    """script: 'ar' ou 'lat' -> forme du glossaire utilisee pour les termes."""
    def sub(m):
        value, row = tags[m.group(1).upper()]
        return row[script] if row else value
    out = _TAG.sub(sub, text)
    return out + (f" (p. {pages})" if pages else "")


def is_latin(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum(bool(_ARABIC.match(c)) for c in letters) / len(letters) < 0.1


def _ask(model: str, messages) -> str:
    return chat(messages, model=model, temperature=0.2)


def to_darija(fr_answer: str, model: str, glossary=None):
    glossary = glossary if glossary is not None else load_glossary()
    text, tags, pages = protect(fr_answer, glossary)
    ar_tagged = normalize_tags(_ask(model, [{"role": "user", "content": TO_DARIJA.format(text=text)}]))

    msgs = []
    for src, dst in FEWSHOT:
        msgs += [{"role": "user", "content": TO_ARABIZI.format(text=src)}, {"role": "assistant", "content": dst}]
    msgs.append({"role": "user", "content": TO_ARABIZI.format(text=ar_tagged)})
    lat_tagged = normalize_tags(_ask(model, msgs))

    return {
        "protected": text,
        "ar": restore(ar_tagged, tags, "ar", pages), "ar_ok": tags_ok(ar_tagged, tags),
        "lat": restore(lat_tagged, tags, "lat", pages),
        "lat_ok": tags_ok(lat_tagged, tags) and is_latin(restore(lat_tagged, tags, "lat", pages)),
    }
