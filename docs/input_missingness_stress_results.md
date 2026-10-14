# Exact-procedure input-missingness stress result

9 October 2026. This exploratory, post-hoc stress test follows the fixed
scenario definitions in [the protocol](input_missingness_stress_protocol.md).
It refits each original outer fold's already selected target-specific model
on its complete training rows and masks inputs **only in held-out rows**.
The full-input probabilities reproduced the saved original out-of-fold
predictions exactly for all four targets (maximum residual 0.0 after CSV
round-trip). Each target has 303 unique held-out rows across five disjoint
outer folds. The verifier checked source and model hashes, fold containment,
row-level labels/probabilities and every aggregate metric.

## Results

All figures below concern **raw** model outputs before the application's
later CAD-vessel display projection. The threshold is the existing 0.5;
no alternative was optimized. `Missed` and `false alarms` are counts among
the same 303 source people.

| Target | Held-out input scenario | AUC | Brier ↓ | Recall | Specificity | Missed | False alarms | Changed 0.5 decisions vs full |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| CAD | Full | .920 | .099 | 90.3% | 75.9% | 21 | 21 | 0 |
| CAD | No laboratory | .927 | .092 | 91.7% | 79.3% | 18 | 18 | 8 |
| CAD | No echo | .907 | .109 | 87.0% | 81.6% | 28 | 16 | 16 |
| CAD | Core only | .901 | .122 | 83.8% | 81.6% | 35 | 16 | 33 |
| LAD | Full | .831 | .168 | 85.9% | 67.5% | 25 | 41 | 0 |
| LAD | No laboratory | .825 | .166 | 83.6% | 67.5% | 29 | 41 | 12 |
| LAD | No echo | .795 | .180 | 81.9% | 65.1% | 32 | 44 | 16 |
| LAD | Core only | .763 | .185 | 74.6% | 71.4% | 45 | 36 | 29 |
| LCX | Full | .741 | .203 | 40.3% | 85.9% | 71 | 26 | 0 |
| LCX | No laboratory | .690 | .217 | 18.5% | 92.9% | 97 | 13 | 47 |
| LCX | No echo | .748 | .202 | 30.3% | 87.5% | 83 | 23 | 17 |
| LCX | Core only | .699 | .218 | 11.8% | 94.6% | 105 | 10 | 54 |
| RCA | Full | .717 | .207 | 40.4% | 82.0% | 68 | 34 | 0 |
| RCA | No laboratory | .681 | .218 | 16.7% | 92.1% | 95 | 15 | 58 |
| RCA | No echo | .719 | .207 | 41.2% | 82.0% | 67 | 34 | 7 |
| RCA | Core only | .675 | .219 | 15.8% | 93.1% | 96 | 13 | 59 |

`Core only` retains demographics, vitals, and history/examination: **31
observations including age**. A fully populated Core profile therefore passes
the application's current age-plus-28 completeness rule while its masked
LCX/RCA positive-case detection falls to 14/119 and 18/114 at 0.5. With only
the laboratory group masked, LCX/RCA detect 22/119 and 19/114 positives.
These are stress-test counts, not estimates for naturally incomplete patients.

The CAD result with laboratory masked improved on these same rows; that does
**not** establish that laboratories are dispensable or harmful. The scenarios
were motivated by prior inspection of this dataset, the source patients were
used repeatedly in development, and no new-patient test is available.
Missingness at a clinic is not a random whole-group deletion from complete
records. The source has no missing cells, and no model here was trained to
handle a real missingness pattern. This result also does not validate a new
minimum input count or demonstrate an accuracy gain.

## Product implication

The generic rule, “at least 28 of 55 observations,” can make an unsupported
pattern appear sufficiently complete. The form now warns before an otherwise
ready prediction, and the API includes the same warning in its response, when
**all laboratory fields** are blank:

> All laboratory observations are missing. In a post-hoc internal test on
> complete records, masking this group changed LCX/RCA raw estimates.
> Performance on naturally incomplete records has not been validated.

When **all echo fields** are blank, the corresponding warning names LAD and
the echo group. The implemented wording explicitly describes a post-hoc
internal test on complete records and says that naturally incomplete records
are unvalidated. These messages describe observed internal sensitivity; they
are not a clinical safety classification. A blanket rule requiring one or
more labs/echo fields would itself need a justified input policy and test.
Do not revise the model, the 0.5 threshold, or historical performance numbers
based on this post-hoc diagnostic alone.

Machine-readable evidence: [results.json](../output/research/input_missingness_v1/results.json),
[manifest.json](../output/research/input_missingness_v1/manifest.json), and
the four `*_predictions.csv` files beside them. Re-run
`python ml/input_missingness_stress.py`, then
`python scripts/verify_input_missingness_stress.py` to check the saved
artifact. The scripts write only to the designated research output folder;
serving and original model files are unchanged.
