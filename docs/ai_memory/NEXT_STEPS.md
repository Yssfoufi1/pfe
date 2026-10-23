# NEXT_STEPS — immediate actions only (updated 2026-10-22)

The **single roadmap tracker** is `docs/ROADMAP_TRACKING.md` (aligned with `roadmap_PFE_RAG_SLM_alignee_encadrant.docx`). This file only lists the next actions and must not grow into a second roadmap.
Done and verified: reorganisation (commit `9ba1cd5`); `ask` regression fixed (D19) — answer correct, smoke test 8/9 (the failure was a test regex, fixed).

## 1. Roadmap Phase 4 — validate the generic RAG, chunk by chunk, in batches (D20)
- **Task:** batch 1 = printed pages 10–12 (8 chunks, 22 gold questions). The student reviews the questions (wording, facts), then runs `py -m evaluation.gold_check` (offline), then `py -m evaluation.run_coverage --mode retrieval --pages 10-12`, `--mode oracle`, `--mode e2e`, and pastes the full outputs. Move to the next batch only when the previous one is understood: pages 13–18, then 2–6, then clubs/contacts; image pages (7–9) are covered by the structured-data checks.
- **Why:** current evaluation covers ≈ 8/42 chunks and is circular; the three modes tell whether a failure comes from retrieval, from reading the passage, or from the prompt; roadmap Phase 4 requires validation before specialisation.
- **Prerequisites:** reorganisation and `ask` fix done and verified; Ollama running; close VS Code/Chrome before long runs (RAM pressure doubled the latency).
- **Files:** `evaluation/gold/guide_questions.csv`, `evaluation/gold_check.py`, `evaluation/run_coverage.py`, `src/common/rag_common.py` (`chat_with_stats`).
- **Expected result:** per-page table of OK/ECHEC per mode, CSV in `evaluation/results/` (not versioned), prompt vs generation token counts in oracle mode.
- **Verify:** `gold_check` says "coherent"; student's outputs; interpret: retrieval OK + oracle ECHEC = reading problem; retrieval ECHEC + oracle OK = retrieval problem; both OK + e2e ECHEC = prompt/context problem.
- **After the batches:** out-of-corpus and ambiguous questions, no-retrieval baseline, calibration of `MIN_SCORE` (abstention), latency/RAM report.

## 2. Groundwork after supervisor answers
Provenance manifest in `documents/README.md`; obtain the official regulation; decide SLM-only vs hybrid for situation-problems before integrating `situation_pipeline.py`.

## Waiting on
Supervisor answers (Q1, Q3, Q4–Q8, Q12, Q14). Student validation of D18 (freeze Darija output) and of the hybrid approach. Optional: recreate the repo to purge history (D17).
