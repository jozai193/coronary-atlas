# Modality audit protocol v1

Written before the audit run on 8 October 2026. The run is internal exploratory evidence on the same 303-row source cohort; it is not external validation and cannot establish clinical usefulness.

## Questions

1. How do prespecified feature groups change held-out performance under a single fixed regularized logistic model?
2. How does that model behave when an entire optional modality is masked only at held-out inference time?
3. Do the input contract, labels, duplicates, or deterministic dependencies show an obvious leakage or data-quality problem?

## Frozen data and safeguards

- Read the populated `Sheet 1 - Table 1` through `ml.schema.read_data()` and use exactly the 55 `ml.schema.FEATURES`. `Cath`, `LAD`, `LCX`, and `RCA` are prohibited inputs. Do not alter labels, remove observations, synthesize records, or select features based on global label associations.
- Record hashes for the workbook and the schema, preprocessing, training, prediction, dataset-analysis, prior-improvement-protocol, and prior-improvement-results sources. Save code/runtime versions and all fold indices with the outputs.
- Every preprocessing step is fit separately inside each outer training fold. The audit estimator mirrors the production regularized logistic candidate (`C=0.03`, standard scaling for numeric columns, training-fold median/mode imputation, one-hot encoding with unseen-category ignore). It is fixed before seeing audit outcomes; there is no estimator or cutoff selection.
- Use two repetitions of five stratified outer folds with seeds `20261007` and `20261108`, separately for each target. Report each repeat as one set of 303 out-of-fold predictions. Do not pool the repeats as independent people.

## Prespecified ablations

Groups come directly from `ml.schema.GROUPS`. `Core` is Demographics + Vitals + History & examination. Evaluate these 11 feature sets for each target and repeat:

- Core.
- Core + ECG; Core + Laboratory; Core + Echocardiography (each adds one group to Core).
- All six groups.
- All groups minus Demographics, minus Vitals, minus History & examination, minus ECG, minus Laboratory, or minus Echocardiography (one group removed at a time).

Report AUC, average precision, Brier score, log loss, accuracy, precision, recall, specificity, F1, and confusion counts for every repeat and feature set. Preserve fold metrics and row-level held-out probabilities. The fixed model comparison is a feature-group diagnostic, not a replacement selection procedure. Report changes relative to `All` and to `Core` descriptively, without significance claims.

## Held-out missing-input stress test

Within the same repeated outer splits, fit the all-feature fixed estimator on complete outer-training rows. On outer-test rows only, evaluate the unmasked prediction and then deterministically mask all ECG, all Laboratory, or all Echocardiography inputs; also evaluate a `Core only` form that masks all three optional modalities together. Numeric cells become missing values and categorical cells become missing values before prediction. No masked rows enter fitting, and no missingness indicator is added. The source cohort contains no missing cells, so this measures imputer behavior under this specified perturbation only. It does not validate performance or training-time missingness generalization in real incomplete populations.

## Data integrity and descriptive strata

- Count exact duplicate full rows, duplicate 55-field input vectors, target conflicts among duplicate input vectors, constant fields, and any exact input-to-label identity or complement.
- Check the stated logical relation `Cath == any(LAD, LCX, RCA stenotic)`, tabulate all four labels, and preserve disagreements. Also check whether any individual input feature value deterministically maps to one class for a target; this is an audit diagnostic only, not feature selection.
- Report descriptive subgroup counts for Sex and age bands `<50`, `50–64`, and `65+`. Compute subgroup metrics from the all-feature out-of-fold predictions only where the subgroup has at least 30 records and at least 10 records from each target class. State that these summaries are descriptive, have no fairness interpretation, and are not independent validation.
- No patient identifier is available. Exact duplicate checks cannot establish that distinct rows represent distinct people.

## Stopping and interpretation

Run only the frozen scenarios above. Preserve all predictions, fold definitions, fold metrics, source hashes, and environment details in `ml/experiments/modality_v2/`. Do not edit production model semantics or infer that a group should be removed from one small internal audit. Any form simplification or deployment decision requires review of acquisition timing, clinical definitions, intended use, and independent data.
