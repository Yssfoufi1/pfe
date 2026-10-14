# NEXT_STEPS — prioritised roadmap (updated 2026-10-14)

## 1. (IMMEDIATE) Verify and deliver the hybrid situation pipeline
- **Task:** test `situation_pipeline.py` (extract → validate → decide via `rules.py` → render), write `test_hybrid.py`, deliver updated `rag_common.py` (with `json_mode`), `situation_pipeline.py`, `test_hybrid.py`, parser-fixed `test_situations.py`.
- **Why:** SLM alone gave 4/11 (oracle) / 8/11 (biased) and never produced the intermediate verdicts (rattrapage, jury) — exactly where students need help.
- **Prerequisites:** `rules.py` ([VERIFIED] 20/20); Ollama + `qwen2.5:3b` running on the student's machine.
- **Files:** `situation_pipeline.py`, `rag_common.py`, `test_hybrid.py` (new), `test_situations.py`, `rules.py`.
- **Expected result:** for ~15 natural-language situations (FR + Arabizi, with and without module average given), report (a) extraction exact-match rate and (b) end-to-end verdict accuracy; invalid JSON → clear "please rephrase" message.
- **Verify:** (i) sandbox with fake models (perfect, malformed JSON, missing fields, out-of-range notes) must trigger the right branches; (ii) student runs `py test_hybrid.py` and pastes the output; compare with the SLM-only numbers.

## 2. Independent test set
- **Task:** collect 30–50 real student questions (FR/EN/AR/Darija, anonymous) + expected source/fact; keep them out of the lexicon/glossary design.
- **Why:** current retrieval results are circular (lexicon built after seeing failures).
- **Depends on:** supervisor's OK (question Q12 in the report) — can start with classmates informally.
- **Files:** new `data/eval_independent.csv`; extend `eval_retrieval.py` to read it.
- **Verify:** report top-1/top-5 per language, with and without expansion.

## 3. Generation evaluation + refusal threshold
- **Task:** score Qwen answers on FR/EN/AR questions (exactness of numbers, page citation, faithfulness); add out-of-scope questions ("recette du tajine", "loyer à Rabat") and calibrate `MIN_SCORE` in `ask.py`.
- **Why:** the assistant must say "not in the guide" instead of inventing.
- **Depends on:** task 2 (partially); `ask.py`.
- **Verify:** table of correct / wrong / refused answers.

## 4. Router information vs situation inside `ask.py`
Only after task 1 results. Detect "situation" questions (notes/moyenne mentioned) → hybrid pipeline; otherwise RAG.

## Later (do not start before the above)
- Regulatory documents once obtained (règlement d'évaluation et délibération, cahier des normes) → re-chunk, re-index, re-run `check_chunks.py` with new facts.
- DODa dataset: student clones the repo and pastes the file list + first 5 lines of the word/sentence CSVs → decide use (transliteration Arabic↔Arabizi, lexicon extension). Check the licence (MIT in the paper vs CC BY-NC in a derived corpus). **Not** for fine-tuning Qwen on this hardware.
- Timetable module (SQLite) + automatic update pipeline (file hash change detection, incremental re-indexing, `année_universitaire` metadata).
- UI (Streamlit/Gradio), Docker, deployment spec for the school server.
- Model/cost comparison (3B vs 7B on external GPU), cloud-vs-local cost table, sovereignty data-flow diagram.
- Optional bonus: small LoRA/transliteration fine-tune on Colab with before/after metrics.
- Report and defence.

## Waiting on others
Supervisor's answers to the 19 questions (esp. Q4–Q8, Q12, Q14). Student: fill names in the PDF, send it, spot-check calendar dates.
