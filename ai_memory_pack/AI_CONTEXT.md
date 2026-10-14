# AI_CONTEXT — PFE: local RAG assistant for EST Fès

> Main reference for any AI assistant. Last updated: 2026-10-14.
> Status tags used in all docs: **[VERIFIED]** = the student ran it and pasted the output · **[SANDBOX]** = verified only in the assistant's sandbox (mock/fake models, no Ollama) · **[PROPOSED]** = code/idea given, no evidence it was applied · **[INFERRED]** · **[UNKNOWN]**.
> Read together with: `AI_HANDOFF.md` (short state), `PROGRESS.md`, `NEXT_STEPS.md`, `DECISIONS.md`, `SESSION_LOG.md`, `AI_INSTRUCTIONS.md`.

## 1. Project
- **Type:** final-year project (PFE), Data Engineering (Ingénierie des Données), École Supérieure de Technologie de Fès (EST Fès).
- **Official title:** *Souveraineté des données et maîtrise des coûts : développement d'un assistant conversationnel via une architecture RAG locale et un SLM.*
- **Problem:** cloud LLMs send questions/documents to foreign servers (data sovereignty, Moroccan law 09-08) and cost money per token. Goal: an assistant that runs fully locally on modest hardware (8 GB RAM, no GPU) with a Small Language Model.
- **Use case chosen (after supervisor feedback):** a university assistant answering students' questions from the *Guide pratique de l'étudiant 2025-2026* (the "head document"). A health use case was considered earlier and is **not** retained.

## 2. Supervisor guidance (paraphrased from his email)
Do not fix the use case too early; first deploy a working generic RAG assistant on any document corpus to validate technical choices; choose the domain by availability/accessibility/usability of data. University domain is judged realistic (public regulations, "cahiers des normes pédagogiques", published timetables, filière descriptions). The assistant must answer direct factual questions **and** handle "situations-problèmes" (e.g. does a student validate a module / pass to the next semester or year?) with argued answers and precise references to source documents. Progressive approach recommended.

## 3. Objectives / requirements
1. Factual Q&A with source citation (printed page number of the guide).
2. Situations-problèmes (module/year validation) with justified answers; ambiguous cases must be flagged, not decided.
3. Languages: **English, French, Arabic (MSA), Darija in Arabic script, Darija in Latin script (Arabizi)** — the student states Darija must work in both scripts.
4. Local, low-cost: runs on the student's laptop; cost/sovereignty argument must be measurable in the report.
5. Keep data fresh (timetables/documents change each semester/year): automatic update pipeline **[planned, not started]**.
6. Possible integration into the school website / deployment on school servers **[planned; needs school authorisation — unknown]**.
7. Evaluation for the report: accuracy, faithfulness to sources, hallucination, latency, cost, model comparison **[partly done, see PROGRESS.md]**.

## 4. Feature status
| Feature | Status |
|---|---|
| PDF text extraction per page (printed-page aware) | [VERIFIED] |
| Image-only pages → structured data (calendar CSV, filières JSON) | [VERIFIED] (checks run; transcription made by the assistant from page images, **not independently re-checked by the student**) |
| Clubs table → CSV | [VERIFIED] |
| Chunking (42 chunks) + fact-integrity tests | [VERIFIED] 24/24 |
| Embeddings (bge-m3) + ChromaDB index + search | [VERIFIED] |
| Multilingual retrieval eval (5 language variants, query expansion) | [VERIFIED] (non-independent test set) |
| RAG answer generation with Qwen2.5 3B (FR/EN) | [VERIFIED] on 2 questions only |
| Darija/Arabizi answer generation | Not working (see DECISIONS D8/D9) |
| Situation rules in code (`rules.py`) | [VERIFIED] 20/20 |
| SLM-only situation answering | [VERIFIED] insufficient (4/11 oracle, 8/11 pipeline-biased; 0/3 intermediate verdicts) |
| Hybrid situation pipeline (`situation_pipeline.py`) | **[SANDBOX-ONLY, written but not even run with a fake model, not delivered to the student]** |
| Timetable SQL module / automatic update pipeline / UI / deployment | Not started |

