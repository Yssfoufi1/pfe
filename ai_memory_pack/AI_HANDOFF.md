# AI_HANDOFF — paste this (plus the GitHub URL) into a new AI chat

**Project.** Final-year project (EST Fès, Data Engineering): a **fully local RAG assistant** (Ollama + Qwen2.5 3B + bge-m3 + ChromaDB) answering students' questions from the *Guide pratique de l'étudiant 2025-2026*, in EN/FR/AR/Darija (Arabic + Latin script), with citations and, ultimately, "situation-problem" answers (does the student validate a module/year?). Title: *Souveraineté des données et maîtrise des coûts…* Hardware: Windows laptop, 8 GB RAM, no GPU; use `py`, not `python`.

**State (2026-10-14).**
- [VERIFIED by the student's outputs] extraction, chunking (42 chunks, 24/24 checks), index, retrieval (12/12 top-1 in 5 language variants **with** a Darija→French lexicon; 8/12 and 6/12 without — optimistic, non-independent test), `ask.py` correct on FR and EN examples, `rules.py` 20/20.
- [VERIFIED, negative] Qwen alone on situations: 4/11 (rules given) / 8/11 (biased); never outputs the intermediate verdicts (rattrapage, jury). Atlas-Chat-2B Darija: fluent but unfaithful (infirmerie→pharmacie). Arabizi questions are currently answered in French.
- [SANDBOX-ONLY, untested, not delivered] `situation_pipeline.py` (Qwen→JSON→`rules.py`→template), `json_mode` in `rag_common.chat()`, parser fix in `test_situations.py`.

**Unfinished.** Hybrid pipeline verification; independent test set; refusal-threshold calibration; timetable/update pipeline; UI/deployment; report. Supervisor answers pending (19 questions).

**Blockers.** Darija *output* quality (needs supervisor decision: answer in Darija or only understand it); ambiguous grading rules in the guide (no official regulation yet).

**Next exact step.** Test `situation_pipeline.py` with fake models, write `test_hybrid.py` (~15 FR + Arabizi situations, ground truth from `rules.py`), deliver the 4 files, then ask the student to run `py test_hybrid.py` and paste the full output.

**Key paths/commands** (`C:\Users\PC\pfe`): `py ask.py "question" --debug` · `py eval_retrieval.py` · `py test_rules.py` · `py test_situations.py [--pipeline]` · data in `data\` · Chroma collection `guide_etudiant` in `data\chroma`.

**Constraints/decisions.** Cite the printed page (PDF page − 1). Never alter numbers from the context. Ambiguous grading cases must be flagged, not decided. Do not fine-tune on this hardware. Do not commit `clubs.csv` (student phone numbers) or the PDF to a public repo.

**How we work.** The student uses a normal AI chat and copies code manually; he writes in Darija Arabizi mixed with French/English and wants answers in Darija Arabizi (Latin script only), step by step, with code verified before sharing and complete copy-paste-ready files.

**Instructions for the next AI**
1. Read `AI_CONTEXT.md`, `PROGRESS.md`, `NEXT_STEPS.md`, `DECISIONS.md`, `AI_INSTRUCTIONS.md` before proposing anything; inspect source files when available.
2. Do not repeat completed work; do not assume a suggested file was applied — ask the student which version of a file he has (e.g. whether `rag_common.py` has `json_mode`).
3. Ask him to run commands/paste output only when necessary; give the exact file path and whether to add, replace or remove.
4. Preserve existing behaviour; no unnecessary rewrites; verify the current implementation before choosing the next task.
5. Distinguish *proposed / applied / verified*; never claim code was executed or pushed without evidence.
6. At the end of a session, update the docs (see `AI_INSTRUCTIONS.md`).
