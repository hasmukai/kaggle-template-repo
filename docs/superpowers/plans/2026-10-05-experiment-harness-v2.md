# Experiment Harness v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the competition experiment harness documentation so humans and agents can jointly control experimentation without losing the strong reproducibility guarantees of the current template.

**Architecture:** Keep experiment artifacts, registry, configs, CV policy, and execution code unchanged. Reorganize project-level knowledge into separate current-state, scientific-knowledge, engineering-knowledge, harness-lesson, and experiment-queue documents; then update `AGENTS.md`, `README.md`, templates, and `docs/experiment_management.md` so every rule points to one clear responsibility instead of duplicating state across documents.

**Tech Stack:** Markdown documentation, YAML/CSV conventions already defined by the repository, existing Python/pytest project unchanged.

**Spec:** `docs/superpowers/specs/2026-10-05-experiment-harness-v2-design.md`

## Global Constraints

- Preserve the existing experiment-level source-of-truth mapping: executed config, metrics, metadata, experiment README, and registry.
- Preserve immutable completed experiments, standard-CV comparability, raw-data immutability, OOF/provenance retention, negative-result recording, and submission separation.
- Do not add MLflow, Weights & Biases, Optuna, distributed execution, dashboards, or other heavyweight experiment-management dependencies.
- Do not hard-code a particular LLM or coding-agent model into project policy.
- Do not impose a universal exploration percentage, universal seed count, or universal statistical threshold.
- Do not change the Python experiment runner or model implementation in this revision.
- Keep `docs/STATUS.md` deliberately short and decision-oriented; do not turn it into an experiment history.
- Keep `docs/EXPERIMENT_SUMMARY.md` focused on durable scientific knowledge, not volatile next actions.
- Prefer removing or relocating duplicated rules over copying the same rule into more files.

## Review Focus

1. **Conflicting current-best definitions:** numerical best in the registry must not be confused with the robust parent chosen for ongoing work; documentation must explicitly distinguish them where needed.
2. **Knowledge duplication:** `STATUS.md`, `EXPERIMENT_SUMMARY.md`, `ENGINEERING_NOTES.md`, and queue files must not all become alternate homes for the same information.
3. **Over-constrained strategy rules:** search breadth and confirmation must be guided without hard-coding model families, experiment quotas, or seed counts that may be wrong for another competition.
4. **Delegation safety:** risky changes such as CV, leakage-sensitive preprocessing, metric code, OOF construction, and submission alignment must require verification independent of a worker's completion report.
5. **Regression of existing strengths:** the refactor must not weaken immutable experiment records, fixed CV comparison rules, provenance capture, experiment/trial semantics, raw-data policy, or negative-result recording.

---

### Task 1: Add the project-level control-plane documents and queue

**Files:**
- Create: `docs/STATUS.md`
- Create: `docs/ENGINEERING_NOTES.md`
- Create: `docs/HARNESS_LESSONS.md`
- Create: `docs/experiment_queue/README.md`
- Create: `docs/experiment_queue/QUEUE.md`
- Create: `docs/templates/status.md`
- Create: `docs/templates/experiment_job.md`

**Interfaces:**
- Consumes: roles and acceptance criteria from the design spec.
- Produces: the canonical document responsibilities later referenced by `AGENTS.md`, `README.md`, and `experiment_management.md`.

- [ ] **Step 1: Create `docs/STATUS.md` as the initialized human control plane**

Include exactly these top-level concepts: project goal, Robust Parent, Apparent Best / Unconfirmed Best, Search Map, High-confidence Findings, Dead Ends / Deprioritized Directions, Open Strategic Questions, Next Candidates, Resource Notes, Last Updated. Initialize competition-specific fields as not yet established rather than inventing values.

- [ ] **Step 2: Create `docs/templates/status.md` with explicit size discipline**

State that STATUS is a short decision document, not a changelog or knowledge archive. Keep the same section names as `docs/STATUS.md` and include guidance that High-confidence Findings and Dead Ends stay around five items, while Open Strategic Questions and Next Candidates stay around three.

- [ ] **Step 3: Create `docs/ENGINEERING_NOTES.md`**

Define the note structure: Recommendation, Evidence, Scope, Last Verified, Caveat. Explain the promotion path `observe -> document -> change default when safe -> add validation/test when silent regression is costly`. Seed the document with generic resource guidance only; do not claim benchmark evidence that does not exist in this template.

- [ ] **Step 4: Create `docs/HARNESS_LESSONS.md` as a retrospective, not policy duplication**

Document both what worked and what failed in the prior competition harness. Each lesson should contain Observed pattern/failure mode, Design response, and General principle. Cover at minimum: reproducibility/immutable artifacts, human-vs-agent context separation, current-best gravity, exploration visibility, screening/confirmation, experiment-vs-trial granularity, engineering-knowledge persistence, task-risk delegation, artifact/test verification, modularity pressure in experiment runners, and post-competition harness retrospectives.

