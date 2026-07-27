# UC 4.16 — Congestion Prediction and Management: Abstract Plan

## 1. Problem Statement

Cell congestion leads to link failures and poor data rates. Current mitigation
is post-facto -- the network reacts after congestion has already degraded
service. UC 4.16 proposes **predictive** congestion management: the Non-RT RIC
uses ML to forecast future traffic patterns, and the Near-RT RIC executes
proactive mitigation (PRB redistribution, load sharing) *before* congestion
occurs.

---

## 2. Testbed Mapping

| UC 4.16 Spec | Testbed Equivalent | Status |
|---|---|---|
| E2 nodes provide KPM metrics | E2SM-KPM xApp -> Kafka -> InfluxDB2 | Done |
| SMO / data collector | Kafka -> InfluxDB2 (AIMLFW-compatible) | Done |
| AI Server trains prediction model | AIMLFW pipeline (feature group -> Kubeflow -> KServe) | Partial -- InfluxDB2 ready, ML stack not deployed |
| Non-RT RIC predicts traffic patterns | rApp reads MongoDB/InfluxDB2, runs inference | TODO |
| Near-RT RIC executes mitigation | RC xApp enforces PRB quotas via E2SM-RC Style 2 | TODO |
| Proactive control (before congestion) | Time-series prediction -> preemptive PRB adjustment | TODO |

### Key Difference from UC 4.8

| Aspect | UC 4.8 (QoS Optimization) | UC 4.16 (Congestion Prediction) |
|---|---|---|
| Trigger | Reactive -- detect throughput drop | Predictive -- forecast congestion before it happens |
| Intelligence | Threshold-based rules | ML model (time-series forecasting) |
| Timing | After congestion detected | Before congestion occurs |
| AIMLFW usage | Not used | Core component |

---

## 3. Scenario

Multiple UEs generate varying traffic loads. The system:

1. Collects KPM throughput data over time (history)
2. Trains a model to predict future throughput / load
3. When prediction indicates imminent congestion, preemptively redistributes
   PRB resources to maintain QoS targets
4. Demonstrates that predicted congestion was avoided (throughput stays stable)

---

## 4. Architecture

```
+----------+  E2SM-KPM   +--------------+  Kafka   +----------+
|  gNB     |------------>|  KPM xApp    |--------->|  Kafka   |
| (srsRAN) |             |  (monitor)   |          |          |
+----------+             +--------------+          +----+-----+
                                                         |
                                          +--------------+--------------+
                                          v                             v
                                    +----------+                 +----------+
                                    | InfluxDB2|                 | MongoDB  |
                                    | (AIMLFW) |                 | (rApp)   |
                                    +----+-----+                 +----+-----+
                                         |                            |
                          +--------------+--------------+              |
                          v              v              v              v
                    +----------+  +----------+  +----------+  +--------------+
                    | Feature  |  | Data     |  | Model    |  |  non-RT RIC  |
                    | Group    |->| Extract  |->| Train    |  |  rApp        |
                    |          |  |          |  | (LSTM)   |  |  (analytics) |
                    +----------+  +----------+  +----+-----+  +------+-------+
                                                       |              |
                                                       v              |
                                                 +----------+        |
                                                 | Model    |        |
                                                 | Artifact |        |
                                                 +----+-----+        |
                                                      |              |
                                                      v              |
                                                 +----------+        |
                                                 | KServe   |        |
                                                 | Inference|        |
                                                 +----+-----+        |
                                                      |              |
                                                      v              v
                                              +----------------------------+
                                              |  Congestion Prediction     |
                                              |  -> PRB redistribution     |
                                              |  -> E2SM-RC Style 2        |
                                              +----------------------------+
                                                      |
                                                      v
                                               +--------------+
                                               |  gNB        |
                                               |  PRB quotas |
                                               |  adjusted   |
                                               +--------------+
```

---

## 5. Implementation Options for ML

The AIMLFW stack (Kubeflow, KServe, Cassandra) is **not deployed** in the
testbed. Three options:

### Option A -- Standalone ML in rApp (Recommended)

Embed a lightweight ML model directly in the rApp Python process.

| Pros | Cons |
|---|---|
| No additional infrastructure | Limited to simple models |
| Fast iteration, easy debugging | Not production-grade AIMLFW |
| Can use scikit-learn, statsmodels, or lightweight PyTorch | Training happens in-process, not via Kubeflow |

Model candidates:
- **ARIMA / SARIMA** -- classical time-series, no GPU needed
- **Prophet** -- Facebook's time-series model, handles seasonality
- **Simple LSTM** -- if PyTorch is acceptable as a dependency

### Option B -- External ML Service

Deploy a separate ML container (e.g., a Jupyter + Flask stack) that:
1. Reads from InfluxDB2
2. Trains on a schedule
3. Exposes a `/predict` HTTP endpoint
4. The rApp calls `/predict` before making policy decisions

| Pros | Cons |
|---|---|
| Separation of concerns | Extra container to manage |
| Can use heavier frameworks | More moving parts |

### Option C -- Simulated AIMLFW

Follow the architecture doc's described pipeline manually:
1. Export features from InfluxDB2 to CSV
2. Train offline (notebook or script)
3. Load trained model in rApp for inference

