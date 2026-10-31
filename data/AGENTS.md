# AGENTS.md — data/

Scope: datasets and data reports. Two kinds live here — do not mix them.

## Layout
- `cucp_cell_report.csv`, `cucp_neighbor_report.csv`, `cucp_ue_report.csv` — real CU/CP reports (read-only source data).
- `QACM/`, `cmsORAN/` — per-xApp synthetic KPI surfaces (`Input1,Input2,Output` CSV).
- `synthetic/` — generated 2-D datasets consumed by CLI/tests.
- `data-report.md`, `data-vs-implementation.md` — what the data is and how it maps to code.

## Rules
- Never hand-edit CSV data; regenerate via `scripts/` (fixed `random_state`).
- Keep the cmsORAN column contract: `Input1,Input2,Output`.
- Update `data-vs-implementation.md` whenever a loader/column change lands.
- Large raw reports stay untracked only if `.gitignore` already covers them; do not add new binaries.
