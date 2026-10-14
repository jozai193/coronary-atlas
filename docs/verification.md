# Verification ledger

## 13 October 2026: cohort-aware calibration follow-up

The new `cohort_calibration_protocol.md` was frozen before fitting/scoring, after reviewing the earlier pooling failure. Existing raw inputs, endpoint eligibility and unit mappings were retained. An extra workbook metadata check found no hidden ICD dictionary, comments, named ranges or validations that resolve its codes. Neither newly downloaded incompatible cohort was fitted.

All 90 target/cohort/repeat/fold roles completed with separate local ranker training, calibration and evaluation. A shared-slope fixed-cohort-intercept model was compared against ordinary local/pooled/other-cohort-only logistic learners; each had raw and locally sigmoid-calibrated arms, plus a local-training prevalence baseline. Every calibrated/raw arm retained .5 and an exploratory calibration-selected 90% sensitivity cutoff. Fits/calibrators/cutoffs were hash-frozen before evaluation. Unknown cohorts are rejected by the fixed-intercept predictor. No current app code, model, cutoff or clinical claim changed.

**11 focused tests passed** (three new three-role/intercept/mutation tests plus eight existing multi-study/mapping tests). Changing held-out features and labels left fits, calibrators and cutoffs identical. Full runner replay verified raw/code/protocol/history hashes, role/fingerprint separation, calibration/evaluation predictions, cutoffs and metrics. The separate `verify_cohort_calibration.py` reproduced **306 metric groups**, raw row/outcome coverage, all 90 disjoint role definitions and calibration-only threshold maximality. All 62 protected historical files were unchanged; original raw workbook/four served models/104 meshes and the prior multi-cohort experiment passed their verifiers again.

LCX cohort-aware calibration improved mean AUC/Brier over equally calibrated local learning in both observed cohorts, but both conditional Brier-difference intervals include zero. CAD was worse in all three. The 90% illustration did not reliably achieve 90% evaluation sensitivity and had many false alarms. All calibration slopes were positive (.1713-2.4008); within-fold ranking is retained, while pooled fold scores can change AUC. Research results reuse inspected people, use 11 CAD/13 vessel inputs, require known-cohort context and local labels, and do not replace the original 55-input accuracy figures. [Every arm/repeat/cutoff](cohort_calibration_results.md) is retained. Private fits/raw data stay excluded from the regenerated source bundle.

## 13 October 2026: additional-source audit and multi-cohort training

New source audits preserve fQRS/ICD workbook SHA `48dc30c99ece5e1c85050f3a815252a512c1aeb212f95c57e635515966ada7ba` (382 x 99) and CM-CAD structured archive SHA `fdedac53f14fc867e653061446a16dc4e5df2aa6378b514d5553d04e4ea791c8` (82 participants). Raw tables remain ignored/local. Source dictionary disambiguates follow-up LAD as left atrial diameter, not coronary disease. ICD code meanings and outcome equivalence were not inferred, so neither new cohort was fitted. Shandong supplements were verified as aggregate regression/VIF tables rather than patient records; MALAT1 file listing and MultiD4CAD access restrictions were inspected.

Frozen `multicohort_protocol.md` and `ml/multicohort.py` define the additional-data training trial. Preparation saved exact hashes/roles before fitting. **All 54 roles completed**, with CAD using 1,201 eligible records/11 shared inputs and vessel models using 13 inputs across two cohorts. Fold-local imputers/scalers and constant .5 decisions were used. Additional cohorts were previously inspected: this is development, not fresh independent validation or a 55-input application score. All arms, negative findings and paired fixed-prediction bootstrap intervals are saved. Research fits remain local-only.

**8 focused tests passed**: three new isolation/weighting/preprocessing tests and five existing cohort-mapping tests. `python -m ml.multicohort verify` passed raw/code/protocol/history hashes, role isolation, exact duplicate exclusion, fitted-prediction replay and metric regeneration. Separate `scripts/verify_multicohort.py` independently reproduced 93 metric groups and checked 54 role definitions and exact once-per-arm patient evaluation. All 53 protected historical model/metric/research/sample/anatomy-manifest files were preserved. CAD augmentation harmed Brier/AUC in every cohort; LCX's small Brier intervals both span zero and source-cohort sensitivity fell. No replacement, backend/UI modification, newly approved operating threshold or clinical accuracy claim resulted.

## 13 October 2026: inputs-first follow-up review

Added review guidance, case overview, A/B differences, draft ECG/echo observations, code/context notes, CAD supplied/imputed counts and printable worksheets. Review loads do not call inference. Draft exports omit stale outputs; completed exports use the response snapshot and full numeric input precision. Two public-development record sheets preserve every original value/label and attribution, without original-report or independent-evaluation claims.

**45 frontend tests passed**, production build passed, and the new Python source-preservation test passed. Both sheets passed deterministic regeneration verification. Original workbook, four models and all 104 meshes passed artifact verification. The model/metric/sample/anatomy-manifest pre-change hash inventory was unchanged. The full Python suite was not rerun for this presentation follow-up; the preceding full-suite result remains historical.

Live authenticated Chromium verified loading without inference, Profile B generation, three worksheet downloads, stale-result clearing after EF edits, A/B differences, both source links and 390px layout (380px document width). Source routes redirect anonymous requests to login (303). The completed worksheet has 55 inputs plus four separate estimate rows. Visual inspection caught Windows default decoding in the new generator; explicit UTF-8 reads corrected units, and the test checks m²/µL notation and no mojibake. Rebuilt sheets passed live inspection. Screenshots: `2026-10-13-review-*` and `2026-10-13-source-sheet-desktop.png`. The report remains six pages; changed pages 3–4 were rendered and visually inspected. Existing Poppler fallback notices and Three.js size advisory remain.

No model retraining, new accuracy claim, clinical sign-off or submission occurred. The final source bundle is checked for exact repository files/bytes/CRC and exclusion of credentials, temporary logs, environments and acquired external raw data.



Executed locally on Windows, 7 October 2026. This ledger distinguishes measured evidence from unperformed release/clinical checks.



## Environment and reproducibility



- Python 3.11.5, Node 24.14.1, npm lockfile and fully pinned `requirements.txt`.

- Installed requirements into a separate new `.venv-verify` environment. Installation and `pip check` passed. The environment reused the machine's package download cache; this was not an offline or empty-cache test.

