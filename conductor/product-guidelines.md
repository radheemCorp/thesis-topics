# Product Guidelines

## Code & Research Principles
- **Reproducibility:** every result must be reproducible via `uv run` commands and deterministic where possible (fixed random_state).
- **Modularity:** each concern (surrogate model, xApp logic, CMC) lives behind a small interface; adding a new xApp must not require editing the CMC.
- **Testability:** all logic covered by pytest (>80%); tests define expected behavior first (TDD).
- **Clarity over cleverness:** explicit, well-documented code; type hints; numpydoc-style docstrings.

## Documentation Style
- Concise, technical prose; tables for comparisons; math notation matching the QACM paper where relevant.
- Every public class/method documented; README-style run guides for demos.

## Consistency
- Follow the existing surrogate_xapps conventions (dataclass configs, ABC-based surrogates, BaseXApp template method).
