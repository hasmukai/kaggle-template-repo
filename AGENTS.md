# AGENTS.md

## Project Overview

This repository is a reusable template for data science competitions.

The primary goal of this project is to improve local validation performance through rapid, reproducible experimentation.

The standard development loop is:

1. Review previous experiments.
2. Form a concrete hypothesis.
3. Create a new experiment based on an appropriate parent experiment.
4. Make the minimum code/configuration changes necessary to test the hypothesis.
5. Run the experiment using the standard local CV.
6. Record all results.
7. Analyze whether the hypothesis was supported.
8. Update the accumulated experiment knowledge when appropriate.
9. Use the findings to decide the next experiment.

Public leaderboard submissions should be used sparingly. Model development and experiment selection should primarily rely on local cross-validation.

---

## Agent Workflow

Before proposing or implementing a new experiment, read the following in this order:

1. `AGENTS.md`
2. `docs/EXPERIMENT_SUMMARY.md`
3. `experiments/experiments.csv`
4. Relevant experiment directories under `experiments/`
5. Relevant configs under `configs/`
6. Relevant implementation under `src/`

Do not read every historical experiment in detail by default.

Use `EXPERIMENT_SUMMARY.md` and `experiments.csv` to identify the experiments relevant to the current task, then inspect their:

* `README.md`
* `config.yaml`
* `metrics.json`

as needed.

When the detailed experiment-management specification is required, consult:

`docs/experiment_management.md`

---

## Experiment Principles

### Hypothesis-driven experiments

Every experiment must test a concrete hypothesis.

Do not create experiments whose only purpose is to "try something" without a reason.

Before modifying code, clearly identify:

* the hypothesis;
* the parent experiment;
* what will change;
* what will remain unchanged;
* which metric will determine whether the change was beneficial.

Prefer experiments that isolate one meaningful change at a time.

### Experiment IDs

Experiment IDs follow:

`exp_NNN_short_description`

Example:

`exp_023_add_depth_feature`

Experiment IDs are immutable after a completed experiment has been recorded.

Do not reuse an existing experiment ID for a different configuration or implementation.

### Parent experiments

New experiments should normally be derived from an existing experiment.

Record the parent using `parent_experiment`.

Choose the parent based on the hypothesis being tested, not simply the most recently executed experiment.

### Baseline and current best

`exp_001_baseline` is the fixed baseline experiment.

Do not modify the meaning or results of the baseline after it has been established.

The current best experiment is determined automatically from experiments evaluated using the standard CV.

Experiments using incompatible CV schemes must not be directly treated as improvements over the standard-CV current best.

---

## Experiments vs Trials

Use a new **experiment** when testing a meaningfully different hypothesis, feature set, preprocessing method, model design, CV design, or other substantive change.

Use multiple **trials within one experiment** when testing small parameter variations under the same hypothesis.

For example, testing:

* `max_depth = 6`
* `max_depth = 8`
* `max_depth = 10`

should normally be one experiment with multiple trials rather than three separate experiments.

Small trial grids may be declared directly in the experiment YAML.

Do not introduce Optuna or large-scale hyperparameter optimization unless there is a clear reason to do so.

Hyperparameter tuning is not an early-stage priority. Prefer improvements to validation, data understanding, preprocessing, features, and model design first.

---

## Experiment Configuration

Each experiment is defined by one self-contained YAML file under `configs/`.

Prefer:

`1 experiment = 1 YAML`

over configuration inheritance spread across many files.

Some duplication is acceptable if it makes an experiment understandable and reproducible from a single config.

Experiment configs should contain, as applicable:

* experiment ID;
* description;
* hypothesis;
* notes;
* parent experiment;
* experiment role;
* data configuration;
* preprocessing configuration;
* feature configuration;
* CV configuration;
* model configuration;
* training configuration;
* trial definitions.

The detailed schema is documented in:

`docs/experiment_management.md`

When an experiment is executed, copy the exact executed configuration into the corresponding experiment result directory.

The copied configuration represents historical state and must not later be edited to describe a different run.

---

## Standard Cross-Validation

Local CV is the primary basis for model development.

A standard CV scheme should be used for normal experiments so results remain directly comparable.

CV design itself is an important research target and may be experimented with separately.

When using a non-standard CV:

* clearly identify the CV scheme;
* do not directly compare its score with standard-CV experiments as though they were equivalent;
* document what the alternative CV is intended to test.

