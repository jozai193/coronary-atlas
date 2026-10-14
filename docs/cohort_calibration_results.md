# Cohort-aware training and calibration - 13 October 2026

**Executed follow-up development. No live model replacement or new clinical accuracy claim.**

## What changed in the experiment

The previous pooled study mixed cohorts with different outcome frequencies. This follow-up fits common clinical-feature slopes with separate cohort intercepts, then evaluates separately fitted local sigmoid calibration. It compares against local-only learning, ordinary pooling and base models trained with the entire destination omitted. CAD uses 11 shared inputs; vessel tasks use 13. The original 55-input app remains unchanged.

All 90 target/cohort/repeat/fold roles completed. Each destination separates about 60% ranker training, 20% calibration and 20% evaluation, with duplicate-input groups kept together. Additional-cohort training excludes any match to destination calibration/evaluation inputs. Two repeats reuse the same people. The imported cohort labels/mappings and all earlier endpoint/timing/unit limitations remain unchanged. Checking the new ICD workbook found no hidden dictionary, cell comments, named ranges or validation lists that establish its unresolved codes; neither ICD nor CM-CAD entered training.

## What the results support

- **LCX remains a promising research lead:** the cohort-aware calibrated arm improved mean out-of-fold AUC and Brier over the equally calibrated local-only arm in both cohorts. Both conditional Brier-difference intervals include zero; this is not a confirmed accuracy gain.
- **CAD did not benefit from sharing feature slopes:** the cohort-aware calibrated arm had worse Brier and AUC than locally calibrated learning in all three cohorts. Separate cohort intercepts improved over ordinary pooling but did not solve predictor/endpoint/population differences.
- **Local calibration corrected much of the transferred probability mismatch.** For Anhui CAD, other-cohort-only pooled Brier .3435 became .1955 after local calibration, while local-only calibrated learning gave .1902. This improvement cannot be credited to adding patients. The calibrated transfer arm uses destination labels and is adaptation, not untouched external validation.
- LAD/RCA results were mixed. No target-specific model was promoted. These figures evaluate reduced-input development procedures, not the served 55-input model or its previously reported accuracies.

## LCX primary comparison

Means across two repeat-level metrics; fixed .5 cutoff. AUC summarizes out-of-fold scores from multiple fitted models; complete within-fold AUC values and both repeats are retained below.

| Cohort | Arm | AUC | Brier (lower better) | Accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|---:|---:|
| uci | local_sigmoid | 0.7063 | 0.2088 | 0.6832 | 0.4244 | 0.8505 |
| uci | cohort_intercepts_sigmoid | 0.7219 | 0.2053 | 0.6815 | 0.4412 | 0.8370 |
| angiocad | local_sigmoid | 0.6885 | 0.1825 | 0.7311 | 0.1000 | 0.9668 |
| angiocad | cohort_intercepts_sigmoid | 0.6994 | 0.1813 | 0.7296 | 0.1611 | 0.9419 |

At .5, UCI LCX missed 71/66 positives with local calibration versus 67/66 with cohort-aware calibration, across repeats 1/2. False alarms were 28/27 versus 29/31. AngioCAD missed 82/80 versus 76/75, with false alarms 8/8 versus 14/14. More detections came with more false alarms; performance is still insufficient for a rule-out claim.

## Additional-data probability comparison

Cohort-aware calibrated minus local-only calibrated. Bootstrap intervals average each patient's two repeat errors first and resample patients. They omit refitting, site, endpoint and post-search uncertainty.

| Target | Cohort | Brier difference | Conditional 95% interval | AUC change repeat 1 / 2 |
|---|---|---:|---|---|
| CAD | angiocad | +0.007462 | +0.000041 to +0.015360 | -0.020689 / -0.022159 |
| CAD | anhui | +0.002417 | -0.003223 to +0.007936 | -0.009046 / -0.011971 |
| CAD | uci | +0.015441 | +0.003845 to +0.027554 | -0.033418 / -0.074819 |
| LAD | angiocad | +0.003385 | -0.003714 to +0.010124 | -0.007512 / -0.012318 |
| LAD | uci | -0.000106 | -0.008859 to +0.008765 | -0.004977 / -0.004170 |
| LCX | angiocad | -0.001163 | -0.006895 to +0.004471 | +0.003181 / +0.018580 |
| LCX | uci | -0.003510 | -0.009669 to +0.003208 | +0.019958 / +0.011189 |
| RCA | angiocad | +0.000117 | -0.006911 to +0.006978 | +0.011356 / +0.007319 |
| RCA | uci | -0.000380 | -0.008236 to +0.007554 | +0.011046 / -0.006498 |

## Exploratory sensitivity illustration

A 90% empirical calibration sensitivity target is not a guarantee for evaluation patients, an approved clinical objective or a recommended cutoff. Thresholds were selected only on calibration positives after calibration fitting; evaluation remained separate. For UCI LCX, mean evaluation sensitivity was 83.2% local-calibrated versus 86.1% cohort-aware-calibrated, with specificity 40.5% versus 38.0%. For AngioCAD it was 88.9% versus 88.3%, with specificity 34.0% versus 31.3%. The latter comparison shows no operational advantage. All selected cutoffs/errors follow below.

## All fixed results - both repeats

No unfavorable cohort, arm or operating point is omitted. The training-prevalence arm is constant within each fold; its aggregate out-of-fold AUC can differ from .5. Calibration slopes ranged .1713 to 2.4008, all positive: within a fold sigmoid retains ranking, while pooled AUC can change as score scales differ between folds. The cohort-intercept model requires a known training-cohort context and rejects unknown cohorts; it is not a general unknown-hospital model.