| Pros | Cons |
|---|---|
| Matches architecture doc exactly | Manual, not automated |
| Good for thesis writing (shows full pipeline) | No real-time retraining |

**Recommendation:** Option A for implementation, with Option C as a
supplementary demo showing the full pipeline for the thesis.

---

## 6. Implementation Steps

### Phase 1 -- Data Collection (already done)

Same as UC 4.8. KPM metrics flow to InfluxDB2 and MongoDB.

### Phase 2 -- Feature Engineering

**New file:** `ric/xApps/python/congestion_features.py`

Responsibilities:
1. Query InfluxDB2 for historical KPM data (sliding window, e.g., last 5 min)
2. Compute features:
   - Throughput mean, std, trend (slope)
   - Utilization ratio (current / peak)
   - Number of active UEs
   - Inter-arrival time variance
3. Output feature vector for model input

### Phase 3 -- Prediction Model

**New file:** `ric/xApps/python/congestion_model.py`

Responsibilities:
1. Train model on historical data (startup or periodic retrain)
2. Predict future throughput N seconds ahead
3. Classify prediction as "congestion imminent" or "normal"
4. Expose `predict(features) -> (congestion_probability, predicted_throughput)`

### Phase 4 -- non-RT RIC rApp (policy engine)

**New file:** `ric/xApps/python/cpm_rapp.py`

Responsibilities:
1. Periodically read KPM from MongoDB
2. Compute features via `congestion_features.py`
3. Run prediction via `congestion_model.py`
4. If congestion predicted within horizon (e.g., 30s):
   - Calculate PRB redistribution (increase for vulnerable UEs, decrease for others)
   - POST policy to RC xApp `/a1/policy` endpoint
5. Log prediction + action for Grafana

Key parameters:

| Parameter | Description | Example |
|---|---|---|
| `PREDICTION_HORIZON_S` | How far ahead to predict | `30` |
| `CONGESTION_THRESHOLD` | Probability threshold for action | `0.7` |
| `CHECK_INTERVAL_S` | Evaluation frequency | `5` |
| `RETRAIN_INTERVAL_S` | How often to retrain model | `300` |
| `PRB_REALLOCATION_STEP` | How aggressively to shift PRBs | `10` |

### Phase 5 -- RC xApp (enforcement)

Same as UC 4.8. The RC xApp accepts PRB quota policies via HTTP and enforces
them via E2SM-RC Style 2.

### Phase 6 -- Observability

**New Grafana dashboard panels:**
- Throughput per UE (actual vs. predicted)
- Congestion probability over time
- PRB quota changes (policy enforcement events)
- Model accuracy metrics (if available)

---

## 7. Files to Create/Modify

| File | Action | Purpose |
|---|---|---|
| `ric/xApps/python/congestion_features.py` | Create | Feature engineering from KPM time series |
| `ric/xApps/python/congestion_model.py` | Create | ML model: train, predict, save/load |
| `ric/xApps/python/cpm_rapp.py` | Create | Non-RT RIC rApp: predict + issue policies |
| `ric/xApps/python/qos_rc_xapp.py` | Create | RC xApp with A1 HTTP endpoint (shared with UC 4.8) |
| `docker-compose.zmq.yml` | Modify | Add cpm_rapp and qos_rc_xapp services |
| `configs/cpm_rapp.env` | Create | Config: thresholds, model params |
| `scripts/demo_cpm.sh` | Create | Demo script |
| `monitoring/grafana/dashboards/cpm.json` | Create | Dashboard: prediction + enforcement |

### Dependencies to Add

| Package | Purpose | Install |
|---|---|---|
| `influxdb-client` | Query InfluxDB2 from rApp | `pip install influxdb-client` |
| `scikit-learn` | ML models (ARIMA alternative) | `pip install scikit-learn` |
| `numpy` | Feature computation | `pip install numpy` |
| `statsmodels` | ARIMA/SARIMA | `pip install statsmodels` |

---

## 8. Thesis Narrative

This use case demonstrates the **O-RAN AI/ML Framework** concept:

1. **Data collection:** E2SM-KPM -> Kafka -> InfluxDB2 (the standard pipeline)
2. **Feature extraction:** Time-series features from raw KPM
3. **Model training:** LSTM or ARIMA on historical throughput patterns
4. **Inference:** Predict congestion N seconds ahead
5. **Closed-loop control:** Prediction -> A1 policy -> E2SM-RC -> PRB adjustment
6. **Validation:** Compare predicted vs. actual throughput; show congestion avoided

The key contribution is showing that **predictive** resource management outperforms
**reactive** approaches (like UC 4.8's threshold-based rules).

---

## 9. Open Questions

1. **ML framework preference?** scikit-learn (simple) vs. PyTorch LSTM (more
   impressive for thesis) vs. statsmodels ARIMA (classical baseline)?
2. **Shared RC xApp with UC 4.8?** If both use cases run on the same testbed,
   the RC xApp can serve both rApps. Otherwise, separate instances.
3. **Retraining strategy?** Periodic (every N minutes) vs. triggered (when
   prediction error exceeds threshold)?
