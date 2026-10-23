"""Etape 5 : assistant complet (recherche + SLM local).
Usage:  py -m src.app.ask "ta question"      ou      py -m src.app.ask   (mode interactif)
Options: --debug (affiche le prompt et les scores)"""
import sys

from src.app.lang_detect import detect_variant
from src.retrieval.query_rewrite import expand_query
from src.common.rag_common import CHAT_MODEL, chat
from src.retrieval.search import search

TOP_K = 3
MIN_SCORE = 0.0       # seuil absolu de pertinence: desactive pour l'instant (a calibrer avec des questions hors sujet)
REL_MARGIN = 0.12     # on ne garde que les chunks dont le score est a moins de 0.12 du meilleur
# Qwen 2.5 3B ecrit mal l'arabizi (test du 11/10): en attendant un modele darija, on repond en francais
DARIJA_LATIN_ANSWER_IN = "fr"

SYSTEM_PROMPT = """Tu es l'assistant de l'EST Fès (École Supérieure de Technologie de Fès). \
Tu aides les étudiants avec les informations du Guide de l'étudiant 2025-2026.

Règles :
1. Réponds UNIQUEMENT à partir du CONTEXTE fourni. N'utilise aucune autre connaissance.
2. Si le contexte ne contient pas la réponse, dis-le clairement et conseille de contacter le service concerné (scolarité, direction pédagogique).
3. Ne modifie jamais un chiffre, une date, un horaire ou un nom du contexte : recopie-les tels quels.
4. Réponds par une ou deux phrases complètes. N'écris aucun numéro de page : les sources sont ajoutées automatiquement après ta réponse.
5. Sois clair et concis.
6. {lang_rule}"""

LANG_RULES = {
    "fr": "Réponds en français.",
    "en": "Answer in English.",
    "ar_script": ("Réponds en arabe simple, en lettres arabes. Garde en lettres latines les sigles, "
                  "noms propres et chiffres du contexte (DUT, AMO, 1 140,00 DH)."),
    "darija_latin": ("Réponds en darija marocaine écrite en lettres latines (arabizi, comme un étudiant "
                     "marocain sur WhatsApp : 3 = ع, 7 = ح, 9 = ق). Phrases courtes. Garde en français "
                     "les termes administratifs, les chiffres et les noms."),
}


def select_hits(hits):
    """Garde le meilleur chunk et ceux dont le score est proche (evite le bruit dans le contexte)."""
    if not hits:
        return []
    best = hits[0]["score"]
    return [h for h in hits if h["score"] >= best - REL_MARGIN]


def build_messages(question: str, hits, variant: str):
    blocks = [f"[Source {i}] {h['context']}\n{h['text']}" for i, h in enumerate(hits, 1)]
    user = ("CONTEXTE :\n\n" + "\n\n".join(blocks)
            + f"\n\nQUESTION : {question}")
    return [
        {"role": "system", "content": SYSTEM_PROMPT.format(lang_rule=LANG_RULES[variant])},
        {"role": "user", "content": user},
    ]


def answer(question: str, debug: bool = False):
    variant = detect_variant(question)
    hits = select_hits(search(question, TOP_K, expand=True))
    if variant == "darija_latin":
        variant = DARIJA_LATIN_ANSWER_IN
    if debug:
        print(f"[langue de reponse: {variant}] [requete: {expand_query(question)[0]}]")
        for h in hits:
            print(f"[score {h['score']:.3f}] p.{h['page']} {h['id']}")
    if not hits or hits[0]["score"] < MIN_SCORE:
        return "Je n'ai pas trouvé cette information dans le Guide de l'étudiant.", hits
    messages = build_messages(question, hits, variant)
    if debug:
        print("\n--- PROMPT ---\n" + messages[0]["content"] + "\n\n" + messages[1]["content"] + "\n--------------\n")
    return chat(messages), hits


def show(question: str, debug: bool):
    text, hits = answer(question, debug)
    print("\n" + text + "\n")
    print("Sources consultées :")
    for h in hits:
        short = h["context"].split(" > ", 1)[-1]
        print(f"  p.{h['page']}  {short}")
    print()


if __name__ == "__main__":
    debug = "--debug" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        show(args[0], debug)
    else:
        print(f"Assistant EST Fès (modèle {CHAT_MODEL}). Tape 'exit' pour quitter.")
        while True:
            q = input("\n> ").strip()
            if q.lower() in ("exit", "quit", ""):
                break
            show(q, debug)
