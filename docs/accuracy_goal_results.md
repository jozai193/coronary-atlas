# Accuracy goal: executed results - 14 October 2026

Two protocols were frozen before their new aggregate outcomes were inspected. Both use the same three repeated five-fold patient partitions of the already studied 303-person source cohort. All four targets share each outer test partition. These are internal development comparisons, not independent or clinical validation.

The baseline refits the original model-selection procedure inside each outer training partition and applies the same coherence projection as the current app. Its scores here differ from historical target-specific splits; only within-table comparisons are paired. The baseline models and explanations were preserved. A separately packaged optional ensemble now has its own inference and attributions; see [delivery and verification](accuracy_goal_delivery.md).

Primary ensemble candidate: sigmoid uniform. Primary feature candidate: selected ridge. All other procedures are secondary, and the secondary winner is not relabeled as a primary success.

## Ensemble experiment

| Candidate | Primary? | Mean Brier difference | Conditional 95% interval | Three repeat differences | Engineering screen |
|---|---|---:|---|---|---|
| uniform | False | -0.00660 | [-0.00916, -0.00396] | -0.00740 / -0.00724 / -0.00517 | Pass |
| sigmoid_uniform | True | -0.01027 | [-0.01424, -0.00638] | -0.01118 / -0.01131 / -0.00833 | Pass |
| simplex | False | -0.00637 | [-0.00904, -0.00379] | -0.00640 / -0.00718 / -0.00553 | Pass |

Negative Brier differences favor the candidate. The conditional bootstrap resamples patients after averaging their repeat-level errors; it excludes retraining, prior-search and site uncertainty. Engineering screens are research nomination rules, not tests of clinical usefulness.

### Mean projected performance

| Target | Procedure | AUC | Brier | Accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|---:|---:|
| CAD | baseline | 0.9083 | 0.1080 | 85.9% | 92.7% | 69.0% |
| CAD | uniform | 0.9215 | 0.1052 | 86.6% | 93.8% | 68.6% |
| CAD | sigmoid_uniform | 0.9207 | 0.0965 | 87.1% | 92.3% | 74.3% |
| CAD | simplex | 0.9196 | 0.1039 | 86.1% | 93.1% | 69.0% |
| LAD | baseline | 0.8169 | 0.1693 | 77.2% | 85.5% | 65.6% |
| LAD | uniform | 0.8407 | 0.1598 | 79.0% | 89.5% | 64.3% |
| LAD | sigmoid_uniform | 0.8408 | 0.1548 | 79.1% | 87.0% | 68.0% |
| LAD | simplex | 0.8366 | 0.1604 | 78.4% | 88.3% | 64.6% |
| LCX | baseline | 0.6960 | 0.2150 | 63.3% | 33.3% | 82.6% |
| LCX | uniform | 0.7290 | 0.2067 | 66.3% | 37.8% | 84.8% |
| LCX | sigmoid_uniform | 0.7250 | 0.2066 | 66.7% | 42.9% | 82.1% |
| LCX | simplex | 0.7226 | 0.2074 | 66.2% | 39.2% | 83.7% |
| RCA | baseline | 0.6998 | 0.2089 | 64.1% | 33.6% | 82.5% |
| RCA | uniform | 0.7215 | 0.2032 | 66.9% | 33.3% | 87.1% |
| RCA | sigmoid_uniform | 0.7234 | 0.2022 | 67.0% | 38.6% | 84.1% |
| RCA | simplex | 0.7162 | 0.2040 | 65.9% | 31.6% | 86.6% |

### All repeats, raw and projected