- [ ] **Step 5: Create `docs/experiment_queue/README.md`**

Specify queue purpose, statuses (`ready`, `blocked`, `needs_review`, `paused`, `superseded`), prioritization by expected information gain/evidence/cost/confounding, and the rules that the queue is a backlog rather than an auto-run list, humans may add hypotheses, selected jobs receive experiment IDs only at execution time, and priorities are reconsidered after meaningful results.

- [ ] **Step 6: Create `docs/experiment_queue/QUEUE.md`**

Use a concise table with fields `Job`, `Status`, `Priority`, `Search Branch`, `Hypothesis`. Initialize it with no fabricated jobs and a short instruction pointing detailed proposals to job files.

- [ ] **Step 7: Create `docs/templates/experiment_job.md`**

Use these fields: Hypothesis, Motivation / Evidence, Search Branch, Parent Candidate, Proposed Change, Fixed Conditions, Decision Metric, Expected Information Gain, Dependencies, Re-evaluation Triggers, Execution Notes.

- [ ] **Step 8: Verify Task 1 responsibility boundaries**

Check that:
- current actions live in STATUS, not HARNESS_LESSONS;
- scientific findings are not duplicated into ENGINEERING_NOTES;
- queue contains proposals, not experiment history;
- HARNESS_LESSONS explains meta-level lessons rather than repeating the full rulebook.

- [ ] **Step 9: Commit Task 1**

Commit message: `docs: add harness control plane and experiment queue`

---

### Task 2: Convert experiment summaries from dashboard-plus-history into durable knowledge

**Files:**
- Modify: `docs/EXPERIMENT_SUMMARY.md`
- Modify: `docs/templates/experiment_summary.md`
- Modify: `docs/templates/experiment_readme.md`

**Interfaces:**
- Consumes: STATUS role from Task 1.
- Produces: durable scientific-knowledge documents that no longer carry volatile next-action state.

- [ ] **Step 1: Rewrite `docs/templates/experiment_summary.md`**

Keep durable sections for Baseline/reference context, What Worked, What Did Not Work, CV Findings, Data Findings, Model Findings, Feature Findings, Interactions/Caveats, and Last Updated. Remove `Current Best`, `Promising Ideas`, `Current Direction`, and other volatile planning sections now owned by STATUS/queue. State explicitly that this file consolidates generalizable findings rather than appending every experiment.

- [ ] **Step 2: Rewrite the initial `docs/EXPERIMENT_SUMMARY.md` to match the new template**

Retain only facts actually supported by the empty template project: no experiments yet, standard CV not yet defined, no scientific findings yet. Point current-state and next-action readers to `docs/STATUS.md` instead of duplicating those sections here.

- [ ] **Step 3: Revise `docs/templates/experiment_readme.md`**

Keep Hypothesis, Changes, Results, Analysis, Conclusion, Next, Notes. Add explicit prompts to assess uncertainty relative to CV variation and to state whether the result needs confirmation before it should affect a robust parent. Clarify that `Next` contains experiment-specific implications; persistent backlog management belongs in `docs/experiment_queue/`.

- [ ] **Step 4: Verify Review Focus items 1 and 2**

Search these three files and confirm:
- no summary template instructs users to maintain a second current-best source of truth;
- no active next-experiment backlog lives in `EXPERIMENT_SUMMARY.md`;
- robust-parent confirmation guidance appears in experiment README guidance, without a fixed seed count or numeric threshold.

- [ ] **Step 5: Commit Task 2**

Commit message: `docs: separate durable experiment knowledge from current status`

---

### Task 3: Refactor `AGENTS.md` into the v2 operating rules

**Files:**
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: all project-level document roles from Tasks 1-2.
- Produces: the primary operational contract for coding agents.

- [ ] **Step 1: Change the startup read order**

Set the default order to:

```text
AGENTS.md
-> docs/STATUS.md
-> experiments/experiments.csv
-> docs/EXPERIMENT_SUMMARY.md as needed
-> docs/experiment_queue/QUEUE.md when selecting future work
-> relevant experiment/config/source files
-> docs/ENGINEERING_NOTES.md when runtime/resource behavior matters
```

Do not require reading every durable document on every task.

- [ ] **Step 2: Add explicit project-level source responsibilities**

Document STATUS = current strategy, EXPERIMENT_SUMMARY = durable scientific knowledge, ENGINEERING_NOTES = operational knowledge, HARNESS_LESSONS = reusable harness meta-knowledge, queue = future hypotheses.

- [ ] **Step 3: Add Screening / Confirmation / Promotion semantics**

State that screening evidence may justify further work but a fragile small gain does not automatically replace the robust parent. Confirmation is required when the decision warrants stronger evidence, especially for small/unstable gains or strategy-changing promotion. Do not prescribe a universal seed count.

