# Accuracy goal: ensemble follow-up v1

14 October 2026. Written before new fits or outcome inspection. The user requested an ongoing goal to increase accuracy. This stage follows promising, already inspected broad-search ensembles; it is deliberately development on reused patients, not independent validation.

## Fixed question and comparison

Can averaging complementary models, followed by training-only probability calibration or regularized weighting, improve the current four-output procedure? Use all original 303 records and the exact 55-input allowlist. Preserve all outcomes, including the inconsistent source record. No synthetic patients, outcome-derived inputs, outcome relabeling, external-data remapping, or tuned evaluation thresholds.

Three shared five-fold outer partitions, seeds 20261021, 20261022, 20261023, stratified by CAD. Identical full-input fingerprints must stay together; use StratifiedGroupKFold. Each outer test partition is withheld from every target, member, calibrator and weight optimizer. New splits of old people are still reused-cohort development. Within each outer training partition, use three target-stratified grouped folds with seed outer_seed + fold + target_index * 100. Persist every split.

Comparator: refit the original four-candidate baseline selector (logistic C=.03/.3, forest, boosting), selected by mean inner ROC-AUC, with fold-local preprocessing. Evaluate both raw probabilities and the existing CAD/vessel coherence projection. The projected baseline is the primary comparator; this evaluates the production learning procedure, not the in-sample predictions of its saved full-data fit.

Fixed ensemble members are the five already specified in broad_search.py: logistic_003, boosting, extra_trees, rbf_svm_sigmoid, catboost_native. Retain their existing configurations, including their own internal calibration where applicable. No hyperparameter search or target-specific member removal.

For each target, fit every member on each inner training partition to obtain complete out-of-fold member probabilities. Fit final members on the entire outer training partition. Three prespecified arms:

1. Uniform: average final-member probabilities.
2. Sigmoid uniform (primary candidate): fit logistic regression C=1 on the logit of inner out-of-fold uniform probabilities, clipping only for the logit at 1e-6. Apply that learned mapping to final-member uniform predictions. Calibration labels never include outer evaluation rows. This is a cross-fitted calibration procedure; full-fit versus inner-fit probability shifts remain a limitation.
3. Simplex blend (secondary): optimize inner OOF Brier plus .01 times squared distance from uniform weights, with nonnegative weights summing to one. SLSQP, tolerance 1e-10, max_iter 1000; fail on nonconvergence. Apply weights without further calibration. No settings selected using outer scores.

Apply the existing coherence projection separately to all three arms; retain all raw outputs as diagnostics. Do not combine target-specific historical OOF files.

## Measures, screen and limits

Primary outcome: mean four-target Brier difference, projected sigmoid uniform minus projected baseline. Report all repeats, all targets and all arms, ROC-AUC, average precision, accuracy, sensitivity, specificity, confusion counts and log loss at the fixed .5 cutoff. No cutoff selection.

Engineering follow-up screen, for each projected candidate separately: mean four-target Brier improvement at least .005; improvement in every repeat; no target's mean Brier deterioration over .005 or mean AUC decrease over .01. This nominates further research; it does not authorize a clinical accuracy claim or automatic live promotion. Publish sensitivity/specificity changes even when the screen passes. No secondary winner may be relabeled as the primary hypothesis.

Compute 2,000 patient bootstrap draws of each person's squared-error difference averaged over repeats and targets. Resample patients, not patient-repeat rows. The interval is conditional on fixed fitted predictions; it excludes refitting, selection, site and prior-search uncertainty. Report per-target intervals too. No nominal statistical-significance claim after these prior searches.

## Execution and verification

Run in the existing research environment, one numerical thread and one job at a time. Budget 45 minutes for fitting; no parameter changes or automatic retries after failure. Prepare partition and source hashes before fitting, save every fitted fold artifact privately and all predictions separately, and evaluate only after the full fit receipt exists. Refuse overwrite of existing results. Preserve hashes of existing models, metrics and historical experiment outputs. Verify in a fresh process by replaying every saved model on its recorded test rows, checking all partitions and rederiving reported metrics, bootstrap and screen. Add leakage-boundary and optimizer tests; include forged-evidence rejection.

Sources: [scikit-learn probability calibration](https://scikit-learn.org/stable/modules/calibration.html), [pipeline leakage prevention](https://scikit-learn.org/stable/common_pitfalls.html). These motivate partition discipline, not a claim that this experiment will succeed. Compatible independent full-input validation and reviewer-defined error costs remain unavailable.
