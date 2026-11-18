#!/bin/sh
# Turn manuscript figure PDFs into submission TIFFs (AAG Annals rules): CMYK, 600 dpi AT PRINTED WIDTH,
# LZW-compressed, named <Surname>Figure<N>.tif (fig_*) and <Surname>FigureS<N>.tif (figS_*).
# Numbers follow the order of \includegraphics in the tex, so they always match the manuscript.
# The vector PDFs stay the LaTeX source; these TIFFs are derived and never edited by hand.
#
# Usage:   sh export_submission_figures.sh <Surname> <out_dir> manuscript/01_main_v2.tex
#          sh export_submission_figures.sh <Surname> <out_dir> fig_a.pdf fig_b.pdf ...   (explicit order)
# Options: WIDTH_MM=84 ...  printed width (default 180 = full width);  DPI=300 ...  (default 600)
# Needs ghostscript and pdfinfo. Check the CMYK result by eye: saturated RGB blues/greens shift in CMYK.
set -e
[ $# -ge 3 ] || { sed -n '2,10p' "$0"; exit 1; }
surname=$1; out=$2; shift 2
width_mm=${WIDTH_MM:-180}; dpi=${DPI:-600}

if [ $# -eq 1 ] && [ "${1%.tex}" != "$1" ]; then
  tex=$1; dir=$(dirname "$tex")
  # included figures in order of appearance, comments stripped, duplicates dropped
  set -- $(sed -e 's/\([^\\]\)%.*/\1/' -e 's/^%.*//' "$tex" \
    | grep -o 'includegraphics\(\[[^]]*\]\)\{0,1\}{[^}]*}' | sed 's/.*{\(.*\)}/\1/' | awk '!seen[$0]++' \
    | while read -r f; do [ "${f%.*}" = "$f" ] && f=$f.pdf; echo "$dir/figures/$f"; done)
fi

mkdir -p "$out"
n=0; s=0
for f in "$@"; do
  case $(basename "$f") in
    figS_*) s=$((s + 1)); num=S$s ;;
    *)      n=$((n + 1)); num=$n ;;
  esac
  case $f in *.pdf) ;; *) echo "skip $f: not a PDF (export rasters by hand at ${dpi} dpi)"; continue ;; esac
  [ -f "$f" ] || { echo "MISSING $f"; continue; }
  w_pt=$(pdfinfo "$f" | awk '/Page size/ {print $3}')
  # render resolution so that the page, shrunk to width_mm, has $dpi pixels per inch
  r=$(awk -v w="$w_pt" -v mm="$width_mm" -v d="$dpi" 'BEGIN {printf "%.1f", d * (mm / 25.4) / (w / 72)}')
  dest="$out/${surname}Figure${num}.tif"
  gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=tiff32nc -sCompression=lzw -r"$r" -sOutputFile="$dest" "$f"
  echo "$(basename "$f") -> $(basename "$dest")  (${width_mm} mm, ${dpi} dpi, CMYK)"
done
