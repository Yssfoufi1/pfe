"""Verifie rules.py contre les 6 exemples du guide (page imprimee 11) + cas limites."""
from rules import module_status, weighted_average, year_decision

ok = 0
total = 0


def check(name, got, expected):
    global ok, total
    total += 1
    good = got == expected
    ok += good
    print(f"  {'OK ' if good else 'ECHEC'} {name:<58} -> {got}" + ("" if good else f"   (attendu {expected})"))


print("Exemples de modules du guide:")
check("Informatique 11, Cours 6, TP 16 (guide: Valide)", module_status(11, [6, 16])[0], "VALIDE")
check("Informatique 11, Cours 4, TP 16 (guide: Rattrap)", module_status(11, [4, 16])[0], "RATTRAPAGE")
check("Intro au droit 3, Cours 3 (guide: Non valide, pas de rattrapage)", module_status(3, [3])[0], "NON_VALIDE_SANS_RATTRAPAGE")

print("\nExemples d'annee du guide (notes finales, moyenne annuelle donnee par le guide):")
r1 = year_decision([(11, None), (14, None), (8, None), (10, None), (16, None)], 11.20)
check("Exemple 1: 11,14,8,10,16 / 11,20 (guide: Admis)", r1["decision"], "ADMIS")
check("   module 11 (8,00) = compensation (guide: Par Compensation)", r1["modules"][2][0], "COMPENSABLE")
r2 = year_decision([(8, [4, 12]), (14, None), (6, None), (10, None), (16, None)], 9.60)
check("Exemple 2: 8(4+12),14,6,10,16 / 9,60 (guide: Ajourne)", r2["decision"], "AJOURNE")
r3 = year_decision([(11, None), (14, None), (6, None), (10, None), (16, None)], 10.95)
check("Exemple 3: 11,14,6,10,16 / 10,95 (guide: Admis par derogation ou Ajourne)", r3["decision"], "DEROGATION_POSSIBLE")

print("\nCas limites:")
check("module moyenne 4.00 -> rattrapage", module_status(4.0, [4])[0], "RATTRAPAGE")
check("module moyenne 3.99 -> pas de rattrapage", module_status(3.99, [3.99])[0], "NON_VALIDE_SANS_RATTRAPAGE")
check("module 10 avec un element a 5 pile -> valide", module_status(10, [5, 15])[0], "VALIDE")
check("module 10 avec un element a 4.99 -> rattrapage", module_status(10, [4.99, 15.01])[0], "RATTRAPAGE")
check("apres rattrapage: 7.00 -> compensable", module_status(7.0, [7], True)[0], "COMPENSABLE")
check("apres rattrapage: 6.99 -> non valide", module_status(6.99, [6.99], True)[0], "NON_VALIDE")
check("apres rattrapage: 8 mais element 4 -> non valide", module_status(8, [4, 12], True)[0], "NON_VALIDE")
check("annee: moyenne exactement 10, tous >= 7 -> admis", year_decision([(10, None), (10, None)], 10.0)["decision"], "ADMIS")
check("annee: moyenne 9.99 -> ajourne", year_decision([(10, None), (9.98, None)], 9.99)["decision"], "AJOURNE")
check("annee: 3 modules < 7, moyenne 11 -> ajourne", year_decision([(6, None)] * 3 + [(15, None)] * 3, 11.0)["decision"], "AJOURNE")
check("annee: 2 modules < 7, moyenne 11 -> derogation possible", year_decision([(6, None)] * 2 + [(15, None)] * 3, 11.0)["decision"], "DEROGATION_POSSIBLE")
check("annee: module 8 avec element 4, moyenne 11 -> ambigu", year_decision([(8, [4, 12]), (14, None)], 11.0)["decision"], "AMBIGU")
avg, how = weighted_average([10, 14], [3, 5])
check("moyenne ponderee (10*3+14*5)/8 = 12.5", round(avg, 2), 12.5)

print(f"\nRESULTAT: {ok}/{total}")
print("Remarque: les moyennes annuelles du guide (11,20 / 9,60 / 10,95) ne se recalculent pas a partir des modules affiches:")
print("  la moyenne simple des 5 modules de l'exemple 1 donne", round(sum([11, 14, 8, 10, 16]) / 5, 2), "(le guide en montre 5 sur 14, et les credits different)")
