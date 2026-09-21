1. GRAPHICA vs. PACIFISTA (Pre-Deployment Gatekeeper vs. Live Observer)
* PACIFISTA (The Gatekeeper): Sits in the Non-RT RIC / SMO. Before an xApp is allowed to go live, PACIFISTA profiles it offline in a sandbox emulator (Colosseum) and blocks it if it is predicted to cause unacceptable conflicts.
* GRAPHICA (The Live Alarm System): Sits inside the Near-RT RIC. It watches live E2 network traffic and uses a Graph Convolutional Network (GCN) to predict conflicts in real time right before they cause performance drops.
* Why Compare: Compares pre-deployment prevention (hardware-in-the-loop emulator) against live detection (event-driven simulation).


2. GRAPHICA vs. A2C Scheduler (Passive Detector vs. Active Controller)
* Common Ground: Both process live E2 telemetry inside the Near-RT RIC and have been evaluated in simulation environments.
* The Difference:
  * GRAPHICA (Detector): Identifies *where* and *why* a conflict is about to happen (Root Cause Analysis). To fix the issue, it relies on an external reaction rule (like pausing the offending xApp).
  * A2C Scheduler (Traffic Cop): Dynamically switches xApps on or off or moves to fallback safety policies based on live network conditions (like traffic load and user speed) [297, 353–355].


3. A2C Scheduler vs. QACM (Macro Coordinator vs. Micro Bargainer) — Recommended Direct Comparison
* Common Ground: Both are active runtime fixers inside the Near-RT RIC that issue E2 control commands to protect network Quality of Service (QoS).
* The Difference:
  * A2C Scheduler (Macro-Level): Controls which xApps are running. It turns xApps on or off depending on the overall network environment.
  * QACM (Micro-Level): Controls specific parameter values [111, 159–160]. When running xApps fight over a setting (like transmit power), QACM calculates a single optimal compromise value so all active xApps meet their QoS targets [111, 159–160].
* Why Compare: This provides the cleanest comparison between app-level scheduling vs. parameter-level tuning for live conflict mitigation.

