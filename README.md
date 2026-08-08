# Kaggle / Competition Experiment Template

Kaggleを含むデータサイエンスコンペティション向けの、再利用可能なローカル開発・実験用templateです。

## Using This Template

新しいコンペティションで利用するときは、最初に以下を行います。

1. READMEのタイトルとcompetition概要を対象コンペティションに合わせる
2. 配布データを変更せず `data/raw/` に配置する
3. データ構造・評価指標・標準CVを確認して文書化する
4. 最小限のbaseline pipelineを実装する
5. `uv run python scripts/new_experiment.py --name baseline` で最初のconfigを作成する

Competition固有の処理は、確認した仕様に基づいて `src/` とexperiment configへ実装してください。

このプロジェクトでは、Public Leaderboard への頻繁な submission よりも、**ローカル Cross-Validation を中心に再現可能な実験を高速に繰り返すこと**を重視します。

主な実験サイクルは次のとおりです。

1. 過去の実験結果を確認する
2. 改善仮説を立てる
3. 親となる実験から新しい experiment を作成する
4. 必要なコード・config を変更する
5. 標準 CV で評価する
6. metrics・OOF・ログなどを保存する
7. 結果を考察する
8. 得られた知見を次の実験へ反映する

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
│   ├── EXPERIMENT_SUMMARY.md
│   ├── experiment_management.md
│   └── templates/
│       ├── experiment_readme.md
│       └── experiment_summary.md
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
│
└── tests/
```

各ディレクトリの詳細な役割や実験管理ルールは `AGENTS.md` および `docs/experiment_management.md` を参照してください。

---

## Environment

Python 環境と依存関係の管理には `uv` を使用します。

### Setup

```bash
uv sync
```

仮想環境を有効化せず、基本的には `uv run` 経由でコマンドを実行します。

例:

```bash
uv run python --version
```

依存ライブラリを追加する場合:

```bash
uv add <package>
```

開発用依存関係を追加する場合:

```bash
uv add --dev <package>
```

---

## Data

各コンペティションで配布された元データは `data/raw/` に配置します。

```text
data/
├── raw/
├── processed/
└── cache/
```

### `data/raw/`

配布された元データを保存します。

元データは原則として変更しません。

### `data/processed/`

再生成可能な加工済みデータを保存します。

各 processed dataset の内容と生成方法は、

```text
data/processed/README.md
```

に記録します。

加工済みデータは、raw data・ソースコード・config から再生成できる状態を維持します。

### `data/cache/`

前処理や特徴量生成を高速化するための一時キャッシュです。

削除しても再生成できることを前提とします。

---

## Experiment Configuration

各 experiment は `configs/` 以下の自己完結した YAML ファイルとして定義します。

```text
configs/
├── exp_001_baseline.yaml
├── exp_002_add_xxx.yaml
└── ...
```

命名規則:

```text
exp_NNN_short_description
```

例:

```text
exp_023_add_depth_feature
```

原則として、

```text
1 experiment = 1 YAML
```

とします。

config には、必要に応じて以下を記録します。

* experiment ID
* description
* hypothesis
* notes
* parent experiment
* data
* preprocessing
* features
* CV
* model
* training
* trials

詳細な schema は `docs/experiment_management.md` を参照してください。

---

## Creating a New Experiment

新しい実験は、原則として既存 experiment を親として作成します。

想定している操作例:

```bash
uv run python scripts/new_experiment.py \
  --from exp_023_add_depth_feature \
  --name add_geology_feature
```

これにより、親 experiment の config を元に、新しい experiment 用 config を作成します。

新しい experiment では、

* 何を検証するのか
* なぜ改善すると考えるのか
* 親 experiment から何を変更するのか

を明確にしてください。

---

## Running an Experiment

実験は 1 コマンドで、

```text
前処理
↓
特徴量生成
↓
Cross-Validation
↓
評価
↓
結果保存
```

まで実行することを目標とします。

想定コマンド:

```bash
uv run python scripts/run_experiment.py \
  --config configs/exp_024_add_geology_feature.yaml
```

通常の実験では、原則として共通の標準 CV を使用します。

CV 設計自体を検証する実験では別の CV を使用しても構いませんが、標準 CV のスコアと直接比較しないよう注意してください。

---

## Experiment Results

実験結果は、

```text
experiments/<experiment_id>/
```

に保存します。

例:

```text
experiments/
└── exp_024_add_geology_feature/
    ├── config.yaml
    ├── metrics.json
    ├── metadata.json
    ├── oof.parquet
    ├── log.txt
    ├── README.md
    └── git_diff.patch
