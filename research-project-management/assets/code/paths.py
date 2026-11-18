"""Where data, outputs, large artefacts and figures live. Every script takes its paths from here.

Defaults keep everything inside this repository (data/, out/, cache/, all git-ignored), so a fresh
clone runs as is. A private research project overrides them with environment variables
(see its env.sh):

    {{PKG_UPPER}}_DATA      raw data root: one folder holding every dataset of the project, each in
                            its own subfolder (large, local disk, never in the repository)
    {{PKG_UPPER}}_OUT       small outputs (tables, logs, metrics); each experiment writes to
                            <root>/<experiment name>/ - in the project: experiments/, beside the CARD
    {{PKG_UPPER}}_CACHE     large artefacts (model checkpoints, weights, intermediate rasters,
                            predictions); local unsynced disk - never the synced project folder
    {{PKG_UPPER}}_FIGURES   manuscript figures

    from paperfigs.paths import data_dir, out_dir, cache_dir, fig_dir, experiment_name
    EXP = experiment_name(__file__)               # e.g. 'EXP-003-flood'
    OUT = out_dir(EXP)                            # metrics.csv, run.log
    CKPT = cache_dir(EXP) / "model.pt"            # big files
    LANDSAT = data_dir("landsat_munich")
"""
import os
from pathlib import Path

PREFIX = "{{PKG_UPPER}}"
REPO = Path(__file__).resolve().parents[2]      # code/  (this file is code/src/paperfigs/paths.py)


def _root(var, default):
    value = os.environ.get(f"{PREFIX}_{var}")
    return Path(value).expanduser() if value else REPO / default


def data_dir(*parts):
    """Raw data: $<PKG>_DATA/<parts>, default code/data/<parts>."""
    return _root("DATA", "data").joinpath(*parts)


def out_dir(experiment):
    """Small outputs of one experiment: $<PKG>_OUT/<experiment>/, default code/out/<experiment>/."""
    p = _root("OUT", "out") / experiment
    p.mkdir(parents=True, exist_ok=True)
    return p


def cache_dir(experiment):
    """Large artefacts of one experiment: $<PKG>_CACHE/<experiment>/, default code/cache/<experiment>/."""
    p = _root("CACHE", "cache") / experiment
    p.mkdir(parents=True, exist_ok=True)
    return p


def fig_dir():
    """Manuscript figures: $<PKG>_FIGURES, default code/out/figures/."""
    p = _root("FIGURES", "out/figures")
    p.mkdir(parents=True, exist_ok=True)
    return p


def experiment_name(file):
    """Name of the experiment folder a script lives in: experiment_name(__file__) -> 'EXP-003-flood'."""
    here = Path(file).resolve()
    for parent in here.parents:
        if parent.parent.name == "experiments":
            return parent.name
    return here.parent.name
