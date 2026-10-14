# Doctor feedback relayed by the user — 13 October 2026

Partial, informal feedback from the user's cousin, described as a doctor. Specialty, relevant coronary experience, review duration and an independently confirmed list of inspected screens remain unspecified. No completed sign-off, clinical validation, endorsement or quoted publicity permission is recorded.

## Reported observations

- The reviewer asked how to analyze Profile A and where the patient details, ECG and echo reports were.
- The user reported that the reviewer saw zeros in the ECG fields and expected some positive findings. Profile A deliberately uses zero/absent flags for those findings; Profile B has ST depression and T-wave inversion set to 1. Neither example has an original tracing, echo image or case report.
- The reviewer questioned why a 72-year-old Profile B has a `mild` valvular-disease value.
- User's exact report: “she said its not correlat9ng and we shouldnt just put mild when he has 99 percent prediction for the disease”. The 99% value is a user-reported observation, not a verified reviewer interpretation or a new accuracy result.

## Source check and interpretation

`scripts/create_samples.py` independently fills unspecified numeric fields with cohort medians and categorical fields with cohort modes, then applies explicit overrides. Both examples inherit VHD=`mild`, the most frequent source category (149/303), and neither explicitly chooses it on clinical grounds. The source field supplies no valve identity or echo measurements. Profiles assembled from independent marginal defaults have unverified clinical coherence; the overall default combination must not be presented as a clinician-authored patient case.

The four models predict CAD and LAD/LCX/RCA stenosis labels. They do not predict valve disease or grade valve severity. A CAD probability is also not a measured stenosis percentage. The reported juxtaposition therefore identifies an input/output interpretation problem and missing case context. It does not by itself establish that mild valve disease is inconsistent with a high CAD-label probability. We have not inferred a clinically correct substitute severity from the displayed prediction.

Primary context: [NHLBI coronary heart disease diagnosis](https://www.nhlbi.nih.gov/health/coronary-heart-disease/diagnosis), [NHLBI heart valve disease diagnosis](https://www.nhlbi.nih.gov/health/heart-valve-diseases/diagnosis). Source dataset field criteria and demo-case clinical coherence remain incompletely established.

## Implemented response

- Add exact per-field example provenance: explicit demo choice, derived BMI or inherited source-cohort default. Mark clinical sign-off unavailable.
- Display a synthetic-profile context card, with the valve input and its origin visible without opening the form. Explain the distinction from CAD probability and absence of source reports.
- Provide a read-only grouped summary of all 55 values and origins, with links to the corresponding editable field.
- Add an input-form reminder that valve severity is an input and the CAD estimate does not grade it.
- Clear the example context when users edit measurements so it cannot describe stale inputs as the original profile.

All A/B input values are preserved, including VHD, because no authoritative corrected case has been supplied. Changing a valve value merely to match a high coronary prediction would not establish clinical coherence. The numerical model outputs, weights and historical evaluation records are unaffected by the presentation change. The reviewer should inspect the revised screen and supply specific corrections or a clearly synthetic, clinician-authored example if willing. No such revised-screen review has yet been reported.

## Further call points and implementation

The user subsequently relayed these additional requests: more detail in the whole heart, unknown values shown as dashes rather than zero, brighter red arteries/blue veins/pale red heart tissue, and predictions that “match” ECG/echo with greater trust in echo. When asked which echo target was intended, the user said the exact wording was uncertain and asked for an educated decision. These are relayed points, not a complete medical specification or a reviewed prediction threshold.

Implemented after that clarification:

- Expand the unchanged source atlas from 56 to 104 meshes with cardiac veins, chamber cavities, valve leaflets and papillary muscles, plus an internal view. Original target geometry/anchors and global transforms are preserved. New detail is reference anatomy, not patient-specific echo reconstruction.
- Render pale red heart tissue, red arteries and blue veins. A separate probability mode uses red shades only for the three coronary targets. Structure colors encode vessel type rather than oxygenation. No disease or valve-severity color is assigned to context meshes.
- Unknown numeric/categorical fields display a dash; CSV dash/blank imports become null. Supplied zeros remain supplied codes. Explanations and input snapshots keep the difference visible; computation uses the existing trained imputers.
- **Superseding the earlier preservation-only response above:** remove six inherited investigation defaults from both synthetic examples: Q wave, ST elevation, LVH, poor R progression, BBB and VHD. These were not explicitly chosen for the examples; they now remain unknown. Each example supplies 49/55 values. Explicit ST depression/T-inversion choices and EF/RWMA inputs are preserved. All example inputs remain synthetic and unreviewed.
- Add a panel showing the exact ECG/echo inputs behind each completed prediction, with links back to their fields and supplied/unknown counts. It does not relabel a model estimate as an echo diagnosis.

No blanket echo override was introduced. [NICE CG95](https://www.nice.org.uk/guidance/CG95/chapter/recommendations) says resting ECG findings can be inconclusive and should be considered with history/risk factors. [NHLBI](https://www.nhlbi.nih.gov/health/angina/diagnosis) describes echo pumping findings and coronary angiography as different observations/tests. Our supplied echo fields (EF/RWMA/VHD) are not confirmed labels for all four coronary outcomes. The existing [modality audit](modality_audit_results.md) found consistent echo gains for CAD/LAD in one fixed model family on reused source patients, but no universal benefit across all targets. That supports showing echo information prominently and reviewing definitions; it does not establish a clinical weighting rule or permission to manufacture agreement. No new models were fitted.

Remote A/B sample checks found the new unknown flags preserved as null and listed for imputation. The numerical A/B probabilities happen to match the previous examples because the existing imputation restores those modal categories for computation; this is not new accuracy evidence. The UI no longer presents them as supplied investigation results. Model/metric hashes remain unchanged. Revised-screen clinical review and a precise intended-use/error-cost specification are still outstanding.

## Follow-up before asking for another review

The next reviewer defaults are now fresh **C/D** examples (ages 56/64, 45 supplied and 10 unknown observations). Historical A/B fixtures are preserved separately. A **Case summary** page presents key inputs, ECG/echo, all four estimates, raw-output distinctions, input origins and missingness; exported worksheets retain full precision. An assisted photo importer proposes explicitly supported printed measurements for individual confirmation. It does not infer diagnoses, ECG findings or missing details. Public fictional Labcorp specimen pages exercise the real browser OCR path; there is no clinical OCR validation. See [feature scope and verification](report_autofill_and_summary.md). The doctor has not yet reviewed this build.

The revised workspace loads inputs before inference, exposes case facts and A/B differences, and shows draft ECG/echo observations. Notes explain limited source codes without inventing diagnoses. Supplied/imputed counts sit beside CAD. Printable worksheets preserve exact inputs, origins and separate outputs; edited drafts omit stale predictions. Optional sheets reproduce two consecutive attributed public-development records with recorded labels, without new scoring or original ECG/echo reports. See [readiness notes](review_readiness_2026-10-13.md) and [review packet](clinical_review_packet.md). The doctor has not yet rechecked these changes.
