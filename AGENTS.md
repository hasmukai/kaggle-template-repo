# AGENTS.md

## Project Overview

This repository is a reusable template for data science competitions.

The primary goal is to improve local validation performance through rapid, reproducible experimentation while keeping the search strategy understandable to both humans and agents.

Public leaderboard submissions should be used sparingly. Model development and experiment selection should primarily rely on local cross-validation.

The harness has two equally important responsibilities:

1. preserve enough evidence to reproduce and interpret completed experiments;
2. keep the current search strategy visible so the project does not drift into unexamined local optimization.

---

## Startup Reading Order

Before proposing or implementing a new experiment, read only the context needed for the decision, in this order:

1. `AGENTS.md`
2. `docs/STATUS.md`
3. `experiments/experiments.csv`
4. `docs/EXPERIMENT_SUMMARY.md` when durable scientific findings are relevant
5. `docs/experiment_queue/QUEUE.md` when selecting or reviewing future work
6. relevant experiment directories, configs, and source files
7. `docs/ENGINEERING_NOTES.md` when runtime, resource use, determinism, cache, or environment behavior matters

Do not read every historical experiment by default.

Use `STATUS.md` and `experiments.csv` to identify the experiments that matter, then inspect their `README.md`, `config.yaml`, and `metrics.json` as needed.

For detailed experiment-management rules, consult `docs/experiment_management.md`.

---

## Project-Level Knowledge Responsibilities

Each project-level document has one primary role.

### `docs/STATUS.md`

The short, volatile human control plane.

It records the current robust parent, any apparent but unconfirmed best result, the Search Map, a few high-confidence findings and dead ends, open strategic questions, near-term candidates, and concise resource notes.

Keep it short enough to understand the project state in roughly five minutes.

### `docs/EXPERIMENT_SUMMARY.md`

The accumulated durable scientific knowledge of the project.

It records generalized findings about validation, data, model families, features, negative results, interactions, and caveats. It is not the active backlog and is not the canonical current-state dashboard.

### `docs/ENGINEERING_NOTES.md`

Reusable engineering and operational knowledge: CPU/GPU usage, parallelism, determinism, cache behavior, library pitfalls, memory constraints, and environment-specific execution notes.

### `docs/HARNESS_LESSONS.md`

Reusable lessons about the experiment harness itself. This is meta-level design knowledge, not competition-specific modeling knowledge.

### `docs/experiment_queue/`

The future hypothesis backlog. It is not an auto-execution plan and not an experiment history.

When a concise project-level document conflicts with immutable experiment artifacts, inspect the experiment artifacts and repair the stale project-level document.

---

## Experiment Principles

### Hypothesis-driven experiments

Every experiment must test a concrete hypothesis or diagnostic question.

Before modifying code, identify:

- the hypothesis;
- the logical parent experiment;
- what changes;
- what remains fixed;
- the decision metric or diagnostic;
- what information is gained if the result is positive or negative.

Prefer one meaningful scientific change at a time unless an interaction itself is the hypothesis.

### Experiment IDs

Experiment IDs follow:

`exp_NNN_short_description`

Example:

`exp_023_add_depth_feature`

Completed experiment IDs and their historical artifacts are immutable. Never reuse an ID for a different configuration or implementation.

### Parent experiments

Choose `parent_experiment` based on the hypothesis, not simply the most recent run or current numerical best.

The robust parent is the experiment currently considered reliable enough to serve as the default foundation for continued work. It may differ from an apparent numerical best that has not been sufficiently confirmed.

### Baseline

`exp_001_baseline` is the fixed baseline experiment once established.

If the baseline implementation is later found to be flawed, create a new corrective experiment. Do not rewrite historical results.

---

## Screening, Confirmation, and Promotion

These are evidence stages, not mandatory experiment types.

### Screening

Use the cheapest evaluation that reasonably answers the immediate question.

A screening result can justify further work, but a small apparent gain does not automatically become the new robust parent when it is plausibly within validation noise.

### Confirmation

Use stronger evidence when the decision warrants it, especially when:

- replacing the robust parent;
- the observed gain is small relative to known validation variation;
- fold or seed behavior is inconsistent;
- runtime/resource cost increases substantially for a small gain;
- the result would materially change project strategy.

Confirmation may use repeated seeds, repeated folds, alternate diagnostics, or another competition-appropriate robustness check. Do not impose one universal seed count or significance threshold.

### Promotion

Promotion is the decision to treat a result as a robust parent or otherwise change the project-level direction.

Promotion is evidence-informed, not simply `argmax(cv_score)`.

The experiment registry remains the source for numerical experiment history. `docs/STATUS.md` records the current strategic choice of robust parent and may separately note an apparent/unconfirmed best.

---

## Search Strategy and Strategic Review

The harness must make exploration breadth visible without enforcing a fixed exploration quota.

Maintain a competition-specific Search Map in `docs/STATUS.md`. Search branches can represent model families, representations, feature families, diagnostics, ensembles, validation questions, or other meaningful directions.

Before reflexively launching another near-neighbor experiment, perform a strategic review when one or more of these conditions are true:

- several consecutive experiments share the same parent lineage and only make local changes;
- recent gains are consistently small relative to observed validation uncertainty;
- parameter tweaks are replacing hypothesis-driven changes;
- the active queue is dominated by one search branch;
- important branches remain unexplored without an explicit reason.

A strategic review does not require switching model families. Valid outcomes include better diagnostics, a new data hypothesis, a new representation, an interaction test, a deliberate pause, or a reasoned decision to continue exploitation.

Do not launch a large speculative batch without evaluating intermediate results.

---

## Experiments vs Trials

Use a new **experiment** for a meaningfully different scientific question, feature family, preprocessing method, model family, data flow, validation design, target transformation, ensemble design, or other substantive change.

Use multiple **trials within one experiment** for homogeneous candidate comparisons under the same question.

Examples that should normally be trials rather than many experiment IDs:

- small hyperparameter grids;
- screening many individual features under one feature-screening hypothesis;
- pairwise feature comparisons under one interaction-screening hypothesis;
- equivalent preprocessing variants;
- the same model family with small structural variants.

The goal is to keep `experiments.csv` at a useful semantic level. Do not create one registry row per candidate value when the interpretation is shared.

Do not introduce Optuna or large-scale hyperparameter optimization unless there is a clear reason. Early effort should usually prioritize validation, data understanding, features, representations, and model design.

---

## Experiment Configuration

Each experiment is defined by one self-contained YAML file under `configs/`.

Prefer:

`1 experiment = 1 YAML`

over inheritance spread across many files.

Some duplication is acceptable if it makes an experiment independently understandable and reproducible.

Config should contain, as applicable:

- experiment ID;
- description;
- hypothesis;
- notes;
- parent experiment;
- experiment role;
- data configuration;
- preprocessing configuration;
- feature configuration;
- CV configuration;
- model configuration;
- training configuration;
- trial definitions;
- explicit resource/device settings when relevant.

When an experiment is executed, copy the exact executed config into its experiment result directory. That copy represents historical state and must not later be rewritten to describe a different run.

---

## Standard Cross-Validation

Local CV is the primary basis for model development.

Normal experiments should use a standard CV so scores remain directly comparable.

CV design itself may be tested separately. When using a non-standard CV:

- clearly identify the scheme;
- state what it is intended to test;
- do not compare its score to standard-CV experiments as though they were equivalent.

Preserve actual fold assignment when practical rather than relying only on a random seed.

---

## Experiment Execution

Formal experiments should be reproducible through the experiment pipeline:

`config -> preprocessing -> feature generation -> CV training -> evaluation -> result persistence`

Avoid undocumented manual preprocessing required for reproduction.

An experiment should be runnable through a single command when practical.

Do not perform unnecessary full-data training or test prediction during ordinary CV experimentation.

Failed runs should preserve useful diagnostic information when possible.

---

## Experiment Results

Experiment outputs live under:

`experiments/<experiment_id>/`

Typical lightweight records include:

- `config.yaml`
- `metrics.json`
- `metadata.json`
- `README.md`

Potential generated artifacts include:

- OOF predictions;
- logs;
- trial results;
- feature importance;
- Git diff;
- diagnostic tables.

### `metrics.json`

Machine-readable evaluation results. Store primary metric, overall CV score, fold statistics, fold-level scores, useful secondary metrics, timing, trial results, and best trial as applicable.

Do not place qualitative interpretation in `metrics.json`.

### `metadata.json`

Execution provenance: timestamps, duration, Git commit, dirty state, relevant environment information, and similar provenance.

### OOF predictions

