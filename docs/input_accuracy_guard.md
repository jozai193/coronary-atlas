# Input accuracy guard — 8 October 2026

## Finding and change

All 303 source rows satisfy `BMI = Weight (kg) / (Length (cm) / 100)^2` exactly. The previous form and API allowed contradictory values. The two synthetic profiles each combined 74 kg and 165 cm with BMI 26.7755, although those measurements imply BMI 27.1809. The default examples therefore exercised an input combination absent from the source cohort.

The API now computes BMI when weight and height are present and BMI is omitted. A supplied BMI within 0.2 of the calculation is normalized to the exact calculated value with a response warning; a larger disagreement receives HTTP 422. This tolerance accepts ordinary one-decimal rounding. The regenerated synthetic profiles have internally consistent values. The model files, 0.5 cutoff, and historical validation results are unchanged.

Numeric values outside the minimum and maximum observed for that field in the 303-row training cohort now receive HTTP 422 before inference. The form uses the same ranges and explains why generation is unavailable. This is a model-support boundary, not a statement that an outside value is medically impossible. Values inside every individual range can still form an unusual combination, and the source has no independent clinical validation.

The BMI formula is consistent with [CDC's metric definition](https://www.cdc.gov/bmi/about/index.html). The source workbook, rather than a general clinical assumption, establishes that BMI was exactly derived this way for this model's training rows.

## Measured effect and limits

The two demonstration profiles' LCX probabilities changed from 4.207% to 3.771% and from 54.803% to 54.571% after correcting BMI. These are deterministic example outputs, not known-diagnosis accuracy measurements.

The [reproducible BMI-missing stress audit](../output/verification/input_accuracy_guard.json) refitted each saved outer-fold model configuration on its original training partition. Its complete-input probabilities exactly reproduced the saved out-of-fold predictions. When BMI alone was masked on held-out rows and median-imputed by the existing pipeline, Brier scores changed as follows:

| Target | Complete BMI | BMI missing and imputed |
|---|---:|---:|
| CAD | 0.09853 | 0.09841 |
| LAD | 0.16797 | 0.16720 |
| LCX | 0.20302 | 0.20212 |
| RCA | 0.20723 | 0.20594 |

Those tiny same-cohort differences do **not** show that deriving BMI improves predictive accuracy; in this diagnostic, masked BMI had slightly lower Brier error. Derivation instead preserves the source's exact input relation and prevents an avoidable contradiction. The numeric-range rule prevents unsupported extrapolations but changes which requests receive a prediction, so it cannot be compared with the existing full-cohort AUC as a model improvement.

The largest unresolved accuracy issue remains the lack of an unused compatible cohort with verified field coding, measurement timing, and matching angiographic labels. The current 28-of-55 input minimum is an engineering guard, not an accuracy-backed completeness threshold. The existing [modality audit](modality_audit_results.md) shows missing-input sensitivity in a fixed logistic diagnostic; it is not an exact performance estimate for every deployed model.

## Verification

- `python scripts/audit_input_accuracy.py` regenerates the held-out BMI diagnostic and checks exact saved-prediction reproduction before writing its result.
- `python -m pytest -q`: 62 passed, 1 optional CatBoost test skipped after this change.
- `npm --prefix frontend test`: 14 passed, including form-level conflict, range, BMI-derivation, and rounded-boundary checks.
- `npm --prefix frontend run build` and `python scripts/verify_artifacts.py` passed. The four original model hashes were unchanged.

The historical CONFIRM experiment's original API file was copied from its existing source archive to `data/external_audit/v3/frozen_backend_main.txt` and checked against the original frozen SHA-256. Its evidence and model hashes remain unchanged; the current API can now evolve without rewriting that historical freeze.
