import csv
import json
from collections import defaultdict
from datetime import date

rows = list(csv.DictReader(open("data/extracted/calendrier_2025_2026.csv", encoding="utf-8")))
d = lambda s: date.fromisoformat(s) if s else None
ok = True


def report(msg):
    global ok
    ok = False
    print("  PROBLEME:", msg)


print("1) Semaines de cours: debut lundi / fin samedi (exceptions notees dans 'remarque')")
for r in rows:
    if r["type"] != "semaine_cours":
        continue
    s, e = d(r["date_debut"]), d(r["date_fin"])
    if (s.weekday() != 0 or e.weekday() != 5) and not r["remarque"]:
        report(f"{r['cycle']} {r['semestre']} {r['libelle']}: {s} ({s.strftime('%A')}) -> {e} ({e.strftime('%A')})")
    if s > e:
        report(f"debut > fin: {r['libelle']}")

print("2) Chevauchements dans un meme semestre (stage technique exclu)")
groups = defaultdict(list)
for r in rows:
    if r["cycle"] in ("DUT", "DBT") and r["type"] != "stage_technique":
        groups[(r["cycle"], r["annee"], r["semestre"])].append(r)
for key, items in groups.items():
    items.sort(key=lambda r: r["date_debut"])
    for a, b in zip(items, items[1:]):
        if d(b["date_debut"]) <= d(a["date_fin"]):
            report(f"{key}: {a['libelle']} ({a['date_fin']}) chevauche {b['libelle']} ({b['date_debut']})")

print("3) Nombre de semaines de cours par semestre")
cnt = defaultdict(int)
for r in rows:
    if r["type"] == "semaine_cours":
        cnt[(r["cycle"], r["annee"], r["semestre"])] += 1
for k, v in sorted(cnt.items()):
    print("  ", k, v)

print("4) Duree des stages techniques vs guide (DUT: 8 semaines, DBT: 12 semaines)")
for r in rows:
    if r["type"] == "stage_technique":
        weeks = ((d(r["date_fin"]) - d(r["date_debut"])).days + 1) / 7
        attendu = 8 if r["cycle"] == "DUT" else 12
        flag = "OK" if round(weeks) == attendu else f"ECART (guide: {attendu})"
        print(f"   {r['cycle']}: {weeks:.1f} semaines -> {flag}")
        if flag != "OK" and not r["remarque"]:
            report("ecart non note dans remarque")

print("5) Filieres: totaux vs 'Chiffres cles' (14 DUT, 6 DBT)")
fil = json.load(open("data/extracted/filieres.json", encoding="utf-8"))
tot = defaultdict(int)
for dep in fil["departements"]:
    for f in dep["filieres"]:
        tot[f["diplome"]] += 1
print("  ", dict(tot))
if tot["DUT"] != 14 or tot["DBT"] != 6:
    report("totaux differents du guide")

print("\nRESULTAT:", "tout est coherent" if ok else "des problemes ont ete trouves")