Preserve OOF predictions for completed experiments whenever practical. They are important for error analysis, experiment comparison, ensembling, calibration analysis, and validation diagnostics.

They do not need to be committed to Git.

---

## Experiment Documentation

Every completed experiment must have a `README.md` following `docs/templates/experiment_readme.md`.

At minimum document:

- hypothesis;
- changes from parent;
- important results;
- analysis;
- conclusion;
- whether the hypothesis was supported;
- whether confirmation is needed before changing the robust parent;
- a small number of local next questions.

Distinguish observed facts from interpretation.

Negative results are valuable. A completed experiment with worse performance is still `completed`, not `failed`.

Persistent future hypotheses belong in `docs/experiment_queue/`, not as an ever-growing list in each experiment README.

---

## Experiment Registry

`experiments/experiments.csv` is the compact experiment registry and source for numerical experiment history.

It should contain concise fields such as:

- experiment ID;
- parent experiment;
- description;
- hypothesis;
- status;
- role;
- CV scheme;
- CV score;
- CV standard deviation;
- model;
- number of trials;
- duration;
- Git commit;
- Git dirty state;
- creation time.

Do not put deeply nested information into the CSV. Detailed metrics belong in `metrics.json`; detailed interpretation belongs in experiment README files.

Do not manually maintain another numerical experiment table in project-level docs.

---

## Engineering Knowledge

Reusable speed, reliability, or environment findings belong in `docs/ENGINEERING_NOTES.md`.

Once an operational lesson is learned, make it progressively harder to forget:

1. record the observation;
2. document the reusable recommendation;
3. change code/config defaults when the recommendation is sufficiently general and safe;
4. add validation or a test when silent regression would be costly.

Do not rely on memory for known parallelism, device, cache, determinism, or library pitfalls.

Avoid accidental single-thread defaults when safe parallelism is available, while respecting shared-server limits, deterministic requirements, and memory constraints.

---

## Agent Delegation and Verification

Do not hard-code a particular model name as the required main or worker agent. Delegate based on the cost of an error.

### Low-risk work

Examples:

- routine config edits;
- extracting metrics;
- formatting structured records;
- executing already-reviewed commands;
- routine documentation updates from authoritative artifacts.

These can be delegated to cheaper or less capable workers.

### Medium-risk work

Examples:

- ordinary feature implementation;
- model adapters;
- preprocessing changes that do not cross target/leakage boundaries;
- refactoring reusable experiment code.

Require targeted tests and review the resulting diff before expensive execution.

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

Recommended quality gate:

`implementation -> targeted unit/invariant tests -> smoke test -> diff review -> cheap execution when possible -> full experiment`

A worker completion report is not proof. Verify authoritative artifacts, tests, diffs, executed configs, and produced results before trusting the experiment.

---

## Data Management

Use the conceptual separation:

- `data/raw/` — original competition data;
- `data/processed/` — reproducible processed datasets;
- `data/cache/` — disposable performance caches.

Treat `data/raw/` as immutable.

Processed data must be reproducible from raw data, source code, and configuration. Do not depend on undocumented manual transformations.

Document processed datasets in `data/processed/README.md`.

Cache deletion must not change experiment semantics. Cache should be regenerable.

---

## Notebooks and Source Code

Use `notebooks/` for EDA, visualization, validation analysis, error analysis, and exploratory investigation.

Do not make notebooks the only implementation of preprocessing, feature generation, training, or evaluation required for reproducible experiments.

Move reusable formal experiment logic into `src/`.

Keep modules focused. Do not introduce abstractions or directory layers before they are needed, but do not allow a general-purpose runner to accumulate unlimited model-specific branches. When a file becomes difficult to reason about, split by responsibility rather than continuing to grow it for convenience.

Avoid unrelated refactoring during an experiment.

---

## Submission Policy

Submission generation is separate from ordinary CV experimentation.

Do not use the public leaderboard as the primary feedback mechanism.

Create submissions only when an experiment has a concrete reason to be evaluated externally. Every submission must be traceable to the experiment it is based on.

Models generally do not need to be permanently saved. Prefer reconstructing selected experiments from config, code state, and data when a full-data model is needed.

---

## Model Artifacts

Do not save model checkpoints for every experiment by default.

Prioritize saving:

- configs;
- metrics;
- metadata;
- OOF predictions;
- diagnostic information;
- interpretation.

