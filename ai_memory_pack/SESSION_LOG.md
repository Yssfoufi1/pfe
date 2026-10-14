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

**Tests/verification:** see PROGRESS.md table.

**Decisions made:** D1–D15 in `DECISIONS.md`.

**Remaining:** NEXT_STEPS.md items 1–4 and "Later".

**Next recommended action:** verify and deliver the hybrid situation pipeline (NEXT_STEPS #1).
