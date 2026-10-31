# AGENTS.md — literature/

Scope: research corpus — summaries and references, not implementation.

## Layout
- `paper-summaries/` — one folder per paper; include arXiv/DOI id in the summary.
- `oran-usecases/` — O-RAN use-case catalogue and focused studies (4.4, 4.8, 4.16, 4.26).
- `testbed-info/` — ns-3, Viavi digital twin, TU Ilmenau ICS, Colosseum, mobile-env constraints.
- `datasets/` — dataset references (QACM, Next-Gen-5G, ComMag, Viavi, Colosseum).
- `xapps/`, `material/` — xApp inventory and source PDFs.

## Rules
- Always cite the paper identifier (e.g. `2405.07324v2` for QACM); never paraphrase without the reference.
- Do not invent use-case numbers; follow the O-RAN catalogue.
- Keep summaries comparable: problem → method → metrics → relevance to QACM/CMC.
- No code changes here; link to `surrogate_xapps/` instead.