| Repeat | Target | Procedure | AUC | Brier | Average precision | Accuracy | Sensitivity | Specificity | Missed positives | False positives |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | cad | baseline_raw | 0.9147 | 0.1034 | 0.9614 | 86.5% | 92.1% | 72.4% | 17 | 24 |
| 1 | lad | baseline_raw | 0.8043 | 0.1744 | 0.8246 | 76.9% | 84.2% | 66.7% | 28 | 42 |
| 1 | lcx | baseline_raw | 0.6592 | 0.2270 | 0.5111 | 62.7% | 36.1% | 79.9% | 76 | 37 |
| 1 | rca | baseline_raw | 0.7007 | 0.2071 | 0.5887 | 63.7% | 34.2% | 81.5% | 75 | 35 |
| 1 | cad | baseline_projected | 0.9157 | 0.1036 | 0.9619 | 86.8% | 92.6% | 72.4% | 16 | 24 |
| 1 | lad | baseline_projected | 0.8051 | 0.1729 | 0.8249 | 76.6% | 83.6% | 66.7% | 29 | 42 |
| 1 | lcx | baseline_projected | 0.6623 | 0.2258 | 0.5129 | 62.7% | 35.3% | 80.4% | 77 | 36 |
| 1 | rca | baseline_projected | 0.7034 | 0.2067 | 0.5890 | 63.4% | 33.3% | 81.5% | 76 | 35 |
| 1 | cad | uniform_raw | 0.9212 | 0.1059 | 0.9673 | 87.1% | 94.4% | 69.0% | 12 | 27 |
| 1 | lad | uniform_raw | 0.8413 | 0.1606 | 0.8761 | 79.2% | 90.4% | 63.5% | 17 | 46 |
| 1 | lcx | uniform_raw | 0.7193 | 0.2097 | 0.5627 | 63.7% | 32.8% | 83.7% | 80 | 30 |
| 1 | rca | uniform_raw | 0.7245 | 0.2032 | 0.5730 | 67.3% | 34.2% | 87.3% | 75 | 24 |
| 1 | cad | uniform_projected | 0.9209 | 0.1062 | 0.9672 | 86.8% | 94.4% | 67.8% | 12 | 28 |
| 1 | lad | uniform_projected | 0.8418 | 0.1603 | 0.8763 | 79.2% | 90.4% | 63.5% | 17 | 46 |
| 1 | lcx | uniform_projected | 0.7192 | 0.2097 | 0.5626 | 63.7% | 32.8% | 83.7% | 80 | 30 |
| 1 | rca | uniform_projected | 0.7247 | 0.2031 | 0.5731 | 67.3% | 34.2% | 87.3% | 75 | 24 |
| 1 | cad | sigmoid_uniform_raw | 0.9212 | 0.0981 | 0.9671 | 86.8% | 92.6% | 72.4% | 16 | 24 |
| 1 | lad | sigmoid_uniform_raw | 0.8410 | 0.1557 | 0.8750 | 78.5% | 87.0% | 66.7% | 23 | 42 |
| 1 | lcx | sigmoid_uniform_raw | 0.7178 | 0.2093 | 0.5587 | 66.3% | 41.2% | 82.6% | 70 | 32 |
| 1 | rca | sigmoid_uniform_raw | 0.7249 | 0.2025 | 0.5748 | 67.3% | 38.6% | 84.7% | 70 | 29 |
| 1 | cad | sigmoid_uniform_projected | 0.9203 | 0.0980 | 0.9669 | 86.8% | 92.6% | 72.4% | 16 | 24 |
| 1 | lad | sigmoid_uniform_projected | 0.8415 | 0.1550 | 0.8751 | 78.9% | 87.0% | 67.5% | 23 | 41 |
| 1 | lcx | sigmoid_uniform_projected | 0.7173 | 0.2092 | 0.5576 | 66.3% | 41.2% | 82.6% | 70 | 32 |
| 1 | rca | sigmoid_uniform_projected | 0.7264 | 0.2021 | 0.5756 | 67.3% | 38.6% | 84.7% | 70 | 29 |
| 1 | cad | simplex_raw | 0.9177 | 0.1050 | 0.9659 | 86.1% | 93.5% | 67.8% | 14 | 28 |
| 1 | lad | simplex_raw | 0.8350 | 0.1619 | 0.8709 | 78.5% | 88.7% | 64.3% | 20 | 45 |
| 1 | lcx | simplex_raw | 0.7023 | 0.2128 | 0.5516 | 64.4% | 35.3% | 83.2% | 77 | 31 |
| 1 | rca | simplex_raw | 0.7196 | 0.2038 | 0.5642 | 66.7% | 31.6% | 87.8% | 78 | 23 |
| 1 | cad | simplex_projected | 0.9185 | 0.1050 | 0.9660 | 86.1% | 93.5% | 67.8% | 14 | 28 |
| 1 | lad | simplex_projected | 0.8355 | 0.1615 | 0.8710 | 78.5% | 88.7% | 64.3% | 20 | 45 |
| 1 | lcx | simplex_projected | 0.7024 | 0.2129 | 0.5511 | 64.0% | 34.5% | 83.2% | 78 | 31 |
| 1 | rca | simplex_projected | 0.7191 | 0.2039 | 0.5639 | 66.7% | 31.6% | 87.8% | 78 | 23 |
| 2 | cad | baseline_raw | 0.9037 | 0.1117 | 0.9571 | 85.5% | 92.6% | 67.8% | 16 | 28 |
| 2 | lad | baseline_raw | 0.8121 | 0.1724 | 0.8376 | 75.9% | 87.6% | 59.5% | 22 | 51 |
| 2 | lcx | baseline_raw | 0.7097 | 0.2113 | 0.5371 | 62.7% | 33.6% | 81.5% | 79 | 34 |
| 2 | rca | baseline_raw | 0.6789 | 0.2158 | 0.5363 | 64.7% | 33.3% | 83.6% | 76 | 31 |
| 2 | cad | baseline_projected | 0.9064 | 0.1108 | 0.9580 | 85.8% | 93.5% | 66.7% | 14 | 29 |
| 2 | lad | baseline_projected | 0.8197 | 0.1689 | 0.8426 | 77.6% | 87.6% | 63.5% | 22 | 46 |
| 2 | lcx | baseline_projected | 0.7099 | 0.2114 | 0.5374 | 62.7% | 33.6% | 81.5% | 79 | 34 |
| 2 | rca | baseline_projected | 0.6832 | 0.2145 | 0.5407 | 64.7% | 33.3% | 83.6% | 76 | 31 |
| 2 | cad | uniform_raw | 0.9252 | 0.1032 | 0.9684 | 86.5% | 93.5% | 69.0% | 14 | 27 |
| 2 | lad | uniform_raw | 0.8326 | 0.1618 | 0.8608 | 78.2% | 87.6% | 65.1% | 22 | 44 |
| 2 | lcx | uniform_raw | 0.7347 | 0.2061 | 0.5691 | 66.3% | 41.2% | 82.6% | 70 | 32 |
| 2 | rca | uniform_raw | 0.7098 | 0.2058 | 0.5723 | 67.0% | 30.7% | 88.9% | 79 | 21 |
| 2 | cad | uniform_projected | 0.9249 | 0.1037 | 0.9684 | 86.1% | 93.5% | 67.8% | 14 | 28 |
| 2 | lad | uniform_projected | 0.8331 | 0.1615 | 0.8610 | 78.2% | 87.6% | 65.1% | 22 | 44 |
| 2 | lcx | uniform_projected | 0.7348 | 0.2059 | 0.5692 | 66.3% | 41.2% | 82.6% | 70 | 32 |
| 2 | rca | uniform_projected | 0.7104 | 0.2055 | 0.5732 | 67.0% | 30.7% | 88.9% | 79 | 21 |
| 2 | cad | sigmoid_uniform_raw | 0.9226 | 0.0956 | 0.9679 | 87.8% | 92.1% | 77.0% | 17 | 20 |
| 2 | lad | sigmoid_uniform_raw | 0.8324 | 0.1577 | 0.8581 | 78.2% | 85.9% | 67.5% | 25 | 41 |
| 2 | lcx | sigmoid_uniform_raw | 0.7333 | 0.2050 | 0.5663 | 65.7% | 44.5% | 79.3% | 66 | 38 |
| 2 | rca | sigmoid_uniform_raw | 0.7091 | 0.2056 | 0.5738 | 67.3% | 37.7% | 85.2% | 71 | 28 |
| 2 | cad | sigmoid_uniform_projected | 0.9240 | 0.0947 | 0.9682 | 87.8% | 92.1% | 77.0% | 17 | 20 |
| 2 | lad | sigmoid_uniform_projected | 0.8333 | 0.1572 | 0.8585 | 78.2% | 85.9% | 67.5% | 25 | 41 |
| 2 | lcx | sigmoid_uniform_projected | 0.7348 | 0.2043 | 0.5667 | 65.7% | 44.5% | 79.3% | 66 | 38 |
| 2 | rca | sigmoid_uniform_projected | 0.7134 | 0.2042 | 0.5781 | 67.7% | 37.7% | 85.7% | 71 | 27 |
| 2 | cad | simplex_raw | 0.9226 | 0.1018 | 0.9678 | 86.1% | 92.1% | 71.3% | 17 | 25 |
| 2 | lad | simplex_raw | 0.8294 | 0.1627 | 0.8615 | 77.9% | 87.0% | 65.1% | 23 | 44 |
| 2 | lcx | simplex_raw | 0.7315 | 0.2064 | 0.5626 | 66.3% | 42.0% | 82.1% | 69 | 33 |
| 2 | rca | simplex_raw | 0.7047 | 0.2073 | 0.5616 | 64.7% | 28.1% | 86.8% | 82 | 25 |
| 2 | cad | simplex_projected | 0.9225 | 0.1026 | 0.9677 | 85.8% | 92.1% | 70.1% | 17 | 26 |
| 2 | lad | simplex_projected | 0.8310 | 0.1615 | 0.8624 | 77.9% | 87.0% | 65.1% | 23 | 44 |
| 2 | lcx | simplex_projected | 0.7328 | 0.2061 | 0.5633 | 66.3% | 42.0% | 82.1% | 69 | 33 |
| 2 | rca | simplex_projected | 0.7069 | 0.2067 | 0.5642 | 65.0% | 28.1% | 87.3% | 82 | 24 |
| 3 | cad | baseline_raw | 0.8997 | 0.1115 | 0.9538 | 84.2% | 90.7% | 67.8% | 20 | 28 |
| 3 | lad | baseline_raw | 0.8244 | 0.1684 | 0.8628 | 78.2% | 86.4% | 66.7% | 24 | 42 |
| 3 | lcx | baseline_raw | 0.7157 | 0.2081 | 0.5878 | 64.4% | 31.1% | 85.9% | 82 | 26 |
| 3 | rca | baseline_raw | 0.7093 | 0.2064 | 0.5628 | 64.4% | 34.2% | 82.5% | 75 | 33 |
| 3 | cad | baseline_projected | 0.9028 | 0.1096 | 0.9549 | 85.1% | 92.1% | 67.8% | 17 | 28 |
| 3 | lad | baseline_projected | 0.8258 | 0.1661 | 0.8624 | 77.6% | 85.3% | 66.7% | 26 | 42 |
| 3 | lcx | baseline_projected | 0.7157 | 0.2079 | 0.5877 | 64.4% | 31.1% | 85.9% | 82 | 26 |
| 3 | rca | baseline_projected | 0.7128 | 0.2056 | 0.5644 | 64.4% | 34.2% | 82.5% | 75 | 33 |
| 3 | cad | uniform_raw | 0.9193 | 0.1055 | 0.9643 | 86.8% | 93.5% | 70.1% | 14 | 26 |
| 3 | lad | uniform_raw | 0.8470 | 0.1579 | 0.8841 | 79.5% | 90.4% | 64.3% | 17 | 45 |
| 3 | lcx | uniform_raw | 0.7329 | 0.2044 | 0.5989 | 69.0% | 39.5% | 88.0% | 72 | 22 |
| 3 | rca | uniform_raw | 0.7287 | 0.2010 | 0.5959 | 66.3% | 35.1% | 85.2% | 74 | 28 |
| 3 | cad | uniform_projected | 0.9188 | 0.1058 | 0.9642 | 86.8% | 93.5% | 70.1% | 14 | 26 |
| 3 | lad | uniform_projected | 0.8472 | 0.1576 | 0.8841 | 79.5% | 90.4% | 64.3% | 17 | 45 |
| 3 | lcx | uniform_projected | 0.7330 | 0.2044 | 0.5989 | 69.0% | 39.5% | 88.0% | 72 | 22 |
| 3 | rca | uniform_projected | 0.7296 | 0.2008 | 0.5970 | 66.3% | 35.1% | 85.2% | 74 | 28 |
| 3 | cad | sigmoid_uniform_raw | 0.9180 | 0.0971 | 0.9628 | 86.8% | 91.7% | 74.7% | 18 | 22 |
| 3 | lad | sigmoid_uniform_raw | 0.8471 | 0.1529 | 0.8828 | 80.2% | 88.1% | 69.0% | 21 | 39 |
| 3 | lcx | sigmoid_uniform_raw | 0.7204 | 0.2077 | 0.5888 | 68.0% | 42.9% | 84.2% | 68 | 29 |
| 3 | rca | sigmoid_uniform_raw | 0.7254 | 0.2019 | 0.5823 | 65.7% | 39.5% | 81.5% | 69 | 35 |
| 3 | cad | sigmoid_uniform_projected | 0.9178 | 0.0968 | 0.9628 | 86.8% | 92.1% | 73.6% | 17 | 23 |
| 3 | lad | sigmoid_uniform_projected | 0.8476 | 0.1523 | 0.8831 | 80.2% | 88.1% | 69.0% | 21 | 39 |
| 3 | lcx | sigmoid_uniform_projected | 0.7230 | 0.2065 | 0.5898 | 68.0% | 42.9% | 84.2% | 68 | 29 |
| 3 | rca | sigmoid_uniform_projected | 0.7304 | 0.2003 | 0.5875 | 66.0% | 39.5% | 82.0% | 69 | 34 |
| 3 | cad | simplex_raw | 0.9185 | 0.1035 | 0.9649 | 86.8% | 93.5% | 70.1% | 14 | 26 |
| 3 | lad | simplex_raw | 0.8424 | 0.1588 | 0.8790 | 78.9% | 89.3% | 64.3% | 19 | 45 |
| 3 | lcx | simplex_raw | 0.7325 | 0.2034 | 0.6041 | 68.3% | 41.2% | 85.9% | 70 | 26 |
| 3 | rca | simplex_raw | 0.7221 | 0.2018 | 0.5822 | 66.0% | 35.1% | 84.7% | 74 | 29 |
| 3 | cad | simplex_projected | 0.9179 | 0.1041 | 0.9648 | 86.5% | 93.5% | 69.0% | 14 | 27 |
| 3 | lad | simplex_projected | 0.8433 | 0.1583 | 0.8793 | 78.9% | 89.3% | 64.3% | 19 | 45 |
| 3 | lcx | simplex_projected | 0.7327 | 0.2033 | 0.6042 | 68.3% | 41.2% | 85.9% | 70 | 26 |
| 3 | rca | simplex_projected | 0.7226 | 0.2015 | 0.5833 | 66.0% | 35.1% | 84.7% | 74 | 29 |