| Target | Cohort | Repeat | Arm | Point | N | AUC | Mean fold AUC | Brier | Accuracy | Sensitivity | Specificity | FN | FP | Cutoff range |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CAD | angiocad | 1 | cohort_intercepts | fixed_50 | 345 | 0.8294 | 0.8288 | 0.1193 | 0.8319 | 0.9855 | 0.2174 | 4 | 54 | 0.50000-0.50000 |
| CAD | angiocad | 1 | cohort_intercepts | target_90 | 345 | 0.8294 | 0.8288 | 0.1193 | 0.8348 | 0.9022 | 0.5652 | 27 | 30 | 0.58543-0.72489 |
| CAD | angiocad | 1 | cohort_intercepts_sigmoid | fixed_50 | 345 | 0.8280 | 0.8288 | 0.1197 | 0.8377 | 0.9819 | 0.2609 | 5 | 51 | 0.50000-0.50000 |
| CAD | angiocad | 1 | cohort_intercepts_sigmoid | target_90 | 345 | 0.8280 | 0.8288 | 0.1197 | 0.8348 | 0.9022 | 0.5652 | 27 | 30 | 0.62519-0.70073 |
| CAD | angiocad | 1 | local | fixed_50 | 345 | 0.8503 | 0.8533 | 0.1204 | 0.8261 | 1.0000 | 0.1304 | 0 | 60 | 0.50000-0.50000 |
| CAD | angiocad | 1 | local | target_90 | 345 | 0.8503 | 0.8533 | 0.1204 | 0.8174 | 0.8696 | 0.6087 | 36 | 27 | 0.68383-0.75545 |
| CAD | angiocad | 1 | local_sigmoid | fixed_50 | 345 | 0.8487 | 0.8533 | 0.1112 | 0.8493 | 0.9746 | 0.3478 | 7 | 45 | 0.50000-0.50000 |
| CAD | angiocad | 1 | local_sigmoid | target_90 | 345 | 0.8487 | 0.8533 | 0.1112 | 0.8174 | 0.8696 | 0.6087 | 36 | 27 | 0.64158-0.71170 |
| CAD | angiocad | 1 | pooled | fixed_50 | 345 | 0.8071 | 0.8115 | 0.1881 | 0.6841 | 0.6703 | 0.7391 | 91 | 18 | 0.50000-0.50000 |
| CAD | angiocad | 1 | pooled | target_90 | 345 | 0.8071 | 0.8115 | 0.1881 | 0.8377 | 0.9167 | 0.5217 | 23 | 33 | 0.30212-0.43660 |
| CAD | angiocad | 1 | pooled_sigmoid | fixed_50 | 345 | 0.8046 | 0.8115 | 0.1279 | 0.8116 | 0.9819 | 0.1304 | 5 | 60 | 0.50000-0.50000 |
| CAD | angiocad | 1 | pooled_sigmoid | target_90 | 345 | 0.8046 | 0.8115 | 0.1279 | 0.8377 | 0.9167 | 0.5217 | 23 | 33 | 0.64120-0.72638 |
| CAD | angiocad | 1 | training_prevalence | fixed_50 | 345 | 0.4928 | 0.5000 | 0.1600 | 0.8000 | 1.0000 | 0.0000 | 0 | 69 | 0.50000-0.50000 |
| CAD | angiocad | 1 | transfer_pooled | fixed_50 | 345 | 0.7889 | 0.7893 | 0.2428 | 0.5739 | 0.4891 | 0.9130 | 141 | 6 | 0.50000-0.50000 |
| CAD | angiocad | 1 | transfer_pooled | target_90 | 345 | 0.7889 | 0.7893 | 0.2428 | 0.8203 | 0.9094 | 0.4638 | 25 | 37 | 0.23239-0.32432 |
| CAD | angiocad | 1 | transfer_pooled_sigmoid | fixed_50 | 345 | 0.7870 | 0.7893 | 0.1335 | 0.8000 | 0.9819 | 0.0725 | 5 | 64 | 0.50000-0.50000 |
| CAD | angiocad | 1 | transfer_pooled_sigmoid | target_90 | 345 | 0.7870 | 0.7893 | 0.1335 | 0.8203 | 0.9094 | 0.4638 | 25 | 37 | 0.65452-0.71249 |
| CAD | angiocad | 2 | cohort_intercepts | fixed_50 | 345 | 0.8357 | 0.8335 | 0.1185 | 0.8348 | 0.9855 | 0.2319 | 4 | 53 | 0.50000-0.50000 |
| CAD | angiocad | 2 | cohort_intercepts | target_90 | 345 | 0.8357 | 0.8335 | 0.1185 | 0.8261 | 0.8841 | 0.5942 | 32 | 28 | 0.63159-0.72372 |
| CAD | angiocad | 2 | cohort_intercepts_sigmoid | fixed_50 | 345 | 0.8310 | 0.8335 | 0.1159 | 0.8377 | 0.9746 | 0.2899 | 7 | 49 | 0.50000-0.50000 |
| CAD | angiocad | 2 | cohort_intercepts_sigmoid | target_90 | 345 | 0.8310 | 0.8335 | 0.1159 | 0.8261 | 0.8841 | 0.5942 | 32 | 28 | 0.64250-0.69167 |
| CAD | angiocad | 2 | local | fixed_50 | 345 | 0.8601 | 0.8544 | 0.1197 | 0.8261 | 1.0000 | 0.1304 | 0 | 60 | 0.50000-0.50000 |
| CAD | angiocad | 2 | local | target_90 | 345 | 0.8601 | 0.8544 | 0.1197 | 0.8464 | 0.8986 | 0.6377 | 28 | 25 | 0.64891-0.75072 |
| CAD | angiocad | 2 | local_sigmoid | fixed_50 | 345 | 0.8531 | 0.8544 | 0.1095 | 0.8464 | 0.9783 | 0.3188 | 6 | 47 | 0.50000-0.50000 |
| CAD | angiocad | 2 | local_sigmoid | target_90 | 345 | 0.8531 | 0.8544 | 0.1095 | 0.8464 | 0.8986 | 0.6377 | 28 | 25 | 0.63231-0.71625 |
| CAD | angiocad | 2 | pooled | fixed_50 | 345 | 0.8098 | 0.8048 | 0.1876 | 0.7014 | 0.6812 | 0.7826 | 88 | 15 | 0.50000-0.50000 |
| CAD | angiocad | 2 | pooled | target_90 | 345 | 0.8098 | 0.8048 | 0.1876 | 0.8290 | 0.9094 | 0.5072 | 25 | 34 | 0.32388-0.41607 |
| CAD | angiocad | 2 | pooled_sigmoid | fixed_50 | 345 | 0.8092 | 0.8048 | 0.1255 | 0.8116 | 0.9855 | 0.1159 | 4 | 61 | 0.50000-0.50000 |
| CAD | angiocad | 2 | pooled_sigmoid | target_90 | 345 | 0.8092 | 0.8048 | 0.1255 | 0.8290 | 0.9094 | 0.5072 | 25 | 34 | 0.64753-0.69436 |
| CAD | angiocad | 2 | training_prevalence | fixed_50 | 345 | 0.4928 | 0.5000 | 0.1600 | 0.8000 | 1.0000 | 0.0000 | 0 | 69 | 0.50000-0.50000 |
| CAD | angiocad | 2 | transfer_pooled | fixed_50 | 345 | 0.7889 | 0.7861 | 0.2428 | 0.5739 | 0.4891 | 0.9130 | 141 | 6 | 0.50000-0.50000 |
| CAD | angiocad | 2 | transfer_pooled | target_90 | 345 | 0.7889 | 0.7861 | 0.2428 | 0.7884 | 0.8804 | 0.4203 | 33 | 40 | 0.23239-0.30569 |
| CAD | angiocad | 2 | transfer_pooled_sigmoid | fixed_50 | 345 | 0.7854 | 0.7861 | 0.1305 | 0.8203 | 0.9964 | 0.1159 | 1 | 61 | 0.50000-0.50000 |
| CAD | angiocad | 2 | transfer_pooled_sigmoid | target_90 | 345 | 0.7854 | 0.7861 | 0.1305 | 0.7884 | 0.8804 | 0.4203 | 33 | 40 | 0.64204-0.70876 |
| CAD | anhui | 1 | cohort_intercepts | fixed_50 | 553 | 0.7605 | 0.7680 | 0.1868 | 0.7089 | 0.4030 | 0.8835 | 120 | 41 | 0.50000-0.50000 |
| CAD | anhui | 1 | cohort_intercepts | target_90 | 553 | 0.7605 | 0.7680 | 0.1868 | 0.5805 | 0.9353 | 0.3778 | 13 | 219 | 0.20749-0.24874 |
| CAD | anhui | 1 | cohort_intercepts_sigmoid | fixed_50 | 553 | 0.7497 | 0.7680 | 0.1897 | 0.7089 | 0.3930 | 0.8892 | 122 | 39 | 0.50000-0.50000 |
| CAD | anhui | 1 | cohort_intercepts_sigmoid | target_90 | 553 | 0.7497 | 0.7680 | 0.1897 | 0.5805 | 0.9353 | 0.3778 | 13 | 219 | 0.20905-0.26631 |
| CAD | anhui | 1 | local | fixed_50 | 553 | 0.7705 | 0.7780 | 0.1850 | 0.7269 | 0.3980 | 0.9148 | 121 | 30 | 0.50000-0.50000 |
| CAD | anhui | 1 | local | target_90 | 553 | 0.7705 | 0.7780 | 0.1850 | 0.5931 | 0.9005 | 0.4176 | 20 | 205 | 0.22625-0.28071 |
| CAD | anhui | 1 | local_sigmoid | fixed_50 | 553 | 0.7587 | 0.7780 | 0.1871 | 0.7306 | 0.4030 | 0.9176 | 120 | 29 | 0.50000-0.50000 |
| CAD | anhui | 1 | local_sigmoid | target_90 | 553 | 0.7587 | 0.7780 | 0.1871 | 0.5931 | 0.9005 | 0.4176 | 20 | 205 | 0.20581-0.30323 |
| CAD | anhui | 1 | pooled | fixed_50 | 553 | 0.7638 | 0.7715 | 0.2297 | 0.6275 | 0.8607 | 0.4943 | 28 | 178 | 0.50000-0.50000 |
| CAD | anhui | 1 | pooled | target_90 | 553 | 0.7638 | 0.7715 | 0.2297 | 0.5805 | 0.8806 | 0.4091 | 24 | 208 | 0.41947-0.53763 |
| CAD | anhui | 1 | pooled_sigmoid | fixed_50 | 553 | 0.7524 | 0.7715 | 0.1905 | 0.6926 | 0.3731 | 0.8750 | 126 | 44 | 0.50000-0.50000 |
| CAD | anhui | 1 | pooled_sigmoid | target_90 | 553 | 0.7524 | 0.7715 | 0.1905 | 0.5805 | 0.8806 | 0.4091 | 24 | 208 | 0.20259-0.30381 |
| CAD | anhui | 1 | training_prevalence | fixed_50 | 553 | 0.4973 | 0.5000 | 0.2314 | 0.6365 | 0.0000 | 1.0000 | 201 | 0 | 0.50000-0.50000 |
| CAD | anhui | 1 | transfer_pooled | fixed_50 | 553 | 0.7374 | 0.7425 | 0.3435 | 0.4231 | 0.9900 | 0.0994 | 2 | 317 | 0.50000-0.50000 |
| CAD | anhui | 1 | transfer_pooled | target_90 | 553 | 0.7374 | 0.7425 | 0.3435 | 0.5588 | 0.9204 | 0.3523 | 16 | 228 | 0.60521-0.72616 |
| CAD | anhui | 1 | transfer_pooled_sigmoid | fixed_50 | 553 | 0.7303 | 0.7425 | 0.1956 | 0.6962 | 0.3731 | 0.8807 | 126 | 42 | 0.50000-0.50000 |
| CAD | anhui | 1 | transfer_pooled_sigmoid | target_90 | 553 | 0.7303 | 0.7425 | 0.1956 | 0.5588 | 0.9204 | 0.3523 | 16 | 228 | 0.21148-0.29829 |
| CAD | anhui | 2 | cohort_intercepts | fixed_50 | 553 | 0.7377 | 0.7389 | 0.1942 | 0.6817 | 0.3980 | 0.8438 | 121 | 55 | 0.50000-0.50000 |
| CAD | anhui | 2 | cohort_intercepts | target_90 | 553 | 0.7377 | 0.7389 | 0.1942 | 0.5967 | 0.8209 | 0.4688 | 36 | 187 | 0.24247-0.32927 |
| CAD | anhui | 2 | cohort_intercepts_sigmoid | fixed_50 | 553 | 0.7339 | 0.7389 | 0.1954 | 0.6926 | 0.3234 | 0.9034 | 136 | 34 | 0.50000-0.50000 |
| CAD | anhui | 2 | cohort_intercepts_sigmoid | target_90 | 553 | 0.7339 | 0.7389 | 0.1954 | 0.5967 | 0.8209 | 0.4688 | 36 | 187 | 0.21162-0.27393 |
| CAD | anhui | 2 | local | fixed_50 | 553 | 0.7511 | 0.7526 | 0.1941 | 0.7071 | 0.3383 | 0.9176 | 133 | 29 | 0.50000-0.50000 |
| CAD | anhui | 2 | local | target_90 | 553 | 0.7511 | 0.7526 | 0.1941 | 0.6040 | 0.8408 | 0.4688 | 32 | 187 | 0.22768-0.35408 |
| CAD | anhui | 2 | local_sigmoid | fixed_50 | 553 | 0.7459 | 0.7526 | 0.1932 | 0.7107 | 0.3582 | 0.9119 | 129 | 31 | 0.50000-0.50000 |
| CAD | anhui | 2 | local_sigmoid | target_90 | 553 | 0.7459 | 0.7526 | 0.1932 | 0.6040 | 0.8408 | 0.4688 | 32 | 187 | 0.19186-0.29234 |
| CAD | anhui | 2 | pooled | fixed_50 | 553 | 0.7375 | 0.7341 | 0.2501 | 0.5750 | 0.8856 | 0.3977 | 23 | 212 | 0.50000-0.50000 |
| CAD | anhui | 2 | pooled | target_90 | 553 | 0.7375 | 0.7341 | 0.2501 | 0.6040 | 0.8408 | 0.4688 | 32 | 187 | 0.41380-0.60473 |
| CAD | anhui | 2 | pooled_sigmoid | fixed_50 | 553 | 0.7302 | 0.7341 | 0.1974 | 0.6926 | 0.3333 | 0.8977 | 134 | 36 | 0.50000-0.50000 |
| CAD | anhui | 2 | pooled_sigmoid | target_90 | 553 | 0.7302 | 0.7341 | 0.1974 | 0.6040 | 0.8408 | 0.4688 | 32 | 187 | 0.20237-0.28219 |
| CAD | anhui | 2 | training_prevalence | fixed_50 | 553 | 0.4963 | 0.5000 | 0.2314 | 0.6365 | 0.0000 | 1.0000 | 201 | 0 | 0.50000-0.50000 |
| CAD | anhui | 2 | transfer_pooled | fixed_50 | 553 | 0.7374 | 0.7349 | 0.3435 | 0.4231 | 0.9900 | 0.0994 | 2 | 317 | 0.50000-0.50000 |
| CAD | anhui | 2 | transfer_pooled | target_90 | 553 | 0.7374 | 0.7349 | 0.3435 | 0.5859 | 0.8557 | 0.4318 | 29 | 200 | 0.64905-0.73442 |
| CAD | anhui | 2 | transfer_pooled_sigmoid | fixed_50 | 553 | 0.7320 | 0.7349 | 0.1954 | 0.6944 | 0.3234 | 0.9062 | 136 | 33 | 0.50000-0.50000 |
| CAD | anhui | 2 | transfer_pooled_sigmoid | target_90 | 553 | 0.7320 | 0.7349 | 0.1954 | 0.5859 | 0.8557 | 0.4318 | 29 | 200 | 0.17628-0.28072 |
| CAD | uci | 1 | cohort_intercepts | fixed_50 | 303 | 0.7371 | 0.7376 | 0.1744 | 0.7294 | 0.9306 | 0.2299 | 15 | 67 | 0.50000-0.50000 |
| CAD | uci | 1 | cohort_intercepts | target_90 | 303 | 0.7371 | 0.7376 | 0.1744 | 0.7294 | 0.9167 | 0.2644 | 18 | 64 | 0.44322-0.59302 |
| CAD | uci | 1 | cohort_intercepts_sigmoid | fixed_50 | 303 | 0.7433 | 0.7376 | 0.1735 | 0.7426 | 0.9398 | 0.2529 | 13 | 65 | 0.50000-0.50000 |
| CAD | uci | 1 | cohort_intercepts_sigmoid | target_90 | 303 | 0.7433 | 0.7376 | 0.1735 | 0.7294 | 0.9167 | 0.2644 | 18 | 64 | 0.43956-0.56172 |
| CAD | uci | 1 | local | fixed_50 | 303 | 0.7768 | 0.7806 | 0.1713 | 0.7360 | 0.9861 | 0.1149 | 3 | 77 | 0.50000-0.50000 |
| CAD | uci | 1 | local | target_90 | 303 | 0.7768 | 0.7806 | 0.1713 | 0.7525 | 0.8981 | 0.3908 | 22 | 53 | 0.58692-0.63085 |
| CAD | uci | 1 | local_sigmoid | fixed_50 | 303 | 0.7768 | 0.7806 | 0.1641 | 0.7492 | 0.9259 | 0.3103 | 16 | 60 | 0.50000-0.50000 |
| CAD | uci | 1 | local_sigmoid | target_90 | 303 | 0.7768 | 0.7806 | 0.1641 | 0.7525 | 0.8981 | 0.3908 | 22 | 53 | 0.49565-0.57392 |
| CAD | uci | 1 | pooled | fixed_50 | 303 | 0.7245 | 0.7329 | 0.1934 | 0.7195 | 0.8056 | 0.5057 | 42 | 43 | 0.50000-0.50000 |
| CAD | uci | 1 | pooled | target_90 | 303 | 0.7245 | 0.7329 | 0.1934 | 0.7096 | 0.9120 | 0.2069 | 19 | 69 | 0.34660-0.44619 |
| CAD | uci | 1 | pooled_sigmoid | fixed_50 | 303 | 0.7277 | 0.7329 | 0.1793 | 0.7261 | 0.9537 | 0.1609 | 10 | 73 | 0.50000-0.50000 |
| CAD | uci | 1 | pooled_sigmoid | target_90 | 303 | 0.7277 | 0.7329 | 0.1793 | 0.7096 | 0.9120 | 0.2069 | 19 | 69 | 0.50635-0.57393 |
| CAD | uci | 1 | training_prevalence | fixed_50 | 303 | 0.5037 | 0.5000 | 0.2047 | 0.7129 | 1.0000 | 0.0000 | 0 | 87 | 0.50000-0.50000 |
| CAD | uci | 1 | transfer_pooled | fixed_50 | 303 | 0.6792 | 0.6819 | 0.2152 | 0.6700 | 0.7222 | 0.5402 | 60 | 40 | 0.50000-0.50000 |
| CAD | uci | 1 | transfer_pooled | target_90 | 303 | 0.6792 | 0.6819 | 0.2152 | 0.7129 | 0.9306 | 0.1724 | 15 | 72 | 0.27715-0.35978 |
| CAD | uci | 1 | transfer_pooled_sigmoid | fixed_50 | 303 | 0.6817 | 0.6819 | 0.1893 | 0.7129 | 0.9583 | 0.1034 | 9 | 78 | 0.50000-0.50000 |
| CAD | uci | 1 | transfer_pooled_sigmoid | target_90 | 303 | 0.6817 | 0.6819 | 0.1893 | 0.7129 | 0.9306 | 0.1724 | 15 | 72 | 0.52247-0.59856 |
| CAD | uci | 2 | cohort_intercepts | fixed_50 | 303 | 0.7365 | 0.7371 | 0.1740 | 0.7360 | 0.9306 | 0.2529 | 15 | 65 | 0.50000-0.50000 |
| CAD | uci | 2 | cohort_intercepts | target_90 | 303 | 0.7365 | 0.7371 | 0.1740 | 0.7261 | 0.9120 | 0.2644 | 19 | 64 | 0.44689-0.57375 |
| CAD | uci | 2 | cohort_intercepts_sigmoid | fixed_50 | 303 | 0.7150 | 0.7371 | 0.1797 | 0.7393 | 0.9537 | 0.2069 | 10 | 69 | 0.50000-0.50000 |
| CAD | uci | 2 | cohort_intercepts_sigmoid | target_90 | 303 | 0.7150 | 0.7371 | 0.1797 | 0.7261 | 0.9120 | 0.2644 | 19 | 64 | 0.53105-0.57394 |
| CAD | uci | 2 | local | fixed_50 | 303 | 0.7984 | 0.7974 | 0.1669 | 0.7393 | 0.9907 | 0.1149 | 2 | 77 | 0.50000-0.50000 |
| CAD | uci | 2 | local | target_90 | 303 | 0.7984 | 0.7974 | 0.1669 | 0.7690 | 0.8843 | 0.4828 | 25 | 45 | 0.60210-0.64383 |
| CAD | uci | 2 | local_sigmoid | fixed_50 | 303 | 0.7899 | 0.7974 | 0.1582 | 0.7558 | 0.9213 | 0.3448 | 17 | 57 | 0.50000-0.50000 |
| CAD | uci | 2 | local_sigmoid | target_90 | 303 | 0.7899 | 0.7974 | 0.1582 | 0.7690 | 0.8843 | 0.4828 | 25 | 45 | 0.55624-0.57716 |
| CAD | uci | 2 | pooled | fixed_50 | 303 | 0.7253 | 0.7212 | 0.1932 | 0.7096 | 0.7963 | 0.4943 | 44 | 44 | 0.50000-0.50000 |
| CAD | uci | 2 | pooled | target_90 | 303 | 0.7253 | 0.7212 | 0.1932 | 0.7228 | 0.9074 | 0.2644 | 20 | 64 | 0.34918-0.44332 |
| CAD | uci | 2 | pooled_sigmoid | fixed_50 | 303 | 0.7049 | 0.7212 | 0.1836 | 0.7327 | 0.9583 | 0.1724 | 9 | 72 | 0.50000-0.50000 |
| CAD | uci | 2 | pooled_sigmoid | target_90 | 303 | 0.7049 | 0.7212 | 0.1836 | 0.7228 | 0.9074 | 0.2644 | 20 | 64 | 0.43097-0.59070 |
| CAD | uci | 2 | training_prevalence | fixed_50 | 303 | 0.4975 | 0.5000 | 0.2047 | 0.7129 | 1.0000 | 0.0000 | 0 | 87 | 0.50000-0.50000 |
| CAD | uci | 2 | transfer_pooled | fixed_50 | 303 | 0.6792 | 0.6831 | 0.2152 | 0.6700 | 0.7222 | 0.5402 | 60 | 40 | 0.50000-0.50000 |
| CAD | uci | 2 | transfer_pooled | target_90 | 303 | 0.6792 | 0.6831 | 0.2152 | 0.7030 | 0.8889 | 0.2414 | 24 | 66 | 0.30266-0.40833 |
| CAD | uci | 2 | transfer_pooled_sigmoid | fixed_50 | 303 | 0.6615 | 0.6831 | 0.1932 | 0.7195 | 0.9815 | 0.0690 | 4 | 81 | 0.50000-0.50000 |
| CAD | uci | 2 | transfer_pooled_sigmoid | target_90 | 303 | 0.6615 | 0.6831 | 0.1932 | 0.7030 | 0.8889 | 0.2414 | 24 | 66 | 0.48466-0.64534 |
| LAD | angiocad | 1 | cohort_intercepts | fixed_50 | 322 | 0.7349 | 0.7338 | 0.1762 | 0.7453 | 0.9518 | 0.2447 | 11 | 71 | 0.50000-0.50000 |
| LAD | angiocad | 1 | cohort_intercepts | target_90 | 322 | 0.7349 | 0.7338 | 0.1762 | 0.7360 | 0.8991 | 0.3404 | 23 | 62 | 0.50443-0.60458 |
| LAD | angiocad | 1 | cohort_intercepts_sigmoid | fixed_50 | 322 | 0.7244 | 0.7338 | 0.1794 | 0.7329 | 0.9649 | 0.1702 | 8 | 78 | 0.50000-0.50000 |
| LAD | angiocad | 1 | cohort_intercepts_sigmoid | target_90 | 322 | 0.7244 | 0.7338 | 0.1794 | 0.7360 | 0.8991 | 0.3404 | 23 | 62 | 0.54514-0.63168 |
| LAD | angiocad | 1 | local | fixed_50 | 322 | 0.7357 | 0.7387 | 0.1774 | 0.7484 | 0.9825 | 0.1809 | 4 | 77 | 0.50000-0.50000 |
| LAD | angiocad | 1 | local | target_90 | 322 | 0.7357 | 0.7387 | 0.1774 | 0.7578 | 0.9123 | 0.3830 | 20 | 58 | 0.54343-0.61434 |
| LAD | angiocad | 1 | local_sigmoid | fixed_50 | 322 | 0.7319 | 0.7387 | 0.1775 | 0.7453 | 0.9825 | 0.1702 | 4 | 78 | 0.50000-0.50000 |
| LAD | angiocad | 1 | local_sigmoid | target_90 | 322 | 0.7319 | 0.7387 | 0.1775 | 0.7578 | 0.9123 | 0.3830 | 20 | 58 | 0.55519-0.62065 |
| LAD | angiocad | 1 | pooled | fixed_50 | 322 | 0.7369 | 0.7357 | 0.1802 | 0.7578 | 0.8904 | 0.4362 | 25 | 53 | 0.50000-0.50000 |
| LAD | angiocad | 1 | pooled | target_90 | 322 | 0.7369 | 0.7357 | 0.1802 | 0.7609 | 0.8947 | 0.4362 | 24 | 53 | 0.42566-0.54058 |
| LAD | angiocad | 1 | pooled_sigmoid | fixed_50 | 322 | 0.7257 | 0.7357 | 0.1788 | 0.7360 | 0.9649 | 0.1809 | 8 | 77 | 0.50000-0.50000 |
| LAD | angiocad | 1 | pooled_sigmoid | target_90 | 322 | 0.7257 | 0.7357 | 0.1788 | 0.7609 | 0.8947 | 0.4362 | 24 | 53 | 0.56914-0.64893 |
| LAD | angiocad | 1 | training_prevalence | fixed_50 | 322 | 0.4953 | 0.5000 | 0.2067 | 0.7081 | 1.0000 | 0.0000 | 0 | 94 | 0.50000-0.50000 |
| LAD | angiocad | 1 | transfer_pooled | fixed_50 | 322 | 0.7225 | 0.7234 | 0.1960 | 0.6957 | 0.7456 | 0.5745 | 58 | 40 | 0.50000-0.50000 |
| LAD | angiocad | 1 | transfer_pooled | target_90 | 322 | 0.7225 | 0.7234 | 0.1960 | 0.7391 | 0.8991 | 0.3511 | 23 | 61 | 0.35465-0.45211 |
| LAD | angiocad | 1 | transfer_pooled_sigmoid | fixed_50 | 322 | 0.7078 | 0.7234 | 0.1837 | 0.7360 | 0.9737 | 0.1596 | 6 | 79 | 0.50000-0.50000 |
| LAD | angiocad | 1 | transfer_pooled_sigmoid | target_90 | 322 | 0.7078 | 0.7234 | 0.1837 | 0.7391 | 0.8991 | 0.3511 | 23 | 61 | 0.58548-0.63874 |
| LAD | angiocad | 2 | cohort_intercepts | fixed_50 | 322 | 0.7234 | 0.7329 | 0.1774 | 0.7609 | 0.9561 | 0.2872 | 10 | 67 | 0.50000-0.50000 |
| LAD | angiocad | 2 | cohort_intercepts | target_90 | 322 | 0.7234 | 0.7329 | 0.1774 | 0.7857 | 0.9386 | 0.4149 | 14 | 55 | 0.53550-0.58403 |
| LAD | angiocad | 2 | cohort_intercepts_sigmoid | fixed_50 | 322 | 0.7151 | 0.7329 | 0.1811 | 0.7360 | 0.9781 | 0.1489 | 5 | 80 | 0.50000-0.50000 |
| LAD | angiocad | 2 | cohort_intercepts_sigmoid | target_90 | 322 | 0.7151 | 0.7329 | 0.1811 | 0.7857 | 0.9386 | 0.4149 | 14 | 55 | 0.52391-0.60819 |
| LAD | angiocad | 2 | local | fixed_50 | 322 | 0.7283 | 0.7299 | 0.1775 | 0.7547 | 0.9868 | 0.1915 | 3 | 76 | 0.50000-0.50000 |
| LAD | angiocad | 2 | local | target_90 | 322 | 0.7283 | 0.7299 | 0.1775 | 0.7764 | 0.9211 | 0.4255 | 18 | 54 | 0.55329-0.62612 |
| LAD | angiocad | 2 | local_sigmoid | fixed_50 | 322 | 0.7274 | 0.7299 | 0.1762 | 0.7516 | 0.9649 | 0.2340 | 8 | 72 | 0.50000-0.50000 |
| LAD | angiocad | 2 | local_sigmoid | target_90 | 322 | 0.7274 | 0.7299 | 0.1762 | 0.7764 | 0.9211 | 0.4255 | 18 | 54 | 0.50713-0.62464 |
| LAD | angiocad | 2 | pooled | fixed_50 | 322 | 0.7257 | 0.7339 | 0.1818 | 0.7857 | 0.9123 | 0.4787 | 20 | 49 | 0.50000-0.50000 |
| LAD | angiocad | 2 | pooled | target_90 | 322 | 0.7257 | 0.7339 | 0.1818 | 0.7919 | 0.9298 | 0.4574 | 16 | 51 | 0.47390-0.50400 |
| LAD | angiocad | 2 | pooled_sigmoid | fixed_50 | 322 | 0.7187 | 0.7339 | 0.1807 | 0.7391 | 0.9781 | 0.1596 | 5 | 79 | 0.50000-0.50000 |
| LAD | angiocad | 2 | pooled_sigmoid | target_90 | 322 | 0.7187 | 0.7339 | 0.1807 | 0.7919 | 0.9298 | 0.4574 | 16 | 51 | 0.54230-0.61383 |
| LAD | angiocad | 2 | training_prevalence | fixed_50 | 322 | 0.4940 | 0.5000 | 0.2067 | 0.7081 | 1.0000 | 0.0000 | 0 | 94 | 0.50000-0.50000 |
| LAD | angiocad | 2 | transfer_pooled | fixed_50 | 322 | 0.7225 | 0.7301 | 0.1960 | 0.6957 | 0.7456 | 0.5745 | 58 | 40 | 0.50000-0.50000 |
| LAD | angiocad | 2 | transfer_pooled | target_90 | 322 | 0.7225 | 0.7301 | 0.1960 | 0.7298 | 0.8816 | 0.3617 | 27 | 60 | 0.41023-0.45118 |
| LAD | angiocad | 2 | transfer_pooled_sigmoid | fixed_50 | 322 | 0.7003 | 0.7301 | 0.1861 | 0.7267 | 0.9693 | 0.1383 | 7 | 81 | 0.50000-0.50000 |
| LAD | angiocad | 2 | transfer_pooled_sigmoid | target_90 | 322 | 0.7003 | 0.7301 | 0.1861 | 0.7298 | 0.8816 | 0.3617 | 27 | 60 | 0.54707-0.62878 |
| LAD | uci | 1 | cohort_intercepts | fixed_50 | 303 | 0.6991 | 0.6953 | 0.2147 | 0.6502 | 0.8136 | 0.4206 | 33 | 73 | 0.50000-0.50000 |
| LAD | uci | 1 | cohort_intercepts | target_90 | 303 | 0.6991 | 0.6953 | 0.2147 | 0.6568 | 0.8814 | 0.3413 | 21 | 83 | 0.41156-0.47839 |
| LAD | uci | 1 | cohort_intercepts_sigmoid | fixed_50 | 303 | 0.7028 | 0.6953 | 0.2124 | 0.6469 | 0.7910 | 0.4444 | 37 | 70 | 0.50000-0.50000 |
| LAD | uci | 1 | cohort_intercepts_sigmoid | target_90 | 303 | 0.7028 | 0.6953 | 0.2124 | 0.6568 | 0.8814 | 0.3413 | 21 | 83 | 0.40894-0.48492 |
| LAD | uci | 1 | local | fixed_50 | 303 | 0.7055 | 0.7058 | 0.2161 | 0.6601 | 0.8418 | 0.4048 | 28 | 75 | 0.50000-0.50000 |
| LAD | uci | 1 | local | target_90 | 303 | 0.7055 | 0.7058 | 0.2161 | 0.6667 | 0.8079 | 0.4683 | 34 | 67 | 0.46422-0.56033 |
| LAD | uci | 1 | local_sigmoid | fixed_50 | 303 | 0.7078 | 0.7058 | 0.2122 | 0.6667 | 0.7571 | 0.5397 | 43 | 58 | 0.50000-0.50000 |
| LAD | uci | 1 | local_sigmoid | target_90 | 303 | 0.7078 | 0.7058 | 0.2122 | 0.6667 | 0.8079 | 0.4683 | 34 | 67 | 0.43357-0.51438 |
| LAD | uci | 1 | pooled | fixed_50 | 303 | 0.6965 | 0.6910 | 0.2204 | 0.6403 | 0.9153 | 0.2540 | 15 | 94 | 0.50000-0.50000 |
| LAD | uci | 1 | pooled | target_90 | 303 | 0.6965 | 0.6910 | 0.2204 | 0.6535 | 0.8701 | 0.3492 | 23 | 82 | 0.48337-0.56022 |
| LAD | uci | 1 | pooled_sigmoid | fixed_50 | 303 | 0.6967 | 0.6910 | 0.2142 | 0.6469 | 0.8136 | 0.4127 | 33 | 74 | 0.50000-0.50000 |
| LAD | uci | 1 | pooled_sigmoid | target_90 | 303 | 0.6967 | 0.6910 | 0.2142 | 0.6535 | 0.8701 | 0.3492 | 23 | 82 | 0.42823-0.50045 |
| LAD | uci | 1 | training_prevalence | fixed_50 | 303 | 0.4935 | 0.5000 | 0.2430 | 0.5842 | 1.0000 | 0.0000 | 0 | 126 | 0.50000-0.50000 |
| LAD | uci | 1 | transfer_pooled | fixed_50 | 303 | 0.6541 | 0.6479 | 0.2409 | 0.6106 | 0.9209 | 0.1746 | 14 | 104 | 0.50000-0.50000 |
| LAD | uci | 1 | transfer_pooled | target_90 | 303 | 0.6541 | 0.6479 | 0.2409 | 0.6205 | 0.8814 | 0.2540 | 21 | 94 | 0.48379-0.60807 |
| LAD | uci | 1 | transfer_pooled_sigmoid | fixed_50 | 303 | 0.6537 | 0.6479 | 0.2273 | 0.6337 | 0.8531 | 0.3254 | 26 | 85 | 0.50000-0.50000 |
| LAD | uci | 1 | transfer_pooled_sigmoid | target_90 | 303 | 0.6537 | 0.6479 | 0.2273 | 0.6205 | 0.8814 | 0.2540 | 21 | 94 | 0.43917-0.50630 |
| LAD | uci | 2 | cohort_intercepts | fixed_50 | 303 | 0.6838 | 0.6851 | 0.2170 | 0.6436 | 0.7966 | 0.4286 | 36 | 72 | 0.50000-0.50000 |
| LAD | uci | 2 | cohort_intercepts | target_90 | 303 | 0.6838 | 0.6851 | 0.2170 | 0.6436 | 0.9379 | 0.2302 | 11 | 97 | 0.34361-0.47009 |
| LAD | uci | 2 | cohort_intercepts_sigmoid | fixed_50 | 303 | 0.6865 | 0.6851 | 0.2172 | 0.6436 | 0.8531 | 0.3492 | 26 | 82 | 0.50000-0.50000 |
| LAD | uci | 2 | cohort_intercepts_sigmoid | target_90 | 303 | 0.6865 | 0.6851 | 0.2172 | 0.6436 | 0.9379 | 0.2302 | 11 | 97 | 0.39301-0.47763 |
| LAD | uci | 2 | local | fixed_50 | 303 | 0.6890 | 0.6923 | 0.2179 | 0.6436 | 0.8023 | 0.4206 | 35 | 73 | 0.50000-0.50000 |
| LAD | uci | 2 | local | target_90 | 303 | 0.6890 | 0.6923 | 0.2179 | 0.6304 | 0.9548 | 0.1746 | 8 | 104 | 0.39349-0.46816 |
| LAD | uci | 2 | local_sigmoid | fixed_50 | 303 | 0.6907 | 0.6923 | 0.2177 | 0.6568 | 0.8757 | 0.3492 | 22 | 82 | 0.50000-0.50000 |
| LAD | uci | 2 | local_sigmoid | target_90 | 303 | 0.6907 | 0.6923 | 0.2177 | 0.6304 | 0.9548 | 0.1746 | 8 | 104 | 0.41155-0.45779 |
| LAD | uci | 2 | pooled | fixed_50 | 303 | 0.6826 | 0.6858 | 0.2219 | 0.6337 | 0.8983 | 0.2619 | 18 | 93 | 0.50000-0.50000 |
| LAD | uci | 2 | pooled | target_90 | 303 | 0.6826 | 0.6858 | 0.2219 | 0.6436 | 0.9322 | 0.2381 | 12 | 96 | 0.43450-0.54257 |
| LAD | uci | 2 | pooled_sigmoid | fixed_50 | 303 | 0.6831 | 0.6858 | 0.2182 | 0.6469 | 0.8531 | 0.3571 | 26 | 81 | 0.50000-0.50000 |
| LAD | uci | 2 | pooled_sigmoid | target_90 | 303 | 0.6831 | 0.6858 | 0.2182 | 0.6436 | 0.9322 | 0.2381 | 12 | 96 | 0.39071-0.46926 |
| LAD | uci | 2 | training_prevalence | fixed_50 | 303 | 0.4935 | 0.5000 | 0.2430 | 0.5842 | 1.0000 | 0.0000 | 0 | 126 | 0.50000-0.50000 |
| LAD | uci | 2 | transfer_pooled | fixed_50 | 303 | 0.6541 | 0.6568 | 0.2409 | 0.6106 | 0.9209 | 0.1746 | 14 | 104 | 0.50000-0.50000 |
| LAD | uci | 2 | transfer_pooled | target_90 | 303 | 0.6541 | 0.6568 | 0.2409 | 0.6106 | 0.9379 | 0.1508 | 11 | 107 | 0.45286-0.55085 |
| LAD | uci | 2 | transfer_pooled_sigmoid | fixed_50 | 303 | 0.6538 | 0.6568 | 0.2275 | 0.6337 | 0.8983 | 0.2619 | 18 | 93 | 0.50000-0.50000 |
| LAD | uci | 2 | transfer_pooled_sigmoid | target_90 | 303 | 0.6538 | 0.6568 | 0.2275 | 0.6106 | 0.9379 | 0.1508 | 11 | 107 | 0.42982-0.52213 |
| LCX | angiocad | 1 | cohort_intercepts | fixed_50 | 331 | 0.7124 | 0.7064 | 0.1777 | 0.7372 | 0.1778 | 0.9461 | 74 | 13 | 0.50000-0.50000 |
| LCX | angiocad | 1 | cohort_intercepts | target_90 | 331 | 0.7124 | 0.7064 | 0.1777 | 0.4532 | 0.9000 | 0.2863 | 9 | 172 | 0.12938-0.20745 |
| LCX | angiocad | 1 | cohort_intercepts_sigmoid | fixed_50 | 331 | 0.7036 | 0.7064 | 0.1825 | 0.7281 | 0.1556 | 0.9419 | 76 | 14 | 0.50000-0.50000 |
| LCX | angiocad | 1 | cohort_intercepts_sigmoid | target_90 | 331 | 0.7036 | 0.7064 | 0.1825 | 0.4532 | 0.9000 | 0.2863 | 9 | 172 | 0.13764-0.20758 |
| LCX | angiocad | 1 | local | fixed_50 | 331 | 0.7082 | 0.7116 | 0.1796 | 0.7311 | 0.0667 | 0.9793 | 84 | 5 | 0.50000-0.50000 |
| LCX | angiocad | 1 | local | target_90 | 331 | 0.7082 | 0.7116 | 0.1796 | 0.4743 | 0.9222 | 0.3071 | 7 | 167 | 0.17174-0.22688 |
| LCX | angiocad | 1 | local_sigmoid | fixed_50 | 331 | 0.7005 | 0.7116 | 0.1815 | 0.7281 | 0.0889 | 0.9668 | 82 | 8 | 0.50000-0.50000 |
| LCX | angiocad | 1 | local_sigmoid | target_90 | 331 | 0.7005 | 0.7116 | 0.1815 | 0.4743 | 0.9222 | 0.3071 | 7 | 167 | 0.14629-0.21063 |
| LCX | angiocad | 1 | pooled | fixed_50 | 331 | 0.7158 | 0.7137 | 0.1786 | 0.7281 | 0.2222 | 0.9170 | 70 | 20 | 0.50000-0.50000 |
| LCX | angiocad | 1 | pooled | target_90 | 331 | 0.7158 | 0.7137 | 0.1786 | 0.4622 | 0.9333 | 0.2863 | 6 | 172 | 0.17068-0.22270 |
| LCX | angiocad | 1 | pooled_sigmoid | fixed_50 | 331 | 0.7096 | 0.7137 | 0.1806 | 0.7251 | 0.1333 | 0.9461 | 78 | 13 | 0.50000-0.50000 |
| LCX | angiocad | 1 | pooled_sigmoid | target_90 | 331 | 0.7096 | 0.7137 | 0.1806 | 0.4622 | 0.9333 | 0.2863 | 6 | 172 | 0.13942-0.20541 |
| LCX | angiocad | 1 | training_prevalence | fixed_50 | 331 | 0.4996 | 0.5000 | 0.1980 | 0.7281 | 0.0000 | 1.0000 | 90 | 0 | 0.50000-0.50000 |
| LCX | angiocad | 1 | transfer_pooled | fixed_50 | 331 | 0.7087 | 0.7046 | 0.1910 | 0.7251 | 0.4000 | 0.8465 | 54 | 37 | 0.50000-0.50000 |
| LCX | angiocad | 1 | transfer_pooled | target_90 | 331 | 0.7087 | 0.7046 | 0.1910 | 0.4230 | 0.8889 | 0.2490 | 10 | 181 | 0.19621-0.33633 |
| LCX | angiocad | 1 | transfer_pooled_sigmoid | fixed_50 | 331 | 0.6993 | 0.7046 | 0.1869 | 0.7251 | 0.1444 | 0.9419 | 77 | 14 | 0.50000-0.50000 |
| LCX | angiocad | 1 | transfer_pooled_sigmoid | target_90 | 331 | 0.6993 | 0.7046 | 0.1869 | 0.4230 | 0.8889 | 0.2490 | 10 | 181 | 0.14180-0.21360 |
| LCX | angiocad | 2 | cohort_intercepts | fixed_50 | 331 | 0.7011 | 0.7090 | 0.1791 | 0.7372 | 0.2000 | 0.9378 | 72 | 15 | 0.50000-0.50000 |
| LCX | angiocad | 2 | cohort_intercepts | target_90 | 331 | 0.7011 | 0.7090 | 0.1791 | 0.4834 | 0.8667 | 0.3402 | 12 | 159 | 0.16876-0.18234 |
| LCX | angiocad | 2 | cohort_intercepts_sigmoid | fixed_50 | 331 | 0.6952 | 0.7090 | 0.1800 | 0.7311 | 0.1667 | 0.9419 | 75 | 14 | 0.50000-0.50000 |
| LCX | angiocad | 2 | cohort_intercepts_sigmoid | target_90 | 331 | 0.6952 | 0.7090 | 0.1800 | 0.4834 | 0.8667 | 0.3402 | 12 | 159 | 0.16736-0.20645 |
| LCX | angiocad | 2 | local | fixed_50 | 331 | 0.6794 | 0.6872 | 0.1830 | 0.7341 | 0.1000 | 0.9710 | 81 | 7 | 0.50000-0.50000 |
| LCX | angiocad | 2 | local | target_90 | 331 | 0.6794 | 0.6872 | 0.1830 | 0.5045 | 0.8556 | 0.3734 | 13 | 151 | 0.18670-0.22145 |
| LCX | angiocad | 2 | local_sigmoid | fixed_50 | 331 | 0.6766 | 0.6872 | 0.1834 | 0.7341 | 0.1111 | 0.9668 | 80 | 8 | 0.50000-0.50000 |
| LCX | angiocad | 2 | local_sigmoid | target_90 | 331 | 0.6766 | 0.6872 | 0.1834 | 0.5045 | 0.8556 | 0.3734 | 13 | 151 | 0.18806-0.21231 |
| LCX | angiocad | 2 | pooled | fixed_50 | 331 | 0.7064 | 0.7120 | 0.1803 | 0.7281 | 0.2444 | 0.9087 | 68 | 22 | 0.50000-0.50000 |
| LCX | angiocad | 2 | pooled | target_90 | 331 | 0.7064 | 0.7120 | 0.1803 | 0.4864 | 0.8667 | 0.3444 | 12 | 158 | 0.20815-0.21500 |
| LCX | angiocad | 2 | pooled_sigmoid | fixed_50 | 331 | 0.7005 | 0.7120 | 0.1790 | 0.7341 | 0.1778 | 0.9419 | 74 | 14 | 0.50000-0.50000 |
| LCX | angiocad | 2 | pooled_sigmoid | target_90 | 331 | 0.7005 | 0.7120 | 0.1790 | 0.4864 | 0.8667 | 0.3444 | 12 | 158 | 0.16283-0.20089 |
| LCX | angiocad | 2 | training_prevalence | fixed_50 | 331 | 0.5000 | 0.5000 | 0.1980 | 0.7281 | 0.0000 | 1.0000 | 90 | 0 | 0.50000-0.50000 |
| LCX | angiocad | 2 | transfer_pooled | fixed_50 | 331 | 0.7087 | 0.7090 | 0.1910 | 0.7251 | 0.4000 | 0.8465 | 54 | 37 | 0.50000-0.50000 |
| LCX | angiocad | 2 | transfer_pooled | target_90 | 331 | 0.7087 | 0.7090 | 0.1910 | 0.4350 | 0.8778 | 0.2697 | 11 | 176 | 0.22075-0.28530 |
| LCX | angiocad | 2 | transfer_pooled_sigmoid | fixed_50 | 331 | 0.7090 | 0.7090 | 0.1790 | 0.7281 | 0.1222 | 0.9544 | 79 | 11 | 0.50000-0.50000 |
| LCX | angiocad | 2 | transfer_pooled_sigmoid | target_90 | 331 | 0.7090 | 0.7090 | 0.1790 | 0.4350 | 0.8778 | 0.2697 | 11 | 176 | 0.16133-0.19860 |
| LCX | uci | 1 | cohort_intercepts | fixed_50 | 303 | 0.7235 | 0.7285 | 0.2068 | 0.6832 | 0.3950 | 0.8696 | 72 | 24 | 0.50000-0.50000 |
| LCX | uci | 1 | cohort_intercepts | target_90 | 303 | 0.7235 | 0.7285 | 0.2068 | 0.5578 | 0.8655 | 0.3587 | 16 | 118 | 0.25085-0.33991 |
| LCX | uci | 1 | cohort_intercepts_sigmoid | fixed_50 | 303 | 0.7221 | 0.7285 | 0.2052 | 0.6832 | 0.4370 | 0.8424 | 67 | 29 | 0.50000-0.50000 |
| LCX | uci | 1 | cohort_intercepts_sigmoid | target_90 | 303 | 0.7221 | 0.7285 | 0.2052 | 0.5578 | 0.8655 | 0.3587 | 16 | 118 | 0.19475-0.31198 |
| LCX | uci | 1 | local | fixed_50 | 303 | 0.7074 | 0.7110 | 0.2117 | 0.6766 | 0.3529 | 0.8859 | 77 | 21 | 0.50000-0.50000 |
| LCX | uci | 1 | local | target_90 | 303 | 0.7074 | 0.7110 | 0.2117 | 0.5743 | 0.8403 | 0.4022 | 19 | 110 | 0.28858-0.34523 |
| LCX | uci | 1 | local_sigmoid | fixed_50 | 303 | 0.7022 | 0.7110 | 0.2108 | 0.6733 | 0.4034 | 0.8478 | 71 | 28 | 0.50000-0.50000 |
| LCX | uci | 1 | local_sigmoid | target_90 | 303 | 0.7022 | 0.7110 | 0.2108 | 0.5743 | 0.8403 | 0.4022 | 19 | 110 | 0.25572-0.34182 |
| LCX | uci | 1 | pooled | fixed_50 | 303 | 0.7189 | 0.7191 | 0.2107 | 0.6403 | 0.2353 | 0.9022 | 91 | 18 | 0.50000-0.50000 |
| LCX | uci | 1 | pooled | target_90 | 303 | 0.7189 | 0.7191 | 0.2107 | 0.5677 | 0.8739 | 0.3696 | 15 | 116 | 0.19987-0.28180 |
| LCX | uci | 1 | pooled_sigmoid | fixed_50 | 303 | 0.7181 | 0.7191 | 0.2062 | 0.6832 | 0.4286 | 0.8478 | 68 | 28 | 0.50000-0.50000 |
| LCX | uci | 1 | pooled_sigmoid | target_90 | 303 | 0.7181 | 0.7191 | 0.2062 | 0.5677 | 0.8739 | 0.3696 | 15 | 116 | 0.18900-0.29448 |
| LCX | uci | 1 | training_prevalence | fixed_50 | 303 | 0.4945 | 0.5000 | 0.2385 | 0.6073 | 0.0000 | 1.0000 | 119 | 0 | 0.50000-0.50000 |
| LCX | uci | 1 | transfer_pooled | fixed_50 | 303 | 0.6916 | 0.6945 | 0.2252 | 0.6238 | 0.0672 | 0.9837 | 111 | 3 | 0.50000-0.50000 |
| LCX | uci | 1 | transfer_pooled | target_90 | 303 | 0.6916 | 0.6945 | 0.2252 | 0.5677 | 0.8151 | 0.4076 | 22 | 109 | 0.20236-0.25658 |
| LCX | uci | 1 | transfer_pooled_sigmoid | fixed_50 | 303 | 0.6815 | 0.6945 | 0.2158 | 0.6304 | 0.3277 | 0.8261 | 80 | 32 | 0.50000-0.50000 |
| LCX | uci | 1 | transfer_pooled_sigmoid | target_90 | 303 | 0.6815 | 0.6945 | 0.2158 | 0.5677 | 0.8151 | 0.4076 | 22 | 109 | 0.25124-0.33448 |
| LCX | uci | 2 | cohort_intercepts | fixed_50 | 303 | 0.7247 | 0.7258 | 0.2064 | 0.6931 | 0.4118 | 0.8750 | 70 | 23 | 0.50000-0.50000 |
| LCX | uci | 2 | cohort_intercepts | target_90 | 303 | 0.7247 | 0.7258 | 0.2064 | 0.5809 | 0.8571 | 0.4022 | 17 | 110 | 0.23821-0.34380 |
| LCX | uci | 2 | cohort_intercepts_sigmoid | fixed_50 | 303 | 0.7216 | 0.7258 | 0.2054 | 0.6799 | 0.4454 | 0.8315 | 66 | 31 | 0.50000-0.50000 |
| LCX | uci | 2 | cohort_intercepts_sigmoid | target_90 | 303 | 0.7216 | 0.7258 | 0.2054 | 0.5809 | 0.8571 | 0.4022 | 17 | 110 | 0.19619-0.31409 |
| LCX | uci | 2 | local | fixed_50 | 303 | 0.7106 | 0.7194 | 0.2101 | 0.6865 | 0.3277 | 0.9185 | 80 | 15 | 0.50000-0.50000 |
| LCX | uci | 2 | local | target_90 | 303 | 0.7106 | 0.7194 | 0.2101 | 0.5710 | 0.8235 | 0.4076 | 21 | 109 | 0.26035-0.33820 |
| LCX | uci | 2 | local_sigmoid | fixed_50 | 303 | 0.7104 | 0.7194 | 0.2069 | 0.6931 | 0.4454 | 0.8533 | 66 | 27 | 0.50000-0.50000 |
| LCX | uci | 2 | local_sigmoid | target_90 | 303 | 0.7104 | 0.7194 | 0.2069 | 0.5710 | 0.8235 | 0.4076 | 21 | 109 | 0.21691-0.31227 |
| LCX | uci | 2 | pooled | fixed_50 | 303 | 0.7225 | 0.7228 | 0.2099 | 0.6502 | 0.2437 | 0.9130 | 90 | 16 | 0.50000-0.50000 |
| LCX | uci | 2 | pooled | target_90 | 303 | 0.7225 | 0.7228 | 0.2099 | 0.5776 | 0.8487 | 0.4022 | 18 | 110 | 0.19877-0.29804 |
| LCX | uci | 2 | pooled_sigmoid | fixed_50 | 303 | 0.7178 | 0.7228 | 0.2062 | 0.6700 | 0.4286 | 0.8261 | 68 | 32 | 0.50000-0.50000 |
| LCX | uci | 2 | pooled_sigmoid | target_90 | 303 | 0.7178 | 0.7228 | 0.2062 | 0.5776 | 0.8487 | 0.4022 | 18 | 110 | 0.19961-0.31717 |
| LCX | uci | 2 | training_prevalence | fixed_50 | 303 | 0.4945 | 0.5000 | 0.2385 | 0.6073 | 0.0000 | 1.0000 | 119 | 0 | 0.50000-0.50000 |
| LCX | uci | 2 | transfer_pooled | fixed_50 | 303 | 0.6916 | 0.6900 | 0.2252 | 0.6238 | 0.0672 | 0.9837 | 111 | 3 | 0.50000-0.50000 |
| LCX | uci | 2 | transfer_pooled | target_90 | 303 | 0.6916 | 0.6900 | 0.2252 | 0.5875 | 0.8908 | 0.3913 | 13 | 112 | 0.21065-0.23954 |
| LCX | uci | 2 | transfer_pooled_sigmoid | fixed_50 | 303 | 0.6897 | 0.6900 | 0.2139 | 0.6337 | 0.3193 | 0.8370 | 81 | 30 | 0.50000-0.50000 |
| LCX | uci | 2 | transfer_pooled_sigmoid | target_90 | 303 | 0.6897 | 0.6900 | 0.2139 | 0.5875 | 0.8908 | 0.3913 | 13 | 112 | 0.26044-0.33432 |
| RCA | angiocad | 1 | cohort_intercepts | fixed_50 | 326 | 0.6992 | 0.7107 | 0.2224 | 0.6411 | 0.5613 | 0.7135 | 68 | 49 | 0.50000-0.50000 |
| RCA | angiocad | 1 | cohort_intercepts | target_90 | 326 | 0.6992 | 0.7107 | 0.2224 | 0.6350 | 0.9226 | 0.3743 | 12 | 107 | 0.31404-0.38857 |
| RCA | angiocad | 1 | cohort_intercepts_sigmoid | fixed_50 | 326 | 0.7003 | 0.7107 | 0.2226 | 0.6288 | 0.5161 | 0.7310 | 75 | 46 | 0.50000-0.50000 |
| RCA | angiocad | 1 | cohort_intercepts_sigmoid | target_90 | 326 | 0.7003 | 0.7107 | 0.2226 | 0.6350 | 0.9226 | 0.3743 | 12 | 107 | 0.33022-0.39192 |
| RCA | angiocad | 1 | local | fixed_50 | 326 | 0.6972 | 0.7097 | 0.2216 | 0.6258 | 0.5484 | 0.6959 | 70 | 52 | 0.50000-0.50000 |
| RCA | angiocad | 1 | local | target_90 | 326 | 0.6972 | 0.7097 | 0.2216 | 0.6258 | 0.9161 | 0.3626 | 13 | 109 | 0.32517-0.38084 |
| RCA | angiocad | 1 | local_sigmoid | fixed_50 | 326 | 0.6890 | 0.7097 | 0.2232 | 0.6012 | 0.4968 | 0.6959 | 78 | 52 | 0.50000-0.50000 |
| RCA | angiocad | 1 | local_sigmoid | target_90 | 326 | 0.6890 | 0.7097 | 0.2232 | 0.6258 | 0.9161 | 0.3626 | 13 | 109 | 0.31103-0.38695 |
| RCA | angiocad | 1 | pooled | fixed_50 | 326 | 0.6995 | 0.7093 | 0.2270 | 0.6074 | 0.4194 | 0.7778 | 90 | 38 | 0.50000-0.50000 |
| RCA | angiocad | 1 | pooled | target_90 | 326 | 0.6995 | 0.7093 | 0.2270 | 0.6472 | 0.9161 | 0.4035 | 13 | 102 | 0.26835-0.32806 |
| RCA | angiocad | 1 | pooled_sigmoid | fixed_50 | 326 | 0.7003 | 0.7093 | 0.2242 | 0.6350 | 0.5161 | 0.7427 | 75 | 44 | 0.50000-0.50000 |
| RCA | angiocad | 1 | pooled_sigmoid | target_90 | 326 | 0.7003 | 0.7093 | 0.2242 | 0.6472 | 0.9161 | 0.4035 | 13 | 102 | 0.33295-0.39260 |
| RCA | angiocad | 1 | training_prevalence | fixed_50 | 326 | 0.5000 | 0.5000 | 0.2494 | 0.5245 | 0.0000 | 1.0000 | 155 | 0 | 0.50000-0.50000 |
| RCA | angiocad | 1 | transfer_pooled | fixed_50 | 326 | 0.6869 | 0.6886 | 0.2336 | 0.5859 | 0.3161 | 0.8304 | 106 | 29 | 0.50000-0.50000 |
| RCA | angiocad | 1 | transfer_pooled | target_90 | 326 | 0.6869 | 0.6886 | 0.2336 | 0.6135 | 0.9161 | 0.3392 | 13 | 113 | 0.25261-0.33234 |
| RCA | angiocad | 1 | transfer_pooled_sigmoid | fixed_50 | 326 | 0.6838 | 0.6886 | 0.2277 | 0.6104 | 0.4516 | 0.7544 | 85 | 42 | 0.50000-0.50000 |
| RCA | angiocad | 1 | transfer_pooled_sigmoid | target_90 | 326 | 0.6838 | 0.6886 | 0.2277 | 0.6135 | 0.9161 | 0.3392 | 13 | 113 | 0.33364-0.38278 |
| RCA | angiocad | 2 | cohort_intercepts | fixed_50 | 326 | 0.6917 | 0.6951 | 0.2253 | 0.6350 | 0.5677 | 0.6959 | 67 | 52 | 0.50000-0.50000 |
| RCA | angiocad | 2 | cohort_intercepts | target_90 | 326 | 0.6917 | 0.6951 | 0.2253 | 0.6135 | 0.8387 | 0.4094 | 25 | 101 | 0.33291-0.39979 |
| RCA | angiocad | 2 | cohort_intercepts_sigmoid | fixed_50 | 326 | 0.6851 | 0.6951 | 0.2285 | 0.6380 | 0.5097 | 0.7544 | 76 | 42 | 0.50000-0.50000 |
| RCA | angiocad | 2 | cohort_intercepts_sigmoid | target_90 | 326 | 0.6851 | 0.6951 | 0.2285 | 0.6135 | 0.8387 | 0.4094 | 25 | 101 | 0.36196-0.37854 |
| RCA | angiocad | 2 | local | fixed_50 | 326 | 0.6839 | 0.6889 | 0.2251 | 0.6380 | 0.5935 | 0.6784 | 63 | 55 | 0.50000-0.50000 |
| RCA | angiocad | 2 | local | target_90 | 326 | 0.6839 | 0.6889 | 0.2251 | 0.5951 | 0.8581 | 0.3567 | 22 | 110 | 0.31752-0.41656 |
| RCA | angiocad | 2 | local_sigmoid | fixed_50 | 326 | 0.6778 | 0.6889 | 0.2277 | 0.6258 | 0.5097 | 0.7310 | 76 | 46 | 0.50000-0.50000 |
| RCA | angiocad | 2 | local_sigmoid | target_90 | 326 | 0.6778 | 0.6889 | 0.2277 | 0.5951 | 0.8581 | 0.3567 | 22 | 110 | 0.31359-0.41450 |
| RCA | angiocad | 2 | pooled | fixed_50 | 326 | 0.6929 | 0.6934 | 0.2295 | 0.6227 | 0.4387 | 0.7895 | 87 | 36 | 0.50000-0.50000 |
| RCA | angiocad | 2 | pooled | target_90 | 326 | 0.6929 | 0.6934 | 0.2295 | 0.6196 | 0.8387 | 0.4211 | 25 | 99 | 0.28659-0.35155 |
| RCA | angiocad | 2 | pooled_sigmoid | fixed_50 | 326 | 0.6856 | 0.6934 | 0.2293 | 0.6350 | 0.4968 | 0.7602 | 78 | 41 | 0.50000-0.50000 |
| RCA | angiocad | 2 | pooled_sigmoid | target_90 | 326 | 0.6856 | 0.6934 | 0.2293 | 0.6196 | 0.8387 | 0.4211 | 25 | 99 | 0.33512-0.38084 |
| RCA | angiocad | 2 | training_prevalence | fixed_50 | 326 | 0.4988 | 0.5000 | 0.2494 | 0.5245 | 0.0000 | 1.0000 | 155 | 0 | 0.50000-0.50000 |
| RCA | angiocad | 2 | transfer_pooled | fixed_50 | 326 | 0.6869 | 0.6895 | 0.2336 | 0.5859 | 0.3161 | 0.8304 | 106 | 29 | 0.50000-0.50000 |
| RCA | angiocad | 2 | transfer_pooled | target_90 | 326 | 0.6869 | 0.6895 | 0.2336 | 0.6012 | 0.8516 | 0.3743 | 23 | 107 | 0.27865-0.32111 |
| RCA | angiocad | 2 | transfer_pooled_sigmoid | fixed_50 | 326 | 0.6850 | 0.6895 | 0.2286 | 0.6104 | 0.4516 | 0.7544 | 85 | 42 | 0.50000-0.50000 |
| RCA | angiocad | 2 | transfer_pooled_sigmoid | target_90 | 326 | 0.6850 | 0.6895 | 0.2286 | 0.6012 | 0.8516 | 0.3743 | 23 | 107 | 0.34541-0.40485 |
| RCA | uci | 1 | cohort_intercepts | fixed_50 | 303 | 0.6833 | 0.6897 | 0.2149 | 0.6469 | 0.2895 | 0.8624 | 81 | 26 | 0.50000-0.50000 |
| RCA | uci | 1 | cohort_intercepts | target_90 | 303 | 0.6833 | 0.6897 | 0.2149 | 0.5578 | 0.8860 | 0.3598 | 13 | 121 | 0.26271-0.29457 |
| RCA | uci | 1 | cohort_intercepts_sigmoid | fixed_50 | 303 | 0.6823 | 0.6897 | 0.2140 | 0.6733 | 0.2982 | 0.8995 | 80 | 19 | 0.50000-0.50000 |
| RCA | uci | 1 | cohort_intercepts_sigmoid | target_90 | 303 | 0.6823 | 0.6897 | 0.2140 | 0.5578 | 0.8860 | 0.3598 | 13 | 121 | 0.26705-0.31399 |
| RCA | uci | 1 | local | fixed_50 | 303 | 0.6851 | 0.6824 | 0.2154 | 0.6370 | 0.2018 | 0.8995 | 91 | 19 | 0.50000-0.50000 |
| RCA | uci | 1 | local | target_90 | 303 | 0.6851 | 0.6824 | 0.2154 | 0.5578 | 0.8509 | 0.3810 | 17 | 117 | 0.26376-0.36232 |
| RCA | uci | 1 | local_sigmoid | fixed_50 | 303 | 0.6712 | 0.6824 | 0.2162 | 0.6667 | 0.2193 | 0.9365 | 89 | 12 | 0.50000-0.50000 |
| RCA | uci | 1 | local_sigmoid | target_90 | 303 | 0.6712 | 0.6824 | 0.2162 | 0.5578 | 0.8509 | 0.3810 | 17 | 117 | 0.27801-0.33445 |
| RCA | uci | 1 | pooled | fixed_50 | 303 | 0.6882 | 0.6927 | 0.2165 | 0.6370 | 0.4386 | 0.7566 | 64 | 46 | 0.50000-0.50000 |
| RCA | uci | 1 | pooled | target_90 | 303 | 0.6882 | 0.6927 | 0.2165 | 0.5710 | 0.8684 | 0.3915 | 15 | 115 | 0.31614-0.36409 |
| RCA | uci | 1 | pooled_sigmoid | fixed_50 | 303 | 0.6854 | 0.6927 | 0.2136 | 0.6601 | 0.2895 | 0.8836 | 81 | 22 | 0.50000-0.50000 |
| RCA | uci | 1 | pooled_sigmoid | target_90 | 303 | 0.6854 | 0.6927 | 0.2136 | 0.5710 | 0.8684 | 0.3915 | 15 | 115 | 0.26493-0.31547 |
| RCA | uci | 1 | training_prevalence | fixed_50 | 303 | 0.4952 | 0.5000 | 0.2347 | 0.6238 | 0.0000 | 1.0000 | 114 | 0 | 0.50000-0.50000 |
| RCA | uci | 1 | transfer_pooled | fixed_50 | 303 | 0.6316 | 0.6352 | 0.2390 | 0.5809 | 0.6053 | 0.5661 | 45 | 82 | 0.50000-0.50000 |
| RCA | uci | 1 | transfer_pooled | target_90 | 303 | 0.6316 | 0.6352 | 0.2390 | 0.5248 | 0.8509 | 0.3280 | 17 | 127 | 0.36305-0.41657 |
| RCA | uci | 1 | transfer_pooled_sigmoid | fixed_50 | 303 | 0.6327 | 0.6352 | 0.2234 | 0.6337 | 0.1579 | 0.9206 | 96 | 15 | 0.50000-0.50000 |
| RCA | uci | 1 | transfer_pooled_sigmoid | target_90 | 303 | 0.6327 | 0.6352 | 0.2234 | 0.5248 | 0.8509 | 0.3280 | 17 | 127 | 0.28773-0.34344 |
| RCA | uci | 2 | cohort_intercepts | fixed_50 | 303 | 0.6893 | 0.6949 | 0.2135 | 0.6370 | 0.2719 | 0.8571 | 83 | 27 | 0.50000-0.50000 |
| RCA | uci | 2 | cohort_intercepts | target_90 | 303 | 0.6893 | 0.6949 | 0.2135 | 0.5776 | 0.8860 | 0.3915 | 13 | 115 | 0.24760-0.31979 |
| RCA | uci | 2 | cohort_intercepts_sigmoid | fixed_50 | 303 | 0.6763 | 0.6949 | 0.2198 | 0.6271 | 0.2193 | 0.8730 | 89 | 24 | 0.50000-0.50000 |
| RCA | uci | 2 | cohort_intercepts_sigmoid | target_90 | 303 | 0.6763 | 0.6949 | 0.2198 | 0.5776 | 0.8860 | 0.3915 | 13 | 115 | 0.26797-0.33701 |
| RCA | uci | 2 | local | fixed_50 | 303 | 0.6991 | 0.7092 | 0.2131 | 0.6568 | 0.2456 | 0.9048 | 86 | 18 | 0.50000-0.50000 |
| RCA | uci | 2 | local | target_90 | 303 | 0.6991 | 0.7092 | 0.2131 | 0.5347 | 0.9386 | 0.2910 | 7 | 134 | 0.25058-0.31885 |
| RCA | uci | 2 | local_sigmoid | fixed_50 | 303 | 0.6828 | 0.7092 | 0.2184 | 0.6370 | 0.2105 | 0.8942 | 90 | 20 | 0.50000-0.50000 |
| RCA | uci | 2 | local_sigmoid | target_90 | 303 | 0.6828 | 0.7092 | 0.2184 | 0.5347 | 0.9386 | 0.2910 | 7 | 134 | 0.26330-0.35382 |
| RCA | uci | 2 | pooled | fixed_50 | 303 | 0.6918 | 0.6949 | 0.2154 | 0.6502 | 0.4561 | 0.7672 | 62 | 44 | 0.50000-0.50000 |
| RCA | uci | 2 | pooled | target_90 | 303 | 0.6918 | 0.6949 | 0.2154 | 0.5545 | 0.9035 | 0.3439 | 11 | 124 | 0.30151-0.35914 |
| RCA | uci | 2 | pooled_sigmoid | fixed_50 | 303 | 0.6700 | 0.6949 | 0.2194 | 0.6271 | 0.2281 | 0.8677 | 88 | 25 | 0.50000-0.50000 |
| RCA | uci | 2 | pooled_sigmoid | target_90 | 303 | 0.6700 | 0.6949 | 0.2194 | 0.5545 | 0.9035 | 0.3439 | 11 | 124 | 0.25618-0.33816 |
| RCA | uci | 2 | training_prevalence | fixed_50 | 303 | 0.4944 | 0.5000 | 0.2347 | 0.6238 | 0.0000 | 1.0000 | 114 | 0 | 0.50000-0.50000 |
| RCA | uci | 2 | transfer_pooled | fixed_50 | 303 | 0.6316 | 0.6250 | 0.2390 | 0.5809 | 0.6053 | 0.5661 | 45 | 82 | 0.50000-0.50000 |
| RCA | uci | 2 | transfer_pooled | target_90 | 303 | 0.6316 | 0.6250 | 0.2390 | 0.5314 | 0.8684 | 0.3280 | 15 | 127 | 0.34773-0.40934 |
| RCA | uci | 2 | transfer_pooled_sigmoid | fixed_50 | 303 | 0.6234 | 0.6250 | 0.2279 | 0.6238 | 0.1667 | 0.8995 | 95 | 19 | 0.50000-0.50000 |
| RCA | uci | 2 | transfer_pooled_sigmoid | target_90 | 303 | 0.6234 | 0.6250 | 0.2279 | 0.5314 | 0.8684 | 0.3280 | 15 | 127 | 0.26323-0.34718 |