- Final backend suite: 22 passed in both the primary and fresh environments. The fresh-environment receipt is retained in `output/verification/fresh-environment-tests.txt`.

- `npm ci` executed from the final lockfile, followed by TypeScript/production build and frontend tests. Three workflow tests pass. npm audit reports zero known vulnerabilities at the time of execution.

- Models regenerated by `ml/train.py` during this build; no independent second full training run is claimed. OOF outputs, seeds, fold indices, parameters and package versions are saved.

- Source download performed live; `setup_data.py` then verified the existing source. Its fresh-download branch has not been separately rerun after removal because raw data is preserved.

- `verify_artifacts.py` passed: original workbook, all four model files, anatomical manifest and 13 original mesh files match their hashes.

- All-row SHAP audit passed for every target: 303 rows each, largest probability reconstruction error 5.56e-16. Receipt: `output/verification/all_rows_shap.json`.



## Automated tests



At the original verification, Python coverage included the training input allowlist, explicit exclusion of LAD/LCX/RCA/Cath, train-only imputation, unknown category handling, outer split separation/coverage, deterministic endpoint inference, response schema, prediction bounds, full-feature SHAP reconstruction, missing-value disclosure, unknown and malformed inputs, nonfinite numbers, extreme finite log-odds stability, model corruption rejection and out-of-range warnings. The later input accuracy guard below supersedes those last two API behaviors: numeric values outside observed ranges now receive 422 before inference.



Frontend tests cover editing after a result (old outputs/export clear), API validation errors (no stale success), and disabling form/sample edits while a request is pending. A revision counter additionally discards stale inference responses if asynchronous CSV processing changes inputs. Prediction response types are generated from the backend OpenAPI contract; `tsc` checks their use in the application. Metadata-driven forms use backend field definitions.



Backend result: `output/verification/backend-tests.txt`. Upstream warnings: Starlette's httpx deprecation and SHAP/Matplotlib color-map deprecations. They do not fail the suite. Build warns about the roughly 1.12 MB Three.js-related minified chunk (about 313 KB gzip). The app chunk is approximately 54 KB. Local anatomy totals about 5.1 MB raw. Gzip middleware is configured for the production server.



## Real-browser evidence



Production app served by FastAPI on 127.0.0.1:8000; Chromium controlled through Playwright. Actual prediction API used, not mocked browser responses.



| Check | Observed result | Evidence |

|---|---|---|

| Empty startup | No probability until enough observations and Generate prediction | Initial browser snapshot |

| Synthetic Profile A | CAD 11.3%, LAD 12.1%, LCX 4.2%, RCA 11.9%; discordance warning shown | `output/playwright/profile-a-desktop.png` |

| Synthetic Profile B | CAD 99.0%, LAD 96.6%, LCX 54.8%, RCA 70.8%; colors differ | `output/playwright/profile-b-desktop.png` |

| Mesh pointer picking | A click on visible RCA changed selected vessel to RCA | Browser return showed RCA pressed in viewer/card/explanation |

| Orbit and zoom | Rendered geometry view visibly changes after drag and wheel | `heart-before-orbit.png`, `heart-after-orbit.png` |

| Reset and HTML vessel controls | Reset restores camera; LCX selection changes explanation | `lcx-explanation.png` |

| Actual SHAP and measurements | Signed attributions and entered values visible | `lcx-explanation.png` |

| Validation panel | Four targets, errors, calibration, baseline and limitations visible | `model-evidence.png` |

| Input edit | Export disabled and prior outputs cleared immediately | Browser assertion `staleResultCleared=true` |

| CSV -> prediction | Imported supplied one-row synthetic CSV; successful inference | One measured interaction took 234 ms |

| JSON export | Download succeeds; exported snapshot and probabilities retained | `exported-result.json` |

| Mobile 390x844 | Anatomy, pills and disclaimer fit; no horizontal page overflow | `mobile-anatomy.png` |

| Console | Zero errors/warnings on the working rebuilt page | Playwright console inspection |



An initial HTML-in-canvas loading fallback caused a DOM removal error; it was removed, the production build repeated and a fresh browser reload had zero errors. No claim of a broad browser/device performance benchmark or dedicated-GPU-free hardware benchmark is made. The scene caps DPR at 1.5 and renders on demand.



Final restarted-server check reproduced all four Profile B probabilities and enabled export. Desktop and 390px mobile screenshots are `output/playwright/final-desktop.png` and `final-mobile.png`; mobile document width equaled viewport width (390px). Browser console reported zero errors and zero warnings. The anatomy response returned HTTP 200 with `Content-Encoding: gzip`; the health endpoint reported all four models loaded.



## Document QA



`output/pdf/technical_report.pdf` renders to **five A4 pages**. All five page images were inspected: no clipping, overlaps or missing content found. It contains actual evaluation plots and an actual application screenshot. Poppler emitted font fallback messages, but page text and symbols rendered visibly. The Markdown source and PDF cover the same report content.



## Not performed / remaining



- Clinical feature/unit review, anatomical expert review, external/prospective validation, fairness/utility study and patient use.

- Linux/macOS fresh setup and container execution. Docker CLI is installed but its Linux-engine daemon was unavailable; `docker version` could not connect to its named pipe. The optional Dockerfile was not built.

- Hosted/public deployment, internet service security/privacy validation, public GitHub publication.

- Demo recording/YouTube publication, real-name team/account checks, eligibility confirmation, one-team/one-track release decision and Devpost submission.

- Private Discord announcements and inaccessible public discussions/resources. Rules were read from official indexed content; live direct requests returned 503.



No engineering check establishes clinical validation or final submission readiness.



## Research-informed redesign verification — 7 October 2026



The earlier screenshots and counts above document the original delivery. The current redesign uses 56 meshes (91,194 faces; 6,302,648 OBJ bytes). Original target mesh records were compared with the previous source archive and are identical for LAD, LCX and RCA. All four models and raw workbook still pass integrity verification. Contextual branch meshes are not assigned independent predictions.



- Production TypeScript/Vite build passed; app JavaScript is 63.26 kB (22.36 kB gzip). The existing Three.js chunk warning remains (1,124.14 kB / 313.09 kB gzip).

