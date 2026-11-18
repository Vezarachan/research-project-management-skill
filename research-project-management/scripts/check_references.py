#!/usr/bin/env python3
"""Audit a manuscript's references against bibliographic databases to catch wrong or fabricated citations.

Checks
  tex <-> bib   cited keys missing from the bib (FAIL), bib entries never cited, duplicate keys/works
  existence     DOI -> Crossref (DataCite for arXiv/Zenodo DOIs); arXiv id -> arXiv;
                no identifier -> title search in Crossref, then OpenAlex
  metadata      title, first author and year compared with the database record
                (a DOI that resolves to a different title is the typical hallucination signature)
  status        retractions / expressions of concern (Crossref "updates"); arXiv preprints that
                have since been published; entries marked unverified = {...}

Usage
  python3 check_references.py manuscript/01_main_v2.tex manuscript/01_supplementary_v2.tex
  python3 check_references.py --report manuscript/REFERENCES_AUDIT.md manuscript/01_main_v2.tex
  python3 check_references.py --abstracts /tmp/cited_abstracts.md manuscript/01_main_v2.tex
  python3 check_references.py --lookup 10.1038/s41586-024-07145-1        # print a verified BibTeX entry
  python3 check_references.py --lookup "Global prediction of extreme floods in ungauged watersheds"

The bib file is taken from \\bibliography{...} in the tex (or pass a .bib directly). Results are cached
for 30 days in <bib dir>/.refcheck_cache.json; --refresh re-queries everything. Standard library only.
Exit code 1 if any FAIL.
"""
import argparse
import difflib
import hashlib
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

VERSION = "5"
UA = "research-project-management/1.0 (reference audit)"
if os.environ.get("CROSSREF_MAILTO"):   # optional, for Crossref's polite pool; never set by default
    UA += f" (mailto:{os.environ['CROSSREF_MAILTO']})"
CACHE_TTL_DAYS = 30
UNVERIFIABLE_TYPES = {"book", "techreport", "misc", "manual", "phdthesis", "mastersthesis", "unpublished", "online", "report"}


# ---------------------------------------------------------------- parsing

def parse_bib(text):
    """Minimal BibTeX parser -> list of dicts with 'ENTRYTYPE', 'ID' and lowercase field names."""
    entries, i = [], 0
    while True:
        m = re.compile(r"@(\w+)\s*([{(])").search(text, i)
        if not m:
            return entries
        etype = m.group(1).lower()
        close = "}" if m.group(2) == "{" else ")"
        j, depth = m.end(), 1
        while j < len(text) and depth:
            if text[j] in "{(":
                depth += text[j] == m.group(2)
            elif text[j] in "})":
                depth -= text[j] == close
            j += 1
        body = text[m.end():j - 1]
        i = j
        if etype in ("comment", "string", "preamble"):
            continue
        key, _, rest = body.partition(",")
        entry = {"ENTRYTYPE": etype, "ID": key.strip()}
        k = 0
        while k < len(rest):
            fm = re.compile(r"\s*([\w\-:]+)\s*=\s*").match(rest, k)
            if not fm:
                break
            name, k = fm.group(1).lower(), fm.end()
            if k < len(rest) and rest[k] == "{":
                d, s = 1, k + 1
                k += 1
                while k < len(rest) and d:
                    d += {"{": 1, "}": -1}.get(rest[k], 0)
                    k += 1
                value = rest[s:k - 1]
            elif k < len(rest) and rest[k] == '"':
                e = rest.index('"', k + 1)
                value, k = rest[k + 1:e], e + 1
            else:
                vm = re.compile(r"[^,]*").match(rest, k)
                value, k = vm.group(0).strip(), vm.end()
            entry[name] = " ".join(value.split())
            k = rest.find(",", k) + 1 if "," in rest[k:] else len(rest)
        entries.append(entry)


