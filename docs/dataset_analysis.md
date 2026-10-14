# Dataset analysis

Source: UCI dataset 411, DOI 10.24432/C5461K, Alizadehsani, Roshanzamir and Sani. CC BY 4.0. Original ZIP and XLSX in `data/raw/`, unchanged. Analysis date: 7 October 2026.

The populated worksheet `Sheet 1 - Table 1` has **303 rows and 59 columns**. A second worksheet (`Sheet1`) has headers but **zero records**, including medication and segment-level column names. Those empty columns are NOT available features or lesion-coordinate evidence.

There are **55 eligible input columns**, before constant-feature handling. Labels are `Cath` (CAD/Normal) and LAD, LCX, RCA (Stenotic/Normal). All four are prohibited inputs to every task.

| Target | Positive | Negative | Positive fraction |
|---|---:|---:|---:|
| CAD | 216 | 87 | 71.29% |
| LAD | 177 | 126 | 58.42% |
| LCX | 119 | 184 | 39.27% |
| RCA | 114 | 189 | 37.62% |

Executed initial inspection found zero missing cells, zero exact duplicate rows, zero duplicate feature vectors, and one disagreement between Cath and the OR of the three vessel labels. Preserve supplied targets. Run a sensitivity analysis excluding that record; do not repair labels without source evidence.

`Sex` contains `Male` and the source spelling `Fmale`. Preserve canonical category codes while displaying Female in the UI. `VHD` mixes `N`, `mild`, `Moderate`, `Severe`. `BBB` uses N/LBBB/RBBB. Many numerically coded fields are categorical. `Exertional CP` is constant N; CHF has only one positive, LowTH Ang two, CVA and Weak Peripheral Pulse five each. These cannot support dependable subgroup conclusions.

Age spans 30–86, TG 37–1050, HDL 15.9–111, PLT 25–742. Outliers are observations to audit, not automatically erroneous records. Retain them; scaling, imputation and constant filtering are fitted only within training folds. Weight/BMI correlate at about 0.725 and Lymph/Neut at -0.923; independent SHAP contributions may split correlated information ambiguously.

Feature groups: demographics (age, sex, anthropometry), vitals (BP, PR), symptoms/history and examination, ECG, laboratory, echo (EF-TTE, Region RWMA, VHD). The UCI page lacks a complete unit/code dictionary. Conventional expansions are documented as interpretation rather than a verified original dictionary. Do not invent cardiac-enzyme fields: none occur in the populated sheet. Timing of measurements relative to angiography is undocumented; pre-test availability of echo/symptom features requires clinical review.

The reproducible EDA artifact below records every column's dtype, category values or numeric range, missingness and IQR flag counts. Groups are in data/processed/feature_schema.json and correlations in data/processed/correlations.csv. Descriptive EDA uses all rows; model selection does not use held-out outcomes. Constants are retained in the final pipeline, with no global feature selection.

Main limitations: small selected cohort, no external/time-separated validation, no verified patient IDs/site strata, no raw signals/images, incomplete feature definitions, rare categories, label inconsistency and possible acquisition-workflow leakage despite excluding target columns. Prediction of these labels is not population risk estimation.

<!-- GENERATED -->
## Executed per-column audit

IQR flags are descriptive, not deletion decisions. Numeric-coded categories use string representation for one-hot encoding.

