# Cohort-aware training and separate calibration

Fixed 13 October 2026 before this trial's fitting/scoring, after the negative multi-cohort pooling experiment. This is a follow-up on already inspected patients, not a fresh independent test. No original model, outcome, prior result or live prediction rule will change.

## Source alignment and remaining limits

Use the exact hash-verified mappings and eligible endpoint sets of `multicohort_protocol.md`: CAD 11 shared fields across UCI/AngioCAD/Anhui; LAD/LCX/RCA 13 fields across UCI/AngioCAD. There is no newly inferred code, unit, threshold, timing or echo value. Preserve the prior glucose/lipid/WBC conversions and all previously recorded selection/endpoint caveats, including Anhui's extreme WBC. Unit conversion does not establish clinical equivalence. The newly acquired ICD workbook was also inspected for hidden dictionaries, comments, named ranges and validations: no additional code definitions were found. CM-CAD LAD remains left atrial diameter. Neither new source is added to fitting.

The next test addresses whether differences in cohort baseline probability can be accommodated without distorting common feature effects, and whether probabilities improve with a separately fitted local calibration. [Falconieri et al.](https://doi.org/10.1002/bimj.201900075) motivate examining center effects; their random-intercept simulation is not validation of our fixed-intercept implementation. [BMJ updating guidance](https://doi.org/10.1136/bmj.i3140) motivates explicit local recalibration comparisons. Do not assume either method helps.

## Three disjoint row roles

For every target/destination cohort, use two shuffled five-fold StratifiedGroupKFold repeats, seeds 20261013/20261014. Group exact shared-input fingerprints. The outer fold is evaluation (about 20%). Split the remaining destination pool using four-fold StratifiedGroupKFold with seed 20261015 + 100*repeat_index + outer_fold; its first held-out fold is calibration (about 20% overall), and the rest is local ranker training (about 60%). This selection is fixed, not rerandomized. Stop if any role has only one class. Each person is evaluated once per repeat; two predictions are not two independent patients.

Remove all destination calibration/evaluation fingerprints from every other training cohort. Local training, calibration and evaluation fingerprints must be pairwise disjoint. Save exact roles before fitting. Destination evaluation features/labels cannot enter preprocessing, fitting, calibration or cutoff selection. Fingerprints are used only for conservative duplicate exclusion, not predictors or patient identity claims.

## Fixed base learners and calibrated arms

Use four fixed reduced-input rankers, no hyperparameter/feature/family search:

1. `local`: existing LogisticRegression(C=.03, max_iter=3000) pipeline fitted only on destination training rows.
2. `pooled`: the same pipeline fitted on local training plus all eligible other-cohort training rows.
3. `cohort_intercepts`: common feature slopes with an unpenalized intercept for each observed training cohort. Minimize sum binary log loss + ||beta||²/(2*.03), using training-only preprocessing from the pooled pipeline. L-BFGS-B, maxiter=3000, ftol=1e-10, gtol=1e-6; abort if convergence fails. The known cohort is training/deployment context metadata, not a clinical feature or disease label. Prediction rejects unknown cohort names. This is a fixed-effects model, not a random-effects model or an unknown-hospital predictor.
4. `transfer_pooled`: the same ordinary logistic pipeline trained only on the other cohorts; no destination ranker-training rows. This includes a genuinely omitted destination in base fitting, but its locally calibrated counterpart uses destination labels and is adaptation, not untouched external validation.

All ordinary models use the existing numeric median imputation/standardization and categorical mode imputation/one-hot encoding fitted on their exact training rows. No oversampling, class weighting or destination-fitted scaling. Each base has a raw arm and a sigmoid arm; fit LogisticRegression(C=1,max_iter=3000) on clipped base-probability logits using only destination calibration rows. Keep negative slopes if they occur and report them. A calibration-dependent AUC reversal must not be described as a calibration-only gain. Also include the destination training-prevalence constant.

For every nonconstant arm save fixed .5 decisions and an exploratory cutoff chosen solely on calibration positives to reach empirical 90% sensitivity: largest positive calibration score meeting that target, ties included, as in `peerj_operating_protocol.md`. The calibrator and cutoff may share calibration rows; the separate evaluation role assesses the complete procedure. No reviewer-endorsed cutoff or rule-out claim exists.

## Primary comparisons and reporting

Primary additional-data comparison: `cohort_intercepts_sigmoid` versus `local_sigmoid`, using equal destination training/calibration budgets. Primary probability outcome is Brier, with AUC/log loss and errors reported alongside. Also compare cohort-intercepts versus ordinary pooling, and each sigmoid versus its raw base, so improvements from local calibration cannot be attributed to adding patients. Report every arm, cohort, target and repeat. Include accuracy, sensitivity/specificity, precision/F1, confusion counts, probability means and five-bin reliability. At the 90% illustration, report actual evaluation sensitivity and false alarms; the target is not a guarantee.

Report pooled out-of-fold AUC alongside mean within-evaluation-fold AUC (fold scores are produced by different fits). Conditional 1,000-resample patient bootstrap intervals for Brier differences average each person's two repeat errors first; they omit fitting, center, selection and endpoint uncertainty. Do not pool multiple target outcomes or repeats as independent people. Show equal-cohort summaries and individual results; no automatic winning score or replacement. No final all-row refit or deployment in this trial.

## Execution and verification

Separate prepare, fit, evaluate and read-only verify. Refuse overwrites and freeze raw/protocol/runner/dependency/prior-evidence hashes and exact partitions. Fit stores models, calibration predictions/labels, slopes/intercepts and selected cutoffs before evaluation. Evaluation cannot refit or retune. One numerical thread, ten-minute fit cap, abort on any failed optimizer/fit. Keep private fitted objects local and publish indexed outcomes/predictions plus aggregate evidence. Verify roles, exact fitted-prediction/cutoff replay, all metrics and historical preservation. Test evaluation-feature/label mutations cannot affect fitted parameters/calibrators/cutoffs, fixed-intercept behavior and unknown-cohort rejection; independently reproduce saved metrics/role coverage in a separate script.