Preserve the actual fold assignment when practical rather than relying only on a random seed to reproduce it.

---

## Experiment Execution

Feature generation and preprocessing used by an experiment must be executable as part of the experiment pipeline.

Avoid manual preprocessing steps required to reproduce an experiment.

The intended execution flow is conceptually:

`config -> preprocessing -> feature generation -> CV training -> evaluation -> result persistence`

An experiment should be runnable through a single command.

Experiment execution must record results even when useful diagnostic information is produced during a failed run.

Do not perform unnecessary full-data training or test prediction during ordinary CV experimentation.

---

## Experiment Results

Experiment outputs are stored under:

`experiments/<experiment_id>/`

Typical lightweight records include:

* `config.yaml`
* `metrics.json`
* `metadata.json`
* `README.md`

Potential generated artifacts include:

* OOF predictions;
* logs;
* trial results;
* feature importance;
* Git diff;
* other diagnostic outputs.

The exact format is defined in:

`docs/experiment_management.md`

### metrics.json

`metrics.json` contains machine-readable evaluation results.

It should contain, when applicable:

* primary metric;
* overall CV score;
* fold mean;
* fold standard deviation;
* fold-level scores;
* best iteration per fold;
* training time;
* preprocessing/training/prediction timing;
* useful secondary metrics;
* trial results;
* best trial.

Do not put qualitative experiment analysis in `metrics.json`.

### metadata.json

`metadata.json` describes the execution environment and provenance rather than model performance.

Record information such as:

* execution timestamp;
* duration;
* Git commit;
* whether the working tree was dirty;
* relevant environment information.

### OOF predictions

Preserve OOF predictions for completed experiments whenever practical.

OOF predictions are important for:

* error analysis;
* comparing experiments;
* ensemble analysis;
* CV diagnostics.

They do not need to be committed to Git.

---

## Experiment Documentation

Every completed experiment must have a `README.md`.

Follow:

`docs/templates/experiment_readme.md`

The experiment README should explain the experiment rather than duplicate machine-readable metrics.

At minimum, document:

* hypothesis;
* changes from the parent;
* important results;
* analysis;
* conclusion;
* possible next steps.

Explicitly state whether the evidence supports the original hypothesis.

Failed or negative experiments are valuable. Do not hide them merely because performance decreased.

---

## Experiment Registry

`experiments/experiments.csv` is the compact experiment registry.

Its purpose is to make experiments easy for both humans and agents to scan, filter, and compare.

It should contain concise information such as:

* experiment ID;
* parent experiment;
* description;
* hypothesis;
* status;
* role;
* CV scheme;
* CV score;
* CV standard deviation;
* model;
* number of trials;
* duration;
* Git commit;
* Git dirty state;
* creation time.

Do not put large or deeply nested information into this CSV.

Detailed metrics belong in `metrics.json`.

Detailed interpretation belongs in the experiment `README.md`.

---

## Experiment Summary

`docs/EXPERIMENT_SUMMARY.md` is the high-level accumulated knowledge of the project.

It is one of the primary entry points for both humans and agents.

Follow:

`docs/templates/experiment_summary.md`

It should summarize topics such as:

* baseline;
* current best;
* approaches that worked;
* approaches that did not work;
* CV findings;
* open questions;
* promising ideas.

Update it when an experiment produces information that materially changes the project's understanding.

Do not mechanically add every experiment to the summary.

The summary should remain concise enough to quickly understand the current state of the competition work.

---

## Data Management

Use the following conceptual separation:

* `data/raw/` — original competition data;
* `data/processed/` — reproducible processed datasets;
* `data/cache/` — disposable caches used for speed.

### Raw data

Treat `data/raw/` as immutable.

Never modify the original competition files in place.

### Processed data

Processed data must be reproducible from:

* raw data;
* source code;
* experiment/configuration information.

Do not create processed datasets through undocumented manual operations.

Document processed datasets in:

`data/processed/README.md`

The README should explain:

* what each processed dataset represents;
* its source data;
* how it was generated;
* relevant preprocessing;
* any important caveats.

Deleting `data/processed/` should not destroy unique project knowledge.

### Cache

`data/cache/` exists only for performance.

Code must remain logically correct if caches are deleted and regenerated.

---

## Notebooks

Use `notebooks/` primarily for:

* EDA;
* visualization;
* CV analysis;
* error analysis;
* exploratory investigation.

