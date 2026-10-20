# ROADMAP_TRACKING — suivi aligné sur `roadmap_PFE_RAG_SLM_alignee_encadrant.docx`

Ce fichier **suit** la roadmap Word de référence (il ne la remplace pas et n'en est pas une seconde version). Dernière mise à jour : 2026-10-18.
Preuves : **[V-élève]** = sortie collée par l'étudiant · **[V-sandbox]** = vérifié par l'assistant sur une copie du dépôt (sans Ollama) · **[non vérifié]**.

## Phases
| Phase | Critère de sortie (roadmap) | État réel | Preuves | Statut |
|---|---|---|---|---|
| 0 Audit | État des lieux vérifiable | Audit fait le 2026-10-18 ; dépôt repassé en privé ; arborescence réorganisée selon la roadmap (§9) | [V-sandbox] reproductibilité, tests hors ligne | **Fait** (réorganisation à appliquer dans le dépôt local) |
| 1 Assistant local | Assistant local + instructions reproductibles | Ollama + Qwen2.5 3B fonctionnent : 6,68 puis 8,06 tokens/s, 100 % CPU, 2,2 Go, contexte 4096. README + `requirements.txt` ajoutés | [V-élève] `ollama run --verbose`, `ollama ps` | **Fait** (RAM totale utilisée non mesurée) |
| 2 Ingestion | Pipeline reproductible, passages traçables | `src/ingest` : 21 pages, décalage page imprimée = page PDF − 1, 42 passages avec page/section ; 3 pages-images transcrites **à la main** (pas d'OCR) ; **pas de manifeste** de provenance | [V-élève] sorties ; [V-sandbox] régénération identique, 24/24 | **Partiel** |
| 3 RAG | Question → recherche → génération → sources | Index 42×1024 ; `search` et `ask` avec sources ; **abstention absente** (`MIN_SCORE = 0.0`) ; questions en arabizi répondues en français | [V-élève] sorties `ask` (FR, EN corrects ; arabizi incohérent avant correctif) ; [V-sandbox] index cohérent | **Partiel** |
| 4 Évaluation RAG générique | Rapport de validation initiale | Seulement l'éval de recherche 12×5 langues (**circulaire**) + 3 essais de génération. Manquent : questions ambiguës / hors corpus, fidélité, citations, latence et mémoire systématiques, comparaison sans recherche | [V-élève] tableaux d'éval | **Non fait** |
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
1. Appliquer la réorganisation dans le dépôt local (voir `AI_HANDOFF.md`), exécuter les commandes du README, vérifier 24/24 · tout est cohérent · 20/20.
2. **Phase 4** : créer `evaluation/` avec un jeu de questions répondables / ambiguës / hors corpus, comparaison sans recherche, calibrage de `MIN_SCORE` (abstention), mesures de latence et de mémoire.
3. Compléter `documents/README.md` (provenance, date de récupération) et obtenir les textes officiels (question au superviseur).
4. Trancher l'approche des situations-problèmes (SLM seul vs hybride) avec le superviseur avant d'intégrer du code.

## Journal des vérifications (2026-10-18, assistant, copie du dépôt)
Compilation de 19 fichiers ; `test_rules` 20/20 ; `check_structured_data` cohérent ; `check_chunks` 24/24 ; pages/clubs/chunks régénérés depuis le PDF = fichiers committés ; index Chroma commité = 42 éléments, 1024 dimensions, mêmes identifiants. Non exécutés (Ollama absent) : `test_embed`, `index_chunks`, `search`, `ask`, `eval_retrieval`, `test_situations`, tests darija ; câblage vérifié seulement avec un serveur Ollama simulé.
