"""Evalue la recherche (sans LLM) en 5 variantes de langue.
Les MEMES 12 questions (memes faits attendus) sont posees dans chaque variante,
donc les resultats par langue sont comparables.
Un chunk est 'bon' s'il contient le texte attendu."""
import json
from pathlib import Path

from src.retrieval.query_rewrite import expand_query
from src.retrieval.search import search

LANGS = ["FR", "EN", "AR", "DAR_AR", "DAR_LAT"]   # AR = arabe standard, DAR_AR = darija en lettres arabes, DAR_LAT = arabizi
K = 5

# (texte attendu dans le chunk, {langue: question})
QUESTIONS = [
    ("Code Massar", {
        "FR": "Quelles pièces faut-il fournir pour l'inscription administrative ?",
        "EN": "Which documents do I need to submit for administrative registration?",
        "AR": "ما هي الوثائق المطلوبة للتسجيل الإداري؟",
        "DAR_AR": "شنو هي الوراق لي خاصني نجيب باش نسجل؟",
        "DAR_LAT": "chno hiya l-wra9 li khassni njib bach nsjjel ?"}),
    ("1 140,00 DH", {
        "FR": "Quel est le loyer annuel de l'internat ?",
        "EN": "How much is the yearly rent for the dormitory?",
        "AR": "كم هو الإيجار السنوي للداخلية؟",
        "DAR_AR": "شحال كيخلص الطالب فالداخلية فالعام؟",
        "DAR_LAT": "ch7al kaykhles talib f l-dakhiliya f l-3am ?"}),
    ("9h00 à 16h00", {
        "FR": "Quels sont les horaires d'ouverture de la bibliothèque ?",
        "EN": "What are the library opening hours?",
        "AR": "ما هي أوقات عمل المكتبة؟",
        "DAR_AR": "فوقاش كتحل المكتبة؟",
        "DAR_LAT": "imta kat7ell l-maktaba ?"}),
    ("5 ouvrages maximum", {
        "FR": "Combien de livres peut-on emprunter à la bibliothèque ?",
        "EN": "How many books can I borrow from the library?",
        "AR": "كم عدد الكتب التي يمكن استعارتها من المكتبة؟",
        "DAR_AR": "شحال من كتاب نقدر نستلف من المكتبة؟",
        "DAR_LAT": "ch7al mn ktab nqder nstelef mn l-maktaba ?"}),
    ("120 crédits", {
        "FR": "Combien de crédits faut-il pour obtenir le DUT ?",
        "EN": "How many credits are required to get the DUT diploma?",
        "AR": "كم عدد الأرصدة (crédits) اللازمة للحصول على DUT؟",
        "DAR_AR": "شحال من كريدي خاصني نجمع باش ناخد DUT؟",
        "DAR_LAT": "ch7al mn credit khass nakhd bach nakhd DUT ?"}),
    ("en dessous de 5", {
        "FR": "Dans quels cas un module est-il validé ?",
        "EN": "When is a module considered validated?",
        "AR": "في أي حالة تعتبر الوحدة (module) مصادقا عليها؟",
        "DAR_AR": "شنو خاصني باش نفاليدي الموديل؟",
        "DAR_LAT": "chno khassni bach nvalidi l-module ?"}),
    ("48 heures", {
        "FR": "Dans quel délai faut-il justifier une absence à un contrôle ?",
        "EN": "Within what time must I justify an absence from an exam?",
        "AR": "ما هي المدة المسموح بها لتبرير الغياب عن امتحان؟",
        "DAR_AR": "شحال عندي من وقت باش نبرر الغياب فالكونترول؟",
        "DAR_LAT": "ch7al 3ndi men w9t bach nbrrer l-ghiyab f l-contrôle ?"}),
    ("moins de 30 ans", {
        "FR": "Quelles sont les conditions d'éligibilité à l'AMO ?",
        "EN": "What are the eligibility conditions for the AMO health insurance?",
        "AR": "ما هي شروط الاستفادة من التأمين الإجباري عن المرض (AMO)؟",
        "DAR_AR": "شنو هوما الشروط باش نستافد من AMO؟",
        "DAR_LAT": "chno homa chrout bach nstafed mn AMO ?"}),
    ("KAOUTAR HANDOUZ", {
        "FR": "Qui est le président du club NEXUS ?",
        "EN": "Who is the president of the NEXUS club?",
        "AR": "من هو رئيس نادي NEXUS؟",
        "DAR_AR": "شكون هو رئيس كلوب NEXUS؟",
        "DAR_LAT": "chkoun ra2is club NEXUS ?"}),
    ("10h00 à 16h00", {
        "FR": "Quels sont les horaires de l'infirmerie ?",
        "EN": "What are the infirmary opening hours?",
        "AR": "ما هي أوقات عمل المستوصف (infirmerie)؟",
        "DAR_AR": "فوقاش كتحل لانفيرميري؟",
        "DAR_LAT": "fuqash kat7ell linfirmerie ?"}),
    ("sept jours ouvrables", {
        "FR": "Combien de jours ai-je pour consulter ma copie d'examen ?",
        "EN": "How many days do I have to see my exam paper after the results?",
        "AR": "كم يوما لدي لمراجعة ورقة امتحاني بعد إعلان النتائج؟",
        "DAR_AR": "شحال من نهار عندي باش نشوف الكوبي ديالي؟",
        "DAR_LAT": "ch7al mn nhar 3ndi bach nchouf copie dyali ?"}),
    ("en dehors de la ville de Fès", {
        "FR": "Puis-je loger à l'internat si j'habite à Fès ?",
        "EN": "Can I live in the dormitory if I live in Fez?",
        "AR": "هل يمكنني السكن في الداخلية إذا كنت أقيم في فاس؟",
        "DAR_AR": "واش نقدر ندخل للداخلية إلا كنت ساكن فاس؟",
        "DAR_LAT": "wach nqder ndkhol l-dakhiliya ila kont sakn f Fès ?"}),
]


