# Bounded improvement protocol v1

Written before running this experiment, 7 October 2026. Preserve `models/` and `ml/metrics/` until a candidate has reviewable evidence and inference/explanation verification. Outputs go to `ml/experiments/improvement_v1/`.

## Questions

1. Can a bounded extension of regularization and class-weighted/extra-tree models improve discrimination or probability quality?
2. Does training-fold sigmoid calibration improve Brier score without materially sacrificing AUC?
3. How much of weak LCX/RCA sensitivity is caused by the arbitrary 0.5 classification cutoff? What false-positive cost accompanies a train-selected alternative?

## Fixed experiment

- Same immutable 303 observations and 55-field allowlist; never use Cath/LAD/LCX/RCA as inputs. No synthetic expansion, label correction, row deletion, target-informed global feature selection or cross-dataset label invention.
- Two repetitions of five stratified outer folds: seeds 20261007 and 20261108. Each outer train partition uses three stratified inner folds, seed = repeat seed + fold index. All transformations fit inside their training fold.
- Baseline reproduces the existing selection among logistic C=.03/.3, random forest and gradient boosting, by mean inner-fold ROC-AUC.
- Expanded candidate set: those four plus logistic C=.003/1, balanced logistic C=.03/.3, balanced random forest (160 trees, leaf 3), extra trees (160 trees, leaf 4) and balanced extra trees (same size). Selection still uses inner ROC-AUC. No further candidates added after reading results.
- Separately assess sigmoid calibration of the selected expanded candidate with three-fold CalibratedClassifierCV wrapping the entire preprocessing/model pipeline. Do not use isotonic calibration on this tiny sample. Calibration selection is not made on outer outcomes.
- For baseline and expanded raw models, compare 0.5 against two training-only cutoffs selected on inner out-of-fold probabilities: maximize balanced accuracy (ties closest to 0.5), and maximize specificity subject to training recall >=80% (ties closest to 0.5). The 80% figure is an exploratory engineering target, not a clinical recommendation or guarantee. Report achieved outer recall and specificity, even when the target fails.
- Save every candidate's inner fold scores, all outer split indices, threshold choices and row-wise held-out probabilities/classes. Evaluate AUC, PR-AUC, Brier, accuracy, precision, recall, specificity, F1 and counts. Do not treat repeated predictions as independent patients.
- Original outer results have already been seen; this is exploratory repeated internal validation on reused data, not a fresh test cohort. Avoid confidence claims from fold selection or repeated seeds.

## Adoption rule and stopping rule

Consider replacing a target's production raw model only if expanded selection improves mean repeated AUC by >=.015, neither repeat's AUC is worse, and mean Brier increases by no more than .005. Require actual-model explanation reconstruction and API regression before migration. Consider a calibrated path only if mean Brier improves by >=.005 and neither repeat loses >.01 AUC versus the corresponding raw expanded procedure; additional explanation/inference work is required before deployment. These are engineering gates, not significance tests or clinical acceptance criteria.

Threshold alternatives can be shown as an educational comparison when achieved recall improves, but must display specificity, precision and false-positive counts with equal prominence. They must not replace probability estimates or erase the default-cutoff evidence. No claim that tuning creates new diagnostic information.

Stop after this bounded run and report negative results. Any further search must be disclosed as a new exploratory iteration. External validation remains open unless a genuinely independent, compatible, licensed labeled cohort is acquired and verified. Inspect public candidates without merging incompatible features or labels.