- [ ] **Step 4: Add Search Map and strategic-review rules**

Require a strategic review before reflexively adding another local experiment when the same lineage dominates, gains are below validation uncertainty, parameter tweaks replace hypotheses, the queue is branch-skewed, or major branches remain unexplored without reason. Explicitly allow the review to conclude that continued exploitation is still correct.

- [ ] **Step 5: Strengthen experiment-vs-trial guidance**

Add homogeneous screening examples: individual feature screening, pairwise feature comparisons, small model-structure variants, preprocessing variants, and small hyperparameter grids should normally be trials when they test one shared scientific question.

- [ ] **Step 6: Add task-risk delegation rules**

Define low-, medium-, and high-risk examples from the spec. Require targeted tests/diff review for medium risk and stronger verification for high-risk CV/leakage/metric/OOF/submission changes. State that worker reports are not proof.

- [ ] **Step 7: Add engineering-lesson institutionalization rule**

Require reusable speed/reliability findings to be added to ENGINEERING_NOTES and, when general enough, promoted into safer defaults or validation checks instead of relying on memory.

- [ ] **Step 8: Rewrite the autonomous experiment cycle**

Replace the implicit `result -> next local experiment` flow with `understand status -> choose strategic question -> inspect evidence -> choose queue hypothesis/parent -> implement/test -> screen -> analyze uncertainty -> confirm if promotion depends on fragile evidence -> update appropriate knowledge -> re-evaluate search map/queue`.

- [ ] **Step 9: Remove obsolete responsibility overlap**

Remove language that describes `EXPERIMENT_SUMMARY.md` as the main current-state dashboard or as the place for active next-direction planning. Keep all strong reproducibility, CV, data, Git, result, testing, and submission rules that do not conflict with v2.

- [ ] **Step 10: Verify Review Focus items 3-5**

Confirm `AGENTS.md` contains:
- no fixed exploration quota;
- no fixed confirmation seed count;
- no named required LLM model;
- explicit verification for high-risk changes;
- unchanged immutable completed-experiment policy, standard-CV comparability, raw-data immutability, provenance, negative-result, and submission-separation rules.

- [ ] **Step 11: Commit Task 3**

Commit message: `docs: update agent rules for harness v2`

---

### Task 4: Align the detailed experiment-management specification

**Files:**
- Modify: `docs/experiment_management.md`

**Interfaces:**
- Consumes: v2 rules from `AGENTS.md` and document responsibilities from Tasks 1-2.
- Produces: the detailed normative reference without contradicting the concise agent rules.

- [ ] **Step 1: Update the document's context-loading guidance**

Replace the old `AGENTS -> EXPERIMENT_SUMMARY -> registry` sequence with the v2 order centered on STATUS and selective reading.

- [ ] **Step 2: Update Current Best semantics**

Keep numerical best derivable from the registry, but explain that the robust parent used for future work is a project decision that may differ from an unconfirmed numerical argmax. Point the current strategic choice to STATUS.

- [ ] **Step 3: Add Screening / Confirmation / Promotion as evidence concepts**

Place them near experiment evaluation/current-best sections. Make confirmation conditional on decision risk and uncertainty, not mandatory for every experiment.

- [ ] **Step 4: Strengthen the Experiment-vs-Trial section**

Add homogeneous feature/pair/model-variant screening examples and the semantic-level rationale: registry rows should represent distinct scientific questions, not every candidate value.

- [ ] **Step 5: Replace the old EXPERIMENT_SUMMARY update section with project-knowledge routing**

Define when to update STATUS, EXPERIMENT_SUMMARY, ENGINEERING_NOTES, HARNESS_LESSONS, and queue. Keep experiment README/metrics/metadata/registry as experiment-level records.

- [ ] **Step 6: Rewrite the autonomous cycle**

Mirror the strategic v2 cycle from `AGENTS.md` but keep implementation details here. Include explicit search-map/queue re-evaluation after meaningful results and confirmation before robust-parent promotion when evidence is fragile.

- [ ] **Step 7: Update Source of Truth section**

Keep all experiment-level mappings and add the five project-level mappings from the spec. State that concise documents are repaired when they conflict with immutable experiment records.

- [ ] **Step 8: Add engineering-knowledge and delegation guidance without duplicating AGENTS verbatim**

Describe the purpose and escalation path, and cross-reference `AGENTS.md` for operational agent behavior.

- [ ] **Step 9: Update the Guiding Rule**

Add questions equivalent to: `What is the robust parent?`, `Which search branches are active/unexplored?`, `How certain is the apparent improvement?`, and `What operational lesson should become a default?` while retaining the original reproducibility questions.

- [ ] **Step 10: Verify no conflicting legacy rules remain**

