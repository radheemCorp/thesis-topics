# Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Package manager | uv |
| Numerical | numpy |
| Data handling | pandas |
| Surrogate models | scikit-learn (LinearRegression, PolynomialFeatures, MLPRegressor) |
| Visualization | matplotlib |
| Testing | pytest (+ pytest-cov) |

**Notes:** scikit-learn-only for surrogates (D1 from completed xApps track). The CMC adds no heavy dependencies: pure numpy for the discrete grid heuristic and the exact brute-force test oracle; the joint 2-D candidate set is built with `np.meshgrid`.

**Deviation log:** (none)

**Dated design note (2026-10-25):** joint 2-D `(p1, p2)` bargaining is an explicit extension beyond the scalar QACM paper (track `cmc-2d_20261025`), aligned with `thesis-proposal/plan/iteration-3/spec.md` FR-4.6. No new runtime dependencies.
