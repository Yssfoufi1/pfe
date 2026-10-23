"""Validation du guide PAGE PAR PAGE (lot par lot) avec les questions de reference.

Trois modes qui isolent la cause d'un echec :
  retrieval : le chunk qui contient la reponse est-il retrouve dans le top-5 ?            (rapide, embeddings seulement)
  oracle    : si on donne a Qwen UNIQUEMENT ce chunk, repond-il correctement ?            (le modele sait-il LIRE ce passage ?)
  e2e       : assistant complet (recherche + Qwen) : la reponse contient-elle le fait ?
Lecture : retrieval OK + oracle ECHEC = probleme de lecture (texte mal extrait, tableau, modele) ;
          retrieval ECHEC + oracle OK = probleme de recherche ; les deux OK mais e2e ECHEC = probleme de prompt/contexte.

Usage (racine du depot, Ollama lance) :
  py -m evaluation.run_coverage --mode retrieval --pages 10-12
  py -m evaluation.run_coverage --mode oracle    --pages 10-12
  py -m evaluation.run_coverage --mode e2e       --pages 10-12
Les resultats detailles vont dans evaluation/results/ (non versionne : peut contenir des donnees personnelles).
"""
import argparse
import csv
import re
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from evaluation.gold_check import fact_ok, load_chunks, load_gold

RESULTS_DIR = Path("evaluation/results")


def parse_pages(spec):
    if not spec:
        return None
    pages = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            pages.update(range(int(a), int(b) + 1))
        else:
            pages.add(int(part))
    return pages


def real_answer(text: str) -> bool:
    return len(re.findall(r"[A-Za-zÀ-ÿ]", text)) >= 8


def run_retrieval(g, chunk, search):
    hits = search(g["question"], 5, expand=True)
    ids = [h["id"] for h in hits]
    rank = ids.index(g["chunk_id"]) + 1 if g["chunk_id"] in ids else None
    return rank is not None, f"rang {rank}" if rank else "absent du top-5", "", {}


def run_oracle(g, chunk, build_messages, chat_with_stats):
    hit = {"context": chunk["context"], "text": chunk["text"], "page": chunk["printed_page"], "score": 1.0}
    text, stats = chat_with_stats(build_messages(g["question"], [hit], "fr"), temperature=0.0)
    ok = fact_ok(g["fact_regex"], text) and real_answer(text)
    return ok, "fait present" if ok else "fait ABSENT", text, stats


def run_e2e(g, chunk, answer):
    text, hits = answer(g["question"])
    ids = [h["id"] for h in hits]
    ok = fact_ok(g["fact_regex"], text) and real_answer(text)
    detail = ("fait present" if ok else "fait ABSENT") + ("; chunk cible recupere" if g["chunk_id"] in ids else "; chunk cible NON recupere")
    return ok, detail, text, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["retrieval", "oracle", "e2e"], required=True)
    ap.add_argument("--pages", default="", help="ex: 10-12 ou 10,11,13")
    args = ap.parse_args()

    pages = parse_pages(args.pages)
    chunks = load_chunks()
    gold = [g for g in load_gold() if pages is None or int(g["page"]) in pages]
    if not gold:
        raise SystemExit("Aucune question pour ces pages.")

    if args.mode == "retrieval":
        from src.retrieval.search import search
    elif args.mode == "oracle":
        from src.app.ask import build_messages
        from src.common.rag_common import chat_with_stats
    else:
        from src.app.ask import answer

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"coverage_{args.mode}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    per_page = defaultdict(lambda: [0, 0])
    rows, times, t0 = [], [], time.time()
    print(f"Mode {args.mode} | pages {args.pages or 'toutes'} | {len(gold)} questions\n")
    for g in gold:
        chunk = chunks[g["chunk_id"]]
        t1 = time.time()
        if args.mode == "retrieval":
            ok, detail, text, stats = run_retrieval(g, chunk, search)
        elif args.mode == "oracle":
            ok, detail, text, stats = run_oracle(g, chunk, build_messages, chat_with_stats)
        else:
            ok, detail, text, stats = run_e2e(g, chunk, answer)
        secs = time.time() - t1
        times.append(secs)
        p = int(g["page"])
        per_page[p][0] += ok
        per_page[p][1] += 1
        extra = f" | prompt {stats['prompt_tokens']} tok / {stats['prompt_s']:.0f}s, generation {stats['gen_tokens']} tok / {stats['gen_s']:.0f}s" if stats and stats.get("prompt_tokens") else ""
        print(f"[{'OK' if ok else 'ECHEC'}] {g['id']:<7} {detail:<38} ({secs:.0f}s){extra}")
        if not ok and text:
            print("         reponse:", " ".join(text.split())[:180])
        rows.append({"mode": args.mode, "id": g["id"], "chunk_id": g["chunk_id"], "page": p, "ok": int(ok), "detail": detail,
                     "seconds": round(secs, 1), "answer": " ".join(text.split())[:300],
                     "prompt_tokens": stats.get("prompt_tokens", ""), "gen_tokens": stats.get("gen_tokens", "")})
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print("\nPar page imprimee :")
    for p in sorted(per_page):
        ok, n = per_page[p]
        print(f"  p.{p:<3} {ok}/{n}")
    total_ok = sum(v[0] for v in per_page.values())
    times.sort()
    print(f"\nRESULTAT: {total_ok}/{len(gold)}   (temps total {time.time() - t0:.0f}s ; par question : min {times[0]:.0f}s, mediane {times[len(times) // 2]:.0f}s, max {times[-1]:.0f}s)")
    print(f"Detail : {out_path}")


if __name__ == "__main__":
    main()
