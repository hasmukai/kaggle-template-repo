# 実験管理仕様

このドキュメントでは、本リポジトリにおける実験管理の規約を定義する。

目的は、実験履歴を人間とコーディングエージェントの双方が容易に理解できる状態を保ちながら、**高速かつ再現可能な実験サイクル**を実現することである。

基本的な開発サイクルは以下とする。

```text
過去の実験を確認
        ↓
仮説を立てる
        ↓
新しいexperimentを作成
        ↓
config / 実装を変更
        ↓
前処理・特徴量生成
        ↓
ローカルCVで評価
        ↓
結果を保存
        ↓
結果を分析
        ↓
得られた知見を更新
        ↓
次のexperimentを決める
```

Public Leaderboardへのsubmissionは、主要な評価手段とはしない。

---

# 1. 基本方針

## 再現性

完了したexperimentについて、後から以下を確認できる状態を維持する。

* どのconfigを使用したか
* どのソースコードの状態を使用したか
* どのCV方式を使用したか
* どのような予測・評価結果が得られたか
* その結果をどのように解釈したか

再生成可能な大容量artifactは、必ずしも永続保存する必要はない。

## 仮説駆動の実験

各experimentでは、原則として1つの明確な問いを検証する。

新しいexperimentには原則として以下を設定する。

* `hypothesis`
* `parent_experiment`
* 親experimentからの明確な変更点
* 評価基準

複数の無関係な変更を一度に加えることは避ける。

複数要素の相互作用そのものを検証する場合は、この限りではない。

## ローカルCVを中心にする

モデル開発では、ローカルCross-Validationを主要な評価手段とする。

通常のexperimentでは標準CVを使用し、experiment間のスコアを比較可能にする。

CV方式そのものを検証するexperimentを行ってもよいが、互換性のないCV方式から得られたスコアを直接比較しない。

## 軽量な実験記録

以下のような軽量ファイルは保存する。

* `config.yaml`
* `metrics.json`
* `metadata.json`
* `README.md`

以下のような大容量かつ再生成可能なartifactは、Gitで永続管理する必要はない。

* processed data
* model checkpoint
* 大容量log
* OOF prediction

## エージェントからの読みやすさ

エージェントがリポジトリ全体を毎回調査しなくても現在の状態を把握できるようにする。

基本的な読み取り順序は以下とする。

```text
AGENTS.md
↓
docs/EXPERIMENT_SUMMARY.md
↓
experiments/experiments.csv
↓
関連するexperiment directory
↓
関連するconfig
↓
関連するsource code
```

---

# 2. Experimentの命名規則

Experiment IDは以下の形式とする。

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

* `NNN` はゼロ埋めした連番とする
* `short_description` は主要な変更内容を簡潔に表す
* lowercase snake_caseを使用する
* Experiment IDを再利用しない
* 完了済みexperimentのIDはimmutableとする

Experiment IDは以下で共通して使用する。

* config filename
* experiment directory
* experiment registry
* `parent_experiment`
* submissionとの紐付け

---

# 3. BaselineとParent Experiment

## Baseline

初期基準experimentは以下とする。

```text
exp_001_baseline
```

baseline確定後、その意味を変更しない。

後からbaseline実装に問題が見つかった場合も、過去のexperimentを上書きしてはならない。

修正版を新しいexperimentとして作成する。

## Parent Experiment

新しいexperimentでは原則として以下を指定する。

```yaml
parent_experiment: exp_XXX_name
```

`parent_experiment`には、新しいexperimentが論理的に派生したexperimentを指定する。

単純に直前に実行されたexperimentを指定してはならない。

例:

```text
exp_010_add_feature_a
        ↓
exp_015_add_feature_b_on_top_of_a
        ↓
exp_021_change_model_with_features_a_b
```

これによりexperimentの系譜を追跡可能にする。

---

# 4. ExperimentとTrialの使い分け

すべてのパラメータ変更について新しいexperimentを作成する必要はない。

## 新しいexperimentを作る場合

意味のある別の仮説を検証するときに新しいexperimentを作る。

例:

* 新しい特徴量群を追加する
* 前処理方法を変更する
* モデル系統を変更する
* target transformationを変更する
* CV設計を変更する
* ensembleを導入する
* 欠損値の処理方法を変更する

## 同一experiment内のtrialとする場合

同じ仮説について、小さなパラメータ差を比較するときはtrialを使用する。

例:

```yaml
trials:
  max_depth:
    - 6
    - 8
    - 10
```

この場合、3つのexperimentではなく、1つのexperiment内の3 trialとして扱う。

別の例:

```yaml
trials:
  learning_rate:
    - 0.03
    - 0.05
  num_leaves:
    - 31
```

初期段階ではtrial数を少なく保つ。

大規模なhyperparameter optimizationは初期段階では行わない。

Optunaなどは、モデル構造・特徴量・validation・主要なモデリング方針がある程度固まってから導入を検討する。

---

# 5. Experiment Config

Experimentの定義は以下に保存する。

```text
configs/
```

各experimentについて、自己完結したYAMLファイルを1つ使用する。

例:

```text
configs/exp_023_add_depth_feature.yaml
```

原則:

```text
1 experiment = 1 YAML
```

複数ファイルにまたがる複雑なconfig継承は避ける。

1つのファイルを読むだけでexperimentの内容を理解できるのであれば、ある程度の重複は許容する。

## 推奨schema

```yaml
experiment:
  id: exp_023_add_depth_feature
  description: "depth由来特徴量を追加"
  hypothesis: >
    depth由来特徴量を追加することで、
    データの構造をより適切に表現でき、
    CV性能が改善すると予想する。
  notes: >
    exp_017をベースとし、特徴量のみ変更する。
  parent_experiment: exp_017_previous_best
  role: candidate

data:
  # dataset configuration

preprocessing:
  # preprocessing configuration

features:
  # feature configuration

cv:
  # CV configuration

model:
  name: lightgbm
  params:
    # model parameters

training:
  # training settings

trials:
  # optional
```

特定のexperimentで不要なsectionは省略してよい。

Configには「どのような動作を行うか」を記述し、実装詳細そのものはsource code側に置く。

---

# 6. Experiment Role

必要に応じて`role`を設定する。

推奨値:

```text
baseline
candidate
cv_study
diagnostic
```

## `baseline`

固定baseline。

## `candidate`

通常の性能改善experiment。

## `cv_study`

validation方法そのものを調査するexperiment。

## `diagnostic`

直接的な性能改善よりも、モデルやデータの挙動理解を目的とするexperiment。

`role`は主に可読性・filteringのための情報であり、実験管理システムが強く依存する設計にはしない。

---

# 7. Cross-Validation

ローカルCVを主要な評価手段とする。

## 標準CV

プロジェクト初期に標準CV方式を決定する。

通常のexperimentでは原則として同じ標準CVを使用する。

これにより、スコア差がvalidation splitではなくexperimentの変更によるものである可能性を高める。

標準CVでは少なくとも以下を定義する。

```text
method
number of folds
random seed（必要な場合）
grouping / stratification rules
```

可能であれば、seedだけでなく実際のfold assignmentも保存する。

例:

```text
data/processed/folds.parquet
```

保存場所や形式はcompetitionのデータ構造に応じて変更してよい。

## Alternative CV

CV設計自体をexperimentの対象としてよい。

その場合:

* 必要に応じて`role: cv_study`とする
* 標準CVとの違いを明記する
* 何を検証するためのCVなのかを説明する
* 標準CVのexperimentとraw scoreを直接比較しない

Alternative CVを新しい標準CVとして採用する場合、その判断を`EXPERIMENT_SUMMARY.md`に明示する。

過去のscoreの意味を後から変更してはならない。

---

# 8. Experimentの作成

新しいexperimentは原則として既存experimentから作成する。

想定interface:

```bash
uv run python scripts/new_experiment.py \
  --from exp_023_previous_experiment \
  --name add_new_feature
```

Scriptは以下を行う。

1. parent experiment/configを特定する
2. 次のexperiment番号を決定する
3. parent configをコピーする
4. 新しいExperiment IDを設定する
5. `parent_experiment`を設定する
6. descriptionなどを新しいexperiment用に更新可能な状態にする
7. ユーザーまたはエージェントが新しいhypothesisと変更内容を記述する

生成例:

```text
configs/exp_024_add_new_feature.yaml
```

このscriptがsource codeを勝手に変更してはならない。

