# TabICLv2 full-cohort explanation/runtime pilot

The fixed TabICLv2 candidate generated an auditable additive explanation for both artificial profiles across CAD, LAD, and LCX. Four sampled feature permutations reconstructed the model probability difference from the specified eight-row empirical background with a maximum recorded residual of `0.0`. This is the telescoping identity built into each permutation path; it does not prove that four permutations estimate the full Shapley value accurately, have converged, or that the artificial profiles are clinically meaningful.

## Measured results

| Target | Profile | Positive probability, seed 20261007 / 20261108 | Mean background probability, about | Cross-seed Spearman | Top-10 overlap |
|---|---|---:|---:|---:|---:|
| CAD | A: numeric medians, categorical modes | .96 / .95 | .73 | .962 | 10/10 |
| CAD | B: numeric 75th percentiles, second-most-common categories | .89 / .90 | .73 | .946 | 10/10 |
| LAD | A | .75 / .73 | .61 | .978 | 8/10 |
| LAD | B | .75 / .77 | .61 | .959 | 10/10 |
| LCX | A | .47 / .46 | .20 | .980 | 8/10 |
| LCX | B | .50 / .54 | .20–.21 | .987 | 10/10 |

Across the six target/profile pairs, the seed-specific 55-feature attribution vectors had mean absolute differences from `0.00077` to `0.00205` probability points (0–1 probability units). Top-ten absolute attribution overlap was 8–10 of 10 features. Both model seeds used the same four feature permutations, so these cross-seed comparisons do not estimate Monte Carlo sampling error or show that four permutations have converged. The complete values for every feature, permutation, and model seed are in `ml/experiments/tabicl_v2/explanation_pilot/result.json`; no feature is designated clinically important by these rankings.

The mean sampled attributions sum to the model probability difference between the profile endpoint and the mean background prediction. Each per-path and averaged reconstruction residual was zero at recorded precision. Repeated full-profile predictions within the batched coalition evaluations varied by at most `1.46e-7` from the row's batch position; the protocol records this numerical spread and defines the reported profile endpoint as the mean of the four path endpoints.

## Local cost and cache check

- Six cached full-cohort model fits (three targets × two seeds) used the 8-estimator official checkpoint. Fit time summed to `29.58 s` (`4.70–5.42 s` each).
- The 12 profile explanations used four 55-feature permutations and eight background rows. Attribution prediction time summed to `204.17 s` (`16.23–19.07 s` per target/profile/seed case).
- Six same-seed, uncached twin fits were used only to check inference-cache behavior; the maximum probability difference between cached and uncached copies on the same eight background rows and two profiles was `1.09e-6`. Cache inference is numerically close but not bit-for-bit identical at a `1e-8` tolerance.
- Total wall time for the complete audit, including cache-twin checks and setup, was `265.82 s` (4 min 26 s), under the 10-minute pilot cap. Peak process RSS was `1,717.46 MiB` (about 1.68 GiB). CPU only, two Torch threads, no GPU, network or runtime API.

This supports a technically feasible on-demand explanation for one selected target/profile when the cached fitted model is already in memory: about 16–19 seconds for the attribution calculation on this machine. Computing the three target explanations synchronously would take roughly 50 seconds per profile at these measured rates, before UI work; a two-profile, two-seed audit took over four minutes. That cost is too high for a default synchronous all-target path. No TabICL model or SHAP explanation was added to product code in this pilot.

## Method and limits

The run follows [the frozen protocol](tabicl_explanation_protocol.md), uses all 303 rows only to fit an explanation model, and computes no held-out metrics. The input contract is the 55 allowed features; each model is fit on its own target. Profiles and the eight source-row backgrounds are specified in the protocol and saved with the output. The Monte Carlo permutation-SHAP estimate averages four seeded feature orders. Its value function takes profile features in a subset and the remaining values from each complete background row, then averages positive-class probability.

This empirical interventional background can create feature combinations that are absent from the source data, including broken dependencies between correlated features. Profile A and B are synthetic, feature-wise summaries and can also be internally implausible. The attribution is a description of how this particular fitted model changes its probability under those substitutions. It is not a causal effect, treatment recommendation, clinical rationale, or explanation of disease biology. The cohort and TabICLv2 training regime remain the same small, reused dataset; these results do not add external validation or cure the below-300-row support limitation.

Reproduction files: `scripts/research_tabicl_explanation.py` and `ml/experiments/tabicl_v2/explanation_pilot/result.json`; the read-only [artifact verifier](../scripts/research_verify_tabicl_explanation.py) checked all 12 cases, six cache comparisons, four permutations per case, reconstruction identities, and source/protocol/runner/checkpoint hashes without fitting a model. The checkpoint has the authors' BSD-3-Clause metadata; this does not convey rights to the clinical dataset or establish suitability for care.
