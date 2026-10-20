"""Regles de validation du Guide de l'etudiant 2025-2026 (page imprimee 11), en code.
Le SLM ne fait pas ces calculs: il comprend la situation de l'etudiant, ce module decide.

Regles (citees du guide):
 - Module valide si moyenne >= 10 ET aucun element constitutif < 5.
 - Module rattrapable si moyenne >= 4. Moyenne < 4 : non valide, pas de rattrapage.
 - Apres rattrapage : non valide (sans compensation) si note finale < 7 OU un element < 5;
   sinon (7 <= note < 10) validation possible par compensation.
 - Annee validee si moyenne generale >= 10 ET aucun module < 7.
 - Derogation possible (chef d'etablissement, sur proposition du jury) pour 2 modules non acquis au maximum.
"""
MODULE_PASS = 10.0
ELEMENT_MIN = 5.0
RATTRAPAGE_MIN = 4.0
COMPENSATION_MIN = 7.0
YEAR_PASS = 10.0
MAX_DEROGATION = 2

REF = "Guide de l'etudiant 2025-2026, p. 11"


def module_status(avg: float, elements=None, after_rattrapage: bool = False):
    """Retourne (statut, explication).
    statut: VALIDE | RATTRAPAGE | NON_VALIDE_SANS_RATTRAPAGE | COMPENSABLE | NON_VALIDE"""
    elements = list(elements or [])
    low_element = [e for e in elements if e < ELEMENT_MIN]
    if avg >= MODULE_PASS and not low_element:
        return "VALIDE", f"moyenne {avg:g} >= 10 et aucun element < 5 ({REF})"
    if not after_rattrapage:
        if avg >= RATTRAPAGE_MIN:
            why = f"element < 5 ({low_element[0]:g})" if low_element and avg >= MODULE_PASS else f"moyenne {avg:g} < 10"
            return "RATTRAPAGE", f"{why}, mais moyenne >= 4: rattrapage possible ({REF})"
        return "NON_VALIDE_SANS_RATTRAPAGE", f"moyenne {avg:g} < 4: pas de rattrapage ({REF})"
    if avg >= COMPENSATION_MIN and not low_element:
        return "COMPENSABLE", f"note finale {avg:g} entre 7 et 10: validation par compensation possible ({REF})"
    why = f"element < 5 ({low_element[0]:g})" if low_element else f"note finale {avg:g} < 7"
    return "NON_VALIDE", f"{why}: pas de compensation ({REF})"


def weighted_average(notes, credits=None):
    """Moyenne generale. Le guide ne dit pas si elle est ponderee par les credits (3 a 5 par module):
    sans credits on fait la moyenne simple et on le signale."""
    if credits:
        total = sum(credits)
        return sum(n * c for n, c in zip(notes, credits)) / total, "ponderee par les credits"
    return sum(notes) / len(notes), "moyenne simple (credits inconnus)"


def year_decision(module_notes, annual_avg: float):
    """module_notes: liste de (moyenne_module, [notes_elements] ou None), notes FINALES (apres rattrapage).
    Retourne dict(decision, reasons, modules).
    decision: ADMIS | AJOURNE | DEROGATION_POSSIBLE | AMBIGU"""
    statuses = [module_status(avg, els, after_rattrapage=True) for avg, els in module_notes]
    below7 = [avg for avg, _ in module_notes if avg < COMPENSATION_MIN]
    blocked_by_element = [s for (avg, _), s in zip(module_notes, statuses)
                          if s[0] == "NON_VALIDE" and avg >= COMPENSATION_MIN]
    reasons = []

    if annual_avg >= YEAR_PASS and not below7:
        if blocked_by_element:
            reasons.append("un module a >= 7 mais un element < 5: le guide dit 'sans compensation' pour le module, "
                           "mais la regle de l'annee ne parle que de la moyenne et des modules < 7")
            return {"decision": "AMBIGU", "reasons": reasons, "modules": statuses}
        reasons.append(f"moyenne generale {annual_avg:g} >= 10 et aucun module < 7 ({REF})")
        return {"decision": "ADMIS", "reasons": reasons, "modules": statuses}

    if annual_avg >= YEAR_PASS and len(below7) <= MAX_DEROGATION:
        reasons.append(f"moyenne generale {annual_avg:g} >= 10 mais {len(below7)} module(s) < 7")
        reasons.append(f"une derogation (max {MAX_DEROGATION} modules) est possible sur proposition du jury: "
                       f"decision non automatique ({REF})")
        return {"decision": "DEROGATION_POSSIBLE", "reasons": reasons, "modules": statuses}

    if annual_avg < YEAR_PASS:
        reasons.append(f"moyenne generale {annual_avg:g} < 10 ({REF})")
    if len(below7) > MAX_DEROGATION:
        reasons.append(f"{len(below7)} modules < 7: plus que le maximum de {MAX_DEROGATION} pour une derogation")
    elif below7:
        reasons.append(f"{len(below7)} module(s) < 7")
    return {"decision": "AJOURNE", "reasons": reasons, "modules": statuses}
