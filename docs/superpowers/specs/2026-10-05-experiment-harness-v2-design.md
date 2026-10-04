# Experiment Harness v2 Design

## Context

This repository is a reusable template for data science competitions. The first-generation harness already has strong foundations: hypothesis-driven experiments, immutable completed experiments, self-contained configs, a standard CV, experiment lineage, lightweight structured artifacts, OOF preservation, and separation between experiment execution and submission generation.

A retrospective of an actual competition project exposed several weaknesses that were not failures of reproducibility, but failures of human control and long-running search strategy:

- project-level knowledge accumulated faster than a human could scan it;
- the same summary document was asked to serve both as durable scientific memory and a current-state dashboard;
- autonomous experiment generation tended to favor small local improvements around the current best lineage;
- weak or cheap workers were sometimes given implementation tasks whose mistakes could invalidate experiments;
- engineering knowledge such as parallelism and resource defaults was learned once but not institutionalized;
- repeated small comparisons sometimes became many separate experiments instead of trials under one hypothesis;
- promising score deltas were sometimes treated as improvements before their robustness against CV noise had been established.

The v2 harness should preserve the successful reproducibility mechanisms while adding an explicit human control plane and rules that help humans and agents jointly manage exploration.

## Goals

1. Keep the current experiment record and reproducibility model intact.
2. Make the current project state understandable by a human in roughly five minutes.
3. Separate current-state navigation from accumulated scientific knowledge.
4. Make exploration breadth visible so the harness does not silently collapse into current-best local search.
5. Distinguish cheap screening evidence from evidence strong enough to promote a new default parent.
6. Preserve engineering and operational lessons as first-class project knowledge.
7. Make agent delegation depend on task risk rather than a hard-coded model name.
8. Keep the template lightweight; do not turn it into a full experiment-management platform.

## Non-goals

This change does not:

- implement a competition-specific model pipeline;
- introduce MLflow, Weights & Biases, Optuna, distributed execution, or a dashboard;
- require an exact exploration percentage or fixed number of seeds for all competitions;
- ban small experiments or force every promising result through an expensive confirmation stage;
- hard-code a particular LLM or coding-agent model into project policy;
- require every operational lesson to be enforced by code immediately.

## Information Architecture

The project-level documents have distinct responsibilities.

### `docs/STATUS.md` — human control plane

Purpose: show the current state of the project quickly.

It should remain deliberately short and volatile. It is not an experiment history and not an encyclopedic knowledge base.

Recommended sections:

- Goal / competition objective
- Robust Parent
- Apparent Best / Unconfirmed Best, when different
- Search Map
- High-confidence Findings, at most about five
- Dead Ends / Deprioritized Directions, at most about five
- Open Strategic Questions, at most about three
- Next Candidates, at most about three
- Resource Notes
- Last Updated

`STATUS.md` may summarize information whose source of truth lives elsewhere. It is a navigation and decision document, not an authoritative numerical database.

### `docs/EXPERIMENT_SUMMARY.md` — accumulated scientific knowledge

Purpose: retain durable project-level knowledge derived from experiments.

It should focus on findings that are likely to remain useful across multiple future decisions:

- validation findings;
- data findings;
- model-family findings;
- feature findings;
- robust positive findings;
- robust negative findings;
- interactions and caveats.

Volatile sections such as a long current-best narrative, active next-experiment list, and current direction move to `STATUS.md`.

The summary is allowed to grow more than `STATUS.md`, but it should still consolidate findings rather than append one entry per experiment.

### `docs/ENGINEERING_NOTES.md` — operational and resource knowledge

Purpose: preserve implementation and execution knowledge that affects speed, reliability, or reproducibility but is not a scientific modeling result.

Examples:

- CPU thread settings;
- GPU enablement and known constraints;
- cache behavior;
- deterministic settings and their cost;
- known library-specific pitfalls;
- recommended execution profiles;
- memory constraints;
- environment-specific caveats.

Each important note should include, when practical:

- recommendation;
- evidence or experiment/reference that motivated it;
- scope or affected component;
- last verification date;
- caveat.