- Six frontend tests passed, including one-click synthetic inference with the chosen inputs, searching/editing then recomputing with the new value, and missing-age guidance/filtering. Original stale/error/pending tests still pass.

- Backend regression: 22 passed, four existing upstream deprecation warnings (51.42 seconds in this run). No model training or threshold changes were made.

- Actual Chromium: both one-click examples complete; original displayed probabilities reproduced. LDL search returned 155 from Profile B, editing to 150 cleared export, and recomputation completed. Model evidence navigation scrolls to its panel.

- Actual RCA mesh click selected RCA; orbit/zoom worked and changed the preset indicator to free view. Front/back/reset, surface/see-through/arteries-only, LCX isolation/show-all and atlas-detail toggle were exercised. Extra geometry loading has an explicit status outside the canvas.

- Fresh 390x844 mobile load starts with input fields collapsed; they can be opened and searched. Prediction, LCX isolation, back view and export availability were checked. Document width 380px versus 390px viewport (scrollbar); no horizontal page overflow. This is browser emulation, not a physical phone or touch gesture test.

- CSV template download succeeded. It contains the 55 allowed headers and a blank row, not populated patient data.

- Browser console: zero errors and zero warnings after the working final page loaded.

- Current screenshots: `redesign-overview.png`, `redesign-report.png`, `redesign-mobile.png`, `redesign-mobile-heart.png`, `redesign-evidence.png`, `redesign-isolated-lcx.png`, `redesign-orbit.png` under `output/playwright/`. Older images are historical.

- Technical report regenerated at five pages; changed anatomy page rendered and visually inspected. Other report sections retain the prior validated evaluation.



Research evidence and remaining user-study questions are in `docs/product_research.md`. The visual design is a design judgment; no comparative usability or learning study has been performed. Branch completeness and clinical anatomy remain unreviewed by an expert.





## Bounded model investigation and cutoff comparison — 7 October 2026



- Completed the prespecified 11-configuration, two-repeat nested-CV experiment; detailed results and deployment rationale are in `model_improvement_results.md`.

- `python -m pytest -q`: **25 passed**, four existing dependency deprecation warnings. Includes three new split/evidence/provenance audits; original inference and SHAP contract tests pass.

- Frontend: **7 tests passed**; TypeScript/Vite production build passes. Existing Three.js bundle-size warning remains.

- Browser at `http://127.0.0.1:8000`: 1440px desktop and 390px mobile; no horizontal overflow. Target/run changes show RCA run 2 recall 71.9%, specificity 54.0%, precision 48.5%, 32 missed cases and 87 false positives for the training-recall policy. Evidence download returned HTTP 200 and version `improvement_v1`. Synthetic profile A still predicts successfully. Browser console: zero errors and warnings.

- Screenshots: `output/playwright/threshold-lab-desktop.png` and `threshold-lab-mobile.png`; both visually reviewed. A fixed disclaimer overlays the tall mobile element capture; all content is scroll-accessible in the actual viewport.

- Production model metadata and source data hashes match the pre-experiment manifest. No model, clinical cutoff, label or SHAP interpretation was replaced. External-data audit copies are outside the training reader's path.

- Original five-page PDF remains a baseline report. The new experiment has its own results document; public publication and submission have not occurred.



## Guided demo, anatomy and optional-model verification — 8 October 2026

- Main Python suite: **49 passed, 1 skipped**. The skip requires optional CatBoost in the separate research environment; all 15 broad-search tests passed there. New candidate tests cover implicit/explicit baseline equivalence, unchanged CAD/LAD/RCA, LCX SHAP reconstruction, unknown variant 422, unavailable variant 503 and corrupted artifact rejection.
- Frontend: **11 passed**. Production TypeScript/Vite build succeeded. App JavaScript 95.89 kB / 32.43 kB gzip; Three.js chunk 1,131.88 kB / 315.74 kB gzip still triggers the size advisory. No bundle-size or hardware performance guarantee is implied.
- Raw workbook, four original model files, anatomy manifest and all 56 meshes passed integrity checks; main Python environment `pip check` passed. Candidate manifest and held-out files passed their own hashes and all 303 serialized-model SHAP checks (maximum raw-margin residual 2.66e-15).
- Actual Chromium, 1440x1050: guided profile B computed; LDL measurement link focused its form input; LCX selection focused the heart; the explanation and evidence steps completed; finishing restored focus to the guide launcher. Optional-model switching cleared export until recomputed. Baseline LAD 96.6%, LCX 54.8%, RCA 70.8%; experimental mode preserved LAD/RCA and changed LCX to 59.8% on this synthetic example. These values are demonstration outputs, not predictive validation.
- Candidate LCX guide evidence showed run-one recall 52.1% and explicitly named the experimental evidence. Original baseline tables stay labeled and unchanged. The model resets to baseline on reload.
- Anatomy tour progressed LAD → LCX → RCA. The camera completed transitions, keyboard arrow/zoom/pan/Home controls worked, and reduced-motion mode snapped directly to the requested view. At 390x1000 the heart fit inside its canvas and page had no horizontal overflow. This is browser emulation, not a physical phone test.
- CSV import accepted displayed Female and Yes, mapping them to the field-specific source codes Fmale and Y. Input minimum/completeness still applies. Browser console after the final working page reported zero errors and warnings.
- Latest visually inspected screenshots: `guided-case-final-desktop.png`, `guided-case-final-mobile.png`, `anatomy-final-lcx-desktop.png`, `anatomy-final-mobile.png`, `model-comparison-final.png`; final whole-page view is `final-overview-desktop.png`, all under `output/playwright/`. Older screenshots document intermediate/historical states.
- No public hosting, repository publication, video upload, new human review, independent cohort evaluation or final submission was performed. The five-page PDF remains a baseline report; current experiments are in the separate dated Markdown reports. Docker was not rebuilt in this pass.

- Separate TabICLv2 research audit: 40 fixed outer fits plus a 12-case explanation/runtime pilot completed. The pilot took 265.82 seconds, used at most 1,717 MiB RSS and cost 16.23–19.07 seconds per approximate attribution. Saved-artifact verification passed; approximation convergence was not established. This model is not registered in the app. Details: `tabicl_explanation_results.md`.
## CONFIRM development evidence — 8 October 2026

