# AGENTS.md — SON xApp Conflict Mitigation (Thesis)

Master prompt for AI agents. Read `context/` files for the four supporting pillars.

## Principle (5th xP — non-negotiable)

1. **Research fidelity** — mirror QACM (arXiv 2405.07324v2); document every deviation from the paper in the relevant docstring or `docs/`.
2. **Modularity** — new xApps implement `BaseXApp` (ABC) and `XAppConfig`; never edit `CMC` internals to add an xApp.
3. **Reproducibility** — synthetic data only via `scripts/` with fixed `random_state`; every behaviour covered by `pytest` (>80%); CLI paths go through `cli/cli.py` → `surrogate_xapps.runner`.
4. **Layering** — data → surrogates → xApps → CMC → runner/CLI. Dependencies point downward only; no imports from `cli/` or `tests/` into `surrogate_xapps/`.
5. **No leakage** — never commit secrets, tokens, credentials, or private dataset URLs.

## Context navigation (lazy-load)

- [context/PROFILE.md](context/PROFILE.md) — who is driving the work
- [context/PRODUCT.md](context/PRODUCT.md) — what and why
- [context/PLATFORM.md](context/PLATFORM.md) — stack and environment
- [context/PROCESS.md](context/PROCESS.md) — how we work

## Folder overrides (most specific wins)

`cli/` · `data/` · `docs/` · `literature/` · `scripts/` · `surrogate_xapps/` · `tests/` · `thesis-proposal/` each carry an `AGENTS.md`; when it conflicts with this file, the folder file wins.

## Resolution order

1. `~/.agents/AGENTS.md` (global)
2. `llms.txt` (PRD, if present)
3. `.agents/AGENTS.md` (project base, if present)
4. `{repo_root}/AGENTS.md` (this file)
5. `{cwd}/AGENTS.md` (folder)

Never read above the repo root.
