# Modality and input-completeness audit — 8 October 2026

This is exploratory repeated internal cross-validation on the same 303-row cohort. It does not establish external validity, clinical usefulness, or that one modality causes a prediction change. The ablations use a fixed regularized logistic model (`C=0.03`) so the estimator stays constant while the available feature groups change. Every transform is fit inside the outer training fold. The deployed model family is target-specific; this fixed-logistic audit is a controlled feature-group diagnostic, not an exact re-evaluation of each deployed artifact.

## Results

The table gives ROC-AUC and Brier score from each repeat's complete set of 303 held-out predictions. Repeats share the same records and are shown separately, not pooled as 606 people.

| Target | All-feature AUC, R1 / R2 | Core AUC, R1 / R2 | All-feature Brier, R1 / R2 | Core Brier, R1 / R2 |
|---|---:|---:|---:|---:|
| CAD | .919 / .914 | .900 / .899 | .114 / .115 | .126 / .126 |
| LAD | .828 / .826 | .783 / .782 | .167 / .169 | .186 / .186 |
| LCX | .749 / .716 | .740 / .731 | .200 / .209 | .203 / .206 |
| RCA | .739 / .724 | .714 / .702 | .198 / .204 | .205 / .208 |

`Core` contains demographics, vitals, and history/examination. Adding one modality to Core gave consistent improvements for echo on CAD and LAD (AUC changes +.016 / +.013 and +.037 / +.045 across repeats), and for laboratory on RCA (+.030 / +.034). ECG helped CAD and LAD modestly (+.010 to +.014) but had little or negative effect for LCX and RCA. No single addition improved every target.

Leave-one-group-out changes below are candidate AUC minus all-feature AUC; each cell lists repeat 1 / repeat 2. Removing history/examination reduced AUC for all four targets. Removing echocardiography reduced CAD and LAD AUC consistently. Removing laboratory reduced RCA AUC consistently, while CAD's AUC was slightly higher without laboratory. LCX group effects varied by repeat and comparator. Vitals were near-neutral or slightly positive when removed in this fixed estimator. These are small-sample descriptive differences, not evidence to change the production form or model.

| Removed group | CAD | LAD | LCX | RCA |
|---|---:|---:|---:|---:|
| Demographics | -.010 / -.008 | -.005 / -.001 | -.046 / -.055 | -.018 / -.027 |
| Vitals | -.001 / -.000 | +.007 / +.003 | -.001 / -.007 | +.009 / +.006 |
| History/examination | -.087 / -.087 | -.050 / -.055 | -.032 / -.029 | -.043 / -.040 |
| ECG | -.005 / -.009 | -.004 / -.003 | +.004 / +.009 | +.001 / +.001 |
| Laboratory | +.004 / +.007 | -.001 / +.006 | -.020 / -.004 | -.031 / -.031 |
| Echocardiography | -.010 / -.009 | -.027 / -.032 | +.005 / +.008 | +.005 / +.010 |

For the held-out missing-input stress test, the all-feature fixed logistic model was fit on complete training folds and then given deterministic missing values in held-out rows. Missing echo lowered LAD AUC by .031 / .037 and increased its Brier score by .014 / .015. Missing laboratory lowered RCA AUC by .033 / .042 and LCX by .022 / .008; RCA Brier increased by .013 / .012 and LCX by .011 / .006. Masking ECG alone caused small AUC changes. With only Core retained, CAD, LAD, and RCA AUC fell by .018–.048; LCX changed in opposite directions between repeats. This measures the current imputer's behavior under these specific test-time masks after complete-data fitting. The source has no missing cells, so it does not validate training or generalization under real-world missingness. The experiment also does not use the deployed target-specific classifier for every target; its missingness metrics are not exact production-model estimates.

The complete report contains accuracy, precision, recall, specificity, F1, AUC, average precision, Brier, log loss, and confusion counts for every target, feature set, missingness pattern, repeat, and outer fold. The subgroup section reports descriptive counts and full-feature metrics by source-coded sex and the fixed age bands `<50`, `50–64`, and `65+`. Metrics were computed only when a stratum had at least 30 records and at least 10 positive and 10 negative examples. No fairness claim is supported.

## Data integrity and review flags

- The input contract contains 55 fields and excludes `Cath`, `LAD`, `LCX`, and `RCA`. There are zero missing input cells, zero exact full-row duplicates, and zero duplicate feature vectors. No patient identifier exists, so distinct rows cannot be confirmed as distinct people. `Exertional CP` is constant (`N`) in all 303 rows.
- `Cath == CAD` differs from “at least one of LAD/LCX/RCA is Stenotic” for one record: zero-based row 93, worksheet row 95. The original labels were preserved. There are no exact whole-column input/label matches.
- A separate all-row label-integrity screen found several feature values with at least 10 observations that were pure for a target in this cohort: CAD had `Q Wave=1` (16/16), `St Elevation=1` (14/14), `HDL=39.0` (21/21), `K=4.7` (12/12), `PLT=170` (10/10), and `Region RWMA=3` or `4` (14/14 each); LAD had `St Elevation=1` (14/14) and `Region RWMA=3` or `4` (14/14 each); LCX had `PLT=170` (10/10); RCA had `ESR=3` (13/13 negatives). These value-level patterns do not prove leakage or direct label derivation. They are reasons to review source definitions, measurement timing, and acquisition workflow before interpreting those fields as pre-test inputs. No feature was removed based on this screen.
- Sex strata are `Fmale` (127) and `Male` (176), preserving the source spelling. Age-band counts are 58, 150, and 95 respectively. Their per-target class counts and full-feature descriptive metrics are in `results.json`.

## Reproducibility and validation

The prespecified design is [modality_audit_protocol.md](modality_audit_protocol.md). The runner is [modality_audit.py](../ml/modality_audit.py). The run used Python 3.11.5, NumPy 2.4.6, pandas 3.0.6, scikit-learn 1.9.1, and a one-thread limit; it made no dependency or production changes.

The source manifest is embedded in `ml/experiments/modality_v2/results.json`. Key SHA-256 values:

- Raw workbook: `739343245c2ba578b541370217531750d8e936022f928b83e0d91756caa3ff0b`
- Audit runner: `473ae141246d17214c576a5a1485fa0e92e4d85b895b1b7c91744ebf20ff8f27`
- Protocol: `07c769176420b7712af12f63f424b14f1b33337237653168e69a89b4a68d610b`

The evidence folder preserves 26,664 ablation predictions, 12,120 missing-input predictions, repeat-level and fold-level metrics, and all outer train/test indices. `tests/test_modality_audit.py` passed (3 tests), checking the feature allowlist, split and row coverage, saved predictions, and source hashes. The saved [UI summary](../ml/experiments/modality_v2/ui_summary.json) contains candidate-minus-comparator deltas by repeat for a possible evidence view; it includes no recommendation or deployment decision.

No production model, input contract, API behavior, or label was changed.
