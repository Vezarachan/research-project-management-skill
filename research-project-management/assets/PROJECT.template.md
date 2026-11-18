# Project: {{PROJECT_NAME}}

<!-- HARD CAP: 150 lines. When adding content pushes past the cap, demote:
     finished experiments -> their CARD.md; resolved decisions -> one line;
     dead threads -> archive/INDEX.md. Never delete, always demote. -->

## Research Question
<!-- 1-3 sentences. The question this project exists to answer. Changes rarely. -->
{{RESEARCH_QUESTION}}

## Current Status
<!-- Updated at every checkpoint. 5-10 lines: where the project stands right now,
     written for someone (including future you) with zero session context. -->
_Last checkpoint: {{DATE}}_

## Active Experiments
<!-- Only experiments currently running or awaiting analysis. One line each:
     EXP-NNN-name — what it tests — current state.
     Finished experiments live in their cards, not here. -->

## Key Decisions
<!-- One line per decision that still constrains current work, newest first:
     [date] decision — reason (EXP-NNN if evidence-based).
     When a decision stops mattering, move it to archive/INDEX.md. -->

## Next Steps
<!-- 3-7 concrete items. If an item has been here for 3+ checkpoints,
     either do it, card it as a follow-up, or archive it. -->

## Pointers
<!-- Stable references only: manuscript draft, key figures, data manifest,
     external resources (overleaf, dataset portals, compute). One line each. -->
- Manuscript: `manuscript/01_main_v1.tex` (target venue: `manuscript/VENUE.md`)
- Data registry: `data/MANIFEST.md`
- Code: `code/` (GitHub: {{REPO_URL}}; anonymous mirror during review: {{MIRROR_URL}}; run `source env.sh` from the project root first)
- Git store of `code/` (off the synced drive), per machine: see `env.sh`
- Archive index: `archive/INDEX.md`
