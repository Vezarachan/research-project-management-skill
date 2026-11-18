# House figure and caption standard

One standard for every project, so figures and captions look the same across papers.
Baseline: the *Annals of the AAG* graphics guidelines (strict on size and resolution) plus the
house panel-heading typography of the author's reference concept figure.
A venue's own rules override this file only where they conflict; record the overrides in
`manuscript/VENUE.md`.

## Contents
1. Workflow
2. File naming
3. Size and resolution
4. Typography
5. Lines, colour, maps
6. Captions
7. Checking and exporting

## 1. Workflow

- **Code figures** (plots, maps from data): where the **nature-figure** skill is installed, use it, Python
  backend. When invoking it, say "Python" up front (it otherwise stops to ask) and hand it this
  contract: house values below override its defaults (font Aptos, not Arial; widths 84/180 mm;
  panel heading style). Scripts live in `code/experiments/EXP-…/` and import
  `paperfigs.plotstyle` (copied from `assets/code/plotstyle.py` at init) instead of setting
  rcParams by hand; they save to `paperfigs.paths.fig_dir()`, which `env.sh` points at the
  project `figures/` (see `references/code-release.md` §3).
- **Schematic / composite figures** (Affinity Designer): set the document to the **printed
  width** (84 or 180 mm) before drawing, then type sizes are literal. Never design on a large
  canvas and scale down: `concept.pdf` was drawn 374 mm wide and printed at 180 mm, which
  shrank its 7.5–12 pt labels to 3.6–5.8 pt — below the 6 pt AAG floor.
- Figures are written by experiment scripts to the project `figures/`; `manuscript/figures/`
  holds copies made by `sync_figures.sh`, so the manuscript folder compiles on its own.
- Every manuscript figure has provenance in a LaTeX comment next to it (see §6) and in the
  generating experiment's CARD.md.

## 2. File naming

Names carry **meaning, not numbers**: figure numbers belong to LaTeX, and figures are reordered
in almost every revision round. A semantic name never has to change when the order does.

```
figures/
├── fig_concept.pdf            # main-text figure: fig_<topic>
├── fig_concept.png            #   600 dpi preview, same stem
├── fig_flood-results.pdf
├── figS_flood-regions.pdf     # supplementary figure: figS_<topic>
├── parts/
│   └── fig_flood-results_a.pdf    # code-made panel later assembled in Affinity: <stem>_<panel>
└── src/
    └── fig_concept.afdesign   # Affinity source, same stem as its output
manuscript/tables/
├── tab_case-settings.tex      # main-text table: tab_<topic>
└── tabS_power.tex             # supplementary table: tabS_<topic>
```

Rules:
- Pattern: `fig_` / `figS_` (tables `tab_` / `tabS_`) + topic in lowercase words joined by
  hyphens. Underscore separates fields, hyphen joins words: `fig_flood-results`, not
  `fig_flood_results` or `Fig_FloodResults`.
- Topic = what the figure is about, 1–3 words, stable for the figure's life (`concept`,
  `method`, `design`, `flood-results`, `alpha-sweep`). Case-study figures put the case first so
  they sort together: `fig_flood-method`, `fig_flood-results`.
- One stem per figure across all its files: `.pdf` (LaTeX), `.png` (preview), `src/<stem>.afdesign`,
  `parts/<stem>_<panel>.pdf`, and the LaTeX label `fig:<topic>` (`\label{fig:flood-results}`).
- **Never** put versions, states or dates in a name: no `_v2`, `_final`, `_new`, `_old`,
  `_modified`, `_draft`, `_test`, `_copy`, `_20261017`. Older states of a figure live in the
  manuscript snapshots (`versions/vNN-…/figures/`); figures still being explored live in their
  experiment directory under any name and enter `figures/` only when they go into the manuscript.
- No `draft/`, `modified/`, `old/` or dated review folders inside `figures/`.
- A figure moving between main text and supplement is renamed `fig_` ↔ `figS_` (and its label
  and `\includegraphics` updated) — the only rename the scheme ever requires.
- Submission files (`LouFigure1.tif`, `LouFigureS1.tif`) are **derived**, never hand-named:
  `export_submission_figures.sh` numbers them from the order of `\includegraphics` in the tex.

## 3. Size and resolution (at final print size)

| Item | Value |
|---|---|
| Single column | 84 mm wide |
| Full width | 180 mm wide |
| Max height | 240 mm **including caption** (keep ≥ 40 mm for it) |
| Raster resolution | 600 dpi at printed width (≥ 300 only if details stay clear) |
| LaTeX source format | vector PDF, fonts embedded (`pdf.fonttype 42`) |
| Submission format (AAG) | TIFF 600 dpi CMYK for imagery/composites; EPS or PDF for pure linework; never JPEG for text or linework |
| Submission file names (AAG) | `LouFigure1.tif`, `LouFigure2.tif`, … — generated, see §2 |
| Composite figures | one file per figure; every sub-panel meets all rules at its printed size |

