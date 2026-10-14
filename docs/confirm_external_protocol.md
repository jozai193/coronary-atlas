# Separate shared-input model: locked external transport test

This protocol is written before reading CONFIRM outcomes or computing external predictions. The user authorized a separate model; no model in the application will be changed. The existing app remains frozen in `data/external_audit/v3/frozen_models.json`.

## Scope

Train four simple classifiers on the original 303-row UCI 411 workbook only. Test them once against independent CONFIRM CCTA outcomes. This is an external transport experiment for a newly specified reduced-input model, not validation of the 55-input application and not a clinical approval. Source angiography and destination CCTA are different reference standards; their nominal 50% stenosis endpoints must not be presented as interchangeable measurements.

The public CONFIRM workbook has 27,125 rows with unique study IDs and 250 columns. It is not the 13,054-person analysis subset reported in the associated paper. The paper describes six countries outside Iran and prospectively collected pre-CCTA clinical variables; this supports independent cohort provenance. Available anonymous identifiers cannot prove patient-level separation globally. Exact shared-input overlap will be checked and matching rows excluded conservatively.

## Fixed inputs and models

Use only `Age`, `BMI`, `LDL`, `HDL`, mapped respectively from `age`, `bmi`, `ldl`, `hdl`. Age is years; BMI is the standard kg/m2 index; the article table explicitly documents LDL and HDL in mg/dL. Do not substitute total cholesterol, CT ejection fraction, imaging findings, downstream outcomes or any target label. Omit categorical inputs because the downloaded workbook does not provide an authoritative code dictionary. This deliberately small feature set tests feasibility, not the best achievable predictor.

For each target: median imputation, StandardScaler, LogisticRegression(C=0.03, max_iter=3000, random_state=20261007), no class weighting. All learned transforms fit on source rows only. C=0.03 is fixed from the existing source-side family, with no search here. Save four fitted artifacts and a hash manifest before the external evaluation command can run. For context, compute five-fold stratified source OOF performance of this same fixed pipeline; do not compare the reduced external model with the app's 55-input internal headline as though only population changed.

## Cohorts and labels

Primary: complete values for all four inputs, age 30–100, BMI 10–80, LDL 10–500, HDL 5–200. These broad sanity bounds are engineering checks fixed before external scoring, not clinical reference ranges. Require explicit zero in past_mi, past_pci and past_cabg. Require observed binary outcomes for each reported target. Report every exclusion and eligible count. Do not select rows based on prediction correctness.

Secondary: the same complete-input/sanity/overlap conditions, without the prior-history exclusion. Mark it secondary and report all four targets irrespective of results. Missing inputs are not imputed for external eligibility; the saved imputer is retained as a source-side pipeline component only. Complete-case selection can bias population coverage.

Use `obstructive_cad`, `lad_50`, `lcx_50`, `rca_50`; binary 1 denotes the named condition, 0 its absence. Record code values and check consistency with `lm_50` and the vessel OR as a data diagnostic, without rewriting labels. The paper defines obstructive CCTA disease as at least 50% diameter stenosis. Vessel headers support the nominal threshold; the workbook lacks a separate formal codebook, so numeric coding and vessel definitions remain a documented assumption requiring author confirmation. If observed values are not binary, stop rather than invent mappings.

## Reporting and freeze

No CONFIRM fitting, calibration, threshold optimization or family selection. Fixed classification cutoff 0.5. Report AUC, Brier, sensitivity, specificity, precision, confusion counts, prevalence, average predicted probability and source-prevalence constant baseline. Use 500 seeded patient-row bootstrap resamples for descriptive 95% AUC and Brier intervals; these condition on the fitted model and do not account for site clustering or source-fitting uncertainty. Do not select a winner across the four targets.

Store predictions by workbook row index only, aggregate summaries, exclusions and hashes. No names, dates or original study IDs in outputs. Raw external workbook stays local and is excluded from source packaging. Preserve negative results. After this run, CONFIRM is known development evidence: any model changes informed by it need a further untouched validation set.

Sources: [public CC BY 4.0 workbook](https://data.mendeley.com/datasets/shntp48zv9/1), [associated original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC7849944/), [source UCI cohort](https://doi.org/10.24432/C5461K).
