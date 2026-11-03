# ICP Semantics and Testbed Data Requirements

**Question this document answers:** the two conflict-mitigation papers talk about
`p1 … p8`, but never say what most of them are. Why not — and if we wanted to
instantiate these KPIs on a real testbed, what data would each xApp need?

**Companion:** the fidelity results and outstanding reproduction work are in
[`REPORT.md`](REPORT.md). This document is about *inputs*, not results.

**Sources used** (primary text, not summaries):

| Ref | Text | Sections read |
|---|---|---|
| `2311.13389v1` | Wadud, Golpayegani, Afraz — *Conflict management in the near-RT-RIC of Open RAN: A game theoretic approach* | §V-D (utility), §V-F (use cases), §VI + Fig. 7/Fig. 8 (example model) |
| `2405.07324v2` | Wadud, Golpayegani, Afraz — *QACM: QoS-Aware xApp Conflict Mitigation in Open RAN* | §III (system model, Fig. 3), §V (benchmark), §VI (method), §VII (case studies), §VIII (practical application, Table V) |
| Repository data | `data/QACM/data1.csv … data5.csv`, `data/QACM/README.md` | column ranges and formula reconstruction |

---

## 1. How the papers describe their inputs

### 1.1 `2311.13389v1` — seven indexed parameters, one name

The paper defines the inputs as a set and never as a named inventory:

> "We represent the set of all xApps as `X = {xApp1, xApp2, …, xAppn}`, set of all
> ICPs as `P = {p1, p2, …, pm}` …"
> — §V, closed-loop description

The example model in Fig. 7 places seven ICP symbols above four xApps:

```
        p2      p1      p3      p4   p5      p6   p7
     xApp1          xApp2         xApp3        xApp4
       o1             o2            o3           o4
```

`p1` is shared by all four xApps; each remaining symbol sits above the xApp that
owns it. The ownership is confirmed by the equations below, not by the figure
alone.

Only one of the seven is ever given a name, and it is given only in prose:

> "Transmission power (TxP) is a common ICP or resource that all of these xApps
> share while functioning." — §V-F

The equations in §VI confirm the ownership implied by Fig. 7, and are the only
place where the role of each symbol is decidable:

| xApp | Function (as printed) | ICPs it uses |
|---|---|---|
| `xApp1` | `o1 = 0.5 · exp(−(p1+50)² / 2p2²)` | `p1` (shared), `p2` |
| `xApp2` | `o2 = exp(−(p1−50)² / 2p3²)` | `p1` (shared), `p3` |
| `xApp3` | `o3 = exp(−(p4+o1)² / 2p5²)` | `p4`, `p5`, and **`o1`** |
| `xApp4` | `o4 = exp(−(p7+o2)² / 2p6²)` | `p6`, `p7`, and **`o2`** |
| `xApp1′` | `o1′ = 0.6 · exp(−(p1−85)² / 2p2²)` | `p1`, `p2` |
| `xApp2′` | `o2′ = 0.35 · exp(−(p1+0)² / 2p3²)` | `p1`, `p3` |

Declared ranges (§VI, Fig. 7): `p1 ∈ [−150, 150]`, `p2 = 20`, `p3 = 60`,
`p4 ∈ [−100, 100]`, `p5 = 60`, `p6 ∈ [−50, 150]`, `p7 = 60`.

So the model has **seven inputs, one name, and six anonymous scalars** — and two
of the KPIs are functions of another xApp's KPI.

### 1.2 `2405.07324v2` — eight indexed parameters, and a table of names that does not connect

QACM has two separate descriptions of the inputs, and they never meet.

**Description A — the experimental model (Fig. 3).** A bare table of ranges with
no names:

| | Value | | Value |
|---|---|---|---|
| `p1` | `[−100, 100]` | `p5` | `−20` |
| `p2` | `[−10, 50]` | `p6` | `[−50, 150]` |
| `p3` | `−20` | `p7` | `60` |
| `p4` | `60` | `p8` | `[−100, 150]` |

