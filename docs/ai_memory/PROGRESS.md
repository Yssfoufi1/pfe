# PROGRESS — latest verified state

**Last update:** 2026-10-22 · **Phase:** Phase 1 — generic RAG on the university corpus (EST Fès student guide) + situation-problem module.
Tags: **[VERIFIED]** student pasted real output · **[SANDBOX]** only checked in the assistant's sandbox with fake/mock models · **[PROPOSED]** no evidence it was applied. No percentage progress is claimed.

## Completed (evidence = outputs pasted by the student)
- PDF page extraction: 21 pages, printed page = PDF page − 1, no mismatches; 3 image-only pages (printed 7, 8, 9) detected. [VERIFIED]
- Clubs table → `clubs.csv` (10 clubs). [VERIFIED]
- Calendar CSV (112 rows) + `filieres.json` (14 DUT + 6 DBT): `check_structured_data.py` → "tout est coherent"; flagged DBT stage 9.9 vs 12 weeks. [VERIFIED] (the transcription itself was done by the assistant from page images; the student was asked to spot-check 5–6 dates against the guide and **has not confirmed doing so**).
- Chunking: 42 chunks (min 112, mean 562, max 1340 chars), 24/24 fact-integrity checks. [VERIFIED]
- bge-m3 via Ollama: 1024 dimensions; 42 embeddings in 110 s; Chroma collection built. [VERIFIED]
- Multilingual retrieval eval (12 questions × 5 variants), **with** Darija→French expansion: 12/12 top-1 in FR, EN, AR, DAR_AR, DAR_LAT. **Without** expansion: FR/EN/AR 12/12; DAR_AR 8/12 top-1 (10/12 top-5); DAR_LAT 6/12 top-1 (7/12 top-5). Caveat: lexicon built after seeing the failures and tested on the same questions → optimistic. [VERIFIED]
- Rules in code (`rules.py`): `test_rules.py` 20/20 (6 guide examples + 14 edge cases). [VERIFIED]
- Progress report PDF for the supervisor (placeholders `[NOM]`, `[Nom de l'encadrant]` still to fill; its date says 13 Oct 2026 — should be corrected). Delivered; **not confirmed sent**.

## Tests and actual results (latest)
| Test | Result |
|---|---|
| `ask.py` FR "loyer annuel de l'internat" | correct: 1 140,00 DH (page citation missing in that early run) |
| `ask.py` EN "how many books…" | correct: up to 5 books (p.14) |
| `ask.py` Arabizi "ch7al kaykhles talib f l-dakhiliya f l-3am ?" (early version) | **incoherent** answer, polluted by an irrelevant chunk (p.11 examples) |
| `test_darija_model.py` v1 (plain Atlas-Chat-2B) | fluent Darija but unfaithful: infirmerie→"pharmacie", emprunter→"produire", "p."→"partie"; Arabizi not produced (text repeated in Arabic script) |
| `test_darija_model.py` v2 (protected tags + glossary + checks) | `ar_ok 3/4`, `lat_ok 1/4`; remaining semantic errors ("loyer"→"installation", "déposer la justification"→"pay the absence"); sentence 2 duplicated hours |
| `ollama run qwen2.5:3b --verbose` (no context) | eval rate 6.68 then 8.06 tokens/s (second run after closing background apps); `ollama ps`: 100% CPU, 2.2 GB, context 4096. Without context the model invented definitions of RAG ("Requiring Augmented Guidance", then "Résumé, Analyse et Génération") |
| `test_situations.py` oracle (rules chunks p.11-1/p.11-2) | printed 0/5 + 1/6 **because of a parser bug**; manually re-scored: modules 2/5, year 2/6 = 4/11; intermediate verdicts (RATTRAPAGE/JURY) 0/3 |
| `test_situations.py --pipeline` | re-scored: modules 3/5, year 5/6 = 8/11; intermediate verdicts 0/3. Biased: Y1–Y3 are the guide's own examples present in retrieved context; n=11, one run |

## In progress
- **Hybrid situation pipeline** (Qwen extracts notes as JSON → `rules.py` decides → fixed template). `situation_pipeline.py` and the `json_mode` option in `rag_common.chat()` were written **only in the assistant's sandbox**: not run with any fake model, not delivered to the student, `test_hybrid.py` not written.

## Pending
Independent test set (30–50 real student questions) · systematic generation eval FR/EN/AR + `MIN_SCORE` calibration with out-of-scope questions · router (info vs situation) in `ask.py` · regulatory documents (évaluation/délibération, normes pédagogiques) · timetable SQL module + automatic update pipeline · UI, Docker, deployment · model/cost comparison · DODa dataset inspection (student must clone and paste file list + first 5 lines) · report writing.

