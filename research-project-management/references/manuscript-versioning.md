# Manuscript layout, versions, revision rounds and venue switches

## Contents
1. Layout and naming
2. What the version number means
3. Taking a snapshot (and bumping the version)
4. Revision rounds (internal and journal)
5. Switching venue
6. Overleaf

## 1. Layout and naming

```
manuscript/
├── 01_main_vN.tex            # THE living main text (version N in progress)
├── 01_supplementary_vN.tex   # THE living supplement, same N
├── 02_references.bib         # one bib, unversioned
├── figures/                  # copies of ../figures/ (fig_<topic>, figS_<topic>), via sync_figures.sh
├── tables/                   # generated tab_<topic>.tex / tabS_<topic>.tex (first line names the script)
├── sync_figures.sh
├── VENUE.md                  # current target venue + its requirements (assets/VENUE.template.md)
├── NUMBERS.md                # optional: source of every number in the text
├── versions/
│   ├── INDEX.md              # snapshot table + venue history
│   └── vNN-<VENUE>-<event>-<YYYY-MM-DD>/
└── reviews/
    ├── R1-comments.md ↔ R1-response.md               # internal rounds (advisor, co-authors)
    └── <VENUE>-R1-comments.md ↔ <VENUE>-R1-response.md   # journal rounds
```

Templates: `assets/manuscript/01_main_v1.tex`, `01_supplementary_v1.tex`, `sync_figures.sh`
(elsarticle layout; swap the class when the venue needs another).

Build files (`.aux .log .bbl .fls .fdb_latexmk .out .blg .spl .synctex.gz`) are regenerable:
`latexmk -c` cleans them; they never go into snapshots.

## 2. What the version number means

`01_main_vN.tex` is **version N in progress**. N changes only at a snapshot: the snapshot keeps
vN frozen, the living files become vN+1. So the file name always says which version you are
editing, and two files called `_v3` never differ. No other copies of the main text exist —
"keep the old one before I change this" is what a snapshot is for.

## 3. Taking a snapshot (and bumping the version)

**When** — a manuscript state that left your hands or closed a round:
- first complete draft;
- end of a review round (internal or journal) once its response file is written;
- every submission and resubmission;
- camera-ready / accepted version.

Not per session, and not for outcomes: a rejection does not change the text, it is a line in
the venue history.

**Steps**
1. Compile. If the snapshot leaves your hands: run `check_figures.py` on both tex files and
   `check_references.py --report manuscript/REFERENCES_AUDIT.md` (no FAIL may remain), plus the
   claim-support check (`references/reference-audit.md` §3).
2. Create `versions/vNN-<VENUE>-<event>-<date>/` with `NN` = N zero-padded and
   `<event>` ∈ `draft · internal-R<k> · submitted · resubmitted-R<k> · accepted · camera-ready`,
   e.g. `v03-IJGIS-submitted-2026-11-02`.
3. Copy in: `01_main_vN.tex/.pdf`, `01_supplementary_vN.tex/.pdf`, `02_references.bib`, `tables/`,
   `VENUE.md`, and `REFERENCES_AUDIT.md` if one was made (not the `.refcheck_cache.json`). Add `figures/` when the snapshot leaves your hands (submitted, resubmitted,
   accepted); internal snapshots may skip it — the PDFs preserve the figures as they were.
4. Add one row to `versions/INDEX.md` (version, date, venue, event, review files, code commit,
   what changed since the previous snapshot in one sentence). If the snapshot leaves your hands,
   run `check_release.py code/` (`--anonymous` for double-anonymous venues), commit, and tag the
   commit with the snapshot name (`git -C code tag vNN-<VENUE>-<event>-<date>`); pushing the tag is
   the user's call. See `references/code-release.md` §6.
5. **Bump**: rename the living files to `_vN+1` (main and supplement), update the header comment
   of both (`% Manuscript vN+1, living draft for <venue>; previous: versions/vNN-…`), run
   `latexmk -c` for the old build files, and update every place that names the file: project
   `CLAUDE.md` (Manuscript section), `PROJECT.md` pointers, `NUMBERS.md`, any scripts that
   hard-code the name (the template `sync_figures.sh` globs, so it needs no change).
6. Never edit inside `versions/`.

For a journal's diff PDF: `latexdiff versions/v03-…/01_main_v3.tex 01_main_v4.tex > diff.tex`.

## 4. Revision rounds

Every round is a **pair** — the comments file and a response file with the same prefix.
- Internal rounds (advisor, co-authors, simulated reviewers): `R1`, `R2`, … numbered across
  the whole project, whatever the venue.
- Journal rounds: `<VENUE>-R1`, `<VENUE>-R2`; the decision letter goes at the top of the
  comments file. Rejection letters are kept too: `<VENUE>-decision-comments.md`, and the lessons
  carried over are written into the venue history.
- Response files answer every comment ID with *done / changed / disagree* + where (section,
  line, figure) — ARS `/ars-revision-coach` can draft the skeleton and response letter; this
  skill owns the file layout.
- Close a round = response complete → snapshot (`internal-R<k>` or `resubmitted-R<k>`) → bump.
- Optional companion files (e.g. `R1-agent-tasks.md`) use the same prefix so the round stays
  together in a directory listing.

## 5. Switching venue

1. Record the outcome of the old venue in the INDEX venue history (rejected / desk-rejected /
   withdrawn / not submitted), with the reviewer points worth carrying over.
2. If the current text differs from the last snapshot, snapshot it first.
3. Bump the version. Archive the old `VENUE.md` (it is already inside the snapshot) and write a
   new one from `assets/VENUE.template.md`.
4. Work through the VENUE.md checklist: document class and template, length limits (words,
   pages, figures, tables, abstract), keywords, section order, reference style (.bst), anonymity,
   required statements (data/code availability, AI-use disclosure via ARS `/ars-disclosure`,
   funding, conflicts, contributions), figure overrides of the house standard (font, panel
   letter case, formats), extra items (cover letter, highlights, graphical abstract).
5. Name everything for the new venue from here on: next snapshot `vNN-<NEWVENUE>-…`, journal
   rounds `<NEWVENUE>-R1`.

The version number never resets on a venue switch — N counts states of *this* paper.

## 6. Overleaf

If the living draft is on Overleaf: keep `manuscript/POINTER.md` with the project URL and the
current N; name the Overleaf main file `01_main_vN.tex` too and rename it there at each bump.
Snapshots are made from the Overleaf zip (Menu → Download → Source) plus the compiled PDF,
unpacked into `versions/vNN-…/` exactly as in §3.
