# Frozen PeerJ China cohort comparison

Frozen 9 October 2026 before fitting these reduced models or computing any predictions for this cohort. The paper, raw schema, marginal counts, ranges and anomalies were inspected to establish mapping. Its published associations and scores were visible; no local model result was used to choose this design. This is a new patient cohort for a **separate 14-input CAD task**, not external validation of the existing 55-input app or its 55-input EBM candidate.

## Source and endpoint

Train only on the 303 UCI Extension of Z-Alizadeh Sani patients. Test once on the official supplement to [Cao et al., PeerJ 2022, DOI 10.7717/peerj.14078](https://doi.org/10.7717/peerj.14078): 553 people from the First Affiliated Hospital of the University of Science and Technology of China, January 2017–January 2020, study age eligibility 18–65 and no prior CHD. The observed ages are 26–65. The paper's CHD definition includes symptoms, ischemic ECG changes, discharge diagnosis and >50% stenosis in a main coronary branch. The original source label nominally uses >=50%; threshold, diagnostic-workflow and selection differences remain. There are no individual vessel outcomes here.

The official [PMC Cloud supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC9653049.1/peerj-10-14078-s001.csv) is 92,823 bytes, SHA-256 `c94efdcd7aed7d2b02c242e405c3d07faffb66687ec119743648335299808cc5`, 553 unique rows, 45 columns, no missing cells. The article is CC BY 4.0; PMC metadata marks it open access and not retracted. `Group=1` (201) denotes CHD and `0` (352) non-CHD, matching Table 1. IDs are used only to check uniqueness and excluded from inputs and released predictions. Raw files remain local in the ignored `data/external_audit/peerj_v1/raw/` directory. Different countries/centers support independence; anonymized records cannot prove identity separation.

A secondary author's GitHub mirror was inspected during acquisition: it has 715 rows, 162 exact duplicates and some altered values. It is **not used**. NCBI retired its old FTP/OA lookup service in August 2026; acquisition used the [official new cloud service](https://registry.opendata.aws/ncbi-pmc/).

## Locked input mapping

Use exactly these 14 fields in the order shown. Table 1 supplies destination units and category counts. Source units remain conventional interpretations from the original project audit, with incomplete original measurement/timing documentation. Unit arithmetic does not establish assay or workflow equivalence.

| Source field | Destination field | Fixed conversion to source representation |
|---|---|---|
| Age | Age | years, unchanged |
| Sex | Gender | 1 -> Male (355), 2 -> Fmale (198), checked against Table 1 |
| BMI | BMI | kg/m², unchanged |
| DM | Diabetes | 0/1 -> source string 0/1; counts 450/103 match no/yes in Table 1 |
| HTN | Hypertension | 0/1 -> source string 0/1; counts 241/312 match no/yes |
| FBS | Fasting blood glucose at admission | mmol/L / 0.05551 -> mg/dL |
| TG | Triglyceride | mmol/L / 0.01129 -> mg/dL |
| LDL | LDLC | mmol/L / 0.02586 -> mg/dL |
| HDL | HDLC | mmol/L / 0.02586 -> mg/dL |
| HB | HGB | g/L / 10 -> g/dL |
| K | Blood potassium | monovalent mmol/L equals mEq/L |
| Na | Blood sodium | monovalent mmol/L equals mEq/L |
| WBC | WBC | 10^9/L * 1000 -> cells/µL |
| PLT | PLT | 10^9/L equals 10^3/µL |

Conversion references: CDC [glucose](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_GLU.htm), [HDL](https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/datafiles/p_hdl.htm), and [LDL/triglycerides](https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/datafiles/p_trigly.htm). No rounding, clipping, repairing, source-range truncation or cohort-specific scaling. Exclude smoking because current-versus-ever semantics are unresolved, BP because the source does not establish systolic equivalence, BUN because the reported analyte/unit convention needs review, echo because method/timing equivalence remains unresolved, all nonshared fields and all outcomes/IDs.

## Models and order

1. Assert exact source and external hashes, rows, labels and code counts. Freeze this protocol digest in the runner. No external feature/outcome is passed to any fit call.
2. Compare one fixed logistic pipeline (training-only numeric median imputation and StandardScaler; categorical mode imputation and one-hot encoding; C=.03, max_iter=3000, seed 20261007) with one fixed EBM. No tuning, calibration, class balancing or feature selection.
3. EBM is interpret-core 0.7.8, 14 explicit continuous/nominal inputs, interactions=0, max_bins=64, outer_bags=8, learning_rate=.015, max_rounds=1000, early_stopping_rounds=100, early_stopping_tolerance=.00001, validation_size=.15, smoothing_rounds=75, min_samples_leaf=4, missing='separate', n_jobs=1, random_state=20261007. This configuration follows the prior EBM trial; no external result chooses parameters. Both source and destination are complete for this mapping.
4. Use StratifiedKFold(5, shuffle=True, random_state=20261007) for paired source OOF context. Fit both final models on all 303 source rows. Save models, OOF rows, source row partitions, timings, software versions and file hashes **before** external scoring. Abort on any failed fit; one numerical thread, maximum ten minutes for the fit phase.
5. In a separate evaluation command, verify the freeze and score the destination once. Preserve results regardless of direction. Do not retrain, recalibrate, select thresholds or add predictors after seeing this test.

## Analysis fixed before scoring

Primary: all 553 official rows at threshold 0.5. Retain the supplied WBC=1069 (10^9/L) anomaly in this headline to avoid silently repairing data. Two sensitivity sets are fixed: exclude WBC>100 in the original destination units; and restrict to source-overlap ages >=30. Report both regardless of score. A diastolic-BP value of 888 is also anomalous but excluded from the feature contract entirely.

For both models, report AUC, Brier, log loss, accuracy, sensitivity, specificity, precision, F1, confusion counts, prevalence, mean probability and ten fixed-width reliability bins. Compare with the source-prevalence constant. Primary paired AUC/Brier differences use 1,000 seed-20261009 patient-row bootstrap draws, sharing each sampled row set between models. Intervals condition on fixed fitted models and omit training, measurement and center uncertainty. There is one primary CAD comparison; subset/subgroup results are descriptive, not alternative headlines.

Describe age <50 / >=50 and sex groups with n, positives and both model metrics only when n>=30 and both classes have >=10 records. Do not claim fairness from nonsignificance or these small strata. Also report mapped-input distribution shifts and fractions outside source numeric ranges. Audit EBM native additive terms by reconstructing the decision score and its sigmoid probability for all source/destination rows; exact additive terms are not SHAP or clinical causes.

The engineering follow-up screen is primary EBM AUC gain >=.015 with nonworse Brier, OR Brier improvement >=.005 with AUC loss <=.01. Passing nominates another independent test and input/domain review; it does not replace the app. A primary probability-transfer failure or poor case detection must be prominent even if EBM beats the comparator. No clinical recommendation, rule-out, prospective benefit or 55-input validation claim follows from this experiment.
