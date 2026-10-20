# AI_INSTRUCTIONS — permanent working rules for any AI assistant on this project

## Before suggesting anything
- Read `AI_HANDOFF.md`, `AI_CONTEXT.md`, `PROGRESS.md`, `NEXT_STEPS.md`, `DECISIONS.md`. Understand the existing implementation first; inspect the relevant source files when you can, otherwise ask for them (only what is genuinely needed).
- Follow the established architecture and conventions (AI_CONTEXT §6, §11). No duplicate implementations; no unnecessary rewrites; preserve working behaviour.

## Style the student expects
- Answer in **Moroccan Darija written in Latin letters (Arabizi)**, French/English technical terms allowed; do **not** mix in Arabic-script or formal Arabic phrasing in replies (Arabic script is fine inside test data/prompts when the task needs it, with a note).
- Go **step by step**, one stage at a time, with debugging help at each stage; explain the *why* as well as the *how*.
- Give **complete, copy-paste-ready files** (not partial diffs), with the exact path and whether to add / replace / remove. Say which PowerShell command to run (`py …`, run from `C:\Users\PC\pfe`). Mention install commands and dependencies.
- Verify code before sharing when you have tools (sandbox) and say precisely what was verified. A sandbox usually has **no Ollama**: tests with mock/fake models validate logic only, never model quality — say so.
- Provide download links for files when possible.

## Honesty rules
- Always distinguish **proposed / applied (student confirmed or output proves it) / verified (output seen)**. Never claim code was executed, tested, committed or pushed without evidence. If unsure whether a file version was applied, ask.
- Report real numbers (counts), not impressions. Say when a test set is small or circular.
- Never mark a task done without evidence. Do not invent files, results, decisions or percentages.

## Project-specific rules
- Cite the printed page (PDF page − 1). Never change numbers, dates or names taken from the context.
- Ambiguous or jury-dependent grading cases must be flagged, not decided (see D12).
- Use `py`, not `python`. Keep everything local (no cloud APIs, no secrets in files).
- Run modules with `py -m src.<package>.<module>` / `py -m tests.<name>` from the repository root (the roadmap tree was applied on 2026-10-18).
- **The roadmap `roadmap_PFE_RAG_SLM_alignee_encadrant.docx` is the reference.** Track phases only in `docs/ROADMAP_TRACKING.md`; do not create another roadmap. Defer what the roadmap defers (SQL timetables, change detection, incremental re-indexing, website integration, deployment, multi-user, exhaustive model comparison). Define expected answers from official texts, not from guesses.
- The repository is **private** and must not contain personal data (phone numbers of students), source documents or generated indexes (see `.gitignore`). New AI chats cannot open a private URL: the student pastes `AI_HANDOFF.md` instead.
- Personal data (club presidents' phones) must not go to a public repository.

## End-of-session workflow (mandatory when the student says we are finishing, switching assistant, or stopping)
Ask the student (briefly) what he actually copied and ran, then update — only the files whose content changed:
1. `PROGRESS.md` (state, tests with real results, blockers, files, exact next action) · 2. `NEXT_STEPS.md` · 3. `DECISIONS.md` (add/supersede, never silently rewrite) · 4. `SESSION_LOG.md` (new session entry) · 5. `AI_HANDOFF.md` (keep short) · 6. `AI_CONTEXT.md` only if architecture/files/commands changed.
Record separately: code **proposed**, code the student **confirmed applied**, code **verified** (with the result), and what stays uncertain. Return the updated files in full (or exact replacements) so he can copy-paste them.
