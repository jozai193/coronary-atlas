# Multi-cohort training and transport experiment

Frozen 13 October 2026 before this experiment's fits or scores. This is development on previously inspected UCI, AngioCAD and Anhui patients, not a fresh independent validation or a promoted replacement for the 55-input app. New public-source candidates are audited separately; none is silently added without a defensible label/field mapping.

## Question

Does learning from additional cohorts improve predictions over training on one cohort, and is merging better than averaging study-specific models? [Patil and Parmigiani](https://doi.org/10.1073/pnas.1708283115) motivate multi-study ensembles; [Guan et al.](https://arxiv.org/abs/1905.07382) show that merging versus ensembling depends on heterogeneity. Their settings/results do not establish a benefit for coronary classification. [BMJ evaluation guidance](https://doi.org/10.1136/bmj-2023-074819) and [TRIPOD-Cluster](https://doi.org/10.1136/bmj-2022-071058) motivate withholding whole cohorts as well as reporting within-cohort development results.

## Data and endpoint contract

Reuse immutable, hash-verified files and exact mappings/primary eligibility from `angiocad_external_protocol.md` and `peerj_external_protocol.md`. Retain all 303 UCI rows and supplied labels, including the contradictory row. AngioCAD: require prior 13-input primary eligibility and unambiguous main-vessel endpoint for each target; no inferred normal labels for missing/boundary values. Anhui: all 553 previously inspected rows, including the WBC anomaly. Existing acquisition timing, units, spectrum and >=50 versus >50 limitations remain. AngioCAD and original source are different Iranian centers; Anhui is a different Chinese center. Anonymous data cannot prove identity separation.

CAD uses exactly 11 shared fields: Age, Sex, BMI, DM, HTN, FBS, TG, LDL, HDL, WBC, PLT. Vessel tasks use the prior 13 AngioCAD fields (those 11 plus Current Smoker and CR). Sex/DM/HTN/smoking use fixed prior categorical mappings. All other fields, IDs, hospital membership, catheterization results, vessel labels, interventions, medications and Gensini scores are excluded from inputs. No inferred ECG or echo inputs.

Before fitting, report exact shared-input fingerprint collisions within/between cohorts. Reject cross-cohort training/test matches conservatively and group identical within-cohort input vectors into one fold. Fingerprints are not global patient identity verification. Save internal row indices only; do not publish patient identifiers or raw feature rows.

## Fixed learners and arms

One logistic family only: numeric median imputation, StandardScaler; categorical most-frequent imputation, OneHotEncoder(handle_unknown='ignore', sparse_output=False); LogisticRegression(C=.03, max_iter=3000, random_state=20261013). All transforms fit only on that model's training rows. No SMOTE, synthetic rows, feature selection, model search, class balancing, calibration or cutoff search. Four arms for within-cohort predictions:

1. `local_only`: train only the destination cohort's current training fold.
2. `pooled`: train that fold plus all other eligible cohorts, equal weight per patient.
3. `study_balanced`: same rows, each cohort contributes equal total weight; total sample weight equals training-row count.
4. `study_ensemble`: fit one logistic model per training cohort and take the equal arithmetic mean of probabilities. No fitted ensemble weights.

Study balancing weights the classifier loss; pooled preprocessing is unweighted and fitted only on the combined training rows. There is no cohort-specific normalization or destination-fitted transform.

## Splits and comparisons

Primary transport assessment: leave one complete cohort out, fit pooled/balanced/ensemble on all remaining cohorts, evaluate the omitted cohort. Also save each single-training-cohort comparator. CAD has three held-out cohorts; each vessel has two, so ensemble and pooled coincide with the sole remaining study for vessel transport. Do not claim those are independent method wins. No omitted-cohort outcomes/features enter fitting or weighting. Cross-cohort matches are removed from the training side only.

Secondary augmentation assessment: within each cohort, use StratifiedGroupKFold(5, shuffle=True, random_state=20261013), grouping exact input fingerprints. Compare all four arms on the same held-out rows. Added cohorts are available only as training data; remove any shared-input match with the current held-out set. Each person gets one prediction per arm/task, not additional independent patients. This tests additional-data benefit within these observed cohorts and is not prospective/new-cohort evidence. Abort if any fitting/evaluation role lacks either class.

At fixed .5, report per-cohort AUC, average precision, Brier, log loss, accuracy, sensitivity, specificity, precision, F1 and confusion counts. Include training-prevalence constant baseline, mean probability and five-bin reliability. Preserve every arm/cohort, not a favorable subset. Headline differences are study-balanced minus local-only Brier/AUC for within-cohort augmentation, and pooled/balanced/ensemble versus single-study comparators for transport. Report unweighted cohort averages and every individual result; do not hide a cohort harm behind a pooled metric. Conditional paired 1,000-resample patient bootstrap Brier differences omit refitting, site and post-search uncertainty.

No automatic promotion. A research signal requires lower Brier and nondecreasing AUC in every observed cohort for that target; even that does not validate the 55-input app. Retain a final all-eligible-data research fit for reproducibility, explicitly unsuitable for evaluating those training people. No explanation or live deployment claim is made for it.

## Evidence and limits

Separate prepare, fit/evaluate, and read-only verification; refuse overwrites. Save protocol/runner/raw/historical artifact hashes, exact partitions and training-role indices, fitted research models, all row-level outcomes/probabilities with generated indices, metrics, timing and package versions. Verify no target/test row entered any model fit, reconstruct every metric independently from saved predictions, and compare historical hashes. One numerical thread, fixed 10-minute fit budget; stop on failures rather than retune. Existing app models and prior results remain immutable. Raw additional cohorts and fitted research artifacts are excluded from the submission bundle; aggregate/row-index evidence and reproducible code are included.
