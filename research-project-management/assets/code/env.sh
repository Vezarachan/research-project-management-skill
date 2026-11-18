# PRIVATE (project root, never inside code/). Source it from the project root before running anything:
#     source env.sh
# Project paths are taken from the folder you source it in, so the file works on every machine the
# project syncs to; machine-specific paths (data disk, cache, git store) go in one block per machine.
# Public scripts read these through code/src/paperfigs/paths.py.

if [ ! -f "$PWD/PROJECT.md" ]; then
  echo "env.sh: source it from the project root (the folder with PROJECT.md)"; return 1 2>/dev/null || exit 1
fi
export {{PKG_UPPER}}_OUT="$PWD/experiments"       # small outputs land beside each CARD.md
export {{PKG_UPPER}}_FIGURES="$PWD/figures"       # manuscript figures

case "$(hostname -s)" in
  {{HOSTNAME}})
    export {{PKG_UPPER}}_DATA="{{DATA_ROOT}}"     # raw data: local or external disk, never synced
    export {{PKG_UPPER}}_CACHE="{{CACHE_ROOT}}"   # checkpoints, weights, big intermediates: local, unsynced
    # git store of code/: {{GIT_STORE}}
    ;;
  *)
    echo "env.sh: no paths for machine '$(hostname -s)' - add a block for it (data root, cache root)"
    ;;
esac
[ -n "${{{PKG_UPPER}}_DATA}" ] && [ ! -d "${{{PKG_UPPER}}_DATA}" ] && echo "env.sh: data root not found: ${{{PKG_UPPER}}_DATA} (disk not mounted?)"