def norm(s):
    return " ".join(s.split())


def rank_of(expected, hits):
    return next((i for i, h in enumerate(hits, 1) if norm(expected) in norm(h["text"])), None)


def tally(stats, lang, rank):
    s = stats[lang]
    s["n"] += 1
    s["r1"] += rank == 1
    s["r3"] += rank is not None and rank <= 3
    s["r5"] += rank is not None


def main():
    corpus = [norm(json.loads(l)["text"]) for l in Path("data/chunks/chunks.jsonl").open(encoding="utf-8")]
    for expected, _ in QUESTIONS:
        if not any(norm(expected) in c for c in corpus):
            print(f"ATTENTION: texte attendu introuvable dans le corpus: {expected!r}")

    new = lambda: {lang: {"n": 0, "r1": 0, "r3": 0, "r5": 0} for lang in LANGS}
    base_stats, exp_stats = new(), new()
    base_ranks, exp_ranks = {}, {}
    for qi, (expected, variants) in enumerate(QUESTIONS, 1):
        for lang in LANGS:
            q = variants[lang]
            rb = rank_of(expected, search(q, K))
            # si l'expansion ne change rien, inutile de refaire la recherche
            rx = rank_of(expected, search(q, K, expand=True)) if expand_query(q)[1] else rb
            base_ranks[(qi, lang)], exp_ranks[(qi, lang)] = rb, rx
            tally(base_stats, lang, rb)
            tally(exp_stats, lang, rx)

    print("\nRang du bon chunk, AVEC expansion (- = absent du top-5); entre parentheses: rang sans expansion")
    print(f"{'Q':<3}" + "".join(f"{l:<12}" for l in LANGS) + "fait attendu")
    for qi, (expected, _) in enumerate(QUESTIONS, 1):
        cells = ""
        for l in LANGS:
            rb, rx = base_ranks[(qi, l)] or "-", exp_ranks[(qi, l)] or "-"
            cells += f"{(str(rx) if rb == rx else f'{rx} ({rb})'):<12}"
        print(f"{qi:<3}{cells}{expected}")

    print("\nRESULTATS par langue: sans expansion -> avec expansion")
    for lang in LANGS:
        b, x, n = base_stats[lang], exp_stats[lang], base_stats[lang]["n"]
        print(f"  {lang:<8} top-1: {b['r1']:>2} -> {x['r1']:>2}/{n}   top-3: {b['r3']:>2} -> {x['r3']:>2}/{n}   top-5: {b['r5']:>2} -> {x['r5']:>2}/{n}")

    print("\nQuestions ratees avec expansion (hors top-5):")
    missed = [(qi, l) for (qi, l), r in exp_ranks.items() if r is None]
    for qi, l in missed:
        print(f"  [{l}] {QUESTIONS[qi - 1][1][l]}")
    if not missed:
        print("  aucune")


if __name__ == "__main__":
    main()