CITE_RE = re.compile(r"\\(?:no)?cite[a-zA-Z]*\*?(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]*)\}|\\(?:paren|text|auto|foot)cite\*?(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]*)\}")


def strip_comments(tex):
    return re.sub(r"(?<!\\)%.*", "", tex)


def cited_keys(tex):
    keys = []
    for a, b in CITE_RE.findall(strip_comments(tex)):
        keys += [k.strip() for k in (a or b).split(",") if k.strip()]
    return keys


def bib_from_tex(tex_path):
    m = re.search(r"\\(?:bibliography|addbibresource)\{([^}]+)\}", strip_comments(tex_path.read_text(errors="replace")))
    if not m:
        return None
    name = m.group(1).split(",")[0].strip()
    p = tex_path.parent / name
    return p if p.suffix == ".bib" else p.with_suffix(".bib")


# ---------------------------------------------------------------- normalisation

def plain(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\\[\'\"`^~=.]\s*", "", s)                        # symbol accents: {\~n} -> n
    s = re.sub(r"\\[uvHckbdr](?=[\s{])\s*", "", s)                # letter accents: \v{c} -> c
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s).replace("$", "")
    s = s.replace("{", "").replace("}", "").replace("&", " and ")
    s = re.sub(r"[‐-―−]", "-", s)                  # unicode hyphens/dashes survive as word breaks
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.lower()).split())


