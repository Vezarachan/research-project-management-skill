"""Where data, outputs and figures live. Every script takes its paths from here - never hard-code one.

Defaults keep everything inside this repository (data/ and out/, both git-ignored), so a fresh
clone runs as is. A private research project overrides them with environment variables
(see its env.sh):

    {{PKG_UPPER}}_DATA      raw data root (large, never in the repository)
    {{PKG_UPPER}}_OUT       output root; each experiment writes to <root>/<experiment name>/
    {{PKG_UPPER}}_FIGURES   manuscript figures

    from paperfigs.paths import data_dir, out_dir, fig_dir, experiment_name
    OUT = out_dir(experiment_name(__file__))      # e.g. <OUT root>/EXP-003-flood/
    CARAVAN = data_dir("caravan")
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
    """Outputs of one experiment: $<PKG>_OUT/<experiment>/, default code/out/<experiment>/."""
    p = _root("OUT", "out") / experiment
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
