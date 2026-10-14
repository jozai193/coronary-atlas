# TabICLv2 explanation and runtime pilot protocol

This protocol is fixed before running the explanation pilot. The pilot fits the official TabICLv2 checkpoint on all 303 source rows for CAD, LAD, and LCX, then measures exact-model inference and an empirical-background, permutation-sampled Shapley approximation. It does not compute held-out performance metrics and does not alter production files.

## Question and limits

Can the fixed TabICLv2 research candidate produce auditable per-feature probability attributions for two artificial profiles with an acceptable local CPU runtime, while the sampled attributions reconstruct the fitted model's probability difference from an explicit empirical background?

These are explanations of the fitted model on synthetic feature combinations. They are not causal effects, treatment guidance, patient-specific clinical explanations, or evidence of predictive validity. Mixing features independently with background rows can create combinations outside the source distribution, especially for correlated or constrained measurements. No medical interpretation is assigned to an attribution sign or magnitude.

## Frozen implementation

- Source: the same read-only 303-row UCI 411 workbook used by the TabICLv2 candidate run, with exactly `ml/schema.py::FEATURES` (55 features). Each target model uses its own binary source label only for fitting. No held-out or external metric is computed.
- Targets: CAD, LAD, and LCX. RCA is excluded from this bounded pilot because the candidate did not clear either engineering screen for RCA.
- Estimator: TabICL 2.2.0, official local TabICLv2 checkpoint `tabicl-classifier-v2-20260212.ckpt`, SHA-256 `bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0`, eight estimators, batch size 1, CPU, two worker threads, no automatic download, same remaining fixed settings as `docs/tabicl_protocol.md`. `kv_cache=True` is enabled to cache training-row computations for repeated explanation predictions; it is an inference cache, not a different trained candidate.
- Fit each target twice using model random states `20261007` and `20261108`. The second seed measures implementation/ensemble variation; it is not another cohort or independent validation.
- Artificial profile A: feature-wise median for each numeric field and most frequent observed value for each categorical field (ties resolved lexicographically).
- Artificial profile B: numeric 75th percentile and, for each categorical field with multiple observed values, its second-most-frequent value (ties lexicographically); single-valued fields retain their sole observed value. These profiles are deterministic feature-wise summaries and may be internally implausible.
- Empirical background: source `X` rows with zero-based indices `[0, 43, 86, 129, 172, 215, 258, 302]`, selected without using any labels. The same rows are used for all models/profiles.
- Value function: for a feature subset `S`, form eight hybrids by taking profile values on `S` and one complete empirical background row on all remaining features; average the fitted model's positive-class probabilities. This is an interventional empirical-background value function and can break feature dependencies.
- Batch arithmetic: predict the background, query profile, and all coalition rows in one call. Define the profile endpoint as the mean of the four sampled paths' full-coalition predictions and report the maximum spread across those repeated profile rows. This keeps the endpoint aligned to the same prediction batch and exposes any small floating-point batch-position variation.
- Estimator: for each model/profile, average feature marginal contributions over four independently drawn, seeded random feature permutations. Permutation seeds are `20261008`, `20261009`, `20261010`, and `20261011`, shared across targets, profiles, and model seeds. Call this a Monte Carlo permutation-SHAP approximation, not exact SHAP. The empty coalition is the mean predicted probability on the eight background rows; each path's full coalition is its repeated-row model prediction for the profile, and the reported profile endpoint is their mean.
- Fidelity check: for each permutation, verify the sum of the 55 marginal contributions equals `f(profile) - mean_background(f(background))`; also verify the averaged contribution vector reconstructs the same difference. Record all residuals and fail if maximum absolute residual exceeds `1e-8`.
- Seed stability: for each target/profile, compare the two seed-specific 55-feature attribution vectors using Spearman rank correlation, top-10 absolute-attribution overlap, mean absolute vector difference, and total absolute attribution magnitude. These are descriptive stability summaries, not inferential tests.
- Resource cap: CPU only, two Torch threads, no cloud/runtime API, and a ten-minute wall-clock limit. Sample process RSS during fits and attribution predictions. If the cap is reached, preserve the partial run and mark the affected cases incomplete; do not change the number of profiles, backgrounds, permutations, estimator size, or seed after seeing attribution results.

## Artifacts and decision rule

The runner is `scripts/research_tabicl_explanation.py`; output belongs only under `ml/experiments/tabicl_v2/explanation_pilot/`. The result records source, checkpoint, protocol, script, and package versions/hashes; fit and prediction time; CPU and peak process RSS; profile values; background indices; per-feature contributions; reconstruction residuals; and cross-seed stability.

This pilot can establish implementation fidelity and local resource cost only. It cannot justify model adoption, clinical claims, a causal reading, or external validity. A user-facing research mode is technically feasible only if all cases complete under the time cap and the artifact records the background, profile, model seed, probability, attribution unit, and reconstruction residual alongside the explanation.