| Column | Pipeline dtype | Missing | Distinct | IQR flags | Range or counts |
|---|---|---:|---:|---:|---|
| Age | int64 | 0 | 46 | 0 | 30 to 86; median 58 |
| Weight | int64 | 0 | 54 | 3 | 48 to 120; median 74 |
| Length | int64 | 0 | 44 | 0 | 140 to 188; median 165 |
| Sex | str | 0 | 2 | None | {'Male': 176, 'Fmale': 127} |
| BMI | float64 | 0 | 263 | 6 | 18.1 to 40.9; median 26.8 |
| DM | str | 0 | 2 | None | {'0': 213, '1': 90} |
| HTN | str | 0 | 2 | None | {'1': 179, '0': 124} |
| Current Smoker | str | 0 | 2 | None | {'0': 240, '1': 63} |
| EX-Smoker | str | 0 | 2 | None | {'0': 293, '1': 10} |
| FH | str | 0 | 2 | None | {'0': 255, '1': 48} |
| Obesity | str | 0 | 2 | None | {'Y': 211, 'N': 92} |
| CRF | str | 0 | 2 | None | {'N': 297, 'Y': 6} |
| CVA | str | 0 | 2 | None | {'N': 298, 'Y': 5} |
| Airway disease | str | 0 | 2 | None | {'N': 292, 'Y': 11} |
| Thyroid Disease | str | 0 | 2 | None | {'N': 296, 'Y': 7} |
| CHF | str | 0 | 2 | None | {'N': 302, 'Y': 1} |
| DLP | str | 0 | 2 | None | {'N': 191, 'Y': 112} |
| BP | int64 | 0 | 17 | 9 | 90 to 190; median 130 |
| PR | int64 | 0 | 21 | 13 | 50 to 110; median 70 |
| Edema | str | 0 | 2 | None | {'0': 291, '1': 12} |
| Weak Peripheral Pulse | str | 0 | 2 | None | {'N': 298, 'Y': 5} |
| Lung rales | str | 0 | 2 | None | {'N': 292, 'Y': 11} |
| Systolic Murmur | str | 0 | 2 | None | {'N': 262, 'Y': 41} |
| Diastolic Murmur | str | 0 | 2 | None | {'N': 294, 'Y': 9} |
| Typical Chest Pain | str | 0 | 2 | None | {'1': 164, '0': 139} |
| Dyspnea | str | 0 | 2 | None | {'N': 169, 'Y': 134} |
| Function Class | str | 0 | 4 | None | {'0': 211, '2': 73, '3': 18, '1': 1} |
| Atypical | str | 0 | 2 | None | {'N': 210, 'Y': 93} |
| Nonanginal | str | 0 | 2 | None | {'N': 287, 'Y': 16} |
| Exertional CP | str | 0 | 1 | None | {'N': 303} |
| LowTH Ang | str | 0 | 2 | None | {'N': 301, 'Y': 2} |
| Q Wave | str | 0 | 2 | None | {'0': 287, '1': 16} |
| St Elevation | str | 0 | 2 | None | {'0': 289, '1': 14} |
| St Depression | str | 0 | 2 | None | {'0': 232, '1': 71} |
| Tinversion | str | 0 | 2 | None | {'0': 213, '1': 90} |
| LVH | str | 0 | 2 | None | {'N': 283, 'Y': 20} |
| Poor R Progression | str | 0 | 2 | None | {'N': 294, 'Y': 9} |
| BBB | str | 0 | 3 | None | {'N': 282, 'LBBB': 13, 'RBBB': 8} |
| FBS | int64 | 0 | 113 | 30 | 62 to 400; median 98 |
| CR | float64 | 0 | 18 | 8 | 0.5 to 2.2; median 1 |
| TG | int64 | 0 | 147 | 16 | 37 to 1.05e+03; median 122 |
| LDL | int64 | 0 | 110 | 6 | 18 to 232; median 100 |
| HDL | float64 | 0 | 47 | 6 | 15.9 to 111; median 39 |
| BUN | int64 | 0 | 33 | 17 | 6 to 52; median 16 |
| ESR | int64 | 0 | 58 | 13 | 1 to 90; median 15 |
| HB | float64 | 0 | 66 | 7 | 8.9 to 17.6; median 13.2 |
| K | float64 | 0 | 27 | 2 | 3 to 6.6; median 4.2 |
| Na | int64 | 0 | 25 | 15 | 128 to 156; median 141 |
| WBC | int64 | 0 | 78 | 9 | 3.7e+03 to 1.8e+04; median 7.1e+03 |
| Lymph | int64 | 0 | 50 | 3 | 7 to 60; median 32 |
| Neut | int64 | 0 | 52 | 1 | 32 to 89; median 60 |
| PLT | int64 | 0 | 135 | 11 | 25 to 742; median 210 |
| EF-TTE | int64 | 0 | 11 | 15 | 15 to 60; median 50 |
| Region RWMA | str | 0 | 5 | None | {'0': 217, '2': 32, '1': 26, '4': 14, '3': 14} |
| VHD | str | 0 | 4 | None | {'mild': 149, 'N': 116, 'Moderate': 27, 'Severe': 11} |
| LAD | str | 0 | 2 | None | {'Stenotic': 177, 'Normal': 126} |
| LCX | str | 0 | 2 | None | {'Normal': 184, 'Stenotic': 119} |
| RCA | str | 0 | 2 | None | {'Normal': 189, 'Stenotic': 114} |
| Cath | str | 0 | 2 | None | {'CAD': 216, 'Normal': 87} |

CAD/vessel disagreement, zero-based row indices: [93]. Original worksheet row numbers are index + 2.

Raw workbook SHA256: `739343245c2ba578b541370217531750d8e936022f928b83e0d91756caa3ff0b`.
