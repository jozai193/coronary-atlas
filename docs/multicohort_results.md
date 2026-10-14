# Multi-cohort training results - 13 October 2026

**Executed research development; no live model replacement or demonstrated overall accuracy gain.**

## What was trained

A fixed logistic model was trained on additional public-cohort records, comparing single-cohort training, pooled patients, equal study weighting and equal study-specific probability averaging. CAD uses 11 shared clinical fields across UCI (303), AngioCAD (345) and Anhui (553): **1,201 eligible CAD records**. Each vessel uses 13 fields across UCI plus target-eligible AngioCAD (LAD 322, LCX 331, RCA 326). These target-specific counts overlap; they are not separate patients. The existing 55-input model and historical metrics remain unchanged.

All 54 specified cohort/within-cohort roles completed. Whole-cohort transport excludes the destination completely; five-fold augmentation excludes current held-out rows and exact matching input fingerprints from every training source. One duplicate-input row in some AngioCAD tasks was grouped with its match. No cross-cohort input-fingerprint matches were found; this is not global identity verification.

These cohorts and earlier outcomes were already inspected. This new training design is development on reused patients, not fresh validation. Clinical selection, timing, units and endpoint thresholds differ. CAD has three cohorts; vessels have only two. Raw data and fitted research models stay local. No ECG/echo values were fabricated to fill a larger feature contract.

## Main findings

- Adding cohorts did not reliably improve predictions. Study-balanced CAD Brier worsened in every cohort: UCI .1664 to .1757, AngioCAD .1182 to .1558, Anhui .1903 to .2423. AUC also fell in all three. Some accuracy/recall changes reflect a shifted decision balance rather than better probabilities.
- LCX showed a small research signal: study-balanced AUC .7154 to .7250 and Brier .2083 to .2074 in UCI; AUC .7022 to .7125 and Brier .1815 to .1799 in AngioCAD. Both conditional Brier-difference intervals include zero. UCI sensitivity at .5 fell from 39.5% to 32.8% (72 versus 80 missed positives); AngioCAD sensitivity rose from 6.7% to 23.3% (84 versus 69 missed). This trade-off does not establish a better operating choice or justify promotion.
- LAD/RCA did not show improved Brier and AUC in every cohort. Averaging study models was not a reliable cure for population shift. Whole-cohort CAD probability transport remained poor, particularly when learning outside Anhui.
- The fixed engineering signal flag is true only for LCX; it is neither statistical significance nor a deployment gate. These reduced-input figures cannot replace the original 55-input model metrics.

## Paired augmentation differences

Study-balanced minus local-only; lower Brier and higher AUC are favorable. Conditional bootstrap intervals resample fixed patient errors, omitting refitting, study and post-search uncertainty.

| Target | Cohort | Brier difference | Conditional 95% interval | AUC difference |
|---|---|---:|---|---:|
| CAD | angiocad | +0.037654 | +0.020551 to +0.054920 | -0.031453 |
| CAD | anhui | +0.052086 | +0.033639 to +0.069790 | -0.011675 |
| CAD | uci | +0.009314 | -0.002292 to +0.021864 | -0.032620 |
| LAD | angiocad | +0.001650 | -0.007438 to +0.009639 | +0.006019 |
| LAD | uci | +0.002525 | -0.005835 to +0.011089 | -0.006546 |
| LCX | angiocad | -0.001676 | -0.009394 to +0.005902 | +0.010327 |
| LCX | uci | -0.000946 | -0.006734 to +0.005700 | +0.009591 |
| RCA | angiocad | +0.004733 | -0.003728 to +0.013119 | +0.003509 |
| RCA | uci | -0.003272 | -0.010860 to +0.004739 | +0.015966 |

## All fixed results

No arm or unfavorable cohort is omitted. Fixed decision cutoff .5. Training-prevalence predictions are constants within each fold; their aggregate out-of-fold AUC can differ from .5 because fold prevalences differ. For vessel transport only one study remains for training, so pooled, balanced, ensemble and single-study predictions coincide.