Do not make notebooks the only implementation of preprocessing, feature generation, training, or evaluation required for reproducible experiments.

When exploratory notebook code becomes part of a real experiment, move the reusable logic into `src/`.

In short:

`notebooks = exploration and analysis`

`src = reproducible experiment logic`

---

## Source Code

Keep reusable experiment logic under `src/`.

Typical responsibilities include:

* preprocessing;
* feature generation;
* models;
* CV;
* metrics;
* shared utilities.

Keep modules focused.

Do not introduce abstractions, frameworks, or directory layers before they are needed.

Prefer simple code that is easy for both humans and agents to inspect and modify.

Avoid unrelated refactoring during an experiment.

---

## Submission Policy

Submissions to competition platforms should be relatively rare.

Do not use the public leaderboard as the primary experiment-feedback mechanism.

Only create submissions from experiments that have a concrete reason to be evaluated externally.

Submission generation should be separate from ordinary CV experimentation.

A submission should be traceable back to the experiment on which it is based.

Models generally do not need to be permanently saved.

When a submission is needed, the preferred workflow is to reconstruct the selected experiment from its configuration and code state, train on the appropriate full training data, and generate test predictions.

---

## Model Artifacts

Do not save model checkpoints for every experiment by default.

The experiment system should prioritize saving:

* configurations;
* metrics;
* metadata;
* OOF predictions;
* diagnostic information.

Models should normally be reproducible by retraining.

Large model artifacts should only be preserved when there is a concrete reason.

---

## Git Policy

Git is used primarily for:

* version control;
* backup;
* historical archival;
* reproducibility.

It is not intended to be the storage mechanism for large generated experiment artifacts.

Commit lightweight project knowledge, including:

* source code;
* scripts;
* configs;
* tests;
* documentation;
* experiment summaries;
* lightweight experiment metadata and analysis.

Do not commit large reproducible/generated artifacts such as:

* raw competition data;
* processed datasets;
* caches;
* large OOF files;
* model checkpoints;
* large logs;
* generated submission files unless there is a specific reason.

### Dirty working trees

Experiments may be executed while the Git working tree contains uncommitted changes.

When this happens:

1. record the current Git commit;
2. record that the working tree was dirty;
3. automatically preserve the relevant Git diff with the experiment.

Do not rely on a commit hash alone when the experiment used uncommitted code.

This mechanism should be automatic rather than requiring the user to manually manage experiment diffs.

---

## Testing

Keep the test suite lightweight and focused on failures that would make experiment results unreliable.

Prioritize tests for:

* preprocessing invariants;
* CV splitting;
* evaluation metrics;
* submission format and integrity;
* other critical data-flow assumptions.

Do not attempt to unit-test every experimental feature or model variation.

When changing a specific component, run the tests relevant to that component rather than automatically running unrelated expensive tests.

---

## Autonomous Experimentation

Agents may be asked to autonomously perform the full experimentation cycle.

When doing so:

1. Read the project summary and experiment registry.
2. Identify relevant previous experiments.
3. Inspect their detailed results.
4. Form one justified hypothesis.
5. Select an appropriate parent experiment.
6. Decide whether the change deserves a new experiment or only a trial.
7. Create the experiment definition.
8. Make the minimum necessary implementation changes.
9. Run appropriate targeted tests.
10. Run the experiment using the appropriate CV.
11. Record all results.
12. Analyze the result against the original hypothesis.
13. Write the experiment README.
14. Update `experiments.csv`.
15. Update `EXPERIMENT_SUMMARY.md` only when project-level knowledge has materially changed.
16. Recommend the next action based on evidence.

Do not launch a large sequence of speculative experiments without evaluating intermediate results.

Do not perform expensive hyperparameter searches by default.

Prefer learning from each experiment before choosing the next one.

---

## General Development Rules

* Preserve reproducibility.
* Prefer simple implementations.
* Make one meaningful experimental change at a time when possible.
* Do not modify raw competition data.
* Do not overwrite historical experiment results.
* Do not silently change the standard CV.
* Do not optimize against the public leaderboard.
* Do not add unnecessary dependencies.
* Do not introduce infrastructure before it is needed.
* Record negative results as carefully as positive ones.
* Keep generated heavy files out of Git.
* Make important decisions discoverable in project documentation.
* When uncertain, inspect existing experiments and documentation before inventing a new convention.