## Blocked / open
- Darija answer generation: Qwen2.5 3B writes incoherent Arabizi; Atlas-Chat-2B unfaithful → answers to Arabizi questions are currently in French (decision D8/D9). Needs supervisor input on whether Darija *output* is required.
- Ambiguities of the guide's grading rules (see AI_CONTEXT §12) → need the official regulation.
- Waiting for supervisor answers (19 questions in the PDF report).

## Last known working state
Retrieval + `ask.py` for FR/EN/AR/Darija questions works on the student's machine (index in `data/chroma`). Answer language for Arabizi = French (provisional).

## Repository audit and reorganisation (2026-10-18)
- Repo `github.com/Yssfoufi1/pfe` cloned and checked by the assistant on a copy (no Ollama): 19 `.py` compile; `test_rules` 20/20; `check_structured_data` coherent; `check_chunks` 24/24; pages/clubs/chunks regenerated from the PDF = committed files; Chroma index = 42 items, 1024 dims, ids match. [VERIFIED in sandbox]
- Findings: the repo was **public** and tracked student phone numbers (`clubs.csv`, `pages.jsonl`, `chunks.jsonl`, 2 numbers in a test), no `.gitignore`, `__pycache__`, Chroma binaries and the PDF; README was empty; no `requirements.txt`. The student set the repo to **private** (confirmed by him). Git history still holds the files (commit `700574c`).
- Reorganisation into the roadmap tree prepared and checked in the sandbox (imports/paths only, no logic change): outputs identical, offline tests pass, wiring checked end to end with a mock Ollama (numbers from the mock mean nothing). **Applied and pushed by the student 2026-10-19 (commit `9ba1cd5`) [VERIFIED by his outputs]:** offline checks 24/24 / coherent / 20/20, index rebuilt (42 chunks, 93.4 s). The folder rename `pfe`→`pfe_old` was refused (folder in use); work continues in `pfe_v2`.
- **Regression [VERIFIED]:** after the move, `ask` answered "(18)" to the rent question. Cause: the "Rappel : termine par la page source" line in the prompt. Fix D19 applied and **verified on Qwen** [VERIFIED]: `ask` answers "…1 140,00 DH"; `evaluation.smoke_generation` 8/9 in 391 s (≈ 43 s/question); the single failure is a regex too strict on "1,140 DH" (English format), fixed in the test; the model reformatted the number (rule 3 says copy numbers as-is). After the regex fix `smoke_generation` = 9/9 (254 s total; per question min 8 s, median 22 s, max 57 s). Latency: both models stay loaded (`ollama ps`: qwen2.5:3b 2.2 GB + bge-m3 1.2 GB, 100% CPU); the old test took 391 s with VS Code open and 161 s after closing it → RAM pressure, not model swapping. [VERIFIED by the student's outputs]
- **Phase 4 method (D20), prepared in the sandbox, not yet run:** `evaluation/gold/guide_questions.csv` (22 questions, pages 10–12, 8 chunks), `evaluation/gold_check.py` (offline: each expected fact matches its source chunk; it caught a line-break bug in one regex), `evaluation/run_coverage.py` (modes retrieval / oracle / e2e), `chat_with_stats()` in `rag_common.py`. Coverage so far: 8/42 chunks.
- Added: `README.md`, `requirements.txt`, `.gitignore`, `documents/README.md`, `docs/ROADMAP_TRACKING.md`; `docs/DECISIONS.md` gained D16–D18. Phone numbers removed from `tests/check_chunks.py`.

## Files this session
- **Delivered to the student:** all scripts listed in `AI_CONTEXT.md` §7 except `situation_pipeline.py`; data files `calendrier_2025_2026.csv`, `filieres.json`, `clubs.csv`, `chunks.jsonl`, `darija_lexicon.csv`, `glossaire_fr_darija.csv`; `compte_rendu_PFE_avancement.pdf`.
- **Sandbox-only changes (student's copies are older):** `situation_pipeline.py` (new); `rag_common.py` (`json_mode` added to `chat()`); `test_situations.py` (verdict-parser fix: regex now takes letters/spaces only).
- Nothing deleted. Git status of the project: [UNKNOWN].

## Exact next action
Roadmap Phase 4, batch 1: student reviews the gold questions then runs `gold_check` and `run_coverage` (see `NEXT_STEPS.md` #1). Then roadmap Phase 4 (`NEXT_STEPS.md` #2). `situation_pipeline.py` stays on hold until the supervisor/student decide SLM-only vs hybrid.

## Must know before continuing
- The student works through normal chat and copies code manually; never assume a suggested file was applied.
- Use `py`, not `python`. Ollama must be running. Student writes in Darija Arabizi (Latin letters) mixed with French/English.
- Do not trust mock-server results as model quality.
- Hardware wording: the laptop has an **integrated** Intel UHD Graphics 620 (not "no GPU"); it shares the 8 GB RAM and `ollama ps` shows 100% CPU, so it is unused. Earlier reports said "sans GPU"; corrected.
