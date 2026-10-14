"""Recherche dans l'index: py search.py "ta question" [k] [--base]"""
import sys

import chromadb

from query_rewrite import expand_query
from rag_common import CHROMA_DIR, COLLECTION, embed


def search(question: str, k: int = 5, expand: bool = False):
    if expand:
        question, _ = expand_query(question)
    col = chromadb.PersistentClient(path=CHROMA_DIR).get_collection(COLLECTION)
    qv = embed([question])[0]
    res = col.query(query_embeddings=[qv], n_results=k, include=["documents", "metadatas", "distances"])
    hits = []
    for cid, doc, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]):
        # vecteurs normalises + distance L2 au carre (defaut Chroma): cos = 1 - d/2
        hits.append({"id": cid, "text": doc, "page": meta["printed_page"],
                     "context": meta["context"], "score": 1 - dist / 2})
    return hits


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Usage: py search.py "question" [k]')
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    expand = "--base" not in sys.argv          # par defaut: avec expansion (utiliser --base pour la desactiver)
    q = args[0]
    k = int(args[1]) if len(args) > 1 else 5
    print(f"Question: {q}")
    if expand:
        print(f"Requete etendue: {expand_query(q)[0]}")
    print()
    for i, h in enumerate(search(q, k, expand=expand), 1):
        preview = " ".join(h["text"].split())[:160]
        print(f"{i}. score={h['score']:.3f}  p.{h['page']}  [{h['id']}]\n   {h['context']}\n   {preview}...\n")