## 4. Typography

All text in **Aptos** (one family per figure — no Arial/DejaVu mixing; matplotlib math via
`mathtext.fontset = custom` → Aptos, as `plotstyle.use()` sets).

| Tier | Size at print | Used for |
|---|---|---|
| Panel heading | 9 pt | bold letter + regular title, one line |
| Body | 7 pt | axis labels, legends, box text, annotations that carry the message |
| Small (floor) | 6.5 pt | tick labels, map place names, secondary notes; nothing smaller |

**Panel heading** — the house signature, taken from `concept.pdf`:
- `**a** Pecos River basin` — bold lowercase letter, one space, regular sentence-case title, same
  size, top-left of the panel, no parentheses, no final period.
- Context panels (map, data, design) take a noun phrase: `a Pecos River basin`.
- Result panels state the finding: `c Standard CRC fails to provide reliable decisions regionally`,
  `d GeoCRC keeps every region risk-controlled`.
- Order panels left→right, top→bottom (a b above c d).
- AAG asks for "A, B, C" letters: keep lowercase unless a venue *requires* uppercase; then change
  the figures and `\panel` (§6) together and note it in VENUE.md.

No figure title inside the artwork — the caption's first sentence is the title. Panel headings are fine.

## 5. Lines, colour, maps

- Lines ≥ 0.3 pt everywhere (AAG minimum); axes 0.6 pt, data lines ~1.2 pt.
- One project palette, defined once in `plotstyle.PALETTE` and reused by hex code in Affinity.
  Colour meanings are fixed across all figures of a paper (e.g. red = above tolerance / fails,
  blue = below / passes, grey = at tolerance / context, one colour per method).
- Colour must survive greyscale: pair hue with line style, marker shape or pattern where
  categories would merge. Prefer ColorBrewer-type schemes; sequential for magnitude, diverging
  around a meaningful centre (e.g. α).
- Text on a coloured area must be clearly darker or lighter than the area; labels never sit on
  a line of similar colour.
- Maps: scale bar; north arrow unless orientation is obvious; no automatic GIS basemaps
  (low-res, cluttered) — use vector or high-res basemaps with few labels; state the CRS in the
  caption or Methods.

## 6. Captions

Captions live in the LaTeX file, never in the artwork. Pattern:

```latex
% source: figures/fig_flood-results.pdf <- experiments/EXP-012-flood/plot_results.py (CARD: EXP-012)
\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{fig_flood-results.pdf}
\caption{Standard CRC misses floods in flash-flood regions; GeoCRC evens out the misses.
\panel{a}Share of floods not warned in each region, 2007--2018, under three rules at $\alpha=0.3$
(grey, at $\alpha$; red, above; blue, below).
\panel{b}Days on alert per basin-year.
\panel{c--d}...}
\label{fig:flood-results}
\end{figure}
```

Rules:
1. **First sentence = the figure's claim**, a full declarative sentence (it is the title). Context
   figures may use a descriptive sentence ("Design of the three case studies.").
2. **Every panel is described**, in order, each opened with `\panel{x}`; ranges as `\panel{b--d}`.
   Define once in the preamble: `\newcommand{\panel}[1]{\textbf{(#1)}~}` — one line to change if a
   venue wants `\textbf{#1}` or `(A)`.
3. **Symbol keys as "term, meaning"** separated by semicolons: `(red line, flood level; red dots, floods)`.
4. **Give the settings** needed to read the panel: period, region, parameter values ($\alpha$, $\lambda$),
   sample sizes, units. Every number traces to an experiment output (NUMBERS.md if the project keeps one).
5. **Interpretation only in the first sentence and, optionally, one closing take-away sentence**
   ("A smaller $\alpha$ misses fewer floods but needs more days on alert."). Panel descriptions stay factual.
6. Names: `\label{fig:<topic>}` with the topic of the file stem (§2); supplementary figures
   numbered S1, S2 via `\renewcommand{\thefigure}{S\arabic{figure}}`.
7. The `% source:` comment above every figure names the file, the generating script and the CARD.

## 7. Checking and exporting

```bash
python3 <skill>/scripts/check_figures.py manuscript/01_main_v2.tex           # all included figures
python3 <skill>/scripts/check_figures.py --single fig_concept manuscript/01_main_v2.tex
sh <skill>/scripts/export_submission_figures.sh Lou submission/figures manuscript/01_main_v2.tex
```

`check_figures.py` reports printed size, every text size after scaling, fonts outside Aptos,
unembedded fonts, raster dpi and file names that break §2; it exits 1 on any FAIL. Run it at every checkpoint where a
figure changed and always before a snapshot that leaves your hands (submission, revision).
`export_submission_figures.sh` renders CMYK TIFFs at 600 dpi of the printed width — inspect
the colours afterwards, saturated RGB shifts in CMYK.
