#!/bin/sh
# Copy every figure that the living 01_*_v*.tex files include from the project's figures/ (where the
# experiment scripts write them) into manuscript/figures/, so the manuscript folder compiles on its own.
# Run after regenerating a figure:  sh sync_figures.sh
cd "$(dirname "$0")" || exit 1
mkdir -p figures
for f in $(sed -e 's/\([^\\]\)%.*/\1/' -e 's/^%.*//' 01_*_v*.tex | grep -o 'includegraphics\[[^]]*\]{[^}]*}\|includegraphics{[^}]*}' | sed 's/.*{\(.*\)}/\1/' | sort -u); do
  if [ -f "../figures/$f" ]; then cp -p "../figures/$f" "figures/$f" && echo "copied $f"; else echo "MISSING ../figures/$f"; fi
done
