# Code release: the public `code/` folder

`code/` is the project's GitHub repository. **Everything inside it is public; nothing private
ever enters it.** That one rule replaces a whitelist `.gitignore` over the whole project, where a
single wrong line publishes experiment cards, reviews or data.

## Contents
1. Layout and what goes where
2. Git setup (repository data off the synced drive)
3. Paths: how public scripts find private data and write private outputs
4. README, examples, project page
5. Before pushing: check_release.py
6. Anonymous review, tags, release

## 1. Layout and what goes where

```
<project>/
├── experiments/EXP-003-flood/      PRIVATE: CARD.md, outputs (csv, logs), scratch/
├── figures/  data/  manuscript/    PRIVATE
├── env.sh                          PRIVATE: this machine's data/output paths (§3)
└── code/                           PUBLIC = the GitHub repository
    ├── README.md  LICENSE  pyproject.toml  requirements.txt  .gitignore
    ├── src/<package>/              the method: importable, tested, no experiment-specific code
    ├── src/paperfigs/              paper support, not the method: plotstyle.py, paths.py
    ├── experiments/EXP-003-flood/  the scripts of that experiment (same name as the private dir)
    ├── examples/                   quickstart.py + a small demo dataset (< ~1 MB)
    └── docs/                       project page for GitHub Pages: index.html (+ supplement.html), .nojekyll
```

| File | Where |
|---|---|
| Reusable method code, unit tests | `code/src/<package>/` |
| Every script whose output is reported (a card, a figure, a table, a number in the paper), incl. data download (`fetch.py`) and figure scripts | `code/experiments/EXP-NNN-name/` |
| Throwaway exploration nobody depends on | `experiments/EXP-NNN-name/scratch/` (private). Promote it into `code/` the moment a reported result depends on it |
| Outputs of scripts (csv, logs, checkpoints) | private `experiments/EXP-NNN-name/`, via `paths.out_dir()` |
| Manuscript figures | private `figures/`, via `paths.fig_dir()` |
| CARD.md, PROJECT.md, AGENTS.md, CLAUDE.md, MANIFEST.md, tex, bib, reviews, Affinity sources, slides, drafts | never in `code/` |
| Project page and online supplement (final versions only) | `code/docs/`; drafts and slides stay in the private project |

The experiment directory has the same name on both sides (`code/experiments/EXP-003-flood/` ↔
`experiments/EXP-003-flood/`); the CARD names the public script as its entry point.

## 2. Git setup

Google Drive sync corrupts `.git` directories (partial syncs, lock files, conflicted copies).
Keep the repository data on a local, unsynced disk and only the work tree in the project:

```bash
cd <project>/code
git init --separate-git-dir="$HOME/git-store/<repo>.git"   # any local, unsynced path
git branch -M main
git remote add origin git@github.com:<owner>/<repo>.git
```

`code/.git` is then a one-line file pointing to the store; the work tree syncs like any other
folder. On a second machine: clone into the store with `--separate-git-dir`, or point a fresh
`code/.git` file at a local clone. Commit and push only from `code/`.

## 3. Paths

Public scripts never contain machine paths (`/Users/...`, `~/my/folders/...`, Drive paths): they
break for everyone else and identify the author during anonymous review. All paths come from
`src/paperfigs/paths.py` (template `assets/code/paths.py`):

```python
from paperfigs.paths import data_dir, out_dir, cache_dir, fig_dir, experiment_name
EXP = experiment_name(__file__)            # 'EXP-003-flood'
OUT = out_dir(EXP)                         # -> $<PKG>_OUT/EXP-003-flood/    small: tables, logs, metrics
CKPT = cache_dir(EXP) / "model.pt"         # -> $<PKG>_CACHE/EXP-003-flood/  large: checkpoints, weights
CARAVAN = data_dir("caravan")              # -> $<PKG>_DATA/caravan          raw data
fig.savefig(fig_dir() / "fig_flood-results.pdf")
```

Defaults are repo-relative (`code/data/`, `code/out/`, `code/cache/`, all git-ignored), so a fresh
clone runs. The private project overrides them in `env.sh` (template `assets/code/env.sh`),
sourced from the project root before running anything (`source env.sh`):

