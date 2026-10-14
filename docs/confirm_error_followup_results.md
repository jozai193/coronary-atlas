# Focused training-only prediction-error audit

Executed 8 October 2026. All comparisons use only the existing CONFIRM development training partition. No new test evaluation or app promotion. Cutoffs use nested training-only OOF scores; validation labels never choose their own cutoff.

| Target | Method | AUC | Brier | Nested-cutoff recall | Specificity | FP / FN | Improvement screen |
|---|---|---:|---:|---:|---:|---:|---|
| CAD | full_linear | 0.770 | 0.1300 | 89.7% | 43.5% | 3930 / 166 | False |
| CAD | full_spline | 0.770 | 0.1300 | 89.8% | 43.3% | 3944 / 164 | False |
| CAD | core_linear | 0.755 | 0.1331 | 89.8% | 40.8% | 4116 / 165 | False |
| CAD | core_spline | 0.756 | 0.1328 | 90.2% | 40.7% | 4124 / 158 | False |
| CAD | full_average | 0.771 | 0.1297 | 90.1% | 43.2% | 3947 / 160 | False |
| CAD | core_average | 0.757 | 0.1326 | 90.1% | 41.5% | 4070 / 159 | False |
| LAD | full_linear | 0.764 | 0.1063 | 89.5% | 42.3% | 4234 / 125 | False |
| LAD | full_spline | 0.764 | 0.1062 | 89.7% | 41.8% | 4268 / 123 | False |
| LAD | core_linear | 0.749 | 0.1083 | 90.3% | 39.6% | 4430 / 116 | False |
| LAD | core_spline | 0.751 | 0.1081 | 89.4% | 39.8% | 4415 / 127 | False |
| LAD | full_average | 0.765 | 0.1060 | 89.4% | 42.3% | 4235 / 127 | False |
| LAD | core_average | 0.752 | 0.1080 | 90.1% | 40.1% | 4394 / 118 | False |
| LCX | full_linear | 0.766 | 0.0561 | 90.1% | 42.1% | 4572 / 53 | False |
| LCX | full_spline | 0.765 | 0.0563 | 92.4% | 39.3% | 4793 / 41 | False |
| LCX | core_linear | 0.758 | 0.0564 | 90.3% | 38.8% | 4830 / 52 | False |
| LCX | core_spline | 0.757 | 0.0565 | 91.6% | 39.2% | 4803 / 45 | False |
| LCX | full_average | 0.767 | 0.0561 | 91.0% | 40.7% | 4680 / 48 | False |
| LCX | core_average | 0.760 | 0.0564 | 90.5% | 40.4% | 4706 / 51 | False |
| RCA | full_linear | 0.775 | 0.0694 | 90.5% | 45.4% | 4261 / 67 | False |
| RCA | full_spline | 0.774 | 0.0695 | 89.8% | 45.1% | 4288 / 72 | False |
| RCA | core_linear | 0.760 | 0.0706 | 90.4% | 44.0% | 4370 / 68 | False |
| RCA | core_spline | 0.760 | 0.0707 | 90.2% | 42.7% | 4469 / 69 | False |
| RCA | full_average | 0.775 | 0.0693 | 89.9% | 45.4% | 4264 / 71 | False |
| RCA | core_average | 0.762 | 0.0705 | 90.5% | 43.2% | 4433 / 67 | False |

## Site/time availability

Candidate headers: ['site', 'date_lipid_panel', 'date_pci', 'date_cabg', 'date_cath', 'date_acs', 'date_mi', 'date_stemi', 'date_nstemi', 'date_cardiac_hosp', 'date_coronary_hosp', 'macedate', 'miacsdate', 'mi_date', 'revasc_date']. Header names alone do not establish authoritative site definitions or measurement dates; no site/time split was claimed.

## Interpretation

The improvement screen requires Brier improvement >=.002 and AUC loss <=.01 against full spline. It is an exploratory engineering screen, not statistical significance. All unsuccessful variants are retained. Subgroup errors are saved in results.json. OOF error patterns cannot establish causes of error or clinical fairness. Missing-input imputation does not recover unavailable measurements.

Original test outcomes remain known from the previous experiment; this training-only work preserves them and makes no fresh external claim. No pipeline was promoted. Further changes should require a specific data-quality or representation hypothesis and new evaluation evidence.

Reproduce with `python scripts/confirm_error_followup.py`; refuses overwrite. See `confirm_error_followup_protocol.md` and `ml/experiments/confirm_error_followup_v1/`.
