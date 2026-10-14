# Broad model search protocol v2

Prepared before the broad run. This is an exploratory search on the already inspected 303-record Z-Alizadeh Sani cohort, not a fresh test. The two repeat seeds reuse the same people; repeated predictions are summarized by repeat and are never counted as independent observations. No production model, metric, API, frontend, or explanation code is changed.

## Questions and fixed data contract

The run asks whether a broader set of model families can improve held-out discrimination, probability quality, and calibration over the existing inner-CV baseline selector. Inputs are exactly the 55 fields in `ml/schema.py::FEATURES`; the four outcome columns Cath, LAD, LCX, and RCA are excluded from every fit. The source workbook is hashed before the run. No rows, labels, or features are altered, synthesized, filtered globally, or harmonized from another dataset.

Every imputer, scaler, encoder, classifier, and SVM probability calibrator is fitted using the current training partition only. CatBoost receives the same training partition's numeric columns and native string categorical columns. The full source cohort is never used to fit a transform or estimator.

## Repeated nested cross-validation

- Repeats use seeds `20261007` and `20261108`.
- Each repeat has five shuffled stratified outer folds.
- Each outer training partition has three shuffled stratified inner folds with seed `outer_seed + outer_fold`.
- Candidate settings and ensemble membership are frozen below. The baseline selector and broad selector choose by mean inner-fold ROC-AUC only. Exact ties retain the first candidate in the listed order.
- For each outer fold, every fixed candidate is scored on the same inner splits and refit on the full outer-training partition for its held-out prediction. A fixed equal-weight ensemble averages its five prespecified member probabilities. Its members are not selected or weighted from any outcome.
- The calibrated RBF SVM wraps the complete preprocessing and SVC pipeline in three-fold sigmoid `CalibratedClassifierCV`. For inner predictions, calibration folds are created only inside each inner training subset. For outer predictions, calibration folds are created only inside that outer training partition.
- The SVM candidate is calibrated only; there is no raw-SVC comparator. Its calibration metrics describe its probabilities and cannot isolate a gain caused by sigmoid calibration.
- Baseline candidates and their settings exactly match the existing `improvement_v1` baseline. Repeat one is checked against its saved row predictions.

## Frozen candidate list

All candidates use the existing fold-local median imputation, numeric standardization, most-frequent categorical imputation, and one-hot encoding unless marked native categorical. Hyperparameters are intentionally small and fixed; there is no post-result expansion of the search.

| Candidate | Family and fixed settings |
|---|---|
| `logistic_003` | Existing logistic regression, C = 0.03 |
| `logistic_03` | Existing logistic regression, C = 0.3 |
| `forest` | Existing random forest, 120 trees, minimum leaf 5, square-root feature sampling |
| `boosting` | Existing gradient boosting, 80 trees, learning rate 0.035, depth 2, minimum leaf 8 |
| `elasticnet_l1_025` | Elastic-net logistic regression, C = 0.1, L1 ratio 0.25, saga, 5,000 iteration cap |
| `elasticnet_l1_075` | Elastic-net logistic regression, C = 0.1, L1 ratio 0.75, saga, 5,000 iteration cap |
| `shrinkage_lda` | Linear discriminant analysis, LSQR solver, automatic shrinkage |
| `hist_gradient_boosting` | Histogram gradient boosting, 100 iterations, learning rate 0.05, 7 leaves, L2 = 2 |
| `extra_trees` | Extra trees, 160 trees, minimum leaf 4, square-root feature sampling |
| `rbf_svm_sigmoid` | RBF SVC, C = 1, sigmoid calibration, three inner calibration folds |
| `mlp_small` | MLP (16, 8), alpha 0.05, 350 iteration cap, early stopping |
| `catboost_native` | CatBoost 1.2.10, 180 iterations, depth 4, learning rate 0.03, L2 = 6, one thread, native categorical inputs |
| `uniform_ensemble` | Fixed equal average of `logistic_003`, `boosting`, `extra_trees`, `rbf_svm_sigmoid`, and `catboost_native` |

## Explanation feasibility

The search measures predictions and does not implement explanations. These are engineering paths to investigate only after a candidate has reviewable validation evidence.

