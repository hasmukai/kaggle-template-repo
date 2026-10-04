# Experiment Summary

この文書は、プロジェクト全体の実験から得られた**耐久性のある科学的知見**をまとめる。

個々のexperiment履歴や、現在の次アクションを列挙することが目的ではない。現在地・robust parent・Search Map・直近の候補は `docs/STATUS.md`、詳細な履歴は `experiments/experiments.csv` と各experiment artifactを参照する。

同じ知見をexperimentごとに追記するのではなく、複数のevidenceを統合して一般化可能なfindingとして残す。

---

## Baseline / Reference Context

固定baselineや、比較解釈に必要なreference experimentを記載する。

- Baseline experiment: `exp_001_baseline`
- CV scheme:
- Primary metric:
- Relevant reference experiments:

Baseline自体の意味は後から変更しない。

---

## What Worked

再現性のある改善や、複数の意思決定に役立つpositive findingをまとめる。

### <finding>

**Evidence**

- `exp_xxx`: ...
- `exp_yyy`: ...

**Interpretation**

- なぜ有効だったと考えられるか
- どの条件で一般化できそうか
- まだ不確かな点

---

## What Did Not Work

有効ではなかった方法、悪化した方法、優先度を下げる根拠となるnegative findingをまとめる。

### <finding>

**Evidence**

- `exp_xxx`: ...

**Interpretation**

- なぜ悪化した可能性があるか
- どの条件では再検証の余地があるか
- 現時点で打ち切る理由

---

## CV Findings

Validationについて得られた長期的に重要な知見を記載する。

例:

- 標準CVの妥当性
- fold間の難易度差
- seed sensitivity
- CVとPublic LBの関係
- leakage risk
- alternative CVから得た注意点

異なるCV schemeのscoreを直接比較しない。

---

## Data Findings

今後のmodeling判断に影響するデータ知見を記載する。

例:

- train/test distribution差
- group構造
- label imbalance
- missingnessの意味
- duplicate / leakage候補
- データ生成過程についての仮説

---

## Model Findings

Model familyや学習挙動について得られた一般的な知見を記載する。

例:

- 強いmodel family
- 特徴量との相性
- 過学習傾向
- parameter sensitivity
- runtimeと性能のtrade-off

---

## Feature Findings

特徴量・表現について得られた一般的な知見を記載する。

例:

- 安定して効くfeature
- model依存のfeature
- 冗長なfeature
- interaction
- 追加候補を考える際の原則

---

## Interactions / Caveats

単純な「効いた / 効かなかった」だけでは表現できない相互作用・条件依存・解釈上の注意を書く。

例:

- feature Xはmodel Aでは有効だがmodel Bでは無効
- 単一seedでは改善するがmulti-seedでは不安定
- runtime増加に対してgainが小さい

---

## Last Updated

- Date:
- Updated after:
- Reason:
