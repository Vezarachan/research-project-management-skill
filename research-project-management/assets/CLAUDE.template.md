# {{PROJECT_NAME}} — project conventions

This project is managed with the research-project-management skill. These rules
keep it lean; follow them in every session.

## Session start
- Read `PROJECT.md` first. It is the current state of the project (≤150 lines).
- Do NOT re-read old experiment cards or archived material unless the task needs them.

## Where things go
- `code/` is the public GitHub repository: everything in it is published, nothing
  private enters it (no cards, PROJECT/CLAUDE/MANIFEST, tex/bib, reviews, drafts, data, outputs).
- The method → `code/src/{{pkg}}/` (must not reference any specific experiment).
  Figure style and paths → `code/src/paperfigs/`.
- Every script whose output is reported (card, figure, table, number) →
  `code/experiments/EXP-NNN-name/`. Throwaway exploration → private
  `experiments/EXP-NNN-name/scratch/`; promote it to `code/` once a result depends on it.
- No machine paths in `code/`: use `paperfigs.paths` (data_dir, out_dir, fig_dir).
  `source env.sh` before running; outputs then land in `experiments/EXP-NNN-name/`
  beside the CARD, manuscript figures in `figures/`.
- Git data lives off the synced drive (`code/.git` is a pointer file). Commit when
  asked; push, create the GitHub repo or refresh the anonymous mirror only when the
  user says so. Before pushing: `python3 ~/.claude/skills/research-project-management/scripts/check_release.py code/`
  (add `--anonymous` while under double-anonymous review).
- New datasets: register in `data/MANIFEST.md` (location, format, CRS, resolution,
  temporal extent, source, size). Never copy large files (rasters, point clouds,
  weights) into the project — this directory is on synced storage.

## Experiments
- New experiment = next EXP number: `experiments/EXP-NNN-short-name/`.
- Every experiment gets a `CARD.md` (one page: Question / Setup / Result /
  Evidence / Decision). A result without a one-sentence conclusion is not done.

## Manuscript
- Living draft: `manuscript/01_main_v1.tex` + `01_supplementary_v1.tex`, references
  `02_references.bib`, figures in `manuscript/figures/` (copies; `sh sync_figures.sh`).
  Never create edited copies (`*_final.tex`, `*_old.tex`).
- vN = version in progress. At a milestone (full draft, closed review round,
  submission, resubmission, acceptance) snapshot it to
  `manuscript/versions/vNN-<VENUE>-<event>-<date>/`, add a row to `versions/INDEX.md`,
  then rename the living files to vN+1 and update this line. Never edit inside `versions/`.
- Target venue and its requirements: `manuscript/VENUE.md`. A venue switch = snapshot,
  outcome into the INDEX venue history, bump, new VENUE.md.
- Review rounds are paired: internal `reviews/R<k>-comments.md` ↔ `R<k>-response.md`;
  journal `reviews/<VENUE>-R<k>-comments.md` ↔ `<VENUE>-R<k>-response.md`.
- Full rules: `~/.claude/skills/research-project-management/references/manuscript-versioning.md`.

## References
- Never write a bib entry from memory. Get it with
  `python3 ~/.claude/skills/research-project-management/scripts/check_references.py --lookup <DOI | arXiv id | title>`;
  every entry carries a DOI or arXiv id where one exists.
- Cannot look it up? Add `unverified = {reason}` to the entry and wrap the citing sentence in `\pending{}`.
- When the bib or citations changed, run `check_references.py manuscript/01_main_vN.tex manuscript/01_supplementary_vN.tex`;
  no FAIL may remain in a snapshot that leaves your hands.
- Full rules: `~/.claude/skills/research-project-management/references/reference-audit.md`.

## Figures
- House standard: `~/.claude/skills/research-project-management/references/figure-standard.md`.
  Short form: draw at printed width (84 / 180 mm); Aptos only; panel heading
  "**a** Title" 9 pt, body 7 pt, nothing below 6.5 pt; lines ≥ 0.3 pt; vector PDF.
- File names: `fig_<topic>` / `figS_<topic>` (tables `tab_` / `tabS_`), lowercase
  hyphen-joined words, same stem for .pdf/.png/src/*.afdesign, label `fig:<topic>`.
  No numbers, versions, dates or draft/ folders — old states live in snapshots.
- Code figures: nature-figure skill (Python) + `paperfigs.plotstyle`; save via `paths.fig_dir()`.
- Captions: first sentence = the claim; `\panel{a}` per panel; keys as "term, meaning";
  a `% source:` comment above each figure (file <- script, CARD).
- Before a snapshot that leaves your hands: `python3 ~/.claude/skills/research-project-management/scripts/check_figures.py manuscript/01_main_vN.tex`.

## Session end
- When substantial results were produced, suggest running a checkpoint
  (`/research-project-management checkpoint` or just "checkpoint") to card
  experiments, update PROJECT.md, and sweep strays.
- All project documents are written in English.