When an engineering lesson is general and safe enough to encode into a default, the implementation/config default should be changed as well. Documentation should not become a substitute for fixing a bad default.

### `docs/HARNESS_LESSONS.md` — harness meta-knowledge

Purpose: record lessons about the experiment system itself, independently of any particular competition.

The initial document should capture the retrospective that motivated v2, including:

- reproducibility and immutable artifacts worked well;
- agent-readable context and human-readable current state are different products;
- a single summary should not serve both current-state navigation and accumulated knowledge;
- current-best gravity creates structural bias toward local exploitation;
- exploration breadth should be made visible before stagnation becomes obvious;
- screening and confirmation should be distinct concepts;
- repeated homogeneous comparisons belong in trials when the scientific question is the same;
- engineering knowledge deserves the same persistence discipline as scientific knowledge;
- delegation should be based on task risk, and worker output is not proof of correctness;
- large general-purpose experiment runners should be split when model-specific logic accumulates;
- the harness itself should be reviewed after a competition and improved using observed failure modes.

This file is the source of truth for reusable lessons about harness design. It is not a changelog of every documentation edit.

### `docs/experiment_queue/`

Purpose: provide a lightweight human-and-agent interface for future hypotheses without turning the queue into an auto-execution plan.

Files:

- `README.md`: queue rules, statuses, prioritization criteria, and re-evaluation behavior;
- `QUEUE.md`: concise active index;
- optional job files for proposals that need more detail.

The queue must state that:

- it is a backlog, not an ordered batch script;
- after each meaningful experiment, active priorities may change;
- humans may add hypotheses directly;
- a job does not receive an experiment ID until it is actually selected for execution;
- detailed history belongs in experiments, not in the queue.

Recommended queue statuses:

- `ready`
- `blocked`
- `needs_review`
- `paused`
- `superseded`

Recommended job fields:

- Hypothesis
- Motivation / Evidence
- Search Branch
- Parent Candidate
- Proposed Change
- Fixed Conditions
- Decision Metric
- Expected Information Gain
- Dependencies
- Re-evaluation Triggers
- Execution Notes

## Experiment Lifecycle

The default loop becomes:

```text
STATUS / accumulated knowledge / registry
        ↓
select a strategic question
        ↓
select or add a queue hypothesis when useful
        ↓
choose logical parent and experiment-vs-trial boundary
        ↓
implement minimum change
        ↓
targeted validation of implementation
        ↓
screening experiment
        ↓
analyze evidence and uncertainty
        ↓
confirm if promotion would rely on a fragile result
        ↓
promote robust parent or retain current parent
        ↓
update durable knowledge, engineering knowledge, and STATUS as applicable
        ↓
re-evaluate search map and queue
```

### Screening, Confirmation, Promotion

These are evidence stages, not rigid experiment types that every run must pass through.

#### Screening

Use the cheapest evaluation that still answers the immediate question reasonably well.

A screening result can justify further investigation, but a small apparent improvement should not automatically become the stable default parent when it is plausibly within CV noise.

#### Confirmation

Use stronger evaluation when the decision being made deserves stronger evidence. Examples include:

- replacing the robust default parent;
- acting on a score difference that is small relative to observed variation;
- relying on a result with inconsistent fold behavior;
- promoting a substantially more expensive model for only a small gain;
- using a result that changes the project strategy.

Confirmation may use repeated seeds, repeated folds, alternate diagnostics, or another competition-appropriate robustness check. The harness does not prescribe one universal seed count.

#### Promotion

A promoted experiment becomes a recommended robust parent or otherwise changes the project-level status.

Promotion is a project decision informed by evidence, not simply `argmax(cv_score)`.

The numerical best score remains derivable from the registry, but `STATUS.md` may distinguish:

- `Robust Parent`
- `Apparent Best / Unconfirmed Best`

when useful.

## Search Strategy and Current-Best Gravity

The harness should not require a fixed 60/25/15 allocation or any universal experiment quota. Instead, it should make exploration state explicit.

`STATUS.md` contains a Search Map with meaningful branches for the current competition, for example:

| Search branch | State | Best evidence | Next question |
| --- | --- | --- | --- |
| Structured GBDT | active | ... | ... |
| Neural tabular | unexplored | ... | ... |
| Text representation | stalled | ... | ... |
| Ensemble | blocked | ... | ... |
| CV diagnostics | active | ... | ... |

Branch names are competition-specific and should not be hard-coded into scripts.

A strategic review is required before simply adding another near-neighbor experiment when one or more of the following are true:

- several consecutive experiments share the same parent lineage and only make local changes;
- recent improvements are consistently smaller than observed validation uncertainty;
- the active queue is dominated by one search branch;
- parameter tweaks are replacing hypothesis-driven changes;
- important branches remain unexplored without an explicit reason.

The response to such a review is not necessarily "try a different model". It may be better diagnostics, a data hypothesis, a new representation, an interaction test, or a deliberate decision to continue exploitation.

## Experiment vs Trial Boundary

The existing rule remains: different scientific hypotheses deserve separate experiments; small variations under one hypothesis should be trials.

The v2 policy strengthens this for homogeneous screening tasks. Examples that should normally remain one experiment with multiple trials when the scientific question is shared:

- parameter sweeps over a small candidate set;
- screening many individual features under one feature-screening hypothesis;
- exhaustive or selected pairwise feature comparisons;
- equivalent preprocessing variants;
- the same model family with small structural variations.

A new experiment is justified when the interpretation, causal question, data flow, model family, or validation question materially changes.

The goal is not to minimize experiment count for its own sake. The goal is to keep the registry at a useful semantic level.

## Agent Delegation and Quality Gates

The project must not hard-code a specific model name as the required main or worker agent.

Delegation should consider the cost of an error.

### Low-risk work

Examples:

- cloning or editing routine config fields;
- extracting metrics;
- formatting structured records;
- executing already-reviewed commands;
- updating routine documentation from authoritative artifacts.

These tasks may be delegated to cheaper or less capable workers.

### Medium-risk work

Examples:

- adding ordinary features;
- adding a model adapter;
- changing preprocessing that does not affect target leakage boundaries;
- refactoring reusable experiment code.

These tasks require targeted tests and review of the resulting diff before expensive execution.

### High-risk work

Examples:

- CV split logic;
- target-dependent preprocessing;
- leakage-sensitive joins;
- metric implementation;
- calibration and threshold logic;
- OOF construction;
- submission alignment;
- train/test row identity and label handling.

These tasks require strong verification before trusting experiment results.

Recommended quality gate for risky changes:

```text
implementation
→ targeted unit/invariant tests
→ smoke test
→ diff review against the intended hypothesis
→ small/cheap execution when possible
→ full experiment
```

A worker's completion report is not evidence that the implementation is correct. Authoritative artifacts, tests, diffs, and produced results must be inspected by the main decision-maker or a capable reviewer.

## Engineering Defaults

An operational lesson should become progressively harder to forget:

1. observe it;
2. record it in `ENGINEERING_NOTES.md` if reusable;
3. change config/code defaults when the recommendation is sufficiently general;
4. add a test or validation check when silent regression would be costly.

Resource settings should be explicit enough to inspect. Competition-specific code may expose fields such as CPU threads, device, memory-sensitive settings, or deterministic mode, but this design does not mandate a universal config schema for all libraries.

The template documentation should recommend avoiding accidental `n_jobs=1`-style defaults when safe parallelism is available, while still respecting shared servers and deterministic requirements.

## Source of Truth

The existing experiment-level sources of truth remain:

- executed definition: `experiments/<experiment_id>/config.yaml`
- numerical result: `experiments/<experiment_id>/metrics.json`
- execution provenance: `experiments/<experiment_id>/metadata.json`
- experiment interpretation: `experiments/<experiment_id>/README.md`
- experiment index: `experiments/experiments.csv`

Project-level sources become:

- current navigation and strategic state: `docs/STATUS.md`
- accumulated scientific knowledge: `docs/EXPERIMENT_SUMMARY.md`
- engineering/operational knowledge: `docs/ENGINEERING_NOTES.md`
- reusable harness-design knowledge: `docs/HARNESS_LESSONS.md`
- future hypothesis backlog: `docs/experiment_queue/`

