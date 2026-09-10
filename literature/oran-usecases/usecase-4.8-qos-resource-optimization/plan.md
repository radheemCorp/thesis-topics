# UC 4.8 — QoS Based Resource Optimization: Implementation Plan

## 1. Testbed Mapping

| UC 4.8 Spec | Testbed Equivalent | Status |
|---|---|---|
| E2 nodes provide UE performance metrics to SMO | E2SM-KPM xApp -> Kafka -> MongoDB | Done |
| SMO monitors slice SLS | consumer_mongo writes to `metrics.kpm` in MongoDB | Done |
| Non-RT RIC reads analytics, generates A1 policies | rApp reads MongoDB, issues PRB quota decisions | TODO |
| Non-RT RIC -> Near-RT RIC via A1 | rApp -> RC xApp via HTTP REST | TODO |
| Near-RT RIC enforces QoS via E2 | `control_slice_level_prb_quota()` (E2SM-RC Style 2, action 6) | Done |
| External priority input (e.g., emergency command) | REST endpoint on rApp | TODO |

### Gaps vs. Full Spec

| Full Spec Element | Testbed Limitation | Mitigation |
|---|---|---|
| A1 policy interface (standardized) | No A1 stack deployed | Simulate via HTTP REST between rApp and RC xApp |
| Multiple slices with isolation | Single-slice Open5GS config | Use UE-level PRB quotas (Style 2 action 6 targets per-UE) |
| SMO O1 interface | Not deployed | Bypass -- rApp reads MongoDB directly |
| Real emergency service UEs | ZMQ virtual UEs | Multiple srsUEs via `multi_ue` container |

---

## 2. Scenario

Multiple UEs share the cell. One UE is designated "priority" (e.g., emergency
video feed). When the priority UE's throughput drops below a threshold
(congestion), the system dynamically increases its PRB quota at the expense of
best-effort UEs.

---

## 3. Architecture

```
                        +----------------------------------+
                        |       External Input              |
                        |  (priority UE identifier +        |
                        |   minimum bitrate target)         |
                        +----------+-----------------------+
                                   | REST / config
                                   v
+----------+  E2SM-KPM   +--------------+  Kafka   +----------+
|  gNB     |------------>|  KPM xApp    |--------->|  Kafka   |
| (srsRAN) |             |  (monitor)   |          |          |
+----------+             +--------------+          +----+-----+
                                                         |
                                          +--------------+--------------+
                                          v              v              v
                                    +----------+  +----------+  +----------+
                                    | InfluxDB3|  | InfluxDB2|  | MongoDB  |
                                    | (Grafana)|  | (AIMLFW) |  | (rApp)   |
                                    +----------+  +----------+  +----+-----+
                                                                     |
                                                                     v
                                                           +--------------+
                                                           |  non-RT RIC  |
                                                           |  rApp        |
                                                           |  (analytics  |
                                                           |   + policy)  |
                                                           +------+-------+
                                                                  |
                                                    +-------------+-------------+
                                                    | HTTP POST   (A1 sim)      |
                                                    v                            v
                                                           +--------------+
                                                           |  RC xApp     |
                                                           |  (enforce)   |
                                                           +------+-------+
                                                                  |
                                                    E2SM-RC       |
                                                    Style 2       |
                                                    Action 6      v
                                                           +--------------+
                                                           |  gNB        |
                                                           |  PRB quota  |
                                                           |  updated    |
                                                           +--------------+
```

---

## 4. Implementation Steps

### Phase 1 -- Data Collection (already done)

- KPM xApp subscribes to E2SM-KPM Style 1 (cell-level) or Style 2 (per-UE)
- Metrics `DRB.UEThpDl`, `DRB.UEThpUl` flow through Kafka -> MongoDB
- Verify: query `db.kpm.find()` in `metrics_mongo` container

### Phase 2 -- non-RT RIC rApp (policy engine)

**New file:** `ric/xApps/python/qos_rapp.py`

Responsibilities:

1. **Read** KPM documents from MongoDB (`metrics.kpm` collection)
2. **Detect** when priority UE throughput < configured threshold
3. **Decide** new PRB quota: increase `min_prb_ratio` / `max_prb_ratio` for
   priority UE, decrease for others
4. **Publish** the decision via HTTP POST to the RC xApp's `/a1/policy` endpoint

Key parameters (configurable via env or config file):

| Parameter | Description | Example |
|---|---|---|
| `PRIORITY_UE_ID` | Which UE is priority | `0` |
| `THROUGHPUT_THRESHOLD_DL` | Minimum acceptable DL throughput (kbps) | `200` |
| `PRB_BOOST` | How much to increase min_prb_ratio when congested | `20` |
| `CHECK_INTERVAL_S` | How often to evaluate | `5` |
| `MONGO_URI` | MongoDB connection string | `mongodb://metrics_mongo:27017` |
| `RC_XAPP_URL` | RC xApp HTTP endpoint | `http://rc_xapp:8090/a1/policy` |

### Phase 3 -- A1 Interface Simulation

HTTP REST is the recommended approach.

The rApp POSTs a JSON policy document to the RC xApp:

```
POST /a1/policy
Content-Type: application/json

{
  "ue_id": 0,
  "min_prb_ratio": 30,
  "max_prb_ratio": 70,
  "dedicated_prb_ratio": 100
}
```

The RC xApp applies the policy immediately via E2SM-RC Style 2.

### Phase 4 -- RC xApp (enforcement)

**New file:** `ric/xApps/python/qos_rc_xapp.py`

Based on `simple_rc_xapp.py` with additions:

1. Expose HTTP endpoint `POST /a1/policy` accepting PRB quota JSON
2. On POST, call `self.e2sm_rc.control_slice_level_prb_quota()`
3. Log the control request with timestamp for Grafana correlation
4. Optionally subscribe to KPM to track enforcement效果

### Phase 5 -- Orchestration & Demo

1. Start full stack: `manage.sh start all`
2. Launch multiple ZMQ UEs: `manage.sh start multi_ue`
3. Start KPM xApp (cell-level, Style 1) -- already in docker-compose
4. Start RC xApp -- new service in docker-compose
5. Start rApp -- new service or run outside Docker
6. Inject traffic: UE data flows via ZMQ
7. **Trigger congestion:** increase traffic load or reduce PRB ceiling
8. **Observe:** rApp detects throughput drop -> issues policy -> RC xApp enforces
   PRB boost -> priority UE throughput recovers
9. **Dashboard:** Grafana panel showing throughput per UE before/during/after
   policy enforcement

---

## 5. Files to Create/Modify

| File | Action | Purpose |
|---|---|---|
| `ric/xApps/python/qos_rapp.py` | Create | Non-RT RIC rApp: read MongoDB, detect congestion, issue policies |
| `ric/xApps/python/qos_rc_xapp.py` | Create | Near-RT RC xApp: accept A1 policy via HTTP, enforce PRB quotas |
| `docker-compose.zmq.yml` | Modify | Add `qos_rc_xapp` and `qos_rapp` services |
| `configs/qos_rapp.env` | Create | Config: priority UE, thresholds, PRB ranges |
| `scripts/demo_qos.sh` | Create | Demo script: start stack, inject load, trigger policy, show results |
| `monitoring/grafana/dashboards/qos.json` | Create | Grafana dashboard: throughput per UE + policy events |

### Existing Dependencies (already in testbed)

- `lib/e2sm_rc_module.py` -> `control_slice_level_prb_quota()` 
- `lib/metrics_writer.py` -> Kafka publisher
- `pubsub/consumer/sinks.py` -> MongoDB sink
- `pymongo` (already in consumer image)

---

## 6. Open Questions

1. **How many UEs to simulate?** The `multi_ue` container supports N srsUEs.
   3-5 is realistic for ZMQ.
2. **HTTP vs MongoDB for A1 simulation?** HTTP recommended (cleaner, lower
   latency).
3. **rApp inside Docker or on the host?** Inside Docker keeps everything
   self-contained; host-side is easier to iterate on.
