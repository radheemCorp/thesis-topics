# Game-Theoretic Baselines

This track adds the arithmetic mean (AM), Nash Social Welfare (NSWF), and
Eisenberg-Gale (EG) selectors described by Wadud, Golpayegani & Afraz
(`2311.13389v1`). They use the same candidate grid and xApp query contract as
the QACM CMC; QACM remains the default CLI method.

## Running

```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 --method nswf --utility-mode minmax10 \
  --qos 0.4 0.4 --weights 1 1
```

The evaluation helper runs the directly loadable synthetic scenarios and
writes CSV plus Markdown output:

```bash
uv run python -m surrogate_xapps.evaluate --scenario S6 --methods all
```

## Utility and provenance

`minmax10` is the paper's per-candidate-grid min-max scaling. `zscore` is
available for comparison with the `normalisedKPI` columns in the QACM files.
For a minimizing KPI, the scale is inverted so larger utility always means
better performance. Constant KPIs produce zero utility and a warning.

S1-S5 retain the paper's fixed-ICP and published-reference metadata in
`surrogate_xapps/scenarios.py`. The repository loader currently supports two
feature columns, while several QACM files contain additional ICPs or multiple
outputs; those scenarios are therefore provenance fixtures rather than silently
truncated runs. S6-S7 are the reproducible two-feature out-of-sample runs.
Joint 2-D mitigation remains the existing QACM extension, not a claim about
the scalar Wadud experiment.

## Policy differences

- **AM** projects the mean preferred point and does not use KPI predictions to
  select it.
- **NSWF** maximizes the sum of log utilities. The default `clamp` policy
  uses a small epsilon for zero factors; `literal` preserves zero factors as
  `-inf`.
- **EG** maximizes weighted utility after normalizing non-negative weights.

All selectors use deterministic lexicographic grid ordering and return the
existing `MitigationResult` schema, including QoS satisfaction counts.