Full probabilities, source/partition manifests, fit receipt, result JSON and fresh-process verification: `ml/experiments/accuracy_ensemble_v1/`. Fitted models remain local in its ignored `private/` directory.

## Feature experiment

| Candidate | Primary? | Mean Brier difference | Conditional 95% interval | Three repeat differences | Engineering screen |
|---|---|---:|---|---|---|
| selected_ridge | True | -0.00143 | [-0.00534, +0.00229] | +0.00065 / -0.00602 / +0.00108 | Fail |
| spline_ridge | False | +0.00479 | [-0.00309, +0.01312] | +0.00504 / +0.00344 / +0.00589 | Fail |

Negative Brier differences favor the candidate. The conditional bootstrap resamples patients after averaging their repeat-level errors; it excludes retraining, prior-search and site uncertainty. Engineering screens are research nomination rules, not tests of clinical usefulness.

### Mean projected performance

| Target | Procedure | AUC | Brier | Accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|---:|---:|
| CAD | baseline | 0.9083 | 0.1080 | 85.9% | 92.7% | 69.0% |
| CAD | selected_ridge | 0.9112 | 0.1073 | 86.8% | 94.0% | 69.0% |
| CAD | spline_ridge | 0.8849 | 0.1169 | 84.6% | 93.2% | 63.2% |
| LAD | baseline | 0.8169 | 0.1693 | 77.2% | 85.5% | 65.6% |
| LAD | selected_ridge | 0.8236 | 0.1655 | 75.8% | 83.2% | 65.3% |
| LAD | spline_ridge | 0.7971 | 0.1774 | 73.4% | 81.5% | 61.9% |
| LCX | baseline | 0.6960 | 0.2150 | 63.3% | 33.3% | 82.6% |
| LCX | selected_ridge | 0.7003 | 0.2134 | 65.1% | 39.2% | 81.9% |
| LCX | spline_ridge | 0.7210 | 0.2088 | 68.9% | 47.6% | 82.6% |
| RCA | baseline | 0.6998 | 0.2089 | 64.1% | 33.6% | 82.5% |
| RCA | selected_ridge | 0.7046 | 0.2094 | 64.8% | 37.7% | 81.1% |
| RCA | spline_ridge | 0.6718 | 0.2174 | 63.4% | 29.8% | 83.6% |

