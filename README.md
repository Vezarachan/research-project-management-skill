# research-project-management

**English** · [中文](README.zh-CN.md)

A [Claude Code](https://claude.com/claude-code) skill that keeps GeoAI and other computational
research projects **lean, consistent and traceable** while you work with an AI agent for months:
experiments, data, code, figures, references and manuscript versions each get a fixed place,
a fixed name and an automatic check.

**Version** 1.2 (2026-11-18) · **Author** Xiayin Lou (TUM) · **License** [MIT](LICENSE)

---

## Why

Long research projects with an AI agent drift in predictable ways:

| Problem | What the skill does |
|---|---|
| Results pile up and the project bloats | A **size-capped `PROJECT.md`** (150 lines) holds only the current state; finished work is demoted to experiment cards or an archive index — never deleted, never left in the always-read file |
| Results take time to understand later | Every experiment gets a **one-page card**: a one-sentence result with the number that matters, and a decision (adopt / discard / follow-up) |
| Token use grows with project memory | Each session reads only `PROJECT.md`; cards and archive are read on demand |
| Folders become a mess | A fixed layout with boundary rules: large geodata is registered, not copied; one-off exploration stays out of the code |
| Figures and captions differ between projects | One **house figure standard** (fonts, sizes at print, naming, caption pattern), checked by script |
| Many revision rounds, changing venues | One living manuscript, **immutable milestone snapshots**, paired review/response files, a per-venue checklist |
| AI-invented or wrong references | References come from databases, and an **audit against Crossref / DataCite / arXiv / OpenAlex** catches fabricated, mismatched and retracted citations |
| Private material leaks into public code | A dedicated public **`code/` folder = the GitHub repo**, and a pre-push check for private files, secrets, machine paths and (for double-anonymous review) author identity |

The principle: **compress at write time, not at cleanup time.**

## Install

```bash
git clone https://github.com/Vezarachan/research-project-management-skill.git
cd research-project-management-skill
sh install.sh
```

`install.sh` copies the skill to `~/.claude/skills/research-project-management/` (an existing copy
is moved to `~/.claude/skill-backups/`) and checks the dependencies. Start a **new** Claude Code
session afterwards. To use it in one project only, copy `research-project-management/` into that
project's `.claude/skills/` instead. For claude.ai, upload `research-project-management.skill`.

| Dependency | For | Needed |
|---|---|---|
| Python 3 (standard library) | all scripts | yes |
| Ghostscript, Poppler (`pdfinfo`, `pdffonts`) | figure checks and TIFF export | for figures |
| git | the public `code/` folder, release check | for code release |
| Network access | reference audit (public APIs, no account) | for references |
| Aptos font, matplotlib, Pillow | house plot style, raster checks | optional |

## Use

Talk to Claude Code in plain language (any language); the skill triggers on intent. You can also
invoke it explicitly with `/research-project-management`.

| When | Say | What happens |
|---|---|---|
| New project | "Initialize a research project here: question …, data in …, target journal …" | Full layout, `PROJECT.md`, rules file, data registry, LaTeX skeletons that compile, `code/` repo skeleton, check scripts in `tools/`; optional git setup with repository data off any synced drive. Nothing is invented: unknown facts are left as `TODO` |
| Daily work | nothing | The project's rules file loads every session: read `PROJECT.md` first, put files in the right place, look up references, follow the figure standard |
| End of a session | "checkpoint" | Cards for every experiment touched, new data registered, changed figures and references checked, `PROJECT.md` trimmed, stray files proposed a home |
| Figures | "make / check this figure" | House style applied; sizes checked at print size |
| References | "add this paper: <DOI or title>" / "check the citations" | Entry built from a database; full audit |
| Code release | "prepare the code for GitHub" | README reproduction table, pre-push check (`--anonymous` under review); pushing only on your say-so |
| Milestones | "I submitted today" / "reviews are back" | Checks, immutable snapshot, git tag of the code, version bump, review/response pair |
| Venue switch | "rejected, resubmitting to …" | Outcome recorded, version bump, new venue checklist |
| Health check | "audit this project" | Read-only report, ranked by how much confusion each issue will cause |
| Old project | "adopt this project" | Inventory and a migration plan; nothing moves without your confirmation |

Claude always proposes before moving files and never deletes without explicit confirmation.

## What a project looks like

```
<project>/
├── PROJECT.md          current state, ≤150 lines, read first in every session
├── AGENTS.md           the project rules (agent-neutral)
├── CLAUDE.md           one line: @AGENTS.md, so Claude Code loads the same rules
├── tools/              the check scripts and full rules (tools/references/), copied from the skill
├── env.sh              paths per machine: data root, local cache, outputs (private)
├── data/MANIFEST.md    every dataset: location, format, CRS, resolution, period, source, size
├── experiments/EXP-001-name/   private half of an experiment: CARD.md, outputs, scratch/
├── code/               PUBLIC = the GitHub repository
│   ├── src/<package>/  the method       src/paperfigs/  plot style + paths
│   ├── experiments/EXP-001-name/        the scripts of that experiment
│   ├── examples/  docs/ (project page)  README  LICENSE  pyproject.toml  requirements.txt
├── figures/            manuscript figures written by the scripts
├── manuscript/         01_main_vN.tex, 01_supplementary_vN.tex, 02_references.bib,
│                       VENUE.md, versions/ (snapshots + INDEX), reviews/
└── archive/INDEX.md    one line per archived item
```

Project rules live in `AGENTS.md` with `CLAUDE.md` importing it, so the files also work for other
agents that read `AGENTS.md`. This release is built and tested for Claude Code.

## Standards in brief

- **Figures** — drawn at printed width (84 / 180 mm); one font (Aptos by default); panel heading
  "**a** Title" 9 pt, body 7 pt, nothing below 6.5 pt; lines ≥ 0.3 pt; 600 dpi; vector PDF for LaTeX,
  CMYK TIFF for submission. Baseline: *Annals of the AAG* graphics guidelines.
- **Figure files** — `fig_<topic>` / `figS_<topic>`, never numbers, versions or dates; figure
  numbers belong to LaTeX.
- **Captions** — first sentence states the claim; every panel opens with `\panel{a}`; symbol keys
  as "term, meaning"; a `% source:` comment names the generating script.
- **Manuscript** — `01_main_vN.tex` is version N in progress; each milestone is frozen to
  `versions/vNN-<VENUE>-<event>-<date>/` and the living files move to vN+1.
- **References** — never written from memory; looked up, then audited before every submission.
- **Code** — everything in `code/` is public and nothing private enters it; no machine paths
  (`paths.py` + a private `env.sh` with one block per machine); small outputs go beside the
  experiment card, checkpoints and weights to a local unsynced cache; every snapshot that leaves
  your hands tags the code commit.

Full rules: `research-project-management/references/` (figure standard, manuscript versioning,
reference audit, code release).

## Scripts

Run from the project root (`tools/` holds copies made at init):

```bash
python3 tools/check_figures.py manuscript/01_main_v2.tex          # fonts and sizes at print, dpi, names
sh tools/export_submission_figures.sh Surname out/ manuscript/01_main_v2.tex   # CMYK 600 dpi TIFFs in figure order
python3 tools/check_references.py manuscript/01_main_v2.tex       # reference audit (cached 30 days)
python3 tools/check_references.py --lookup 10.1038/s41586-019-0912-1           # verified BibTeX entry
python3 tools/check_release.py code/ --anonymous --names "Surname,University"  # before pushing
```

Each exits with code 1 when something FAILs, so it can gate a submission. They were tested on
planted errors (fabricated, mismatched and retracted references; private files, secrets and
identity leaks in a repo; undersized figure text) and on a real project without false failures.

## Customize

| What | Where |
|---|---|
| Author block | asked at init |
| LaTeX class (elsarticle by default) | `assets/manuscript/01_main_v1.tex`; swapped at init if the venue needs another |
| Font, sizes, widths, palette | `assets/code/plotstyle.py` (+ `references/figure-standard.md`) |
| Check thresholds | script flags: `--font`, `--min-pt`, `--width-mm`, `--dpi`, `--fail-mb` |
| Crossref polite pool (optional) | `CROSSREF_MAILTO` environment variable |

Optional companions in Claude Code: the *nature-figure* skill for figure design and the
*Academic Research Skills* plugin for review responses and AI-use statements. The skill works
without them.

## License

[MIT](LICENSE) © 2026 Xiayin Lou