Search for stale statements that say project-level knowledge/current direction belongs only in `EXPERIMENT_SUMMARY.md`, or that current best is simply the highest standard-CV score for all downstream decisions. Rewrite or remove them.

- [ ] **Step 11: Commit Task 4**

Commit message: `docs: align experiment management spec with harness v2`

---

### Task 5: Update the user-facing README and repository map

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: finalized document structure and rules from Tasks 1-4.
- Produces: concise onboarding for humans starting a new competition from the template.

- [ ] **Step 1: Update `Project Structure`**

Add STATUS, ENGINEERING_NOTES, HARNESS_LESSONS, experiment_queue, status template, and experiment_job template. Do not list speculative future tooling.

- [ ] **Step 2: Update `Using This Template`**

After competition/data/CV setup, instruct the user to initialize STATUS/Search Map and engineering constraints relevant to the environment. Keep baseline creation and standard CV establishment as first modeling priorities.

- [ ] **Step 3: Replace the Experiment Summary explanation**

Explain STATUS as the quick current-state entry point and EXPERIMENT_SUMMARY as durable scientific knowledge. Add short sections for Engineering Notes and Experiment Queue without copying the full policy.

- [ ] **Step 4: Update Agent Usage read order**

Match `AGENTS.md`: STATUS before broad historical knowledge, selective summary/queue/engineering-note reads as needed.

- [ ] **Step 5: Add a concise evidence-stage explanation**

Introduce screening, confirmation, and robust-parent promotion in practical terms without expanding README into the normative specification.

- [ ] **Step 6: Verify README remains an onboarding document**

Remove duplicate policy prose when `AGENTS.md` or `experiment_management.md` is the better home. Ensure a new user can find every new document and understand why it exists.

- [ ] **Step 7: Commit Task 5**

Commit message: `docs: update template onboarding for harness v2`

---

### Task 6: Whole-branch consistency and regression verification

**Files:**
- Review: all files changed in Tasks 1-5
- No new product files unless a consistency fix is required.

**Interfaces:**
- Consumes: completed documentation refactor.
- Produces: a branch that satisfies the design acceptance criteria.

- [ ] **Step 1: Verify document responsibility uniqueness**

Search for the terms `Current Direction`, `Promising Ideas`, `current best`, `robust parent`, `EXPERIMENT_SUMMARY`, `STATUS.md`, `ENGINEERING_NOTES`, and `experiment_queue`. Confirm each current-state/planning concept has one canonical home and cross-references are consistent.

- [ ] **Step 2: Verify no hard-coded agent-model policy exists**

Search policy/docs for known model-name examples and generic phrases that mandate a particular worker model. Historical explanatory text in HARNESS_LESSONS may describe the failure mode without prescribing a model.

- [ ] **Step 3: Verify existing strong rules survived**

Confirm the final docs still explicitly preserve:
- immutable completed experiments;
- standard-CV comparability and caution with alternative CV;
- immutable raw data;
- OOF/provenance records;
- negative completed results;
- experiment/trial distinction;
- submission separation;
- lightweight Git artifact policy.

- [ ] **Step 4: Verify strategy rules are competition-agnostic**

Confirm there is no mandatory model-family list, exact exploration ratio, exact number of seeds, or universal significance threshold.

- [ ] **Step 5: Verify initial-state documents do not invent evidence**

Confirm STATUS, EXPERIMENT_SUMMARY, ENGINEERING_NOTES, and QUEUE do not claim experiments, benchmarks, current best models, resource measurements, or queue priorities that have not actually been produced in this template.

- [ ] **Step 6: Run repository tests if a local checkout is available**

Run: `uv run pytest -q`

Expected: existing tests pass unchanged because this revision modifies documentation only. If local execution is unavailable, record that limitation and verify no Python/config file changed in the branch.

- [ ] **Step 7: Compare the branch to `main`**

Expected changed files are limited to documentation/rule files plus the already-approved spec/plan. Unexpected source-code or dependency changes must be removed.

- [ ] **Step 8: Perform a fresh-reader acceptance check**

Using only `AGENTS.md`, `docs/STATUS.md`, and the repository map, verify a new human/agent can answer:
1. Where is the current robust parent recorded?
2. Where is the numerical experiment history?
3. Where are durable scientific findings?
4. Where are CPU/GPU/runtime lessons?
5. Where are future hypotheses?
6. When does an apparent improvement need confirmation?
7. What triggers a strategic exploration review?
8. Which changes require stronger implementation verification?

- [ ] **Step 9: Commit any consistency fixes**

Commit message: `docs: verify experiment harness v2 consistency`

- [ ] **Step 10: Open a pull request**

Target: `main`

PR title: `Improve experiment harness for human-agent search control`

PR body should summarize the new information architecture, strategy/confirmation rules, delegation safety, preserved v1 strengths, and note that no experiment-runner code or heavyweight dependencies were added.
