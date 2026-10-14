# TabICLv2 fixed-candidate evaluation protocol

Prepared before the TabICL target results were computed. This is a fixed, untuned, local-model comparison on the already inspected Z-Alizadeh Sani cohort. It is not external validation, a clinical evaluation, or permission to replace a production model.

## Question and evidence boundary

Does the official TabICLv2 classifier, run with its documented default ensemble size and only resource-related CPU settings changed, improve repeated held-out probability performance over the existing nested baseline selector on this 303-row, 55-input dataset?

The official TabICL repository describes pretraining/benchmarking from 300 training rows and says generalization below 300 rows has not been tested. This is an empirical evidence boundary, not an API minimum: the installed estimator accepts smaller inputs. In this experiment, outer training sets have about 242 rows, below that boundary. The small feasibility run showed that the implementation can fit/predict at 161, 242, and 303 rows; it did not evaluate real labels or model quality. The nested result must therefore be described as an exploratory below-support-regime stress test.

## Fixed model and data

- Source: the immutable 303-row UCI 411 workbook, SHA-256 `739343245c2ba578b541370217531750d8e936022f928b83e0d91756caa3ff0b`.
- Inputs: exactly `ml/schema.py::FEATURES` (55 columns). The four outcome columns are prohibited from X; each target fit receives only its own binary y.
- Outcomes: `Cath == CAD` for CAD and `LAD/LCX/RCA == Stenotic` for vessel tasks, matching `ml/improvement.py`.
- Estimator: TabICL 2.2.0 with the official TabICLv2 checkpoint `tabicl-classifier-v2-20260212.ckpt`, checkpoint SHA-256 `bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0` (110,368,038 bytes).
- Fixed estimator settings: `n_estimators=8` (official default), `batch_size=1` (lower memory use), `device="cpu"`, `n_jobs=2`, `random_state=outer_seed + outer_fold`, `allow_auto_download=False`. Other estimator parameters remain at package defaults. Input is the raw schema DataFrame; categorical fields arrive as strings according to `read_data()` and TabICL applies its documented preprocessing.
- Runtime: Python 3.11.5; TabICL 2.2.0; PyTorch 2.10.0+cpu; scikit-learn 1.9.1; two CPU threads. No CUDA device was available. The official model repository marks both the code and checkpoint BSD-3-Clause. Do not treat this license as a clinical or dataset permission.

## Repeated held-out evaluation

- Use the same two seeds as the existing experiment: `20261007` and `20261108`.
- For each target and seed, use five shuffled stratified outer folds (`StratifiedKFold(5, shuffle=True, random_state=seed)`). Fit once per outer fold on that fold's training rows and predict its held-out rows. This fixed candidate has no hyperparameter, model-family, calibration, or threshold selection, so inner fits are unnecessary.
- Reuse the saved baseline-selector probabilities in `ml/experiments/improvement_v1/{cad,lad,lcx,rca}_repeat_{1,2}.csv`. Before computing metrics, assert that the regenerated outer fold number and y match each baseline row exactly. This pairs each fixed TabICL outer probability with the already saved nested baseline probability on the same row and split.
- Save all outer folds, target labels, per-row held-out probabilities, repeat-level metrics, elapsed fit/predict time, source/checkpoint/package hashes and eligibility screens. No outer result is used to modify the candidate.
- Report ROC-AUC, average precision, Brier score, log loss, and the existing fixed 0.5 metrics. The 0.5 cutoff is not refit. The experiment does not tune a clinical operating threshold.

## Prespecified engineering screens

Use the same two screens defined in `docs/broad_search_protocol.md`, comparing TabICL with the saved nested baseline selector for each target:

- Raw-predictor screen: mean two-repeat AUROC gain at least `0.015`, neither repeat's AUROC lower, and mean Brier increase no greater than `0.005`.
- Probability-quality screen: mean Brier improvement at least `0.005`, and neither repeat's AUROC more than `0.01` lower.

These are engineering screens only. Passing would nominate a candidate for a separate review; it would not establish statistical significance, independent validity, clinical utility, explanation fidelity, or release readiness. Failing closes this fixed TabICLv2 comparison without a post-hoc sweep.

## Known limitations

The cohort has already been used for product/model development, so repeated CV is not fresh evidence. Two repeats reuse the same people. There are no verified patient/site/time identifiers for stronger group or temporal splitting. Published performance on this same cohort is not an independent comparator. The exact UCI 412 audit confirms it is the same 303 records and must not be pooled. The below-300 training sizes are outside the authors' tested regime. No external compatible cohort is available in the current audit.
