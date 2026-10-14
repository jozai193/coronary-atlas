# Fixed shared-label forest: internal result

Completed 8 October 2026 under the [fixed protocol](multitask_protocol.md). One native four-output random forest (120 trees, minimum leaf size 5, square-root feature sampling) was compared with the saved target-specific baseline selector. All 55 allowed inputs were used; none of the four observed outcome labels entered the input features. For each target's saved outer fold, all four training labels came only from its training patients and only the target's held-out output was scored. The source's contradictory CAD/vessel label at zero-based row **93** was preserved.

The two five-fold repeats reuse the **same 303 patients**, not 606 independent cases. Candidate and baseline were compared on identical target-specific row IDs and folds. Unlike the separate coherence experiment, the four targets here use their own target-stratified outer partitions; their out-of-fold vectors must not be combined into a leakage-safe joint output.

## Measured comparison

Changes are candidate minus baseline. Positive AUC and negative Brier changes favor the candidate; negative recall change means more missed positives at the unchanged 0.5 cutoff. Each mean is the arithmetic average of the two repeat differences.

| Target | Mean ΔAUC | Mean ΔBrier | Recall change, repeats 1 / 2 | Prespecified nomination screen |
|---|---:|---:|---:|---|
| CAD | +0.003539 | +0.011563 | +0.041667 / +0.023148 | Fail: Brier worsened in both repeats |
| LAD | +0.005291 | +0.000014 | +0.028249 / −0.028249 | Fail: mean AUC below +0.015 and Brier did not improve |
| LCX | +0.005343 | −0.000682 | −0.084034 / −0.033613 | Fail: repeat-one recall loss exceeds 0.05 |
| RCA | +0.021118 | −0.004783 | −0.087719 / −0.017544 | Fail: repeat-one recall loss exceeds 0.05 |

RCA's AUC and Brier improved in both repeats, but its repeat-one recall fell from **40.35% to 31.58%**. LCX's repeat-one recall fell from **40.34% to 31.93%**. These are material losses in the already weaker vessel operating points. **No target met the prespecified screen** for nomination to an independent test; there was no parameter search or post-run threshold adjustment. The screen is an engineering rule, not a significance test.

## Decision and limits

The forest remains a research artifact. No multitask production model, API route or SHAP explanation was added. Existing application SHAP explains the original raw single-target model outputs; it cannot be presented as an explanation for this candidate. Interaction between this candidate and the coherence projection was **not evaluated**. The fixed candidate was run on a repeatedly studied single cohort, without independent validation or verified measurement timing, so neither the favorable RCA ranking result nor the failed screen establishes clinical performance elsewhere.

The [saved result](../ml/experiments/multitask_v1/results.json) records source/protocol/runner identities, target-specific matched metrics for both repeats, and each screen decision. Eight `ml/experiments/multitask_v1/{target}_repeat_{1,2}.csv` files contain row identities, outcomes, folds and paired probabilities. A read-only check found 303 unique row IDs in every CSV and independently recomputed each candidate AUC, Brier and recall to the saved values. Current protocol and runner hashes match those in the result.

To regenerate in an isolated clean copy with an empty `ml/experiments/multitask_v1/` destination, run:

```powershell
.\.venv\Scripts\python.exe ml/multitask_fixed.py
```

The runner refuses to overwrite the saved result in the current workspace. Inspect the existing evidence with `Get-Content ml/experiments/multitask_v1/results.json`.
