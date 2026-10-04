# Kaggle / Competition Experiment Template

Kaggleを含むデータサイエンスコンペティション向けの、再利用可能なローカル開発・実験templateです。

このtemplateは、**ローカルCross-Validationを中心に再現可能な実験を高速に回すこと**と、**人間とagentが探索戦略を共同で把握できること**を重視します。

Public Leaderboardへのsubmissionは主要なfeedback loopにしません。

## Using This Template

新しいcompetitionで利用するときは、最初に以下を行います。

1. READMEのタイトルとcompetition概要を対象competitionに合わせる
2. 配布dataを変更せず `data/raw/` に配置する
3. data structure、評価指標、標準CVを確認する
4. `docs/STATUS.md` にGoalと初期Search Mapを記載する
5. CPU / GPU / memory / deterministic requirement等の重要な環境制約があれば `docs/ENGINEERING_NOTES.md` に記録する
6. 最小限のbaseline pipelineを実装する
7. `uv run python scripts/new_experiment.py --name baseline` で最初のconfigを作る
8. `exp_001_baseline` を実行し、以後の比較基準を確立する

Competition固有処理は、確認した仕様に基づいて `src/` とexperiment configへ実装してください。

---

## Core Experiment Loop

```text
STATUS / registryを確認
↓
strategic questionを選ぶ
↓
hypothesisを立てる
↓
logical parentとexperiment-vs-trialを決める
↓
最小限の変更を実装・検証
↓
screening CV
↓
結果とuncertaintyを分析
↓
必要ならconfirmation
↓
robust parentをpromotionまたは維持
↓
適切なknowledge documentを更新
↓
Search Map / queueを再評価
```

小さなscore改善を毎回そのまま次のparentへ昇格させるのではなく、observed CV variationやfold/seed behaviorも考慮します。

---

## Project Structure

```text
.
├── README.md
├── AGENTS.md
├── .gitignore
├── pyproject.toml
├── uv.lock
│
├── configs/
│   └── ...
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   └── README.md
│   └── cache/
│
├── docs/
│   ├── STATUS.md
│   ├── EXPERIMENT_SUMMARY.md
│   ├── ENGINEERING_NOTES.md
│   ├── HARNESS_LESSONS.md
│   ├── experiment_management.md
│   ├── experiment_queue/
│   │   ├── README.md
│   │   └── QUEUE.md
│   └── templates/
│       ├── experiment_readme.md
│       ├── experiment_summary.md
│       ├── status.md
│       └── experiment_job.md
│
├── experiments/
│   ├── experiments.csv
│   └── ...
│
├── notebooks/
│
├── scripts/
│   ├── new_experiment.py
│   ├── run_experiment.py
│   └── make_submission.py
│
├── src/
│   ├── preprocessing/
│   ├── features/
│   ├── models/
│   ├── cv/
│   ├── metrics/
│   └── utils/
│
├── submissions/
└── tests/
```

詳細なrulesは `AGENTS.md` と `docs/experiment_management.md` を参照してください。

---

## Project-Level Documents

### `docs/STATUS.md`

現在地を短時間で理解するためのhuman control planeです。

主に以下を置きます。

- Goal
- Robust Parent
- Apparent Best / Unconfirmed Best
- Search Map
- High-confidence Findings
- Dead Ends / Deprioritized Directions
- Open Strategic Questions
- Next Candidates
- concise Resource Notes

Experiment historyや長期的な知識archiveにはしません。

### `docs/EXPERIMENT_SUMMARY.md`

複数の意思決定に再利用できるdurable scientific knowledgeをまとめます。

例:

- CV findings
- data findings
- model findings
- feature findings
- robust positive / negative findings
- interactions / caveats

Current directionやactive backlogはここへ置きません。

### `docs/ENGINEERING_NOTES.md`

実験の速度・安定性・再現性に関する再利用可能な運用知識を置きます。

例:

- CPU parallelism
- GPU settings
- memory constraints
- deterministic behavior
- cache behavior
- library-specific pitfalls