```

`git_diff.patch` は、未 commit のコード変更を含む状態で実験した場合のみ保存します。

### `config.yaml`

実際に実行した config のコピーです。

### `metrics.json`

評価結果の詳細を保存します。

例:

* overall CV score
* fold ごとの score
* CV mean / std
* best iteration
* secondary metrics
* 実行時間
* trial の結果

### `metadata.json`

実験実行時の provenance を保存します。

例:

* 実行日時
* Git commit
* Git dirty state
* 実行環境
* 実行時間

### `oof.parquet`

OOF prediction を保存します。

Error Analysis や ensemble 検討などに使用します。

### `README.md`

その experiment の人間向け・LLM 向けの考察を保存します。

書式は、

```text
docs/templates/experiment_readme.md
```

に従います。

---

## Experiment Registry

全 experiment の一覧は、

```text
experiments/experiments.csv
```

で管理します。

このファイルは、すべての experiment を横断的に比較するための軽量な experiment registry です。

主な情報:

* experiment ID
* parent experiment
* description
* hypothesis
* status
* role
* CV scheme
* CV score
* CV std
* model
* number of trials
* duration
* Git commit
* Git dirty state
* creation time

詳細な fold 結果などは `metrics.json` を参照してください。

---

## Experiment Summary

プロジェクト全体で得られた重要な知見は、

```text
docs/EXPERIMENT_SUMMARY.md
```

にまとめます。

このファイルには、すべての experiment を列挙するのではなく、

* baseline
* current best
* 効果があったこと
* 効果がなかったこと
* CV に関する知見
* データに関する知見
* モデル・特徴量に関する知見
* 未解決の問い
* 次に試す価値が高いアイデア

など、今後の意思決定に重要な情報だけを残します。

書式は、

```text
docs/templates/experiment_summary.md
```

に従います。

---

## Baseline and Current Best

`exp_001_baseline` を固定 baseline とします。

baseline は一度確定したら、後から意味を変更しません。

current best は、原則として標準 CV を使用した completed experiment の中から自動的に判定します。

異なる CV scheme を使用した experiment は、標準 CV の current best 判定には含めません。

---

## Experiments and Trials

意味のある仮説の違いは、別 experiment として管理します。

一方、同じ仮説の中での小さなパラメータ違いは、同一 experiment 内の trial として扱います。

例えば、

```text
max_depth = 6
max_depth = 8
max_depth = 10
```

だけを比較する場合は、3つの experiment を作らず、1つの experiment 内で複数 trial として実行します。

初期段階では大規模なハイパーパラメータ探索を行わず、YAML に少数の候補値を列挙する程度に留めます。

Optuna 等の導入は必要性が明確になってから検討します。

---

## Notebooks

`notebooks/` は主に以下の用途で使用します。

* Exploratory Data Analysis
* 可視化
* CV 分析
* Error Analysis
* 仮説検証のための探索

再現可能な正式実験で使用する処理は、Notebook のみに残さず `src/` へ移します。

```text
notebooks = exploration / analysis
src       = reproducible experiment logic
```

---

## Submission

コンペティションプラットフォームへの submission は頻繁には行いません。

モデル開発の判断は原則としてローカル CV に基づきます。

有望な experiment を外部評価したい場合のみ submission を作成します。

想定コマンド:

```bash
uv run python scripts/make_submission.py \
  --experiment exp_024_add_geology_feature
```

submission 作成時は保存済み config を使って必要な学習を再実行し、test prediction を生成します。

通常の experiment では、学習済み model checkpoint を保存しない方針です。

---

## Git Policy

Git は主に以下の目的で使用します。

* バージョン管理
* バックアップ
* 実験時点のコード状態の記録
* 長期的なアーカイブ

Git を大容量 experiment artifact の共有ストレージとしては使用しません。

### Git に保存するもの

例:

* source code
* config
* scripts
* tests
* documentation
* experiment README
* metrics / metadata などの軽量な記録
* experiment summary

### Git に保存しないもの

例:

* competition raw data
* processed data
* cache
* large OOF predictions
* model checkpoints
* large logs
* generated submission files

実験時に working tree が dirty だった場合は、その状態を metadata に記録し、必要な `git diff` を experiment directory に保存します。

---

## Testing

コンペ用プロジェクトのため、大規模な test suite は作りません。

実験結果の信頼性を損なう可能性が高い部分を重点的にテストします。

主な対象:

* preprocessing
* CV splitting
* metrics
* submission format
* 重要な data-flow invariant

コード変更時は、変更に直接関係する test を優先して実行します。

---

## Agent Usage

Codex などの coding agent にこのプロジェクトを扱わせる場合は、まずルートの

```text
AGENTS.md
```

を参照してください。

Agent は原則として、

```text
AGENTS.md
↓
docs/EXPERIMENT_SUMMARY.md
↓
experiments/experiments.csv
↓
関連する experiment
↓
関連する config / source code
```

の順で現在の状況を把握します。

Agent が自律的に experiment を行う際も、実験結果を確認せずに多数の experiment を一括実行するのではなく、

```text
仮説
↓
実験
↓
評価
↓
考察
↓
次の仮説
```

を繰り返すことを基本とします。

---

## Documentation

詳細については以下を参照してください。

* `AGENTS.md`

  * Agent 向けのプロジェクト運用ルール

* `docs/experiment_management.md`

  * experiment 管理システムの詳細仕様

* `docs/EXPERIMENT_SUMMARY.md`

  * 現在までの主要な実験知識

* `docs/templates/experiment_readme.md`

  * 各 experiment の README template

* `docs/templates/experiment_summary.md`

  * Experiment Summary の template

* `data/processed/README.md`

  * processed dataset の説明
