https://github.com/wineslab/xDevSM/tree/main

The xDevSM API framework provides xApp developers with a SDK exposing simple APIs to streamline the procedures defined by different E2SM protocols, facilitating interactions between the xApp, the near-RT RIC, and the E2 termination on the RAN. It wraps and orchestrates message encoding/decoding, RMR-based communication, and SM-specific behavior. Internally, it delegates encoding and decoding tasks to the sm_framework, which defines the core logic for each Service Model (KPM, RC, and CCC).

sample xapps: https://github.com/wineslab/xDevSM-xapps-examples/tree/dev