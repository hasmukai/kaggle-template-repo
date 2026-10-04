# Project Status

この文書は、プロジェクトの現在地と次の意思決定を**およそ5分で把握できる長さ**に保つ。

ここは changelog、実験履歴、長期的な知識アーカイブではない。詳細な数値は experiment artifact / registry、耐久性のある科学的知見は `docs/EXPERIMENT_SUMMARY.md`、運用知識は `docs/ENGINEERING_NOTES.md` に置く。

## Goal

Competition の目的、primary metric、現在の主要な制約を簡潔に記載する。

## Robust Parent

現在、次の実験の標準的な親として採用している experiment を記載する。

- Experiment:
- CV score:
- Why robust:

数値上の最高scoreと一致しない場合がある。

## Apparent Best / Unconfirmed Best

確認が十分でないが、数値上は有望な experiment がある場合のみ記載する。

- Experiment:
- CV score:
- Why unconfirmed:

該当しなければ `なし` とする。

## Search Map

| Search Branch | State | Best Evidence | Next Question |
| --- | --- | --- | --- |
|  |  |  |  |

Branch 名は competition 固有に定義する。`active`、`unexplored`、`stalled`、`blocked` など、現在の探索状態が分かる表現を使う。

## High-confidence Findings

最大5件程度に保つ。今後の複数の意思決定に影響するものだけを残す。

1. 

## Dead Ends / Deprioritized Directions

最大5件程度に保つ。打ち切りまたは優先度を下げた理由を短く書く。

1. 

## Open Strategic Questions

最大3件程度に保つ。

1. 

## Next Candidates

最大3件程度に保つ。詳細な backlog は `docs/experiment_queue/` に置く。

1. 

## Resource Notes

現在の実験計画に直接影響する CPU / GPU / memory / runtime 上の注意を簡潔に書く。再利用可能な詳細は `docs/ENGINEERING_NOTES.md` に置く。

## Last Updated

- Date:
- Updated after:
- Reason:
