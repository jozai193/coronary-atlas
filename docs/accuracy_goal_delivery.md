# Accuracy improvement delivery — 14 October 2026

The primary calibrated ensemble passed the frozen internal improvement screen and is available locally as **Research calibrated ensemble · adjusted display** in Prediction model. The baseline remains the default. The optional candidate changes all four models and supplies its own approximate permutation attributions. Exports identify version `1.0.0+calibrated-ensemble-v1`.

## Measured improvement

All values below are means over three repeated five-fold evaluations of the same 303 people, at the unchanged 0.5 threshold, after the same coherence projection. The comparator is the original selection procedure refitted inside each matching training partition. These are paired internal development results, not independent clinical validation.

| Target | Baseline accuracy | Ensemble accuracy | Baseline AUC | Ensemble AUC | Baseline Brier | Ensemble Brier |
|---|---:|---:|---:|---:|---:|---:|
| CAD | 85.9% | 87.1% | 0.9083 | 0.9207 | 0.1080 | 0.0965 |
| LAD | 77.2% | 79.1% | 0.8169 | 0.8408 | 0.1693 | 0.1548 |
| LCX | 63.3% | 66.7% | 0.6960 | 0.7250 | 0.2150 | 0.2066 |
| RCA | 64.1% | 67.0% | 0.6998 | 0.7234 | 0.2089 | 0.2022 |

Mean accuracy across the four targets rises **72.6% to 75.0%** (+2.34 percentage points); this is not the fraction of patients with all four labels correct. Mean Brier error falls **0.17532 to 0.16504**, a 5.9% relative reduction. The primary Brier difference is -0.01027, with conditional patient-bootstrap interval [-0.01424, -0.00638]. It improves in all three repeats. This interval excludes retraining, prior model search and site uncertainty.

Sensitivity/specificity tradeoffs remain: CAD sensitivity falls 92.7% to 92.3%; LCX specificity falls 82.6% to 82.1%. Ensemble LCX/RCA sensitivities are only 42.9%/38.6%. A better aggregate score does not establish a safe screening or diagnostic tool. Full per-target and per-repeat metrics, including negative feature-selection and spline results, remain in [the results report](accuracy_goal_results.md).

## Missing observations

Saved outer-fold models were replayed after fixed artificial masks, using only their training-fitted imputers. No models were refitted and no missingness threshold was optimized.

| Scenario | Mean Brier difference, ensemble minus baseline | Conditional 95% interval |
|---|---:|---|
| Complete | -0.01027 | [-0.01424, -0.00638] |
| Laboratory omitted | -0.00646 | [-0.01036, -0.00277] |
| Echo omitted | -0.00916 | [-0.01309, -0.00532] |
| Laboratory, echo and ECG omitted | -0.00165 | [-0.00584, +0.00240] |

The core-only result is uncertain. Artificial masks of originally complete source records do not validate naturally missing observations or define a clinical minimum-input rule. The API and interface retain this warning. [Frozen protocol](accuracy_missingness_protocol.md), [machine-readable results](../ml/experiments/accuracy_missingness_v1/results.json).

## Implementation and verification

The packaged models fit the frozen primary procedure to all 303 source records. Their in-sample predictions were checked only for engineering correctness and never counted as accuracy evidence. Three profile predictions with their own attributions took approximately 0.87–0.91 seconds locally. The attribution sums reconstruct raw calibrated output within 2.23e-16, but allocation is approximate, feature hybrids can be unrealistic, and stability/causal meaning are unvalidated.

Verification completed:

- Fresh-process ensemble replay: all 60 outer roles, 1,260 inner member predictions, 3,636 output records and 96 metric groups reproduced; maximum outer probability residual zero. All 212 protected historical files remained unchanged.
- Feature/spline replay: 60 roles, 2,160 inner predictions and 120 selected outer models reproduced. Both approaches failed their improvement screens; those negative results are preserved.
- Missingness replay: all 14,544 target prediction records across 240 model/scenario roles reproduced.
- Focused backend regression suite: 42 tests passed. The separately expanded candidate unit suite passed all three tests, including optional dependency absence. Research suites passed 23 tests plus the separate missingness test. Counts overlap and are not a unique combined total.
- Frontend: all 57 tests in 19 files passed; TypeScript/Vite production build passed. Existing dependency deprecations, constant-feature ANOVA warnings in research tests and the large Three.js chunk advisory remain.
- Real Chromium at desktop and 390×844 mobile: candidate selection, Profile C prediction, paired evidence, own attribution labels, versioned JSON export and clearing results after model switching checked. Mobile document width was 380px; browser console had zero errors/warnings. Screenshots were visually inspected. This was browser emulation, not a physical-device test.
- Optional dependency environment passed `pip check`. The default Docker image was not rebuilt or exercised in this work.

The final production-path verifier is [verify_packaged_ensemble.py](../scripts/verify_packaged_ensemble.py). It checks candidate artifact/evidence hashes and replays the deployed probability function with the saved held-out fold models for all four input scenarios. The check passed with zero maximum probability residual across all 14,544 held-out target predictions. Its durable [receipt](../output/verification/2026-10-14-packaged-ensemble.json) distinguishes those held-out checks from full-data packaged-model inference.

## Scope and remaining evidence

The work delivered a measurable internal improvement and an optional usable model. It does not prove a globally optimal model or exhaust every public dataset. The fresh data search found a 130-person imaging study and a public 3,504-person Duke catheterization cohort. The former has missing app inputs and unresolved endpoint codes; the latter shares only age/sex and uses a stricter CAD endpoint. Neither can validate or be pooled into the current 55-input four-target model. More closely matched Shimla, Kano and Emory cohorts are described in papers, but no open patient-level download was verified. Details and local Duke audit are in the [data review](accuracy_goal_data_review.md).

The next substantial evidence gain requires an unused cohort with compatible pre-outcome inputs, reviewed vessel/CAD definitions and independently confirmed participant separation. No new split of these 303 people supplies that independence. No clinical default promotion, public deployment, submission, outreach, purchase or patient-data collection was performed.

The original goal is satisfied at the internal research-performance level: source evidence audited; fixed ensemble/calibration and feature approaches executed with fold-local selection; negative results and uncertainty retained; historical evidence preserved; stronger candidate packaged with its own explanations; actual API/UI behavior verified. Independent clinical validation remains an explicit unmet research requirement, not a completed part of this result.
