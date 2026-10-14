# Broad model search v2 results

This report records the completed exploratory run specified in [the frozen protocol](broad_search_protocol.md). The experiment reuses the already studied 303-row Z-Alizadeh Sani cohort, so these results are internal model-development evidence, not independent validation. The two repeats reuse the same people and are summarized separately before their average; they are not treated as 606 independent observations. The four source outcome columns remained excluded from model inputs.

## Run and audit status

The run completed all 40 outer folds across four targets and two repeats in 1,161.86 seconds (19.4 minutes). It attempted and completed 480 individually fitted candidate jobs. There were no timeouts, candidate failures, worker failures, stage-budget omissions, or fits over 15 seconds. The fixed equal-weight ensemble was evaluated from its five frozen members. The run emitted 320 estimator warnings, all ElasticNet `penalty='elasticnet'` deprecation notices; they did not produce fit failures. The settings were not changed after this run.

The audit confirmed all eight held-out prediction CSVs contain 303 unique row IDs, five outer folds, complete predictions, and probabilities within [0, 1]. All 40 outer partitions are disjoint and cover the source rows; all 120 inner partitions are disjoint and cover only their corresponding outer-training rows. Repeat-one baseline-selector predictions parsed from the saved CSVs exactly match the original [improvement-v1 predictions](../ml/experiments/improvement_v1/). The runner's separate in-memory exact-equality flag is false because its direct comparison found differences no larger than 1.11e-16; this is machine-precision equality, and the saved CSV comparison is exactly equal.

The manifest's hashes for the protocol, runner, source workbook, schema, preprocessing, metrics, and baseline runner were independently rechecked against the current files and all match. The saved run is marked complete with no fatal error. The broad-v2 folder retains the manifest, per-target nested results, per-fold split and score details, and all row-level predictions. The `summary.json` and per-target JSONs are the source of the metrics below.

## Nested selector comparison

The table averages each metric across the two repeat-level held-out metrics. Deltas are broad selector minus the existing baseline selector; lower Brier and ECE are better, and a calibration slope closer to 1 is generally better. The preregistered raw-predictor screen requires mean AUROC gain ≥0.015, no repeat AUROC decrease, and mean Brier increase ≤0.005. The probability-quality screen requires mean Brier improvement ≥0.005 and no repeat AUROC decrease greater than 0.01.

| Target | Baseline AUROC | Broad AUROC | Δ AUROC | Baseline Brier | Broad Brier | Δ Brier | Baseline slope / ECE | Broad slope / ECE | Raw screen | Quality screen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| CAD | 0.9098 | 0.9069 | -0.0029 | 0.10451 | 0.10650 | +0.00199 | 1.049 / 0.0241 | 1.069 / 0.0336 | Fail | Fail |
| LAD | 0.8287 | 0.8306 | +0.0019 | 0.16832 | 0.16310 | -0.00522 | 1.557 / 0.0719 | 1.055 / 0.0447 | Fail | Pass |
| LCX | 0.7276 | 0.7296 | +0.0020 | 0.20606 | 0.20426 | -0.00180 | 1.329 / 0.0564 | 1.210 / 0.0432 | Fail | Fail |
| RCA | 0.7079 | 0.7031 | -0.0048 | 0.20801 | 0.20959 | +0.00158 | 0.981 / 0.0418 | 0.812 / 0.0427 | Fail | Fail |

Only the LAD broad selector passes either nested-procedure gate, and it passes the probability-quality screen only. Across targets, selector choices varied by outer fold. The broad selection procedure does not meet the preregistered raw-predictor screen for any target and is not a general replacement for the baseline procedure.

## Fixed-candidate diagnostics

The fixed candidates were evaluated on the same outer partitions and screened against the baseline selector. Because the family was scanned, these per-candidate results are post-search diagnostics and do not estimate an unbiased winning model. They can nominate a family/configuration for a newly prespecified evaluation.

