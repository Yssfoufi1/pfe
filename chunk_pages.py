"""Etape 3 : decoupage de data/pages.jsonl en chunks -> data/chunks.jsonl

Principes :
- un chunk ne traverse jamais une page (la page imprimee est donc exacte pour la citation);
- on decoupe d'abord par sections (titres en MAJUSCULES) et sous-titres ("Titre :"),
  puis, si un bloc est trop long, par unites (puces / phrases);
- chaque chunk garde son contexte (document > chapitre > section > sous-section > page),
  qui sera ajoute au texte avant l'embedding.
"""
import csv
import json
from pathlib import Path

PAGES_PATH = Path("data/pages.jsonl")
CLUBS_PATH = Path("data/clubs.csv")
OUT_PATH = Path("data/chunks.jsonl")

DOC_TITLE = "Guide de l'etudiant EST Fes 2025-2026"
MAX_CHARS = 1400
MIN_CHARS = 300                 # un bloc plus petit est fusionne avec le precedent (meme section)
MIN_PAGE_CHARS = 100            # pages-images: remplacees par calendrier_*.csv / filieres.json
SKIP_PDF_PAGES = {1, 2}         # couverture et sommaire
CHAPTER_OVERRIDES = {3: "Mot du Directeur", 21: "Contacts de l'ecole"}
# page PDF -> debut du tableau (le tableau est traite a part via un CSV)
STOP_AT = {20: "CLUBS & ASSOCIATIONS"}
EXTRA_SUBHEADINGS = {"La carte d'étudiant", "La délivrance des diplômes"}
BULLETS = ("▪", "•", "- ", "– ")


def is_bullet(line: str) -> bool:
    return line.lstrip().startswith(BULLETS)


def is_upper_heading(line: str) -> bool:
    letters = [c for c in line if c.isalpha()]
    return (len(letters) >= 5 and all(c.isupper() for c in letters)
            and len(line) <= 70 and not is_bullet(line))


def is_subheading(line: str) -> bool:
    s = line.strip()
    if is_bullet(s):
        return False
    # un vrai sous-titre commence par une majuscule; "conditions suivantes :" (fin de phrase) non
    return (s.endswith(":") and len(s) <= 80 and s[:1].isupper()) or s in EXTRA_SUBHEADINGS


def split_units(lines):
    """Unites = une puce avec ses lignes de suite, ou une phrase/paragraphe."""
    units, cur = [], []
    for line in lines:
        starts_new = bool(cur) and (
            is_bullet(line)
            or (cur[-1].rstrip().endswith((".", "!", "?")) and line[:1].isupper())
        )
        if starts_new:
            units.append("\n".join(cur))
            cur = []
        cur.append(line)
    if cur:
        units.append("\n".join(cur))
    return units


def pack(units):
    chunks, cur = [], ""
    for u in units:
        if cur and len(cur) + 1 + len(u) > MAX_CHARS:
            chunks.append(cur)
            cur = ""
        cur = f"{cur}\n{u}" if cur else u
    if cur:
        chunks.append(cur)
    return chunks


def page_blocks(lines, state):
    """Retourne la liste de blocs (section, sous-section, lignes); state porte le contexte entre pages."""
    blocks, cur = [], None

    def start():
        nonlocal cur
        cur = {"section": state["section"], "sub": state["sub"], "lines": []}
        blocks.append(cur)

    start()
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if is_upper_heading(s):
            state["section"], state["sub"] = s, None
            start()
        elif is_subheading(s):
            name = s.rstrip(" :")
            if name in ("Exemple", "Exemples") and state["sub"]:
                name = state["sub"].split(" — ")[0] + " — Exemples"
            state["sub"] = name
            start()
        else:
            cur["lines"].append(s)
    return [b for b in blocks if b["lines"]]


def merge_small(blocks):
    out = []
    for b in blocks:
        text = "\n".join(b["lines"])
        if out and len(text) < MIN_CHARS and out[-1]["section"] == b["section"]:
            out[-1]["lines"].extend(b["lines"])
        else:
            out.append({"section": b["section"], "sub": b["sub"], "lines": list(b["lines"])})
    return out


def main():
    pages = [json.loads(l) for l in PAGES_PATH.open(encoding="utf-8")]
    chunks, skipped = [], []
    state = {"chapter": None, "section": None, "sub": None}

    for p in pages:
        pdf_page, printed = p["pdf_page"], p["printed_page"]
        if pdf_page in SKIP_PDF_PAGES or p["n_chars"] < MIN_PAGE_CHARS:
            skipped.append((pdf_page, printed, p["n_chars"]))
            continue

        lines = [l.strip() for l in p["text"].splitlines() if l.strip()]
        if lines and lines[-1].isdigit():          # numero de page en bas
            lines = lines[:-1]

        if pdf_page in STOP_AT:
            for idx, l in enumerate(lines):
                if l.startswith(STOP_AT[pdf_page]):
                    lines = lines[:idx]
                    break

        chapter = CHAPTER_OVERRIDES.get(pdf_page)
        if chapter is None and lines and is_upper_heading(lines[0]):
            chapter, lines = lines[0], lines[1:]
        if chapter != state["chapter"]:
            state.update(chapter=chapter, section=None, sub=None)

        blocks = merge_small(page_blocks(lines, state))
        k = 0
        for b in blocks:
            for body in pack(split_units(b["lines"])):
                k += 1
                parts = [DOC_TITLE, chapter, b["section"], b["sub"]]
                context = " > ".join(x for x in parts if x) + f" (p. {printed})"
                chunks.append({
                    "id": f"guide2526-p{printed}-{k}",
                    "source": p["source"],
                    "printed_page": printed,
                    "pdf_page": pdf_page,
                    "chapter": chapter,
                    "section": b["section"],
                    "subsection": b["sub"],
                    "context": context,
                    "text": body,
                    "n_chars": len(body),
                })

    if CLUBS_PATH.exists():
        with CLUBS_PATH.open(encoding="utf-8") as f:
            for k, r in enumerate(csv.DictReader(f), start=1):
                body = (f"Club ou association : {r['club']}. President(e) : {r['president']}. "
                        f"Contact : {r['contact']}. Domaines d'activites : {r['domaines']}.")
                printed = int(r["page_imprimee"])
                chunks.append({
                    "id": f"guide2526-club-{k}", "source": "guide_etudiant_2025_2026.pdf",
                    "printed_page": printed, "pdf_page": printed + 1,
                    "chapter": "VIE ASSOCIATIVE", "section": "LES ASSOCIATIONS ET CLUBS",
                    "subsection": r["club"],
                    "context": f"{DOC_TITLE} > VIE ASSOCIATIVE > Clubs et associations > {r['club']} (p. {printed})",
                    "text": body, "n_chars": len(body),
                })

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    sizes = [c["n_chars"] for c in chunks]
    print(f"{len(chunks)} chunks -> {OUT_PATH}")
    print(f"taille (caracteres): min={min(sizes)}  moyenne={sum(sizes)//len(sizes)}  max={max(sizes)}")
    print("pages ignorees (pdf, imprimee, chars):", skipped)
    print("\nchunks par page imprimee:")
    per = {}
    for c in chunks:
        per[c["printed_page"]] = per.get(c["printed_page"], 0) + 1
    print(per)


if __name__ == "__main__":
    main()
