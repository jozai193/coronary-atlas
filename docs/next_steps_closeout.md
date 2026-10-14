# Hackathon improvement pass — 8 October 2026

## Executed

1. **Prediction error audit:** six fixed full/core/ensemble strategies, four targets, three outer folds and three inner cutoff folds, restricted to existing development-training patients. 192 classifier fits. No new test-set scoring or promotion. No candidate met the prespecified Brier improvement of .002 with AUC loss no worse than .01. The full ensembles gained only about .0002-.0003 Brier over full splines; removing symptoms/history generally worsened discrimination. See `confirm_error_followup_results.md`.
2. **Stronger robustness assessment:** discovered a complete 12-code site field and executed 48 leave-code-out fits on development-training rows, with fitting/calibration/validation separated and site excluded from predictors. Pooled CAD/LAD/LCX/RCA AUC .762/.756/.736/.755. Hospital identities are not verified; previous exposure to this registry remains disclosed. No universal enrollment date was established, so no temporal validation is claimed. See `confirm_site_results.md`.
3. **Explanation verification:** reconstructed all four baseline outputs across all 303 source rows (maximum probability residual 5.56e-16). Varied five backgrounds for the fixed LAD/RCA logistic models: average top-five overlap 92.7%/88.6%, worst 40%, no top-five sign disagreement in this specific audit. It does not cover refit stability or forest-background variation. See `output/verification/explanation_background_stability.json`.
4. **Anatomy/integration verification:** original source, four model hashes, anatomy manifest and all 56 meshes verified. Real Chromium computed synthetic Profile B, enabled export, exercised Focus LAD and checked 390-pixel layout with no horizontal overflow. This is a local functional check, not anatomical expert approval or a hardware benchmark.
5. **Submission preparation:** updated the technical report (six pages), rendered and inspected all six pages, corrected the existing submission draft and narration to distinguish application and research evidence. Refreshed source package. The Devpost submission-requirements connector returned an internal error; the saved official Track A requirements were used. No eligibility, registration or official-account readiness inferred.

## Verification

Ten focused external/development/error-follow-up tests passed, followed by one site-audit test. Tests independently reproduce metrics, verify immutable hashes, enforce training-only rows and held-out site separation, and verify saved threshold decisions. One read-only openpyxl extension warning; no raw workbook changed. This bounded audit made no app code/model change and claimed no new full-suite run. The later baseline display update is documented below.

## Remaining work requiring new evidence or user action

- A genuinely unused compatible cohort and authoritative feature timing/codes are still needed. Reusing this registry cannot establish fresh independent validation. Current site-code audit is a completed robustness step, not a replacement.
- Anatomical/clinical review and a small learner usability study still require actual reviewers. No outreach or fabricated feedback.
- Public GitHub repository: no remote configured. Source bundle is prepared, but destination/account and publication remain unresolved.
- English demo: updated 6:45 script is ready; final narrated recording and YouTube upload remain outstanding.
- Confirm real-name roster, eligibility and single team/track; final Devpost submission remains a separate action. No legal terms or registration accepted.

## Decision

At the close of this bounded audit, the development candidates did not support a model replacement. The later baseline display adjustment is a separate, explicitly documented change. Further predictive progress should be justified by additional information or a new validation design rather than repeated searches for a better displayed score.

## Later input accuracy guard

The 8 October [input accuracy guard](input_accuracy_guard.md) corrected inconsistent demonstration inputs and blocks unsupported numeric extrapolation. It changed API/form validation and synthetic examples, not fitted models or the historical experiments above. The requested predictive-accuracy goal remains open: this change does not establish a higher AUC, Brier gain or clinical validity. The next decisive step is an unused compatible cohort with reviewed field and outcome definitions.

## Subsequent coherence display update

A pilot-informed [shared-fold evaluation](coherence_projection_results.md) found a mean four-target Brier reduction of only .001198 when four raw baseline probabilities were projected to satisfy `CAD >= LAD, LCX, RCA`. Both repeats reused the same 303 people. Its engineering screen passed, and the default baseline now displays the disclosed projected values (`1.0.0+coherence-v1`) with each raw model value and adjustment shown separately. Fitted model artifacts and the historical raw-model evaluation were not changed. SHAP reconstructs raw model outputs, not projected display values. The optional LCX candidate (`1.0.0+histgb-lcx-v2`) remains unadjusted; displayed CAD/LAD/RCA values can therefore differ between variants even though those three fitted models are the same.

The separate [fixed four-output forest](multitask_results.md) met no nomination screen and was not integrated. Its interaction with the projection was not evaluated. Neither experiment supplies independent validation or resolves the need for reviewed input and outcome definitions on an unused compatible cohort.

## 9 October continuation

A new [AngioCAD independent-center experiment](angiocad_external_results.md) was completed under a frozen protocol using **13 shared inputs** and a separate source-trained model. It is new-population evidence for that reduced model, not a matched external validation of the 55-input app. A [held-out error challenge](heldout_case_mode.md) was added for teaching from four deliberately selected original-cohort rows; it uses saved raw fold outputs and does not supply an external performance sample. The six-page report and [judge-direction audit](winning_direction_audit.md) now include both findings. The broad pass at that point was 73 Python tests passed/one optional skip, 17 frontend tests passed and a production build. The frozen AngioCAD prediction verifier passed. The [7:30 demo script](demo_script.md) remains a plan, not a recorded video.

Human-dependent and publication work still open: an observed [learner comparison](learner_validation_plan.md), a qualified clinical/anatomy and field-coding review, public repository, English YouTube demo, real-name roster/eligibility verification and Devpost submission. The first two would support stronger value/meaning claims; the last four are submission gates. No participant or reviewer has been contacted from this task.

## 9 October pre-submission hardening

The revealed vessel cases now jump to **reference-only anatomy** with no saved probability mapped to the heart; a CAD case has no single-vessel jump. The Model evidence panel shows the separate AngioCAD 13-input transport table with its exact input-contract boundary. A post-hoc [whole-group missingness stress test](input_missingness_stress_results.md) reproduced the original raw out-of-fold predictions before masking held-out laboratory or echo inputs. The form and API now warn when either entire group is absent; the model, 0.5 cutoff and age-plus-28 guard remain unchanged. These warnings do not establish performance for naturally incomplete patients or an accuracy gain.

The integrated regression pass is **74 Python tests passed, one optional skip; 22 frontend tests passed; TypeScript/Vite build passed**. Hash, external-metric and missingness-stress verifiers passed. A 390 px browser check found and corrected unreadable side-by-side warning text. The [4:35 judge cut](demo_script_judge_cut.md) and [one-reviewer packet](clinical_review_packet.md) are ready but neither has been used. Public release and human review remain open.

## 9 October follow-through

The [next independent population experiment](peerj_external_results.md) is complete. The reduced-input EBM failed its comparison against logistic regression on 553 Chinese patients. This adds meaningful negative transport evidence, not an app accuracy gain. The product now shows it with the appropriate input/endpoint boundaries. Hung-request recovery and exact-byte Git portability defects were also repaired. Human input/clinical anatomy review and a short observed user task remain the most direct outstanding evidence; one qualified reviewer can cover the focused review packet, but cannot establish clinical validation or user demand alone.
