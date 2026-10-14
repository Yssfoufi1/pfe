## AI memory system (for switching AI assistants)

This repository contains documentation meant to let any AI assistant continue the work without re-explaining the project:

| File | Purpose |
|---|---|
| [`AI_HANDOFF.md`](AI_HANDOFF.md) | Short handoff: paste it into a new AI chat together with the repository URL |
| [`AI_CONTEXT.md`](AI_CONTEXT.md) | Full project reference (architecture, files, commands, limitations) |
| [`PROGRESS.md`](PROGRESS.md) | Latest verified state, test results, blockers, exact next action |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | Prioritised roadmap |
| [`DECISIONS.md`](DECISIONS.md) | Technical decisions and their rationale |
| [`SESSION_LOG.md`](SESSION_LOG.md) | Chronological session summaries |
| [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) | Permanent working rules for AI assistants |

**When switching assistants:** open a new chat, paste the prompt below with the repository URL, and let the assistant read the files.
**At the end of every session:** ask the assistant to update the docs (see `AI_INSTRUCTIONS.md`), copy the files into the repo, then commit and push.

**Prompt to paste into a new AI chat** (replace the URL):
```
I'm continuing an existing project. Repository: <GITHUB_URL>.
Read AI_HANDOFF.md first, then AI_CONTEXT.md, PROGRESS.md, NEXT_STEPS.md, DECISIONS.md and AI_INSTRUCTIONS.md.
Do not assume suggested code was applied: ask me what I actually ran. Tell me in 5 lines what you understood,
then continue with the exact next step. Reply in Moroccan Darija (Latin letters), step by step.
(If you cannot open the URL, I will paste AI_HANDOFF.md.)
```