---

# 9. Experimentの実行

想定interface:

```bash
uv run python scripts/run_experiment.py \
  --config configs/exp_024_add_new_feature.yaml
```

Experiment pipelineは必要な処理を自動実行する。

概念的な処理フロー:

```text
config読み込み
↓
experiment definition検証
↓
Git状態取得
↓
データ準備
↓
前処理
↓
特徴量生成
↓
CV fold読み込み / 生成
↓
trial実行（定義されている場合）
↓
各foldで学習
↓
validation prediction生成
↓
metrics計算
↓
OOF prediction保存
↓
metrics / metadata保存
↓
experiment registry更新
↓
experiment README準備
```

内部architectureは必要に応じて変更してよいが、通常のexperimentは1コマンドで実行可能な状態を維持する。

---

# 10. ExperimentのImmutable性

completed experimentのresult directoryは過去の実行状態を表す。

以下を行ってはならない。

* 後の実行内容に合わせて`config.yaml`を書き換える
* 異なる結果で`metrics.json`を置き換える
* 同じExperiment IDを別のコードで再利用する
* 別条件のOOF predictionで既存ファイルを上書きする

意味のある変更を行う場合は、新しいexperimentを作る。

## Failed run

有効なcompleted resultが一度も生成されておらず、experiment definitionも変更されていない場合は、同じExperiment IDで再実行してよい。

Debug中に科学的な結果へ影響する変更を加えた場合は、新しいExperiment IDを作ることを優先する。

---

# 11. Experiment Result Directory

Experiment resultは以下に保存する。

```text
experiments/<experiment_id>/
```

例:

```text
experiments/
└── exp_024_add_new_feature/
    ├── config.yaml
    ├── metrics.json
    ├── metadata.json
    ├── README.md
    ├── oof.parquet
    ├── log.txt
    ├── trials.csv
    ├── feature_importance.csv
    └── git_diff.patch
```

すべてのexperimentにすべてのoptional fileが必要なわけではない。

---

# 12. config.yaml

Experiment result directoryには、実際に実行したconfigの完全なコピーを保存する。

```text
experiments/exp_024_add_new_feature/config.yaml
```

Training開始前までに保存する。

Experiment完了後、このファイルはimmutableとして扱う。

`configs/`側のファイルが将来変更されたとしても、このコピーによって実際に何を実行したのかを確認できるようにする。

---

# 13. metrics.json

`metrics.json`には構造化された評価結果を保存する。

定性的な考察は含めない。

推奨構造:

```json
{
  "primary_metric": {
    "name": "macro_f1",
    "overall": 0.7241,
    "mean": 0.7238,
    "std": 0.0062
  },

  "folds": [
    {
      "fold": 0,
      "score": 0.7184,
      "best_iteration": 842,
      "train_time_sec": 31.4
    },
    {
      "fold": 1,
      "score": 0.7295,
      "best_iteration": 917,
      "train_time_sec": 29.8
    }
  ],

  "secondary_metrics": {
    "accuracy": 0.812,
    "precision_macro": 0.731,
    "recall_macro": 0.719
  },

  "timing": {
    "total_sec": 182.5,
    "preprocessing_sec": 12.8,
    "training_sec": 154.2,
    "prediction_sec": 4.1
  }
}
```

実際に使用するmetricはcompetitionに応じて変更する。

## Primary Metric

最低限以下を保存する。

```text
name
overall
mean
std
```

Competition metricがfold mean/stdに自然に分解できない場合は適宜変更する。

## Fold Results

各foldについて必要に応じて以下を保存する。

```text
fold
score
best_iteration
train_time_sec
```

有用なmodel固有情報がある場合は追加してよい。

## Secondary Metrics

モデルの挙動理解に役立つmetricのみ保存する。

ライブラリから計算できるmetricを無条件ですべて保存する必要はない。

## Timing

必要に応じて以下を保存する。

```text
total_sec
preprocessing_sec
feature_generation_sec
training_sec
prediction_sec
```

これにより、性能改善と計算コストのtrade-offを評価できるようにする。

---

# 14. Trial Results

複数trialを実行した場合、その結果を保存する。

小規模trialでは以下を使用してよい。

```text
trials.csv
```

例:

```text
trial_id,max_depth,num_leaves,cv_score,duration_sec
trial_001,6,31,0.7210,172.4
trial_002,8,31,0.7241,181.7
trial_003,10,31,0.7228,196.2
```

選択されたbest trialは`metrics.json`にも記録する。

例:

```json
{
  "best_trial": "trial_002"
}
```

Trial configurationが複雑な場合も、各trialを一意に識別し再現できるだけのparameter情報を保存する。

---

# 15. metadata.json

`metadata.json`にはexperimentの実行来歴を保存する。

推奨項目:

```json
{
  "experiment_id": "exp_024_add_new_feature",
  "status": "completed",
  "created_at": "2026-08-08T17:00:00+09:00",
  "completed_at": "2026-08-08T17:03:02+09:00",
  "duration_sec": 182.5,

  "git": {
    "commit": "abc1234",
    "dirty": true,
    "diff_saved": true
  },

  "environment": {
    "python_version": "3.11.x"
  }
}
```

再現性に重要であれば追加のenvironment情報を保存してよい。

ただし、毎回数百個のpackage versionを保存するような仕組みは原則不要とする。

Dependency historyの多くは`uv.lock`から追跡できる。

---

# 16. Git Stateとgit_diff.patch

未commitの変更が存在する状態でもexperimentを実行してよい。

高速な試行錯誤のため、experimentごとのcommitを必須にはしない。

Experiment開始時に自動的に以下を記録する。

```text
current Git commit
working treeがdirtyかどうか
```

Working treeがdirtyの場合、関連するdiffを以下に保存する。

```text
experiments/<experiment_id>/git_diff.patch
```

概念的には、

```text
experiment実行時のcode state
=
recorded Git commit
+
git_diff.patch
```

となる。

この処理はexperiment runnerが自動的に行う。

ユーザーやエージェントが手動でdiffをコピーする必要はない。

---

# 17. OOF Predictions

可能な限りOut-of-Fold predictionを保存する。

推奨file:

```text
oof.parquet
```

OOF predictionは以下に利用できる。

* Error Analysis
* experiment間比較
* calibration分析
* ensemble
* foldごとの挙動調査
* 不自然なCV改善の調査

元のtraining rowとpredictionを対応付けられる情報を持たせる。

典型的なcolumn:

```text
row_id
fold
target
prediction
```

Classificationの場合はclass probabilityも保存してよい。

具体的なschemaはcompetitionに合わせる。

OOF fileは大容量になる可能性があるため、通常Gitにはcommitしない。

---

# 18. Feature ImportanceとDiagnostics

Modelから意味のあるfeature importanceを取得できる場合、必要に応じて以下を保存する。

```text
feature_importance.csv
```

すべてのmodelを無理に同じfeature importance interfaceへ合わせる必要はない。

その他、有用なdiagnostic artifactも必要に応じて保存してよい。

例:

```text
confusion matrix用データ
group別score
class別metric
residual table
```

大量のplotを自動生成するより、後から分析可能な元データを保存することを優先する。

可視化は主にNotebook側で行う。

---

# 19. Logs

Experiment実行時に以下を保存してよい。

```text
log.txt
```

Logは主にdebugやfailed runの原因調査に利用する。

重要なexperiment情報をlogだけに保存してはならない。

体系的な分析に必要な情報は以下に保存する。

```text
metrics.json
metadata.json
README.md
experiments.csv
```

大容量logは通常Gitにcommitしない。

---

# 20. Experiment README

各completed experimentには以下を作成する。

```text
README.md
```

Template:

```text
docs/templates/experiment_readme.md
```

READMEはexperimentの定性的な解釈を記録する。

主なsection:

```text
Hypothesis
Changes
Results
Analysis
Conclusion
Next
```

`metrics.json`の単純なコピーにしてはならない。

READMEが答えるべき中心的な問いは、

> このexperimentから何を学んだか？

である。

性能が悪化したexperimentも重要な情報なので記録する。

Conclusionでは必要に応じて以下を使用する。

```text
Supported
Partially supported
Not supported
Inconclusive
```

観測された事実と推測は区別して記述する。

---

# 21. experiments.csv

Experiment registryは以下に保存する。

```text
experiments/experiments.csv
```

1 experimentにつき1行とする。

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

例:

```csv
experiment_id,parent_experiment,description,hypothesis,status,role,cv_scheme,cv_score,cv_std,model,num_trials,duration_sec,git_commit,git_dirty,created_at
exp_001_baseline,,baseline,Establish baseline performance,completed,baseline,standard,0.7012,0.0081,lightgbm,1,144.2,abc123,false,2026-08-08T10:00:00+09:00
```

用途:

* filtering
* sorting
* experimentの簡易比較
* エージェントへのcontext提供
* 関連experimentの検索

複雑なnested structureはCSVに保存しない。

例えばfoldごとの詳細scoreは`metrics.json`に保存する。

---

# 22. Status

推奨status:

```text
planned
running
completed
failed
```

## `planned`

Configは存在するが、実行されていない。

## `running`

Experiment実行中。

## `completed`

正常に完了し、有効な評価結果が生成された。

## `failed`

実行に失敗し、有効なcompleted resultが生成されなかった。

可能な限りregistryを自動更新する。

---

# 23. Current Best

Current bestは`experiments.csv`から判定する。

原則として、

```text
status == completed
AND
cv_scheme == standard
```

を満たすexperimentのみを候補とする。

Primary CV scoreが最も良いexperimentをcurrent bestとする。

Metricには最大化するものと最小化するものがある。

最大化例:

```text
F1
AUC
accuracy
```

最小化例:

```text
RMSE
MAE
log loss
```

そのためmetric directionはmetric名から推測せず、明示的に定義する。

複数箇所でcurrent bestを手動管理しない。

`EXPERIMENT_SUMMARY.md`に可読性のためcurrent bestを書いてもよいが、構造化されたsource of truthはexperiment registryとする。

---

# 24. Processed Data

Processed datasetは以下に保存する。

```text
data/processed/
```

Processed dataは以下から再生成可能にする。

```text
raw data
+
source code
+
configuration
```

文書化されていない手作業に依存してはならない。

Processed datasetについて以下に説明を書く。

```text
data/processed/README.md
```

各主要datasetについて以下を記録する。

```text
name
source data
purpose
generation method
important transformations
important caveats
```

例:

```markdown
## dataset_v002

Source:
- `data/raw/train.csv`

Generated by:
- `src/preprocessing/` のpreprocessing pipeline

Changes:
- missing valueを正規化
- invalid rowを除外
- derived field Xを追加

Used by:
- exp_014以降
```

READMEは説明用である。

実際の変換logicはcode/configに置き、datasetを再生成できるようにする。

---

# 25. Cache

Cacheは以下に保存する。

```text
data/cache/
```

Cacheはexperiment高速化だけを目的とする。

例:

* 計算コストの高いfeature
* intermediate transformation
* 一時的なserialized representation

以下を満たす必要がある。

```text
cacheを削除してもexperimentの意味が変化しない
```

Cacheが存在しない場合、可能な限り自動再生成する。

異なるconfigから異なる内容が生成される場合、filenameだけをcache keyにすることは避ける。

可能であれば、関連するpreprocessing / feature configurationをcache identityに反映する。

初期実装ではcache invalidationを過度に複雑化しない。

---

# 26. PreprocessingとFeature Generation

正式なexperimentに必要な前処理・特徴量生成はexperiment commandから実行可能にする。

以下のようなworkflowを正式experimentの再現に必要としてはならない。

```text
Notebookを手動実行
↓
CSVを手動保存
↓
experiment実行
```

推奨workflow:

```text
run_experiment.py
↓
preprocessing code
↓
feature generation code
↓
model training
```

重い共通処理にはprocessed dataやcacheを利用してよい。

---

# 27. Notebooks

Notebookはexperiment definitionではない。

主な用途:

```text
EDA
visualization
OOF analysis
CV analysis
Error Analysis
小規模な探索
```

Notebook内のlogicが正式experimentに必要になった場合、再利用可能な実装を`src/`へ移す。

Notebook filenameには必要に応じて連番を使用する。

```text
001_eda.ipynb
002_target_analysis.ipynb
003_cv_analysis.ipynb
```

Notebook番号とExperiment IDの番号は独立して扱う。

---

# 28. Submission Generation

Submission生成は通常のCV experimentから分離する。

想定interface:

```bash
uv run python scripts/make_submission.py \
  --experiment exp_024_add_new_feature
```

選択されたexperimentの保存済みconfigを使用する。

概念的なflow:

```text
experiment config読み込み
↓
preprocessing / features再現
↓
必要なfull training dataで学習
↓
test prediction
↓
submission生成
↓
submission provenance記録
```

通常のexperimentではfull-data modelを学習する必要はない。

これにより、submissionしないexperimentに不要な計算を行わずに済む。

---

# 29. Submission Tracking

Submission fileは以下に保存する。

```text
submissions/
```

各submissionは元experimentを追跡可能にする。

単純な命名例:

```text
sub_001_exp_024_add_new_feature.csv
```

または同等の構造を使用する。

意味のある外部評価結果が得られたsubmissionについては、

```text
docs/EXPERIMENT_SUMMARY.md
```

に履歴をまとめる。

Public Leaderboard scoreをローカルCVの代わりとなる主要なモデル選択基準にはしない。

---

# 30. Model Checkpoint

Model checkpointはデフォルトでは保存しない。

通常のexperiment artifactでは以下を優先する。

```text
config
metrics
metadata
OOF prediction
analysis
```

Modelは必要になったときに、

```text
config
+
source code state
+
data
```

から再学習することを基本とする。

以下のような場合のみcheckpoint保存を検討する。

* training costが非常に大きい
* 正確な再学習が難しい
* 特定のdownstream operationでmodel自体が必要

大容量checkpointはGitにcommitしない。

---

# 31. Git Tracking Policy

Gitは以下を目的とする。

```text
version control
backup
historical archive
reproducibility
```

大容量generated artifactの主要storageとしては使用しない。

## Gitで管理するもの

