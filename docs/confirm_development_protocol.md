# CONFIRM development v1 — locked before new fits

8 October 2026. User authorized improvements, with experimental models separate from the app. This is **retrospective development within an already inspected cohort**, not fresh independent validation. Preserve `confirm_external_v1` and all frozen app files byte-for-byte. No promotion into the app is authorized by this experiment.

## Questions and fixed design

1. Can calibration reduce the old four-input model's probability error?
2. Can training on more records, nonlinear models and additional baseline clinical fields improve ranking?
3. Can missing-input handling increase coverage, and what false-alarm cost accompanies a high-sensitivity cutoff?

Keep the original primary complete-case and no-prior-MI/PCI/CABG eligibility. An additional available-input cohort requires age 30–100 and explicit absence of all three histories; missing BMI/LDL/HDL is permitted, but observed values must satisfy the original bounds. Exclude exact four-numeric-input matches to the original source. Keep outcome mapping and its unresolved codebook qualification from the original external experiment.

Three arms: `four_complete` uses age/BMI/LDL/HDL; `clinical_complete` adds sex, htn, dm, chol, famhx, smokecurrent, smokepast, chest_pain, typicality, exertion, sob on those SAME complete-case rows; `clinical_available` uses these 15 fields with missing numeric inputs allowed. Source categories remain opaque nominal codes: no assumed sex or symptom-code meanings and no substitution into the original app. This allows computational research, not a usable clinical input contract. No calcium, CT/echo, stenosis, treatment, outcome, identifier or follow-up fields are predictors. Timing/definitions still require domain review.

Assign each registry ID deterministically using SHA256 of `confirm-development-v1:ID`: first 8 hexadecimal digits / 2^32 yields train <.6, calibration <.8, test otherwise. One patient has the same partition across every arm/target. IDs are used only for splitting, never stored in exported evidence. No rerandomization. These test rows have already participated in the historical transport evaluation; label knowledge limits claims even though new fitting cannot use them.

Within each training partition, three stratified folds (seed 20261008) compare four fixed pipelines by mean Brier loss: standardized logistic C=1; cubic additive splines (4 knots) with logistic C=1; histogram boosting (150 iterations, learning rate .05, 7 leaves, L2=10, minimum leaf 30, early stopping disabled); random forest (150 trees, minimum leaf 20, max_features=1, seed fixed, two threads). Numeric medians and all preprocessing are fitted inside each fold; nominal missing values have their own encoded category; unknown categories ignored. Numeric missingness indicators included. Retain all fold losses; choose lowest training-CV Brier, tie by fixed order. Fit the selected pipeline on training rows only.

Calibrate both frozen source probabilities and the selected model with logistic regression on clipped logits, C=1e6, using calibration rows only. Retain raw and calibrated selected predictions, source raw/calibrated (complete arms), and a training-prevalence constant baseline. No post-test winner selection. Select a diagnostic cutoff on calibration predictions only: largest observed probability meeting sensitivity >=90%. Also report fixed .5. The 90% goal is a research operating-point illustration, not a clinically justified requirement or guaranteed test sensitivity. Reusing calibration rows to choose this cutoff does not provide an unbiased calibration-set performance claim.

Separate `prepare`, `fit`, `evaluate` stages. Save protocol/runner/data/history hashes before fits; freeze selected artifacts, calibration models, cutoffs, CV records and indices before reading test outcomes in the new evaluation stage. Refuse overwrites. Verify historical/app identities before and after stages.

## Reporting and decision

Report every arm/target/comparator: count, positives, AUC, Brier, log loss, average probability, observed prevalence, .5 confusion, diagnostic-cutoff confusion, average precision and five probability-bin reliability table. On each arm use 500 paired row bootstraps for selected calibrated minus source raw (complete arms) or constant (available arm), AUC/Brier difference intervals. Also report paired clinical-complete minus four-complete differences, raw/calibrated selection effects and subgroup descriptive metrics by age (<60/>=60), opaque sex code and any missing numeric input, requiring >=100 rows and both classes. Intervals condition on fitted artifacts and ignore site clustering, fitting and selection uncertainty; no multiple-comparison claims.

No success threshold causes automatic app integration. Improved internal performance is a research candidate. A fresh, compatible cohort plus reviewed input timing/codes and reference-standard definitions is still needed. Raw clinical inputs and registry IDs stay local; exported evidence contains row indices, split roles, labels and predictions only.

Methods: [scikit-learn calibration](https://scikit-learn.org/stable/modules/calibration.html) and [threshold selection](https://scikit-learn.org/stable/modules/classification_threshold.html). Dataset: [CONFIRM, Cademartiri, CC BY 4.0](https://data.mendeley.com/datasets/shntp48zv9/1). Original failed transport results remain authoritative for that frozen model.
