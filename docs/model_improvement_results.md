# Model improvement investigation — 7 October 2026

The bounded experiment found that the low vessel recall is partly a decision-cutoff problem. More cases can be detected, with substantially more false positives. It did not establish a generally better replacement predictor or remove the need for independent validation.

## Executed comparison

Protocol: `model_improvement_protocol.md`, written before the run. Eleven configurations, two repeats of five outer folds, three inner folds, four targets. Selection, preprocessing, cutoff selection and sigmoid calibration stay inside each outer training partition. The same 303 observations appear in each repeat; these are not 606 independent people. Previously inspected source data and original outer results make this exploratory internal validation.

The first repeat reproduces the original baseline AUC, Brier, recall and specificity exactly. The table below averages metrics across the two repeats; it does not pool repeated observations as independent patients.

| Target | Baseline AUC | Expanded AUC | Calibrated expanded AUC | Baseline Brier | Expanded Brier | Calibrated expanded Brier |
|---|---:|---:|---:|---:|---:|---:|
| CAD | .910 | .905 | .909 | .1045 | .1121 | .1026 |
| LAD | .829 | .807 | .822 | .1683 | .1766 | .1641 |
| LCX | .728 | .732 | .739 | .2061 | .2092 | .2014 |
| RCA | .708 | .701 | .704 | .2080 | .2124 | .2073 |

No expanded raw procedure met the prespecified replacement gate. All four calibrated procedures met the gate for further consideration relative to their corresponding expanded raw procedure. **That is not an automatic deployment decision:** the expanded raw procedure is often worse than the existing baseline. Against the baseline, calibration's mean Brier gains are only .00194, .00417, .00464 and .00067 respectively. No gain reaches the protocol's .005 magnitude when compared with baseline. This baseline comparison is the post-run deployment rationale, not a rewritten experimental gate. No statistical significance is claimed. No calibrated production artifact or calibrated SHAP explanation was deployed.

## Decision-cutoff result

Using the baseline model-selection procedure, choose a cutoff from inner out-of-fold predictions that maximizes specificity while achieving at least 80% recall **on training rows**. Apply that cutoff once to the untouched outer test fold. The target is exploratory and can fail out of sample.

| Target / run | Default recall | Alternative recall | Default specificity | Alternative specificity | Default precision | Alternative precision | Missed cases: default → alternative | False positives: default → alternative |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LCX / 1 | 40.3% | 84.9% | 85.9% | 56.0% | 64.9% | 55.5% | 71 → 18 | 26 → 81 |
| LCX / 2 | 36.1% | 77.3% | 84.8% | 52.2% | 60.6% | 51.1% | 76 → 27 | 28 → 88 |
| RCA / 1 | 40.4% | 80.7% | 82.0% | 56.1% | 57.5% | 52.6% | 68 → 22 | 34 → 83 |
| RCA / 2 | 35.1% | 71.9% | 85.7% | 54.0% | 59.7% | 48.5% | 74 → 32 | 27 → 87 |

Mean recall rises from 38.2% to 81.1% for LCX and 37.7% to 76.3% for RCA. Mean specificity falls from 85.3% to 54.1% for LCX and 83.9% to 55.0% for RCA. Probabilities and AUC are identical across cutoff policies. Increasing recall alone does not establish greater clinical utility.

The app now includes **Model evidence → Catch more cases. See the cost.** Users can compare all four targets, both validation runs and three policies (default, balanced accuracy, training recall target). Missed cases, false alarms, precision and specificity have equal prominence. The downloadable evidence is derived from the saved experiment with source hashes. The original patient probabilities, 0.5 classes and SHAP explanations remain in use.

## Independent-data audit

- [UCI Heart Disease, dataset 45](https://archive.ics.uci.edu/dataset/45/heart+disease): official CC BY 4.0 archive downloaded and inspected, SHA256 `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc`. The raw 76-attribute schema contains vessel segments, which the familiar processed 14-column version omits. The archive's `WARNING` explicitly identifies corrupted raw Cleveland data. Parsing produced 294 name-delimited chunks, only 282 with the expected token count; a valid count does not prove valid values. Hungary has 294, Switzerland 123 and Long Beach 200 structurally complete records, but important fields/labels are missing or unresolved. Hungary's proximal LAD is missing in 236/294 records. Source `ask-detrano` also flags anomalous codes.
- The schemas cannot be merged by column resemblance: total cholesterol is not LDL; binary fasting glucose >120 is not continuous FBS; exercise maximum heart rate is not resting pulse; radionuclide ejection fraction is not EF-TTE. The source lacks much of our 55-field laboratory/echo/input contract. Vessel codes 1/2 require an authoritative definition before harmonizing with Normal/Stenotic. Missing vessel measurements must never become normal labels. No external records entered training or evaluation.
- [UCI Z-Alizadeh Sani, dataset 412](https://archive.ics.uci.edu/dataset/412/z+alizadeh+sani) is another 303-record dataset from the same named source family; it is not established as an independent cohort and cannot be counted as new evidence without record-level provenance and overlap checks.
- [STAFF III](https://www.physionet.org/content/staffiii/1.0.0/) is a controlled coronary balloon-occlusion ECG dataset. [ARCADE](https://pmc.ncbi.nlm.nih.gov/articles/PMC10764944/) is coronary angiography image data. Neither supplies a verified drop-in equivalent of this app's paired clinical inputs and four labels. They may support a separately scoped imaging/ECG project; they do not externally validate this predictor.

The UCI 45 archive and reproducible audit are under `data/external_audit/`; inspection code is `scripts/audit_external_data.py`. Attribution: Andras Janosi, William Steinbrunn, Matthias Pfisterer and Robert Detrano, DOI [10.24432/C52P4X](https://doi.org/10.24432/C52P4X), CC BY 4.0. Audit copies are excluded from all model input paths.

## What would remove specific evidence gaps

1. Obtain an independent, de-identified cohort with the same pre-test measurement definitions, collection timing and angiographic vessel labels. Freeze the existing pipelines and evaluate before any adaptation. If adaptation follows, keep a further untouched test cohort.
2. Ask a qualified domain reviewer to reconcile ambiguous source units/labels and check vessel mappings. Record actual review outcomes; software cannot manufacture them.
3. Define the intended educational task and measure learner comprehension and interpretation errors. For any later clinical use, threshold choice needs a justified error-cost objective and appropriate prospective evaluation.

There is no supported route to a model with zero limitations. A stronger hackathon submission can demonstrate honest evaluation, useful interaction and a defensible improvement rather than conceal failures or advertise unvalidated accuracy.

## Reproducibility and verification

- Full evidence: `ml/experiments/improvement_v1/{cad,lad,lcx,rca}.json`, eight row-level CSVs, `summary.json`, and `run_manifest.json`.
- Experimental runner: `ml/improvement.py`. Its source, protocol, dataset and production-metadata hashes are recorded. It resumes completed target files; do not edit code/protocol or mix outputs from different runs. Preserve the current folder before a genuinely fresh rerun.
- Export: `python scripts/export_improvement.py` checks source/protocol/production hashes before generating `frontend/src/generated/improvement.json`.
- `tests/test_improvement.py` verifies all inner/outer partitions, coverage, saved fold cutoffs, every displayed confusion matrix/rate, source hashes and original-baseline reproduction. CSV verification uses round-trip float parsing.
- All 25 Python tests pass (four existing dependency deprecation warnings). Seven frontend tests pass, including target/run switching and updated missed-case/false-positive counts. Production TypeScript/Vite build passes; existing large Three.js chunk warning remains.
- Real Chrome browser verified desktop and 390px mobile layout without horizontal overflow, RCA run 2 values, evidence download (HTTP 200, version improvement_v1), and a successful synthetic-profile prediction after adding the panel. Screenshots: `output/playwright/threshold-lab-desktop.png` and `threshold-lab-mobile.png`. Fixed disclaimer appears within tall element screenshots as a viewport overlay; content is reachable by scrolling.

Method references: scikit-learn [decision thresholds](https://scikit-learn.org/1.5/modules/classification_threshold.html) and [probability calibration](https://scikit-learn.org/stable/modules/calibration.html). Threshold tuning changes decisions; it does not improve the underlying ranking. Calibration must be evaluated with data excluded from fitting.
