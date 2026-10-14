# China calibration and local-learning development protocol

Locked 10 October 2026 before new fitting. This is retrospective development on the already inspected 553-person PeerJ cohort. Previous labels, raw source-model outputs and transport results are known. Row-level fitting separation does not make this a fresh independent test. Preserve the original transport trial and the 55-input app unchanged.

## Question and fixed arms

Can a small locally labeled sample reduce the observed probability overprediction, and does fitting a local ranker add value beyond recalibration? Use the **same 14-input CAD contract** and original CHD labels as `peerj_external_protocol.md`. This is not an experiment on the 55-input app. Endpoint, source-unit/timing, single-center and selected-population limitations remain. Retain all 553 rows and the extreme WBC value; no new feature engineering, outcome recoding or data repair.

The source model is the frozen logistic comparator from `peerj_v1`. Its choice is informed by the completed comparison and disclosed as development selection. EBM is not reconsidered. On each fixed adaptation subset compare:

1. **Frozen source:** unchanged saved logistic probabilities; no destination fit.
2. **Local constant:** disease prevalence of the adaptation subset, repeated for its test rows.
3. **Intercept offset:** add one fitted scalar to the source logit, minimizing binary log loss. Solve mean fitted probability = adaptation prevalence, using Brent's method on [-40,40]. This preserves rank within a fold.
4. **Sigmoid:** logistic regression on the source logit, C=1, max_iter=3000, seed=20261010. It learns an intercept and slope; report every coefficient including a negative slope if one occurs. No tuning. Clip source probabilities to [1e-6,1-1e-6] before logit for both calibration arms.
5. **Local logistic:** the same fixed 14-input logistic pipeline as the original source comparator (C=.03), now fit only to the adaptation subset. Numeric imputation/scaling and nominal encoding are fitted inside that subset. No source records are added, no EBM or family selection.

## Splits, budgets and isolation

Two repetitions of StratifiedKFold(5, shuffle=True), seeds 20261010 and 20261011. Each repetition produces exactly one prediction per destination row. Within each outer training pool, order its indices with RNG seed `20261010 + 100*repeat_index + fold_index`, then use (a) its first **64 rows**, the primary adaptation budget, and (b) all training rows (442 or 443), secondary larger-data context. The 64 rows are a deterministic unstratified subset of the pool, so class prevalence is not forced to match the test fold. Save partitions before fitting. Stop if an adaptation subset has only one class; do not rerandomize.

Neither fitting, preprocessing nor cutoff selection can use that outer fold's test labels. No cross-repeat predictions enter a fit. The original model was fitted only to the original 303 source rows; its saved destination probabilities can be treated as fixed inputs. Raw destination data are needed only for local-logistic fitting. IDs, outcomes, unshared clinical fields and prior model predictions are excluded from that local model's 14 inputs. Run one numerical thread; no search. Save all fitted scalars/coefficients, pipeline artifacts and adaptation-row indices. Freeze them before an evaluation stage produces results. Never refit a final full-cohort deployment model or promote automatically.

## Outputs and interpretation

Report both budgets, all five methods, both repeats: AUC, Brier, log loss, mean probability, prevalence, accuracy, sensitivity, specificity and confusion at .5. Also report average precision, fixed ten-bin reliability, and the mean of the five within-fold AUCs. Pooled OOF AUC can change merely because different folds use different calibrators, so it is not evidence that an intercept adjustment improved ranking.

Primary comparison: 64-row sigmoid minus frozen source. Report mean repeat-level Brier difference and a 1,000-draw seed-20261010 paired patient-row bootstrap interval on squared-error differences averaged across the two repeats. The 553 people, not 1,106 independent predictions, are resampled. Intervals condition on fits/splits and omit fitting, selection and center uncertainty. Do not use fold SD or repetitions as independent patients. Also compare every fitted arm against the same-budget local-prevalence constant; publish all arms regardless of outcome.

Use fixed .5 cutoff counts prominently. Do not select a threshold on the evaluation rows or claim fewer false positives without reporting the change in missed positives. No automatic rule-out, clinical recommendation, sample-size guarantee or fairness claim. Diagnostic sex/age strata (female/male, <50/>=50) are descriptive, with n and positives, only if n>=30 and each class >=10.

The prespecified follow-up screen, for each budget/arm separately, is mean Brier at least .01 lower than frozen source and .005 lower than same-budget constant, with mean within-fold AUC loss <=.01 versus frozen source. This nominates a hypothesis for another untouched study, not the app. The 64-row sigmoid is the primary arm; other successes cannot replace a failed primary headline.

## Integrity and execution

Use `prepare`, `fit`, `evaluate`, `verify` stages; refuse overwrites. Preparation stores the source/external/protocol/code hashes, all split indices and hashes of all files in the historical transport folder plus `models/` and `ml/metrics/`. Fit only from preparation, record all 60 fits (offset, sigmoid, local logistic across 20 budget/fold combinations), and save the model hash before scoring. Evaluation produces 20 method-wide row-prediction tables (two budgets times two repeats times five folds), summarized into one CSV, JSON results and report data. Verification independently reproduces saved-output metrics, split/subset identities, parameters and pipeline predictions, confirms no evaluated row is in its own fit subset, and checks historical hashes. A label-perturbation regression test will confirm that changing labels outside a fit subset cannot alter its fitted outputs.

The raw external data stay ignored and outside packaging. Saved predictions contain sequential indices, fold/repeat/budget, labels and predictions; subgroup flags remain in the historical public evidence. Optional fitted research pipelines are trusted project artifacts, not accepted uploads.

Method references: [scikit-learn calibration](https://scikit-learn.org/stable/modules/calibration.html) and [cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html). Dataset attribution: Cao et al., PeerJ 10:e14078 (2022), DOI [10.7717/peerj.14078](https://doi.org/10.7717/peerj.14078), CC BY 4.0. This development work does not erase the original failed transport result.
