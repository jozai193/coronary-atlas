# Progress

## 13 October: cohort effects and separate calibration

Checked source-alignment gaps, including absent ICD workbook code definitions, and froze a follow-up shared-slope/cohort-intercept experiment. Completed 90 disjoint training/calibration/evaluation roles across two repeats with all eight raw/calibrated arms and prevalence baseline. LCX showed small uncertain probability/ranking gains over equally calibrated local-only learning; CAD worsened, and 90% calibration-target decisions retained many missed cases/false alarms. 11 focused tests passed; an independent verifier reproduced 306 groups. Prior 62 artifact hashes and the 55-input app remain unchanged. [Protocol](cohort_calibration_protocol.md), [complete results](cohort_calibration_results.md). No deployment or clinical sign-off.

## 13 October: additional public data and multi-study training

Found and downloaded new 382-person ICD and 82-person CM-CAD structured deposits, preserved hashes, and rejected incompatible/ambiguous labels for fitting. CM-CAD's LAD means left atrial diameter. Reviewed primary methods papers, froze a multi-study protocol and completed all 54 roles using eligible UCI/AngioCAD/Anhui cohorts (1,201 CAD rows, 11 shared fields; vessel tasks use 13 fields). CAD pooling worsened probability quality; LCX showed a small uncertain signal with worse original-cohort detection at .5. Three new plus five existing mapping tests passed; independent verification reproduced 93 metric groups. No live promotion. See [source/paper review](public_data_and_papers_2026-10-13.md) and [all results](multicohort_results.md).

## 13 October: prepare the revised clinician review

Delivered inputs-first guidance, case facts, A/B differences, draft ECG/echo inspection, code explanations, CAD supplied/imputed context and exact-input printable worksheets. Added two attributed consecutive original-dataset record sheets for field review, without new scoring or original-report claims. 45 frontend tests, the source-preservation Python test, build, live desktop/mobile flows and artifact checks passed. See [readiness](review_readiness_2026-10-13.md), [review packet](clinical_review_packet.md) and [verification](verification.md). Revised clinical inspection, source definitions/timing and intended-use/error-cost guidance remain pending.

- [x] Inspect entire initial workspace (empty; no existing app to preserve).
- [x] Locate official event and inspect Track A plus general submission/prize PDFs.
- [x] Audit public overview, indexed rules, schedule, update and gallery; record unavailable/private sources.
- [x] Download original UCI workbook; inspect both sheets, dimensions, target distributions and data quality.
- [x] Write research, dataset analysis, architecture, implementation plan, judging strategy and this checklist before application code.
- [x] Complete reproducible per-column EDA, hashes and provenance.
- [x] Execute nested model evaluation and baseline/calibration/sensitivity analysis.
- [x] Save four pipelines and tested SHAP explanations, including reconstruction across all 303 inputs.
- [x] Implement validated API and focused regression tests (22 Python, 6 frontend tests).
- [x] Acquire and verify 13 licensed coronary/heart meshes with FMA mappings.
- [x] Build responsive dashboard and production bundle; one-row CSV and JSON export included.
- [x] Verify real browser input/result, mesh picking, orbit/zoom, export and 390px layout; capture evidence.
- [x] Finish README, five-page rendered/visually checked technical report, demo script and Devpost draft.
- [x] Verify new Windows Python environment, npm lock installation and source/model/mesh integrity; limits in verification.md.
- [ ] Publish public GitHub repository and record/upload 3–10 minute English YouTube demo.
- [ ] Confirm eligibility, real-name team roster, single track/team and final rules; submit on Devpost.

Local engineering completion does not establish clinical validation, public availability or submission completion. Every reported performance number comes from executed code.

## Delivered local state

The app runs at http://127.0.0.1:8000 when the bundled local server is active. README contains exact start commands. The local stack is Python 3.11 + FastAPI/sklearn/SHAP and React/TypeScript/Three.js. No runtime API keys or GPU are required.

Original raw-model nested OOF ROC-AUC: CAD 0.920, LAD 0.831, LCX 0.741, RCA 0.717. Raw LCX/RCA sensitivity is approximately 40% at 0.5; a low classification cannot rule out disease. The fitted models remain independent. Default baseline serving now discloses a CAD/vessel coherence adjustment to displayed probabilities; raw probabilities and SHAP are retained separately. The optional LCX candidate remains unadjusted. One contradictory source label is retained and covered by a diagnostic sensitivity analysis.

Remaining release work is the public repository/video and user-specific submission prerequisites above. Scientific next steps require new evidence, not more polish on these same 303 records.

## Research and usability improvement pass

