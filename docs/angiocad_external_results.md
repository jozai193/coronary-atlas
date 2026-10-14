# AngioCAD: new patient population transport test

Completed 9 October 2026 under the [pre-score frozen protocol](angiocad_external_protocol.md). This is the first test here on a **new invasive-angiography center's patient cohort**. It evaluates a **separate 13-input logistic model trained on the original 303 UCI patients**. The 55-input Coronary Atlas app was neither modified nor externally tested by this run. No external data were used for fitting, calibration, feature selection, threshold selection or retraining. The original app's four headline nested-CV AUCs must not be compared to these figures as if only the population changed: inputs, model family and vessel endpoint derivation also changed.

## Provenance and execution

[AngioCAD](https://doi.org/10.5281/zenodo.15826856) supplies CC BY 4.0 clinical and segment-label workbooks; its [paper](https://www.sciencedirect.com/science/article/pii/S0169260726001331) reports retrospective cases from Shahid Chamran Heart Center, Isfahan. Published descriptions place the original [Z-Alizadeh Sani cohort](https://www.sciencedirect.com/science/article/pii/S0169260713000801) at Shahid Rajaei Cardiovascular Center, Tehran. The centers differ; anonymous data cannot formally rule out patient identity overlap. A six-field exact-match screen found no source/external matches, but it is a weak identity check. AngioCAD has 413 unique label IDs and 377 unique clinical IDs; 36 label-only patients cannot be predicted. Its feature workbook repeats the stenosis outcomes. The runner constructed an explicit 13-field allowlist and never used those repeated labels, diagnosis, angiography series, Gensini score or other outcome-derived fields as predictors.

Raw workbook SHA-256: features `978f2415ab52f11724e1ef00bb63597b8497487afd84b97f7112fc7975a33295`; labels `5bba3f4ba8bed0df0d2f412d5e2ca6deacca0eff20d531a599fe1b8f4d897425`. Local acquired raw files stay out of the source package. Run with `python -m ml.angiocad_external fit`, then `python -m ml.angiocad_external evaluate`; the second phase checked the frozen source model, protocol, runner and data hashes. The [read-only verifier](../scripts/verify_angiocad_external.py) reproduced all 16 external target/cohort AUC, Brier and confusion results and all four source OOF AUC/Brier pairs from the saved row-level predictions. Its recorded output was: **PASS: 16 external target/cohort metrics and 4 source OOF pairs reproduced; hashes match**.

## Cohort and endpoint coverage

The primary input rule retained **363/377** matched feature patients: six lacked age, six had a broad prespecified numeric anomaly (one BMI, one creatinine, four platelet values), and two had fewer than 10/13 available inputs. The 363 kept patients include 32 missing BMI and 44 missing smoking values, which received source-fitted imputation. Complete-input sensitivity retained 283 patients before endpoint ambiguity. AngioCAD's diagnosis entries include many acute presentations; it is a selected catheterization population, not a population-screening sample.

For the primary endpoint, main-vessel proximal/mid/distal bins above 50% are positive; `NL`/`1-25` are negative. `26-50` without a higher bin remains unresolved and is excluded for that target because it may contain exactly 50%; source labels nominally use at least 50%. CAD additionally includes left main. Among the 363 input-eligible patients, ambiguous endpoints exclude 18 CAD, 41 LAD, 32 LCX and 37 RCA rows. Interpretability and prevalence thus vary by target. Branch-inclusive labeling and input-cohort alternatives were prespecified sensitivity analyses, not a search for the best metric.

## Primary held-out scores

All probabilities below come from the **frozen source-only full fit** and all decisions use 0.5. Confidence ranges are 1,000 patient-row bootstrap resamples of fixed external predictions. They omit uncertainty from source fitting, site choice, measurement meaning and endpoint bins.

| Target | External n (positive) | AUC (conditional 95% range) | Brier | Mean prediction / observed prevalence | Sensitivity / specificity | TN / FP / FN / TP |
|---|---:|---:|---:|---:|---:|---:|
| CAD | 345 (276) | **0.781** (0.722–0.841) | 0.144 | 0.695 / 0.800 | 0.931 / 0.362 | 25 / 44 / 19 / 257 |
| LAD | 322 (228) | **0.723** (0.661–0.779) | 0.196 | 0.586 / 0.708 | 0.746 / 0.574 | 54 / 40 / 58 / 170 |
| LCX | 331 (90) | **0.709** (0.644–0.763) | 0.191 | 0.387 / 0.272 | **0.400** / 0.846 | 204 / 37 / 54 / 36 |
| RCA | 326 (155) | **0.687** (0.627–0.746) | 0.234 | 0.399 / 0.475 | **0.316** / 0.830 | 142 / 29 / 106 / 49 |

The fixed 13-input procedure's **source five-fold OOF** AUC/Brier were CAD 0.790/0.164, LAD 0.695/0.216, LCX 0.732/0.205 and RCA 0.712/0.210. This is contextual evidence, not an internal-to-external causal comparison: populations and label construction differ. The external Brier scores beat a fixed **source-prevalence** constant for all four tasks (CAD 0.168, LAD 0.222, LCX 0.213, RCA 0.259); a destination-prevalence baseline would be a different, post-observation comparison. Average probabilities versus observed prevalences show underprediction for CAD/LAD and overprediction for LCX; a single mean difference does not fully measure calibration. The new data preserve the major vessel failure: 54/90 LCX positives and 106/155 RCA positives were missed at 0.5. CAD specificity is only 25/69, so the high sensitivity has substantial false alarms.

## Prespecified sensitivity checks

| Analysis | CAD AUC / n | LAD AUC / n | LCX AUC / n | RCA AUC / n | What changed |
|---|---:|---:|---:|---:|---|
| Primary main-vessel | .781 / 345 | .723 / 322 | .709 / 331 | .687 / 326 | Prespecified primary |
| All age-present, anomalies unfiltered | .778 / 353 | .714 / 330 | .704 / 338 | .685 / 334 | Relaxed completeness/range screen |
| Complete 13 inputs | .770 / 269 | .716 / 251 | .708 / 258 | .722 / 254 | Selected complete-input subset |
| Branch-inclusive bins | .777 / 353 | .745 / 330 | .697 / 317 | .674 / 329 | Include diagonal/OM/PDA/PLB branches |

The broad cohort filter makes little difference to the four AUCs. The RCA complete-input AUC rises, but this is a different selected subset and is not a model improvement. Adding side branches changes case labels and interpretable counts, so its scores cannot be treated as repeat measurements of the same endpoint. All sensitivity Brier, prevalence, confusion and conditional intervals are retained in [external_results.json](../output/research/angiocad_v1/external_results.json).

## Decision for the product

This is useful evidence that a modest shared-input predictor can retain some discrimination across two selected Iranian angiography centers. It **does not establish clinical readiness, a reliable rule-out, benefit for patients, or accuracy of the app's 55-input models**. The source and AngioCAD have incomplete comparable unit/timing dictionaries, source patient identities are unavailable, and AngioCAD's coarsened stenosis bins prevent exact threshold matching. The result strengthens the project's *evidence-aware educational* case: show that cross-center performance and error types matter, with especially visible LCX/RCA misses. Keep the current production artifacts and clinical-use disclaimer unchanged. A future app model based on these 13 features would require a new, separately reviewed protocol and usability/clinical evaluation.