def similarity(a, b):
    a, b = plain(a), plain(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def first_family(author_field):
    if not author_field:
        return ""
    first = re.split(r"\s+and\s+", author_field)[0].strip()
    if first.startswith("{") and first.endswith("}"):      # {Organisation Name}
        return ""
    fam = first.split(",")[0] if "," in first else first.split()[-1]
    return plain(fam)


def norm_doi(d):
    d = (d or "").strip().lower()
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", d)


def arxiv_id(e):
    if e.get("eprint") and ("arxiv" in e.get("archiveprefix", "").lower() or re.match(r"^\d{4}\.\d{4,5}", e["eprint"])):
        return re.sub(r"v\d+$", "", e["eprint"].strip())
    for field in ("doi", "url", "journal", "note", "howpublished"):
        m = re.search(r"(?:arxiv[.:/ ]*(?:abs/)?|10\.48550/arxiv\.)(\d{4}\.\d{4,5})", e.get(field, ""), re.I)
        if m:
            return m.group(1)
    return None


# ---------------------------------------------------------------- HTTP

class SearchFailed(Exception):
    """A search endpoint did not answer - the entry is 'not checked', never 'not found'."""


def get(url, accept="application/json", retries=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            return e.code, ""
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            return 0, str(e)
    return 0, ""


def get_json(url):
    status, body = get(url)
    try:
        return status, json.loads(body) if status == 200 else None
    except json.JSONDecodeError:
        return status, None


# ---------------------------------------------------------------- database records -> common shape

def rec_crossref(m):
    title = " ".join(m.get("title") or [""])
    if m.get("subtitle"):
        title_full = f"{title}: {' '.join(m['subtitle'])}"
    else:
        title_full = title
    years = set()
    for k in ("issued", "published-print", "published-online", "published"):
        try:
            years.add(int(m[k]["date-parts"][0][0]))
        except (KeyError, IndexError, TypeError, ValueError):
            pass
    return {
        "source": "Crossref", "doi": norm_doi(m.get("DOI")), "title": title, "title_full": title_full,
        "families": [plain(a.get("family") or a.get("name") or "") for a in m.get("author", [])],
        "years": years, "venue": " ".join(m.get("container-title") or []), "type": m.get("type", ""),
    }


def rec_datacite(d):
    a = d["data"]["attributes"]
    t = (a.get("titles") or [{}])[0].get("title", "")
    return {
        "source": "DataCite", "doi": norm_doi(a.get("doi")), "title": t, "title_full": t,
        "families": [plain(c.get("familyName") or c.get("name", "").split(",")[0]) for c in a.get("creators", [])],
        "years": {int(a["publicationYear"])} if a.get("publicationYear") else set(),
        "venue": a.get("publisher", ""), "type": (a.get("types") or {}).get("resourceTypeGeneral", ""),
    }


def rec_openalex(w):
    return {
        "source": "OpenAlex", "doi": norm_doi(w.get("doi")), "title": w.get("title") or "",
        "title_full": w.get("title") or "",
        # full display names; names_match() looks for the family name among their tokens
        "families": [plain((a.get("author") or {}).get("display_name", "")) for a in w.get("authorships", [])],
        "years": {w["publication_year"]} if w.get("publication_year") else set(),
        "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "") or "",
        "type": w.get("type", ""),
    }


def fetch_doi(doi):
    st, js = get_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    if st == 200 and js:
        return rec_crossref(js["message"])
    st2, js2 = get_json(f"https://api.datacite.org/dois/{urllib.parse.quote(doi)}")
    if st2 == 200 and js2:
        return rec_datacite(js2)
    return None if st == 404 and st2 == 404 else "network"   # only a double 404 means "does not exist"


def fetch_arxiv(aid):
    st, body = get(f"https://export.arxiv.org/api/query?id_list={aid}", accept="application/atom+xml")
    if st != 200:
        return "network"          # arXiv answers 200 even for unknown ids, so any other status is a failure
    entry = re.search(r"<entry>(.*?)</entry>", body, re.S)
    if not entry or "<id>http://arxiv.org/api/errors" in body:
        return None
    e = entry.group(1)
    title = " ".join(re.search(r"<title>(.*?)</title>", e, re.S).group(1).split())
    names = re.findall(r"<name>(.*?)</name>", e)
    year = re.search(r"<published>(\d{4})", e)
    return {"source": "arXiv", "doi": f"10.48550/arxiv.{aid}", "title": title, "title_full": title,
            "families": [plain(n.split()[-1]) for n in names], "years": {int(year.group(1))} if year else set(),
            "venue": "arXiv", "type": "preprint"}


SKIP_TYPES = {"peer-review", "component", "grant", "paratext", "erratum", "retraction"}
PREPRINT_TYPES = {"posted-content", "preprint"}


def search_crossref(title, family="", year="", rows=8):
    q = urllib.parse.quote(" ".join(x for x in (title, family, str(year or "")) if x))
    st, js = get_json(f"https://api.crossref.org/works?query.bibliographic={q}&rows={rows}"
                      "&select=DOI,title,subtitle,author,issued,published-print,published-online,container-title,type")
    if st != 200 or not js:
        raise SearchFailed(f"Crossref search HTTP {st}")
    recs = [rec_crossref(m) for m in js["message"]["items"]]
    return [r for r in recs if r["type"] not in SKIP_TYPES and "/review" not in r["doi"]]


def search_openalex(title, rows=8):
    q = urllib.parse.quote(plain(title))
    st, js = get_json(f"https://api.openalex.org/works?search={q}&per_page={rows}")
    if st != 200 or not js:
        raise SearchFailed(f"OpenAlex search HTTP {st}")
    recs = [rec_openalex(w) for w in js.get("results", [])]
    return [r for r in recs if r["type"] not in SKIP_TYPES]


def updates_for(doi):
    """Retractions / corrections registered in Crossref for this DOI."""
    st, js = get_json(f"https://api.crossref.org/works?filter=updates:{urllib.parse.quote(doi)}&rows=10&select=DOI,update-to")
    if st != 200 or not js:
        return [("unchecked", "")]
    found = []
    for item in js.get("message", {}).get("items", []):
        for u in item.get("update-to", []):
            if norm_doi(u.get("DOI")) == doi:
                found.append((u.get("type", "update").lower(), norm_doi(item.get("DOI"))))
    return found


def names_match(fam, name):
    return bool(fam and name) and (fam == name or fam in name.split() or name in fam.split()
                                   or fam.replace(" ", "") == name.replace(" ", ""))


def bib_year(entry):
    m = re.search(r"\d{4}", entry.get("year", ""))
    return int(m.group(0)) if m else None


def author_ok(entry, rec, top=4):
    fam = first_family(entry.get("author", ""))
    return not fam or not rec["families"] or any(names_match(fam, n) for n in rec["families"][:top])


def year_ok(entry, rec):
    y = bib_year(entry)
    if not y or not rec["years"]:
        return True
    if rec["type"] in PREPRINT_TYPES or rec["source"] == "arXiv":
        return min(rec["years"]) - 1 <= y   # a preprint usually predates the cited version
    return min(abs(y - ry) for ry in rec["years"]) <= 1


def best_match(entry, candidates):
    """Pick the candidate that is the same work: title first, then author, year and a published type."""
    title = entry.get("title", "")
    scored = []
    for c in candidates:
        if not c["title"]:
            continue
        sim = max(similarity(title, c["title"]), similarity(title, c["title_full"]))
        score = sim + 0.15 * author_ok(entry, c) + 0.15 * year_ok(entry, c) - 0.05 * (c["type"] in PREPRINT_TYPES)
        scored.append((score, sim, c))
    if not scored:
        return 0.0, None
    _, sim, c = max(scored, key=lambda x: x[0])
    return sim, c


# ---------------------------------------------------------------- verification of one entry

def compare(entry, rec, problems):
    """Append metadata mismatches between bib entry and database record."""
    fam = first_family(entry.get("author", ""))
    if fam and rec["families"] and rec["families"][0] and not names_match(fam, rec["families"][0]):
        where = "is not first in" if author_ok(entry, rec) else "not among"
        problems.append(("WARN", f"first author '{fam}' {where} the record's authors ({', '.join(rec['families'][:3])})"))
    if not year_ok(entry, rec):
        problems.append(("WARN", f"year {bib_year(entry)} but record says {sorted(rec['years'])}"))


def verify(entry):
    e, problems, info = entry, [], {}
    title = e.get("title", "")
    if "unverified" in e:
        problems.append(("WARN", f"marked unverified: {e['unverified']}"))
    doi, aid = norm_doi(e.get("doi")), arxiv_id(e)

    rec = None
    if doi and not doi.startswith("10.48550/"):
        rec = fetch_doi(doi)
        if rec == "network":
            return {"status": "ERROR", "problems": [("ERROR", "network error, not checked")], "info": {}}
        if rec is None:
            problems.append(("FAIL", f"DOI {doi} does not resolve in Crossref or DataCite"))
        else:
            sim = max(similarity(title, rec["title"]), similarity(title, rec["title_full"]))
            if sim < 0.6:
                problems.append(("FAIL", f"DOI resolves to a different work: \"{rec['title'][:90]}\" ({rec['source']})"))
                rec = None
            else:
                if sim < 0.9:
                    problems.append(("WARN", f"title differs from record: \"{rec['title'][:90]}\""))
                compare(e, rec, problems)
    elif aid:
        rec = fetch_arxiv(aid)
        if rec == "network":
            return {"status": "ERROR", "problems": [("ERROR", "network error, not checked")], "info": {}}
        if rec is None:
            problems.append(("FAIL", f"arXiv:{aid} not found"))
        else:
            if similarity(title, rec["title"]) < 0.6:
                problems.append(("FAIL", f"arXiv:{aid} is a different work: \"{rec['title'][:90]}\""))
                rec = None
            else:
                compare(e, rec, problems)
                # has the preprint been published since? (best effort)
                try:
                    found = search_crossref(rec["title"], rows=5)
                except SearchFailed:
                    found = []
                sim, pub = best_match(e, [c for c in found
                                          if c["type"] in ("journal-article", "proceedings-article", "book-chapter")])
                if pub and sim >= 0.93:
                    problems.append(("WARN", f"published since as doi:{pub['doi']} ({pub['venue'][:50]}, {min(pub['years']) if pub['years'] else '?'}) - cite the published version?"))

    if rec is None and title:
        # no identifier, or the identifier was wrong: search by title
        fam, year = first_family(e.get("author", "")), e.get("year", "")
        try:
            sim, cand = best_match(e, search_crossref(title, fam, year))
            if sim < 0.9:
                sim2, cand2 = best_match(e, search_openalex(title))
                if sim2 > sim:
                    sim, cand = sim2, cand2
        except SearchFailed as err:
            return {"status": "ERROR", "problems": problems + [("ERROR", f"{err}, not checked - rerun later")], "info": info}
        if cand and sim >= 0.9 and not author_ok(e, cand) and e["ENTRYTYPE"] in UNVERIFIABLE_TYPES:
            # books are often matched by reviews of them, which carry the book's title
            problems.append(("WARN", f"only a same-titled record by other authors found ({', '.join(cand['families'][:2])}, "
                                     f"{cand['source']}; e.g. a review) - {e['ENTRYTYPE']}, check by hand"))
        elif cand and sim >= 0.9 and not author_ok(e, cand) and not year_ok(e, cand):
            # same title, but neither author nor year fits: a different work, or a badly wrong entry
            problems.append(("WARN", f"only a same-titled record with other authors/year found: "
                                     f"{', '.join(cand['families'][:2])} {sorted(cand['years'])} ({cand['source']}) - verify the entry"))
        elif cand and sim >= 0.9:
            rec = cand
            compare(e, rec, problems)
            # suggest a DOI only from a publisher record with positive author AND year evidence
            # (OpenAlex also carries repository/encyclopedia DOIs that are not the cited work)
            confident = rec["source"] == "Crossref" and rec["families"] and rec["years"] \
                and author_ok(e, rec) and year_ok(e, rec)
            if not doi and not aid and rec["doi"] and confident:
                info["suggest_doi"] = rec["doi"]
                if rec["type"] in PREPRINT_TYPES and e["ENTRYTYPE"] == "article":
                    info["suggest_note"] = "matched record is a preprint/discussion paper - use the final article's DOI"
            elif doi and rec["doi"] and rec["doi"] != doi:
                problems.append(("FAIL", f"the correct DOI is probably {rec['doi']}"))
        elif not doi and not aid:
            closest = f" Closest: \"{cand['title'][:80]}\" ({cand['source']}, {sim:.2f})." if cand and sim >= 0.6 else ""
            if e["ENTRYTYPE"] in UNVERIFIABLE_TYPES:
                problems.append(("WARN", f"not found in Crossref/OpenAlex - {e['ENTRYTYPE']}, check by hand.{closest}"))
            else:
                problems.append(("FAIL", f"not found in Crossref or OpenAlex - possibly fabricated, verify.{closest}"))
    elif not title:
        problems.append(("WARN", "entry has no title"))

    final_doi = (rec or {}).get("doi") or doi
    if final_doi and not final_doi.startswith("10.48550/") and (rec or {}).get("source") != "DataCite":
        for kind, notice in updates_for(final_doi):
            if kind == "unchecked":
                return {"status": "ERROR", "problems": problems + [("ERROR", "retraction status not checked (Crossref did not answer) - rerun later")], "info": info}
            if kind in ("retraction", "withdrawal", "removal"):
                problems.append(("FAIL", f"{kind.upper()}: notice doi:{notice}"))
            elif kind in ("expression_of_concern", "expression-of-concern"):
                problems.append(("WARN", f"expression of concern: doi:{notice}"))
            else:
                info.setdefault("updates", []).append(f"{kind} doi:{notice}")
    if rec:
        info["matched"] = f"{rec['source']}: {rec['title'][:80]}"
    status = "FAIL" if any(p[0] == "FAIL" for p in problems) else "WARN" if problems else "OK"
    return {"status": status, "problems": problems, "info": info}


# ---------------------------------------------------------------- cache

def entry_hash(e):
    keys = ("ENTRYTYPE", "title", "author", "year", "doi", "eprint", "archiveprefix", "url", "journal", "unverified")
    return hashlib.sha1(json.dumps([VERSION] + [e.get(k, "") for k in keys]).encode()).hexdigest()


def load_cache(path, refresh):
    if refresh or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    cutoff = time.time() - CACHE_TTL_DAYS * 86400
    return {k: v for k, v in data.items() if v.get("time", 0) > cutoff}


# ---------------------------------------------------------------- abstracts for the claim-support check

def citing_sentences(texts, key):
    out = []
    for tex in texts:
        flat = " ".join(strip_comments(tex).split())
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", flat):
            if any(key in [k.strip() for k in (a or b).split(",")] for a, b in CITE_RE.findall(s)):
                out.append(s[:400])
    return out


def abstract_for(doi):
    st, w = get_json(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}")
    if st != 200 or not w or not w.get("abstract_inverted_index"):
        return ""
    pos = {p: word for word, ps in w["abstract_inverted_index"].items() for p in ps}
    return " ".join(pos[i] for i in sorted(pos))


# ---------------------------------------------------------------- lookup -> BibTeX

def bib_key(rec, title):
    fam = (rec["families"][0] if rec["families"] else "anon").replace(" ", "")
    year = min(rec["years"]) if rec["years"] else ""
    stop = {"a", "an", "the", "on", "of", "for", "in", "and", "to", "with", "from", "towards", "toward"}
    word = next((w for w in plain(title).split() if w not in stop), "")
    return f"{fam}{year}{word}"


def lookup(query):
    q = query.strip()
    aid = re.search(r"(\d{4}\.\d{4,5})", q) if re.search(r"arxiv", q, re.I) or re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", q) else None
    if aid:
        rec = fetch_arxiv(aid.group(1))
        if not isinstance(rec, dict):
            sys.exit(f"arXiv {aid.group(1)} not found")
        st, body = get(f"https://export.arxiv.org/api/query?id_list={aid.group(1)}", accept="application/atom+xml")
        names = re.findall(r"<name>(.*?)</name>", body)
        authors = " and ".join(f"{n.split()[-1]}, {' '.join(n.split()[:-1])}" for n in names)
        print(f"@misc{{{bib_key(rec, rec['title'])},\n  author        = {{{authors}}},\n  title         = {{{rec['title']}}},\n"
              f"  year          = {{{min(rec['years'])}}},\n  eprint        = {{{aid.group(1)}}},\n  archivePrefix = {{arXiv}},\n"
              f"  doi           = {{10.48550/arXiv.{aid.group(1)}}}\n}}")
        return
    doi = norm_doi(q) if re.match(r"^(https?://(dx\.)?doi\.org/|doi:)?10\.\d{4,9}/", q, re.I) else None
    if not doi:
        try:
            sim, rec = best_match({"title": q}, search_crossref(q))
        except SearchFailed as err:
            sys.exit(f"{err} - try again later")
        if not rec or sim < 0.85:
            sys.exit(f"no confident match for that title (best {sim:.2f}: {rec['title'] if rec else '-'}); give the DOI instead")
        doi = rec["doi"]
        print(f"% matched by title ({sim:.2f}) - confirm this is the intended work", file=sys.stderr)
    rec = fetch_doi(doi)
    if not isinstance(rec, dict):
        sys.exit(f"DOI {doi} does not resolve")
    st, bib = get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}/transform/application/x-bibtex", accept="application/x-bibtex")
    if st != 200 or not bib.strip().startswith("@"):
        st, bib = get(f"https://doi.org/{doi}", accept="application/x-bibtex")
    if st != 200 or not bib.strip().startswith("@"):
        sys.exit(f"no BibTeX available for {doi}")
    bib = re.sub(r"^(@\w+\{)[^,]*,", lambda m: m.group(1) + bib_key(rec, rec["title"]) + ",", bib.strip(), count=1)
    if "\n" not in bib:   # Crossref returns one line: put each field on its own line
        bib = re.sub(r",\s*(\w+)\s*=\s*", r",\n  \1 = ", bib[:-1].rstrip()) + "\n}"
    print(bib)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help=".tex files (bib found via \\bibliography) and/or a .bib file")
    ap.add_argument("--report", help="write a markdown report to this path")
    ap.add_argument("--abstracts", help="write cited works' abstracts + citing sentences (for the claim-support check)")
    ap.add_argument("--lookup", help="print a verified BibTeX entry for a DOI, arXiv id or title, then exit")
    ap.add_argument("--refresh", action="store_true", help="ignore the cache")
    ap.add_argument("-v", "--verbose", action="store_true", help="also print info-only entries (DOIs to add, unused entries)")
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()

    if args.lookup:
        lookup(args.lookup)
        return
    if not args.paths:
        ap.error("give .tex and/or .bib files, or --lookup")

    texs = [Path(p) for p in args.paths if p.endswith(".tex")]
    bibs = [Path(p) for p in args.paths if p.endswith(".bib")]
    for t in texs:
        b = bib_from_tex(t)
        if b and b not in bibs:
            bibs.append(b)
    if not bibs:
        sys.exit("no .bib file found (pass it explicitly)")
    tex_texts = [t.read_text(errors="replace") for t in texs]

    entries = []
    for b in bibs:
        entries += parse_bib(b.read_text(errors="replace"))
    by_key = {}
    findings = {}   # key -> list of (level, message)
    for e in entries:
        if e["ID"] in by_key:
            findings.setdefault(e["ID"], []).append(("FAIL", "duplicate key in bib"))
        by_key[e["ID"]] = e

    cited = []
    for t in tex_texts:
        cited += cited_keys(t)
    cite_all = "*" in cited
    cited_set = {k for k in cited if k != "*"}
    if texs:
        for k in sorted(cited_set - set(by_key)):
            findings.setdefault(k, []).append(("FAIL", "cited in the text but missing from the bib"))
        if not cite_all:
            for k in sorted(set(by_key) - cited_set):
                findings.setdefault(k, []).append(("INFO", "in the bib but never cited"))

    # duplicate works under different keys
    seen_doi, seen_title = {}, []
    for e in entries:
        d = norm_doi(e.get("doi"))
        if d and d in seen_doi:
            findings.setdefault(e["ID"], []).append(("WARN", f"same DOI as '{seen_doi[d]}'"))
        elif d:
            seen_doi[d] = e["ID"]
        for other_id, other_title in seen_title:
            if e.get("title") and similarity(e["title"], other_title) >= 0.95:
                findings.setdefault(e["ID"], []).append(("WARN", f"same title as '{other_id}'"))
        seen_title.append((e["ID"], e.get("title", "")))

    # online verification of the entries that matter (cited ones, or all if no tex given)
    targets = [e for e in by_key.values() if not texs or cite_all or e["ID"] in cited_set]
    cache_path = bibs[0].parent / ".refcheck_cache.json"
    cache = load_cache(cache_path, args.refresh)
    todo = [e for e in targets if cache.get(e["ID"], {}).get("hash") != entry_hash(e)]
    print(f"{len(entries)} bib entries, {len(cited_set)} cited keys; verifying {len(targets)} ({len(targets) - len(todo)} cached)...", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for e, res in zip(todo, pool.map(verify, todo)):
            if res["status"] != "ERROR":
                cache[e["ID"]] = {"hash": entry_hash(e), "time": time.time(), "result": res}
            else:
                cache.pop(e["ID"], None)
            cache[e["ID"] + "#latest"] = res
    try:
        cache_path.write_text(json.dumps({k: v for k, v in cache.items() if not k.endswith("#latest")}, indent=0))
    except OSError:
        pass

    results = {}
    for e in targets:
        res = cache.get(e["ID"] + "#latest") or cache[e["ID"]]["result"]
        results[e["ID"]] = res
        findings.setdefault(e["ID"], []).extend(tuple(p) for p in res["problems"])
        if res["info"].get("suggest_doi"):
            note = res["info"].get("suggest_note")
            findings[e["ID"]].append(("INFO", f"found doi:{res['info']['suggest_doi']} - add it to the entry" + (f" ({note})" if note else "")))
        for u in res["info"].get("updates", []):
            findings[e["ID"]].append(("INFO", f"has a {u}"))

    order = {"FAIL": 0, "ERROR": 1, "WARN": 2, "INFO": 3}
    level = lambda fs: min((order[f[0]] for f in fs), default=9)
    rows = sorted(((k, fs) for k, fs in findings.items() if fs), key=lambda x: (level(x[1]), x[0]))
    counts = {s: sum(1 for _, fs in rows if level(fs) == order[s]) for s in order}
    n_ok = sum(1 for k, r in results.items() if r["status"] == "OK" and r["info"].get("matched")
               and level(findings.get(k, [])) >= order["INFO"])
    n_doi = sum(1 for r in results.values() if r["info"].get("suggest_doi"))
    n_unused = sum(1 for fs in findings.values() for f in fs if f[1] == "in the bib but never cited")

    lines = []
    for k, fs in rows:
        worst = min(fs, key=lambda f: order[f[0]])[0]
        if worst == "INFO" and not args.verbose:
            continue
        lines.append(f"{worst:5s} {k}")
        for lv, msg in fs:
            lines.append(f"      - [{lv}] {msg}")
    summary = (f"{n_ok} verified, {counts['FAIL']} FAIL, {counts['WARN']} WARN, {counts['ERROR']} not checked (network); "
               f"{n_doi} entries could add a DOI, {n_unused} bib entries never cited"
               f"{'' if args.verbose else ' (details: -v or --report)'}")
    print("\n".join(lines) + ("\n\n" if lines else "") + summary)

    if args.report:
        md = [f"# References audit", "", f"{time.strftime('%Y-%m-%d %H:%M')} — `{', '.join(str(p) for p in texs + bibs)}`", "",
              f"**{summary}**", "", "| Status | Key | Findings |", "|---|---|---|"]
        for k, fs in rows:
            worst = min(fs, key=lambda f: order[f[0]])[0]
            md.append(f"| {worst} | `{k}` | " + "<br>".join(f"[{lv}] {m}".replace("|", "\\|") for lv, m in fs) + " |")
        Path(args.report).write_text("\n".join(md) + "\n")
        print(f"report: {args.report}", file=sys.stderr)

    if args.abstracts:
        out = ["# Cited works: abstracts and citing sentences", "",
               "For each citation, judge whether the abstract supports the sentence that cites it:",
               "supported / partly / not evident from abstract (read full text) / contradicts.", ""]
        for k in sorted(cited_set & set(by_key)):
            e = by_key[k]
            res = results.get(k, {})
            m = (res.get("info") or {}).get("matched", "")
            d = norm_doi(e.get("doi")) or (res.get("info") or {}).get("suggest_doi", "")
            ab = abstract_for(d) if d else ""
            out += [f"## {k}", f"*{plain(e.get('title', ''))}* ({e.get('year', '?')}) {('— ' + m) if m else ''}", "",
                    "**Cited in:**"] + [f"- {s}" for s in citing_sentences(tex_texts, k)] + \
                   ["", f"**Abstract:** {ab or '(not available — check the full text)'}", ""]
        Path(args.abstracts).write_text("\n".join(out))
        print(f"abstracts: {args.abstracts}", file=sys.stderr)

    sys.exit(1 if counts["FAIL"] else 0)


if __name__ == "__main__":
    main()
