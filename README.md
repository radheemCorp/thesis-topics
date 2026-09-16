# SON xApp Conflict Mitigation

This repository investigates how Self-Organizing Network (SON) functions can be implemented as O-RAN xApps and coordinated when their control actions conflict. It collects the problem context, relevant O-RAN use cases, mitigation approaches, implementation constraints, and material for testing those approaches.

The central question is:

> How can independently developed SON xApps safely share RAN control while preserving their objectives, QoS/SLA requirements, and near-real-time constraints?

## Repository Index

Use the sections below as a reading path. Start with the problem and system context, compare candidate mitigation strategies, then use the testbed notes to ground an implementation and evaluation.

### 1. Problem and O-RAN context

- [O-RAN use-case catalogue](literature/oran-usecases/usecases.md) - overview of the use cases, their problems, proposed RIC/xApp solutions, and required infrastructure.
- [Integrated SON function (UC 4.19)](literature/oran-usecases/usecases.md#19-integrated-son-function-uc-419) - the most direct use-case context for moving legacy SON functions into xApps and rApps.
- [Interference detection, prediction, and optimization (UC 4.26)](literature/oran-usecases/usecase-4.26-interference-detection/interference-detection-usecase.md) - a concrete conflict-prone control problem involving interference graphs and collaborative optimization.
- [QoE optimization (UC 4.4)](literature/oran-usecases/usecase-4.4-qos-qoe-optimization/usecase.md) and [QoS resource optimization (UC 4.8)](literature/oran-usecases/usecase-4.8-qos-resource-optimization/usecase.md) - examples where competing objectives and service guarantees shape the mitigation policy.

### 2. Conflict-mitigation approaches

- [Approaches index](literature/paper-summaries/index.md) - the main comparison of RL-based, game-theoretic, rule-based, digital-twin, blending, detection, and scheduling approaches.
- [Relevant papers](literature/paper-summaries/relevant-papers.md) - common references and a prioritized reading list.
- [Summary template](literature/paper-summaries/summary-template.md) - structure for adding a consistent paper analysis.

The approaches can be read as complementary layers:

1. **Detect or predict conflicts:** dependency mapping, interference detection, and context modelling.
2. **Choose or constrain actions:** priorities, QoS/SLA projection, bargaining, and scheduler activation.
3. **Learn or construct a compromise:** team learning, distillation, digital-twin-guided policies, and continuous action blending.

### 3. SON and xApp inventory

- [xApps used in the research](literature/xapps/xapps-used.md) - candidate xApps and the RAN parameters or objectives they control.
- [SON use-case research notes](bak/son-usecase-lr.md) - exploratory notes on SON functions and their relevance to this work.
- [Potential work directions](bak/potential-work.md) - early hypotheses and possible research paths.

The xApp inventory is useful when defining a conflict scenario: identify each xApp's objective, controlled parameter, KPI, action space, timescale, and QoS constraints before selecting a mitigation method.

### 4. Implementation and testbed constraints

- [Testbed limitations](literature/testbed-info/testbed-limitations.md) - capabilities and constraints that affect what can be implemented and measured.
- [Control service style](literature/testbed-info/control-service-style2.md) - notes on the control-service integration style.
- [E2SM-KPM offerings](literature/testbed-info/e2sm-kpm-offerings.md) - available measurements for observation, conflict detection, and evaluation.

These notes should be read before committing to an experiment. They define which xApp controls, measurements, interfaces, and timescales are realistic in the available environment.

### 5. Focused study areas

- [Congestion prediction (UC 4.16)](literature/oran-usecases/usecase-4.16-congestion-prediction/usecase.md) - proactive mitigation based on predicted traffic and congestion.
- [Use-case 4.26 summary](literature/oran-usecases/usecase-4.26-interference-detection/summary.md) and [working notes](literature/oran-usecases/usecase-4.26-interference-detection/work.md) - current analysis of the interference-focused scenario.
- [QoE optimization summary](literature/oran-usecases/usecase-4.4-qos-qoe-optimization/summary.md) - service-aware optimization context.
- [QoS resource optimization plan](literature/oran-usecases/usecase-4.8-qos-resource-optimization/plan.md) - planning material for a QoS-oriented scenario.

## Suggested Workflow

1. Select a SON conflict scenario from the [use-case catalogue](literature/oran-usecases/usecases.md) and define the participating xApps.
2. Record each xApp's objective, controlled RAN parameter, KPI, action space, operating timescale, and SLA/QoS constraints.
3. Use the [approaches index](literature/paper-summaries/index.md) to choose a detection, arbitration, optimization, or learning strategy.
4. Check the [testbed notes](literature/testbed-info/testbed-limitations.md) and [E2SM-KPM measurements](literature/testbed-info/e2sm-kpm-offerings.md) to make the design implementable.
5. Implement the selected mitigation path and its baseline, then evaluate conflict rate, KPI performance, fairness, SLA satisfaction, stability, and control overhead.
6. Add the resulting design, experiment plan, or paper analysis beside the closest existing material and update this index.

## Evaluation Questions

Any implementation should make it possible to answer at least these questions:

- How often do the xApps issue conflicting actions?
- Does mitigation improve the joint objective without hiding degradation for an individual xApp?
- How many xApps meet their QoS or SLA targets?
- How stable are the resulting control actions over time?
- What latency, data, training, twin, or coordination overhead does the method introduce?
- How does it behave under changing traffic, mobility, interference, and out-of-distribution conditions?

## Repository Layout

```text
literature/
	oran-usecases/       O-RAN use cases and focused scenario studies
	paper-summaries/     Structured comparisons of conflict-mitigation methods
	testbed-info/         Integration, measurement, and platform constraints
	xapps/               Candidate xApp inventory
bak/                   Exploratory notes and early research directions
```

This README is the entry point. The detailed claims, equations, experiment plans, and implementation decisions belong in the linked documents rather than in this overview.