- [x] Search Reddit, GitHub, anatomy products and primary user-research studies; document overlaps, evidence strength and audience hypotheses in `product_research.md`.
- [x] Replace the white dashboard with a navy/teal design, clear three-step introduction and one-click synthetic examples.
- [x] Expand licensed atlas geometry from 13 to 56 meshes with unchanged target mappings; add view presets, surface/see-through/arteries-only, isolate and context detail controls.
- [x] Add input search, missing-field filter, progress counts, disabled-action explanations, mobile input collapse and blank CSV template download.
- [x] Explain actual top model contributions in plain language and put model limitations beside predictions.
- [x] Verify final production build, six frontend tests, 22 backend tests, artifact identities and real desktop/mobile browser flows.
- [x] Update the five-page report, asset attribution, screenshots and source bundle.
- [ ] Optional later: run the proposed learner/educator comparison if participants become available; no demand or learning benefit has been claimed as validated. The feasible pre-submission human check is one qualified reviewer using `clinical_review_packet.md`.


## Bounded model improvement investigation

- [x] Prespecify and execute 11 candidate configurations, calibration and training-only cutoff policies across two nested-CV repeats.
- [x] Preserve negative replacement findings, every fold/prediction and production artifact hashes.
- [x] Add an interactive cutoff comparison with matched false-positive/missed-case counts, target/run selectors and evidence download.
- [x] Inspect the official UCI 45 archive for independent-data compatibility; record corruption, missingness and feature-definition barriers without merging it.
- [x] Verify evidence partitions/counts, seven frontend tests, production build and desktop/mobile browser flows.
- [ ] Obtain a compatible independent cohort and actual domain/user review; no external or clinical validation claimed.

Details and deployment rationale: `model_improvement_results.md`. The original five-page PDF describes the baseline; this new experiment is documented separately and has not been incorporated into that report.


## Top-three improvement delivery — 8 October 2026

- [x] Five-step guided synthetic case, linked measurements, real prediction/explanation/evidence, and stale-state clearing.
- [x] Mesh-anchored labels, three-vessel tour, focused orientation, responsive framing, keyboard controls and reduced motion.
- [x] Broad model families, TabICLv2, modality/missing-input diagnostics and compatible-data research, with negative findings retained.
- [x] Explicit optional LCX HistGradientBoosting comparison; baseline default preserved, candidate artifact/evidence verified and actual SHAP reconstruction checked.
- [x] Matching model evidence and versioned exports; main Python suite 49 passed/1 optional-dependency skip, frontend 11 passed, production build and real desktop/mobile browser checks.
- [ ] Independent compatible cohort, anatomical/domain review and actual audience study remain unavailable. No clinical or user-benefit validation is claimed.

Reports: `broad_search_results.md`, `tabicl_results.md`, `modality_audit_results.md`, `prediction_opportunities.md`. Original PDF covers the baseline. See the latest dated section of `verification.md` for the delivered UI checks.


## Independent-cohort follow-up

- [x] Acquire public CONFIRM clinical workbook, inspect schema and preserve raw file locally.
- [x] Freeze current app; separately train four shared-input models only on original 303 records after user authorization.
- [x] Stop on an unexpected three-class outcome field, document a coding-only amendment, and evaluate against the supplied binary stenosis endpoint.
- [x] Record negative external probability-transfer results, primary/secondary cohorts, uncertainty and exclusions. Four new read-only evidence audits passed; app hashes unchanged.
- [ ] Full 55-input app independent validation remains open. The completed reduced-model experiment has different inputs and a CCTA reference standard; it is not promoted into the app.

See `confirm_external_results.md` and `ml/experiments/confirm_external_v1/`.
## Separate CONFIRM development — 8 October 2026

- [x] Preserve original failed transport evidence and app hashes.
- [x] Freeze patient partitions, four model families, calibration and cutoff rules before new fits.
- [x] Complete 12 target/feature/coverage experiments with training-only family selection, separate calibration and reserved development-test evaluation.
- [x] Save matched comparisons, negative results, missing-input coverage, reliability bins, subgroup diagnostics, paired bootstrap intervals and every selected model.
- [x] Generate a standalone results report and reliability/error figure. No experimental models added to the app.
- [ ] Fresh independent evaluation of these changed models, authoritative field-code/timing review and clinical/user review remain open.

See `confirm_development_results.md`. CONFIRM has become development data for the changed models; its new test results are not an independent validation claim.
## Error analysis, site robustness and submission preparation — 8 October 2026

- [x] Execute 192 training-only model fits across fixed ensembles/feature ablations and nested cutoff evaluation; no improvement-screen winner.
- [x] Audit 12 site codes using 48 leave-code-out model fits, separate calibration and zero patient overlap with existing development-test/calibration rows.
- [x] Verify 303-row app explanation reconstruction and quantify five-background sensitivity for fixed linear models.
- [x] Verify original models and 56 meshes; exercise prediction/export readiness/LAD focus and mobile overflow in real Chromium.
- [x] Update and visually check the six-page PDF; correct local submission draft and demo narration; refresh portable evidence bundle.
- [ ] Public repository, narrated video/upload, clinical/anatomical/usability reviewers, authoritative feature-code review and final account/eligibility/submission remain outstanding.