- Executed all three frozen stages of `scripts/develop_confirm.py`: patient partition preparation, training/calibration, and reserved development-test evaluation. Completed 12 experiments and 144 candidate CV fits, plus 12 selected-model fits and separate calibration fits.
- Focused command: `.venv/Scripts/python.exe -X utf8 -m pytest tests/test_confirm_development.py tests/test_confirm_external.py -q`: **8 passed** in 21.62 seconds. One openpyxl warning about an unsupported workbook extension during reading; the source workbook was not saved or changed.
- Audits verify historical/app hashes, current runner/protocol/artifact identities, patient partition consistency, train/calibration/test disjointness, training-CV selection, calibration-only cutoffs, exact reproduced metrics, training-only numerical medians and serialized-model test predictions. Perturbing all unused categorical columns leaves four-input predictions identical.
- `scripts/report_confirm_development.py` produced the Markdown report and PNG/SVG chart; PNG visually inspected. No app/UI changes, frontend rebuild or new browser check was necessary in this research-only pass.
- The new scores are internal development results on previously inspected CONFIRM data. This is not a fresh independent validation; no model promotion, public release, clinical review or human study occurred.
## Error/site follow-up and report verification — 8 October 2026

- `pytest tests/test_confirm_error_followup.py tests/test_confirm_development.py tests/test_confirm_external.py -q`: 10 passed in 17.23 seconds. `pytest tests/test_confirm_site.py -q`: 1 passed in 1.37 seconds. One read-only workbook-extension warning in the first command.
- Current original-source/model/anatomy integrity check passed. SHAP reconstruction passed for all 303 source inputs and four models; probability residual <=5.56e-16. Fixed-model background sensitivity measured separately, not conflated with correctness.
- Real Playwright Chromium: Profile B completed with export enabled, LAD focus executed, one 3D canvas present; at 390x1000 document width did not overflow. Screenshots `followup-desktop.png` and `followup-mobile.png` inspected. These are a scoped recheck, not new exhaustive UI QA or a physical-device benchmark.
- Updated PDF rendered with bundled reportlab/pypdf runtime: six pages. All page layouts inspected; revised sixth page inspected at full rendered size. Poppler issued fallback-font notices; no visible overlap or clipping in reviewed pages. Original report generator remains unchanged.
- See `next_steps_closeout.md` for scope, negative results and unfinished external/human-dependent work. No frontend/model changes or publication in this pass.

## Input accuracy guard — 8 October 2026

- Corrected both synthetic profiles' mathematically inconsistent BMI values, added API and form checks for conflicting weight/height/BMI entries, and declined numeric inputs outside the observed source range before model execution. Original model artifacts and historical research evidence were not changed. The [audit note](input_accuracy_guard.md) records the measured effect and its limits.
- Full Python suite: **62 passed, 1 optional CatBoost skip**. Frontend: **14 passed**. Production TypeScript/Vite build and original model/anatomy hash verification passed. The final targeted backend regression also accepts one-decimal rounding of the source minimum BMI.
- In real Chromium, corrected Profile A showed LCX 3.8%. Changing weight from 74 to 100 while retaining old BMI disabled prediction with a specific correction message. Clearing BMI restored prediction; the API derived it and disclosed this in the result. At 390px, document width equaled viewport width. The inspected viewport screenshot is `output/playwright/input-accuracy-mobile.png`.
- The BMI-missing held-out stress check did not establish a predictive accuracy gain; Brier scores were slightly lower when BMI was masked in this source-cohort diagnostic. Input consistency and avoidance of unsupported extrapolation are the shipped changes. No independent cohort, clinical review or release approval was added.

## Coherence-adjusted baseline accuracy — 8 October 2026

- A pilot-informed, shared-fold paired evaluation tested Euclidean projection of the four raw probabilities onto `CAD >= LAD, LCX, RCA`. Both repeats used the same 303 source patients with different five-fold partitions. Mean four-target Brier changed from **0.172124 to 0.170247** in repeat 1 and **0.175809 to 0.175290** in repeat 2. The average reduction was **0.001198**. Raw CAD/vessel probability conflicts fell from 79/42 rows to zero. This is a small internal result, not external or clinical validation. Individual target metrics, the single inconsistent label row, and the pilot-informed protocol are in `docs/coherence_projection_results.md`.
- `scripts/verify_coherence_evidence.py` passed: source/protocol/code hashes, all 303 held-out rows per repeat, shared nonoverlapping outer partitions, labels, probability bounds, projection optimality, per-target Brier/AUC/recall/accuracy/confusion counts and the adoption screen were checked against saved CSVs. Original workbook, four fitted model artifacts and 56 anatomy meshes passed `scripts/verify_artifacts.py`.
- Default `/api/predict` now reports a coherence-adjusted `probability`, class and band, plus each raw `model_probability` explained by SHAP. It identifies the adjusted response as `1.0.0+coherence-v1`. The optional `histgb_lcx_v2` variant remains unadjusted because its interaction with this projection was not evaluated. `/api/model/coherence` exposes compact paired evidence; the UI distinguishes it from historical raw, target-specific OOF metrics.
- Final regressions: **68 Python tests passed, 1 optional CatBoost skip**; **16 frontend tests passed**; TypeScript/Vite production build passed. The large Three.js chunk advisory remains. API boundary tests cover projection crossing the 0.5 class boundary and 0.3/0.7 display bands while SHAP reconstruction stays tied to the raw model output.
- In actual Chromium, synthetic Profile A displayed CAD/LAD/RCA **11.73%** after adjustment (raw **11.29%/12.07%/11.85%**) and LCX stayed **3.77%**. The visible adjustment card listed raw and displayed values; the LAD explanation showed raw **12.1%** versus displayed **11.7%**. Profile B required no adjustment and displayed CAD **99.0%**. Switching to Experimental LCX cleared stale results and disabled export until recomputation; its result showed unadjusted outputs and its own version/limit note. The evidence panel showed repeat Brier **0.1721→0.1702** and **0.1758→0.1753** with the same-303-person caveat.
- At 390px viewport width, document width was 380px and the adjustment card was legible without horizontal overflow. The final Chromium console reported zero errors and warnings. Inspected screenshots: `output/playwright/coherence-card-final.png`, `coherence-mobile-card.png` and `coherence-evidence.png`. The six-page PDF report was rebuilt and all rendered pages were inspected; no clipping or layout defect was found. Its app screenshot is a previously captured baseline example, while the current adjustment is documented in text.
- Synthetic profiles were relabeled by age because both contain 55 supplied observations; the earlier “fewer/more recorded findings” wording was inaccurate. A compatible unused external cohort and clinician review remain unavailable. These checks establish a measured improvement in the product's internal aggregate probability error under this dataset's label rule, not diagnostic accuracy in a new population.

