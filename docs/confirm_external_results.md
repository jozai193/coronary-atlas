# Independent cohort experiment: CONFIRM

Completed 8 October 2026. **A separate four-input model was externally tested; it is not suitable for promotion. The existing 55-input app has not been independently validated.** No application model, prediction route, UI or training record changed.

## What was acquired

The public [CONFIRM workbook](https://data.mendeley.com/datasets/shntp48zv9/1), contributed by Filippo Cademartiri under CC BY 4.0 (DOI 10.17632/shntp48zv9.1), contains **27,125 rows, 27,125 distinct study IDs and 250 columns**. It includes explicit artery-level stenosis fields. Its SHA-256 is `67eef2dcdd4b62901a459f020c0231afdabae73e70c109bf57b0540f2e25035a`. This is the actual downloaded workbook, not a claim based on a search result. The workbook is larger than the paper-specific selected analysis cohort; we did not claim to reproduce that paper's cohort or model.

The [associated primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7849944/) describes a multicountry CT angiography registry. The original development cohort is the UCI Z-Alizadeh Sani angiography cohort from Iran. This supports independent cohort provenance; anonymous IDs cannot prove cross-registry identity separation. No exact match on the four shared numeric inputs was found. That fingerprint check alone is not a patient-identity proof.

A second download, the Mendeley Z-Alizadeh extension, was exactly the same 303×59 workbook as our training source, including its SHA-256. It was excluded as independent evidence. Other reviewed leads included MultiD4CAD (restricted access, limited clinical feature set), PARADIGM (longitudinal plaque progression task), and MIMIC-IV (credentialing/training/agreement required, with no verified matching artery-label table). Search and acquisition records are under `data/external_audit/v3/`.

## Why a separate model was necessary

CONFIRM does not supply enough equivalent measurements for the app's existing age-plus-28-of-55 input guard. The audit identifies only 24 even superficially corresponding inputs, including several that should **not** be substituted without domain review. In particular, CT ejection fraction is not automatically EF-TTE, and a binary wall-motion indicator does not reproduce the source regional code.

The user authorized a separate experiment. We fixed four numeric inputs—**age, BMI, LDL, HDL**—and a logistic regression pipeline, trained only on the original 303 records. No external record was used to fit scaling, imputation, coefficients, calibration, thresholds or model selection. Source-only artifacts were saved and hashed before external prediction. This intentionally simple compatibility experiment does not test the strongest possible shared-input model.

## Protocol and mapping correction

The [original protocol](confirm_external_protocol.md), original runner, source models and original app hashes remain frozen. The first evaluation stopped before making predictions because `obstructive_cad` contained three codes. A subsequent coding-only audit found the binary `stenosis_50` field: it equals 0 for all 19,320 rows with obstructive_cad 0/1 and equals 1 for all 6,969 rows with obstructive_cad 2. A [recorded amendment](confirm_external_mapping_amendment.md) selected that supplied binary endpoint before external scoring; it did not change the fitted models or other rules.

The selected binary CAD endpoint agrees with the OR of LM/LAD/LCX/RCA indicators on all **25,326** rows where all five fields are observed. The [registry methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC3402246/) describe the nominal >=50% stenosis endpoint. However, a formal workbook codebook was not supplied: the column mapping is an explicit inference from published definitions, field names and cross-column consistency, not author-confirmed coding. This qualification limits the strength of the validation claim.

## Primary results

Complete inputs, prespecified broad sanity ranges, age at least 30, no exact four-input source match, and explicit absence of prior MI/PCI/CABG were required. Each target also required an observed label. AUC measures ranking; Brier measures probability error (lower is better). Sensitivity and specificity use the frozen 0.5 cutoff.

| Target | External rows | Same reduced model, source OOF AUC | External AUC (95% interval) | Brier | Sensitivity | Specificity |
|---|---:|---:|---:|---:|---:|---:|
| CAD | 7,095 | 0.718 | 0.656 (0.639–0.673) | 0.409 | 98.4% | 7.6% |
| LAD | 7,086 | 0.667 | 0.644 (0.627–0.662) | 0.303 | 85.8% | 30.9% |
| LCX | 7,045 | 0.679 | 0.647 (0.618–0.673) | 0.164 | 28.5% | 86.6% |
| RCA | 7,090 | 0.601 | 0.626 (0.604–0.647) | 0.166 | 15.0% | 92.4% |

The CAD model predicted an average probability of **69.6%**, while **18.0%** of the primary cohort had the supplied CCTA outcome. At cutoff 0.5, it detected 1,254 positives and missed 21, but produced **5,379 false positives** and only 441 true negatives. High sensitivity here is not good overall performance: specificity was only 7.6%. The source cohort CAD prevalence was 71.3%, which is consistent with a large population/prevalence shift, though this experiment cannot isolate its causal contribution.

LAD, LCX and RCA also overestimated average probabilities. These results support retaining the separate model as a research artifact only. They do not establish that the full app has the same performance; the full app was not evaluated.

## Coverage, secondary analysis and limitations

Of the 27,125 rows, 16,831 lacked one or more of the four numeric inputs; 149 complete rows failed the prespecified broad sanity bounds. There were 10,145 eligible complete-input rows. Requiring explicit absence of prior disease/intervention excluded another 3,045, including unknown histories, before target-specific missing labels were removed. Complete-case and history selection can bias the evaluated population; this is not a validation on all 27,125 patients.

The prespecified secondary analysis retained prior/unknown histories. It yielded CAD AUC .665 (9,345 rows), LAD .652 (9,280), LCX .660 (9,077), and RCA .643 (9,174). It did not reverse the poor probability-transfer conclusion. Full metrics and confusion counts for every target are saved; no outcome was suppressed.

Intervals use 500 patient-row bootstrap resamples. They condition on the saved model and do not account for site clustering or uncertainty from fitting on only 303 source cases. CT and invasive angiography are different reference standards; the source dataset's unit/timing documentation is incomplete. The external paper itself cautions that CCTA can overestimate stenosis, especially with calcification. This is therefore a qualified independent-cohort **transport experiment**, not a demonstration of diagnostic safety or equivalence between reference standards.

CONFIRM outcomes are now known. Any new feature choices, recalibration or tuning informed by these results make it development data for that changed model. A further untouched cohort or prospectively reserved data would be needed for a fresh confirmatory assessment. Do not silently adjust this model and reuse these numbers as independent validation.

## Reproduction and integrity

- Source-only fit: `python scripts/validate_confirm_external.py fit`. Existing fitted artifacts cannot be overwritten by this command.
- Original evaluation failure is preserved in `attempt_1_stopped.json`; do not rerun it as an accepted evaluation.
- Amended evaluation: `python scripts/validate_confirm_external_v2.py evaluate`; refuses to overwrite existing results and verifies frozen source/model identities.
- Read-only verification: `python -m pytest tests/test_confirm_external.py -q`: **4 passed**. Tests reproduce metrics from all eight saved prediction files, validate source-only preprocessing statistics, verify original app hashes, and check the amendment and evidence identities.
- Artifacts: `ml/experiments/confirm_external_v1/`. Raw source workbooks are local-only; the external workbook is excluded from source packaging. Prediction outputs use workbook row indices, not original study IDs or dates. Public data remains credited to its authors and CC BY 4.0.
