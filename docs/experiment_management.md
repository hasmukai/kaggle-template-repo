# 実験管理仕様

このドキュメントでは、本リポジトリにおける実験管理の詳細規約を定義する。

目的は、実験履歴を人間とコーディングエージェントの双方が理解できる状態に保ちつつ、**高速・再現可能・戦略的なexperiment cycle**を実現することである。

Public Leaderboardへのsubmissionは主要な評価手段としない。

基本cycle:

```text
STATUS / registry / durable knowledgeを確認
        ↓
strategic questionを選ぶ
        ↓
hypothesisを選択・作成
        ↓
logical parentとexperiment-vs-trialを決める
        ↓
最小限のconfig / 実装変更
        ↓
実装のriskに応じてverification
        ↓
screening experiment
        ↓
結果・uncertaintyを分析
        ↓
必要ならconfirmation
        ↓
robust parentをpromotionまたは維持
        ↓
適切なknowledge documentを更新
        ↓
Search Map / queueを再評価
```

---

# 1. 基本方針

## 再現性

Completed experimentについて、後から以下を確認できる状態を維持する。

- どのconfigを使用したか
- どのsource code stateを使用したか
- どのCV方式を使用したか
- どのようなprediction / metricが得られたか
- その結果をどのように解釈したか

再生成可能な大容量artifactは必ずしもGitで永続保存しない。

## 仮説駆動

各experimentでは原則として1つの明確なscientific questionまたはdiagnostic questionを検証する。

新しいexperimentでは少なくとも以下を明示する。

- `hypothesis`
- `parent_experiment`
- parentからの変更点
- 固定条件
- decision metric / diagnostic
- positive / negativeのどちらでも得られるinformation

複数要素のinteraction自体がhypothesisの場合を除き、無関係な変更を一度に混ぜない。

## ローカルCV中心

通常のmodel developmentでは標準Cross-Validationを主要評価とする。

CV設計自体を研究してよいが、互換性のないCV schemeのraw scoreを直接比較しない。

## 軽量記録

軽量なhistorical recordを優先して保存する。

- `config.yaml`
- `metrics.json`
- `metadata.json`
- `README.md`

大容量かつ再生成可能なartifactは必要に応じて保存し、通常Gitへcommitしない。

## Context loading

Defaultの読み取り順序:

```text
AGENTS.md
↓
docs/STATUS.md
↓
experiments/experiments.csv
↓
docs/EXPERIMENT_SUMMARY.md（durable findingが必要な場合）
↓
docs/experiment_queue/QUEUE.md（future work選定時）
↓
関連experiment / config / source
↓
docs/ENGINEERING_NOTES.md（runtime / resourceが関係する場合）
```

過去experimentを毎回すべて読む必要はない。

---

# 2. Experiment命名規則

形式:

```text
exp_NNN_short_description
```

例:

```text
exp_001_baseline
exp_012_add_group_features
exp_023_catboost_baseline
exp_031_test_alternative_cv
```

ルール:

- `NNN` はゼロ埋め連番
- `short_description` はlowercase snake_case
- IDを再利用しない
- completed experimentのIDはimmutable

Experiment IDはconfig filename、result directory、registry、`parent_experiment`、submission provenanceで共通して使用する。

---

# 3. Baseline / Parent / Robust Parent

## Baseline

初期基準は `exp_001_baseline` とする。

Baseline確定後、その意味を変更しない。実装上の問題が見つかった場合は新しいcorrective experimentを作る。

## Parent Experiment

新experimentは原則としてlogical parentを指定する。

```yaml
parent_experiment: exp_XXX_name
```

Parentは「直前に実行したexperiment」や「数値上の最高score」を機械的に選ばず、hypothesisに最も適した系譜を選ぶ。

## Robust Parent

`docs/STATUS.md` には、今後の標準的な土台として十分に信頼できるexperimentをRobust Parentとして記録する。

これはnumerical bestと一致しない場合がある。

---

# 4. ExperimentとTrial

## 新しいexperimentにする場合

意味のある別の問いを検証するときに新experimentを作る。

例:

- 新しいfeature family
- preprocessing方式変更
- model family変更
- target transformation変更
- CV設計変更
- ensemble導入
- data flowや欠損処理方針変更

## Trialにする場合

同じscientific questionの下で、小さな候補差を比較するときは同一experiment内のtrialとする。

例:

