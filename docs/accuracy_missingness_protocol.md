# Calibrated ensemble incomplete-input check

14 October 2026. Post-search engineering follow-up, frozen before masked-input predictions. The complete-input ensemble comparison passed its predeclared research screen. This check does not retrain, tune or select another predictor.

Replay the 60 saved outer-fold artifacts on their corresponding held-out patients, in four fixed scenarios already used in the project's prior missingness work: complete inputs; all laboratory fields absent; all echo fields absent; core only (demographics, vitals, history/examination). These masks describe artificial stress tests of originally complete records, not observed clinical missingness.

The fitted sklearn members already impute inside their pipelines. The native CatBoost member needs a categorical-missing policy. For this follow-up and any packaged candidate, fill its absent numeric and categorical inputs with the median/mode already fitted on the same outer training rows by the logistic member's imputers. No held-out statistics or labels are used. This policy cannot alter complete-input predictions; verify exact replay of the earlier baseline and calibrated-ensemble probabilities before considering masked results.

Retain .5 cutoff and existing coherence projection. Report every scenario, target and repeat for the baseline and calibrated ensemble, including raw/projected AUC, Brier, accuracy, sensitivity, specificity and confusion counts. Do not use these post-search masks to claim a clinically validated completeness rule, discard a target or tune a threshold. No all-missing prediction is authorized for use.

Prepare code/protocol/source hashes before execution; fail on incomplete baseline receipts or changed historical artifacts. Save row predictions and aggregate evidence, and replay in a fresh process. No live app changes are part of this check. A usable research candidate still requires a final full-data fit, input-integrity checks, explanation fidelity, resource/runtime tests and explicit experimental presentation.
