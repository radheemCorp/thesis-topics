# Specification: Surrogate CCO & ES xApps (QACM / cmsORAN-style)

**Track ID:** `surrogate-xapps_20261014`
**Status:** Draft
**Type:** Feature
**Scope:** A clean, modular Python implementation of two surrogate xApps driven by CSV datasets, producing structured control requests for a QACM Conflict Mitigation Controller (CMC).

---

## 1. Overview

Two surrogate xApps are implemented over the same dataset structure used by the **QACM** (`2405.07324v2`) and **cmsORAN** repositories:

| | **CCO xApp** (`xApp_CCO`) | **ES xApp** (`xApp_ES`) |
| :--- | :--- | :--- |
| **Role** | Coverage & Capacity Optimization | Energy Saving |
| **Objective** | **Maximize** throughput KPI (`k1`) | **Minimize** power KPI (`k2`) |
| **Features (ICPs)** | `[p1, p2]` | `[p1, p2]` |
| **Model** | Surrogate regression (poly / ANN) | Surrogate regression (poly / ANN) |
| **Output** | Structured control-request dict | Structured control-request dict |

Both xApps predict a KPI for any candidate parameter setting, then search the parameter range to select the setting that best satisfies their objective. Because their objectives are opposed over the same shared ICPs, the two xApps produce **directly conflicting control requests** — the trigger a QACM CMC is designed to resolve. This track delivers the xApps and their control-request output only; conflict *mitigation* is out of scope (see §7).

### 1.1 Design Decisions (MVP)

| # | Decision | Choice | Rationale |
| :--- | :--- | :--- | :--- |
| D1 | ML backend | **scikit-learn only** (PolynomialRegression + `MLPRegressor`) | Fastest path to a working MVP; no PyTorch/training infrastructure needed |
| D2 | ES data source | **A separate CSV file** (e.g. `data/cmsORAN/data2.csv`) | Each xApp owns its KPI curve; mirrors the cmsORAN one-KPI-per-file convention |
| D3 | Requested parameter | **Full tuple `[p1, p2]`** | Simply achievable in the MVP via a 2-D grid search; preserves both ICPs |

---

## 2. Data Contract

The QACM/cmsORAN datasets are CSV files with a **header row** and three columns in the general form `(Input1, Input2, Output)`:

```
Input1,Input2,Output
-100.0,-10.0,1.54e-20
...
```

- `Input1` → `p1` (primary ICP)
- `Input2` → `p2` (secondary ICP)
- `Output` → the KPI for that xApp
- QACM files additionally carry `normalisedKPI` and `normalised_threshold` columns; these are optional and may be used as the QoS threshold source when present.

### 2.1 Datasets used (verified in-repo)

| Role | File | Rows | `p1` range | `p2` | Peak |
| :--- | :--- | ---: | :--- | :--- | :--- |
| CCO (maximize `k1`) | `data/cmsORAN/data1.csv` | 10 000 | `[-150, 150]` | 20.0 (const) | `k1 ≈ 0.999` at `p1 ≈ -51` |
| ES (minimize `k2`) | `data/cmsORAN/data2.csv` | 10 000 | `[-150, 150]` | 60.0 (const) | `k2 ≈ 0.999` at `p1 ≈ +49` |

The opposing optima (`p1 ≈ -51` for CCO vs. `p1 ≈ +49` for ES) provide a **natural, built-in conflict** for the demonstration in `main()`.

### 2.2 Schema abstraction

The loader is schema-agnostic via a `DatasetSpec(feature_cols, target_col)` so both cmsORAN and QACM files load without code changes.

---

## 3. Functional Requirements

### FR-1 Dataset Ingestion
- FR-1.1 Load a CSV by path into feature matrix `X` (N×2) and target vector `y` (N).
- FR-1.2 Accept a configurable `DatasetSpec` mapping column names → `p1, p2, k`.
- FR-1.3 Drop rows with missing/non-numeric values; warn on the number dropped.
- FR-1.4 Raise a clear, actionable error for: missing file, malformed/empty file, missing required columns.
- FR-1.5 Return the observed parameter ranges (min/max per feature) for downstream search.

### FR-2 Surrogate Models
- FR-2.1 Provide a `PolyRegSurrogate` (PolynomialFeatures + LinearRegression pipeline).
- FR-2.2 Provide an `ANNSurrogate` (`sklearn.neural_network.MLPRegressor`).
- FR-2.3 Expose a common interface: `fit(X, y)`, `predict(X)`, `score(X, y)`.
- FR-2.4 Report held-out fit quality (`R²`) so the model choice is data-driven.
- FR-2.5 Be deterministic (`random_state` fixed).

### FR-3 CCO xApp
- FR-3.1 Train a surrogate to predict throughput `k1` from `[p1, p2]`.
- FR-3.2 Evaluate candidate `[p1, p2]` over the parameter range.
- FR-3.3 Select the candidate that **maximizes** predicted `k1`.
- FR-3.4 Expose `infer_action()` returning the control-request dict (§5).

