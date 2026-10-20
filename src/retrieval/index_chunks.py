"""Etape 4 : embeddings des chunks (bge-m3 via Ollama) + stockage dans ChromaDB."""
import json
import time
from pathlib import Path

import chromadb

from src.common.rag_common import CHROMA_DIR, COLLECTION, EMBED_MODEL, embed

CHUNKS_PATH = Path("data/chunks/chunks.jsonl")


def main():
    chunks = [json.loads(l) for l in CHUNKS_PATH.open(encoding="utf-8")]
    # le contexte (document > chapitre > section > page) est ajoute au texte avant l'embedding
    texts = [f"{c['context']}\n{c['text']}" for c in chunks]

    t0 = time.time()
    vectors = embed(texts)
    print(f"{len(vectors)} embeddings ({len(vectors[0])} dimensions) en {time.time() - t0:.1f}s avec {EMBED_MODEL}")

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(COLLECTION)
    col.add(
        ids=[c["id"] for c in chunks],
        embeddings=vectors,
        documents=[c["text"] for c in chunks],
        metadatas=[{
            "printed_page": c["printed_page"] or 0,
            "section": c["section"] or "",
            "subsection": c["subsection"] or "",
            "context": c["context"],
        } for c in chunks],
    )
    print(f"collection '{COLLECTION}': {col.count()} chunks -> {CHROMA_DIR}")


if __name__ == "__main__":
    main()