## AngioCAD population test and held-out teaching cases — 9 October 2026

- The separate [AngioCAD 13-input protocol](angiocad_external_protocol.md) was saved before source fitting and external scoring. Source model/OOF artifacts were frozen with hashes, then the 377-feature/413-label public workbooks were joined by unique ID. Input eligibility yielded 363 patients before target-specific 26–50% ambiguity exclusions. The [result report](angiocad_external_results.md) records all four primary metrics, confidence ranges and three prespecified sensitivity variants. This is an external transport test of the reduced model, not the 55-input app.
- `python scripts/verify_angiocad_external.py` passed after scoring: frozen protocol/model/prediction hashes, 16 external target/cohort AUC/Brier/confusion results and four source OOF AUC/Brier pairs reproduced from saved row-level probabilities. The clinical workbooks stay local and are excluded from source packaging.
- The [held-out case challenge](heldout_case_mode.md) packages four deliberately selected original-cohort examples with saved raw outer-fold probabilities and labels. It uses no final-model inference, SHAP or coherence adjustment. Focused API/React tests passed, and the actual production build was checked in Chromium at desktop and 390 px mobile width. Case load, CAD guess/reveal, mobile result scroll and console were checked; no console errors or horizontal overflow were observed. Inspected receipts: `output/playwright/heldout-case-desktop.png` and `heldout-case-mobile.png`. These cases are teaching examples, not a representative accuracy sample.
- Broader regressions at that stage: **73 Python tests passed, one optional dependency skip**; **17 frontend tests passed**; TypeScript/Vite production build passed. The existing Three.js large-chunk advisory remains. The report was rebuilt with the bundled PDF runtime, confirmed at **six pages**, and all six rendered pages plus the final full-resolution page 6 were visually inspected without clipping or overlap.

## Adversarial pre-submission review — 9 October 2026

- The [loss pre-mortem](loss_premortem.md) was checked against the current Track A rubric, local model and UI evidence, the unpublished entrant gallery, and adjacent public products. Hypothetical rival strengths are labeled as such; no winner score or complete competitor census is claimed.
- Corrected the README/submission wording from “no GPU” to “no dedicated GPU; WebGL browser required,” and made `/model/info` explicitly distinguish the 55-input app from separate reduced-input external work. Updated the already-completed error-challenge task and the learner/demo plans to test whether users connect a saved vessel error to reference anatomy.
- `python -m py_compile backend/main.py` and the focused `tests/test_pipeline.py::test_schema_and_health` both passed. The latter was **1 passed**, with four upstream deprecation warnings. No model, training data, probability, threshold, mesh or frontend behavior was changed; the previous broad regression counts remain historical receipts for the prior build.
- `docker --version` succeeded but `docker info` could not connect to a running Docker Desktop Linux engine. Container startup remains unverified, not a passed check.
- `scripts/package_source.py` was rerun after the review edits. The archive check asserts the pre-mortem and updated learner plan are included, the acquired AngioCAD workbooks are absent, and the archive hash matches its manifest. Public checkout, video, learner observation and clinical review remain open.

## 9 October integrated hardening check

The following is a new check of the current working tree; older counts and screenshots above are historical receipts. `python -m pytest -q` passed **74 tests with one optional skip**. `npm --prefix frontend test -- --run` passed **22 tests**, and the TypeScript/Vite production build passed. The existing Three.js chunk-size advisory remains. `scripts/verify_artifacts.py`, `scripts/verify_angiocad_external.py` and `scripts/verify_input_missingness_stress.py` passed their hash, saved prediction and metric checks.

An actual FastAPI-served Chromium run on the rebuilt assets completed Case D's saved LCX false-negative reveal (23.2%, positive dataset label), followed its vessel jump, and confirmed the heart said **no probability mapped**. The reference view hid live prediction cards and gave a return control. Selecting RCA afterward kept the card's original Case D–LCX link distinct from the artery currently being explored. The separate AngioCAD panel rendered on desktop and at 390 px. At 390 px the document width equaled the viewport width, while the 570 px evidence table scrolled inside its own region with a cue. A synthetic one-row CSV with all 14 laboratory and all three echo observations blank supplied 38 inputs, displayed the two measured-scenario warnings before prediction, and successfully predicted; the API response repeated the warnings. The first warning layout used narrow side-by-side columns and was corrected to stacked text, then rebuilt and visually rechecked. The browser console reported zero errors and warnings at the checked reference state.

Current visual receipts: `output/playwright/2026-10-09-heldout-reference-desktop.png`, `2026-10-09-external-evidence-desktop.png`, `2026-10-09-external-evidence-mobile.png`, and `2026-10-09-missingness-warning-mobile.png`. The last receipt shows the corrected warning layout. These are local Chromium checks, not a physical-phone/touch or clinical review.

The technical report source and PDF were then updated with the reference-only case link, measured laboratory masking result, separate AngioCAD evidence panel, and a fresh valid synthetic Profile B screenshot (`output/playwright/2026-10-09-profile-b-current.png`). The bundled report runtime generated a **six-page A4 PDF**. Poppler rendered all six pages; every page was visually inspected with no clipping, overlap or missing text. `pdfinfo` confirmed six A4 pages, and text extraction found all three new passages. Poppler printed Symbol/ArialUnicode font fallback messages, but the final rendered pages showed the intended text and figures. The PDF is still a local artifact; no public link or clinical review is claimed. The current frontend labels the LCX percentage as sensitivity, distinguishes the linked case vessel from the currently explored vessel, and narrows the input-retention claim; 22 frontend tests and the production build passed after those changes.

## Pre-GitHub packaged-source cold check — 9 October 2026

