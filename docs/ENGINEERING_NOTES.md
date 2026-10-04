# Engineering Notes

この文書は、実験の**速度・安定性・再現性**に影響する engineering / operational knowledge を保存する。

科学的な modeling の知見は `docs/EXPERIMENT_SUMMARY.md`、現在の意思決定は `docs/STATUS.md` に置く。

## Principle

再利用可能な運用知識は、次の順に「忘れにくく」する。

```text
observe
→ ENGINEERING_NOTES に記録
→ 十分に一般化できるなら code / config の default を改善
→ silent regression のコストが高いなら validation / test を追加
```

Document は悪い default を放置するための代替手段ではない。

## Resource Usage

### CPU parallelism

**Recommendation**

安全に並列化できる library / model では、意図せず single-thread 実行になっていないか確認する。共有serverでは利用可能CPUを独占しない設定を優先する。

**Evidence**

このtemplateではまだ benchmark 未実施。

**Scope**

CPU training、feature generation、前処理。

**Last Verified**

未検証。

**Caveat**

Libraryごとに deterministic behavior、memory usage、thread oversubscription の影響が異なる。`n_jobs=-1` 等を無条件の universal default としない。

### GPU usage

**Recommendation**

GPU対応modelを利用する場合は、device設定・memory制約・CPU fallback をconfigから確認できる形にする。

**Evidence**

このtemplateではまだ benchmark 未実施。

**Scope**

GPU trainingを導入したcompetition。

**Last Verified**

未検証。

**Caveat**

GPUを使うこと自体を性能改善とみなさない。実行速度と再現性への影響を別に評価する。

## Note Template

新しい知見は必要に応じて以下の形式で追記する。

```markdown
### <topic>

**Recommendation**
- 推奨設定または運用方法

**Evidence**
- 関連 experiment / benchmark / issue

**Scope**
- 影響する component / environment

**Last Verified**
- YYYY-MM-DD

**Caveat**
- 適用しない条件、再確認が必要な条件
```
