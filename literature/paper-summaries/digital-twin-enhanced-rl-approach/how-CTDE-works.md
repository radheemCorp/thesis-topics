In the paper, this dual operation is achieved through the **Centralized Training with Decentralized Execution (CTDE)** paradigm, combined with the offline simulation environment provided by the **Digital Twin (DT)**.

---

### 1. Centralized Training in the Digital Twin
During the training phase, multiple Multi-Agent Reinforcement Learning (MARL) agents are trained offline inside the Digital Twin virtual sandbox:
* **Global Information Access:** The Digital Twin emulates overall RAN dynamics, granting agents access to **global data**—such as the joint network state, global KPIs, and the concurrent actions of all operating xApps.
* **Centralized Critic:** Algorithms like MAPPO, HAPPO, and FACMAC utilize a **centralized critic network**. This critic analyzes system-wide data to accurately evaluate how well the joint actions of all xApps performed, which stabilizes training and resolves resource conflicts during learning.
* **Zero Live Signaling Burden:** Because training occurs offline using pre-collected or synthetic datasets in the Digital Twin, it avoids sending heavy synchronization messages across the live network control plane.

---

### 2. Decentralized Execution in the Live Network
Once training is complete, the global centralized critic is no longer required for real-time decision-making:
* **Exporting Policy Networks:** Only the trained **Actor policy networks** are exported and encapsulated into individual xApps, which are then deployed on the Near-RT RIC.
* **Autonomous Local Decisions:** In the live network, each xApp operates independently using strictly its own **local observations** (e.g., cell-specific radio metrics or PRB usage within its own control domain).
* **Low Overhead & Latency:** Because xApps do not need to exchange state messages with peer xApps or query global network states during inference, execution remains lightweight and avoids E2 signaling bottlenecks.

---

### How xApps Train on Global Data but Act on Local Data
The transition from global training to local execution works through the separation of roles in the **Actor-Critic architecture**:

1. **Input Separation During Training:** The **Critic** receives the global joint state to compute overall system rewards, but each **Actor** network is explicitly restricted to accepting only its specific local observations as input.
2. **Learning Implicit Coordination:** As the globally aware Critic guides policy updates during training, the Actor's weights are iteratively tuned to select actions that naturally align with system goals and avoid clashing with other xApps.
3. **Runtime Inference:** During live execution, the global Critic is detached. The xApp simply inputs its local observations into its trained Actor model to generate optimal, conflict-avoiding actions in near-real-time without needing external global inputs.

---