Keep large reproducible artifacts out of Git unless there is a concrete reason to preserve them.

---

## Git Policy

Git is used for version control, backup, historical archive, and reproducibility, not as storage for large generated artifacts.

Commit lightweight project knowledge:

- source code;
- scripts;
- configs;
- tests;
- documentation;
- experiment READMEs;
- metrics/metadata when lightweight;
- experiment summaries and queue metadata.

Do not commit large generated artifacts such as raw competition data, processed datasets, caches, large OOF files, model checkpoints, large logs, or generated submissions unless there is a specific reason.

Experiments may run with a dirty working tree. When they do:

1. record the current Git commit;
2. record that the tree was dirty;
3. automatically preserve the relevant Git diff with the experiment.

Do not rely on a commit hash alone when uncommitted code affected the run.

---

## Testing

Keep the suite focused on failures that would make experiment results unreliable.

Prioritize:

- preprocessing invariants;
- CV splitting;
- metric calculation;
- important data joins;
- leakage prevention;
- submission format and integrity;
- other critical data-flow assumptions.

Run targeted tests for ordinary changes. Run broader tests when shared infrastructure changes.

Training completing successfully is not proof that preprocessing or validation logic is correct.

---

## Experiment Queue

Use `docs/experiment_queue/` for future hypotheses that should persist beyond a single experiment README.

The queue is a backlog, not a batch script.

- humans and agents may add jobs;
- jobs do not reserve experiment IDs;
- priorities may change after every meaningful result;
- queue entries may become blocked, paused, superseded, or require review;
- experiment history belongs in `experiments/`, not the queue.

Use Expected Information Gain, evidence quality, expected benefit, compute/implementation cost, confounding risk, and downstream value when prioritizing.

---

## Autonomous Experimentation

When asked to continue experimentation autonomously, use this loop:

1. Read `AGENTS.md`, `docs/STATUS.md`, and `experiments/experiments.csv`.
2. Identify the active strategic question and relevant Search Map branch.
3. Read durable summary/queue/engineering notes only as needed.
4. Inspect only the relevant experiment artifacts.
5. Form or select one justified hypothesis.
6. Choose the logical parent and decide experiment vs trial.
7. Make the minimum implementation/config change.
8. Run the verification appropriate to task risk.
9. Run a screening experiment.
10. Analyze evidence relative to parent, baseline, numerical best, and observed uncertainty.
11. Decide whether confirmation is needed before promotion.
12. If confirmation is warranted, run an appropriate robustness check before replacing the robust parent.
13. Write the experiment README and update registry/artifacts.
14. Update `EXPERIMENT_SUMMARY.md` only for durable scientific knowledge.
15. Update `ENGINEERING_NOTES.md` when a reusable operational lesson was learned.
16. Update `STATUS.md` when current strategy, robust parent, Search Map, or near-term decisions changed.
17. Re-evaluate relevant queue jobs and the overall Search Map before selecting the next experiment.

Do not interpret every completed result as an instruction to create another local experiment on the same lineage.

---

## Source of Truth

### Experiment definition

`experiments/<experiment_id>/config.yaml`

### Numerical result

`experiments/<experiment_id>/metrics.json`

### Execution provenance

`experiments/<experiment_id>/metadata.json`

### Experiment interpretation

`experiments/<experiment_id>/README.md`

### Experiment index / numerical history

`experiments/experiments.csv`

### Current navigation and strategic state

`docs/STATUS.md`

### Durable scientific knowledge

`docs/EXPERIMENT_SUMMARY.md`

### Engineering / operational knowledge

`docs/ENGINEERING_NOTES.md`

### Harness meta-knowledge

`docs/HARNESS_LESSONS.md`

### Future hypothesis backlog

`docs/experiment_queue/`

---

## General Development Rules

- Preserve reproducibility.
- Prefer simple implementations.
- Make one meaningful experimental change at a time when possible.
- Do not modify raw competition data.
- Do not overwrite historical experiment results.
- Do not silently change the standard CV.
- Do not optimize primarily against the public leaderboard.
- Do not add unnecessary dependencies.
- Do not introduce infrastructure before it is needed.
- Record negative results as carefully as positive ones.
- Keep generated heavy files out of Git.
- Make important decisions discoverable in the correct project document.
- Do not rely on chat history as the source of truth for experiment state.
- When uncertain, inspect authoritative artifacts and existing rules before inventing a new convention.
