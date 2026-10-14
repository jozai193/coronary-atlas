# Local learning with separate calibration and cutoff selection

10 October 2026. **Retrospective development, not fresh validation.** Same previously inspected 553 Anhui patients and separate 14-input CAD task. The user confirms no reviewer guidance on intended use or acceptable error costs. All sensitivity targets are exploratory. No live model or cutoff changed.

## What was done

The [protocol](peerj_operating_protocol.md) and runner were frozen before 30 new fits: ten local logistic rankers and twenty sigmoid calibrators. Two five-fold repeats use **331–332 training, 111 calibration, 110–111 evaluation** rows per split, with pairwise disjoint roles. Training fits preprocessing and the ranker. Calibration fits sigmoid parameters and the largest cutoff meeting each predeclared empirical sensitivity target. Evaluation rows fit neither. All 553 people are evaluated once per repeat, not 1,106 independent people. Earlier labels/results are known, so role isolation does not erase development selection.

## Probability quality

Means over two repeats; AUC is the mean within-fold AUC. Pooled OOF AUC is separately saved because changing calibration scales across folds can alter pooled rankings.

| Model | Within-fold AUC | Brier error | Log loss | Mean probability |
|---|---:|---:|---:|---:|
| Frozen source | .6743 | .30735 | .82677 | .6737 |
| Training prevalence constant | .5000 | .23164 | .65602 | .3600 |
| Source + separate sigmoid | .6743 | .21229 | .61381 | .3692 |
| Local logistic | .7847 | .18316 | .54631 | .3588 |
| Local + separate sigmoid | .7847 | .18186 | .54422 | .3712 |

Local + sigmoid minus source Brier: **−.12549**, conditional 95% interval **[−.14869, −.10056]**. Versus the local constant: −.04978 [−.06493, −.03506]. Versus uncalibrated local logistic: **−.00130 [−.00593, +.00312]**. Most of the improvement comes from local learning; the small incremental calibration gain is uncertain. All saved sigmoid slopes are retained. Positive slopes preserve within-fold ranking and the calibration-target decisions are identical with/without sigmoid for each ranker; sigmoid must not be credited for the operating-point gain.

## Detection and false alarms

Counts are **repeat 1 / repeat 2**, each over the same **201 positives and 352 negatives**. Sensitivity/specificity are mean repeat rates. A calibration target is not a guarantee on evaluation patients.

| Model / cutoff rule | Missed positives | False alarms | Sensitivity | Specificity |
|---|---:|---:|---:|---:|
| Source / fixed .5 | 16 / 16 | 294 / 294 | 92.0% | 16.5% |
| Source / calibration 80% | 44 / 39 | 195 / 219 | 79.4% | 41.2% |
| Source / calibration 90% | 27 / 20 | 257 / 260 | 88.3% | 26.6% |
| Source / calibration 95% | 11 / 15 | 298 / 292 | 93.5% | 16.2% |
| Source + sigmoid / fixed .5 | 136 / 149 | 44 / 28 | 29.1% | 89.8% |
| Local / fixed .5 | 124 / 121 | 28 / 33 | 39.1% | 91.3% |
| Local + sigmoid / fixed .5 | 96 / 107 | 49 / 38 | 49.5% | 87.6% |
| Local + sigmoid / calibration 80% | 48 / 39 | 132 / 159 | 78.4% | 58.7% |
| Local + sigmoid / calibration 90% | 27 / 17 | 191 / 208 | 89.1% | 43.3% |
| Local + sigmoid / calibration 95% | 13 / 8 | 243 / 252 | 94.8% | 29.7% |

All target-based counts for source + sigmoid match source, and all target-based local counts match local + sigmoid. Every arm/target is in the saved JSON, including per-fold performance, per-repeat descriptive Wilson intervals and the fraction flagged.

Calibration sets contained 35–58 positives among 111 people. Across the ten splits, local + sigmoid cutoffs ranged from .2302–.3998 (80%), .1525–.3480 (90%) and .1049–.2645 (95%). Source cutoffs ranged from .5923–.6752, .4995–.6149 and .4860–.5282, respectively. Three of ten local 90%-target evaluation folds fell below 90%. All sigmoid slopes were positive: source .6587–1.4015, local .8851–2.1949. Exact per-split cutoffs/class counts are preserved in `fit_manifest.json`; these ranges are not recommended thresholds.

At the primary **90% illustration**, local learning versus source with its own calibration-selected 90% cutoff yields **+0.75 percentage points sensitivity** (conditional interval −4.48 to +5.72) and **+16.76 points specificity** (+11.65 to +21.88). That is 66 / 52 fewer false alarms with 0 / 3 fewer misses in these two repeats. This supports the local-learning direction in development; it does not establish a population-level sensitivity improvement.

Compared with the local + sigmoid model at .5, the 90% rule recovers many positives but increases false alarms from 49 / 38 to 191 / 208. Compared with source at .5, it has fewer false alarms but **more missed positives** (27 / 17 versus 16 / 16). We have not chosen a clinically preferred trade-off. The 95% illustration is reported alongside the others, not selected after seeing results.

The bootstrap first averages the two repeat contributions for each person, then resamples 553 people for Brier, 201 positives for sensitivity or 352 negatives for specificity, using 1,000 fixed-seed draws. Intervals condition on saved fits and omit training, threshold-estimation, model-selection and center uncertainty. Descriptive Wilson intervals also omit fitted-model uncertainty. Neither is a deployment guarantee.

## New-center search and next gate

The [Beijing audit](beijing_source_audit.md) found public data but unresolved participant selection and endpoint coding, plus an incompatible input contract. That cohort remains unscored. A fresh compatible evaluation and reviewer-defined intended use/error costs remain open. The 55-input app, vessel predictions and original negative transport results are preserved. No clinical superiority or rule-out use is established.

## Reproduction

Immutable snapshots, exact splits, fit/calibration parameters, per-row outputs and metrics: `output/research/peerj_operating_v1/`. Raw acquired cohorts remain excluded from packaging. `python -m ml.peerj_operating verify` checks hashes, historical preservation, all roles, predictions, cutoffs, metric arithmetic and bootstrap. `python scripts/verify_peerj_operating.py` separately checks cutoff maximality, confusion arithmetic, calibration algebra, training preprocessing and saved linear predictions. With raw data absent, both explicitly skip raw prediction/preprocessing checks and still verify packaged outputs. Regression tests perturb evaluation labels/features and calibration data to verify role isolation.
