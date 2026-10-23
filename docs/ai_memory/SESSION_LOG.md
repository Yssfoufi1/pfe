# SESSION_LOG (concise, chronological; newest at the bottom)

## Session 1 — ≈ 2026-10-08 → 2026-10-14 (one long chat; per-step dates unknown)
**Objective:** choose and build the first working version of the PFE assistant.

**Work done (phases)**
1. *Scoping:* explained RAG/SLM/sovereignty/cost; RAG vs fine-tuning vs distillation → RAG (D1). Compared health vs EST Fès use cases; student emailed the supervisor; supervisor replied (see AI_CONTEXT §2) → university domain (D2).
2. *Environment:* Ollama, qwen2.5:3b, bge-m3. First Darija test: Qwen answered that Arabizi was Wolof.
3. *Corpus:* extraction of the guide, structured data for image pages, clubs table, chunking, indexing, search, tests.
4. *Language work:* 5-variant retrieval eval; Darija→French lexicon expansion; language detector.
5. *Generation:* `ask.py`; relative-score filtering; Atlas-Chat-2B experiments (plain and guarded).
6. *Situation-problems:* `rules.py` (+tests), `test_situations.py`; SLM-only results; decision for a hybrid design; `situation_pipeline.py` written in sandbox.
7. *Supervisor communication:* progress-report PDF + 19 questions generated.
8. *DODa dataset:* student shared the repo link; GitHub fetch was blocked for the assistant, information came from search snippets only.
9. This documentation pack created.

**Files changed:** see PROGRESS.md "Files this session".

**Errors and solutions**
- `pip` not recognised → use `py -m pip` / `py`.
- `bge-m3` not found on first `test_embed.py` → `ollama pull bge-m3` (then OK).
- Chunking: wrapped sentence ends ("…les pièces suivantes :") mistaken for sub-headings → rule: sub-heading must start with a capital letter; chunk count 47 → 42.
- Clubs table split into fragments → dedicated `extract_clubs.py`.
- Example boxes on guide p.11 interleaved by columns → boxes extracted separately.
- Glossary sigle `EST` matched French verb "est" (sandbox test) → acronyms matched case-sensitively.
- `test_situations.py` parser cut answers at "(p." → regex fixed **in sandbox only**; scores re-computed manually from the student's output.
- Darija quality: no fix; deferred (D8/D9).
- Hardware misdescribed as "no GPU" by the assistant; the student showed Task Manager (Intel UHD Graphics 620, 3.9 GB shared). Corrected everywhere ("no dedicated GPU"); `ollama ps` shows 100% CPU.

**Tests/verification:** see PROGRESS.md table.

**Decisions made:** D1–D15 in `DECISIONS.md`.

**Remaining:** NEXT_STEPS.md items 1–4 and "Later".

**Next recommended action:** verify and deliver the hybrid situation pipeline (NEXT_STEPS #1).

## Session 2 — 2026-10-18 (same chat)
**Objective:** align the project with the supervisor's roadmap document and audit the repository.

**Work completed:** read the roadmap (phases 0–8); cloned and audited the repo (see PROGRESS "Repository audit"); produced the phase-by-phase comparison; found the privacy incident (public repo with student phone numbers, no `.gitignore`); the student set the repo private; prepared the reorganisation into the roadmap tree, README, `requirements.txt`, `.gitignore`, `docs/ROADMAP_TRACKING.md`.

**Files changed (in the assistant's sandbox copy; student's local repo: unknown):** whole layout (git renames), import/path edits, new docs; `tests/check_chunks.py` (phone numbers removed).

**Errors / issues:** `grep` false positive on `data/chunks/chunks.jsonl` (new path) — not a bug; mock-server numbers are meaningless (wiring check only).

**Tests:** see PROGRESS "Repository audit". Not run: anything needing Ollama.

**Decisions:** D16 (reorganise), D17 (private repo, untrack sensitive files; history purge pending), D18 (freeze Darija output; to validate).

**Remaining:** NEXT_STEPS #1–#3.

**Update 2026-10-19:** the student applied the reorganisation in `pfe_v2` and pushed it (commit `9ba1cd5`); offline checks 24/24, coherent, 20/20; index rebuilt in 93.4 s. Found: `ask` answered "(18)" (prompt reminder, D19) — fix and `evaluation/smoke_generation.py` prepared. Folder rename `pfe`→`pfe_old` refused (folder in use), harmless. Git emitted LF→CRLF warnings (harmless) and showed an empty Chroma file as "renamed" to `evaluation/__init__.py` (both empty; cosmetic).

**Next recommended action:** student runs the fix verification (NEXT_STEPS #1); then Phase 4.