### FR-4 ES xApp
- FR-4.1 Train a **separate** surrogate (D2: own data file) to predict power `k2`.
- FR-4.2 Evaluate candidate `[p1, p2]` over the parameter range.
- FR-4.3 Select the candidate that **minimizes** predicted `k2`.
- FR-4.4 Expose `infer_action()` returning the control-request dict (§5).

### FR-5 Decision Logic (MVP)
- FR-5.1 Build a 2-D candidate grid over `p1 × p2` from the observed ranges (configurable resolution).
- FR-5.2 Score all candidates with the surrogate in one vectorized `predict` call.
- FR-5.3 Return the best full tuple `[p1*, p2*]` per objective (D3).

### FR-6 Control-Request Schema (QACM CMC)
- FR-6.1 `infer_action()` returns a dict with the QACM CMC fields (see §5).
- FR-6.2 `target_parameter` and `requested_value` carry the **full tuple** `[p1, p2]` (MVP extension of the scalar template).
- FR-6.3 `parameter_range` carries the 2-D search bounds.
- FR-6.4 Include `predicted_kpi`, `qos_threshold`, and `priority_weight`.
- FR-6.5 Validate the payload (types/key presence) before returning.

### FR-7 Simulation & Conflict Demonstration
- FR-7.1 `main()` loads both datasets, builds and trains both xApps.
- FR-7.2 Call `infer_action()` on both xApps over the same parameter space.
- FR-7.3 Print the two control requests **side-by-side**.
- FR-7.4 Emit an explicit `CONFLICT` / `NO CONFLICT` verdict based on a configurable tolerance between requested tuples.
- FR-7.5 Provide a CLI (`--cco-file`, `--es-file`, `--model`, `--resolution`, `--out`).

### FR-8 Visualization
- FR-8.1 Plot predicted KPI curves for both xApps with requested control points marked.
- FR-8.2 Save the figure to an output directory; only call `plt.show()` in interactive mode.

---

## 4. Non-Functional Requirements

- **NFR-1 Reproducibility:** fixed RNG seeds; no network access; deterministic outputs.
- **NFR-2 Robustness:** all I/O errors handled with descriptive messages; no unhandled exception on bad input.
- **NFR-3 Performance:** full run (load + train 2 models + infer) completes in well under 2 minutes on CPU with 10k-row datasets.
- **NFR-4 Extensibility:** model, dataset, and objective are swappable without touching orchestration code.
- **NFR-5 Portability:** paths are relative/configurable; runs on Linux/macOS with the documented dependencies.
- **NFR-6 Observability:** print model `R²`, selected tuples, and predicted KPIs.

---

## 5. Control-Request Output Schema

```jsonc
{
  "xapp_id": "xApp_CCO" | "xApp_ES",
  "target_parameter": ["p1", "p2"],          // tuple (MVP extension)
  "requested_value": [<p1*>, <p2*>],         // full tuple
  "parameter_range": [[<p1_min>, <p1_max>], [<p2_min>, <p2_max>]],
  "predicted_kpi": <float>,
  "qos_threshold": <float>,
  "priority_weight": <float>
}
```

---

## 6. Acceptance Criteria

1. Loads `data/cmsORAN/data1.csv` (CCO) and `data/cmsORAN/data2.csv` (ES) without error; also loads a QACM file via `DatasetSpec` unchanged.
2. Trains both surrogates and reports `R²` for each.
3. `infer_action()` returns a schema-conformant dict for both xApps, including the full `[p1, p2]` tuple.
4. CCO requests a tuple that maximizes `k1`; ES requests a tuple that minimizes `k2` (verified against the grid).
5. `main()` prints both requests side-by-side and prints a `CONFLICT` verdict for the opposing optima.
6. Missing-file and malformed-schema inputs raise a clear, caught error (not a traceback).
7. A matplotlib figure comparing both KPI curves and control points is written to the output directory.
8. `pytest` suite passes (red→green per task).

---

## 7. Out of Scope (MVP)

- No live E2 interface, Near-RT RIC, or ns-O-RAN integration (offline CSV only).
- No PyTorch / custom ANN (sklearn `MLPRegressor` only).
- No CMC arbitration, bargaining, or conflict *resolution* — only request generation.
- No RL / online learning or retraining loop.
- No multi-cell / multi-xApp deployment; exactly two xApps over a shared parameter space.
- No QoS-threshold calibration beyond values present in the data or supplied by config.

---

## 8. References

- QACM: `literature/Rule-Based & SLA Constraint Projection/2405.07324v2.md`
- Dataset notes: `data/QACM/README.md`, `data/cmsORAN/README.md`
- Conflicting xApps: `literature/xapps/conflicing-xapps.md`