| Target | Candidates passing at least one screen | Diagnostic mean AUROC / Brier | Readout |
|---|---|---|---|
| CAD | Fixed uniform ensemble: raw screen only | 0.9252 / 0.10314 | Mean AUROC gain +0.01535; both repeats improved. Calibration was worse (slope 1.715, ECE 0.0788 versus 1.049, 0.0241 for baseline), so do not advance without a calibration gate. |
| LAD | Boosting, ExtraTrees, CatBoost: quality only; fixed uniform ensemble: both | Ensemble 0.8452 / 0.15815 | The ensemble's AUROC gains were +0.0143 and +0.0187; Brier improved by 0.01016. Its mean calibration slope was 1.498 and ECE 0.0742, with ECE slightly above the baseline's 0.0719. |
| LCX | HistGradientBoosting, CatBoost, fixed uniform ensemble: both | HistGradientBoosting 0.7439 / 0.19951; CatBoost 0.7479 / 0.19926; ensemble 0.7519 / 0.20034 | All three passed both engineering screens. HistGradientBoosting's repeat AUROC gains were +0.0131 and +0.0195 and Brier improved by 0.00655; CatBoost gains were +0.0208 and +0.0197 and Brier improved by 0.00680. |
| RCA | Logistic C=0.03, ElasticNet L1 ratio 0.25, fixed uniform ensemble: both; ElasticNet L1 ratio 0.75: raw only | Logistic C=0.03 0.7317 / 0.20082; ElasticNet 0.25 0.7322 / 0.20032 | Logistic C=0.03 and ElasticNet 0.25 improved AUROC in both repeats by at least 0.021 and Brier by 0.00719 and 0.00770, respectively. The ensemble passed both screens but its ECE was 0.0773 versus baseline 0.0418. |

## Follow-up recommendation

Do not promote a model from this search. The strongest practical next artifact is the fixed LCX HistGradientBoosting candidate: it passed both prespecified engineering screens, uses the existing scikit-learn stack, and avoids adding a production dependency. Its mean held-out AUROC was 0.7439 versus 0.7276 for the baseline selector, and Brier was 0.19951 versus 0.20606. These are exploratory post-search figures. At threshold 0.5 its held-out recall was 0.538 and specificity 0.815; those operating characteristics need an explicitly chosen use policy and independent validation.

LCX CatBoost is also a candidate for a later controlled comparison based on the nested candidate diagnostics, but needs a separately reviewed dependency and native-feature explanation path. The LAD ensemble and RCA logistic/ElasticNet configurations may merit prespecified follow-up if their probability quality is the priority. The ensemble's poorer calibration in some targets and its model-agnostic explanation path weigh against selecting it now.

An isolated [LCX HistGradientBoosting candidate package](../models/candidates/histgb_lcx/manifest.json) was built for an opt-in research comparison. Its manifest links both repeats of row-level held-out predictions, the baseline-selector comparisons, and the original repeat-one baseline reference. The serialized candidate passed the existing `ml.explain` path on all 303 source rows: maximum raw-margin reconstruction residual was 2.66e-15, and the explained output matched the model decision function exactly. Synthetic inputs with a missing numeric and categorical field and with out-of-range numeric values also reconstructed successfully. An identical second fit produced exactly the same probabilities; batch prediction of 303 rows took about 0.009 seconds, and the 303 explanation checks took 5.92 seconds with one thread. These are engineering fidelity and local timing checks, not held-out performance evidence. The artifact was fit on all 303 rows only to create a locally usable candidate; only the nested held-out CSV predictions above support the reported candidate metrics. The manifest confirms the production metadata and LCX artifact hashes still match the frozen broad-search baseline.

The broad selector is the only nested procedure estimate; individual fixed-candidate values are not new external-test results. Any follow-up protocol should be frozen before evaluating a new cohort and should include exact-model explanation reconstruction, calibration, and API compatibility gates. The search itself did not change the original production artifacts or metrics. A subsequent application integration exposes the packaged LCX candidate only through explicit opt-in, shows matched evidence, and preserves the baseline as default; see README and the 8 October verification notes.

## Reproducibility and completion checks

The frozen run settings, seeds, candidate list, environment, source hashes, job counters, and completion state are recorded in [run_manifest.json](../ml/experiments/broad_v2/run_manifest.json). Detailed target results and selection frequencies are in [summary.json](../ml/experiments/broad_v2/summary.json), with full repeat-level splits, inner scores, candidate predictions, and baseline deltas in the target JSON files and row predictions in the eight CSVs.

The focused runner test suite completed with 15 passing tests in `.venv-research`; the same suite completed with 14 passing and one CatBoost-dependent skip in the unchanged main environment. Runner byte-compilation passed. Test coverage includes synthetic family fits, optional CatBoost handling, and spawned-worker transport; no test retrained or rewrote the broad-v2 outputs. The broader experiment audit above was read-only and validated the persisted predictions, partitions, source hashes, and completion counters.

This search does not evaluate the separate TabICL/TabPFN foundation-model avenue, target-independent feature selectors beyond the fixed 55-field allowlist, or clinical interaction terms. Feature selectors, interactions and TabPFN remain untested avenues, not negative results. The separate TabICLv2 experiment and explanation pilot are now documented in tabicl_results.md and tabicl_explanation_results.md.