| Target | Destination | Design | Arm | N | AUC | Brier | Accuracy | Sensitivity | Specificity | FN | FP |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CAD | angiocad | augmentation | local_only | 345 | 0.8451 | 0.1182 | 0.8348 | 1.0000 | 0.1739 | 0 | 57 |
| CAD | angiocad | augmentation | pooled | 345 | 0.8096 | 0.1783 | 0.7275 | 0.7283 | 0.7246 | 75 | 19 |
| CAD | angiocad | augmentation | study_balanced | 345 | 0.8136 | 0.1558 | 0.8087 | 0.8514 | 0.6377 | 41 | 25 |
| CAD | angiocad | augmentation | study_ensemble | 345 | 0.8423 | 0.1574 | 0.8232 | 0.8804 | 0.5942 | 33 | 28 |
| CAD | angiocad | augmentation | training_prevalence | 345 | 0.4928 | 0.2160 | 0.8000 | 1.0000 | 0.0000 | 0 | 69 |
| CAD | angiocad | transport | pooled | 345 | 0.7889 | 0.2428 | 0.5739 | 0.4891 | 0.9130 | 141 | 6 |
| CAD | angiocad | transport | single_anhui | 345 | 0.8234 | 0.3279 | 0.4174 | 0.2826 | 0.9565 | 198 | 3 |
| CAD | angiocad | transport | single_uci | 345 | 0.7751 | 0.1460 | 0.8145 | 0.9275 | 0.3623 | 20 | 44 |
| CAD | angiocad | transport | study_balanced | 345 | 0.7715 | 0.2235 | 0.5855 | 0.5217 | 0.8406 | 132 | 11 |
| CAD | angiocad | transport | study_ensemble | 345 | 0.8241 | 0.2051 | 0.6580 | 0.6123 | 0.8406 | 107 | 11 |
| CAD | angiocad | transport | training_prevalence | 345 | 0.5000 | 0.2579 | 0.2000 | 0.0000 | 1.0000 | 276 | 0 |
| CAD | anhui | augmentation | local_only | 553 | 0.7608 | 0.1903 | 0.7143 | 0.3433 | 0.9261 | 132 | 26 |
| CAD | anhui | augmentation | pooled | 553 | 0.7540 | 0.2298 | 0.6166 | 0.8408 | 0.4886 | 32 | 180 |
| CAD | anhui | augmentation | study_balanced | 553 | 0.7492 | 0.2423 | 0.5841 | 0.8806 | 0.4148 | 24 | 206 |
| CAD | anhui | augmentation | study_ensemble | 553 | 0.7575 | 0.2584 | 0.5081 | 0.9801 | 0.2386 | 4 | 268 |
| CAD | anhui | augmentation | training_prevalence | 553 | 0.4963 | 0.2867 | 0.3635 | 1.0000 | 0.0000 | 0 | 352 |
| CAD | anhui | transport | pooled | 553 | 0.7374 | 0.3435 | 0.4231 | 0.9900 | 0.0994 | 2 | 317 |
| CAD | anhui | transport | single_angiocad | 553 | 0.7405 | 0.3766 | 0.3924 | 0.9950 | 0.0483 | 1 | 335 |
| CAD | anhui | transport | single_uci | 553 | 0.6727 | 0.3234 | 0.4304 | 0.9751 | 0.1193 | 5 | 310 |
| CAD | anhui | transport | study_balanced | 553 | 0.7340 | 0.3423 | 0.4268 | 0.9900 | 0.1051 | 2 | 315 |
| CAD | anhui | transport | study_ensemble | 553 | 0.7309 | 0.3443 | 0.3924 | 0.9950 | 0.0483 | 1 | 335 |
| CAD | anhui | transport | training_prevalence | 553 | 0.5000 | 0.3880 | 0.3635 | 1.0000 | 0.0000 | 0 | 352 |
| CAD | uci | augmentation | local_only | 303 | 0.7862 | 0.1664 | 0.7360 | 0.9815 | 0.1264 | 4 | 76 |
| CAD | uci | augmentation | pooled | 303 | 0.7347 | 0.1892 | 0.7294 | 0.8194 | 0.5057 | 39 | 43 |
| CAD | uci | augmentation | study_balanced | 303 | 0.7536 | 0.1757 | 0.7426 | 0.8796 | 0.4023 | 26 | 52 |
| CAD | uci | augmentation | study_ensemble | 303 | 0.7480 | 0.1832 | 0.7261 | 0.8981 | 0.2989 | 22 | 61 |
| CAD | uci | augmentation | training_prevalence | 303 | 0.4913 | 0.2252 | 0.7129 | 1.0000 | 0.0000 | 0 | 87 |
| CAD | uci | transport | pooled | 303 | 0.6792 | 0.2152 | 0.6700 | 0.7222 | 0.5402 | 60 | 40 |
| CAD | uci | transport | single_angiocad | 303 | 0.6756 | 0.1948 | 0.7129 | 0.9676 | 0.0805 | 7 | 80 |
| CAD | uci | transport | single_anhui | 303 | 0.7025 | 0.2966 | 0.4620 | 0.2778 | 0.9195 | 156 | 7 |
| CAD | uci | transport | study_balanced | 303 | 0.6759 | 0.2051 | 0.6832 | 0.7778 | 0.4483 | 48 | 48 |
| CAD | uci | transport | study_ensemble | 303 | 0.7052 | 0.2022 | 0.6997 | 0.8148 | 0.4138 | 40 | 51 |
| CAD | uci | transport | training_prevalence | 303 | 0.5000 | 0.2377 | 0.7129 | 1.0000 | 0.0000 | 0 | 87 |
| LAD | angiocad | augmentation | local_only | 322 | 0.7339 | 0.1751 | 0.7609 | 0.9825 | 0.2234 | 4 | 73 |
| LAD | angiocad | augmentation | pooled | 322 | 0.7395 | 0.1776 | 0.7826 | 0.9167 | 0.4574 | 19 | 51 |
| LAD | angiocad | augmentation | study_balanced | 322 | 0.7399 | 0.1767 | 0.7764 | 0.9211 | 0.4255 | 18 | 54 |
| LAD | angiocad | augmentation | study_ensemble | 322 | 0.7431 | 0.1785 | 0.7702 | 0.9342 | 0.3723 | 15 | 59 |
| LAD | angiocad | augmentation | training_prevalence | 322 | 0.4931 | 0.2112 | 0.7081 | 1.0000 | 0.0000 | 0 | 94 |
| LAD | angiocad | transport | pooled | 322 | 0.7225 | 0.1960 | 0.6957 | 0.7456 | 0.5745 | 58 | 40 |
| LAD | angiocad | transport | single_uci | 322 | 0.7225 | 0.1960 | 0.6957 | 0.7456 | 0.5745 | 58 | 40 |
| LAD | angiocad | transport | study_balanced | 322 | 0.7225 | 0.1960 | 0.6957 | 0.7456 | 0.5745 | 58 | 40 |
| LAD | angiocad | transport | study_ensemble | 322 | 0.7225 | 0.1960 | 0.6957 | 0.7456 | 0.5745 | 58 | 40 |
| LAD | angiocad | transport | training_prevalence | 322 | 0.5000 | 0.2221 | 0.7081 | 1.0000 | 0.0000 | 0 | 94 |
| LAD | uci | augmentation | local_only | 303 | 0.7156 | 0.2120 | 0.6700 | 0.8192 | 0.4603 | 32 | 68 |
| LAD | uci | augmentation | pooled | 303 | 0.7041 | 0.2167 | 0.6436 | 0.9040 | 0.2778 | 17 | 91 |
| LAD | uci | augmentation | study_balanced | 303 | 0.7090 | 0.2145 | 0.6469 | 0.8927 | 0.3016 | 19 | 88 |
| LAD | uci | augmentation | study_ensemble | 303 | 0.6985 | 0.2194 | 0.6436 | 0.9322 | 0.2381 | 12 | 96 |
| LAD | uci | augmentation | training_prevalence | 303 | 0.4935 | 0.2479 | 0.5842 | 1.0000 | 0.0000 | 0 | 126 |
| LAD | uci | transport | pooled | 303 | 0.6541 | 0.2409 | 0.6106 | 0.9209 | 0.1746 | 14 | 104 |
| LAD | uci | transport | single_angiocad | 303 | 0.6541 | 0.2409 | 0.6106 | 0.9209 | 0.1746 | 14 | 104 |
| LAD | uci | transport | study_balanced | 303 | 0.6541 | 0.2409 | 0.6106 | 0.9209 | 0.1746 | 14 | 104 |
| LAD | uci | transport | study_ensemble | 303 | 0.6541 | 0.2409 | 0.6106 | 0.9209 | 0.1746 | 14 | 104 |
| LAD | uci | transport | training_prevalence | 303 | 0.5000 | 0.2583 | 0.5842 | 1.0000 | 0.0000 | 0 | 126 |
| LCX | angiocad | augmentation | local_only | 331 | 0.7022 | 0.1815 | 0.7221 | 0.0667 | 0.9668 | 84 | 8 |
| LCX | angiocad | augmentation | pooled | 331 | 0.7122 | 0.1800 | 0.7281 | 0.2222 | 0.9170 | 70 | 20 |
| LCX | angiocad | augmentation | study_balanced | 331 | 0.7125 | 0.1799 | 0.7311 | 0.2333 | 0.9170 | 69 | 20 |
| LCX | angiocad | augmentation | study_ensemble | 331 | 0.7135 | 0.1807 | 0.7311 | 0.2333 | 0.9170 | 69 | 20 |
| LCX | angiocad | augmentation | training_prevalence | 331 | 0.4983 | 0.2021 | 0.7281 | 0.0000 | 1.0000 | 90 | 0 |
| LCX | angiocad | transport | pooled | 331 | 0.7087 | 0.1910 | 0.7251 | 0.4000 | 0.8465 | 54 | 37 |
| LCX | angiocad | transport | single_uci | 331 | 0.7087 | 0.1910 | 0.7251 | 0.4000 | 0.8465 | 54 | 37 |
| LCX | angiocad | transport | study_balanced | 331 | 0.7087 | 0.1910 | 0.7251 | 0.4000 | 0.8465 | 54 | 37 |
| LCX | angiocad | transport | study_ensemble | 331 | 0.7087 | 0.1910 | 0.7251 | 0.4000 | 0.8465 | 54 | 37 |
| LCX | angiocad | transport | training_prevalence | 331 | 0.5000 | 0.2126 | 0.7281 | 0.0000 | 1.0000 | 90 | 0 |
| LCX | uci | augmentation | local_only | 303 | 0.7154 | 0.2083 | 0.6898 | 0.3950 | 0.8804 | 72 | 22 |
| LCX | uci | augmentation | pooled | 303 | 0.7253 | 0.2084 | 0.6601 | 0.3025 | 0.8913 | 83 | 20 |
| LCX | uci | augmentation | study_balanced | 303 | 0.7250 | 0.2074 | 0.6700 | 0.3277 | 0.8913 | 80 | 20 |
| LCX | uci | augmentation | study_ensemble | 303 | 0.7221 | 0.2125 | 0.6436 | 0.1849 | 0.9402 | 97 | 11 |
| LCX | uci | augmentation | training_prevalence | 303 | 0.4945 | 0.2434 | 0.6073 | 0.0000 | 1.0000 | 119 | 0 |
| LCX | uci | transport | pooled | 303 | 0.6916 | 0.2252 | 0.6238 | 0.0672 | 0.9837 | 111 | 3 |
| LCX | uci | transport | single_angiocad | 303 | 0.6916 | 0.2252 | 0.6238 | 0.0672 | 0.9837 | 111 | 3 |
| LCX | uci | transport | study_balanced | 303 | 0.6916 | 0.2252 | 0.6238 | 0.0672 | 0.9837 | 111 | 3 |
| LCX | uci | transport | study_ensemble | 303 | 0.6916 | 0.2252 | 0.6238 | 0.0672 | 0.9837 | 111 | 3 |
| LCX | uci | transport | training_prevalence | 303 | 0.5000 | 0.2531 | 0.6073 | 0.0000 | 1.0000 | 119 | 0 |
| RCA | angiocad | augmentation | local_only | 326 | 0.7021 | 0.2191 | 0.6166 | 0.5419 | 0.6842 | 71 | 54 |
| RCA | angiocad | augmentation | pooled | 326 | 0.7057 | 0.2245 | 0.6227 | 0.4516 | 0.7778 | 85 | 38 |
| RCA | angiocad | augmentation | study_balanced | 326 | 0.7056 | 0.2238 | 0.6288 | 0.4645 | 0.7778 | 83 | 38 |
| RCA | angiocad | augmentation | study_ensemble | 326 | 0.7120 | 0.2216 | 0.6319 | 0.4452 | 0.8012 | 86 | 34 |
| RCA | angiocad | augmentation | training_prevalence | 326 | 0.4977 | 0.2522 | 0.5245 | 0.0000 | 1.0000 | 155 | 0 |
| RCA | angiocad | transport | pooled | 326 | 0.6869 | 0.2336 | 0.5859 | 0.3161 | 0.8304 | 106 | 29 |
| RCA | angiocad | transport | single_uci | 326 | 0.6869 | 0.2336 | 0.5859 | 0.3161 | 0.8304 | 106 | 29 |
| RCA | angiocad | transport | study_balanced | 326 | 0.6869 | 0.2336 | 0.5859 | 0.3161 | 0.8304 | 106 | 29 |
| RCA | angiocad | transport | study_ensemble | 326 | 0.6869 | 0.2336 | 0.5859 | 0.3161 | 0.8304 | 106 | 29 |
| RCA | angiocad | transport | training_prevalence | 326 | 0.5000 | 0.2592 | 0.5245 | 0.0000 | 1.0000 | 155 | 0 |
| RCA | uci | augmentation | local_only | 303 | 0.6826 | 0.2163 | 0.6502 | 0.2456 | 0.8942 | 86 | 20 |
| RCA | uci | augmentation | pooled | 303 | 0.6929 | 0.2148 | 0.6469 | 0.4211 | 0.7831 | 66 | 41 |
| RCA | uci | augmentation | study_balanced | 303 | 0.6986 | 0.2130 | 0.6601 | 0.4211 | 0.8042 | 66 | 37 |
| RCA | uci | augmentation | study_ensemble | 303 | 0.6780 | 0.2204 | 0.6403 | 0.4035 | 0.7831 | 68 | 41 |
| RCA | uci | augmentation | training_prevalence | 303 | 0.4944 | 0.2379 | 0.6238 | 0.0000 | 1.0000 | 114 | 0 |
| RCA | uci | transport | pooled | 303 | 0.6316 | 0.2390 | 0.5809 | 0.6053 | 0.5661 | 45 | 82 |
| RCA | uci | transport | single_angiocad | 303 | 0.6316 | 0.2390 | 0.5809 | 0.6053 | 0.5661 | 45 | 82 |
| RCA | uci | transport | study_balanced | 303 | 0.6316 | 0.2390 | 0.5809 | 0.6053 | 0.5661 | 45 | 82 |
| RCA | uci | transport | study_ensemble | 303 | 0.6316 | 0.2390 | 0.5809 | 0.6053 | 0.5661 | 45 | 82 |
| RCA | uci | transport | training_prevalence | 303 | 0.5000 | 0.2445 | 0.6238 | 0.0000 | 1.0000 | 114 | 0 |

