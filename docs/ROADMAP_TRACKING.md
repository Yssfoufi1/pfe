# ROADMAP_TRACKING — suivi aligné sur `roadmap_PFE_RAG_SLM_alignee_encadrant.docx`

Ce fichier **suit** la roadmap Word de référence (il ne la remplace pas et n'en est pas une seconde version). Dernière mise à jour : 2026-10-22.
Preuves : **[V-élève]** = sortie collée par l'étudiant · **[V-sandbox]** = vérifié par l'assistant sur une copie du dépôt (sans Ollama) · **[non vérifié]**.

## Phases
| Phase | Critère de sortie (roadmap) | État réel | Preuves | Statut |
|---|---|---|---|---|
| 0 Audit | État des lieux vérifiable | Audit fait le 2026-10-18 ; dépôt repassé en privé ; arborescence réorganisée selon la roadmap (§9) | [V-sandbox] reproductibilité, tests hors ligne | **Fait** : réorganisation appliquée et poussée par l'étudiant (commit `9ba1cd5`, 2026-10-19) |
| 1 Assistant local | Assistant local + instructions reproductibles | Ollama + Qwen2.5 3B fonctionnent : 6,68 puis 8,06 tokens/s, 100 % CPU, 2,2 Go, contexte 4096. README + `requirements.txt` ajoutés | [V-élève] `ollama run --verbose`, `ollama ps` | **Fait** (RAM totale utilisée non mesurée) |
| 2 Ingestion | Pipeline reproductible, passages traçables | `src/ingest` : 21 pages, décalage page imprimée = page PDF − 1, 42 passages avec page/section ; 3 pages-images transcrites **à la main** (pas d'OCR) ; **pas de manifeste** de provenance | [V-élève] sorties ; [V-sandbox] régénération identique, 24/24 | **Partiel** |
| 3 RAG | Question → recherche → génération → sources | Index 42×1024 ; `search` et `ask` avec sources ; **abstention absente** (`MIN_SCORE = 0.0`) ; questions en arabizi répondues en français | [V-élève] sorties `ask` (FR, EN corrects ; arabizi incohérent avant correctif) ; [V-sandbox] index cohérent | **Partiel** — régression du 2026-10-19 (`ask` répondait « (18) » à cause d'une ligne « Rappel » du prompt) **corrigée et vérifiée** : `ask` répond « 1 140,00 DH » ; `smoke_generation` 8/9 (échec = regex trop stricte sur « 1,140 DH », corrigée) |
| 4 Évaluation RAG générique | Rapport de validation initiale | Seulement l'éval de recherche 12×5 langues (**circulaire**) + 3 essais de génération. Manquent : questions ambiguës / hors corpus, fidélité, citations, latence et mémoire systématiques, comparaison sans recherche | [V-élève] tableaux d'éval | **En cours** — méthode : validation du guide chunk par chunk, par lots (D20) ; lot 1 (pages 10–12, 22 questions) rédigé et vérifié hors ligne, **pas encore exécuté** |
| 5 Corpus universitaire | Corpus documenté | Guide 2025-2026 uniquement (résumé, erreurs relevées). **Règlement d'évaluation et cahier des normes absents** | — | **Partiel** |
| 6 Questions factuelles + cas pédagogiques | Assistant évalué | `src/app/rules.py` (règles du guide p. 11) 20/20. SLM seul : 4/11 (règles fournies), 8/11 (biaisé) ; 0/3 verdicts intermédiaires. Réponses attendues tirées du **guide**, pas de textes officiels | [V-élève] `test_rules`, `test_situations` ; [V-sandbox] 20/20 | **Partiel** |
| 7 Interface | Prototype démontrable | CLI uniquement | — | **Non commencé** |
| 8 Évaluation finale + doc | Rapport reproductible | README, requirements, ce suivi créés ; rapport final non commencé | — | **Non commencé** |

## Écarts par rapport à la roadmap
1. Dépôt initialement public avec données personnelles (numéros d'étudiants) → passé en privé ; fichiers sensibles retirés du suivi (`.gitignore`). **L'historique Git contient encore ces fichiers** (commit `700574c`) : décision en attente (voir `DECISIONS.md` D17).
2. Travail sur la génération en darija (Atlas-Chat) hors priorités de la roadmap → dossier `src/experimental/`, gelé (D18, à valider).
3. Phase 4 (validation du RAG générique) non réalisée avant la spécialisation.
4. Fonctionnalités différées par la roadmap : non développées (module SQL emplois du temps, détection des modifications, réindexation incrémentale, intégration au site, déploiement, multi-utilisateurs, comparaison exhaustive de modèles). Le calendrier et les filières sont des données structurées versionnées, pas un module.
5. `situation_pipeline.py` (extraction par SLM → règles) existe seulement dans le bac à sable de l'assistant : non intégré, non testé.

## Prochaines actions (ordre)
1. Phase 4, lot 1 : l'étudiant relit `evaluation/gold/guide_questions.csv`, puis `py -m evaluation.gold_check` et `py -m evaluation.run_coverage --mode retrieval|oracle|e2e --pages 10-12` ; ensuite lots suivants (pages 13–18, 2–6, clubs), puis questions ambiguës / hors corpus, comparaison sans recherche, calibrage de `MIN_SCORE`, latence et mémoire.
2. **Phase 4** : créer `evaluation/` avec un jeu de questions répondables / ambiguës / hors corpus, comparaison sans recherche, calibrage de `MIN_SCORE` (abstention), mesures de latence et de mémoire.
3. Compléter `documents/README.md` (provenance, date de récupération) et obtenir les textes officiels (question au superviseur).
4. Trancher l'approche des situations-problèmes (SLM seul vs hybride) avec le superviseur avant d'intégrer du code.

## Journal des vérifications (2026-10-18, assistant, copie du dépôt)
Compilation de 19 fichiers ; `test_rules` 20/20 ; `check_structured_data` cohérent ; `check_chunks` 24/24 ; pages/clubs/chunks régénérés depuis le PDF = fichiers committés ; index Chroma commité = 42 éléments, 1024 dimensions, mêmes identifiants. Non exécutés (Ollama absent) : `test_embed`, `index_chunks`, `search`, `ask`, `eval_retrieval`, `test_situations`, tests darija ; câblage vérifié seulement avec un serveur Ollama simulé.

## Journal des vérifications (2026-10-19, étudiant)
Réorganisation appliquée sur sa machine (dossier `pfe_v2`) : `check_chunks` 24/24 ; `check_structured_data` cohérent (écart DBT 9,9 vs 12 semaines = anomalie du guide) ; `test_rules` 20/20 ; index reconstruit : 42 vecteurs de 1024 dimensions en 93,4 s ; `git status` : renommages et suppressions attendues, aucun PDF / pages / clubs / chunks / index suivi ; `git push` réussi (`733b52b..9ba1cd5`). **`ask` : réponse « (18) » au lieu de « 1 140,00 DH »** (régression due au prompt, D19). Renommage du dossier `pfe` → `pfe_old` refusé (« Access denied » : dossier ouvert par un autre programme) : sans conséquence, le travail continue dans `pfe_v2`.

## Journal des vérifications (2026-10-19, étudiant, après le correctif D19)
`ask` sur « Quel est le loyer annuel de l'internat ? » : « …est de 1 140,00 DH », puis « Sources consultées » (p. 17, p. 18). `py -m evaluation.smoke_generation` : 8/9 en 391 s (≈ 43 s par question, bien plus que ≈ 12 s pour un appel direct à Qwen : à examiner, possible échange de modèles bge-m3 / Qwen en mémoire). Le cas en échec (« The yearly rent … is 1,140 DH. ») est un faux négatif du test (expression régulière), pas une erreur du modèle ; le modèle a toutefois reformaté « 1 140,00 DH » en « 1,140 DH » (règle 3 : ne pas modifier un chiffre).

## Journal des vérifications (2026-10-22, étudiant, latence)
Après avoir fermé VS Code : ancien test de fumée 8/9 en 161 s (391 s avec VS Code ouvert) ; `ollama ps` : `qwen2.5:3b` (2,2 Go) et `bge-m3` (1,2 Go) chargés **en même temps**, 100 % CPU : l'hypothèse « échange de modèles » est écartée, la lenteur venait de la pression sur la RAM. Nouveau test de fumée (seul Ollama lancé) : **9/9**, 254 s au total, par question min 8 s, médiane 22 s, max 57 s (forte variance non expliquée ; le mode `oracle` mesure désormais tokens du prompt et de la génération).
