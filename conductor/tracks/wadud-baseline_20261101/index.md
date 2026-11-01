# Track wadud-baseline_20261101 Context

Implements the game-theoretic baselines from Wadud, Golpayegani & Afraz (`2311.13389v1`) — arithmetic mean (AM), Nash Social Welfare (NSWF) and Eisenberg-Gale (EG) — so QACM can be compared against the method it was designed to improve on.

- [Specification](./spec.md) — metrics compared (§4) and scenarios under test (§5)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)

## Quick reference

- **Baseline paper:** http://arxiv.org/abs/2311.13389
- **Current implementation (QACM):** `2405.07324v2`
- **Thesis requirements:** `thesis-proposal/plan/iteration-3/spec.md` FR-6.2, FR-6.3, FR-8.2, FR-8.4
- **Scenarios:** S1 direct (non-priority), S2 direct (priority), S3 indirect, S4 implicit, S5 four-way, S6–S7 synthetic out-of-sample, S8 weight sweep, S9 edge cases
- **Headline metric:** per-xApp QoS satisfaction count (`n_satisfied_after`), reported alongside utility (`u_i`) and regret (`Δu_i`) so the comparison is not one-sided
