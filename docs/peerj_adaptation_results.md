# Local calibration and learning — 10 October 2026

**Result:** a fixed development experiment found lower probability error after local adaptation. With 64 labeled rows per fit, the primary sigmoid calibrator reduced mean Brier error from **.3073 to .2121** and beat the corresponding local-prevalence baseline (.2358). A fixed local logistic model trained on 442–443 rows per fold improved mean within-fold AUC from **.6743 to .7823** and reduced Brier to **.1842**. The 0.5 cutoff still missed many positives. None of these models replaces the app.

This reuses the already inspected 553-person Chinese cohort and its existing 14-input contract. It is **retrospective development**, not another independent transport test or validation of the 55-input app. The previous negative EBM and source-model transport result is preserved. Model choice and the adaptation hypothesis were informed by those known results.

## What was fixed before fitting

The [protocol](peerj_adaptation_protocol.md) fixes all inputs, methods, splits, label budgets, metrics and the primary arm before these new fits. Two seeded five-fold repetitions produce one held-out prediction per person per repeat and budget. Each outer training pool supplies a deterministic 64-row subset and a secondary 442–443-row full-pool subset. The small subset is not forced to match test prevalence. All 20 subsets contain both classes. Test rows never enter their own calibration, scaling, imputation, encoding or local model fit.

The five comparators are unchanged frozen source logistic probabilities, local training prevalence, a fitted intercept offset, a two-parameter sigmoid calibrator, and fixed local logistic regression on the same 14 fields. No search, new predictor, label repair, destination threshold optimization or full-cohort deployment fit was performed. The extreme WBC record remains. The 60 fits took about 0.36 seconds, excluding process startup, and were frozen before evaluation. Saved evidence contains 2,212 prediction rows, representing **553 people evaluated twice under two budgets**, not 2,212 different patients.

## All fixed comparisons

Values are means of two repeat-level metrics. The AUC column averages the five within-fold AUCs, then repetitions. Larger local fits are secondary context, not a replacement for the primary 64-row sigmoid comparison.

| Method | Locally labeled rows per fit | Within-fold AUC | Brier error | Log loss | Mean probability | Sensitivity at .5 | Specificity at .5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Frozen source logistic | 0 | .6743 | .3073 | .8268 | 67.37% | 92.04% | 16.48% |
| Local constant | 64 | .5000 | .2358 | .6654 | 35.77% | 0% | 100% |
| Intercept offset | 64 | .6743 | .2113 | .6115 | 35.62% | 32.09% | 89.35% |
| **Sigmoid recalibration — primary** | **64** | **.6743** | **.2121** | **.6140** | **35.52%** | **25.37%** | **91.48%** |
| Local logistic | 64 | .7404 | .2058 | .5989 | 35.21% | 22.64% | 94.46% |
| Local constant | 442–443 | .5000 | .2314 | .6554 | 36.35% | 0% | 100% |
| Intercept offset | 442–443 | .6743 | .2081 | .6037 | 36.35% | 30.85% | 91.34% |
| Sigmoid recalibration | 442–443 | .6743 | .2082 | .6039 | 36.33% | 29.10% | 91.48% |
| Local logistic | 442–443 | .7823 | .1842 | .5490 | 36.32% | 39.30% | 90.34% |

Observed prevalence is 201/553, **36.35%**. The primary Brier change versus source is **−.09523**, conditional paired 95% interval **−.12051 to −.07224**. Against the 64-row local constant it is **−.02365**, interval **−.03365 to −.01378**. All fixed fitted arms pass the engineering follow-up screen; this does not establish clinical suitability. The slightly lower offset loss is reported without changing the primary arm after evaluation.

The bootstrap averages each person's two repeat squared-error differences first, then resamples 553 people for 1,000 draws. It conditions on fitted models and splits and excludes refitting, search-history and center uncertainty. Repeated rows and folds are not independent observations. These descriptive intervals do not overcome prior inspection of the cohort.

## The detection trade-off

Each repetition has the same 201 positives and 352 negatives. Entries below show repetition 1 / repetition 2, not sums across unique people.

