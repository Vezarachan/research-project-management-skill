---
name: research-project-management
description: Keep GeoAI / scientific research projects lean, structured and consistent as they grow — project scaffolding, one-page experiment cards, a size-capped PROJECT.md, a public code/ folder that is the GitHub repo, a house figure and caption standard (Aptos, AAG print sizes, checked by script), a reference audit that catches fabricated or retracted citations, and LaTeX manuscript versioning across revision rounds and venue switches. Use this skill whenever the user starts or initializes a research project, runs a checkpoint / session wrap-up, logs an experiment, tidies or audits a messy project, prepares code for GitHub or an anonymous mirror, makes or checks figures or captions, adds or checks references, snapshots a manuscript, submits or resubmits a paper, gets reviews back, or switches journal/conference — and whenever they mention PROJECT.md, 实验卡, 项目整理, 收尾, checkpoint, 代码开源, 作图规范, 图注, 参考文献, 引用核查, 稿件版本, 返修, 投稿, or 换期刊 in a research context.
---

# Research Project Management

Research projects accumulate entropy: every session adds scripts, results, figures, drafts and
notes, and nothing removes them. This skill makes **compression happen at write time, not
cleanup time**, through a three-layer information architecture whose always-loaded layer has a
fixed size budget — so token cost and cognitive load stay constant however long the project runs.

1. **`PROJECT.md`** — living state. Hard cap **150 lines**. Read at the start of every session.
   Only what is currently true and actionable: question, status, active experiments, decisions, next steps.
2. **Experiment cards** (`experiments/EXP-NNN-name/CARD.md`) — one page per experiment, the permanent record.
3. **`archive/INDEX.md`** — one line per archived item. Read almost never.

Information flows downward: when `PROJECT.md` would exceed its cap, demote finished or stale
content into cards or the archive index — never just delete it, never let the cap slip.

## Modes

| User intent | Mode |
|---|---|
| "start a new project", "initialize", "set up project structure" | **init** |
| "checkpoint", "wrap up", "log this experiment", "收尾" | **checkpoint** |
| "audit", "how healthy is this project", "what's cluttered" | **audit** |
| "adopt this existing project", "clean up this messy repo" | **adopt** |
| "snapshot the manuscript", "I submitted today", "reviews are back", "this round is done" | **snapshot** |
| "we're switching to journal X", "rejected, resubmit to …", "换期刊" | **venue switch** |
| "make / fix / check this figure", "write the caption", "作图", "图注" | **figures** |
| "add this reference", "check the citations", "参考文献核查", "查引用" | **references** |
| "push the code", "make the repo public", "anonymous mirror", "代码开源", "上传 GitHub" | **release** |

## Project structure

```
<project>/
├── PROJECT.md            # living state, ≤150 lines (assets/PROJECT.template.md)
├── CLAUDE.md             # standing rules for every session (assets/CLAUDE.template.md)
├── env.sh                # this machine's data/output paths for the public scripts (assets/code/env.sh)
├── data/
│   ├── MANIFEST.md       # registry of ALL datasets (assets/MANIFEST.template.md)
│   └── processed/        # small derived files only (<~50 MB each)
├── experiments/
│   └── EXP-001-name/     # PRIVATE half of an experiment: CARD.md, outputs, scratch/
├── code/                 # PUBLIC = the GitHub repository; everything in it is published
│   ├── src/<package>/    #   the method (importable, tested)
│   ├── src/paperfigs/    #   paper support: plotstyle.py, paths.py (assets/code/)
│   ├── experiments/EXP-001-name/   # scripts of that experiment (same name as the private dir)
│   ├── examples/         #   quickstart + small demo data
│   ├── docs/             #   project page (GitHub Pages)
│   └── README.md LICENSE pyproject.toml requirements.txt .gitignore
├── figures/              # manuscript figures written by the scripts (and Affinity sources)
├── manuscript/
│   ├── 01_main_vN.tex          # THE living main text, vN = version in progress
│   ├── 01_supplementary_vN.tex
│   ├── 02_references.bib
│   ├── figures/  tables/       # copies via sync_figures.sh; generated tables
│   ├── VENUE.md                # current target venue + requirement checklist
│   ├── versions/INDEX.md       # snapshot table + venue history
│   └── reviews/                # R<k>-comments ↔ R<k>-response; <VENUE>-R<k>-… for journals
└── archive/
    └── INDEX.md          # one line per archived item: what, why archived, where
```

