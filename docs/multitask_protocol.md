# Fixed shared-label forest experiment — 8 October 2026

This protocol is fixed before computing the experiment's predictions. It tests one previously unrun hypothesis from `prediction_opportunities.md`: learning CAD, LAD, LCX and RCA together may help the weaker vessel estimates because their labels are related. The original labels, including the known Cath/vessel disagreement, are preserved. This is internal development on the repeatedly studied 303 people, not an independent confirmation or a clinical result.

## Frozen comparison

- Inputs are exactly the 55 fields in `ml.schema.FEATURES`. Cath/LAD/LCX/RCA are never model inputs.
- Candidate: one native multi-output `RandomForestClassifier` with 120 trees, `min_samples_leaf=5`, `max_features='sqrt'`, `n_jobs=1`, and seed 20261007. Numeric median imputation and scaling plus categorical mode imputation and one-hot encoding match the existing forest preprocessing. No candidate tuning, calibration, resampling, feature selection, or threshold search is allowed.
- Use the two five-fold target-stratified outer partitions already saved in `ml/experiments/broad_v2/{target}.json` (seeds 20261007 and 20261108). For each target's fold, fit **all four** labels only on its training rows and score that target only on its test rows. Other target labels from a test row may never enter fitting.
- Compare each target/repeat to the saved `baseline_selector` probabilities in the corresponding `ml/experiments/broad_v2/{target}_repeat_{repeat}.csv` on identical row IDs and folds. Save row-level predictions, per-fold indices and aggregate metrics. Verify repeat-one baseline exactly reproduces the original saved OOF record.
- Report AUC, Brier, accuracy, recall, specificity, F1, confusion counts and prevalence at the unchanged 0.5 cutoff, plus paired differences. Show repeats separately, then their arithmetic mean. These are two views of the same 303 people, not 606 independent observations.

## Prespecified screen and stopping

Nominate a target for a later independent test only if mean AUC gains at least 0.015, neither repeat loses more than 0.005 AUC, mean Brier does not worsen, neither repeat worsens Brier by more than 0.005, and recall at 0.5 loses no more than 0.05 in either repeat. The screen is an engineering decision rule, not statistical significance. Every target and negative result must be reported. Passing does not authorize default promotion: the hypothesis, model family, cohort and prior comparator have already been considered in this project, so another same-cohort score cannot prove transportability or remove overall selection optimism.

Stop after this single fixed candidate. Do not adjust parameters or try variants based on its result. A real default replacement requires an unused compatible cohort with verified pre-test field definitions, matching invasive-angiography labels and patient-level separation.
