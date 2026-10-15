# Coronary Atlas

A local educational research app for the Multimodal AI Hackathon 2026, Track A. It predicts the supplied CAD, LAD, LCX and RCA labels from 55 clinical observations and maps the estimates onto licensed BodyParts3D anatomy. Baseline models use SHAP explanations; the optional calibrated ensemble uses its own sampled permutation attributions.

The redesigned interface includes two complete recorded examples, searchable observations, dash-based missing-field guidance, a CSV template, 104 atlas meshes, internal heart views, camera presets, vessel isolation and plain-language contribution summaries. [Product research](docs/product_research.md) documents existing alternatives, public feedback and the learner/educator audience hypothesis; it does not claim validated user demand or unique invention.

**Working educational prototype; not clinically validated.** These are disease-label probabilities in a small selected cohort, not future heart-attack risk, measured stenosis percentages, diagnostic findings or localized plaque maps. LCX/RCA held-out sensitivity is only about 40% at the fixed 0.5 threshold.

## Judge quick start

- [Open the live application](https://coronary-atlas-production.up.railway.app) · [Watch the narrated demo](https://youtu.be/opyfTMic1kc) · [Stable judge portal](https://jozai182-coronary-atlas.static.hf.space/index.html). The complete application runs on Railway and does not require the entrant's laptop. Availability depends on the hosting account's remaining credits/plan.
- Repository: https://github.com/jozai193/coronary-atlas.
- Choose **Explore profile A** or **Explore profile B**. Both have all 55 recorded model inputs and immediately compute four outputs. A/B are selected development examples, not independent tests. C/D have been removed from the judge-facing choices.
- **Explore** focuses on the reference heart, four estimates and explanations. Select LAD, LCX or RCA; try the internal view and camera presets. Optional colour, label and tour controls are under **View, colour & anatomy options**.
- **Inputs & reports** contains searchable observations, CSV import and reviewed report assistance. **Start your own case** clears the examples so judges can enter their own de-identified observations.
- **Evidence** contains model comparison, evaluation and separate public ECG references. **Open case summary** provides a worksheet; **Export research result** downloads the current outputs.
- **Import a report photo** runs OCR locally. Confirm each numerical proposal. Echo excerpts require separate case/source review; unreadable measurements remain unknown. **Explore real public ECG references** is separate from the current case.
- No password, API key or account is required. Anonymous A/B predictions passed for all three model variants, alongside desktop/mobile browser checks. If the host is unavailable, use the narrated video or reproduce locally from this repository.

The [six-page technical report](output/pdf/technical_report.pdf) is included. AI assistance: OpenAI Codex / ChatGPT supported research, engineering, testing and documentation; the demo uses Deepgram Aura 2 Orion stock synthetic narration. No inference API key is required to use the app.

See [judge walkthrough](docs/judge_guide.md), [report support and limits](docs/report_autofill_and_summary.md), and [model evidence](docs/accuracy_goal_results.md).

## Run locally

Prerequisites: Python **3.11**, Node.js **22.12+** (Node 24 works), npm and a browser with WebGL support. No dedicated GPU, API key or paid service is required. Commands below run from the repository root. Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/setup_data.py
.\.venv\Scripts\python.exe scripts/verify_artifacts.py
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. Use Explore profile A/B for complete recorded examples. Drag/zoom the heart; click a vessel or its labelled button. Use the explanation tabs and the Evidence view. Both examples were used in development and are not independent evaluation.

For source review, choose **Start clinician review** and inspect A/B before predicting. Their exact tabular source sheets are available there, with input values and separate recorded outcomes. These are not original ECG/echo reports. Regenerate/check them with `python scripts/build_source_review_sheets.py` / `--verify`.

Linux/macOS equivalent (not yet executed here):

```bash
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/setup_data.py
python scripts/verify_artifacts.py
npm --prefix frontend ci
npm --prefix frontend run build
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Bundled model artifacts are trusted project files; never load joblib/pickle files from uploads. The service checks their hashes against metadata before loading. Models and selected anatomy files are included for fast startup. No patient values are persisted by the app; explicitly exported JSON is saved by the user. Operate on synthetic/de-identified observations. The local server has no authentication or clinical data governance for public patient use.

## Development

### Optional calibrated ensemble research model

The **Prediction model** control now offers **Research calibrated ensemble · adjusted display** when its optional dependencies and bundled candidate are installed:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ensemble.txt
```

Restart the backend after installation. The baseline remains the default, and the Railway Docker image installs the optional ensemble dependencies. The ensemble changes all four fitted models, retains the coherence adjustment, and has its own sampled permutation attributions; these are approximate allocations that reconstruct its calibrated probabilities before adjustment. They are not the baseline's SHAP factors. Model switching clears previous outputs, and exported results identify the selected version.

On three matched internal repeats of the same 303 people, mean accuracy across the four targets improved **72.6% → 75.0%** and mean Brier error fell **0.1753 → 0.1650**. These are development results, not an independent or clinical validation. LCX/RCA sensitivity remains low; naturally incomplete profiles and attribution stability remain unvalidated. Feature selection and splines did not pass their separate improvement screens. [Complete results](docs/accuracy_goal_results.md), [frozen ensemble protocol](docs/accuracy_goal_protocol.md), [missing-input protocol](docs/accuracy_missingness_protocol.md), [additional-data audit](docs/accuracy_goal_data_review.md).


Backend terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend terminal:

```powershell
npm.cmd --prefix frontend run dev
```

Vite prints its local URL (normally port 5173) and proxies `/api` to port 8000. Production uses the same origin and requires rebuilding the frontend after changes. If the backend started before `frontend/dist` existed, restart it after the first build. `.env.example` documents the key-free configuration; no environment variables are required.

## Regenerate the dataset analysis and models

```powershell
.\.venv\Scripts\python.exe scripts/setup_data.py
.\.venv\Scripts\python.exe scripts/analyze_data.py
.\.venv\Scripts\python.exe ml/train.py
.\.venv\Scripts\python.exe scripts/create_samples.py
.\.venv\Scripts\python.exe scripts/plot_evaluation.py
.\.venv\Scripts\python.exe scripts/verify_artifacts.py
```

`setup_data.py` verifies or downloads UCI 411 and fails if the source hash changed. It does not overwrite differing raw data. Original data remains in `data/raw/`; cleaned CSV/schema/EDA outputs go to `data/processed/`. The 303-row populated sheet is used; a second, empty sheet is ignored. Sample CSV: `data/sample_patient.csv` (one synthetic profile). CSV inputs accept one row, canonical feature headers, explicit missing cells, and never target labels.

Training uses seed **20261007**, 5 stratified outer folds and 3 inner folds for ROC-AUC selection among regularized logistic regression (C=0.03/0.3), random forest and gradient boosting. All imputation, scaling and encoding are inside fitted pipelines. Four target columns are never inputs. The production models use no oversampling and retain the 0.5 cutoff. A separate bounded experiment evaluates training-only alternative cutoffs without changing production predictions. Constants remain harmless in regularized/partition-based models; no full-dataset feature selection is performed.

`ml/metrics/evaluation.json` contains executed results, fold train/test indices, candidate scores, ROC/reliability points and dispersion. `*_oof.csv` records each held-out row and prediction. `sensitivity.json` is a separate fixed-logistic diagnostic excluding the inconsistent label row, not a tuned replacement headline. `models/metadata.json` records package versions, final configurations and hashes.

| Target | Held-out AUC | Fold AUC SD | Accuracy | Sensitivity | F1 | Brier |
|---|---:|---:|---:|---:|---:|---:|
| CAD | 0.920 | 0.034 | 86.1% | 90.3% | 0.903 | 0.099 |
| LAD | 0.831 | 0.060 | 78.2% | 85.9% | 0.822 | 0.168 |
| LCX | 0.741 | 0.042 | 68.0% | 40.3% | 0.497 | 0.203 |
| RCA | 0.717 | 0.054 | 66.3% | 40.4% | 0.474 | 0.207 |

These evaluate the nested model-selection procedure. Final full-data selection chooses forests for CAD/LCX and logistic regression for LAD/RCA; it is not itself an independent evaluation. Fold SD is not a confidence interval. Bootstrap ranges condition on fixed OOF predictions and omit model-refitting uncertainty. The **55-input application has no external or prospective validation**; the separate reduced-input transport experiments below do not change that.

## Tests and quality checks

Follow-up: [cohort-aware training with separate calibration](docs/cohort_calibration_results.md) completed all 90 three-role splits. LCX showed small, uncertain reduced-input gains; CAD did not outperform locally calibrated learning. All 306 metric groups were independently reproduced, and 11 focused tests passed. The live models remain unchanged. Replay with `python scripts/run_cohort_calibration.py verify` and `python scripts/verify_cohort_calibration.py`; the known-cohort research model is not an unknown-hospital predictor.

Latest additional-data research: [public datasets and primary-paper review](docs/public_data_and_papers_2026-10-13.md) and [executed multi-cohort training](docs/multicohort_results.md). The fixed reduced-input comparison used 1,201 CAD records and target-specific vessel records. Pooling did not reliably improve predictions; the small LCX signal is uncertain and has a sensitivity trade-off. No new research model replaced the 55-input application. Run `python -m ml.multicohort verify` and `python scripts/verify_multicohort.py` to audit the locally preserved trial; original external workbooks/research fits remain excluded from the source bundle.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend audit
```

Backend tests cover prohibited labels, fold partitions, preprocessing isolation, unseen categories, missingness, input errors, probability bounds, deterministic inference, model integrity and SHAP reconstruction. Frontend tests exercise stale results, request errors and disabled edits during inference. Browser evidence and actual tested limits are in `docs/verification.md` and `output/playwright/`.

To regenerate the typed prediction contract after backend schema edits, run `python scripts/export_schema.py`, then `npx --prefix frontend openapi-typescript docs/openapi.json -o frontend/src/generated/api.d.ts` (or run the tool from `frontend` with the corresponding relative paths). To rebuild the technical report PDF, install `requirements-report.txt` and run `python scripts/build_report.py`; visually review its output before publication. The optional Dockerfile is provided; see verification.md for whether a container build was actually tested.

## API

- `GET /health`
- `GET /model/info` - canonical input schema and limitations
- `GET /model/metrics` - original baseline evaluation evidence
- `GET /model/candidates` - optional candidate availability and matched LCX comparisons
- `GET /sample-patients` - synthetic profiles

- `GET /api/held-out/cases` and `GET /api/held-out/cases/{case_id}/{target}` - coarse original-cohort teaching cases and their saved raw outer-fold evidence
- `POST /predict` - body `{"features": {"Age": 42, ...}, "model_variant": "baseline"}`; omit the variant for baseline, or explicitly choose `histgb_lcx_v2` for the research candidate

The original routes also have `/api` aliases; held-out teaching routes are API-prefixed only. Interactive schema: `/docs`; OpenAPI: `/openapi.json`. Age, echo EF, valve assessment, all seven recorded ECG fields and at least 28 available observations are required. Supplying these fields does not establish a complete clinical record or clinical validity. This completeness rule is an engineering guard, not clinically validated. Missing BMI is calculated when weight and height are supplied; other missing inputs are imputed and disclosed. An [internal whole-group masking stress test](docs/input_missingness_stress_results.md) found large changes in LCX/RCA case detection without laboratory inputs and in LAD discrimination without echo inputs. The form and API flag these exact absent-group scenarios; performance for naturally incomplete patients is unknown. Unknown fields, forbidden labels, invalid categories/nonfinite numbers, out-of-cohort numeric values and malformed payloads return 422. Result fields include four displayed probabilities and classes at 0.5, the corresponding raw model probabilities and coherence adjustments, display bands, raw-model SHAP contributions, an input snapshot and a missing-feature list. The optional LCX candidate returns unadjusted probabilities.
The current input guard calculates BMI from weight and height when both are present, rejects a conflicting supplied BMI, and declines numeric values outside the source cohort's observed range. These checks prevent unsupported or internally contradictory estimates; they do not establish a higher predictive AUC. See [input accuracy guard](docs/input_accuracy_guard.md).

## Anatomy, licenses and attribution

BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International. Downloaded from the [official archive](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html); the [current license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) was verified on 7 October 2026. Historical mirrors may carry older license wording. Our asset manifest retains source IDs and file hashes. Native-coordinate OBJ geometry is centered, scaled and rotated at render time; no patient-specific geometry is generated.

LAD: FMA74912; LCX: FMA3895; RCA: FMA3802. The expanded 104 meshes contain 147,474 faces and total about 10.0 MB before HTTP compression. Context now includes cardiac veins, four chamber cavities, valve leaflets and papillary muscles alongside the original heart walls and major vessels. Pale red heart tissue, red arteries and blue veins identify structure types; the separate probability-shading mode maps light-to-dark red only to LAD/LCX/RCA. **Inside heart** reveals internal atlas structures. To re-extract, use the original archive and official `isa_element_parts.txt` with `scripts/prepare_anatomy.py`. Attribution and full provenance: `assets/README.md`.

Dataset: Alizadehsani, R., Roshanzamir, M., & Sani, Z. (2013). *extention of Z-Alizadeh sani dataset*. UCI Machine Learning Repository, [DOI 10.24432/C5461K](https://doi.org/10.24432/C5461K), CC BY 4.0. Original workbook and derived processing are credited separately in `data/provenance.json`.

Original application code: MIT (see LICENSE). Dataset and anatomical assets retain their own attribution licenses. Dependencies retain their upstream licenses.

## AI assistance disclosure

OpenAI Codex assisted official-source research, data analysis, architecture, code, tests, documentation and local verification. The participant must review and understand the work and list **OpenAI Codex / ChatGPT** in Devpost Built With. No clinical expert review is claimed; no human evaluation or sign-off is invented.

## Submission package

Start with `docs/progress.md`, `docs/technical_report.md`, `output/pdf/technical_report.pdf`, the focused `docs/demo_script_judge_cut.md`, `docs/judging_strategy.md` and `docs/submission_draft.md`. The longer `docs/demo_script.md` remains a rehearsal reference. The official deadline is **15 October 2026, 00:15 IST**. Public GitHub publication, the actual 3–10 minute YouTube demo, full-name roster and final Devpost submission remain separate release tasks. One person may belong to only one submitting team; each team may enter only one track.


## Bounded model improvement experiment

Eleven configurations, sigmoid calibration and training-selected cutoffs were evaluated with two repeats of nested validation on the same 303 records. No raw replacement met the prespecified gate. The app's **Model evidence** panel compares cutoff trade-offs, including missed cases and false alarms, with downloadable evidence. That experiment did not change fitted models; the later default coherence layer can adjust displayed probabilities while SHAP continues to explain the raw model outputs.

See [experiment results](docs/model_improvement_results.md), [pre-run protocol](docs/model_improvement_protocol.md), and `ml/experiments/improvement_v1/`. Three evidence-integrity tests audit saved splits, counts and hashes. `python scripts/export_improvement.py` regenerates the UI data from these records. An independent-data compatibility audit found no verified drop-in external cohort; the audited UCI 45 copies under `data/external_audit/` never enter training. They retain CC BY 4.0 attribution in the results document.


## Guided demo and broader research — 8 October 2026

**Explore real public ECG references** adds twelve separate PTB-XL cases with calibrated waveform excerpts, original report strings and source annotations. Selecting a reference leaves the current profile and CAD estimates unchanged. These are different participants, without paired echo/angiography outcomes for the app's cases. See [PhysioNet use and verification](docs/physionet_use_results_2026-10-14.md) for acquisition, the bounded MIMIC parser check and remaining credentialed-data requirements.

**Start guided case** runs a synthetic example through five steps: inputs, vessel orientation, actual SHAP contributions, and the matching evaluation evidence. Measurement links open the corresponding form field. Editing inputs or changing model clears stale results. The heart now has mesh-anchored vessel labels, a three-vessel tour, automatic focus views, keyboard controls and reduced-motion support; its camera fits narrow screens.

**Try four cases** is a separate quiz using deliberately selected original-cohort held-out rows and their saved raw outer-fold probabilities. It includes both model successes and errors, shows only coarse observations, and never attributes a full-data SHAP explanation to an outer-fold prediction. After revealing a vessel case, **Inspect vessel on reference heart** locates LAD, LCX or RCA in a reference-only view; saved fold probabilities are never painted onto that heart. It is not external validation or a representative performance sample. See [case method and privacy boundary](docs/heldout_case_mode.md).

Open **Prediction model** above the workspace to compare the optional experimental LCX HistGradientBoosting model. The original fitted CAD/LAD/RCA models remain the same, but displayed values can differ between variants: the default baseline uses a CAD/vessel coherence adjustment, while the optional candidate is unadjusted. The UI shows both runs, including missed cases and false alarms. Baseline responses and exports carry `model_version=1.0.0+coherence-v1`; candidate responses carry `1.0.0+histgb-lcx-v2`. Candidate startup verifies its artifact and linked evidence hashes. Missing candidate manifest disables the option; corrupted packaged evidence fails startup rather than being silently used.

The broad family experiment completed 480 candidate jobs (1,920 individual inner/outer fits), including regularized linear models, forests, boosting, LDA, SVM, MLP, CatBoost and a fixed ensemble. The general broad selector was not a universal improvement. The optional LCX candidate's mean AUC was .744 versus .728 and Brier .200 versus .206; mean recall rose from 38.2% to 53.8%, while specificity fell from 85.3% to 81.5%. These are post-search diagnostics on reused rows, not an unbiased winner estimate. Its serialized artifact's explanations reconstructed all 303 fitted-row outputs; those fidelity checks are separate from held-out performance.

A separate fixed TabICLv2 experiment completed 40 outer fits: CAD mean AUC .930 versus .910 and Brier .090 versus .105. LAD/LCX probability-quality screens passed; RCA did not. It remains a research result, separate from application predictions. Its checkpoint is not bundled with the application. A 12-case explanation pilot completed in 266 seconds, with each approximate explanation taking 16–19 seconds; reconstruction does not prove approximation convergence. See [the runtime and explanation report](docs/tabicl_explanation_results.md). The input-group audit adds a UI comparison for core observations, ECG, laboratory and echo findings using a fixed logistic diagnostic; it does not establish the value of imaging or clinical acquisition.

Read [broad-search results](docs/broad_search_results.md), [TabICL results](docs/tabicl_results.md), [input-group audit](docs/modality_audit_results.md), and the [research opportunity matrix](docs/prediction_opportunities.md). The matrix distinguishes tested approaches from untested and unavailable avenues. UCI 412 duplicates the same 303 records; AngioCAD is a new invasive-angiography cohort with **13** well-mapped inputs, not a drop-in 55-input cohort. The technical report summarizes the research follow-ups, with detailed experiment reports linked here.


## Independent-cohort follow-up — 8 October 2026

A separate age/BMI/LDL/HDL model trained only on the 303-row source was tested against a newly acquired public CONFIRM workbook (27,125 records). The primary complete-case CAD analysis included 7,095 eligible records: AUC .656, Brier .409, mean prediction 69.6% versus 18.0% observed disease. The result is negative for probability transfer and is not promoted into the app. It is not validation of the current 55-input model. A pre-scoring endpoint-mapping correction, CT versus invasive-angiography differences, codebook assumptions, exclusions and all four target results are documented in [the external experiment report](docs/confirm_external_results.md). Four read-only evidence tests pass. That external experiment did not change the then-current app or fitted-model artifacts; the later coherence update changed the baseline display layer.
## Separate CONFIRM development follow-up

The failed source-only transport experiment led to a separate, staged development study using calibration, larger training partitions, additional clinical fields and missing-input handling. On matched CAD development-test patients, AUC increased from .658 for the frozen source model to .789 for a calibrated 15-input CONFIRM-trained model; Brier error decreased from .411 to .119. These are **internal development results on an already inspected cohort**, not new independent validation. That study did not change the app or its fitted-model artifacts. A later coherence update changed the baseline display layer. See [the results and limitations](docs/confirm_development_results.md) and [the frozen design](docs/confirm_development_protocol.md).

The subsequent [training-only error audit](docs/confirm_error_followup_results.md) found no replacement meeting its fixed improvement screen. A [leave-site-code-out audit](docs/confirm_site_results.md) tested additional robustness without reusing development-test patients. The [six-page report](output/pdf/technical_report.pdf) now includes the research follow-ups; [completed work and remaining release steps](docs/next_steps_closeout.md) distinguish executed checks from outstanding publication, recording and human review.

## New invasive-angiography population — 9 October 2026

[AngioCAD](https://doi.org/10.5281/zenodo.15826856) supplied 413 segment-labeled patients from another center; 377 have clinical features. A [pre-score frozen protocol](docs/angiocad_external_protocol.md) matched only 13 high-confidence source inputs, trained four fixed logistic models on the original 303 patients, then evaluated them once on the new cohort. Among primary eligible, interpretable rows, CAD/LAD/LCX/RCA AUC was **.781/.723/.709/.687** and Brier **.144/.196/.191/.234**. At the fixed 0.5 threshold, LCX missed 54/90 positives and RCA missed 106/155. The **Model evidence** panel now exposes these separate transport results beside the original-cohort evidence and names the different input contract. The [full report](docs/angiocad_external_results.md) gives mapping, exclusions, denominator changes, uncertainty and prespecified sensitivities; `python scripts/verify_angiocad_external.py` independently reproduced saved-prediction metrics and hashes. The acquired clinical workbooks stay local and are excluded from source packaging. This is a transport test of a **separate 13-input model**, not external validation of the current app or a clinical-use claim.

## CAD–vessel coherence and shared-label experiments

A pilot-informed probability projection enforced `CAD >= LAD, LCX, RCA` on four jointly held-out baseline outputs. Mean four-target Brier fell by only **0.001198** across two five-fold repeats of the **same 303 patients**; 79 and 42 contradictory probability vectors became coherent. Its prespecified engineering screen passed, and a disclosed baseline serving layer now applies this adjustment. The one contradictory source-label row was retained. Original SHAP values explain the raw fitted-model probabilities, not projected outputs. The adjustment has no independent validation. See [coherence results](docs/coherence_projection_results.md) and the [protocol](docs/coherence_projection_protocol.md).

A separate fixed four-output forest was tested against matched target-specific baseline folds. RCA mean AUC rose **0.0211** and Brier fell **0.00478**, but repeat-one recall fell **0.0877**, breaching the prespecified screen. No target met that screen and no multitask model was promoted. The forest and projection were not evaluated together. See [multitask results](docs/multitask_results.md) and the [protocol](docs/multitask_protocol.md). Both experiments reuse the original cohort; neither resolves the need for an unused compatible invasive-angiography cohort.

## China cohort and reliability audit — 9 October 2026

A frozen **separate 14-input CAD** comparison tested source-only logistic regression and InterpretML EBM on 553 new Chinese hospital patients. EBM did not improve AUC (.664 versus .674) or Brier error (.333 versus .307); both substantially overpredicted the observed 36.3% prevalence. The two prespecified sensitivity checks retained that conclusion. The app's Model evidence panel now shows the negative result, error counts and downloadable metrics. This is not validation of the 55-input app or its 55-input EBM candidate. See [the full result and limitations](docs/peerj_external_results.md) and [frozen protocol](docs/peerj_external_protocol.md).

Run `python -m ml.peerj_external verify` for saved-model, source-fold, primary/sensitivity metric and bootstrap checks, and `python scripts/verify_peerj_external.py` for subgroup/reliability and UI-copy checks. Verification needs no optional InterpretML install or raw external supplement. `python scripts/export_peerj_evidence.py` regenerates the exact UI evidence copy. Raw acquired records remain outside the source bundle.

Requests now time out after 30 seconds and release controls for retry, including when a response body stalls. Git preserves exact artifact bytes across checkout/export through `.gitattributes`, keeping the existing evidence hashes meaningful. Windows tests from a Git export with `core.autocrlf=false` exercise startup and packaged integrity; this does not claim execution on Linux.

## Local calibration and learning — 10 October 2026

The [fixed China development follow-up](docs/peerj_adaptation_results.md) found a concrete probability-quality improvement: with 64 locally labeled rows per fit, sigmoid recalibration reduced mean Brier error from .3073 to .2121 versus .2358 for a local-prevalence constant. A fixed local logistic model using 442–443 rows per fit raised mean within-fold AUC from .6743 to .7823, with Brier .1842. All 60 fits used disjoint adaptation/evaluation rows within each fold. **This reuses the inspected 553-person cohort; it is not new external validation of the 55-input app.** At .5, the primary calibrator missed 145/155 of 201 positives across two repetitions; the probability gain does not imply safer detection. Models remain research-only.

The China evidence card now has a collapsed development follow-up with all primary comparators, the missed-case cost and downloadable results. Verify with `python -m ml.peerj_adaptation verify` and `python scripts/verify_peerj_adaptation.py`; regenerate UI evidence with `python scripts/export_peerj_adaptation.py`. The protocol and frozen snapshots are preserved in `output/research/peerj_adaptation_v1/`. No optional EBM package is needed to verify the saved development outputs.

## Separate training, calibration and operating points

The [next frozen development study](docs/peerj_operating_results.md) used 331–332 model-training, 111 calibration and 110–111 evaluation rows per split. Local learning plus calibration gave Brier **.1819** versus source **.3073** and training prevalence **.2316**; local training alone achieved **.1832**, making the extra sigmoid benefit small and uncertain. At exploratory calibration-selected 90% sensitivity cutoffs, local/source evaluation sensitivity was **89.1%/88.3%**, specificity **43.3%/26.6%**. The evidence card shows missed cases, false alarms and downloadable results for all targets. These are repeated development results on the same 553 people, not independent validation or a clinically approved cutoff; the app's predictions remain unchanged.

Run `python -m ml.peerj_operating verify` and `python scripts/verify_peerj_operating.py`; regenerate the UI copy with `python scripts/export_peerj_operating.py`. The [Beijing source audit](docs/beijing_source_audit.md) preserves a newly found public cohort unscored because the final study population and CAD endpoint cannot be reconstructed reliably. No reviewer-defined operating objective or acceptable error costs have been supplied.

## Doctor feedback follow-up — 13–14 October

[Relayed informal feedback](docs/doctor_feedback_2026-10-13.md) prompted clearer example provenance, unknown values and anatomy. The final judge-facing A/B cases contain all 55 recorded inputs, selected by contrasting source labels and original row order before scoring. They replace the earlier incomplete synthetic demonstrations. Missing manual/CSV values remain **—**, distinct from supplied zero codes, with computation-time imputation disclosed where permitted by the completeness guard. Source records, model weights and historical evaluation remain unchanged. These development examples are not new accuracy evidence.

An **ECG and echo behind this estimate** panel shows the exact supplied findings separately from CAD/vessel probability. EF, RWMA and VHD are inputs, not model-predicted echo diagnoses. The existing modality audit does not justify a blanket echo override for all four labels. Informal feedback remains distinct from a completed qualified anatomy/input review or clinical sign-off.


## Smoking, alcohol and lipid review

The reviewer workspace prominently shows modeled current/former smoking and LDL/HDL/triglycerides. Reported smoking exposure, alcohol, total cholesterol and lifestyle notes are separate browser-only review context, included in summaries and explicit exports but excluded from the trained model. New-case actions clear those notes. [Field scope and verification](docs/smoking_alcohol_lipid_context.md).
