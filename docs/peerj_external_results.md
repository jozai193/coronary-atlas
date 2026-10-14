# Frozen China cohort comparison — 9 October 2026

**Completed negative result.** A fixed 14-input Explainable Boosting Machine (EBM) did not beat a fixed 14-input logistic comparator on 553 new patients. Both transferred probabilities poorly. The app's fitted models are unchanged. This is not an external test of either the 55-input app or the separate 55-input EBM candidate.

## Source and frozen design

[Cao et al., PeerJ 2022](https://doi.org/10.7717/peerj.14078) provide the official 553-row supplement from a Chinese hospital, with 201 CHD and 352 non-CHD labels. It contains no vessel outcomes. The source and destination differ in center, country, selection, observed age range, prevalence and outcome definition. The study combines clinical assessment with >50% stenosis; source labels nominally use >=50%. Source measurement units and timing are incompletely documented. This is a qualified transport experiment, not proof of equivalent clinical endpoints.

The [protocol](peerj_external_protocol.md) was frozen before fitting or scoring. Exactly 14 mapped fields were used: Age, Sex, BMI, DM, HTN, FBS, TG, LDL, HDL, HB, K, Na, WBC, PLT. Unit conversion uses the published destination units and disclosed source conventions. No destination data were fitted, calibrated or used for feature selection. One fixed logistic model and one main-effects EBM configuration were evaluated in five paired source folds, then fit on all 303 original records. The final model freeze preceded destination scoring by seven seconds (13:23:17 and 13:23:24 UTC). All 12 source fits completed in 3.61 seconds. The prior 55-input EBM trial used different inputs; its CAD gain cannot be transferred to this task.

## Primary result

All 553 official rows, including the supplied extreme WBC value, are retained. Cutoff is the predeclared 0.5.

| Metric | Logistic | EBM |
|---|---:|---:|
| AUC | 0.6741 | 0.6642 |
| Conditional 95% AUC interval | 0.6265–0.7211 | 0.6186–0.7076 |
| Brier error (lower better) | 0.3073 | 0.3326 |
| Log loss | 0.8268 | 0.9150 |
| Mean predicted probability | 67.37% | 70.30% |
| Observed prevalence | 36.35% | 36.35% |
| Accuracy | 43.94% | 47.38% |
| Sensitivity | 92.04% | 91.04% |
| Specificity | 16.48% | 22.44% |
| Precision | 38.62% | 40.13% |
| True positives / false negatives | 185 / 16 | 183 / 18 |
| True negatives / false positives | 58 / 294 | 79 / 273 |

EBM-minus-logistic AUC is **−0.00992** (paired conditional 95% interval −0.03290 to +0.01186). Brier error increases **0.02528** (interval +0.01720 to +0.03284). The 1,000 paired row-bootstrap draws condition on frozen models and omit training, measurement and center uncertainty. The frozen engineering screen fails. Higher thresholded accuracy here does not rescue worse ranking and probability error.

The source disease prevalence is 216/303 (71.29%). Its constant-probability predictor has external Brier 0.3534. Both fitted models beat that source constant, but still substantially overpredict disease and generate many false positives. Neither result establishes a useful clinical operating point. No destination threshold or calibration was selected after this test.

## Prespecified checks

| Analysis | n / positives | Logistic AUC / Brier | EBM AUC / Brier |
|---|---:|---:|---:|
| Primary | 553 / 201 | .6741 / .3073 | .6642 / .3326 |
| Exclude WBC >100 in destination units | 552 / 200 | .6724 / .3079 | .6654 / .3330 |
| Source-overlap ages >=30 | 550 / 201 | .6713 / .3086 | .6613 / .3341 |
| Female, descriptive | 198 / 40 | .7593 / .3403 | .7736 / .3464 |
| Male, descriptive | 355 / 161 | .6319 / .2890 | .5984 / .3250 |
| Age <50, descriptive | 136 / 46 | .6899 / .2514 | .6628 / .2665 |
| Age >=50, descriptive | 417 / 155 | .6931 / .3256 | .6789 / .3542 |

Neither sensitivity check changes the primary decision. Subgroups are small descriptive checks, not alternate model-selection targets or fairness evidence. Female observed prevalence is 20.20%, versus 64.87%/65.35% mean predictions. This emphasizes poor probability transfer even where within-group ranking appears better.

The matched source five-fold OOF AUC/Brier was .7950/.1632 for logistic and .7595/.1681 for EBM. These results were preserved without changing the configuration. Cross-cohort differences cannot isolate a population effect from selection, measurement or label differences.

The median age shifts from 58 to 55, BMI 26.78 to 25.00, mapped fasting glucose 98 to 112.59, LDL 100 to 90.49, and potassium 4.2 to 3.9. Full medians, IQRs, outside-source-range counts and ten-bin reliability summaries are saved. These describe observed shift; they do not identify its causal driver.

EBM's 14 native additive terms reconstruct all 303 source and 553 external decision scores, maximum residual 1.34e-15; reconstructed probabilities differ by at most 2.23e-16. These are exact model terms, not SHAP or clinical causes. This checks explanation arithmetic, not predictive validity.

## Provenance and reproducibility

The official [PMC Cloud supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC9653049.1/peerj-10-14078-s001.csv) has 92,823 bytes, 553 unique rows, 45 columns, no missing cells and SHA-256 `c94efdcd7aed7d2b02c242e405c3d07faffb66687ec119743648335299808cc5`. PMC metadata and the article indicate CC BY 4.0 and no retraction. Attribution and file details are in `data/external_audit/peerj_v1/provenance.json`.

A secondary GitHub mirror had 715 rows, including 162 exact duplicates and altered values. It was rejected. The official 553-row data were used unchanged. Its implausible diastolic BP value is outside the input contract; the WBC anomaly is retained in the headline and handled only in the predeclared sensitivity check. Anonymization prevents proving person-level independence, although the separate center and country support it.

Protocol SHA-256: `40469f7e0557fa53659a7a1b07b15d3e20d2cf0c55682e319444f7281dcf6a47`. All files under `output/research/peerj_v1/` are immutable evidence: protocol/code lock, runner snapshot, source folds and OOF probabilities, frozen models, external predictions, metrics and hash manifests. Published prediction rows contain sequential row indices, outcomes, probabilities and coarse subgroup flags; raw IDs and measurements are omitted. This is not a formal de-identification assessment. Raw supplements remain local and excluded from the source ZIP.

```powershell
.venv\Scripts\python.exe -m ml.peerj_external verify
.venv\Scripts\python.exe scripts/verify_peerj_external.py
.venv\Scripts\python.exe scripts/export_peerj_evidence.py
```

The first verifier recomputes source/external metrics, fold integrity and paired intervals without optional InterpretML or external raw data. The second independently checks subgroup/reliability summaries, the promotion screen and the UI copy. Re-fitting requires the exact official raw file and optional `interpret-core==0.7.8`; the runner refuses to overwrite this trial. Its saved versions are numpy 2.4.6, pandas 3.0.6 and scikit-learn 1.9.1. Keep any future development separate from this completed test.

## Decision and next accuracy work

Keep the app baseline. The evidence now points toward reviewed feature meaning, measurement availability and population-specific calibration as concrete weaknesses; it does not establish which correction would work. A calibration study would need a new development protocol and a further untouched evaluation. The one available doctor/coronary reviewer should first check source units/timing, endpoint correspondence, and whether the displayed probabilities and reference anatomy are understandable. An observed learner task and clinical anatomical review remain unperformed. Additional same-cohort searches cannot replace that evidence.