**Description B — the real-world mapping (Table V).** Five SON functions with
their genuine ICP names:

| xApp | ICPs | Objective |
|---|---|---|
| MLB | TTT, CIO, TXP, RET | Minimise load, maximise resource use |
| CCO | TXP, RET | Maximise downlink throughput, minimise SINR |
| ES | TXP | Maximise energy efficiency, minimise power use |
| MRO | TXP, TTT, CIO, NL, HYS | Maximise handover rate, minimise call drops/blocks |

Table V is explicitly **cited from Banerjee et al. [17]**, not derived in this
paper. It is used in §VIII to argue that four *real* direct conflicts exist
(everyone shares TXP; MLB vs CCO over RET; MLB vs MRO over CIO and TTT) and one
indirect conflict (MLB → MRO through the handover-boundary parameter group).

**The two descriptions are never linked.** `p1 … p8` are never equated with
TTT/CIO/TXP/RET/NL/HYS. The only place a physical unit appears anywhere is the
MATLAB study in §VIII-A, which uses `TXP ∈ [6, 40] dBm` — and that study does not
use `p1 … p8` at all; it uses measured throughput and power.

The KPI equations (§III) show what each anonymous symbol actually does:

| KPI | Function (as printed) | Symbols used |
|---|---|---|
| `k1` | `80 · exp(−(p1+0)² / 2p2²)` | `p1`, `p2` |
| `k2` | `100 · exp(−(p1+p3)² / 2p2²)` | `p1`, `p2`, `p3` |
| `k3` | `120 · exp(−(p1+45)² / 2p4²)` | `p1`, `p4` |
| `k41` | `120 · exp(−(p6+(p2−30))² / 2p5²)` | `p6`, `p2`, `p5` |
| `k42` | `150 · exp(−(p6+(p2−50))² / 2p5²)` | `p6`, `p2`, `p5` |
| `k5` | `−35 · exp(−(p8+(p1−25))² / 2p7²)` | `p8`, `p1`, `p7` |

QoS thresholds (§III): `q1 = 55`, `q2 = 95`, `q3 = 85`, `q41 = 75`,
`q42 = 80`, `q5 = −25`.

Parameter groups (§III), which define the conflict topology:

- `PkG41 = PkG42 = {p2, p5, p6}` — x4's KPIs
- `PkG5 = {p7, p8}` — extended to `{p1, p7, p8}` once an implicit conflict with
  `p1` is "detected"

---

## 2. Why no name is attached to the inputs

Five distinct reasons, in order of importance.

### 2.1 The framework is deliberately parameter-agnostic

The CMC is specified to work for *any* conflicting ICP. The database schema
makes this explicit: the PGD component stores "parameters that influence the
same area in the network" — an arbitrary grouping — and the RCP component stores
"recently changed parameters" by timestamp. Nothing in the architecture requires
knowing *what* the parameter is. Using `p1 … pm` is therefore a design choice
consistent with the system, not laziness.

The cost is that the evaluation model inherits the abstraction: the experiment
can only speak about `p1`, never about transmit power.

### 2.2 The only real names are borrowed from a different paper

QACM's Table V is a quotation of Banerjee et al. [17]. It tells you which ICPs
the SON functions *would* contend over in a real network. It is not the data
model. Because the paper never maps Table V onto Fig. 3, the reader is left with
six real ICP names and eight anonymous symbols and no correspondence between
them.

### 2.3 The KPIs are staging functions, not measurements

The Gaussian forms are chosen so the *conflict topology* appears:

- `k1` peaks at `p1 = 0`, `k2` at `−p3 = +20`, `k3` at `−45` → three-way direct
  conflict over `p1`
- `k41`/`k42` peak at `p2 = 30` and `p2 = 50` → x4 responds to `p2` without
  owning it
- `k5` peaks at `p1 = 25 − p8` → x5 responds to `p1` without owning it

