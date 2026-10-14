# CAD–vessel probability coherence: internal result

Completed 8 October 2026. This was a **pilot-informed** evaluation: a read-only single-repeat pilot suggested a small gain before the [repeated-run protocol](coherence_projection_protocol.md) was fixed. The two five-fold runs reuse the **same 303 patients**, so they are two views of one cohort, not 606 independent observations or an untouched confirmation. The evaluation did not alter fitted model artifacts; a disclosed baseline serving layer was integrated afterward.

## Method and measured result

For each shared held-out fold, all four baseline models were selected and fitted using only that fold's training patients. The four probabilities were then projected onto the constraint `CAD >= LAD, LCX, RCA`, using probabilities alone. The shared folds matter: historical target-specific out-of-fold probabilities cannot be joined into one leakage-safe four-output vector because their training sets differ.

| Repeat | Mean four-target Brier, raw → projected | Mean per-patient sum of four squared errors, raw → projected | Incoherent probability rows, raw → projected | Largest absolute probability adjustment |
|---|---:|---:|---:|---:|
| 1 | 0.172124 → 0.170247 | 0.688495 → 0.680987 | 79 → 0 | 0.230243 |
| 2 | 0.175809 → 0.175290 | 0.703237 → 0.701161 | 42 → 0 | 0.191545 |

The mean Brier change across repeats was **−0.001198** (lower is better). The [prespecified engineering screen](coherence_projection_protocol.md#adoption-screen-and-limits) passed: both aggregate Brier values decreased and no target crossed its Brier, AUC or recall loss limit. This is a small same-cohort effect, not a demonstrated improvement in clinical accuracy or external transportability.

At the fixed 0.5 class cutoff, mean accuracy across the four labels changed from **73.10% to 73.35%** in repeat 1 and **73.02% to 73.10%** in repeat 2. No individual target lost classification accuracy in either repeat; these differences amount to only three and one additional correct target-label decisions, respectively, among 1,212 decisions per repeat. They are descriptive same-cohort counts, not evidence of a reliable effect in new patients.

The table below gives projected minus raw metrics. AUC and recall gains are positive; a negative Brier change is favorable. Recall uses the unchanged 0.5 cutoff.

| Target | Repeat 1 ΔAUC | Repeat 1 ΔBrier | Repeat 1 Δrecall | Repeat 2 ΔAUC | Repeat 2 ΔBrier | Repeat 2 Δrecall |
|---|---:|---:|---:|---:|---:|---:|
| CAD | +0.002927 | −0.001332 | +0.013889 | +0.005109 | −0.001949 | +0.004630 |
| LAD | +0.008206 | −0.004807 | −0.005650 | −0.000852 | +0.000095 | 0 |
| LCX | +0.000594 | −0.000319 | 0 | 0 | +0.000012 | 0 |
| RCA | +0.004084 | −0.001051 | 0 | +0.001300 | −0.000235 | 0 |

Euclidean projection guarantees that the **sum of four squared probability errors for a patient cannot increase when that patient's four binary labels satisfy the constraint**. It does not guarantee improvement for any one target, AUC, recall, or an incoherent label vector. The supplied workbook has exactly one contradictory label vector, zero-based row **93**. Its observed labels were preserved, and its projected-minus-raw sum of squared errors happened to be zero in both saved runs. The geometric guarantee was checked only on the other 302 coherent rows in each repeat.

## Decision and evidence boundary

This establishes a modest internal probability-coherence result for the baseline procedure. The application now uses this deterministic projection for **default baseline display** and reports the raw model probability, adjusted probability and change separately. It does **not** establish a clinically accurate or externally transportable default. Existing SHAP values reconstruct each **raw fitted-model probability**; they do not explain the joint projected probability. The optional LCX HistGradientBoosting candidate stays unadjusted. Interactions with that candidate, the fixed multitask forest, and calibration were not evaluated. No independent compatible invasive-angiography cohort was available.

The [saved result](../ml/experiments/coherence_v1/results.json) contains source/protocol/runner hashes, all outer partitions and selections, both aggregate summaries and the screen. `ml/experiments/coherence_v1/repeat_{1,2}.csv` contains every held-out row, four labels, raw probabilities and projected probabilities. The read-only verifier passed: it checked 303 shared held-out rows in each repeat, source and code identities, geometric optimality, the coherent-row squared-error bound, row 93, aggregate and target metrics, and the saved screen. Current protocol and runner hashes match those recorded in the result.

Reproduce or verify from the repository root, using the project Python environment:

```powershell
.\.venv\Scripts\python.exe scripts/verify_coherence_evidence.py
```

To regenerate the experiment, run `.\.venv\Scripts\python.exe ml/evaluate_coherence.py` in an isolated clean copy with an empty `ml/experiments/coherence_v1/` destination; the runner refuses to overwrite saved evidence.