- `<PKG>_OUT` and `<PKG>_FIGURES` are derived from the folder it is sourced in, so they are right
  on every machine the project syncs to;
- `<PKG>_DATA` (one data root, each dataset a subfolder) and `<PKG>_CACHE` sit in one block per
  machine, keyed by `hostname -s`, on local or external, unsynced disks. The block also notes
  where that machine keeps the git store. A new machine = a new block; an unmounted data disk
  is reported when sourcing.

Large artefacts never go to `<PKG>_OUT`: it is the private `experiments/` folder on synced storage.

Install the code once into the project's environment: `pip install -e code/`.

## 4. README, examples, project page

README (template `assets/code/README.template.md`), in this order:
1. Title + one sentence: what the method does, for which decisions.
2. Paper (anonymous during review; full citation after acceptance) and project page link.
3. Install (`pip install -e .`, tested Python version).
4. Quickstart: runs `examples/quickstart.py` in under a minute on the bundled demo data.
5. Layout: one line per folder.
6. Data: table of every dataset — version, licence, link/DOI, where it goes under `$<PKG>_DATA`, the fetch command.
7. **Reproducing the paper**: a table mapping every figure, table and in-text number group to the
   command that makes it (`Fig. 4 (fig_flood-method) | python experiments/EXP-003-flood/fig_method.py`).
   Every `code/experiments/` folder appears in this table.
8. Determinism (seeds, hardware notes), citing, licence.

Requirements: `requirements.txt` pins the versions actually used; `pyproject.toml` lists the
method's minimal dependencies only. Licence: MIT unless a collaborator or data licence requires otherwise.

Project page: `docs/index.html` (+ `supplement.html`) with `docs/.nojekyll`; enable GitHub Pages
from `/docs` on `main`. Page builds are scripts too (`code/experiments/EXP-.../build_online_supplement.py`).

## 5. Before pushing: check_release.py

```bash
python3 <skill>/scripts/check_release.py code/
python3 <skill>/scripts/check_release.py code/ --anonymous --names "Surname,Institution,github-user"
```

It checks the files git would publish (tracked + untracked not ignored):

| Level | Finding |
|---|---|
| FAIL | private file type (CARD/PROJECT/AGENTS/CLAUDE/MANIFEST.md, .tex, .bib, .afdesign, .pptx, .env, keys); file > 25 MB; secret/token patterns; machine paths (`/Users/<name>`, `/home/<name>`, Drive/Dropbox/OneDrive paths); Python syntax errors; in `--anonymous` mode, any identity term (from git config, the remote owner and `--names`) in a file name or text |
| WARN | file > 5 MB; data/model formats (.tif, .nc, .pth, .parquet …) > 1 MB; personal default paths (`Path.home() / "…"`, `~/…`); paths escaping the repo (`../../`); notebooks with stored outputs; draft/backup/scratch names; non-web files in `docs/`; experiment folders missing from the README reproduction table; missing README/LICENSE/requirements/.gitignore; e-mail addresses |

Run it before every push that matters, and always before a snapshot that leaves your hands.

## 6. Anonymous review, tags, release

- **During double-anonymous review** link only an anonymous mirror (e.g. anonymous.4open.science)
  of the GitHub repo — never the GitHub or GitHub Pages URL (both contain the user name). Run
  `check_release.py --anonymous` first and refresh the mirror after each push. The manuscript's
  code availability statement points at the mirror.
- **Every snapshot that leaves your hands** (submitted, resubmitted, accepted) tags the commit
  with the snapshot's name and records the short hash in `versions/INDEX.md`:
  `git -C code tag v03-IJGIS-submitted-2026-11-02 && git -C code push --tags`.
  Reviewers' "which code produced Table 3?" is then always answerable.
- **At acceptance**: de-anonymise README and docs, make a GitHub release from the camera-ready tag,
  archive it on Zenodo for a DOI, add `CITATION.cff`, and cite the DOI in the paper's code
  availability statement.