| Method | Local labels per fit | Missed positives / 201 | False positives / 352 |
|---|---:|---:|---:|
| Frozen source | 0 | 16 / 16 | 294 / 294 |
| Local constant | 64 or all | 201 / 201 | 0 / 0 |
| Intercept offset | 64 | 145 / 128 | 37 / 38 |
| **Sigmoid — primary** | **64** | **145 / 155** | **38 / 22** |
| Local logistic | 64 | 161 / 150 | 18 / 21 |
| Intercept offset | 442–443 | 140 / 138 | 30 / 31 |
| Sigmoid | 442–443 | 142 / 143 | 29 / 31 |
| Local logistic | 442–443 | 126 / 118 | 32 / 36 |

The gain is in probability loss and, for local learning, ranking. It is not a claim of improved sensitivity, safer exclusion of disease or patient benefit. Reducing exaggerated probabilities moves many records below .5; that reduces false alarms but also increases missed cases. No cutoff was adjusted to hide this trade-off.

## Ranking, reliability and subgroup interpretation

The offset is monotone and every fitted sigmoid slope is positive (.338 to 1.186), so both preserve ranking within each fold. Pooled OOF AUC is .6609 for 64-row sigmoid and .6741 for the raw source; this is affected by differing fold calibrators and is not evidence of changed within-fold ordering. For local logistic, pooled OOF AUC is .7107 at 64 labels and .7785 at the larger budget; within-fold means are .7404 and .7823. Both versions are saved, not interchanged.

Ten fixed-width reliability bins and female/male/age<50/age>=50 descriptive metrics are saved for every method, budget and repeat. No subgroup-specific fit, threshold or fairness claim is made. A mean probability close to prevalence is not sufficient proof of calibration throughout the range; Brier and log loss assess both discrimination and probability quality. The fixed local-prevalence comparator helps distinguish learning a ranking from merely knowing the new disease rate.

## Reproduction and audit

```powershell
.venv\Scripts\python.exe -m ml.peerj_adaptation verify
.venv\Scripts\python.exe scripts/verify_peerj_adaptation.py
.venv\Scripts\python.exe -m pytest tests/test_peerj_adaptation.py -q
.venv\Scripts\python.exe scripts/export_peerj_adaptation.py
```

The staged runner refuses overwrites. `output/research/peerj_adaptation_v1/` contains the frozen protocol/code identity, partitions, fitted pipelines, parameter records, all held-out probabilities, results and hashes. The verifier recomputes all summaries and intervals and checks unchanged original transport, app models and raw-model metrics. With the locally retained raw supplement, it also reconstructs every saved pipeline prediction. Without the raw supplement, that last check is explicitly skipped; packaged saved-output checks still run without InterpretML.

The independent verifier checks direct MSE/AUC/log-loss/confusion arithmetic, the shared source-code dependency, every training-subset median/scale/category set, fixed hyperparameters and offset balance. Regression tests mutate labels, features and source probabilities outside the fitting subset and require identical learned parameters and evaluation outputs. This is a useful isolation test, not proof of a future clinical study's validity.

## Decision

The strongest measured direction is now specific: **local calibration addresses probability overprediction, while local training can improve ranking** in this development cohort. The live app remains source-cohort only. A follow-up needs a reviewed input/endpoint contract, local training/calibration data and an untouched site/time evaluation with a clinically justified error-cost objective. The present 64-row simulation does not establish that 64 real cases are sufficient in a new hospital. No clinical review, observed learner task or prospective benefit was fabricated.

Sources: [Cao et al., PeerJ 2022](https://doi.org/10.7717/peerj.14078), CC BY 4.0; [original transport result](peerj_external_results.md); [scikit-learn calibration](https://scikit-learn.org/stable/modules/calibration.html) and [cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html).


### Post-fit verifier portability correction

The first clean Git export caught an accidental runtime-cache entry in the preparation inventory: `models/candidates/histgb_lcx/__pycache__/build_candidate.cpython-311.pyc`. It is generated bytecode, intentionally absent from packages. All durable historical model/evidence files had matching hashes. The live runner's read-only `verify` path now excludes `__pycache__`/`.pyc` from that inventory comparison. Its executed `runner_snapshot.py`, original inventory, partitions, fits and outputs remain unchanged. Fit/evaluate still require the exact original runner digest; the revised verifier does not authorize new fitting or rescoring. Independent arithmetic and the original shared dependency check also pass. This corrects portable verification only and does not alter any result or evidence hash.
