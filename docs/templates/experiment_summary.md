# Experiment Summary

この文書は、プロジェクト全体の実験から得られた重要な知見をまとめる。

個々の実験履歴を網羅することが目的ではない。

新しい実験を考える人間またはエージェントが、この文書を読むことで現在の状況を短時間で把握できる状態を維持する。

---

## Current Best

現在の標準CVにおける最良実験を記載する。

* Experiment:
* CV score:
* Model:
* Main characteristics:
* Parent experiment:

### Why it is currently best

現在のbestに至った主要な改善点を簡潔にまとめる。

---

## Baseline

固定baselineについて記載する。

* Experiment: `exp_001_baseline`
* CV score:
* Model:
* CV scheme:
* Main characteristics:

baseline自体は後から変更しない。

---

## What Worked

これまでの実験で、性能改善につながったことをまとめる。

単一実験の結果をそのまま列挙するのではなく、複数実験から得られた一般化可能な知見を優先する。

例:

### <finding>

Evidence:

* `exp_xxx`: ...
* `exp_yyy`: ...

Interpretation:

なぜ有効だったと考えられるかを書く。

---

## What Did Not Work

試したものの、有効ではなかった方法や悪化した方法をまとめる。

失敗したという事実だけでなく、再度試す価値があるのか、条件を変えれば可能性があるのかも可能な範囲で記載する。

例:

### <finding>

Evidence:

* `exp_xxx`: ...

Interpretation:

* なぜ悪化した可能性があるか
* この方向性を打ち切るべきか
* 条件を変えて再検証する価値があるか

---

## CV Findings

Cross-validationについて分かったことをまとめる。

例:

* 標準CVの構成
* fold間の難易度差
* 特定foldだけ挙動が異なる現象
* CVとPublic LBの関係について得られた知見
* leakageの可能性
* alternative CVから得られた知見
* CV scoreを比較する際の注意点

CV方式を変更した実験のスコアを、標準CVの実験と直接比較しないこと。

---

## Data Findings

データそのものについて判明した重要事項をまとめる。

例:

* 強い特徴を持つ変数
* 欠損値の性質
* グループ構造
* train/test差
* ラベル分布
* 外れ値
* 重複
* leakage候補
* データ生成過程についての仮説

単なるEDA結果ではなく、今後のモデリング判断に影響する知見を優先する。

---

## Model Findings

モデルについて得られた一般的な知見をまとめる。

例:

* どのモデル系が強いか
* 過学習しやすいモデル
* パラメータ感度
* 特徴量との相性
* 学習時間と性能のトレードオフ
* ensemble候補

---

## Feature Findings

特徴量について得られた重要な知見をまとめる。

例:

* 安定して効く特徴量
* 特定モデルでのみ有効な特徴量
* 冗長だった特徴量
* 悪化した特徴量
* 今後派生させる価値がある特徴量

---

## Open Questions

まだ答えが出ていない重要な問いを書く。

例:

1. CVの特定foldだけ性能が低い原因は何か
2. feature Xの改善はfeature Yとの相互作用によるものか
3. train/testで特定特徴量の分布差が性能に影響しているか

実験によって解決済みになった項目は削除する。

---

## Promising Ideas

次に検証する価値が高いアイデアを優先順にまとめる。

各アイデアには可能な限り理由を付ける。

### High priority

1. `<idea>`

   * Reason:
   * Related experiments:
   * Expected benefit:

### Medium priority

1. `<idea>`

   * Reason:

大量のアイデア置き場にはしない。
有望度が下がったものは削除または別のメモへ移す。

---

## Submission History

重要なcompetition submissionのみ記録する。

| Submission | Based on | Local CV | Public Score | Notes |
| ---------- | -------- | -------: | -----------: | ----- |
|            |          |          |              |       |

Public leaderboardへのsubmissionはモデル選択の主な判断基準にしない。

---

## Current Direction

現在どの方向性を優先しているかを簡潔に書く。

例:

> 現在はハイパーパラメータ調整よりも、CVの妥当性確認とfeature X周辺の特徴量設計を優先する。

このセクションを読むだけでも、次に何をすべきか大まかに分かる状態を維持する。

---

## Last Updated

* Date:
* Updated after:
* Reason:
