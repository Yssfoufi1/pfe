# PFE — Assistant conversationnel local (RAG + SLM) pour l'EST Fès

**Sujet :** *Souveraineté des données et maîtrise des coûts : développement d'un assistant conversationnel via une architecture RAG locale et un SLM.*

Prototype 100 % local (aucun appel réseau hors `localhost`) : Ollama + Qwen2.5 3B (génération), bge-m3 (embeddings), ChromaDB (index), sur un portable de 8 Go de RAM, GPU intégré non utilisé par Ollama (100 % CPU, ≈ 7–8 tokens/s). Corpus actuel : le *Guide pratique de l'étudiant 2025-2026*.

Référence de développement : `roadmap_PFE_RAG_SLM_alignee_encadrant.docx`. Suivi des phases, preuves et prochaines actions : [`docs/ROADMAP_TRACKING.md`](docs/ROADMAP_TRACKING.md).

## État réel (2026-10-18)
- **Fonctionne, vérifié :** extraction du PDF, découpage (42 passages, 24/24 faits conservés), index (42 vecteurs de 1024 dimensions), recherche multilingue (FR/EN/AR/darija), assistant `ask` avec sources, règles de validation du guide codées (20/20).
- **Pas encore fait :** évaluation du RAG générique (questions ambiguës / hors corpus, fidélité), seuil de refus (abstention), textes officiels (règlement d'évaluation, cahier des normes), interface.
- **Résultats à interpréter avec prudence :** l'évaluation de la recherche est circulaire (lexique darija construit après observation des échecs). Le SLM seul résout mal les situations-problèmes (voir `docs/ROADMAP_TRACKING.md`).

## Structure
```
documents/     documents sources (non versionnés)         src/common/      client Ollama (embed, chat)
data/extracted textes extraits + données structurées       src/ingest/      extraction, nettoyage, découpage
data/chunks    passages et métadonnées (non versionnés)    src/retrieval/   index, recherche, expansion darija
data/index     index Chroma local (non versionné)          src/app/         assistant (ask), langue, règles du guide
data/resources lexique darija→français, glossaire          src/experimental/ essais darija (Atlas-Chat), gelés
tests/         vérifications       evaluation/ évaluation de la recherche       docs/ suivi, décisions, mémoire IA
```

## Installation (Windows, PowerShell, depuis la racine du dépôt)
```powershell
py -m pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama pull bge-m3
```
Placer le PDF dans `documents\guide_etudiant_2025_2026.pdf` (voir `documents/README.md`). Toujours utiliser `py` (et non `python`) et lancer les commandes depuis la racine.

## Exécution, dans l'ordre
```powershell
# 1) ingestion (hors ligne)
py -m src.ingest.extract_pages
py -m src.ingest.extract_clubs
py -m src.ingest.chunk_pages
# 2) vérifications hors ligne
py -m tests.check_chunks            # attendu : 24/24 faits intacts
py -m tests.check_structured_data   # attendu : tout est coherent
py -m tests.test_rules              # attendu : 20/20
# 3) index et recherche (Ollama doit tourner)
py -m tests.test_embed
py -m src.retrieval.index_chunks
py -m src.retrieval.search "Quel est le loyer annuel de l'internat ?"
# 4) assistant et évaluation
py -m src.app.ask "Quel est le loyer annuel de l'internat ?" --debug
py -m evaluation.smoke_generation  # la reponse contient-elle le bon fait ? (garde-fou anti-regression)
py -m evaluation.eval_retrieval
py -m evaluation.gold_check                      # hors ligne : faits attendus presents dans leurs chunks + carte de couverture
py -m evaluation.run_coverage --mode retrieval --pages 10-12   # puis --mode oracle, --mode e2e
py -m tests.test_situations         # ajouter --pipeline pour la recherche normale (SLM seul)
```
`data/extracted/calendrier_2025_2026.csv` et `filieres.json` sont versionnés : transcription des pages-images du guide (régénérables avec `py -m src.ingest.build_structured_data`).

## Confidentialité
Le guide publie des numéros de téléphone d'étudiants (présidents de clubs) : `documents/`, `data/extracted/pages.jsonl`, `data/extracted/clubs.csv`, `data/chunks/` et `data/index/` ne sont **pas versionnés** (voir `.gitignore`). Le traitement reste local.

## Documentation
[`docs/ROADMAP_TRACKING.md`](docs/ROADMAP_TRACKING.md) (suivi) · [`docs/DECISIONS.md`](docs/DECISIONS.md) · [`docs/ai_memory/`](docs/ai_memory/) (passation entre assistants IA : commencer par `AI_HANDOFF.md`).
