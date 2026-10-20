"""Fonctions communes : appel a Ollama pour les embeddings (sans dependance externe)."""
import json
import math
import urllib.error
import urllib.request

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "bge-m3"
CHAT_MODEL = "qwen2.5:3b"
CHROMA_DIR = "data/index/chroma"
COLLECTION = "guide_etudiant"
BATCH = 16


def _post(path: str, payload: dict, timeout: int = 600) -> dict:
    req = urllib.request.Request(
        OLLAMA_URL + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code == 404:
            m = payload.get("model", "?")
            raise SystemExit(f"Modele '{m}' introuvable. Lance: ollama pull {m}\n({body})")
        raise SystemExit(f"Erreur Ollama {e.code}: {body}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Impossible de joindre Ollama ({OLLAMA_URL}): {e.reason}\n"
                         "Ouvre l'application Ollama ou lance 'ollama serve'.")


def normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def embed(texts):
    """Liste de textes -> liste de vecteurs normalises (norme 1)."""
    out = []
    for i in range(0, len(texts), BATCH):
        res = _post("/api/embed", {"model": EMBED_MODEL, "input": texts[i:i + BATCH]})
        out.extend(normalize(v) for v in res["embeddings"])
    return out


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


def chat(messages, model=CHAT_MODEL, temperature=0.1, num_ctx=4096):
    """Appel au SLM local (Ollama /api/chat), sans streaming."""
    res = _post("/api/chat", {
        "model": model, "messages": messages, "stream": False,
        "options": {"temperature": temperature, "num_ctx": num_ctx},
    })
    return res["message"]["content"].strip()
