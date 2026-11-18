#!/usr/bin/env python3
"""Check manuscript figures against the house figure standard at FINAL print size.

A figure drawn on a large canvas is shrunk to the journal column width when printed,
so every font size must be judged after that scaling. This script reports, per figure:
final size, smallest text in points, fonts outside the house family, unembedded fonts,
raster resolution, and file names outside the fig_<topic> / figS_<topic> scheme.

Usage:
  python3 check_figures.py figures/*.pdf                     # full width (180 mm)
  python3 check_figures.py manuscript/01_main_v2.tex         # every \\includegraphics in the file
  python3 check_figures.py --single fig_concept fig.pdf      # these stems are single-column (84 mm)

Needs ghostscript (gs) for PDF text; pdfinfo/pdffonts (poppler) are used when present.
Exit code 1 if any figure FAILs, so it can gate a checkpoint or a submission.
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

MM_PER_PT = 25.4 / 72


def page_size_pt(pdf):
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", out)
        if m:
            return float(m.group(1)), float(m.group(2))
    m = re.search(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)", pdf.read_bytes())
    if m:
        x0, y0, x1, y1 = map(float, m.groups())
        return x1 - x0, y1 - y0
    return None


def text_spans(pdf):
    """(font, size_pt, text) for every text span on page 1, via ghostscript txtwrite."""
    out = subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-dFirstPage=1", "-dLastPage=1",
         "-sDEVICE=txtwrite", "-dTextFormat=0", "-sOutputFile=-", str(pdf)],
        capture_output=True, text=True, errors="replace").stdout
    spans = []
    for font, size, body in re.findall(
            r'<span bbox="[^"]*" font="([^"]*)" size="([\d.]+)">(.*?)</span>', out, re.S):
        txt = html.unescape("".join(re.findall(r'c="([^"]*)"', body))).strip()
        if txt:
            spans.append((clean_font(font), float(size), txt))
    return spans


def clean_font(name):
    name = name.split("+")[-1]
    return re.sub(r"-Identity-[HV]$", "", name)


def unembedded_fonts(pdf):
    if not shutil.which("pdffonts"):
        return []
    out = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    bad = []
    for line in out:
        cols = line.split()
        # columns: name type... emb sub uni id gen; 'emb' is the 5th field from the end
        if len(cols) >= 6 and cols[-5] == "no":
            bad.append(clean_font(cols[0]))
    return bad


def family_ok(font, family):
    norm = lambda s: s.lower().replace(" ", "").replace("-", "")
    return norm(font).startswith(norm(family))


def check_pdf(pdf, width_mm, args):
    res = {"fail": [], "warn": [], "info": []}
    size = page_size_pt(pdf)
    if not size:
        res["warn"].append("could not read page size")
        return res
    w_pt, h_pt = size
    scale = (width_mm / MM_PER_PT) / w_pt
    h_final = h_pt * scale * MM_PER_PT
    res["info"].append(f"canvas {w_pt * MM_PER_PT:.0f}x{h_pt * MM_PER_PT:.0f} mm -> printed {width_mm:.0f}x{h_final:.0f} mm (scale {scale:.2f})")
    if h_final > args.max_height_mm:
        res["fail"].append(f"printed height {h_final:.0f} mm exceeds {args.max_height_mm:.0f} mm (page incl. caption)")
    elif h_final > args.max_height_mm - 40:
        res["warn"].append(f"printed height {h_final:.0f} mm leaves <40 mm for the caption on a {args.max_height_mm:.0f} mm page")

    spans = text_spans(pdf)
    if not spans:
        res["warn"].append("no extractable text (outlined text or raster-only figure?) - check sizes by eye")
        return res
    sizes = defaultdict(list)
    fonts = defaultdict(list)
    for font, s, txt in spans:
        sizes[round(s * scale, 1)].append(txt)
        fonts[font].append(txt)
    smallest = min(sizes)
    small = sorted((s, t) for s, ts in sizes.items() if s < args.min_pt for t in ts)
    tiers = ", ".join(f"{s}pt" for s in sorted(sizes))
    res["info"].append(f"text sizes at print: {tiers}")
    if small:
        examples = "; ".join(f"{t[:18]!r} {s}pt" for s, t in small[:6])
        res["fail"].append(f"{len(small)} text spans below {args.min_pt} pt (smallest {smallest} pt), e.g. {examples}")
    foreign = {f: ts for f, ts in fonts.items() if not family_ok(f, args.font)}
    if foreign:
        desc = "; ".join(f"{f} ({len(ts)}x, e.g. {ts[0][:12]!r})" for f, ts in foreign.items())
        res["warn"].append(f"fonts outside {args.font}: {desc} - fine for math symbols, otherwise unify")
    for f in unembedded_fonts(pdf):
        res["fail"].append(f"font not embedded: {f}")
    return res


def check_raster(img, width_mm, args):
    res = {"fail": [], "warn": [], "info": []}
    try:
        from PIL import Image
    except ImportError:
        res["warn"].append("Pillow not installed - cannot read raster size")
        return res
    with Image.open(img) as im:
        w_px, h_px = im.size
        mode = im.mode
    dpi = w_px / (width_mm / 25.4)
    res["info"].append(f"{w_px}x{h_px} px, mode {mode} -> {dpi:.0f} dpi at {width_mm:.0f} mm")
    if dpi < 300:
        res["fail"].append(f"{dpi:.0f} dpi at print width (minimum 300, target {args.dpi})")
    elif dpi < args.dpi * 0.99:  # tolerate pixel rounding
        res["warn"].append(f"{dpi:.0f} dpi at print width (target {args.dpi})")
    if img.suffix.lower() in (".jpg", ".jpeg"):
        res["warn"].append("JPEG: never use for figures with text or linework")
    return res


NAME_RE = re.compile(r"^figS?_[a-z0-9]+(-[a-z0-9]+)*(_[a-z])?$")
STATE_RE = re.compile(r"(^|[_-])(v\d+|final|new|old|draft|test|copy|modified|backup|tmp|\d{6,8})($|[_-])", re.I)


def name_issues(path):
    """House naming (figure-standard.md section 2): fig_<topic> / figS_<topic>, no versions or dates."""
    stem = path.stem
    issues = []
    if STATE_RE.search(stem):
        issues.append(f"name '{stem}' carries a version/state/date - older states belong in manuscript snapshots")
    if not NAME_RE.match(stem):
        issues.append(f"name '{stem}' is not fig_<topic> / figS_<topic> (lowercase, hyphen-joined words)")
    return issues


def figures_from_tex(tex):
    src = re.sub(r"(?<!\\)%.*", "", tex.read_text(errors="replace"))
    m = re.search(r"\\graphicspath\{\{([^}]*)\}", src)
    base = tex.parent / (m.group(1) if m else "")
    found = []
    for name in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", src):
        p = base / name
        if not p.suffix:
            p = next((p.with_suffix(e) for e in (".pdf", ".png", ".tif", ".tiff", ".jpg") if p.with_suffix(e).exists()), p)
        if p not in found:
            found.append(p)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="figure files and/or .tex files")
    ap.add_argument("--width-mm", type=float, default=180, help="printed width of full-width figures (default 180, AAG)")
    ap.add_argument("--single-mm", type=float, default=84, help="printed width of single-column figures (default 84)")
    ap.add_argument("--single", default="", help="comma-separated figure stems printed single-column")
    ap.add_argument("--max-height-mm", type=float, default=240)
    ap.add_argument("--min-pt", type=float, default=6.5, help="smallest allowed text at print (AAG: >6 pt)")
    ap.add_argument("--font", default="Aptos", help="house font family")
    ap.add_argument("--dpi", type=int, default=600)
    args = ap.parse_args()
    if not shutil.which("gs"):
        sys.exit("ghostscript (gs) is required: brew install ghostscript")

    single = {s.strip() for s in args.single.split(",") if s.strip()}
    files = []
    for p in map(Path, args.paths):
        files += figures_from_tex(p) if p.suffix == ".tex" else [p]

    n_fail = 0
    for f in files:
        width = args.single_mm if f.stem in single else args.width_mm
        if not f.exists():
            print(f"\nFAIL  {f}\n  - file not found")
            n_fail += 1
            continue
        res = check_pdf(f, width, args) if f.suffix.lower() == ".pdf" else check_raster(f, width, args)
        res["warn"] += name_issues(f)
        status = "FAIL" if res["fail"] else "WARN" if res["warn"] else "OK"
        n_fail += status == "FAIL"
        print(f"\n{status:4s}  {f}")
        for k in ("fail", "warn", "info"):
            for msg in res[k]:
                print(f"  {'-' if k != 'info' else ' '} {msg}")
    print(f"\n{len(files)} figure(s) checked, {n_fail} failing.")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
