# Leave-site-code-out robustness audit

Training partition only; fixed spline model, separate other-site calibration, 12 opaque site codes. Not fresh independent validation. Site code never enters predictors. Test and previous calibration patients excluded.

| Target | Pooled AUC | Brier | Sensitivity | Specificity | FP / FN |
|---|---:|---:|---:|---:|---:|
| CAD | 0.762 | 0.132 | 90.7% | 40.4% | 4144 / 150 |
| LAD | 0.756 | 0.108 | 88.7% | 44.1% | 4097 / 135 |
| LCX | 0.736 | 0.057 | 89.2% | 43.1% | 4494 / 58 |
| RCA | 0.755 | 0.072 | 88.5% | 42.4% | 4493 / 81 |

## Per-code results

| Target | Site code | Rows | Positives | AUC | Brier |
|---|---:|---:|---:|---:|---:|
| CAD | 3 | 1124 | 231 | 0.710 | 0.150 |
| CAD | 5 | 504 | 86 | 0.677 | 0.140 |
| CAD | 7 | 396 | 118 | 0.799 | 0.163 |
| CAD | 8 | 2327 | 265 | 0.729 | 0.094 |
| CAD | 9 | 1179 | 330 | 0.738 | 0.176 |
| CAD | 10 | 1756 | 292 | 0.771 | 0.126 |
| CAD | 11 | 986 | 258 | 0.809 | 0.156 |
| CAD | 12 | 293 | 31 | 0.763 | 0.084 |
| LAD | 3 | 1124 | 169 | 0.717 | 0.119 |
| LAD | 5 | 504 | 67 | 0.667 | 0.113 |
| LAD | 7 | 396 | 100 | 0.768 | 0.159 |
| LAD | 8 | 2327 | 187 | 0.709 | 0.071 |
| LAD | 9 | 1178 | 239 | 0.730 | 0.147 |
| LAD | 10 | 1722 | 218 | 0.770 | 0.100 |
| LAD | 11 | 985 | 195 | 0.787 | 0.139 |
| LAD | 12 | 293 | 20 | 0.801 | 0.056 |
| LCX | 3 | 1120 | 68 | 0.694 | 0.056 |
| LCX | 5 | 501 | 25 | 0.587 | 0.052 |
| LCX | 7 | 395 | 38 | 0.731 | 0.086 |
| LCX | 8 | 2327 | 81 | 0.742 | 0.033 |
| LCX | 9 | 1172 | 117 | 0.717 | 0.086 |
| LCX | 10 | 1641 | 78 | 0.759 | 0.044 |
| LCX | 11 | 984 | 119 | 0.771 | 0.101 |
| LCX | 12 | 292 | 10 | 0.728 | 0.031 |
| RCA | 3 | 1122 | 97 | 0.672 | 0.079 |
| RCA | 5 | 504 | 33 | 0.672 | 0.061 |
| RCA | 7 | 394 | 55 | 0.804 | 0.106 |
| RCA | 8 | 2327 | 91 | 0.753 | 0.037 |
| RCA | 9 | 1176 | 165 | 0.728 | 0.113 |
| RCA | 10 | 1709 | 119 | 0.744 | 0.068 |
| RCA | 11 | 986 | 135 | 0.795 | 0.107 |
| RCA | 12 | 292 | 10 | 0.708 | 0.031 |

## Interpretation

The held-out code is absent from fitting and calibration. Pooled AUC blends within- and between-site discrimination; per-code values and class counts are necessary context. Small site groups have unstable estimates. No code-to-hospital mapping was verified. This uses sites already present in known development evidence and does not supply pristine independent validation. Calibration and training sizes differ from the random-fold follow-up, so a difference is not a causal estimate of site shift.

Dates inspected were lipid-panel and intervention/event dates, not a verified universal baseline enrollment date. No temporal split or future-event task was invented. All prior app and experiment artifacts remain unchanged.
