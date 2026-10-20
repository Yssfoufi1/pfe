# AI_HANDOFF — paste this into a new AI chat (the repo is PRIVATE: a new chat cannot open its URL)

**Project.** Final-year project (EST Fès, Data Engineering): a **fully local RAG assistant** (Ollama + Qwen2.5 3B + bge-m3 + ChromaDB) answering students' questions from the *Guide pratique de l'étudiant 2025-2026*, in EN/FR/AR/Darija (Arabic + Latin script), with citations and, later, "situation-problem" answers (does a student validate a module/year?). Title: *Souveraineté des données et maîtrise des coûts…* Repo: `github.com/Yssfoufi1/pfe` (private). Hardware: Windows laptop, 8 GB RAM, Intel UHD 620 integrated GPU **not used** by Ollama (100% CPU, ≈ 7–8 tokens/s). Use `py`, not `python`.

**Reference document.** `roadmap_PFE_RAG_SLM_alignee_encadrant.docx` (revised per the supervisor). Phases 0–8; tracker = `docs/ROADMAP_TRACKING.md` (do not create another roadmap). The roadmap defers: SQL timetables, change detection, incremental re-indexing, website integration, deployment, multi-user, exhaustive model comparison.

**State (2026-10-18).**
- Audit done (repo cloned and checked by the assistant, no Ollama). Verified: extraction/chunking reproducible (regenerated files identical), 42 chunks, 24/24 fact checks, rules 20/20, Chroma index 42×1024 consistent. Student-verified earlier: retrieval eval (12/12 in 5 language variants **with** a Darija→French lexicon; circular test), `ask` correct on FR/EN examples.
- Phase status: 0 done · 1 done · 2 partial (no provenance manifest; 3 pages transcribed by hand) · 3 partial (**no abstention**: `MIN_SCORE=0.0`) · 4 **not done** · 5 partial (guide only; no official regulation) · 6 partial (SLM alone 4/11 and 0/3 intermediate verdicts; rules in code OK) · 7–8 not started.
- Incident handled: the repo was public and tracked phone numbers of students; it is now private, sensitive/generated files are untracked (`.gitignore`), **history still contains them** (commit `700574c`; decision D17).
- Repository reorganised into the roadmap's tree (decision D16): `src/{common,ingest,retrieval,app,experimental}`, `tests/`, `evaluation/`, `docs/`, `documents/`, `data/{extracted,chunks,index,resources}`. **Proposed by the assistant; ask the student whether it is applied locally and whether the offline checks pass on his machine.**
- Sandbox-only, untested, not in the repo: `situation_pipeline.py` (SLM extracts notes → `rules.py` decides), `json_mode` in `chat()`, verdict-parser fix in `test_situations.py`.

**Blockers / open.** Supervisor answers pending (19 questions in the progress report; key: Q1 official texts, Q3 personal data, Q4–Q7 grading rules, Q8 Darija output, Q12 independent test set, Q14 hybrid approach). Darija generation is frozen (D18, to validate).

**Next exact step.** (1) Student applies the reorganisation locally and pastes the output of `py -m tests.check_chunks`, `py -m tests.check_structured_data`, `py -m tests.test_rules`. (2) Then roadmap **Phase 4**: create `evaluation/` with answerable / ambiguous / out-of-corpus questions + a no-retrieval baseline, calibrate `MIN_SCORE` (abstention), measure latency and memory.

**Key commands** (repo root): `py -m src.ingest.extract_pages` · `py -m src.ingest.chunk_pages` · `py -m src.retrieval.index_chunks` · `py -m src.app.ask "question" --debug` · `py -m evaluation.eval_retrieval` · `py -m tests.test_rules`. Full list: `docs/ai_memory/AI_CONTEXT.md` §8.

**Constraints/decisions.** Cite the printed page (PDF page − 1). Never alter numbers from the context. Flag ambiguous grading cases (jury) instead of deciding. Local only. No personal data, source PDFs or indexes in Git. No fine-tuning on this hardware.

**How we work.** The student uses a normal AI chat and copies code manually; he writes in Darija Arabizi mixed with French/English and wants answers in Darija Arabizi (Latin letters only), step by step, with code verified before sharing and complete copy-paste-ready files.

**Instructions for the next AI**
1. Read `docs/ROADMAP_TRACKING.md`, `AI_CONTEXT.md`, `PROGRESS.md`, `DECISIONS.md`, `AI_INSTRUCTIONS.md` first; inspect source files when available.
2. Do not repeat completed work; never assume a suggested change was applied — ask which version he has.
3. Ask him to run commands only when needed; give exact paths and add/replace/remove instructions.
4. Preserve working behaviour; no unnecessary rewrites; verify before choosing the next task.
5. Distinguish proposed / applied / verified; never claim an unexecuted command was run.
6. At the end of a session update the docs (`AI_INSTRUCTIONS.md`).
