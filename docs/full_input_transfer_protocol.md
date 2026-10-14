# Full-input LCX transfer experiment v1

Frozen before fitting on 13 October 2026. Research only; no served model changes.

Question: can the previously screened AngioCAD cohort improve LCX estimation on the 303-person source cohort while preserving all 55 inputs? Prior reduced-input pooling does not answer this question.

Use the existing audited binary main-vessel LCX endpoint and 13-field harmonization from `ml/angiocad_external.py`. No new interpretation of ambiguous labels. Source-private features (the other 42) are never fabricated for AngioCAD. Their transformed contribution is zero for that cohort. A separate intercept absorbs each cohort's prevalence; all 55 feature coefficients are shared where observed.

Two repeated five-fold stratified group splits (seeds 20261013, 20261014) of source rows. Fingerprints use the 13 common fields; exclude every held-out fingerprint from additional-cohort training. All imputation, scaling and categories are fitted on training observations only. Source-private preprocessing is fitted solely on source training rows. Evaluation labels are unavailable to fitting. No calibration, threshold search or hyperparameter tuning.

Three fixed arms: common-13 local logistic; full-55 local logistic; full-55 augmented logistic. Ridge C=0.03 for all feature coefficients; unpenalized cohort intercepts. The full-local versus augmented comparison is primary; reduced-local quantifies the effect of retaining private features. Use a single fixed optimizer, fail on nonconvergence.

Prepare/freeze partitions and hashes, fit/freeze all models, then evaluate. Primary metric is paired source out-of-fold Brier difference; report AUC, average precision, accuracy, sensitivity and specificity at 0.5 for context. Report both repeats and a 1,000-draw row bootstrap of repeat-averaged squared-error differences. This interval is conditional on fitted models, not a full retraining interval. No promotion criterion is created after seeing scores. Reused populations, previous experimentation and absence of a compatible independent 55-input cohort prevent a claim of independent validation. These fixed logistic controls are not the deployed nested-selector forest benchmark; cross-protocol headline comparisons are prohibited.

Preserve live weights, original metrics, old sample fixtures and previous research bytes. New review examples are separate fixtures. Raw workbooks and fitted models remain excluded from the distributable source bundle. Limit fitting to 300 seconds; no retries with different parameters.
