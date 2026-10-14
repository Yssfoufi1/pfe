"""Detection simple de la variante de langue d'une question (sans modele).
Retourne: 'fr' | 'en' | 'ar_script' (arabe ou darija en lettres arabes) | 'darija_latin' (arabizi)."""
import re

from query_rewrite import expand_query, normalize

_ARABIC = re.compile("[\u0600-\u06ff\u0750-\u077f]")
_ARABIZI_DIGITS = re.compile(r"[a-z][23579]|[23579][a-z]")
_DARIJA_PARTICLES = {"wach", "chno", "chkoun", "imta", "kifach", "3lach", "bach", "dyal", "dyali",
                     "khassni", "bghit", "kayn", "kayna", "fuqash", "fouqach", "ch7al", "chhal"}
_EN = {"the", "what", "how", "is", "are", "can", "do", "does", "i", "my", "to", "for", "of", "when",
       "which", "who", "where", "a", "an", "in", "from", "much", "many", "need", "must", "if", "after"}
_FR = {"le", "la", "les", "un", "une", "des", "du", "de", "quel", "quels", "quelle", "quelles", "est",
       "sont", "que", "qui", "ou", "puis", "je", "mon", "ma", "pour", "dans", "combien", "comment",
       "ai", "faut", "il", "peut", "on", "et", "si", "a"}


def detect_variant(question: str) -> str:
    letters = [c for c in question if c.isalpha()]
    if letters and sum(bool(_ARABIC.match(c)) for c in letters) / len(letters) > 0.3:
        return "ar_script"
    text = normalize(question)
    tokens = re.findall(r"[0-9a-z]+", text)
    if _ARABIZI_DIGITS.search(text) or any(t in _DARIJA_PARTICLES for t in tokens):
        return "darija_latin"
    _, matched = expand_query(question)          # mots darija du lexique (cles latines d'au moins 5 lettres)
    if any(len(k) >= 5 and k.isascii() for k in matched):
        return "darija_latin"
    en = sum(t in _EN for t in tokens)
    fr = sum(t in _FR for t in tokens)
    return "en" if en > fr else "fr"