When a concise project document conflicts with an experiment's immutable raw record, inspect the experiment record and repair the stale project document.

## Required Changes to Existing Rules

### `AGENTS.md`

Keep the core rules, but change the startup read order to prioritize the human control plane:

```text
AGENTS.md
→ docs/STATUS.md
→ docs/EXPERIMENT_SUMMARY.md as needed
→ experiments/experiments.csv
→ docs/experiment_queue/QUEUE.md when selecting future work
→ relevant experiment/config/source files
```

Add:

- search-map and strategic-review rules;
- screening/confirmation/promotion semantics;
- task-risk delegation and verification;
- engineering-lesson institutionalization;
- queue semantics;
- explicit statement that robust parent selection is not simply numerical argmax.

Remove or rewrite:

- language that treats `EXPERIMENT_SUMMARY.md` as the primary current-state entry point;
- any implication that one project document should contain current best, future plan, and all accumulated knowledge;
- overly generic autonomous-loop wording that encourages a new local experiment immediately after every result without strategic branch review.

### `README.md`

Update the project structure and onboarding flow to introduce the new documents. Keep the README practical rather than duplicating the full management specification.

### `docs/experiment_management.md`

Preserve experiment artifact, registry, Git, OOF, CV, data, and submission sections. Revise project-level knowledge, agent cycle, current-best interpretation, and guiding rules to match v2.

Where possible, remove duplicated explanations that now belong to dedicated documents instead of adding the same rule in several sections.

### Templates

Add:

- `docs/templates/status.md`
- `docs/templates/experiment_job.md`

Revise `experiment_summary.md` so it is a durable-knowledge template rather than the current-state dashboard.

Revise `experiment_readme.md` only where needed to encourage explicit uncertainty/confirmation recommendations and to distinguish experiment-specific next steps from queue management.

## Initial `HARNESS_LESSONS.md` Content

The first version should be a compact retrospective rather than a policy duplicate. It should explain what happened, why it mattered, and what design response v2 adopts.

Each lesson should use a structure similar to:

```markdown
## Lesson: Separate current state from accumulated knowledge

Observed failure mode:
- The project summary grew until it remained machine-useful but became slow for a human to scan.

Design response:
- `STATUS.md` is bounded and volatile.
- `EXPERIMENT_SUMMARY.md` stores durable knowledge.

General principle:
- Human navigation and long-term knowledge preservation have different compression requirements.
```

The document should include both successful patterns and failure modes so future revisions do not discard mechanisms that already worked.

## Validation and Acceptance Criteria

The documentation refactor is complete when:

1. A new human or agent can identify the current robust parent, active search branches, major findings, open strategic questions, and next candidates without reading historical experiment READMEs.
2. `EXPERIMENT_SUMMARY.md` no longer needs to carry the volatile current plan.
3. The source-of-truth mapping is unambiguous.
4. Queue documentation makes clear that jobs are hypotheses, not an automatic sequential run list.
5. Agent rules contain no hard-coded model name for worker quality.
6. Risky experiment-code changes have an explicit verification gate.
7. Engineering/resource lessons have a durable home and a rule for promoting lessons into defaults.
8. Small homogeneous sweeps are clearly directed toward trials rather than registry-spamming experiments.
9. The concept of robust parent vs apparent numerical best is documented without requiring a universal statistical threshold.
10. Existing strong rules—immutable completed experiments, standard CV comparability, raw-data immutability, OOF/provenance retention, negative-result recording, and submission separation—remain intact.
11. No new heavyweight dependency or experiment-management service is introduced.

## Future Extensions

Possible future work, only if actual project pain justifies it:

- a command that renders `STATUS.md` from structured registry data while preserving human-authored strategy sections;
- automated warnings for repeated same-lineage local experiments;
- resource profiles such as local CPU, shared CPU, and GPU;
- experiment-stage fields in registry/config if screening and confirmation become hard to track manually;
- a lightweight search-map or experiment-lineage visualization;
- automated consistency checks across STATUS, registry, and completed artifacts.

These are intentionally deferred until the documentation-first v2 rules are used in a real competition and their value is demonstrated.
