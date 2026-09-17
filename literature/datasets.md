
### Available Datasets in the Literature

The sources highlight several datasets and repository benchmarks used for training, evaluating, and simulating multi-xApp conflict mitigation:

1. **QACM & CMS Repository Datasets (`GitHub`)**:
   * **Location / Reference:** `dewanwadud1/QACM` and `dewanwadud1/cmsORAN`.
   * **Description:** Contains synthetic conflict tables generated for stochastic xApps. Includes Gaussian-distributed KPI values, normalized utility metrics (min-max and z-score), and input control parameter ranges for direct, indirect, and implicit conflict scenarios.
   * link: https://github.com/dewanwadud1/QACM
   * link: https://github.com/dewanwadud1/cmsORAN

2. **GRAPHICA Binary-State & Synthetic Graph Datasets**:
   * **Description:** Event-driven binary-state datasets capturing state transitions (\\(1\\) for change, \\(0\\) for no change) across 10 xApps, 15 controllable parameters, and 20 KPIs. It includes skewed conflict datasets at varying imbalance ratios (40%, 30%, 20%, and 10% conflict prevalence) as well as Gaussian-distributed KPI benchmark datasets.

3. **Colosseum Rome Scenario / OpenRAN Gym Dataset**:
   * **Description:** Extracted from the Colosseum wireless network emulator reproducing a real-world cellular deployment in Rome, Italy, using OpenCelliD GPS base station coordinates. It includes MGEN traffic generator logs serving eMBB (4 Mbps CBR), URLLC (89.29 kbps Poisson), and mMTC (44.64 kbps Poisson) slices across 50 PRBs, capturing over 30 KPMs per UE.
   link: https://github.com/wineslab/open-ran-commercial-traffic-twinning-dataset

4. **Viavi RIC Testbed Synthetic UE-Level Dataset**:
   * **Description:** Synthesized from a Viavi RIC testbed containing 30,000 records with 25 to 41 features per record. It includes radio indicators (RSRP, RSRQ, SINR), QoS scores, 5QI indices, PRB consumption, scheduled transport blocks, and 3D spatial coordinates across 3 base stations, 6 cells, and 20 IoT UEs.
    * link: https://comms.viavisolutions.com/viavi-network-digital-twin-vs12584

6. **OpenCelliD Dataset**:
   * **Location / Reference:** OpenCelliD open-source database.
   * **Description:** Contains real-world GPS coordinates and structural topology of cell towers, used to construct realistic physical base station layouts in digital twin emulators.
   * link: https://docs.opencellid.org/docs/introduction

7. **Raca et al. 5G Context Dataset**:
   * **Reference:** Raca et al. (2020).
   * **Description:** A 5G dataset containing channel metrics, throughput metrics, and context variables used for KPI normalizations and network state modeling.
   * link: https://dl.acm.org/doi/10.1145/3339825.3394938

8. **Colosseum O-RAN COMMAG Dataset**:
   * **Reference:** Bonati et al. (2021), "Intelligence and Learning in O-RAN for Data-driven NextG Cellular Networks," IEEE Communications Magazine.
   * **Description:** Dataset from the Colosseum wireless network emulator for O-RAN network slicing. Contains 4 BSs (3 MHz / 15 PRBs), 3 slices per BS, 40 UEs, and scheduling policies (Round-robin, Waterfilling, Proportionally fair) across 18 training configurations. Includes eMBB, MTC, and URLLC traffic classes, static/slow UE mobility, and dynamic slice resizing. Provides CSV data and trained PPO DRL agents for slice scheduling.
   * link: https://github.com/wineslab/colosseum-oran-commag-dataset