| Model family | Plausible explanation path | Current evidence boundary |
|---|---|---|
| Logistic and elastic-net logistic | Grouped linear SHAP in the transformed feature space | The app has a grouped Linear SHAP path for its existing logistic artifacts; each candidate still needs exact reconstruction checks. |
| Random forest and gradient boosting | Grouped tree SHAP after the same preprocessing | The app uses a grouped Tree SHAP path for its existing tree artifacts; each candidate needs its own additivity check. |
| Extra trees | Tree SHAP with one-hot contributions regrouped to source fields | Plausible, but not verified for a saved candidate artifact. |
| Shrinkage LDA | Linear posterior-margin decomposition | Plausible, but feature grouping and reconstruction are not implemented. |
| Histogram gradient boosting | Tree SHAP if the installed explainer supports this estimator; otherwise a model-agnostic method | Support and reconstruction are unverified. |
| Calibrated RBF SVM and MLP | Model-agnostic explanation of final probabilities | Approximate and potentially expensive; no fidelity result exists. |
| CatBoost | Native Tree SHAP over original feature names | Requires a native-category artifact path and original-field grouping checks. |
| Uniform ensemble | Model-agnostic explanation of the averaged probability, or verified probability-scale member composition | Member explanations may use different output scales; no additive result is established. |

The result files include this per-candidate feasibility assessment alongside the baseline deltas. It is not a claim that an explanation exists or is faithful.

The fixed feature allowlist itself is the target-independent feature screen. No extra correlation filter or target-derived univariate selector is added: the small sample and the lack of a prespecified clinical rule make such choices outcome-sensitive or arbitrary. No interaction search is added because unrestricted pairwise expansion of 55 fields would create many more terms than observations and there is no domain-reviewed interaction list. Both remain untested avenues rather than post-hoc additions.

TabICL and TabPFN foundation models are outside this run. They require separate checks of their training-row regime, weights, and licensing; this protocol does not make their results a hidden part of broad v2.

CatBoost is installed only in the isolated research environment. If its package is missing or a fit fails, the candidate is logged as failed and the fixed five-member ensemble becomes unavailable for that fold; membership is never silently changed or renormalized.

## Metrics and interpretation

For each target, candidate, and repeat, report ROC-AUC, average precision, Brier score, log loss, and threshold-0.5 classification metrics. Calibration diagnostics include calibration intercept and slope from held-out predictions, five quantile calibration bins, and a five-bin expected calibration error. These are descriptive summaries of the same held-out rows; they do not establish statistical significance or clinical utility.

The main comparison is the nested broad selector against the exact baseline selector, averaged across the two repeat-level metrics while also showing both repeat deltas. Candidate-by-candidate held-out results are diagnostic and remain exposed as a family search, not a new single-test estimate. No candidate is auto-promoted. A possible follow-up still needs independent compatible data, explanation fidelity on the exact fitted model, API regression, and human review appropriate to its use.

## Preregistered engineering eligibility screens

Apply both screens to the nested `broad_selector`, the fixed uniform ensemble, and each prespecified fixed candidate, always relative to the baseline selector for the same target and repeat:

- **Raw-predictor screen:** mean two-repeat AUROC gain is at least 0.015, neither repeat's AUROC is lower, and mean Brier-score increase is no more than 0.005.
- **Probability-quality screen:** mean Brier-score improvement is at least 0.005 and neither repeat's AUROC is more than 0.01 lower.

These thresholds are engineering screens, not significance tests, clinical criteria, or approval to replace a model. The broad selector is the nested procedure result. Individual fixed-candidate gates are post-search family diagnostics; a candidate that passes can inform a separate full protocol, but it is not an unbiased winning estimate after scanning this family set. A broad-selector failure does not erase evidence from an individually prespecified family configuration. Independent data and exact-model explanation/API checks remain necessary before any production review.

## Resource, failures, and outputs

The run uses one spawned worker process with numerical thread pools limited to one (within a two-CPU ceiling). Each candidate/outer-fold job has a 120-second hard wall-time limit. A timeout terminates and joins the worker before starting another; estimator exceptions, warnings, slow individual fits, worker failures, and stage-budget omissions are saved as separate counts. The full stage budget is three hours. It does not silently retry a failed candidate with new settings.

The runner, protocol, schema, preprocessing, metric implementation, prior search runner and repeat-one baseline reference CSVs, source workbook, and existing model metadata are SHA-256 recorded. `ml/experiments/broad_v2/` contains a manifest, per-target JSON with all inner split indices/scores and inner predictions, per-fold JSON, and one held-out row-prediction CSV per target and repeat. Missing predictions remain missing and make that candidate's metric status incomplete. Outputs distinguish a completed cross-validation schedule from individual family fit failures.

Search evidence is exploratory because this source was already used for model development and earlier validation. Nothing here replaces independent external validation or constitutes a release decision.