Amplitudes (80, 100, 120, 150, −35) and offsets (0, +20, −45, 30, 50, 25) are
chosen to make thresholds discriminating. They are not fitted to or sampled from
measured KPIs. Naming the symbol would invite the question "measured where?",
which the model cannot answer.

Wadud says this plainly: the outputs "follow a Gaussian distribution function, as
it often mirrors real-life scenarios [10]" — i.e. a shape assumption justified by
plausibility.

### 2.4 The published datasets themselves are column-indexed

`data/QACM/` does not use `p_i` as headers. Every file is `Input1, Input2, …,
Output`. The mapping from column to paper symbol is recoverable **only from the
value ranges** — see §3. So even the artifact behind the paper declines to name
its inputs.

### 2.5 Most of the "ICPs" are not control parameters at all

This is the decisive reason, and it is visible only once the equations are read
as functions of the swept variable. Decomposing each Gaussian into
`amplitude × exp(−(location)² / (2·width²))`:

| Symbol | Role in the KPI model | Is it something an xApp can "set"? |
|---|---|---|
| `p1` | location (centre of `k1`, `k2`, `k3`, `k5`) | **Yes** — a knob that moves the peak |
| `p2` | width of `k1`,`k2`; **location** of `k41`,`k42` | Ambiguous — two incompatible roles |
| `p3` | constant `−20`, centre offset of `k2` | No — a fixed model coefficient |
| `p4` | constant `60`, width of `k3` | No — a fixed model coefficient |
| `p5` | constant `−20`, width of `k41`,`k42` | No — a fixed model coefficient |
| `p6` | location term of `k41`,`k42` | Per-row variable, but a shape term |
| `p7` | constant `60`, width of `k5` | No — a fixed model coefficient |
| `p8` | location term of `k5` | Per-row variable, but a shape term |

Only `p1` behaves like a parameter a network function would adjust. The rest are
the Gaussian's width and offset terms. A testbed cannot "deliver `p3 = −20`"
because `p3` is not a quantity in the network — it is a coefficient of the
simulation.

This is why the paper only ever demonstrates conflicts over `p1` and `p2`, and
why `p2` is the awkward case: it is a *width* in `k1`/`k2` and a *location* in
`k41`/`k42`. A single physical variable can legitimately affect both the shape
and the position of a KPI curve, but then the printed equations cannot also
produce Case A's reported peaks at `p2 = 18` and `p2 = 25` (see P4). Either the
symbol means different things in different figures, or the figures were generated
from unpublished equations.

---

## 3. What the shipped datasets actually encode

Reconstructing the column-to-symbol mapping from the declared ranges, and then
verifying it against the formulas:

| File | Columns | Reconstructed mapping | Max abs. error vs. formula |
|---|---|---|---|
| `data1.csv` | `Input1, Input2 → Output` | `p1 ∈ [−100,100]`, `p2 ∈ [−10,50]` → `k1` | `2.8e-14` |
| `data2.csv` | `Input1..3 → Output` | `p1`, `p2`, `p3 = −20` → `k2` | `3.6e-14` |
| `data3.csv` | `Input1, Input2 → Output` | `p1`, `p4 = 60` → `k3` | `2.8e-14` |
| `data4.csv` | `Input1..4 → Output1, Output2` | `p6 ∈ [−50,150]`, `p5 = −20`, `p2`, **`p2` again** → `k41`, `k42` | `7.1e-14` |
| `data5.csv` | `Input1..3 → Output` | `p8 ∈ [−100,150]`, `p7 = 60`, `p1 ∈ [−100,100]` → `k5` | `1.1e-14` |

(Errors are floating-point round-off; the formulas reproduce the files exactly.)

Three things this establishes:

1. **The mapping is inferable and the formulas are exact.** The 10 000 rows are
   the printed equations evaluated on a grid; there is no measurement noise and
   no hidden model. A faithful reproduction is therefore a data-mapping problem,
   not a modelling problem.
