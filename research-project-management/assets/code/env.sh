# PRIVATE (project root, never inside code/): where this machine keeps data and where results go.
# Source before running experiments:   source env.sh
# Public scripts read these through code/src/paperfigs/paths.py.
export {{PKG_UPPER}}_DATA="{{LOCAL_DATA_ROOT}}"        # raw data on a local, unsynced disk
export {{PKG_UPPER}}_OUT="{{PROJECT_ROOT}}/experiments"   # outputs land beside each CARD.md
export {{PKG_UPPER}}_FIGURES="{{PROJECT_ROOT}}/figures"   # manuscript figures