原則として以下を管理する。

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
experiment README
experiment config copy
metrics.json
metadata.json
小容量のgit_diff.patch
```

## Gitで管理しないもの

原則として以下を除外する。

```text
data/raw/
data/processed/ の生成データ
data/cache/
大容量OOF file
model checkpoint
大容量log
生成されたsubmission CSV
その他の大容量かつ再生成可能なartifact
```

具体的な`.gitignore`は実際のartifact形式に合わせて設定する。

---

# 32. Testing

Experiment結果の信頼性を損なう可能性のある処理を重点的にtestする。

優先対象:

```text
preprocessing invariant
CV splitting
metric calculation
submission format
重要なdata join
data leakage prevention
```

Coverageを増やすこと自体を目的として大規模なtest suiteを作らない。

Experiment変更時は:

1. 変更したcomponentに関連するtestを実行する
2. 高コストで無関係なtestは実行しない
3. 共通infrastructureを変更した場合は、より広範囲なtestを実行する

Trainingが正常終了したという事実だけで、preprocessingやvalidation logicが正しいと判断してはならない。

---

# 33. Failed Experiment

Failed experimentを何も残さず消してはならない。

実行に失敗した場合、可能な範囲で以下を保存する。

```text
status
error message
log
config
metadata
Git state
```

ただし、

```text
execution failure
```

と、

```text
正常に完了したが性能が悪化したexperiment
```

を区別する。

例えば、

```text
CV scoreが0.01悪化した
```

experimentは`failed`ではない。

正常に完了したがhypothesisが支持されなかった`completed` experimentである。

---

# 34. EXPERIMENT_SUMMARY.mdの更新

Project全体の重要な知見は以下に保存する。

```text
docs/EXPERIMENT_SUMMARY.md
```

Template:

```text
docs/templates/experiment_summary.md
```

すべてのexperiment後に機械的に更新する必要はない。

Project全体の理解が変化した場合に更新する。

例:

* 特徴量群の有効性が複数experimentで確認された
* 有望だったhypothesisが明確に否定された
* 新しいcurrent bestにより今後の方向性が変化した
* CVの重大な問題が見つかった
* train/test distributionの重要な差が判明した
* 特定のmodeling方向を優先することになった

`EXPERIMENT_SUMMARY.md`をexperiment changelogにしてはならない。

Experiment履歴そのものは`experiments.csv`で管理する。

---

# 35. エージェントによる自律Experiment Cycle

エージェントに自律的なexperiment継続を依頼した場合、以下のcycleを基本とする。

## Step 1: 現状を理解する

以下を読む。

```text
AGENTS.md
docs/EXPERIMENT_SUMMARY.md
experiments/experiments.csv
```

以下を把握する。

```text
baseline
current best
最近の関連experiment
有効だった既知の方法
有効でなかった既知の方法
open questions
```

## Step 2: 関連Evidenceを選択する

次の判断に必要なexperimentだけを詳細に調査する。

優先的に読むもの:

```text
README.md
metrics.json
config.yaml
```

必要がない限り、過去の全experimentを詳細に読み込まない。

## Step 3: Hypothesisを立てる

明確なhypothesisを1つ立てる。

以下を説明できるようにする。

```text
なぜ改善すると考えるか
どの過去experimentが根拠となるか
どの変更によって検証するか
```

## Step 4: Parentを選択する

新しいhypothesisに最も適したexperimentをparentとして選択する。

別のparentの方が論理的に適切であれば、current bestから必ず派生させる必要はない。

## Step 5: ExperimentかTrialか判断する

同一hypothesisにおける小さなparameter差だけならtrialを使用する。

それ以外は新しいexperimentを作成する。

## Step 6: Implement

必要最小限のcode/config変更を行う。

無関係なrefactoringを行わない。

## Step 7: Test

高コストなexperimentを実行する前に、必要に応じて関連する軽量testを実行する。

## Step 8: Experiment実行

標準のexperiment commandを使用する。

## Step 9: Record

Experiment artifactとregistryが正しく保存されたことを確認する。

## Step 10: Analyze

必要に応じて以下と比較する。

```text
parent experiment
baseline
current best
```

Hypothesisについて以下のいずれかを判断する。

```text
Supported
Partially supported
Not supported
Inconclusive
```

## Step 11: Knowledgeを更新する

Experiment READMEを書く。

Project全体の理解が変化した場合のみ`EXPERIMENT_SUMMARY.md`を更新する。

## Step 12: 次のExperimentを決める

得られた結果をevidenceとして次のhypothesisを決める。

中間結果を分析せず、大量のspeculative experimentを一括実行してはならない。

---

# 36. 初期実装のScope

Experiment systemの初期versionはシンプルに保つ。

初期段階で必要な機能:

```text
self-contained experiment YAML
Experiment ID管理
parent experiment tracking
1コマンドでのCV実行
標準CV
自動preprocessing / feature generation
metrics.json
metadata.json
OOF保存
experiments.csv
experiment README
Git commit / dirty検出
git diff保存
processed data documentation
軽量test
```

以下は必要性が明確になってから追加する。

```text
Optuna integration
複雑なconfig inheritance
experiment dashboard
MLflow
Weights & Biases
automatic report generation
高度なcache dependency graph
distributed experimentation
```

シンプルなsystemで不足が生じるまで導入しない。

---

# 37. Source of Truth

同じ情報が複数箇所に存在する場合、以下をsource of truthとする。

## Experiment Definition

```text
experiments/<experiment_id>/config.yaml
```

実際に実行されたexperiment definitionのsource of truth。

## Numerical Result

```text
experiments/<experiment_id>/metrics.json
```

詳細な数値評価結果のsource of truth。

## Execution Provenance

```text
experiments/<experiment_id>/metadata.json
```

実行環境・Git状態などのsource of truth。

## Experiment Interpretation

```text
experiments/<experiment_id>/README.md
```

定性的なexperiment interpretationのsource of truth。

## Experiment Index

```text
experiments/experiments.csv
```

Project全体のexperiment registryのsource of truth。

## Project-level Knowledge

```text
docs/EXPERIMENT_SUMMARY.md
```

現在までに得られたproject-level knowledgeのsource of truth。

Summaryと個別experimentの記録が矛盾している場合は、個別experimentのraw recordを確認し、古くなったsummaryを修正する。

---

# 38. Guiding Rule

Experiment management systemによって、以下の問いに簡単に答えられる状態を維持する。

> 何を試したか？

> なぜ試したか？

> 具体的に何を変更したか？

> どのコードとconfigから結果が生成されたか？

> どのように評価したか？

> 性能は改善したか？

> 何を学んだか？

> 次に何を試すべきか？

Project structureやtoolingによってこれらの問いへの回答が難しくなった場合、experiment management systemを単純化または見直す。
