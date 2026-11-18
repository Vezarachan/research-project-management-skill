# {{Name}} — {{one line: what the method does, for which decisions}}

{{Two or three sentences: the problem, what the method guarantees or improves, and on which data it was shown.}}

**Paper:** {{during review: "under review" + anonymous mirror link; after acceptance: full citation + DOI}}
**Project page:** {{docs/ link — omit during anonymous review if it reveals the account}}

## Install

```bash
pip install -e .            # the method only
pip install -r requirements.txt   # everything used for the paper (tested with Python {{3.11}})
```

## Quickstart

```bash
python examples/quickstart.py   # runs in under a minute on the bundled demo data
```

{{Short walk-through of the quickstart: inputs, the one or two calls that matter, the output.}}

## Layout

```
src/{{pkg}}/              the method
src/paperfigs/            paper support (figure style, paths), not part of the method
examples/                 quickstart and demo data
experiments/EXP-NNN-…/    scripts that reproduce the paper, one folder per experiment
docs/                     project page (GitHub Pages)
```

Paths: data are read from `${{PKG_UPPER}}_DATA` (default `data/`), outputs go to `${{PKG_UPPER}}_OUT`
(default `out/`), figures to `${{PKG_UPPER}}_FIGURES` (default `out/figures/`).

## Data

All data used are public. Fetch scripts download them into `${{PKG_UPPER}}_DATA`.

| Case | Dataset | Version | Licence | Link / DOI | Place under `${{PKG_UPPER}}_DATA/` | Fetch |
|---|---|---|---|---|---|---|
| {{…}} | {{…}} | {{…}} | {{…}} | {{…}} | {{…}} | `python experiments/EXP-NNN-…/fetch.py` |

## Reproducing the paper

| Paper element | Command |
|---|---|
| Fig. 1 (`fig_{{topic}}`) | `python experiments/EXP-NNN-…/fig_{{topic}}.py` |
| Table 1 | `python experiments/EXP-NNN-…/{{script}}.py` |
| Unit tests | `python -m pytest src/{{pkg}}/tests -q` |

## Determinism

{{Seeds, hardware, expected runtime of each stage, known nondeterminism (GPU).}}

## Citing

{{BibTeX — after acceptance. During review: "Citation withheld for anonymous review."}}

## License

{{MIT}} — see `LICENSE`. Data keep their own licences (table above).