## Reproduction and checks

Canonical entry: `python scripts/run_cohort_calibration.py prepare`, then `fit`, `evaluate`, `verify`. Preparation/fitting/evaluation refuse overwrites; preserve the existing frozen trial. The wrapper imports the model module canonically so saved class names remain loadable. `python scripts/verify_cohort_calibration.py` independently checks saved evidence; `python scripts/report_cohort_calibration.py` regenerates this report without fitting. Raw cohort workbooks and private fitted objects must be available locally for full replay.

The runner verified all raw/code/protocol/history hashes, exact row roles, calibration/evaluation prediction replay, frozen cutoffs and metric regeneration. A separate script reproduced **306 metric groups** and independently checked all 90 disjoint three-role definitions, raw outcome/row coverage, duplicate exclusions and calibration-only cutoff selection. Metamorphic tests changed held-out features/labels and confirmed identical fits/calibrators/cutoffs. Cohort-intercept tests checked distinct baselines and unknown-cohort rejection. All 62 protected historical files remain unchanged.

Evidence: [frozen protocol](cohort_calibration_protocol.md), [all metrics](../ml/experiments/cohort_calibration_v1/results.json), [indexed evaluation predictions](../ml/experiments/cohort_calibration_v1/evaluation_predictions.csv), [partitions](../ml/experiments/cohort_calibration_v1/partitions.json), [calibration metadata](../ml/experiments/cohort_calibration_v1/fit_metadata.json). Fitted research objects remain local/ignored in `ml/experiments/cohort_calibration_v1/private/`.

## Decision

Preserve LCX as a follow-up candidate; no production promotion. Benefit is small, uncertain and limited to reduced-input models on reused cohorts with a known cohort context and local labeled calibration records. New compatible data, clinical field/timing confirmation, exact explanation fidelity and an intended-use/error-cost objective remain necessary before any live replacement. Calibration is not a substitute for matching the clinical task.

Methods context: [Falconieri et al., multicenter model simulation](https://doi.org/10.1002/bimj.201900075) and [BMJ recalibration guidance](https://doi.org/10.1136/bmj.i3140). The simulation studies random intercepts; our fixed-intercept experiment is distinct. These sources motivate a comparison, not a claim that it must work.
