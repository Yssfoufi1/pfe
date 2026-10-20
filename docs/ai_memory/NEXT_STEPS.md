# NEXT_STEPS — immediate actions only (updated 2026-10-18)

The **single roadmap tracker** is `docs/ROADMAP_TRACKING.md` (aligned with `roadmap_PFE_RAG_SLM_alignee_encadrant.docx`). This file only lists the next actions and must not grow into a second roadmap.

## 1. Apply and verify the reorganisation (Phase 0 closure)
- **Task:** the student applies the new tree in his local repo (see the migration steps given in chat), regenerates the data and runs the offline checks.
- **Why:** commands, imports and `.gitignore` now assume the new layout; old flat commands (`py ask.py`) no longer exist after the move.
- **Prerequisites:** backup of the local folder; the PDF kept and placed in `documents/`.
- **Files:** whole tree; `README.md`, `.gitignore`, `requirements.txt`.
- **Expected result:** `git status` shows renames and removals of the sensitive files, none of `documents/*.pdf`, `data/extracted/pages.jsonl`, `data/extracted/clubs.csv`, `data/chunks/`, `data/index/` is tracked.
- **Verify:** `py -m tests.check_chunks` → 24/24 · `py -m tests.check_structured_data` → coherent · `py -m tests.test_rules` → 20/20 · `py -m src.retrieval.index_chunks` → 42 chunks; then paste the outputs.

## 2. Roadmap Phase 4 — validate the generic RAG
- **Task:** create `evaluation/` question sets: answerable, ambiguous, out-of-corpus; a no-retrieval baseline; calibrate `MIN_SCORE` for abstention; record latency and memory.
- **Why:** required before specialisation; without abstention the assistant answers every question (without context Qwen invented "RAG = Requiring Augmented Guidance").
- **Prerequisites:** task 1; Ollama running with `qwen2.5:3b` and `bge-m3`.
- **Files:** `evaluation/`, `src/app/ask.py` (`MIN_SCORE`), `docs/ROADMAP_TRACKING.md`.
- **Expected result:** a validation report table (correct / wrong / refused; sources; latency; RAM) and a documented abstention rule.
- **Verify:** the student runs the evaluation script and pastes the full output; compare with the baseline.

## 3. Roadmap Phase 5/6 groundwork (after supervisor answers)
Provenance manifest in `documents/README.md`; obtain the official regulation; decide SLM-only vs hybrid for situation-problems before integrating `situation_pipeline.py`.

## Waiting on
Supervisor answers (Q1, Q3, Q4–Q8, Q12, Q14). Student validation of D18 (freeze Darija output) and of the hybrid approach. Optional: decide whether to recreate the repo to purge history (D17).
