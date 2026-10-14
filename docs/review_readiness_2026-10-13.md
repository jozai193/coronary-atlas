# Follow-up readiness after relayed doctor feedback

These changes improve reviewability and input interpretation. They do not establish clinical accuracy, reviewer approval or a new echo weighting rule.

## Delivered

- Inputs-first clinician review guide: load A/B without inference, inspect findings, inspect reference anatomy, then generate an estimate. Case switching is locked during inference.
- Visible case overview, supplied/unknown counts and per-field origins. A/B comparison shows only actual differing values.
- ECG/echo observations are visible before prediction. Draft unknowns say not supplied; completed snapshots disclose computational imputation.
- Explicit source-code labels and context for ECG, EF, RWMA, valve input, blood pressure and unclear symptom/function categories. No source code is expanded into an unsupported diagnosis.
- CAD card places model meaning and supplied/imputed counts beside the percentage, with navigation to the inputs. Existing detailed anatomy/colors and six unknown investigation fields remain available.
- Downloadable standalone HTML worksheet: all 55 exact values, origins and field context; completed snapshots include separate raw/displayed outputs. Edited drafts omit stale predictions. No scripts, remote images or feedback storage.
- Two exact consecutive public-development source records, preserving all 55 values and four supplied labels, attributed to UCI/CC BY 4.0. No performance-based case selection, new scoring or original-report claim.

## Verification

45 frontend tests and the production build passed. A new Python source-preservation test independently checks every input and label against workbook rows 0/1, including numeric precision and UTF-8 units. Source-sheet regeneration verification and original workbook/model/104-mesh integrity verification passed. Live Chromium checked inputs-first behavior, one prediction, three worksheet downloads, edited-result clearing, source links, authenticated access and 390px layouts. The downloaded completed Profile B worksheet is in `output/review/`. Historical metrics, model artifacts, sample values and anatomy manifests were compared against the pre-change hash inventory and preserved.

## Next reviewer task

Refresh the app, choose Start clinician review and Profile B inputs. Ask for exact corrections to values/definitions, anatomy labels and number meaning. The original dataset codebook, acquisition timing, clinically coherent synthetic cases, intended use and missed-case/false-alarm trade-off remain unresolved. Record what was actually inspected; do not treat general encouragement as clinical sign-off.
