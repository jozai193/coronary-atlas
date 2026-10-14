# TabICLv2 fixed-candidate result

TabICLv2 produced better mean CAD and LAD/LCX probability metrics than the saved nested baseline selector in this repeated internal evaluation, but the evidence is small-cohort and below the model authors' tested training-row range. The preregistered raw-predictor screen passes for CAD only; the probability-quality screen passes for CAD, LAD and LCX. These screens nominate research follow-up only. No production model, API, threshold, or explanation artifact was changed.

## Results

The fixed comparison used two repeats of five shuffled stratified outer folds on the same 303 people. The TabICLv2 configuration was fixed before reading these results. Baseline probabilities come from the saved nested selector on the exact same target, row, and outer fold; the runner asserted matching row order, labels, and fold assignment.

| Target | Baseline AUC → TabICLv2 | AUC change, repeat 1 / 2 | Baseline Brier → TabICLv2 | Brier change, repeat 1 / 2 | Raw screen | Probability-quality screen |
|---|---:|---:|---:|---:|---|---|
| CAD | .9098 → .9301 | +.0128 / +.0278 | .1045 → .0896 | −.0117 / −.0182 | Pass | Pass |
| LAD | .8287 → .8354 | +.0025 / +.0109 | .1683 → .1584 | −.0088 / −.0111 | Fail: mean AUC gain below .015 | Pass |
| LCX | .7276 → .7421 | +.0152 / +.0137 | .2061 → .2001 | −.0085 / −.0035 | Fail: mean AUC gain .0144 is below .015 | Pass |
| RCA | .7079 → .7148 | +.0291 / −.0152 | .2080 → .2071 | −.0117 / +.0099 | Fail: one repeat's AUC is lower | Fail |

The raw screen is the broad-search engineering rule: mean AUROC gain at least .015, no repeat worse, and mean Brier increase no greater than .005. The probability-quality screen requires mean Brier improvement of at least .005 and no repeat AUROC loss greater than .01. Both are engineering screens, not significance tests or deployment decisions.

At the unchanged 0.5 cutoff, mean recall/specificity moved from .910/.747 to .921/.782 for CAD, .870/.651 to .859/.694 for LAD, .382/.853 to .584/.753 for LCX, and .377/.839 to .421/.796 for RCA. The LCX recall gain is accompanied by lower specificity. These are cohort-specific descriptive operating points; no use-specific cost ratio was established.

## Fixed evaluation details

- Protocol: [tabicl_protocol.md](tabicl_protocol.md); runner: [research_tabicl_nested.py](../scripts/research_tabicl_nested.py).
- Runtime: Python 3.11.5, TabICL 2.2.0, PyTorch 2.10.0+cpu, scikit-learn 1.9.1, two CPU threads, no CUDA. The estimator used `n_estimators=8`, `batch_size=1`, CPU inference, and its documented remaining defaults. Forty outer fits completed with no reported model warnings or failed rows.
- Official checkpoint: `tabicl-classifier-v2-20260212.ckpt`, 110,368,038 bytes, SHA-256 `bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0`. The [authors' Hugging Face model card](https://huggingface.co/jingang/TabICL) labels the checkpoint BSD-3-Clause; the [official repository](https://github.com/soda-inria/tabicl) provides the code and pretraining implementation under the same license.
- Training uses only the 55 fields in `ml/schema.py::FEATURES`; each task receives only its own y column. `Cath`, `LAD`, `LCX`, and `RCA` are excluded from X. The model handles preprocessing internally; the source schema's categorical columns were passed as strings.
- The authors describe TabICLv2's tested pretraining/benchmarking range as 300–48,000 training rows and state that generalization below 300 has not been tested. Our outer training folds contain 242 or 243 rows. The API and checkpoint ran successfully at those sizes, but runnability does not establish performance support.
- All repeated folds reuse the same source cohort already used during model development. Two repeats are not 606 independent patients. There are no verified site, patient, or time identifiers for group-held-out evaluation. This is not external validation.

## Evidence and next decision

The CAD result passes both predeclared screens, and LAD/LCX pass only the probability-quality screen. Given the below-300 support boundary and reused-cohort evidence, keep these as research-only candidates. The separate [full-data explanation/runtime pilot](tabicl_explanation_results.md) verifies additive reconstruction for sampled empirical-background attributions, with roughly 16–19 seconds per target/profile and about 1.68 GiB peak RSS in the complete audit. It does not add model-quality evidence or remove the need for a frozen independent-cohort evaluation before promotion. Do not tune the model to the current outer outcomes or promote its probabilities into production from this run.

Machine-readable evidence, row-wise predictions, fold indices, repeat metrics, and hash manifest are under `ml/experiments/tabicl_v2/`.