The rebuilt source ZIP had **521 entries**, passed CRC, and its entry names and bytes matched the final tracked/unignored working-tree files. The SHA-256 matched `output/release/manifest.json`; the acquired AngioCAD and CONFIRM raw workbooks were absent. A separate package scan found no credential or email-pattern matches. The source snapshot ledger now explains why historical organizer snapshots listed by hash are intentionally not all bundled.

A fresh extraction passed `npm ci` with zero reported vulnerabilities, **22 frontend tests**, the TypeScript/Vite production build, and the artifact, AngioCAD and input-missingness verifiers. Cold Python tests reported **73 passed, 2 skipped**: optional CatBoost is unavailable, and the licensed CONFIRM raw workbook is intentionally local-only. The source working tree had **74 passed, 1 skipped** when that workbook was present. A separate served-build Chromium smoke checked the narrowed privacy wording, sensitivity label, Case D LCX false negative, linked-versus-viewed reference artery, and unmapped heart probability; the checked console had zero errors and warnings. No clinician or learner review has occurred.

## GitHub-informed 320 px viewport check — 9 October 2026

The [open-source anatomy comparison](github_repo_opportunities.md) prompted a narrower browser check. At a 320×568 Chromium viewport, the initial three-column workflow text was cramped, so the steps now stack below 360 px. The rebuilt production assets showed readable steps; document and body scroll widths both stayed at 320 px. The synthetic-example card, held-out challenge and main workspace were visually inspected at that width. Receipts: `output/playwright/2026-10-09-320-intro-final.png`, `2026-10-09-320-quickstart.png` and `2026-10-09-320-challenge.png`. The browser console reported zero errors and warnings. This checks Chromium layout, not physical-phone touch performance or clinical usability.

## GitHub EBM research verifier — 9 October 2026

`.venv/Scripts/python.exe ml/ebm_github_trial.py --verify` passed independently after the run: it checked the frozen protocol, source, schema, 40 saved folds, eight matched baseline files, eight new 303-row prediction files, manifest/output hashes, recomputed metrics and prespecified screens. `.venv/Scripts/python.exe -m py_compile ml/ebm_github_trial.py` passed. The [report](ebm_github_trial.md) records the repeated same-patient results and why the app model stays unchanged.

The post-fit verifier was also run in disposable Git checkout simulations: 57 saved fold/baseline/result text files were converted from CRLF to LF, then the schema, frozen protocol and fit-runner snapshot were converted to CRLF. Both checks passed without editing the frozen artifacts or refitting a model.

The current checkout also passed all **22 frontend tests** and **74 Python tests** (one skipped because of the documented optional condition). The 320 px production build and browser check are recorded above. The source archive was rebuilt after these edits and checked against the repository file list and byte contents. A fresh extraction also passed the EBM `--verify` audit using the existing Python environment. The archive's current count and digest are recorded in `output/release/manifest.json`.

## China cohort, request recovery and Git portability — 9 October 2026

The frozen 14-input experiment and its limitations are in `docs/peerj_external_results.md`. `python -m ml.peerj_external verify` reproduced all source/primary/sensitivity metrics, fold partitions, frozen hashes and paired-bootstrap intervals. `python scripts/verify_peerj_external.py` separately reproduced the four subgroup summaries, reliability-bin counts/means, freeze-before-score ordering and failed promotion screen. The frontend JSON and actual Chromium download match the frozen results file byte-for-byte (SHA-256 `13f5378d7437aa9e23e531a6ed224973e68204dc7b70c104d2d4c44371666713`). Raw destination measurements/IDs remain excluded from packaging; the released saved-prediction evidence contains coarse subgroup flags.

Final working-checkout checks: **76 Python tests passed, 1 skipped** (optional CatBoost); **27 frontend tests passed**; TypeScript and Vite production build passed. Existing Vite large-Three.js-chunk and dependency deprecation advisories remain. The artifact, original EBM, AngioCAD, coherence and missing-input-stress verifiers all passed. No historical model was refit. An initial root pytest invocation also collected disposable copies under ignored `tmp/`, causing import mismatches; `pytest.ini` now confines discovery to the actual `tests/` directory. The rerun passes. The evidence component test was scoped to the named AngioCAD region when the second download link was added.

Five API-helper regression tests cover ordinary requests, HTTP/network errors, hung fetches including abort-ignoring transports, hung response bodies, timer cleanup and fresh retry. In real Chromium, a held `/api/predict` request disabled edits while pending, then displayed the 30-second timeout and enabled inputs/retry with stale export still disabled. Removing interception and retrying returned **Prediction ready** and enabled export. Receipt: `output/playwright/2026-10-09-timeout-recovery.png`.

The production evidence panel was inspected at 1440x1000 and 390x844, including expanded uncertainty and a horizontally scrolled table. The document/body width was 380 at a 390-pixel viewport (reserved scrollbar space), so there was no page-level horizontal overflow. The JSON download succeeded and matched frozen evidence exactly. Browser console: zero errors and warnings. Receipts: `2026-10-09-china-evidence-desktop.png`, `2026-10-09-china-evidence-mobile.png`, `2026-10-09-china-mobile-top.png` and `2026-10-09-china-mobile-footer.png` under `output/playwright/`. Full-element mobile screenshots include the fixed disclaimer at the active viewport position; the separate viewport screenshots show actual reading positions.

The report was regenerated with the bundled ReportLab runtime and remains **six pages**. All six rendered pages were visually inspected; page 6 now includes the 55-input internal EBM finding and separate negative China result. Page 6 has no clipped text or footer overlap. Poppler emitted existing Symbol/ArialUnicode fallback notices; the inspected output contains readable labels and figures.

A fresh Git archive with `core.autocrlf=false` previously converted CRLF evidence to LF, invalidating candidate-loader hashes and blocking the entire API startup. `.gitattributes` now preserves exact bytes. Renormalization changes many Git blobs while preserving the working evidence/model files and their historical manifests. `git diff --ignore-space-at-eol` distinguishes that newline repair from substantive edits. A staged Git export already passed **73 Python tests with 2 skips** before the China tests were added; the additional skip is the intentionally unbundled raw CONFIRM workbook. This is Windows execution from an LF-configured Git export, not a claim of Linux/Docker execution.


