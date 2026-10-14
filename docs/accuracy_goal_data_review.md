# Accuracy-goal data search - 14 October 2026

Bounded follow-up of primary repositories while the frozen model experiments run. No patient data from this search entered training or evaluation.

## New acquired workbook

[Pontone, 2018 IJC single-stress CTP study](https://data.mendeley.com/datasets/smwx5gzvxn/1), DOI 10.17632/smwx5gzvxn.1, CC BY 4.0. The primary description concerns 130 symptomatic participants scheduled for invasive angiography/FFR, with CT anatomy and perfusion comparisons. The public API supplied `Database Blinded.xlsx` (163,785 bytes); its SHA256 matches the provider's `aea2c411f59d91fe183a3f97ea80dfcff8739f4e2cdd167ad75ba768bbb32ff2`.

The actual workbook has 130 ID-bearing rows and many imaging/procedure fields. It includes family history, smoking, hypertension, dyslipidemia and diabetes codes; its demographic and clinical-history heading columns are empty and it has no age/sex columns. Symptoms and angina have undocumented numeric codes. Named LAD/LCX/RCA invasive-angiography summary fields and segment percentages are present, but their exact threshold and branch aggregation must be established before harmonization. The absence of a lesion in a selected segment cannot establish a normal entire vessel. Scan heart rate, imaging findings and FFR/perfusion outcomes cannot silently become this app's resting pulse, clinical inputs or angiographic labels.

Decision: retain as a limited-feature data lead, unscored. It does not solve full-input validation. [Reproducible aggregate audit](../scripts/audit_stress_ctp.py), [audit output](../data/external_audit/stress_ctp_v1/audit.json), [source metadata](../data/external_audit/stress_ctp_v1/source_metadata.json). Raw data remain local and excluded from Git.

## Other checked leads

* [2018 Z-Alizadeh Sani paper](https://pubmed.ncbi.nlm.nih.gov/29903478/) describes a 500-person extension. The inspected public repository/search records did not establish an accessible matching 500-row table. Do not treat this as a new download or compare its reported accuracy to our held-out procedure.
* [X-Ray Angiography Images and SYNTAX-Score Dataset](https://figshare.com/articles/dataset/X-Ray_Angiography_Images_and_SYNTAX-Score_Dataset/25801447): public Figshare API confirms CC BY 4.0, a frame-selection Python file and a 740,742,561-byte RAR archive. The description concerns 232 angiography images and angiographic variables; no standalone compatible clinical table is listed. Large archive not acquired in this pass; contents remain unverified.
* [LAD_data](https://data.mendeley.com/datasets/spvxxsfvg9/1): author description concerns CCTA-derived geometric morphology, with curvature, torsion and tortuosity inputs. These are unavailable in the current app; no compatible clinical input/outcome table was established.

This does not exhaust all public data. More records help only when their measurements, outcome definitions, timing and independence can be established. No outreach, restricted access application or purchase was made.

## Additional internet search — 14 October 2026

### Downloaded: Duke ACATH

The [Vanderbilt Biostatistics source page](https://hbiostat.org/data/) grants permission to use its datasets with citation and attribution, and provides an [ACATH file](https://hbiostat.org/data/repo/acath) plus Stata/Excel downloads. I downloaded the official Stata file (`acath.dta`, 85,406 bytes; SHA-256 `b30537eb4c14827791e54a4b00411ddd31311f7d4cc635e8bcdafaf4d7ac92d0`) and inspected it locally. It has 3,504 rows and six columns: sex, age, symptom duration, total cholesterol, significant CAD (`sigdz`) and three-vessel/left-main disease (`tvdlm`). Cholesterol is absent for 1,246 people; `tvdlm` is absent for three. The official description defines `sigdz` as at least 75% narrowing in an important artery and `tvdlm` as three-vessel or left-main disease.

This is a genuine additional public patient-level cohort and a useful lead for a **separately defined reduced-input or severe-CAD model**. Only age and sex are exact shared app predictors; total cholesterol is not LDL, and symptom duration is not an app field. Its ≥75% outcome cannot be relabeled to the source's ≥50% CAD target, and it does not have the three required vessel-specific outputs. It therefore cannot be pooled into or used to evaluate/improve the current 55-input four-target model without changing the task. The repeatable [aggregate-only audit](../scripts/audit_duke_acath.py) saves no row-level output; the downloaded source remains local and ignored by Git.

### Stronger matching cohorts found, but record-level access is not open

| Cohort | What the primary source reports | Access/use status |
|---|---|---|
| [Emory “Heart” cohort](https://www2.cs.uh.edu/~ordonez/pdfwww/w-2006-HIKM-ardtmed.pdf) | The author's original paper describes 655 patients and 25 fields, including nine perfusion measures and four coronary narrowing outcomes. The 25 are not all shared clinical predictors. | Promising for a reduced-input vessel study. No public patient-level download or release terms verified. An access-route inquiry was sent through the author's department office on 14 October; [request and status](emory_data_access_2026-10-14.md). |
| [Indira Gandhi Medical College, Shimla](https://link.springer.com/article/10.1007/s40747-017-0048-6) | 335 consecutive suspected-CAD patients undergoing angiography; age, risk factors, LDL/HDL/TG, BP, BMI and CAD/severity are described. | Strong feature-level match, but the article page exposed no patient-level data download. A separate-access route would need to be established before use. |
| [Kano, Nigeria clinical dataset](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218284/) | Primary paper describes 506 complete records from two hospitals, with demographics, symptoms, glucose, lipids, BP, creatinine and CAD diagnosis. | Promising risk-factor overlap; no public patient-level repository/file was verified in this search. The article's reported row count and metrics are not data we can fit. |
| [ICADD, India](https://www.medrxiv.org/content/10.1101/2023.05.13.23289934v1) | 70 patients with CCTA, invasive angiography, FFR/RFR and available echo/hematology reports. | Authors say data are available on reasonable request; no public row-level download. Imaging/physiology labels and small size also make it a separate study. |

The [PLOS 2024 “improved accuracy” paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307952) links back to UCI dataset 411, the same 303-person Z-Alizadeh Sani cohort. Its high reported score is not extra patients or independent evidence. This pass found one immediately downloadable complementary cohort (Duke), and several more attractive but access-limited leads. No new rows were silently invented or merged. The most useful next acquisition is an approved Emory/Shimla/Kano patient-level release with reviewed predictor timing and angiographic label definitions.