## Reproduce and verify

Run from the project root with the original locally acquired workbooks: `python -m ml.multicohort prepare`, `python -m ml.multicohort run`, `python -m ml.multicohort verify`, `python scripts/verify_multicohort.py`. Preparation/fitting refuse overwrite; preserve the frozen run. `python scripts/report_multicohort.py` regenerates this report without fitting.

The runner checks raw/code/protocol/historical hashes, training roles, fitted prediction replay and saved metrics. A separate verifier recomputes 93 metric groups and checks exact one-time evaluation across 54 roles without reusing the runner metric function. Three focused multi-study tests and five existing cohort-mapping tests passed. All 53 protected historical files were unchanged.

Evidence: [protocol](multicohort_protocol.md), [all metrics](../output/research/multicohort_v1/results.json), [indexed predictions](../output/research/multicohort_v1/predictions.csv), [partitions](../output/research/multicohort_v1/partitions.json), [fit receipt](../output/research/multicohort_v1/fit_receipt.json). Research fit artifact is local-only at `output/research/multicohort_v1/private/fitted.joblib`; it includes explicitly labeled all-data fits and must never be evaluated on its training patients as if unseen.

## Decision

Keep the current app unchanged. LCX multi-study training is a small follow-up lead, with uncertain probability benefit and worse source-cohort detection at .5. A new compatible cohort and an explicit reviewed missed-case/false-alarm objective are needed before selecting a revised predictor or operating point. More rows and higher recall alone are insufficient.

Methods informed by [Patil and Parmigiani, PNAS](https://doi.org/10.1073/pnas.1708283115), [Guan et al., merging versus ensembling](https://arxiv.org/abs/1905.07382), [BMJ model evaluation](https://doi.org/10.1136/bmj-2023-074819), and [TRIPOD-Cluster](https://doi.org/10.1136/bmj-2022-071058). Dataset provenance and mapping caveats are in the linked protocol and original cohort protocols.
