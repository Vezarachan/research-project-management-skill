#!/bin/sh
# Install the research-project-management skill for Claude Code and check its dependencies.
#   sh install.sh
# Installs to ~/.claude/skills/research-project-management (override the parent with CLAUDE_SKILLS_DIR).
# An existing copy is moved to ~/.claude/skill-backups/ first - not left inside skills/, where it
# would load as a second skill with the same name.
set -e
here=$(cd "$(dirname "$0")" && pwd)
src="$here/research-project-management"
skills_dir="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
dst="$skills_dir/research-project-management"
[ -f "$src/SKILL.md" ] || { echo "research-project-management/SKILL.md not found next to install.sh"; exit 1; }

mkdir -p "$skills_dir"
if [ -d "$dst" ]; then
  backups="$(dirname "$skills_dir")/skill-backups"
  mkdir -p "$backups"
  bak="$backups/research-project-management-$(date +%Y%m%d-%H%M%S)"
  mv "$dst" "$bak"
  echo "previous version moved to $bak"
fi
cp -R "$src" "$dst"
chmod +x "$dst"/scripts/*
echo "installed: $dst"
echo

ok()      { echo "  ok       $1"; }
missing() { echo "  MISSING  $1"; echo "           -> $2"; }
have()    { command -v "$1" >/dev/null 2>&1; }

echo "dependencies:"
if have python3; then ok "python3"; else missing "python3" "required by all scripts"; fi
if have gs; then ok "ghostscript (gs)"; else missing "ghostscript (gs)" "required by check_figures.py / export_submission_figures.sh: brew install ghostscript"; fi
if have pdfinfo; then ok "poppler (pdfinfo, pdffonts)"; else missing "poppler" "required by export_submission_figures.sh, improves check_figures.py: brew install poppler"; fi
if have python3; then
  if python3 -c "import PIL" 2>/dev/null; then ok "Pillow"; else missing "Pillow (optional)" "raster dpi checks: pip install pillow"; fi
  if python3 -c "import matplotlib" 2>/dev/null; then
    ok "matplotlib"
    if python3 -c "import sys, matplotlib.font_manager as f; sys.exit(0 if any(x.name == 'Aptos' for x in f.fontManager.ttflist) else 1)" 2>/dev/null; then
      ok "Aptos font visible to matplotlib"
    else
      missing "Aptos font for matplotlib" "install Aptos (ships with Microsoft 365, or free from Microsoft), then delete matplotlib's font cache (see README, FAQ)"
    fi
  else
    missing "matplotlib (optional)" "only needed for plotstyle.py: pip install matplotlib"
  fi
fi
if have git; then ok "git"; else missing "git" "needed for the public code/ folder and check_release.py: xcode-select --install"; fi
if have latexmk; then ok "latexmk"; else missing "latexmk (optional)" "compiling manuscripts locally (MacTeX / TeX Live)"; fi
echo
echo "Open a NEW Claude Code session to load the skill. See README.md (English) or README.zh-CN.md (中文)."