安全で一般化可能なrecommendationは、documentへ残すだけでなくcode/config defaultへ反映することを優先します。

### `docs/HARNESS_LESSONS.md`

Experiment harness自体から得たmeta-level lessonを記録します。

Competition固有のmodeling findingではなく、「実験ループをどう設計すると良いか」の知見を蓄積します。

### `docs/experiment_queue/`

将来検証したいhypothesisのbacklogです。

Queueは自動実行listではありません。意味のある結果の後はpriorityを再評価します。

人間もagentもjobを追加できます。Jobにexperiment IDを事前予約せず、実際に実行すると決めた時点で採番します。

---

## Environment

Python環境とdependency管理には `uv` を使用します。

```bash
uv sync
```

基本的に仮想環境を手動activateせず `uv run` 経由で実行します。

例:

```bash
uv run python --version
```

Dependency追加:

```bash
uv add <package>
```

Development dependency:

```bash
uv add --dev <package>
```

---

## Data

```text
data/
├── raw/
├── processed/
└── cache/
```

### `data/raw/`

Competitionから配布されたoriginal dataを保存します。原則immutableです。

### `data/processed/`

再生成可能なprocessed dataを保存します。

内容と生成方法を `data/processed/README.md` に記録し、raw data・source code・configから再生成できる状態を維持します。

### `data/cache/`

Speed-up用の一時cacheです。削除してもexperiment semanticsが変わらないことを前提とします。

---

## Experiment Configuration

各experimentは `configs/` 以下の自己完結したYAMLとして定義します。

```text
configs/exp_001_baseline.yaml
configs/exp_002_add_xxx.yaml
```

命名:

```text
exp_NNN_short_description
```

原則:

```text
1 experiment = 1 YAML
```

Configには必要に応じて以下を含めます。

- experiment ID
- description
- hypothesis
- notes
- parent experiment
- data
- preprocessing
- features
- CV
- model
- training
- trials
- resource/device settings

詳細schemaは `docs/experiment_management.md` を参照してください。

---

## Creating a New Experiment

想定例:

```bash
uv run python scripts/new_experiment.py \
  --from exp_023_add_depth_feature \
  --name add_geology_feature
```

新experimentでは、少なくとも以下を明確にします。

- 何を検証するか
- なぜ検証する価値があるか
- logical parentはどれか
- parentから何を変更するか
- 何を固定するか
- どのmetric / diagnosticで判断するか

Current robust parentから必ず派生する必要はありません。

---

## Experiments and Trials

意味のあるscientific questionの違いは別experimentとして管理します。

同じ問いの中での小さな候補差はtrialとして扱います。

例:

```text
max_depth = 6
max_depth = 8
max_depth = 10
```

は通常1experiment + 3 trialsです。

同様に、多数のindividual feature screening、feature pair比較、小さなpreprocessing variationなども、問いが同じならtrialへまとめます。

Registryを「候補値の一覧」にしないことが重要です。

---

## Running an Experiment

想定command:

```bash
uv run python scripts/run_experiment.py \
  --config configs/exp_024_add_geology_feature.yaml
```

Experimentは概念的に:

```text
preprocessing
↓
feature generation
↓
Cross-Validation
↓
evaluation
↓
result persistence
```

まで1commandで実行することを目標とします。

通常experimentでは標準CVを使用します。CV studyで別schemeを使う場合はstandard-CV scoreと直接比較しません。

---

## Screening, Confirmation, Promotion

### Screening

次に詳しく調べる価値があるか判断するための安価な評価です。

### Confirmation

Robust Parentの置き換え、small gain、fold/seed instability、大きなresource increase、strategy changeなど、判断リスクが高い場合により強いevidenceを取ります。

Confirmation方法はcompetitionに合わせます。Fixed seed countやuniversal thresholdは設けません。

### Promotion

新しいexperimentをRobust Parentまたはproject-level strategyへ昇格させる判断です。

