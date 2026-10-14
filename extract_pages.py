"""Etape 1 (v2) : extraction du texte page par page -> data/pages.jsonl

Differences avec la v1 :
- les encadres d'exemples (petites images contenant du texte) sont extraits a part,
  pour ne plus melanger les colonnes cote a cote (page imprimee 11);
- le texte superpose aux grandes images (plans, photos) est ignore (lettres D, E, F du plan page 4).
"""
import json
import re
from pathlib import Path

import pdfplumber

PDF_PATH = Path("data/guide_etudiant_2025_2026.pdf")
OUT_PATH = Path("data/pages.jsonl")
MIN_CHARS = 200        # en dessous, la page est probablement une image
PAGE_OFFSET = 1        # page imprimee = page PDF - 1 (la couverture n'est pas numerotee)
BIG_IMAGE_H = 150      # image haute (plan, photo): on ignore le texte qui la recouvre
BOX_MIN_W = 100        # petite image contenant du texte (encadre d'exemple): extraite a part
KEEP_ALL_TEXT = {1}    # couverture: on garde tout


def clean(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def inside(obj, b, tol=1.0):
    return (obj["x0"] >= b[0] - tol and obj["x1"] <= b[2] + tol
            and obj["top"] >= b[1] - tol and obj["bottom"] <= b[3] + tol)


def classify_images(page, words):
    drop, boxes = [], []
    for im in page.images:
        b = (im["x0"], im["top"], im["x1"], im["bottom"])
        w, h = b[2] - b[0], b[3] - b[1]
        if not any(inside(wd, b) for wd in words):
            continue
        if h >= BIG_IMAGE_H:
            drop.append(b)
        elif w >= BOX_MIN_W:
            boxes.append(b)
    return drop, boxes


def page_text(page, pdf_page: int) -> str:
    words = page.extract_words()
    drop, boxes = ([], []) if pdf_page in KEEP_ALL_TEXT else classify_images(page, words)
    excluded = drop + boxes
    if not excluded:
        return clean(page.extract_text() or "")

    def keep(obj):
        return obj.get("object_type") != "char" or not any(inside(obj, b) for b in excluded)

    items = [(l["top"], l["x0"], l["text"]) for l in page.filter(keep).extract_text_lines()]
    px0, ptop, px1, pbottom = page.bbox
    for b in boxes:
        cb = (max(b[0], px0), max(b[1], ptop), min(b[2], px1), min(b[3], pbottom))
        t = page.crop(cb).extract_text() or ""
        if t.strip():
            items.append((b[1], b[0], t))
    items.sort(key=lambda it: (round(it[0]), it[1]))
    return clean("\n".join(t for _, _, t in items))


def footer_number(text: str):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return int(lines[-1]) if lines and lines[-1].isdigit() else None


def main():
    pages = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page_text(page, i)
            pages.append({
                "source": PDF_PATH.name,
                "pdf_page": i,
                "printed_page": i - PAGE_OFFSET if i > 1 else None,
                "footer_seen": footer_number(text),
                "n_chars": len(text),
                "low_text": len(text) < MIN_CHARS,
                "text": text,
            })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for p in pages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"{len(pages)} pages -> {OUT_PATH}")
    print("\npdf  imprime  footer  chars  low_text")
    for p in pages:
        print(f"{p['pdf_page']:>3}  {str(p['printed_page']):>7}  {str(p['footer_seen']):>6}  {p['n_chars']:>5}  {p['low_text']}")
    mism = [p["pdf_page"] for p in pages
            if p["footer_seen"] is not None and p["printed_page"] is not None
            and p["footer_seen"] != p["printed_page"]]
    print("\nPages ou le numero imprime ne correspond pas a l'offset:", mism or "aucune")


if __name__ == "__main__":
    main()
