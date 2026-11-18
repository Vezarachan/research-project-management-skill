# {{PROJECT_TITLE}} — TODO: one line: what the method does, for which decisions

TODO: Two or three sentences: the problem, what the method guarantees or improves, and on which data it was shown.

**Paper:** TODO: during review: "under review" + anonymous mirror link; after acceptance: full citation + DOI
**Project page:** TODO: docs/ link — omit during anonymous review if it reveals the account

## Install

```bash
pip install -e .            # the method only
pip install -r requirements.txt   # everything used for the paper (tested with Python {{PYTHON_VERSION}})
```

## Quickstart

```bash
python examples/quickstart.py   # runs in under a minute on the bundled demo data
```

TODO: Short walk-through of the quickstart: inputs, the one or two calls that matter, the output.

## Layout

```
src/{{PKG}}/              the method
src/paperfigs/            paper support (figure style, paths), not part of the method
examples/                 quickstart and demo data
experiments/EXP-NNN-…/    scripts that reproduce the paper, one folder per experiment
docs/                     project page (GitHub Pages)
```

Paths: data are read from `${{PKG_UPPER}}_DATA` (default `data/`), outputs go to `${{PKG_UPPER}}_OUT`
(default `out/`), figures to `${{PKG_UPPER}}_FIGURES` (default `out/figures/`).

## Data

TODO: data availability (which datasets are public). Fetch scripts download them into `${{PKG_UPPER}}_DATA`.

| Case | Dataset | Version | Licence | Link / DOI | Place under `${{PKG_UPPER}}_DATA/` | Fetch |
|---|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | TODO | `python experiments/EXP-NNN-…/fetch.py` |

## Reproducing the paper

| Paper element | Command |
|---|---|
| Fig. 1 (`fig_<topic>`) | `python experiments/EXP-NNN-…/fig_<topic>.py` |
| Table 1 | `python experiments/EXP-NNN-…/<script>.py` |
| Unit tests (once `src/{{PKG}}/tests/` exists) | `python -m pytest src/{{PKG}}/tests -q` |

## Determinism

TODO: Seeds, hardware, expected runtime of each stage, known nondeterminism (GPU).

## Citing

TODO: BibTeX — after acceptance. During review: "Citation withheld for anonymous review."

## License

{{LICENSE_NAME}} — see `LICENSE`. Data keep their own licences (table above).
