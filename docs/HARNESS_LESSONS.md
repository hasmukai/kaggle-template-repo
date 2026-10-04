# Experiment Harness Lessons

この文書は、個々のcompetitionではなく、**実験ハーネスそのものの設計・運用から得た再利用可能な知見**を記録する。

これは project policy の全文を複製する場所でも、document変更の changelog でもない。規範的なルールは `AGENTS.md` と `docs/experiment_management.md` を参照する。

## Lesson: 再現性と immutable artifact は強い基盤になる

**Observed pattern**

- self-contained config、固定CV、experiment lineage、metrics / metadata / README、OOF、Git provenance を残す設計は、長い実験列の後でも「何を試して何が起きたか」を復元しやすかった。
- negative result も残したことで、同じ失敗を再試行しにくくなった。

**Design response**

- v2でも experiment-level source of truth と completed experiment の immutability を維持する。

**General principle**

- ハーネス改善で新しい管理機能を足すときも、再現性を担う単純な artifact 構造は壊さない。

## Lesson: 人間向け現在地とagent向け累積contextは別物

**Observed failure mode**

- project summary が長期知識と現在の方針の両方を担うと、agentには検索可能でも、人間が短時間で現在地をつかみにくくなった。

**Design response**

- `docs/STATUS.md` を短い human control plane とする。
- `docs/EXPERIMENT_SUMMARY.md` は耐久性のある科学的知識に限定する。

**General principle**

- 現在地表示と長期記憶では必要な情報圧縮率が違う。同じdocumentに統合しない。

## Lesson: current-best gravity は探索を狭める

**Observed failure mode**

- current best ができると、その周辺へ特徴量やparameterを足す実験が自然に増え、別のmodel family、representation、diagnosticsなどの枝が相対的に薄くなった。

**Design response**

- `STATUS.md` に Search Map を置き、active / unexplored / stalled / blocked な枝を可視化する。
- 同一lineageの近傍実験が続く場合は strategic review を挟む。

**General principle**

- 探索の多様性は「停滞したら思い出す」だけでは維持できない。探索空間の状態を外部化する。

## Lesson: exploration は固定比率ではなく可視化と理由付けで管理する

**Observed pattern**

- 別modelを試すこと自体が目的になると、計算資源を浪費する。
- 一方、未探索の枝を理由なく放置するとlocal optimumに入りやすい。

**Design response**

- 固定のexploration quotaは設けず、Search Mapとstrategic reviewで「なぜ今この枝を続ける／止めるのか」を明示する。

**General principle**

- 探索の幅は量ではなく、意思決定理由が可視化されているかで管理する。

## Lesson: Screening と Confirmation を分ける

**Observed failure mode**

- 単一CVでわずかに良かった候補が、そのまま次のdefault parentになり、後でmulti-seed等により差がnoiseだったと分かることがあった。

**Design response**

- 安価な Screening と、promotion判断に必要な Confirmation を概念的に分ける。
- seed数や統計閾値はcompetition固有とし、universal ruleにはしない。

**General principle**

- 「次に詳しく調べる価値がある」と「標準parentを置き換えるに十分」は異なるevidence levelである。

## Lesson: 同型比較を大量のexperimentにしない

**Observed failure mode**

- 同じ問いのparameter違いやfeature pair違いを別experimentとして大量に記録すると、registryの意味密度が下がり、human / agentの双方が履歴を読みづらくなった。

**Design response**

- 同じscientific questionの小さな候補比較は1 experimentのtrialsへ寄せる。

**General principle**

- experiment IDは候補値ではなく、意味のある問いの単位で切る。

## Lesson: Engineering knowledge も科学的知見と同じように永続化する

**Observed failure mode**

- multicore利用などの高速化を一度学んでも、次の実装でdefaultへ反映されずsingle-threadへ戻ることがあった。

**Design response**

- `docs/ENGINEERING_NOTES.md` を設け、再利用可能な運用知識を記録する。
- 十分に一般化できる知見はdocumentだけでなくcode / config defaultへ昇格させる。

**General principle**

- 人間の記憶を運用ルールにしない。一度学んだ安全な改善は次回のdefaultに近づける。

## Lesson: Delegation はmodel名ではなくtask riskで決める

**Observed failure mode**

- 安価なworkerへ広く実装を任せた結果、実験の意味を変えるimplementation mistakeが混入し、手戻りが発生した。

**Design response**

- routine work、ordinary implementation、CV / leakage / metric / OOF / submissionのようなhigh-risk workを分け、後者ほど強いverification gateを要求する。

**General principle**

- 「誰に任せるか」より「間違えたとき何が壊れるか」でdelegation policyを設計する。

## Lesson: Worker report は proof ではない

**Observed failure mode**

- agentが完了と報告しても、diffやartifactを確認すると意図と違う実装になっていることがあった。

**Design response**

- test、diff、executed config、metrics、OOFなどauthoritative artifactをmain decision-makerまたはcapable reviewerが確認する。

**General principle**

- agentの自己申告ではなく、外部化されたevidenceで完了を判定する。

## Lesson: runnerの肥大化はmodularityの警告

**Observed pattern**

- modelやfeatureの種類が増えるにつれて、汎用runnerへmodel-specific分岐が集まりやすかった。

**Design response**

- 現時点ではtemplateへ早すぎるabstractionを追加しない。
- 実際のcompetitionで分岐が蓄積したら、model adapter等へ分離するsignalとみなす。

**General principle**

- 最初からframework化しないが、巨大なgeneral-purpose fileを「高速実験のため」と正当化し続けない。

## Lesson: competition終了後にharness自体をretrospectiveする

**Observed pattern**

- 実験結果だけでなく、experiment loopの運用にも再利用可能な成功・失敗が残る。

**Design response**

- competition終了後または大きなmilestoneで、ハーネスのfriction、忘れられた知見、過剰なmanual step、探索偏りを振り返り、この文書とtemplateへ還元する。

**General principle**

- experiment harnessも固定インフラではなく、実際の失敗から改善される対象である。