2. **`data4.csv` contains a duplicated column.** `Input3` and `Input4` are
   identical for all 10 000 rows. `k41`/`k42` need only `p6`, `p5`, `p2`. The
   fourth column is redundant.
3. **The normalisation is sample statistics.** `normalisedKPI` is
   `(k − μ)/σ` with `σ` computed over the file (`ddof = 0`), and
   `normalised_threshold` is `(q − μ)/σ` using the same statistics. I verified
   this to machine precision for all five files and all six KPIs.

Point 3 matters beyond bookkeeping: the *normalised* threshold — and therefore
which points count as "satisfied" — depends on the sampling grid, not only on
the KPI. Re-normalising on a 1-D sweep instead of the paper's 2-D grid moves
`q′5` from `−0.56` to `−0.35`, which is enough to flip satisfaction near the
boundary. The paper's satisfaction counts are therefore partly a property of its
sampling, and a reproduction that uses a different grid is not comparing like
with like unless the normalisation is held fixed.

---

## 4. What a testbed must supply, per xApp

The papers' own named mapping (QACM Table V) plus each xApp's stated objective
gives a much more concrete data list than the Gaussian formulas do. The
inference is: *the KPI is the quantity the xApp is trying to move; the ICPs are
the knobs it is allowed to turn.*

**Caveat.** Wadud names all four xApps (MLB, CCO, ES, MRO). QACM uses `x1 … x5`
and names only the ES-vs-CCO pair in its MATLAB study; `x5` is never identified.
Everything below is therefore paper-grounded for the four SON functions and
inferred for `x5`.

### 4.1 MLB (`xApp1` / `x1`)

| Item | Detail |
|---|---|
| ICPs (Table V) | TTT, CIO, TXP, RET |
| What it optimises | Load balance across cells; minimise load, maximise resource use |
| KPI to measure | PRB load spread across cells; active UEs per cell; HO distribution |
| Required series | `PRB.UsedDl` / `PRB.AvailDl` per cell; `Z_{c,t}` active UEs per cell; HO counts per (source, target) pair; RSRP/SINR for cell-edge UEs |
| E2 / O1 source | E2SM-KPM Style 1 (cell aggregate); HO data from RRC / ANR; CIO, TTT, RET from O1 configuration |
| Window | 1–10 s (load is slow-moving) |
| Aggregation | mean load per cell; spread = max − min across cells |

### 4.2 CCO (`xApp2` / `x2`)

| Item | Detail |
|---|---|
| ICPs (Table V) | TXP, RET |
| What it optimises | Downlink throughput, coverage |
| KPI to measure | DL throughput (mean and cell-edge), coverage fraction, SINR |
| Required series | `DRB.UEThpDl`, `RSRP`, `SINR`, `CQI`, PRB utilisation |
| E2 / O1 source | E2SM-KPM Style 2 (per-UE periodic) + Style 1 (cell); TXP via O1 or E2SM-RC Style 8; RET via O1 |
| Window | 1 s |
| Aggregation | 5th-percentile UE throughput for the QoS claim, mean for the paper comparison |

### 4.3 ES (`xApp3` / `x3`)

| Item | Detail |
|---|---|
| ICPs (Table V) | TXP |
| What it optimises | Energy efficiency; minimise power use |
| KPI to measure | Power consumption (W / Wh); energy-saving ratio, subject to a coverage constraint |
| Required series | Per-cell `TxPower`; PA efficiency; energy counters; plus RSRP/throughput to prove no outage |
| E2 / O1 source | **No E2 KPI.** O1 PM (`PEE.Energy`, TS 28.552) or an external power meter |
| Window | 1–10 s for near-RT experiments; 15 min for energy reporting |
| Aggregation | mean power over window; ratio to a baseline period |

### 4.4 MRO (`xApp4` / `x4`)

| Item | Detail |
|---|---|
| ICPs (Table V) | TXP, TTT, CIO, NL, HYS |
| What it optimises | Handover robustness; minimise call drops / blocks |
| KPI to measure | HO success rate; too-early / too-late HO; ping-pong rate; RLF rate |
| Required series | `HOAttempt`, `HOExec`, `HOFailure`; RLF indications; per-neighbour RSRP/SINR; time-of-stay; CIO/TTT/HYS/NL configuration |
| E2 / O1 source | Mobility counters from RRC / ANR; `Avg_DynMobility` is currently only a proxy |
| Window | 30 s – minutes (HO events are sparse) |
| Aggregation | ratio of successful to attempted HOs over the window |

### 4.5 `x5` (QACM only)

| Item | Detail |
|---|---|
| ICPs | `p7`, `p8` — semantics never stated |
| Evidence for identity | `k5` is negative-valued and thresholded at `−25`, and the objective is a minimisation; the most plausible reading is a power / energy KPI |
| KPI to measure | Power, or a 5QI-scoped QoS metric (delay, drop, throughput) |
| Required series | Same as ES, or QoS-flow counters |
| E2 / O1 source | O1 PM or QoS flow counters |
| Window | As ES |

### 4.6 Data needed regardless of xApp

| Need | Source | Why |
|---|---|---|
| Topology and neighbour relations | `CellIdentity`, PCI, ANR neighbour lists | `p3`/`p6` offsets cannot be mapped to real cells without it |
| Per-UE context | `UE_ID`, serving cell, neighbour set | A KPI cannot be attributed to an xApp's scope otherwise |
| Timestamped parameter-change log | E2SM-RC control acknowledgements + an RCP-style log | The paper's RCP table; not available from KPM telemetry |
| SLA / QoS thresholds `q_i` | O1 policy, or the CS xApp | Satisfaction `s_i` is undefined without them |
| Parameter groups (PGD) | O1 NRM or a manual registry | Defines which ICPs are allowed to interact |
| Time synchronisation across E2 nodes | PTP / GPS | KPI windows must be aligned to control events |
| Settling time per parameter | Empirical | A window that starts before the parameter takes effect measures the old state |

---

## 5. How to compute a KPI over a window

For a control action at `t0`:

```
window = [t0 + t_settle, t0 + t_settle + T_w]
rate   = (counter[t_end] − counter[t_start]) / T_w     # volume counters
gauge  = mean(samples in window)                        # rate gauges
kpi    = aggregate over the xApp's UE/cell scope
```

Practical parameters:

- `T_w ≥ 10 ×` report period (`≥ 1 s` at 100 ms; `≥ 10 s` on the 1 s stack)
- `t_settle` measured per parameter: TXP and tilt settle in seconds, PRB
  allocation in one scheduling epoch, HO statistics over tens of seconds
- report the aggregation rule explicitly — the papers' values are means, but QoS
  claims are usually driven by the 5th percentile
- store raw samples plus window bounds, not just the aggregate, or the result is
  not auditable

---

## 6. Other problems

Each item is something that blocks or biases a testbed-based comparison.

### P1 — Wadud's prose contradicts its own equations

§VI states: *"xApp1 demands `p1 = 50` … whereas xApp2 demands `p1 = −50`"*.
But `o1` peaks at `p1 = −50` and `o2` at `p1 = +50`. The equations and the
summary agree with each other; the paper's sentence has the two xApps swapped.
**Impact:** any reproduction built from the prose instead of the equations gets
the conflict backwards.

### P2 — The surfaces are scenario-specific, not one model

Wadud uses two variants: `o1, o2` for the direct and indirect scenarios, and
`o1′, o2′` (different amplitudes — 0.6 and 0.35 — and different centres) for the
implicit scenario. `o1′` peaks at `p1 = +85`, while the text says xApp1 "sets
`p1 = −85`" — a second sign inconsistency.

**Impact:** there is no single "Wadud dataset". A reproduction must regenerate
the surface per scenario, and the paper does not publish which variant belongs to
which figure.

### P3 — KPIs depend on other xApps' KPIs, not on shared ICPs

`o3 = f(p4, p5, o1)` and `o4 = f(p6, p7, o2)`. QACM does the same thing by
redefining a parameter group: `PkG5` grows from `{p7, p8}` to `{p1, p7, p8}`.

The papers motivate this as "implicit conflict". Operationally it means an xApp's
input includes another xApp's private output. But the same papers insist xApps
are independent black boxes that do not share information. **The implicit
conflict is created by editing the data model, not by a hidden coupling in the
network.** On a real RIC, `o2` is not an ICP and is not readable by x4 unless the
shared data layer exposes it — which the papers assume but never specify.

Consequence for a regression-based reproduction: you cannot train four
independent `ICPs → KPI` models, because two of them take another model's output
as an input. Our current per-xApp scalar projections silently break this
dependency.

### P4 — QACM's `p2` case studies cannot be derived from the published equations

Case A (§VII-A) sweeps `p2` and reports `k1` peaking at `p2 = 18` and `k2` at
`p2 = 25`. Case C reports x4 preferring `p2 = 15`. But in the printed equations
`p2` is the **width** of `k1`/`k2`, so neither can have a peak in `p2`; and
`k41`/`k42` peak at `p2 = 30` and `p2 = 50` respectively, not at 15.

**Impact:** the surfaces used for Cases A and C are not the surfaces printed in
§III. They are not published anywhere in the text, only as CSVs in the
repository. Any reproduction of those cases must take the data files as the
ground truth and treat the printed equations as covering only the `p1` cases.

### P5 — The utility formula is monotone-increasing, but two xApps minimise

Wadud's utility is
`u_i = (1/|J|) Σ_j ((o_ij − o_min)/(o_max − o_min) × 10)` — increasing in the
KPI. Yet ES is described as minimising power. The paper never inverts the
normalisation for a minimised KPI. QACM fixes this properly with the `δ` flag,
but Table V still lists CCO as "minimise SINR", which is either an error or a
mislabel of interference.

**Impact:** the sign convention determines whether the shortfall `d_i` is
`q′ − U` or `U − q′`. Getting it wrong flips the entire result. Our harness
currently hard-codes maximisation for every Wadud xApp, which is why `k5` behaves
incorrectly.

### P6 — `data4.csv` has a duplicated input column

Verified: `Input3 == Input4` for all 10 000 rows; the formulas need only three
inputs. Harmless for training, but it means any automatic feature-count check
will disagree with the equations.

### P7 — No physical units anywhere in the synthetic model

`p1 ∈ [−150, 150]` and `[−100, 100]` are dimensionless. The only physical range
in either paper is `TXP ∈ [6, 40] dBm` in QACM §VIII-A. There is no basis for
mapping a synthetic range onto a physical one by endpoint-matching.

### P8 — The control path the papers assume is not available on our stacks

Both papers' central conflict is over TXP. In our testbed documentation:

- E2SM-RC **Style 8 (power control) is unsupported** in the TU Ilmenau stack
- Style 8 is **unverified** in ns-O-RAN
- E2SM-CCC is **disabled** because it crashes the srsRAN DU
- TXP, tilt and beamforming are listed as **not implementable**

So the headline direct conflict cannot be enacted on hardware today, regardless
of whether the data is available.

### P9 — The KPIs we can measure are not the KPIs the papers use

The current CU-CP exports carry RSRP/RSRQ/SINR and topology, but no throughput,
no PRB utilisation, no transport-block counts, no modulation ratios, and no
energy counters. `DRB.UEThpDl` exists in the stack but is not in the exported
dataset. The single largest gap is that throughput — the KPI behind `k1`, `k2`,
`k3`, `k41`, `k42` — is absent.

### P10 — Report granularity and event sparsity conflict

ns-O-RAN reports at 100 ms; the TU Ilmenau stack enforces a **1 s minimum**. HO
and RLF events are sparse at both rates, so MRO's KPI needs windows of tens of
seconds while CCO's needs one second. One conflict resolution cannot satisfy
both with a single window.

### P11 — Weights and thresholds are asserted, not derived

`w_i` come from the MNO or a CS xApp; the papers never say how. `q_i` are stated
as numbers with no provenance. In QACM the thresholds are additionally z-scored
per dataset, so they move with the sampling grid (§3). Neither is data a
testbed can supply — both are policy inputs that must be declared explicitly in
any comparison.

### P12 — Multi-KPI aggregation is ad hoc

QACM's `x4` has two KPIs combined by "weighted-average … assuming equal
importance". The paper acknowledges PCA or factor analysis as alternatives and
leaves the choice open. On real data the choice changes the satisfaction count.

### P13 — Passive telemetry is the wrong sampling design

A live xApp visits only the operating points it chooses. Passive logging
therefore yields a narrow, biased slice of the KPI surface — adequate for
validation, inadequate for fitting or for reproducing a published grid. Producing
comparable data requires deliberately sweeping each ICP across levels with fixed
dwell time and repeats. That is an experiment-design task, not a logging task.

### P14 — Neither paper validates on a RIC

QACM §VIII-A states: *"The simulation is performed without a RIC, and xApps are
implemented as logic functions."* The synthetic case studies in both papers run
on "a Python-based simulator". The papers' own stated limitation is that the KPI
prediction model "may not comprehensively represent the complexity and dynamism
of real-world RAN environments". Any claim that our testbed "reproduces" them
must be scoped to the synthetic model.

---

## 7. What this changes for our reproduction

The mapping problem is narrower than it looked, and it is now two problems, not
one:

1. **Which `p_i` does each KPI depend on?** — *Solved.* Recovered from the value
   ranges and verified exactly against the formulas (§3).
2. **Which `p_i` is a real network parameter?** — *Only `p1`.* Everything else
   is a Gaussian width or offset. So the only defensible testbed instantiation is
   the one the papers themselves use in §VIII: a single physical knob (TXP) with
   a measured KPI on each side.

That is a materially better position than "the mapping is unknown". It means:

- our `data/wadud/` projections should keep `p1` as the shared sweep and treat
  `p2 … p7` as **declared constants of the model**, not as fixed network
  parameters — the metadata currently calls them "fixed ICPs", which overstates
  what they are;
- **`data/wadud/metadata.json` mixes the two papers' symbol tables.** It applies
  QACM's equations (`k1, k2, k3, k41/k42, k5`) but fills `p3 = 60`, `p5 = 60`
  and `p7 = 60` from Wadud's table, where those symbols mean different things —
  QACM defines `p3 = −20`, `p5 = −20`. `p8` does not exist in Wadud at all and is
  set to `0`. The projection is therefore a hybrid of two incompatible parameter
  sets and needs regenerating from one consistent table;
- the `k5` minimisation error (P5) is a harness bug, not an ambiguity, and can be
  fixed immediately;
- the indirect/implicit scenarios (P3) cannot be reproduced as independent
  per-xApp regressors and need either a compositional model or an explicit
  recorded deviation;
- Cases A and C of QACM (P4) must be reproduced from the shipped CSVs, not from
  the printed equations.

The fidelity results that follow from this are in [`REPORT.md`](REPORT.md) §5.

---

## 8. Open questions for the authors or the repository

1. Is `p1 … p8` intended to be a *renaming* of TTT/CIO/TXP/RET/NL/HYS, or an
   independent synthetic model? Table V suggests the former; the equations
   suggest the latter.
2. Which equations generated `data1`–`data5` for the `p2` cases (P4)?
3. Which scenario uses `o1′`/`o2′`, and is the centre `+85` or `−85` (P2)?
4. Is `k5` a power KPI, and is `x5` the ES xApp under a second identifier?
5. How were `q1 … q5` chosen, and were they normalised on the same grid used for
   the reported satisfaction counts (P11)?
6. Why does `data4.csv` carry a duplicated `p2` column (P6)?
