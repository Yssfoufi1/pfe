"""Tableau des clubs (page PDF 20 / imprimee 19) -> data/extracted/clubs.csv

pdfplumber ne detecte pas les lignes de ce tableau; on reconstruit donc les lignes
a partir des traits horizontaux (y) et des colonnes (x) de CE tableau precis.
"""
import csv
from pathlib import Path

import pdfplumber

PDF_PATH = Path("documents/guide_etudiant_2025_2026.pdf")
OUT_PATH = Path("data/extracted/clubs.csv")
PDF_PAGE = 20
PRINTED_PAGE = 19
# traits horizontaux du tableau (y): bas de l'en-tete puis une ligne par club
ROW_EDGES = [157, 196, 228, 266, 304, 342, 380, 421, 459, 505, 552]
# colonnes (x): club | president | contact | domaines d'activites
COL_EDGES = [0, 145, 215, 270, 420]
COLS = ["club", "president", "contact", "domaines"]


def cell_text(words, x0, x1, y0, y1):
    ws = [w for w in words if x0 <= w["x0"] < x1 and y0 <= w["top"] < y1]
    ws.sort(key=lambda w: (round(w["top"] / 4), w["x0"]))
    return " ".join(w["text"] for w in ws)


def main():
    with pdfplumber.open(PDF_PATH) as pdf:
        words = pdf.pages[PDF_PAGE - 1].extract_words()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for y0, y1 in zip(ROW_EDGES, ROW_EDGES[1:]):
        row = {c: cell_text(words, COL_EDGES[i], COL_EDGES[i + 1], y0, y1) for i, c in enumerate(COLS)}
        row["page_imprimee"] = PRINTED_PAGE
        rows.append(row)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS + ["page_imprimee"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} clubs -> {OUT_PATH}")
    for r in rows:
        print(f"  {r['club']:<20} | {r['president']:<20} | {r['contact']:<11} | {r['domaines']}")


if __name__ == "__main__":
    main()