### All repeats, raw and projected

| Repeat | Target | Procedure | AUC | Brier | Average precision | Accuracy | Sensitivity | Specificity | Missed positives | False positives |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | cad | baseline_raw | 0.9147 | 0.1034 | 0.9614 | 86.5% | 92.1% | 72.4% | 17 | 24 |
| 1 | lad | baseline_raw | 0.8043 | 0.1744 | 0.8246 | 76.9% | 84.2% | 66.7% | 28 | 42 |
| 1 | lcx | baseline_raw | 0.6592 | 0.2270 | 0.5111 | 62.7% | 36.1% | 79.9% | 76 | 37 |
| 1 | rca | baseline_raw | 0.7007 | 0.2071 | 0.5887 | 63.7% | 34.2% | 81.5% | 75 | 35 |
| 1 | cad | baseline_projected | 0.9157 | 0.1036 | 0.9619 | 86.8% | 92.6% | 72.4% | 16 | 24 |
| 1 | lad | baseline_projected | 0.8051 | 0.1729 | 0.8249 | 76.6% | 83.6% | 66.7% | 29 | 42 |
| 1 | lcx | baseline_projected | 0.6623 | 0.2258 | 0.5129 | 62.7% | 35.3% | 80.4% | 77 | 36 |
| 1 | rca | baseline_projected | 0.7034 | 0.2067 | 0.5890 | 63.4% | 33.3% | 81.5% | 76 | 35 |
| 1 | cad | selected_ridge_raw | 0.9062 | 0.1108 | 0.9593 | 86.5% | 94.4% | 66.7% | 12 | 29 |
| 1 | lad | selected_ridge_raw | 0.8112 | 0.1719 | 0.8450 | 75.6% | 81.9% | 66.7% | 32 | 42 |
| 1 | lcx | selected_ridge_raw | 0.6800 | 0.2199 | 0.5400 | 64.7% | 37.8% | 82.1% | 74 | 33 |
| 1 | rca | selected_ridge_raw | 0.7072 | 0.2095 | 0.5556 | 65.0% | 39.5% | 80.4% | 69 | 37 |
| 1 | cad | selected_ridge_projected | 0.9058 | 0.1119 | 0.9594 | 86.5% | 94.4% | 66.7% | 12 | 29 |
| 1 | lad | selected_ridge_projected | 0.8128 | 0.1710 | 0.8454 | 75.9% | 81.9% | 67.5% | 32 | 41 |
| 1 | lcx | selected_ridge_projected | 0.6824 | 0.2194 | 0.5416 | 65.0% | 37.8% | 82.6% | 74 | 32 |
| 1 | rca | selected_ridge_projected | 0.7081 | 0.2093 | 0.5561 | 65.0% | 39.5% | 80.4% | 69 | 37 |
| 1 | cad | spline_ridge_raw | 0.8796 | 0.1160 | 0.9412 | 85.1% | 94.0% | 63.2% | 13 | 32 |
| 1 | lad | spline_ridge_raw | 0.7892 | 0.1810 | 0.8340 | 71.9% | 81.9% | 57.9% | 32 | 53 |
| 1 | lcx | spline_ridge_raw | 0.7094 | 0.2116 | 0.5584 | 65.7% | 44.5% | 79.3% | 66 | 38 |
| 1 | rca | spline_ridge_raw | 0.6398 | 0.2271 | 0.4826 | 61.4% | 27.2% | 82.0% | 83 | 34 |
| 1 | cad | spline_ridge_projected | 0.8854 | 0.1137 | 0.9428 | 85.1% | 94.4% | 62.1% | 12 | 33 |
| 1 | lad | spline_ridge_projected | 0.7923 | 0.1795 | 0.8351 | 72.9% | 81.9% | 60.3% | 32 | 50 |
| 1 | lcx | spline_ridge_projected | 0.7112 | 0.2109 | 0.5627 | 66.3% | 43.7% | 81.0% | 67 | 35 |
| 1 | rca | spline_ridge_projected | 0.6447 | 0.2250 | 0.4888 | 61.4% | 27.2% | 82.0% | 83 | 34 |
| 2 | cad | baseline_raw | 0.9037 | 0.1117 | 0.9571 | 85.5% | 92.6% | 67.8% | 16 | 28 |
| 2 | lad | baseline_raw | 0.8121 | 0.1724 | 0.8376 | 75.9% | 87.6% | 59.5% | 22 | 51 |
| 2 | lcx | baseline_raw | 0.7097 | 0.2113 | 0.5371 | 62.7% | 33.6% | 81.5% | 79 | 34 |
| 2 | rca | baseline_raw | 0.6789 | 0.2158 | 0.5363 | 64.7% | 33.3% | 83.6% | 76 | 31 |
| 2 | cad | baseline_projected | 0.9064 | 0.1108 | 0.9580 | 85.8% | 93.5% | 66.7% | 14 | 29 |
| 2 | lad | baseline_projected | 0.8197 | 0.1689 | 0.8426 | 77.6% | 87.6% | 63.5% | 22 | 46 |
| 2 | lcx | baseline_projected | 0.7099 | 0.2114 | 0.5374 | 62.7% | 33.6% | 81.5% | 79 | 34 |
| 2 | rca | baseline_projected | 0.6832 | 0.2145 | 0.5407 | 64.7% | 33.3% | 83.6% | 76 | 31 |
| 2 | cad | selected_ridge_raw | 0.9190 | 0.1020 | 0.9652 | 87.1% | 94.0% | 70.1% | 13 | 26 |
| 2 | lad | selected_ridge_raw | 0.8290 | 0.1613 | 0.8537 | 76.2% | 84.7% | 64.3% | 27 | 45 |
| 2 | lcx | selected_ridge_raw | 0.7266 | 0.2061 | 0.5893 | 64.0% | 38.7% | 80.4% | 73 | 36 |
| 2 | rca | selected_ridge_raw | 0.6895 | 0.2129 | 0.5475 | 65.3% | 35.1% | 83.6% | 74 | 31 |
| 2 | cad | selected_ridge_projected | 0.9192 | 0.1026 | 0.9654 | 86.8% | 94.0% | 69.0% | 13 | 27 |
| 2 | lad | selected_ridge_projected | 0.8310 | 0.1604 | 0.8551 | 76.2% | 84.7% | 64.3% | 27 | 45 |
| 2 | lcx | selected_ridge_projected | 0.7275 | 0.2058 | 0.5898 | 64.0% | 38.7% | 80.4% | 73 | 36 |
| 2 | rca | selected_ridge_projected | 0.6902 | 0.2127 | 0.5477 | 65.3% | 35.1% | 83.6% | 74 | 31 |
| 2 | cad | spline_ridge_raw | 0.8829 | 0.1207 | 0.9449 | 83.5% | 90.7% | 65.5% | 20 | 30 |
| 2 | lad | spline_ridge_raw | 0.7913 | 0.1792 | 0.8343 | 73.3% | 83.6% | 58.7% | 29 | 52 |
| 2 | lcx | spline_ridge_raw | 0.7322 | 0.2078 | 0.5737 | 70.6% | 52.9% | 82.1% | 56 | 33 |
| 2 | rca | spline_ridge_raw | 0.6762 | 0.2158 | 0.5174 | 63.4% | 29.8% | 83.6% | 80 | 31 |
| 2 | cad | spline_ridge_projected | 0.8850 | 0.1200 | 0.9456 | 84.2% | 92.1% | 64.4% | 17 | 31 |
| 2 | lad | spline_ridge_projected | 0.7963 | 0.1772 | 0.8379 | 74.3% | 83.1% | 61.9% | 30 | 48 |
| 2 | lcx | spline_ridge_projected | 0.7331 | 0.2073 | 0.5753 | 70.6% | 52.9% | 82.1% | 56 | 33 |
| 2 | rca | spline_ridge_projected | 0.6795 | 0.2148 | 0.5188 | 63.4% | 29.8% | 83.6% | 80 | 31 |
| 3 | cad | baseline_raw | 0.8997 | 0.1115 | 0.9538 | 84.2% | 90.7% | 67.8% | 20 | 28 |
| 3 | lad | baseline_raw | 0.8244 | 0.1684 | 0.8628 | 78.2% | 86.4% | 66.7% | 24 | 42 |
| 3 | lcx | baseline_raw | 0.7157 | 0.2081 | 0.5878 | 64.4% | 31.1% | 85.9% | 82 | 26 |
| 3 | rca | baseline_raw | 0.7093 | 0.2064 | 0.5628 | 64.4% | 34.2% | 82.5% | 75 | 33 |
| 3 | cad | baseline_projected | 0.9028 | 0.1096 | 0.9549 | 85.1% | 92.1% | 67.8% | 17 | 28 |
| 3 | lad | baseline_projected | 0.8258 | 0.1661 | 0.8624 | 77.6% | 85.3% | 66.7% | 26 | 42 |
| 3 | lcx | baseline_projected | 0.7157 | 0.2079 | 0.5877 | 64.4% | 31.1% | 85.9% | 82 | 26 |
| 3 | rca | baseline_projected | 0.7128 | 0.2056 | 0.5644 | 64.4% | 34.2% | 82.5% | 75 | 33 |
| 3 | cad | selected_ridge_raw | 0.9090 | 0.1068 | 0.9588 | 86.8% | 93.1% | 71.3% | 15 | 25 |
| 3 | lad | selected_ridge_raw | 0.8266 | 0.1654 | 0.8704 | 74.9% | 83.6% | 62.7% | 29 | 47 |
| 3 | lcx | selected_ridge_raw | 0.6883 | 0.2158 | 0.5603 | 66.3% | 41.2% | 82.6% | 70 | 32 |
| 3 | rca | selected_ridge_raw | 0.7147 | 0.2063 | 0.5628 | 64.0% | 38.6% | 79.4% | 70 | 39 |
| 3 | cad | selected_ridge_projected | 0.9086 | 0.1073 | 0.9588 | 87.1% | 93.5% | 71.3% | 14 | 25 |
| 3 | lad | selected_ridge_projected | 0.8269 | 0.1650 | 0.8699 | 75.2% | 83.1% | 64.3% | 30 | 45 |
| 3 | lcx | selected_ridge_projected | 0.6909 | 0.2151 | 0.5613 | 66.3% | 41.2% | 82.6% | 70 | 32 |
| 3 | rca | selected_ridge_projected | 0.7156 | 0.2061 | 0.5632 | 64.0% | 38.6% | 79.4% | 70 | 39 |
| 3 | cad | spline_ridge_raw | 0.8828 | 0.1164 | 0.9431 | 84.8% | 93.1% | 64.4% | 15 | 31 |
| 3 | lad | spline_ridge_raw | 0.7993 | 0.1772 | 0.8384 | 72.9% | 80.2% | 62.7% | 35 | 47 |
| 3 | lcx | spline_ridge_raw | 0.7174 | 0.2087 | 0.5829 | 69.3% | 46.2% | 84.2% | 64 | 29 |
| 3 | rca | spline_ridge_raw | 0.6835 | 0.2140 | 0.5239 | 65.3% | 32.5% | 85.2% | 77 | 28 |
| 3 | cad | spline_ridge_projected | 0.8844 | 0.1169 | 0.9435 | 84.5% | 93.1% | 63.2% | 15 | 32 |
| 3 | lad | spline_ridge_projected | 0.8026 | 0.1756 | 0.8400 | 72.9% | 79.7% | 63.5% | 36 | 46 |
| 3 | lcx | spline_ridge_projected | 0.7188 | 0.2080 | 0.5839 | 69.6% | 46.2% | 84.8% | 64 | 28 |
| 3 | rca | spline_ridge_projected | 0.6914 | 0.2122 | 0.5293 | 65.3% | 32.5% | 85.2% | 77 | 28 |

