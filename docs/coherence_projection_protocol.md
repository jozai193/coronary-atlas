# CAD–vessel probability coherence experiment — 8 October 2026

This protocol formalizes one task-specific postprocessing idea after a read-only, single-repeat pilot suggested a small gain. It is **pilot-informed internal development**, not a preregistered independent validation. The author-supplied [dataset description](https://data.mendeley.com/datasets/9k56pwtvz9/1) says CAD occurs when at least one LAD, LCX or RCA artery is stenotic. The local workbook has one contrary source row (zero-based row 93); its four labels are preserved.

## Fixed method

Let `p = (CAD, LAD, LCX, RCA)` be the four independently fitted probabilities for one patient. Compute the unique Euclidean projection onto `C = {q in [0,1]^4 : q_CAD >= q_LAD, q_LCX, q_RCA}`. This uses only the four already predicted probabilities; it never uses a patient's observed outcomes at inference. When CAD is below any vessel probability, pool CAD with the highest violating vessel probabilities until their mean is no lower than the next vessel. Set those pooled values to the mean and leave other vessel estimates unchanged. No threshold, learned parameter, calibration fit or label repair is added.

For every logically coherent binary outcome vector `y in C`, projection cannot increase the **sum** of four squared probability errors for that patient. This is a property of Euclidean projection onto a closed convex set; it does not guarantee each target's Brier score or AUC improves, and the anomalous source row is outside `C`.

## Leakage-safe paired evaluation

- Use `ml.schema.FEATURES` as the only inputs and preserve all four source labels. Use two shared five-fold outer partitions stratified by CAD with seeds 20261007 and 20261108. Unlike the historical target-specific OOF files, every target in a given repeat has the **same test people per fold**. The target-specific historical OOF predictions must not be combined, because their different training folds can contain other targets' test people.
- In each shared outer training partition, rerun the original three-fold ROC-AUC selection among the four baseline configurations for each target, using the same seed rule as `ml/train.py`; fit each selected pipeline only on that fold's training rows. Predict the four held-out probabilities and project them as a vector. Save the outer indices, selections, raw and projected row-level probabilities. No held-out label may influence model selection or projection.
- Report each repeat separately: mean per-patient sum of four squared errors, mean four-target Brier, per-target AUC/Brier/accuracy/recall/specificity/confusion counts, number and size of adjusted predictions, and the row-93 effect. Repeats are the same 303 patients, not 606 independent observations. Verify the geometric inequality for every coherent source row and the probability-order constraint for every output.

## Adoption screen and limits

Consider a clearly identified **coherence-adjusted output layer** only if both repeats lower mean four-target Brier, no target loses more than 0.005 Brier or 0.01 AUC in either repeat, and no target loses more than 0.02 recall at the fixed 0.5 cutoff in either repeat. Report all individual metrics even if the screen fails. Passing does not establish clinical validity or external transportability.

If integrated, retain raw fitted-model probabilities and their SHAP reconstruction as separate evidence. The geometric adjustment must be disclosed as a distinct joint-probability step with its own exact delta; SHAP must never be represented as reconstructing an adjusted probability. Do not silently replace the independent outputs or describe the constraint as lesion localization. An independent compatible cohort and source-label review remain required before a clinical or transportability claim.