Boundary rules that do most of the anti-clutter work — enforce them and explain when violated:
- **`code/` is public as a whole; nothing private enters it.** No cards, PROJECT/CLAUDE/MANIFEST,
  tex/bib, reviews, drafts, slides, data or outputs. This replaces any whitelist `.gitignore`.
- **All code lives in `code/`**: every script whose output is reported (a card, figure, table or
  number) in `code/experiments/EXP-NNN-name/`; throwaway exploration in the private
  `experiments/EXP-NNN-name/scratch/` until a reported result depends on it, then promote it.
  Nothing lives in the project root.
- **`code/src/<package>/` never depends on a specific experiment** — no hardcoded EXP paths or constants.
- **No machine paths in `code/`.** Scripts get data, output and figure paths from
  `paperfigs/paths.py`; the private `env.sh` points them at the local data root,
  `experiments/` and `figures/`.
- **Large geodata** (rasters, point clouds, weights) is never copied into the project (it sits on
  synced Google Drive); register it in `data/MANIFEST.md` with location, format, CRS,
  resolution, temporal extent, source, size.
- **Exactly one living manuscript** (`01_main_vN.tex`); older states exist only as snapshots.

## Mode: init

1. Ask for (or infer): project name, research question, data sources, first target venue, the
   Python package name of the method, the GitHub repo name, and a local unsynced path for raw data.
2. Create the structure above.
3. Instantiate from `assets/`: `PROJECT.md`, `CLAUDE.md`, `data/MANIFEST.md`, `archive/INDEX.md`,
   `manuscript/versions/INDEX.md` (VERSIONS-INDEX template), `manuscript/VENUE.md`, the LaTeX
   skeletons and `sync_figures.sh` from `assets/manuscript/`.
4. Instantiate `code/` from `assets/code/`: `README.md`, `.gitignore` (from `gitignore.template`),
   `pyproject.toml`, `src/<package>/__init__.py`, `src/paperfigs/{__init__,paths,plotstyle}.py`,
   empty `experiments/ examples/ docs/` (with `docs/.nojekyll`), and the private `env.sh` at the
   project root with absolute paths filled in. Ask which licence (default MIT) before adding `LICENSE`.
5. Offer to set up git (`references/code-release.md` §2): `git init --separate-git-dir=<local
   unsynced path>` inside `code/`, so repository data never sits on the synced drive. Creating the
   GitHub repository and pushing are the user's call — never push without being asked.
6. The generated `CLAUDE.md` enforces the conventions in sessions where this skill does not
   trigger. Keep it under ~80 lines; it is loaded every session.
7. Fill known manifest rows and the venue now rather than leaving them empty.

## Mode: checkpoint

Session wrap-up, as a review of *what changed*:
1. **Inventory** files created/modified this session; map them to experiments.
2. **Card every experiment touched** (`assets/CARD.template.md`). The fields that matter:
   **Result** — one sentence with the number that matters, written for the researcher two weeks
   later ("NDVI input improved mIoU by 2.1 pt on Munich tiles; no gain on water"), never "see
   results.csv"; **Decision** — `adopt` / `discard` / `follow-up (EXP-NNN)`.
3. **Register new data** in `MANIFEST.md`. **New scripts in the right half?** Reported-result
   scripts in `code/experiments/`, scratch in the private `scratch/`; anything private that
   slipped into `code/` comes out now.
4. **Figures changed?** Run `scripts/check_figures.py` on them and `sync_figures.sh`; report fails.
   **Bib or citations changed?** Run `scripts/check_references.py` on the living tex files; report FAIL/WARN.
5. **Update `PROJECT.md`** and enforce the cap by demoting.
6. **Manuscript milestone?** If a round closed or something was submitted, offer a snapshot
   (not per session — that would only relocate the clutter).
7. **Sweep strays**: propose a destination for each file outside the structure; move after
   confirmation; **never delete without explicit confirmation**.
8. **Report** briefly: cards, PROJECT.md delta, figure check, strays, one-line state of the project.

If a result exists but you cannot write its one-sentence conclusion, say so — the experiment
needs another look, and flagging it beats a vague card.

## Figures and captions (mode: figures)

