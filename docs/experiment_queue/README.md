# Experiment Queue

`docs/experiment_queue/` は、**将来検証したいhypothesisのbacklog**を人間とagentが共有する場所です。

Queueは上から順に自動実行するbatch planではありません。意味のあるexperiment結果が出るたびに、優先順位・依存関係・Search Mapを見直します。

## Core Rules

- 人間もagentもjobを追加してよい。
- Jobはhypothesis proposalであり、experiment historyではない。
- Jobにexperiment IDを事前予約しない。実際に実行すると決めた時点で `exp_NNN_*` を採番する。
- 同じscientific questionの小さなparameter差は、複数job / experimentへ分解せずtrialsを優先する。
- 実験完了後は、関連jobだけでなくqueue全体の優先度を必要に応じて再評価する。
- 実行済みの詳細結果は `experiments/` に残し、queueをhistory archiveにしない。

## Status

### `ready`

前提条件が満たされており、優先度が合えば実行可能。

### `blocked`

data、実装、外部依存、先行experimentなどの前提待ち。

### `needs_review`

仮説や実験設計に人間またはmain agentの判断が必要。

### `paused`

現時点では優先しないが、条件が変われば再開可能。

### `superseded`

別jobや既存experimentによって問いが置き換えられた。削除せず理由を残してよい。

## Prioritization

Priorityは単純な期待score gainだけで決めない。少なくとも次を考慮する。

- Expected Information Gain: 成否にかかわらず何を学べるか
- Evidence: 既存experimentやdomain reasoningによる根拠
- Expected Benefit: 成功時の影響
- Compute Cost: 実行時間・memory・GPU等
- Implementation Cost: 実装・検証の複雑さ
- Confounding Risk: 複数要因が混ざり解釈しづらくないか
- Downstream Value: 後続の複数方向を解放するか

高priority jobが常に次に実行されるとは限らない。`docs/STATUS.md` のSearch MapとOpen Strategic Questionsを含めて判断する。

## Detailed Job Files

詳細が必要なproposalは、例えば次のように個別fileへ置く。

```text
docs/experiment_queue/job_feature_group_screening.md
```

Template:

```text
docs/templates/experiment_job.md
```

Jobを選択してexperiment化した後も、experimentのauthoritative recordは `experiments/<experiment_id>/` と `experiments/experiments.csv` に置く。