- `max_depth = 6 / 8 / 10`
- 多数のindividual feature screening
- feature pair screening
- 小さなmodel structure variation
- equivalent preprocessing variants

Registry rowは「候補値」ではなく「意味のある問い」の単位に保つ。

大規模hyperparameter optimizationは初期段階のdefaultにしない。

---

# 5. Experiment Config

Experiment definitionは `configs/` に自己完結したYAMLとして保存する。

```text
configs/exp_023_add_depth_feature.yaml
```

原則:

```text
1 experiment = 1 YAML
```

Config inheritanceを複雑化しすぎない。

推奨section:

```yaml
experiment:
  id: exp_023_add_depth_feature
  description: "..."
  hypothesis: "..."
  notes: "..."
  parent_experiment: exp_017_previous
  role: candidate

data: {}
preprocessing: {}
features: {}
cv: {}
model: {}
training: {}
trials: {}
```

必要に応じてCPU threads、device、determinism等のresource設定をconfigから確認可能にする。

---

# 6. Experiment Role

推奨値:

```text
baseline
candidate
cv_study
diagnostic
```

Roleは主に可読性・filtering用であり、systemが強く依存しすぎない。

---

# 7. Cross-Validation

## 標準CV

Project初期に標準CVを定義する。

最低限:

```text
method
number of folds
random seed（必要な場合）
grouping / stratification rules
```

通常experimentでは同じ標準CVを使用する。

可能ならseedだけでなくactual fold assignmentを保存する。

## Alternative CV

CV設計そのものをexperiment対象にしてよい。

- 必要に応じて `role: cv_study`
- 標準CVとの差を明記
- 何を検証するCVか説明
- standard-CV experimentとraw scoreを直接比較しない

Alternative CVを新しい標準へ採用する場合は、`docs/STATUS.md` のcurrent strategyを更新し、CVに関するdurable findingを `docs/EXPERIMENT_SUMMARY.md` に記録する。

過去scoreの意味を後から変更しない。

---

# 8. Experiment作成

想定interface:

```bash
uv run python scripts/new_experiment.py \
  --from exp_023_previous_experiment \
  --name add_new_feature
```

Scriptはparent configを基に新IDと`parent_experiment`を設定するが、hypothesisやdescriptionを勝手に決めない。

Source codeを自動変更しない。

---

# 9. Experiment実行

想定interface:

```bash
uv run python scripts/run_experiment.py \
  --config configs/exp_024_add_new_feature.yaml
```

Conceptual flow:

```text
config validation
↓
Git state capture
↓
data preparation
↓
preprocessing
↓
feature generation
↓
fold load / generation
↓
trial execution
↓
fold training
↓
validation prediction
↓
metrics
↓
OOF / artifacts
↓
metrics / metadata
↓
registry update
↓
experiment README
```

通常experimentは1commandで実行可能な状態を目標とする。

---

# 10. Immutable性

Completed experiment directoryはhistorical recordである。

禁止事項:

- 後のrunに合わせて保存済み`config.yaml`を書き換える
- 異なる結果で`metrics.json`を置き換える
- 同じIDを別条件で再利用する
- 別条件のOOFで既存artifactを上書きする

Meaningful changeは新experimentとして実行する。

Failed runで、科学的条件が変わっていない場合のみ同じIDで再実行してよい。

---

# 11. Result Directory

```text
experiments/<experiment_id>/
```

典型例:

```text
config.yaml
metrics.json
metadata.json
README.md
oof.parquet
log.txt
trials.csv
feature_importance.csv
git_diff.patch
```

Optional fileはexperimentに応じて省略可能。

---

# 12. config.yaml

Result directoryへ実際に実行したconfigの完全copyを保存する。

Training開始前までに保存し、experiment完了後はimmutableとする。

---

# 13. metrics.json

Machine-readableな評価結果を保存し、定性的考察は含めない。

最低限、primary metricについて可能なら以下を保持する。

```text
name
overall
mean
std
```

Fold-level score、best iteration、timing、secondary metric等は有用なものだけ追加する。

Timingは性能と計算コストのtrade-off評価に使える粒度で保存する。

---

# 14. Trial Results

複数trialがある場合は、必要に応じて `trials.csv` 等にtrial parameterとresultを保存する。

```text
trial_id,max_depth,num_leaves,cv_score,duration_sec
trial_001,6,31,0.7210,172.4
```

Best trialは `metrics.json` にも記録する。

各trialを一意に再現できるparameter情報を残す。

---

# 15. metadata.json

Execution provenanceを保存する。

例:

```json
{
  "experiment_id": "exp_024_add_new_feature",
  "status": "completed",
  "created_at": "...",
  "completed_at": "...",
  "duration_sec": 182.5,
  "git": {
    "commit": "abc1234",
    "dirty": true,
    "diff_saved": true
  },
  "environment": {
    "python_version": "3.x"
  }
}
```

Package versionを無条件に大量保存せず、dependency historyは可能な範囲で`uv.lock`から追跡する。

---

# 16. Git State / git_diff.patch

Dirty working treeでのexperimentを許容する。

開始時に:

```text
current Git commit
working tree dirty state
```

を保存する。

Dirtyの場合、関連diffを `experiments/<experiment_id>/git_diff.patch` に自動保存する。

概念的には:

```text
experiment code state = recorded commit + git_diff.patch
```

---

# 17. OOF Predictions

可能な限りOOF predictionを保存する。

推奨:

```text
oof.parquet
```

利用例:

- Error Analysis
- experiment comparison
- calibration
- ensemble
- fold diagnostics
- suspicious CV improvement investigation

元training rowとpredictionを対応付けられるschemaにする。

OOFは通常Gitへcommitしない。

---

# 18. Feature Importance / Diagnostics

意味のある場合のみfeature importanceやdiagnostic artifactを保存する。

例:

```text
feature_importance.csv
confusion matrix用data
group score
class metric
residual table
```

大量plotを自動生成するより、後から分析できるraw diagnostic dataを優先する。

---

# 19. Logs

`log.txt` はdebug / failed run調査に利用してよい。

重要情報をlogだけに閉じ込めない。

Systematic analysisに必要な情報は `metrics.json`、`metadata.json`、`README.md`、registryへ保存する。

---

# 20. Experiment README

Completed experimentには `README.md` を作る。

Template: `docs/templates/experiment_readme.md`

中心的な問い:

> このexperimentから何を学んだか？

記載内容:

- Hypothesis
- Changes
- Results
- Analysis
- Conclusion
- local Next

Conclusionは必要に応じて:

```text
Supported
Partially supported
Not supported
Inconclusive
```

さらに、robust parentを変更するのにconfirmationが必要か記載する。

Persistentなfuture hypothesisは `docs/experiment_queue/` へ移す。

---

# 21. experiments.csv

Registry:

```text
experiments/experiments.csv
```

1 experiment = 1 row。

初期推奨schema:

```text
experiment_id
parent_experiment
description
hypothesis
status
role
cv_scheme
cv_score
cv_std
model
num_trials
duration_sec
git_commit
git_dirty
created_at
```

用途:

- filtering
- sorting
- experiment comparison
- agent context
- relevant experiment search

Fold detail等は `metrics.json` へ置く。

---

# 22. Status

推奨:

```text
planned
running
completed
failed
```

Performanceが悪化した正常runは`completed`であり`failed`ではない。

---

# 23. Numerical Best / Screening / Confirmation / Promotion

## Numerical Best

標準CVを使ったcompleted experimentのnumerical rankingはregistryから計算する。

```text
status == completed
AND
cv_scheme == standard
```

Metric directionは明示定義し、metric名から推測しない。

Numerical historyのsource of truthはregistryであり、project-level documentに別の手動tableを維持しない。

## Screening

Screeningは、次に調べる価値があるか判断するための最小限の評価。

Small gainがobserved variation内にありうる場合、screeningだけでRobust Parentを置き換えない。

## Confirmation

Decision riskに応じ、より強いevidenceを取る。

典型trigger:

- robust parentを置き換える
- gainがvalidation variationに対して小さい
- fold / seed挙動が不安定
- resource増加が大きい
- strategy変更に使う

Repeated seed、repeated fold、alternate diagnostics等からcompetitionに合う方法を選ぶ。Universal seed countは定めない。

## Promotion

Promotionはproject decisionであり、単なる`argmax(cv_score)`ではない。

現在のRobust ParentとApparent Best / Unconfirmed Bestは `docs/STATUS.md` に記録する。

---

# 24. Processed Data

`data/processed/` はraw data + source code + configurationから再生成可能にする。

Manual undocumented operationへ依存しない。

主要datasetは `data/processed/README.md` にsource、purpose、generation method、transformations、caveatsを記載する。

---

# 25. Cache

`data/cache/` はperformance目的の一時data。

```text
cacheを削除してもexperimentの意味が変わらない
```

ことを満たす。

Config依存cacheは可能な範囲でidentityに関連configを反映する。

---

# 26. Preprocessing / Feature Generation

Formal experimentに必要な処理はexperiment commandから実行可能にする。

避ける:

```text
Notebook手動実行
→ CSV手動保存
→ experiment
```

推奨:

```text
run_experiment.py
→ preprocessing
→ feature generation
→ model training
```

---

# 27. Notebooks

Notebookはexperiment definitionではない。

用途:

- EDA
- visualization
- OOF analysis
- CV analysis
- Error Analysis
- small exploratory work

Formal experimentに必要なlogicは `src/` へ移す。

---

# 28. Submission Generation

Submission生成はCV experimentから分離する。

```bash
uv run python scripts/make_submission.py \
  --experiment exp_024_add_new_feature
```

保存済みexperiment configとcode stateから必要なfull trainingを再現する。

普通のCV experimentで不要なfull-data trainingを行わない。

---

# 29. Submission Tracking

Submissionは元experimentを追跡可能にする。

Public scoreはlocal CVの代替となる主要model selection基準にしない。

重要なexternal evaluationから一般化可能な知見が得られた場合のみ、`docs/EXPERIMENT_SUMMARY.md` のCV / caveat findingとしてまとめる。単なるsubmission履歴は別途submission provenanceに置く。

---

# 30. Model Checkpoint

Defaultでは全experimentのmodel checkpointを保存しない。

優先artifact:

```text
config
metrics
metadata
OOF
analysis
```

Checkpointを保存するのはtraining costが非常に高い、正確な再学習が難しい、downstreamでmodel自体が必要など明確な理由がある場合。

---

# 31. Git Tracking Policy

Gitの目的:

```text
version control
backup
historical archive
reproducibility
```

Gitで管理する軽量情報:

```text
AGENTS.md
README.md
pyproject.toml
uv.lock
configs/
src/
scripts/
tests/
docs/
experiments/experiments.csv
experiment README/config/metrics/metadata
small git_diff.patch
```

通常Gitで管理しないもの:

```text
data/raw/
generated processed data
data/cache/
large OOF
model checkpoints
large logs
generated submission CSV
```

---

# 32. Testing / Task Risk

Experiment resultの信頼性を損なう処理を重点testする。

優先対象:

```text
preprocessing invariants
CV splitting
metric calculation
submission format
data join
data leakage prevention
OOF construction
row alignment
```

Riskに応じたquality gateは `AGENTS.md` を参照する。

特にCV、target-dependent preprocessing、leakage-sensitive join、metric、calibration、OOF、submission alignmentはhigh-riskとみなし、worker reportだけで正しいと判断しない。

Trainingが完走したことはvalidation logicの正しさの証明ではない。

---

# 33. Failed Experiment

Execution failureは可能な範囲で以下を残す。

```text
status
error message
log
config
metadata
Git state
```

正常完了したnegative resultとexecution failureを区別する。

---

# 34. Project-level Knowledge Routing

Project-level情報を1つのsummaryへ集約しない。

## `docs/STATUS.md`

更新する場合:

- Robust Parentが変わった
- Apparent Best / Unconfirmed Bestが生じた・解消した
- Search Mapのbranch stateが変わった
- Open Strategic Questionが変わった
- Next Candidatesが変わった
- current executionに影響するresource noteが変わった

## `docs/EXPERIMENT_SUMMARY.md`

更新する場合:

- 複数decisionに再利用できるdurable scientific findingが得られた
- robust positive / negative findingが確立した
- CV / data / model / featureに関する一般化可能な知見が増えた
- interaction / caveatが重要になった

Experiment changelogにしない。

## `docs/ENGINEERING_NOTES.md`

更新する場合:

- parallelism、GPU、cache、determinism、memory、library behavior等で再利用可能な運用知識を得た

十分に一般的で安全なら、documentへ書くだけでなくcode/config defaultも改善する。

## `docs/HARNESS_LESSONS.md`

更新する場合:

- experiment loop自体に再利用可能な成功・失敗patternが見つかった

Competition modeling ruleの置き場にしない。

## `docs/experiment_queue/`

Future hypothesisのbacklog。Experiment historyではない。

意味のある結果の後は優先順位とSearch Mapとの整合を再評価する。

---

# 35. Agent Autonomous Experiment Cycle

## Step 1: Current stateを理解する

読む:

```text
AGENTS.md
docs/STATUS.md
experiments/experiments.csv
```

必要に応じてdurable summary、queue、engineering notesを追加で読む。

把握する:

- baseline
- Robust Parent
- Apparent Best / Unconfirmed Best
- relevant experiments
- active / unexplored / stalled search branches
- open strategic questions

## Step 2: Strategic questionを選ぶ

Near-neighbor improvementを自動的に次の仕事としない。

同一lineageが続く、gainがuncertaintyより小さい、parameter tweakに偏る、queueが一branchへ偏る、重要branchが理由なくunexploredの場合はstrategic reviewを行う。

## Step 3: Evidenceを選ぶ

必要なexperimentだけ詳細に読む。

優先:

```text
README.md
metrics.json
config.yaml
OOF / diagnostics（必要時）
```

## Step 4: Hypothesis / Queue Jobを選ぶ

Queueから選ぶか、新しく明確なhypothesisを1つ立てる。

## Step 5: ParentとExperiment-vs-Trialを決める

Logical parentを選び、homogeneous comparisonならtrialsを使う。

## Step 6: Implement / Verify

必要最小限の変更を行い、task riskに応じてtest、smoke test、diff reviewを実施する。

## Step 7: Screening

標準experiment commandでscreeningを実行する。

## Step 8: Analyze

比較対象:

- parent
- baseline
- numerical best
- Robust Parent
- observed validation variation

Hypothesis conclusion:

```text
Supported
Partially supported
Not supported
Inconclusive
```

## Step 9: Confirmation判断

Promotionがfragile resultに依存する場合、適切なconfirmationを実施する。

## Step 10: Record / Route Knowledge

- experiment README
- metrics / metadata / registry
- durable finding → EXPERIMENT_SUMMARY
- engineering lesson → ENGINEERING_NOTES
- strategy change → STATUS
- persistent future hypothesis → queue

## Step 11: Re-evaluate Search Map / Queue

次experimentを決める前に、active branchとqueue priorityを再評価する。

大量のspeculative experimentをanalysisなしに一括実行しない。

---

# 36. 初期実装Scope

初期systemはシンプルに保つ。

必要なもの:

```text
self-contained YAML
Experiment ID / parent tracking
1-command CV
standard CV
preprocessing / feature generation
metrics / metadata
OOF
registry
experiment README
Git provenance
git diff
processed data docs
lightweight tests
STATUS / durable summary / engineering notes / queue
```

必要性が明確になるまで追加しない:

```text
Optuna integration
complex config inheritance
experiment dashboard
MLflow
Weights & Biases
automatic report generation
complex cache graph
distributed experimentation
```

---

# 37. Source of Truth

## Experiment Definition

`experiments/<experiment_id>/config.yaml`

## Numerical Result

`experiments/<experiment_id>/metrics.json`

## Execution Provenance

`experiments/<experiment_id>/metadata.json`

## Experiment Interpretation

`experiments/<experiment_id>/README.md`

## Experiment Index / Numerical History

`experiments/experiments.csv`

## Current Navigation / Strategic State

`docs/STATUS.md`

## Durable Scientific Knowledge

`docs/EXPERIMENT_SUMMARY.md`

## Engineering / Operational Knowledge

`docs/ENGINEERING_NOTES.md`

## Harness Meta-Knowledge

`docs/HARNESS_LESSONS.md`

## Future Hypothesis Backlog

`docs/experiment_queue/`

Project-level documentとimmutable experiment recordが矛盾する場合、experiment recordを確認し、staleなproject-level documentを修正する。

---

# 38. Guiding Rule

Experiment management systemによって、少なくとも以下へ簡単に答えられる状態を維持する。

> 何を試したか？

> なぜ試したか？

> 何を変更したか？

> どのcode/configから結果が生成されたか？

> どのように評価したか？

> numerical bestは何か？

> Robust Parentは何か？ それがnumerical bestと違うならなぜか？

> 観測された改善はvalidation uncertaintyに対してどの程度確かか？

> どのSearch Branchがactive / unexplored / stalledなのか？

> 何を学んだか？

> 次に検証する価値が高い問いは何か？

> どのengineering lessonをdefaultへ昇格させるべきか？

これらの問いへの回答が難しくなった場合、管理systemを複雑化するのではなく、まず責務・document・experiment granularityを見直す。
