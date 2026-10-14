# Exact-procedure input-missingness stress test

9 October 2026. This is an exploratory follow-up to the already inspected
input-completeness issue. A one-off in-memory calculation informed the fixed
scenarios below before this saved artifact was built. It is **not** a
preregistered test, an independent cohort, or an estimate of safety with
real-world incomplete records.

## Question and fixed scenarios

The application accepts age and any 28 of its 55 fields. Its training source
has no missing cells. How do the saved, target-specific outer-fold model
procedures behave when whole groups are absent from held-out rows?

For each original target and each of its saved five outer folds, refit the
fold's **already selected** model kind and strength on that fold's complete
training rows. Score the untouched test rows under four input scenarios:

1. `full`: all 55 original measurements (reproduction control).
2. `no_lab`: mask all fields in `ml.schema.GROUPS['Laboratory']`.
3. `no_echo`: mask all fields in `ml.schema.GROUPS['Echocardiography']`.
4. `core_only`: mask ECG, Laboratory, and Echocardiography. The remaining
   31 fields include age, so this pattern passes the current 28-field API
   completeness guard when the 31 fields are supplied.

Masking happens **after fitting and only on the outer test rows**. The current
pipeline's training-fold imputers fill those unknown fields. There is no
retraining for missingness, target tuning, new feature selection, threshold
choice, or production model change. Report pooled 303-row ROC-AUC, Brier,
recall, specificity and confusion counts at the existing 0.5 threshold, plus
changed decisions and mean absolute probability change from `full`.

## Reproducibility and interpretation

`ml/input_missingness_stress.py` checks source, model metadata, fold
containment and exact reproduction of each saved `ml/metrics/*_oof.csv` before
writing the aggregate result and four row-level prediction CSVs in
`output/research/input_missingness_v1/`. The manifest records hashes of the
source workbook, saved evaluation and OOF files, model metadata and fitted
production artifacts, schema, preprocessing, evaluation code, protocol, and
runner. `scripts/verify_input_missingness_stress.py` checks those hashes,
rows, folds, probabilities and every aggregate metric without refitting.

Because all 303 source patients are complete, this intervention differs from
observed missingness. It cannot validate the 28-field rule, prescribe a new
minimum, establish external calibration, or show a model improved. Raw
target-specific probabilities are analyzed; the application's later
CAD-vessel display projection is not included. The results can justify a
carefully worded input-completeness warning and a future missing-data study.