Eleven focused tests passed across the two commands recorded in `next_steps_closeout.md`. App code and model files unchanged; no new external-validation or diagnostic-readiness claim.

## Subsequent accuracy update — 8 October 2026

- [x] Audit input consistency, derive BMI from weight/height, reject contradictory or out-of-range numeric inputs, and correct synthetic BMI values.
- [x] Run a fixed four-output forest comparison; preserve the negative nomination result and weaker RCA/LCX recall.
- [x] Measure a pilot-informed CAD/vessel probability projection with paired shared outer folds. Mean four-target Brier fell by 0.001198 across two repeats of the same 303 people; the engineering screen passed, with no independent validation.
- [x] Integrate the projection into default baseline serving as `1.0.0+coherence-v1`, keep raw model probabilities and SHAP separate, and leave the optional LCX candidate unadjusted.
- [x] Verify saved predictions, fold structure, projection optimality, API and UI semantics, full regression suites, desktop/mobile browser flows, the six-page report and the source bundle. Exact commands and results are in the latest section of `verification.md`.
- [ ] Obtain unused compatible patient data and reviewed feature/outcome definitions for an external accuracy test. No clinical or population-level gain is claimed.

The earlier dated sections describe the state at those checkpoints. The current product contract and limits are in `README.md` and `coherence_projection_results.md`.

## 9 October — next accuracy step and portability repair

- [x] Freeze and execute a separate 14-input source-only EBM/logistic comparison on the official 553-patient China cohort; preserve the negative result and all fixed sensitivity analyses.
- [x] Expose the comparison, calibration failure, false alarms and download in Model evidence; update the six-page report.
- [x] Add bounded API request handling and retry recovery for hung fetches and response bodies.
- [x] Preserve exact saved-evidence bytes in Git so an LF-configured archive does not invalidate historical hashes or break candidate/API startup.
- [ ] Qualified coronary/input review and an observed user task remain unperformed; no publication or final submission has been made.

## 10 October — local calibration and learning

- [x] Freeze two repeated five-fold adaptation designs with 64 and 442–443 local labels per fit; complete and preserve all 60 fits.
- [x] Compare unchanged source probabilities, local prevalence, offset, sigmoid and fixed local logistic models; preserve probability gains alongside increased missed positives at .5.
- [x] Verify training-subset preprocessing and label-perturbation isolation; reproduce saved probabilities and all metrics without changing historical app/transport artifacts.
- [x] Add a clearly labeled development follow-up to the China evidence card and report. No clinical model promotion or fresh external-validation claim.

## 12 October closeout — separate roles and operating-point evidence

- [x] Complete 30 frozen fits with distinct model-training, calibration and evaluation rows; publish every prespecified target and both repeats.
- [x] Show the local-learning gain, small uncertain sigmoid increment, missed cases and false alarms together in the evidence panel and report.
- [x] Audit a new public Beijing workbook and codebook. Preserve its unresolved population/endpoint issues and leave it unscored.
- [ ] Reviewer-defined intended use and error costs remain unavailable. All sensitivity targets are exploratory; no clinical model promotion or fresh external-validation claim.

## 13 October — relayed doctor call fixes

- [x] Record informal feedback and its unconfirmed scope; distinguish it from clinical sign-off.
- [x] Add source-based chamber, valve, muscle and vein detail (104 meshes), internal view, pale red myocardium/red arteries/blue veins and explicit probability-shading mode.
- [x] Display unknowns as dashes; preserve null through CSV, API snapshots and explanations. Remove six unchosen investigation defaults from each synthetic example.
- [x] Show exact ECG/echo inputs beside their supplied/unknown counts; retain source-trained CAD/vessel inference with no unsupported echo override.
- [x] Verify all model/metric hashes, 89 Python tests (one optional skip), 40 frontend tests, browser flows, six-page report and portable package.
- [ ] A precise reviewer-defined clinical objective, qualified anatomical sign-off and revised-screen review remain open.


## 14 October — calibrated ensemble accuracy improvement

The primary frozen ensemble improved matched mean target accuracy from 72.6% to 75.0% and mean Brier error from 0.1753 to 0.1650 across three internal repeats of 303 people. Feature-selection and spline follow-ups failed their improvement screens. All historical evidence was preserved. The optional research ensemble is available in Prediction model, with its own approximate attributions and versioned export; the baseline remains default.

[Delivery, complete verification and limits](accuracy_goal_delivery.md) records the replay checks, missing-input stress results, regression tests and desktop/mobile browser checks. This is an internal development gain, not independent or clinical validation. LCX/RCA sensitivity remains low, core-only improvement is uncertain, and the newly audited external workbook is not compatible full-input validation.