Read `references/figure-standard.md` before making, editing or reviewing any manuscript figure
or caption. In brief:
- Code figures: invoke the **nature-figure** skill, telling it up front *Python backend* and that
  the house standard overrides its defaults (Aptos not Arial, 84/180 mm, panel heading style);
  scripts live in `code/experiments/EXP-…/`, use `paperfigs.plotstyle` and save via `paths.fig_dir()`.
- Affinity figures: document width = printed width (84 or 180 mm), so sizes are literal.
- File names: `fig_<topic>` / `figS_<topic>` (tables `tab_` / `tabS_`), lowercase hyphen-joined
  words, one stem for .pdf/.png/`src/*.afdesign`/label `fig:<topic>`. No figure numbers (LaTeX
  numbers them), no versions, dates or `draft/` folders (old states live in snapshots).
- Typography at print: Aptos only; panel heading **a** Title (bold letter + regular sentence-case
  title) 9 pt; body 7 pt; floor 6.5 pt (AAG rejects ≤ 6 pt); lines ≥ 0.3 pt; 600 dpi.
- Captions: first sentence = the figure's claim; `\panel{a}` per panel; keys as "term, meaning";
  settings and units given; a `% source:` comment above each figure.
- Verify with `python3 scripts/check_figures.py <tex or figure files>` (exit 1 on fail); export
  submission TIFFs with `scripts/export_submission_figures.sh <Surname> <dir> figs…`.
  Paths are relative to this skill's directory.

## References (mode: references)

Read `references/reference-audit.md` before adding references or auditing them. In brief:
- **Never write a bib entry from memory.** `python3 scripts/check_references.py --lookup <DOI | arXiv id | title>`
  prints a database-built BibTeX entry; confirm a title match is the intended work. If nothing
  can be looked up, add `unverified = {reason}` and wrap the citing sentence in `\pending{}`.
- **Audit**: `python3 scripts/check_references.py manuscript/01_main_vN.tex manuscript/01_supplementary_vN.tex`
  checks tex↔bib keys, existence (Crossref/DataCite/arXiv/OpenAlex), title/author/year against
  the record, retractions and published versions of preprints. FAIL = fix; WARN = check by hand;
  ERROR = API did not answer, rerun later (never treat it as "not found"). Cached 30 days.
- **Claim support** (before submissions): `--abstracts <scratch file>` pairs each citing sentence
  with the cited abstract; read it and report citations that are not supported. Never silently
  rewrite a claim or swap a citation — list them for the user.
- When a FAIL says "not found", treat the reference as fabricated until the user confirms they
  hold the paper; do not "fix" it by finding a similar-sounding real paper.

## Code release (mode: release)

Read `references/code-release.md` before preparing `code/` for GitHub or a mirror. In brief:
- README follows `assets/code/README.template.md`; its **Reproducing the paper** table maps every
  figure, table and number group to a command, and names every `code/experiments/` folder.
- `requirements.txt` pins what was used; `pyproject.toml` lists the method's minimal dependencies.
- Before any push that matters: `python3 scripts/check_release.py code/` — private files, > 25 MB
  files, secrets, machine paths and syntax errors FAIL; personal default paths, `../../`
  escapes, data files, drafts and notebook outputs WARN. Fix every FAIL.
- **Double-anonymous review**: `check_release.py code/ --anonymous --names "<surname>,<institution>"`
  (git identity and the GitHub owner are added automatically); link only an anonymous mirror,
  never the GitHub or Pages URL.
- Committing locally is fine when asked; **pushing, creating the GitHub repo, making it public,
  and refreshing the mirror are outward-facing — do them only when the user says so.**

## Manuscript: snapshot and venue switch

Read `references/manuscript-versioning.md` before either mode. In brief:
- `01_main_vN.tex` is version N in progress. At a milestone — first full draft, closed review
  round, submission, resubmission, acceptance — freeze it as
  `versions/vNN-<VENUE>-<event>-<date>/` (tex, PDF, bib, tables, VENUE.md; plus figures when it
  leaves your hands), add an INDEX row, then **rename the living files to vN+1** and update every
  reference to the file name (project CLAUDE.md, PROJECT.md, NUMBERS.md).
- Review rounds are pairs: internal `R<k>-comments.md` ↔ `R<k>-response.md` (numbered across the
  project); journal `<VENUE>-R<k>-…`. Closing a round = response complete → snapshot → bump.
  ARS `/ars-revision-coach` can draft response content; this skill owns the files.