The final staged Git export, including the new China runner/tests/UI artifacts, passed **75 Python tests, 2 skipped**, plus both China verifiers without any raw China supplement or optional InterpretML installation in the export. The same existing Windows interpreter was used; this was a clean source-tree check, not a new dependency installation. An exact-byte comparison against the parent commit identified **240 newline-only existing-file changes** and 14 substantive existing-file changes (plus explicitly added files). Historical evidence was preserved; no manifest hashes were relaxed or rewritten. The source ZIP was rebuilt from the final committed file set and checked for entry count, CRC, byte equality and raw-external/environment exclusions. Its current SHA-256 and count are in `output/release/manifest.json`.

## 10 October — local adaptation prediction experiment

A locked development experiment on the already inspected China cohort completed 60 fits across 20 fixed adaptation subsets. The original source/transport/model hashes were checked before and after; no app model or historical evidence changed. `python -m ml.peerj_adaptation verify` reproduced all 2,212 held-out prediction rows, per-repeat metrics, subgroup summaries, reliability bins, conditional intervals, saved parameters and pipeline outputs against the retained raw supplement. The independent `python scripts/verify_peerj_adaptation.py` verified direct loss/AUC/confusion arithmetic, the shared frozen dependency, training-only medians/scaler means/category levels, fixed hyperparameters and offset balance. The [result report](peerj_adaptation_results.md) states the prior cohort inspection and worsened missed-case counts at .5 alongside the probability/ranking gains.

**78 Python tests passed, 1 optional test skipped; 29 frontend tests passed.** The new label-perturbation test changes labels/features/source probabilities outside an adaptation subset and requires identical fitted parameters and evaluation predictions. Another test checks offset prevalence balance, monotone ranking and single-class refusal. Frontend tests check derived summary identity, the actual primary error/sensitivity numbers, the development boundary and missed-case disclosure. TypeScript and Vite production build passed, with the existing large Three.js chunk advisory; the Python suite retains existing dependency warnings.

Chromium production-browser QA at 1440x1100 and 390x844 opened the development disclosure, checked the table and missed-case paragraph, scrolled the table on mobile, and downloaded the full result. The actual downloaded bytes equal the frozen research JSON. No page-level horizontal overflow and no console errors/warnings were observed after startup. Receipts: `output/playwright/2026-10-10-adaptation-desktop.png`, `2026-10-10-adaptation-mobile-table.png`, and `2026-10-10-adaptation-mobile-tradeoff.png`. The local server was started for this check after an initial connection-refused attempt found it stopped; that is not counted as an app regression.

The report's new paragraph initially overflowed to seven pages; follow-up prose was shortened and regenerated to **six pages**. The changed final page was rendered and visually reviewed at full-page resolution with readable references and no footer overlap; the existing five preceding layouts were preserved apart from the date. No public deployment or final submission was performed. Fitted adaptation pipelines are research artifacts only. Full-app external validation, clinical/anatomical review and an observed learner task remain unperformed.


The clean Git export initially exposed one generated `.pyc` accidentally included in the preparation inventory. All durable historical files matched. A documented verifier-only correction excludes bytecode/cache paths while retaining exact original runner-snapshot, model, protocol and result hashes; no fits or scores changed. The original inventory remains saved. Both development verifiers and the original China transport verifier are rerun from the export with raw external data excluded. This uses the existing Windows interpreter, not a new dependency installation or Linux execution.

## 12 October — separate calibration and exploratory cutoffs

The 10 October frozen operating-point experiment completed 30 fits using pairwise disjoint model-training/calibration/evaluation roles. Preparation, fit-freeze and evaluation-manifest timestamps are ordered. `python -m ml.peerj_operating verify` reproduces role assignments, all predictions/decisions, thresholds, metrics, reliability and conditional bootstrap intervals. `python scripts/verify_peerj_operating.py` independently checks maximum feasible calibration thresholds, confusion arithmetic, calibration algebra, training-only medians/scaler means/category levels and matrix-form local probabilities. Both passed with the retained raw data. Original China transport and adaptation verifiers passed again; their durable artifacts and all historical model files remain unchanged.

**82 Python tests passed, 1 optional test skipped; 31 frontend tests passed.** Tests mutate evaluation labels/features/source probabilities and require identical learned models/calibrators/cutoffs; changing calibration rows cannot refit the ranker. Cutoff ties, maximality, invalid inputs and complete disjoint row coverage are checked. Frontend tests tie every displayed rate/error count to frozen outputs and require exploratory/clinical-boundary text. TypeScript/Vite production build passed; the existing large Three.js chunk advisory and dependency warnings remain.

The PDF initially overflowed to seven pages; research prose was shortened without reducing type size and the final report is **six pages**. Updated pages 1 and 6 were rendered and visually reviewed with no clipped text or footer overlap. Poppler emitted the existing font fallback notices. Date updated to 12 October for closeout; frozen experiment records retain their original timestamps.

Real Chromium production QA at 1440x1100 and 390x844 opened the new disclosure and inspected error counts, target limitations and mobile table scrolling. Document/body width was 380 at viewport 390, with no page-level horizontal overflow. Console: zero errors/warnings. The actual downloaded metrics match the frozen 170,709-byte JSON exactly, SHA-256 `96a48afb1a362f140af4866715bc5f0478b2eec83828698555dd770bf41d92f6`. Screenshots: `output/playwright/2026-10-12-operating-desktop.png`, `2026-10-12-operating-mobile-top.png`, `2026-10-12-operating-mobile-table.png`. The first navigation found the local server stopped; starting Uvicorn resolved it.

A staged Git export with `core.autocrlf=false` and no acquired raw external records passed both operating-point verifiers. Raw prediction/preprocessing checks explicitly report skipped there; packaged metrics, thresholds, partitions and historical hashes are still verified. The export uses the existing Windows interpreter, not a fresh dependency install or Linux execution. The source archive is regenerated after closeout and checked against every repository file, CRC and raw/environment exclusions; its current count and SHA-256 are in `output/release/manifest.json`.

The Beijing schema audit records public-source hashes, actual 3,000-row workbook shape, codebook and unresolved population/endpoint issues. No model scored that cohort and no binary CAD label was guessed. Reviewer guidance remains unavailable. No clinically preferred cutoff, new independent validation, app-model promotion, publication or submission is claimed.

## 13 October — example input provenance after relayed doctor feedback

The [feedback record](doctor_feedback_2026-10-13.md) distinguishes the user's relayed observations from completed review or clinical facts. The sample generator now records explicit choices, derived BMI and inherited defaults for every example input. All 110 A/B input values were compared before/after regeneration and preserved. The live Profile B prediction JSON was saved before the change and compared exactly afterward through the HTTPS reviewer link; identical. No model weights, medical labels or historical evaluation artifacts were altered.

The app shows the VHD=`mild` origin beside the selected example, distinguishes that input from CAD probability and provides a grouped read-only 55-input summary. Selecting a summary field opens its actual input control. Edited observations clear the original example context and stale prediction/export. This addresses misleading example presentation; it does not establish that the synthetic combinations are clinically coherent.

**26 focused Python tests passed** (new provenance test plus pipeline/API checks), and **all 33 frontend tests passed**. The new checks require disjoint/complete input provenance, actual cohort-default agreement, absence of invented clinical sign-off, exact displayed sample values/origins and removal of stale example context. TypeScript/Vite production build passed with the existing large Three.js chunk advisory; dependency warnings remain.

Chromium checked the actual remote reviewer URL at 1440x1000 and 390x844: password login, Profile B prediction, visible valve-origin explanation, all 55 definitions, navigation to the VHD input, mobile width (380px), and stale-state clearing after editing VHD. Console: zero errors/warnings. Screenshots under `output/playwright/`: `2026-10-13-profile-context-desktop.png`, `2026-10-13-profile-context-mobile.png`, and `2026-10-13-profile-context-mobile-top.png`. The reviewer must refresh to receive the new frontend. No revised-screen reviewer feedback or completed sign-off has yet been reported.

## 13 October — whole-heart detail, unknowns and investigation context

The next relayed call points and the user's clarification are recorded in `doctor_feedback_2026-10-13.md`. The official archive supplied 48 additional unchanged meshes: cardiac veins, four chamber cavities, valve leaflets and papillary muscles. The final 104 meshes contain 147,474 faces/10,042,179 OBJ bytes. All original 56 files, LAD/LCX/RCA mappings, global transforms and target anchors were compared and preserved. `python scripts/verify_artifacts.py` checks every final mesh hash and model identity; `tests/test_detailed_anatomy.py` checks nonempty disjoint files/FMA mappings and restricts predicted structures to the three targets.

The viewer now uses pale red tissue, red arteries and blue veins, with explicit structure-type versus probability-shading modes and an internal view. Probability shading stays dynamically tied only to coronary targets. New valves/chambers/veins never receive inferred disease labels. Native fine geometry and material/lighting changes produce the detail; no generated patient anatomy or echo reconstruction is claimed.

Missing numeric and categorical observations display **—**. CSV blank/hyphen/en-dash/em-dash imports become null; valid numeric/source-code zero is retained. The exact completed-prediction ECG/echo input snapshot is shown with supplied counts, source codes and imputation notes. No clinical echo weighting rule was invented. Six previously inherited investigation defaults in each synthetic profile are now null: Q Wave, St Elevation, LVH, Poor R Progression, BBB and VHD. The examples supply 49 values; explicitly chosen ST depression/T inversion and EF/RWMA remain supplied. Live API checks confirmed the exact six missing flags. Existing imputation happens to recover the previous modal categories, so A/B output probabilities remain the same; that is not an accuracy gain.

**89 Python tests passed, 1 optional CatBoost test skipped; all 40 frontend tests passed.** The initial focused API run exposed two existing tests that assumed complete sample inputs; their exact expected missing sets now derive from actual null fields rather than assuming only the fields added by that test are missing. The rerun/full suite passed. The initial TypeScript build found test-only unsupported `exact` options and the API's generic snapshot value type; these were corrected and the final TypeScript/Vite build passed. Existing dependency warnings and the large Three.js chunk advisory remain. `python -m ml.peerj_operating verify` passed again; all historical model and metric hashes were compared to the pre-change inventory and preserved.

Real Chromium on the live HTTPS review link checked all 104 meshes loading, Profile B, anatomy/probability color modes, front/back/internal views, CSV-dash prediction, null snapshot retention, supplied-zero retention, new six-unknown sample state, exact ECG/echo counts, and field navigation at desktop 1440x1100 and mobile 390x844. Mobile page width was 380px; console had zero errors/warnings. Receipts under `output/playwright/`: `2026-10-13-doctor-heart-surface.png`, `-heart-back.png`, `-heart-inside.png`, `-heart-inside-front.png`, `-heart-probability.png`, `-heart-mobile.png`, `-unknown-echo.png`, `-profile-b-current.png`, `-investigation-final.png`, `-unknown-ecg-mobile.png` (all share the same dated prefix). Screenshots were visually inspected. This is browser emulation, not a physical phone/clinical validation.

The report now includes the new geometry, current 49-input screenshot and partial-review status; it remains **six pages**. Changed pages 3–4 were rendered and visually checked without clipping/footer overlap; source date is 13 October. Existing Poppler fallback notices remain. The final source bundle is regenerated and checked for exact repository file set/bytes/CRC and exclusion of acquired raw data, credentials, local runtimes and caches. No patient data acquisition, fitting, model promotion or submission occurred during these fixes. Refreshed expert inspection and source-code/clinical objective clarification remain open.

The imported OBJ files retain the official source's trailing spaces to preserve their exact provenance hashes. An unrestricted `git diff --check` reports that upstream mesh formatting; the code/documentation check excluding only `frontend/public/anatomy/*.obj` passes. No geometry bytes were whitespace-normalized. The ZIP's complete file set, exact bytes, CRC and exclusions were verified after the implementation commit; the final manifest is regenerated after this note.


## 14 October — calibrated ensemble accuracy improvement

The primary frozen ensemble improved matched mean target accuracy from 72.6% to 75.0% and mean Brier error from 0.1753 to 0.1650 across three internal repeats of 303 people. Feature-selection and spline follow-ups failed their improvement screens. All historical evidence was preserved. The optional research ensemble is available in Prediction model, with its own approximate attributions and versioned export; the baseline remains default.

[Delivery, complete verification and limits](accuracy_goal_delivery.md) records the replay checks, missing-input stress results, regression tests and desktop/mobile browser checks. This is an internal development gain, not independent or clinical validation. LCX/RCA sensitivity remains low, core-only improvement is uncertain, and the newly audited external workbook is not compatible full-input validation.