これは単純な `argmax(cv_score)` ではありません。

Numerical historyはregistryにあり、現在のRobust Parentは `docs/STATUS.md` に記録します。

---

## Experiment Results

Result directory:

```text
experiments/<experiment_id>/
```

例:

```text
config.yaml
metrics.json
metadata.json
oof.parquet
log.txt
README.md
git_diff.patch
```

### `config.yaml`

実際に実行したconfigのcopy。Completed後はimmutableです。

### `metrics.json`

Machine-readableなevaluation result。Qualitative analysisは入れません。

### `metadata.json`

Execution provenance。Git commit / dirty state、timestamp、runtime等を保存します。

### `oof.parquet`

Error analysis、experiment comparison、ensemble、validation diagnostics等に利用します。通常Gitへcommitしません。

### `README.md`

Hypothesis、changes、results、analysis、conclusion、confirmationの必要性、local next questionsを記録します。

---

## Experiment Registry

全experimentのcompact indexは:

```text
experiments/experiments.csv
```

で管理します。

主なfields:

- experiment ID
- parent experiment
- description
- hypothesis
- status
- role
- CV scheme
- CV score / std
- model
- number of trials
- duration
- Git state
- created time

詳細なfold resultは `metrics.json`、解釈はexperiment READMEを参照します。

---

## Search Map and Strategic Review

`docs/STATUS.md` のSearch Mapで、探索branchの状態を明示します。

Branchはcompetition固有に定義して構いません。

Near-neighbor experimentを続ける前にstrategic reviewを行う目安:

- same lineageのlocal changesが連続
- recent gainがvalidation uncertaintyより小さい
- hypothesisよりparameter tweakが中心
- queueが1branchへ偏る
- important branchが理由なくunexplored

Reviewの結論は「別modelを試す」に限定しません。Diagnostics、data hypothesis、representation、interaction、またはcontinued exploitationでも構いません。

---

## Notebooks

`notebooks/` は主に:

- EDA
- visualization
- CV analysis
- Error Analysis
- exploratory investigation

に使用します。

正式experimentに必要なlogicはNotebookだけに残さず `src/` へ移します。

---

## Submission

Submission generationはordinary CV experimentから分離します。

```bash
uv run python scripts/make_submission.py \
  --experiment exp_024_add_geology_feature
```

Public LBをprimary experiment-feedback mechanismにしません。

Submissionは元experimentへtraceできる状態にします。

---

## Git Policy

Gitはversion control、backup、historical archive、reproducibilityのために使います。

Gitに保存する軽量情報:

- source
- configs
- scripts
- tests
- docs
- experiment README
- metrics / metadata
- registry

通常保存しないgenerated heavy data:

- raw competition data
- processed datasets
- cache
- large OOF
- model checkpoint
- large logs
- generated submissions

Dirty working treeでexperimentした場合はGit commitとdirty stateを記録し、relevant diffをexperiment directoryへ保存します。

---

## Testing and Agent Usage

Agentはまず `AGENTS.md` を参照してください。

Default context order:

```text
AGENTS.md
↓
docs/STATUS.md
↓
experiments/experiments.csv
↓
必要に応じて EXPERIMENT_SUMMARY / queue / ENGINEERING_NOTES
↓
関連experiment / config / source
```

Implementation taskは、間違えたときのcostに応じてverification levelを変えます。

特にCV splitting、target-dependent preprocessing、leakage-sensitive join、metric、calibration、OOF construction、submission alignmentはhigh-riskです。

Workerの完了報告だけでexperiment correctnessを判断せず、tests、diff、executed config、metrics等のauthoritative artifactを確認します。

---

## Further Details

Normativeな詳細仕様:

```text
docs/experiment_management.md
```

Harness designのretrospective:

```text
docs/HARNESS_LESSONS.md
```

このtemplateでは、必要性が明確になるまでMLflow、Weights & Biases、distributed experimentation、complex config inheritance等を導入しません。