- Venue switch: snapshot if the text moved, record the outcome and lessons in the INDEX venue
  history, bump, replace `VENUE.md` from the template, then work through its checklist (class,
  limits, anonymity, reference style, statements, figure overrides). N never resets.
- Before any snapshot that leaves your hands, run `check_figures.py`,
  `check_references.py --report manuscript/REFERENCES_AUDIT.md` (no FAIL may remain; the report
  goes into the snapshot), the claim-support check, and `check_release.py code/` (with
  `--anonymous` for double-anonymous venues). Then tag the code commit with the snapshot name and
  record the short hash in the INDEX row, so "which code produced this version" is always answerable.
- If you are unsure which file is the submitted one (several candidates, no record), say so and
  ask the user to confirm against the journal system — a silently wrong snapshot is worse than none.

## Mode: audit

Read-only health check; propose fixes, change nothing without confirmation:
- Experiments without `CARD.md`, or cards missing Result/Decision.
- `PROJECT.md` over 150 lines, or stale (Next Steps older than the newest experiment).
- Code: scripts outside `code/`; private files inside `code/`; experiment-specific code in
  `code/src/<package>/`; `check_release.py` FAIL/WARN; experiments with a card but no public
  scripts (or the reverse); `.git` as a real directory on the synced drive.
- Outputs not referenced by any card (orphaned work).
- Data unregistered in `MANIFEST.md`; manifest rows pointing at vanished locations.
- Manuscript: more than one living draft (`*_final*.tex`, `*_old*.tex`, mismatched vN between
  main and supplement), a living vN identical in name to a snapshot but different in content,
  snapshots missing from INDEX, review comments without a paired response, no VENUE.md.
- Figures: `check_figures.py` failures and warnings (small text, mixed fonts, low dpi, names
  outside `fig_`/`figS_`); version-named files or `draft/`-style folders in `figures/`; captions
  not following the caption pattern; figures without a `% source:` comment.
- References: `check_references.py` FAIL/WARN; entries without DOI/arXiv id; `unverified` entries;
  bib entries never cited.
- Root-level clutter.

Rank findings by how much confusion they will cause in three months, not by count.

## Mode: adopt

For an existing messy project — slower and more careful than init:
1. Inventory (tree, file types, experiment clusters, data files, manuscript copies).
2. Reconstruct history: group files into experiments, draft retroactive cards from filenames,
   notebooks and results; mark unrecoverable ones honestly (`Result: unknown — predates cards`).
   For manuscripts, identify the living draft and which copy was sent where — ask when unsure.
   For code, separate what is public (method, reproduction scripts, page) into `code/` and keep
   cards, outputs and scratch private; if the project root is already a git repo with a whitelist
   `.gitignore`, propose moving its work tree to `code/` (keeping the history) rather than starting over.
3. Present a migration plan; get confirmation **before moving anything**.
4. Execute, then run a checkpoint to establish the baseline `PROJECT.md`.

## Files in this skill

- `references/figure-standard.md` — figure sizes, typography, colour, maps, caption pattern, checks
- `references/manuscript-versioning.md` — naming, version bumps, snapshots, review rounds, venue switches, Overleaf
- `references/reference-audit.md` — adding references, audit levels, claim-support check
- `references/code-release.md` — the public `code/` folder, git off the synced drive, paths, README, anonymous review, tags
- `scripts/check_figures.py` — printed-size font/dpi/font-family/name check (needs ghostscript)
- `scripts/check_references.py` — reference audit and `--lookup` (standard library, public APIs)
- `scripts/check_release.py` — pre-push check of `code/` (private files, secrets, paths, anonymity)
- `scripts/export_submission_figures.sh` — CMYK 600 dpi TIFFs named `<Surname>Figure<N>.tif`
- `assets/` — PROJECT, CARD, CLAUDE, MANIFEST, INDEX, VERSIONS-INDEX, VENUE templates;
  `manuscript/` LaTeX skeletons (`01_main_v1.tex`, `01_supplementary_v1.tex`, `02_references.bib`) and `sync_figures.sh`;
  `code/` README, gitignore, pyproject templates, `paths.py`, `plotstyle.py`, private `env.sh`

All project documents are written in **English** (they feed directly into manuscripts);
converse with the user in whatever language they use.