Full probabilities, source/partition manifests, fit receipt, result JSON and fresh-process verification: `ml/experiments/accuracy_features_v1/`. Fitted models remain local in its ignored `private/` directory.

## Feature selection frequencies

| Target | Procedure | Selected configuration | Outer folds |
|---|---|---|---:|
| cad | selected_ridge | {'arm': 'selected_ridge', 'percentile': 25, 'C': 0.1} | 2 |
| cad | selected_ridge | {'arm': 'selected_ridge', 'percentile': 50, 'C': 0.1} | 5 |
| cad | selected_ridge | {'arm': 'selected_ridge', 'percentile': 100, 'C': 0.1} | 8 |
| cad | spline_ridge | {'arm': 'spline_ridge', 'C': 0.03} | 2 |
| cad | spline_ridge | {'arm': 'spline_ridge', 'C': 0.1} | 13 |
| lad | selected_ridge | {'arm': 'selected_ridge', 'percentile': 25, 'C': 0.1} | 8 |
| lad | selected_ridge | {'arm': 'selected_ridge', 'percentile': 50, 'C': 0.1} | 3 |
| lad | selected_ridge | {'arm': 'selected_ridge', 'percentile': 100, 'C': 0.1} | 4 |
| lad | spline_ridge | {'arm': 'spline_ridge', 'C': 0.03} | 15 |
| lcx | selected_ridge | {'arm': 'selected_ridge', 'percentile': 25, 'C': 0.03} | 2 |
| lcx | selected_ridge | {'arm': 'selected_ridge', 'percentile': 50, 'C': 0.03} | 7 |
| lcx | selected_ridge | {'arm': 'selected_ridge', 'percentile': 50, 'C': 0.1} | 1 |
| lcx | selected_ridge | {'arm': 'selected_ridge', 'percentile': 100, 'C': 0.01} | 1 |
| lcx | selected_ridge | {'arm': 'selected_ridge', 'percentile': 100, 'C': 0.03} | 3 |
| lcx | selected_ridge | {'arm': 'selected_ridge', 'percentile': 100, 'C': 0.1} | 1 |
| lcx | spline_ridge | {'arm': 'spline_ridge', 'C': 0.01} | 9 |
| lcx | spline_ridge | {'arm': 'spline_ridge', 'C': 0.03} | 6 |
| rca | selected_ridge | {'arm': 'selected_ridge', 'percentile': 25, 'C': 0.03} | 1 |
| rca | selected_ridge | {'arm': 'selected_ridge', 'percentile': 25, 'C': 0.1} | 4 |
| rca | selected_ridge | {'arm': 'selected_ridge', 'percentile': 50, 'C': 0.03} | 2 |
| rca | selected_ridge | {'arm': 'selected_ridge', 'percentile': 50, 'C': 0.1} | 2 |
| rca | selected_ridge | {'arm': 'selected_ridge', 'percentile': 100, 'C': 0.03} | 3 |
| rca | selected_ridge | {'arm': 'selected_ridge', 'percentile': 100, 'C': 0.1} | 3 |
| rca | spline_ridge | {'arm': 'spline_ridge', 'C': 0.01} | 14 |
| rca | spline_ridge | {'arm': 'spline_ridge', 'C': 0.03} | 1 |

## What remains unresolved

Every repeat reuses the same people. The experiments cannot establish independent generalization, resolve undocumented source measurement timing, or pick a clinically appropriate missed-case/false-alarm tradeoff. Raising sensitivity alone is not a general accuracy gain. No target labels or angiography findings were added to model inputs.

The new public 130-participant CTP workbook was acquired and audited, but missing demographic inputs and unresolved codes/endpoint definitions prevent treating it as compatible full-input validation. See [the data review](accuracy_goal_data_review.md).

Reproduce with the existing research environment: `python -m ml.accuracy_ensemble prepare`, `fit`, `evaluate`; then `python scripts/verify_accuracy_ensemble.py`. For the second stage use `ml.accuracy_features` and `scripts/verify_accuracy_features.py`. Existing result directories are protected against overwrite; a genuinely fresh run needs a separately designated output location and recorded source version.
