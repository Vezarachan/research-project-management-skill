# Reference audit: preventing wrong and fabricated citations

Language models misremember references in characteristic ways: a real title with the wrong
year or authors, a plausible DOI that belongs to another paper, or a paper that does not exist.
Three layers stop this, from cheapest to most expensive.

## Contents
1. Prevention: how references enter the bib
2. Automatic audit: check_references.py
3. Claim support: does the cited work say what the sentence says?
4. When to run what

## 1. Prevention: how references enter the bib

- **Never write a bib entry from memory.** Get it from the database:
  `python3 <skill>/scripts/check_references.py --lookup <DOI | arXiv id | exact title>`
  prints a BibTeX entry built from Crossref (or arXiv) with a `key = familyYEARword` key, the DOI
  and the publisher's metadata. A title lookup prints which record it matched — confirm it is
  the intended work before pasting.
- Every entry carries `doi` (or `eprint` + `archivePrefix = {arXiv}` for preprints). Books,
  reports, software and web pages without DOIs carry `url` or `isbn`.
- If a reference cannot be looked up (grey literature, a paper only remembered vaguely), add it
  with a field `unverified = {why}` — BibTeX styles ignore unknown fields, the audit lists it —
  and wrap the citing sentence in `\pending{...}` so it shows orange in the PDF.
- Cite the published version, not the preprint, once it exists.
- Keys follow `familyYEARfirstword` (`nearing2024global`); never rename a key that is already cited.

## 2. Automatic audit: check_references.py

```bash
python3 <skill>/scripts/check_references.py manuscript/01_main_vN.tex manuscript/01_supplementary_vN.tex
python3 <skill>/scripts/check_references.py --report manuscript/REFERENCES_AUDIT.md manuscript/01_main_vN.tex manuscript/01_supplementary_vN.tex
```

The bib is found from `\bibliography{}`. Only cited entries are checked online. Results are
cached for 30 days in `manuscript/.refcheck_cache.json` (reruns take seconds; `--refresh` forces
new queries). Public APIs only (Crossref, DataCite, arXiv, OpenAlex); no account, no e-mail sent.

| Level | Meaning | What to do |
|---|---|---|
| **FAIL** | cited key missing from bib · DOI does not exist · DOI belongs to a different work · arXiv id wrong · article not found in Crossref *or* OpenAlex · **retracted** · duplicate key | Fix before any snapshot that leaves your hands. A "not found" article is presumed fabricated until you hold the PDF. |
| **WARN** | first author / year differ from the record · title differs · preprint since published · same-titled record by other authors (often a book review) · book/report not in databases · `unverified` field · expression of concern · same work under two keys | Check by hand; correct the entry or note why it is right. |
| **ERROR** | an API did not answer (rate limit, network) | Not a verdict. Rerun later; only these entries are re-queried. |
| INFO | DOI found for an entry without one · bib entry never cited | Add the DOI; drop or keep unused entries deliberately. |

Exit code 1 on any FAIL, so it can gate a submission.

Tested on a planted set (fabricated article, real title with a foreign DOI, non-existent DOI,
fake arXiv id, retracted paper, wrong author/year, missing key): every one was caught, and on
the 62 references of a real manuscript it produced no false FAIL.

Limits: it confirms that a work exists and matches its metadata — not that it supports the
sentence (§3). Grey literature (agency reports, websites, software) always needs a human look.

## 3. Claim support: does the cited work say what the sentence says?

A real paper can still be cited for something it does not show. Check this before a submission
or resubmission, not every session — it costs reading.

1. `python3 <skill>/scripts/check_references.py --abstracts <scratch>/cited_abstracts.md manuscript/01_main_vN.tex ...`
   writes, per cited key, every sentence that cites it and the work's abstract (OpenAlex).
   Put the file in a scratch location, not the project.
2. Read it and classify each citation:
   **supported** · **partly** (cites more than the abstract shows) · **not evident from the
   abstract** (needs the full text) · **contradicts**.
   Prioritise sentences that carry a number, a "X showed that…" claim, or a method attribution;
   background citations ("GeoAI is increasingly used…") rarely need it.
3. Report only the non-supported ones to the user as a short list (key, sentence, why). The
   user decides; do not silently rewrite claims or swap citations.

## 4. When to run what

| Moment | Layer |
|---|---|
| Adding any reference | 1 (`--lookup`) |
| Checkpoint where `02_references.bib` or citations changed | 2 |
| Snapshot that leaves your hands (submission, resubmission, camera-ready) | 2 with `--report` (kept in the snapshot) + 3 |
| Audit mode | 2 |
| Venue switch | 2 (reference style changes often expose broken entries) |
