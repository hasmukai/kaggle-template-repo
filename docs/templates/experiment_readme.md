# <experiment_id>

## Hypothesis

このexperimentで検証する仮説を書く。

- なぜこの変更で性能または理解が改善すると考えたのか
- どの現象・domain knowledge・過去experimentを根拠にしているのか

必要なら関連するparent experimentや過去experimentを記載する。

## Changes

Parent experimentから変更した内容を書く。

できるだけ「何を変えたか」が一目で分かるようにする。

例:

- `feature_x` を追加
- `model_type` を LightGBM から CatBoost に変更
- 欠損値補完方法を変更
- その他の条件は `parent_experiment` と同一

複数箇所を変更した場合は、それぞれ明示する。

## Results

主要な結果を簡潔にまとめる。

詳細な数値は `metrics.json` を参照する。

例:

- Primary CV score:
- Parent CV score:
- Difference:
- CV std / observed variation:
- Best trial:
- Runtime:

必要に応じて、特に重要なfold別結果やsecondary metricも記載する。

## Analysis

結果から分かったことを分析する。

以下の観点を必要に応じて検討する。

- 仮説どおりの改善が見られたか
- 改善または悪化した理由として何が考えられるか
- fold間で傾向に差があるか
- 特定のデータ群で改善・悪化していないか
- OOF予測からどのような特徴が見えるか
- 親experimentとの差は、観測されているCV variationに対して十分大きいか
- 小さい差が偶然・seed sensitivity・fold構成に依存している可能性はないか
- 実行時間や計算量に対して改善幅は妥当か

観測された事実と推測は区別して書く。

## Conclusion

このexperimentの仮説に対する結論を書く。

以下のいずれかを明確にする。

- Supported
- Partially supported
- Not supported
- Inconclusive

そのうえで、この変更を今後のexperimentで採用するかどうかを書く。

さらに、**この結果だけでrobust parentを置き換えてよいか、confirmationが必要か**を明示する。

Confirmationが必要な理由の例:

- gainがobserved CV variationに対して小さい
- fold挙動が不安定
- strategyを大きく変更する判断になる
- runtime / resource増加が大きい割にgainが小さい

Universalなseed数やscore閾値はここでは決めない。Competitionと判断リスクに応じて確認方法を選ぶ。

## Next

このexperimentから自然に導かれる**局所的な次の問い**を書く。

優先度の高いものだけを記載し、思いついた案を無制限に列挙しない。Persistentなbacklogとして残す価値があるものは `docs/experiment_queue/` へ移す。

例:

1. `feature_x` と関連する `feature_y` のinteractionを確認する
2. 改善が大きかったデータ群をOOFで分析する
3. 同じfeatureを別model familyでも検証する

## Notes

Experiment中に気づいた補足事項があれば記載する。

例:

- データ品質に関する気づき
- 実装上の注意点
- 再実行時に注意すべき事項
- 想定外の挙動
- 後で確認したい事項

再利用可能なruntime / resource知識は `docs/ENGINEERING_NOTES.md` に昇格させる。
