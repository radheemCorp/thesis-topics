# AGENTS.md — thesis-proposal/

Scope: thesis proposal material — narrative and planning, not the implementation.

## Layout
- `glossary.md`, `open-questions.md`, `slide-deck.md` — core proposal docs.
- `plan/` — iteration plans (`iteration-1..3`).
- `literature/` — proposal-specific paper notes (distinct from root `literature/`).
- `a2c-qacm/`, `notes/`, `bak/` — A2C experiments, scratch notes, archived material.

## Rules
- Keep claims consistent with the code in `surrogate_xapps/`; link to it rather than duplicating formulas.
- Cite QACM (2405.07324v2) and any new paper by identifier.
- `bak/` is archival — do not treat as current; promote only after review.
- Do not add runnable code here; scripts belong in `scripts/`, logic in `surrogate_xapps/`.