## 5. Technology stack
Windows 11 laptop (Lenovo X1 Carbon 7th gen, Intel i7 8th gen, 8 GB RAM, no GPU) · Python 3.13 via the `py` launcher (the `python` alias opens the Microsoft Store — **always use `py`**) · Ollama (local LLM server, `http://localhost:11434`) · models: `qwen2.5:3b` (generation), `bge-m3` (embeddings, 1024-dim), `atlas-chat-2b` (alias of `hf.co/QuantFactory/Atlas-Chat-2B-GGUF:Q4_K_M`, tested for Darija, not used in the pipeline) · `pdfplumber`, `chromadb` · standard library only for HTTP (`urllib`). Planned: FastAPI/Streamlit, Docker, SQLite.

## 6. Architecture
```
Information question:
  question -> lang_detect (fr|en|ar_script|darija_latin) -> query_rewrite (Darija->French keyword expansion)
  -> bge-m3 embedding -> ChromaDB top-3 -> keep chunks within 0.12 of best score
  -> constrained prompt (answer only from context, cite page, never alter numbers) + Qwen2.5 3B -> answer + sources
  (darija_latin questions are currently answered in French)

Situation question (hybrid, PLANNED/UNTESTED):
  free text -> Qwen JSON extraction (notes) -> validation -> rules.py (code decides) -> fixed-template answer + page + caveats

Structured data (not RAG): data/calendrier_2025_2026.csv, data/filieres.json, data/clubs.csv (clubs also embedded as one chunk per row)
```
Vector scores: vectors are normalised; Chroma default distance is squared L2 → `score = 1 - d/2` (= cosine).

## 7. Directory layout (student's machine: `C:\Users\PC\pfe`) — repository layout [UNKNOWN: whether this folder is a git repo / GitHub URL]
```
pfe/
  extract_pages.py  extract_clubs.py  build_structured_data.py  check_structured_data.py
  chunk_pages.py  check_chunks.py  rag_common.py  test_embed.py  index_chunks.py  search.py
  eval_retrieval.py  query_rewrite.py  lang_detect.py  ask.py
  darija_pipeline.py  test_darija_model.py  rules.py  test_rules.py  test_situations.py
  situation_pipeline.py   <- sandbox only, not yet delivered
  data/
    guide_etudiant_2025_2026.pdf  pages.jsonl  chunks.jsonl  clubs.csv
    calendrier_2025_2026.csv  filieres.json  darija_lexicon.csv  glossaire_fr_darija.csv
    chroma/   (ChromaDB persistent store, collection "guide_etudiant")
  doda/       (Darija Open Dataset clone — NOT done yet)
```
### File responsibilities
| File | Role | Status |
|---|---|---|
| `extract_pages.py` (v2) | PDF → `data/pages.jsonl`; extracts example boxes separately, drops text over big images, checks page offset | [VERIFIED] |
| `extract_clubs.py` | rebuilds the clubs table by x/y positions → `data/clubs.csv` (10 rows) | [VERIFIED] |
| `build_structured_data.py` / `check_structured_data.py` | generate / validate calendar CSV (112 rows) and filières JSON (20 filières) | check [VERIFIED]; build run by assistant only |
| `chunk_pages.py` | section-aware chunking → `data/chunks.jsonl` (42 chunks; clubs = 1 chunk/row) | [VERIFIED] |
| `check_chunks.py` | 24 facts must stay in one chunk; flags suspicious sub-sections | [VERIFIED] 24/24 |
| `rag_common.py` | Ollama calls: `embed()`, `chat()`; constants (models, Chroma path) | [VERIFIED]; **local copy lacks `json_mode` param added in sandbox** |
| `test_embed.py` | sanity check of bge-m3 (dimensions, cosine) | [VERIFIED] |
| `index_chunks.py` | embeds `context + text`, stores in Chroma | [VERIFIED] 110 s |
| `search.py` | retrieval, optional expansion (`--base` disables in CLI) | [VERIFIED] |
| `query_rewrite.py` + `darija_lexicon.csv` | 176-entry Darija→French keyword expansion (Latin + Arabic script) | [VERIFIED] |
| `eval_retrieval.py` | 12 questions × 5 language variants, base vs expanded | [VERIFIED] |
| `lang_detect.py` | rule-based language/script detection | used by `ask.py` [VERIFIED]; 60/60 on own eval questions [SANDBOX] |
| `ask.py` | full RAG assistant (interactive or one question; `--debug`) | [VERIFIED] (evidence that the version with relative-score filter is applied: `test_situations --pipeline` output) |
| `darija_pipeline.py` + `glossaire_fr_darija.csv` | guarded FR→Darija translation with Atlas-Chat (protected tags) | [VERIFIED] ran; result unsatisfactory |
| `test_darija_model.py` | tests the above | [VERIFIED] |
| `rules.py` / `test_rules.py` | grading rules p. 11 in code / 20 checks | [VERIFIED] 20/20 |
| `test_situations.py` | 11 situations, oracle vs pipeline mode, ground truth from `rules.py` | ran [VERIFIED]; **local copy has a verdict-parser bug** (fixed in sandbox only) |
| `situation_pipeline.py` | extraction→rules→template | [SANDBOX-ONLY, untested] |

