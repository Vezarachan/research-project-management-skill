#!/usr/bin/env python3
"""Check the public code folder before pushing it to GitHub (or an anonymous mirror).

Checks the files git would publish - tracked plus untracked-but-not-ignored - for private
project files, oversized data, secrets, machine paths, broken Python, missing release files,
and, with --anonymous, anything that identifies the authors.

Usage:
  python3 check_release.py code/
  python3 check_release.py code/ --anonymous --names "Surname,Given,University,Lab"

Identity terms for --anonymous are collected automatically from git config (user.name,
user.email) and the GitHub owner of the 'origin' remote, plus --names. Read-only: writes nothing.
Exit code 1 if any FAIL.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PRIVATE_NAMES = {"CARD.md", "PROJECT.md", "CLAUDE.md", "AGENTS.md", "MANIFEST.md", "NUMBERS.md", "VENUE.md",
                 ".env", "env.sh", "id_rsa", "id_ed25519"}
PRIVATE_EXT = {".tex", ".bib", ".afdesign", ".afphoto", ".pptx", ".docx", ".key", ".pem", ".p12"}
DATA_EXT = {".tif", ".tiff", ".nc", ".h5", ".hdf5", ".pth", ".pt", ".ckpt", ".safetensors", ".npy", ".npz",
            ".parquet", ".feather", ".gpkg", ".shp", ".las", ".laz", ".zip", ".tar", ".gz", ".pkl",
            ".pickle", ".joblib", ".grib", ".grb", ".zarr", ".jp2", ".csv"}
TEXT_EXT = {".py", ".md", ".txt", ".toml", ".cfg", ".ini", ".yaml", ".yml", ".json", ".html", ".htm",
            ".js", ".css", ".sh", ".r", ".R", ".ipynb", ".tex", ".bib", ".cff", ".rst", ".svg", ""}
WEB_EXT = {".html", ".htm", ".css", ".js", ".json", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
           ".woff", ".woff2", ".ttf", ".ico", ".mp4", ".webm", ".pdf", ".txt", ".xml"}

MACHINE_PATH = re.compile(r"(/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[A-Za-z]:\\\\?Users\\\\?[A-Za-z0-9._-]+|"
                          r"GoogleDrive|CloudStorage|Google Drive|My Drive|Dropbox|OneDrive)")
PERSONAL_DEFAULT = re.compile(r"""(Path\.home\(\)\s*/\s*["'][^"']+["']|["']~/[^"'\s]+["']|expanduser\(\s*["']~/[^"']+)""")
SECRETS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "GitHub token"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"), "API secret key"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"""(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["'][^"'\s]{12,}["']"""), "hard-coded credential"),
]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
DRAFTY = re.compile(r"(^|[_\-.])(draft|old|backup|bak|copy|tmp|scratch|untitled|v\d+|final)([_\-.]|$)", re.I)


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def published_files(repo):
    """Files git would publish; falls back to a directory walk outside a git work tree."""
    if git(repo, "rev-parse", "--is-inside-work-tree"):
        top = Path(git(repo, "rev-parse", "--show-toplevel").strip())
        out = git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", ".") or ""
        files = sorted({top / f for f in out.split("\0") if f})
        return [f for f in files if f.exists()], top, True
    skip = {".git", "__pycache__", "out", "data", ".pytest_cache", "node_modules", ".ipynb_checkpoints"}
    files = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in skip]
        files += [Path(dirpath) / f for f in filenames if f != ".DS_Store"]
    return sorted(files), Path(repo), False


def identity_terms(repo, extra):
    terms = set()
    for key in ("user.name", "user.email"):
        v = (git(repo, "config", key) or "").strip()
        if v:
            terms.add(v)
            if key == "user.email":
                terms.add(v.split("@")[0])
            else:
                generic = {"test", "user", "admin", "author", "dev", "root", "the", "and", "lab"}
                terms.update(p for p in v.split() if len(p) >= 3 and p.lower() not in generic)
    remote = (git(repo, "remote", "get-url", "origin") or "").strip()
    m = re.search(r"github\.com[:/]([^/]+)/", remote)
    if m:
        terms.add(m.group(1))
    terms.update(t.strip() for t in extra.split(",") if t.strip())
    return sorted(terms, key=len, reverse=True)


def term_regex(term):
    # short terms must match as whole words; longer ones anywhere (e.g. inside a URL)
    t = re.escape(term)
    return re.compile(rf"(?<![A-Za-z]){t}(?![A-Za-z])" if len(term) <= 5 else t, re.I)


def read_text(f):
    try:
        if f.stat().st_size > 5_000_000:
            return None
        data = f.read_bytes()
        if b"\0" in data[:4096]:
            return None
        return data.decode("utf-8", "replace")
    except OSError:
        return None


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="the public code folder (git work tree)")
    ap.add_argument("--anonymous", action="store_true", help="fail on anything identifying the authors")
    ap.add_argument("--names", default="", help="extra identity terms, comma-separated (surname, institution, ...)")
    ap.add_argument("--fail-mb", type=float, default=25, help="FAIL above this size (default 25 MB)")
    ap.add_argument("--warn-mb", type=float, default=5, help="WARN above this size (default 5 MB)")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        sys.exit(f"not a folder: {repo}")
    files, top, in_git = published_files(repo)
    findings = []   # (level, file, message)
    add = lambda lv, f, msg: findings.append((lv, f.relative_to(top) if isinstance(f, Path) else f, msg))

    if not in_git:
        add("WARN", ".", "not a git work tree - checked every file in the folder (see references/code-release.md §2)")
    terms = identity_terms(repo, args.names) if args.anonymous else []
    if args.anonymous and not terms:
        add("WARN", ".", "--anonymous but no identity terms found: pass --names")
    term_res = [(t, term_regex(t)) for t in terms]

    names = {f.name for f in files}
    rel = {str(f.relative_to(top)) for f in files}
    for req, alts in (("README.md", ["README.md", "README.rst"]), ("LICENSE", ["LICENSE", "LICENSE.md", "LICENSE.txt"]),
                      ("requirements", ["requirements.txt", "pyproject.toml", "environment.yml"]), (".gitignore", [".gitignore"])):
        if not any(a in rel for a in alts):
            add("WARN", ".", f"no {req} at the repository root")

    readme = next((read_text(top / r) for r in ("README.md", "README.rst") if r in rel), "") or ""
    exp_dirs = sorted({Path(r).parts[1] for r in rel if r.startswith("experiments/") and len(Path(r).parts) > 2})
    for d in exp_dirs:
        short = re.match(r"(EXP-\d+)", d)
        if d not in readme and not (short and short.group(1) in readme):
            add("WARN", f"experiments/{d}", "not mentioned in the README (reproduction table)")

    for f in files:
        r = f.relative_to(top)
        size_mb = f.stat().st_size / 1e6
        ext = f.suffix.lower()
        if f.name in PRIVATE_NAMES or ext in PRIVATE_EXT:
            add("FAIL", f, "private project file - it belongs outside code/")
        if size_mb > args.fail_mb:
            add("FAIL", f, f"{size_mb:.1f} MB (GitHub rejects > 100 MB; keep data out of the repo)")
        elif size_mb > args.warn_mb:
            add("WARN", f, f"{size_mb:.1f} MB")
        if ext in DATA_EXT and size_mb > 1:
            add("WARN", f, f"data/model file ({size_mb:.1f} MB) - publish via a data repository and fetch script instead")
        if DRAFTY.search(f.stem):
            add("WARN", f, "name looks like a draft/backup/scratch file")
        if r.parts[0] == "docs" and ext not in WEB_EXT and f.name != ".nojekyll":
            add("WARN", f, "non-web file in docs/ (drafts and slides stay in the private project)")
        if args.anonymous:
            for t, rx in term_res:
                if rx.search(str(r)):
                    add("FAIL", f, f"file name contains identity term '{t}'")

        text = read_text(f) if ext in TEXT_EXT or ext.lower() in TEXT_EXT else None
        if text is None:
            continue
        if ext == ".ipynb":
            try:
                nb = json.loads(text)
                if any(c.get("outputs") for c in nb.get("cells", [])):
                    add("WARN", f, "notebook has stored outputs (may contain paths or data) - clear them")
            except json.JSONDecodeError:
                pass
        if ext == ".py":
            try:
                compile(text, str(f), "exec")
            except SyntaxError as e:
                add("FAIL", f, f"syntax error line {e.lineno}: {e.msg}")
        for m in MACHINE_PATH.finditer(text):
            add("FAIL", f, f"line {line_of(text, m.start())}: machine-specific path '{m.group(0)}' - use paths.py / env vars")
            break
        if ext in (".py", ".sh", ".r", ".R", ".ipynb"):
            for m in PERSONAL_DEFAULT.finditer(text):
                add("WARN", f, f"line {line_of(text, m.start())}: personal default path {m.group(0)[:70]} - make the default repo-relative")
                break
            m = re.search(r"\.\./\.\./", text)
            if m:
                add("WARN", f, f"line {line_of(text, m.start())}: path escapes the repository ('../../') - route through paths.py")
        for rx, what in SECRETS:
            m = rx.search(text)
            if m:
                add("FAIL", f, f"line {line_of(text, m.start())}: looks like a {what}")
        if args.anonymous:
            for t, rx in term_res:
                m = rx.search(text)
                if m:
                    add("FAIL", f, f"line {line_of(text, m.start())}: identity term '{t}'")
            m = EMAIL.search(text)
            if m and not m.group(0).endswith(("example.com", "noreply.github.com")):
                add("WARN", f, f"line {line_of(text, m.start())}: e-mail address '{m.group(0)}'")

    order = {"FAIL": 0, "WARN": 1}
    findings.sort(key=lambda x: (order[x[0]], str(x[1])))
    for lv, f, msg in findings:
        print(f"{lv:4s}  {f}: {msg}")
    n_fail = sum(1 for x in findings if x[0] == "FAIL")
    n_warn = len(findings) - n_fail
    total = sum(f.stat().st_size for f in files) / 1e6
    mode = "anonymous" if args.anonymous else "public"
    print(f"\n{len(files)} files would be published ({total:.1f} MB) from {top} [{mode} check]"
          + (f"; identity terms: {', '.join(terms)}" if terms else ""))
    print(f"{n_fail} FAIL, {n_warn} WARN")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
