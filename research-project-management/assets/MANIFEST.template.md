# Data Manifest — {{PROJECT_NAME}}

<!-- Registry of ALL datasets used or produced by this project.
     Large files (rasters, point clouds, model weights) stay at their source
     location — only their metadata lives here. Small derived files may live
     in data/processed/. One row per dataset; keep rows current. -->

| ID | Description | Status | Location | Format | CRS | Resolution | Temporal extent | Source / provenance | Licence | Size |
|----|-------------|--------|----------|--------|-----|------------|-----------------|---------------------|---------|------|
| D001 | | | | | | | | | | |

<!-- Conventions:
     - ID: D001, D002, ... referenced from experiment cards ("data: D003").
     - Status: available | planned (not downloaded yet) | to check (disk not mounted, metadata
       unverified). Unknown metadata is written "to check", never guessed; facts the user
       stated are recorded with "(stated)" until checked against the data.
     - Planned data: Location = <data root>/<short dataset name>/, where it will be downloaded to.
     - Location: absolute path, server path (host:/path), or URL/DOI. Keep a project's datasets
       as subfolders of one data root ($<PKG>_DATA in env.sh), so scripts reach them as
       data_dir("<subfolder>").
     - Provenance: where it came from — portal + query, or "derived from D001
       by code/experiments/EXP-002-prep/preprocess.py". Derived data must name its parent and script.
     - Resolution: spatial (10 m, 0.1°) and, if relevant, point density.
     - N/A is fine for non-spatial data (e.g. model weights) — leave CRS blank. -->