## 8. Install / run / test (PowerShell, in `pfe`)
```powershell
py -m pip install pdfplumber chromadb
ollama pull qwen2.5:3b
ollama pull bge-m3
# optional (Darija experiment)
ollama pull hf.co/QuantFactory/Atlas-Chat-2B-GGUF:Q4_K_M
ollama cp hf.co/QuantFactory/Atlas-Chat-2B-GGUF:Q4_K_M atlas-chat-2b
# pipeline (PDF must be at data\guide_etudiant_2025_2026.pdf)
py extract_pages.py ; py extract_clubs.py ; py chunk_pages.py ; py check_chunks.py
py test_embed.py ; py index_chunks.py
py search.py "Quel est le loyer annuel de l'internat ?"
py eval_retrieval.py
py ask.py "Quel est le loyer annuel de l'internat ?" --debug
py test_rules.py ; py test_situations.py ; py test_situations.py --pipeline
```
`calendrier_2025_2026.csv`, `filieres.json`, `darija_lexicon.csv`, `glossaire_fr_darija.csv` were delivered as files (the build script can regenerate the first two).

## 9. Data formats
- `chunks.jsonl` fields: `id` (`guide2526-p{printed}-{k}` or `guide2526-club-{k}`), `source`, `printed_page`, `pdf_page`, `chapter`, `section`, `subsection`, `context`, `text`, `n_chars`.
- Chroma collection `guide_etudiant`; documents = `text`; embedded string = `context + "\n" + text`; metadata: `printed_page`, `section`, `subsection`, `context`.
- Key parameters: `MAX_CHARS=1400`, `MIN_CHARS=300`, `TOP_K=3`, `REL_MARGIN=0.12`, `MIN_SCORE=0.0` (disabled, to calibrate), `num_ctx=4096`, embed batch 16.

## 10. Constraints
8 GB RAM / no GPU: ≈ 15–20 s per Qwen call; bge-m3 (~1.2 GB) and Qwen (~2 GB) both resident; first embedding call ≈ 9 s (model load). Windows console shows Arabic poorly (copy-paste outputs). Sandbox used by the assistant has no Ollama: only mock servers (results with mocks say nothing about model quality).

## 11. Conventions
Printed page = PDF page − 1 (cite the printed page). Scripts are standalone, run from the project root, UTF-8, no secrets. Every new data-processing step gets an automatic check script. Tests report counts, not impressions.

## 12. Known limitations and source anomalies
See `PROGRESS.md` §Blockers and `DECISIONS.md`. Guide anomalies found: (1) DUT year-1 S2 dates printed with 2025 (`vendredi 20 juin 2025`, `vendredi 30 mai 2025`); (2) Marche verte / Independence Day printed with 2026 (should be 2025); (3) vacations "dimanche 24" vs 25 January; (4) DBT technical internship 12 weeks (p.10) vs ≈10 weeks in calendar; (5) example "Cours 04 + TP 16 = 11,00" (arithmetic mean 10); (6) year-average examples (11,20 / 9,60 / 10,95) can't be recomputed (5 of 14 modules shown, credit weighting unspecified); (7) module ≥7 with an element <5: module rule says no compensation, year rule silent; (8) "Admis par dérogation ou Ajourné" = jury decision; (9) student club presidents' phone numbers are published (personal data, law 09-08).

## 13. Open questions (to the supervisor — 19 listed in the progress report PDF)
Official evaluation regulation and "cahier des normes pédagogiques"? Credit weighting of the annual average? Must the assistant *answer* in Darija or only *understand* it? Evaluation criteria expected? Permission to collect 30–50 real student questions? Deployment contact/authorisation? Fine-tuning expected? Report dates?
