# Relayed review feedback and resulting input contract

Follow-up implementation and remaining evidence requirements are recorded in [clinical evidence resolution](clinical_evidence_resolution_2026-10-14.md). The user confirmed that only public dataset examples are available; no original patient reports or independent cohort was supplied.

The user later supplied a partly completed echo template as an example. It now grounds [echo source-text review and reference-range safeguards](echo_template_review_2026-10-14.md). Actual-photo OCR abstained on numerical values; corrected-text regression checks are reported separately. This example does not supply original UCI reports or an independent clinical cohort.

14 October 2026. Feedback was relayed by the user during a doctor call, not collected as a signed clinical validation. Exact clinical intended use, specialist scope and diagnostic error costs remain unresolved.

## Reported concerns

- EF and valve assessment need to be present when reviewing the echo context.
- ECG and echo information should be available; incomplete key information should stop prediction rather than silently rely on imputation.
- A complete set of inputs would be a better example to inspect than the incomplete synthetic C/D cases.
- The reviewer asked how much LAD/LCX/RCA blockage is present. The source data contain categorical outcomes, not exact narrowing percentages. Model probabilities must not be presented as measured narrowing.

## Implemented

- Both browser and API reject predictions without age, echo EF, valve assessment or any of the seven recorded ECG input fields. The existing minimum of 28 available inputs remains. Valid zero codes count as supplied; null/blank does not. The API checks this before calling any of the three available model options. This conservative engineering rule implements the request for ECG/echo availability; it is not a clinically validated minimum feature set or proof that the case is diagnostically sufficient.
- Quick-start examples cannot bypass the guard. Changing a required value clears old results; the summary and export cannot retain a previous prediction.
- C/D stay incomplete synthetic examples, with no invented negatives or valve grades. Their predictions are blocked until required observations are genuinely supplied.
- Added **Recorded profile R1**, copied from the first recorded UCI development-dataset row: all 55 model inputs, EF 50%, recorded valve category `N`. It has no original ECG tracing or complete echo report attached. This is a development example, not an independent test. Source: DOI [10.24432/C5461K](https://doi.org/10.24432/C5461K), CC BY 4.0; worksheet row 2, zero-based record 0.
- Recorded CAD/LAD/LCX/RCA labels are displayed separately as reference outcomes, never sent as input features. Exact blockage percentages are explicitly unavailable. These development labels cannot establish the live model's accuracy on new patients.
- The investigation panel, case summary and worksheet state that only selected echo inputs are represented. Even all three model echo fields together are not a complete echo report. No diagnosis is inferred from EF alone or from an ECG zero code.

Follow-up questions sent through the user: which exact fields are clinically required, and what valve detail is needed? The relayed answer names ECG/echo and requests the corresponding echo values; a detailed report/code dictionary remains unavailable. No arbitrary clinical values or required report fields outside the dataset have been fabricated.

The separately launched updated review instance preserves the existing review session. The current password is unchanged; credentials and temporary URLs remain in ignored local state. No live baseline weights, trained imputers or original evaluation metrics were changed by this feedback implementation. Historical missing-input experiments remain historical research; their permissive inference scenarios are no longer accepted by the public API when required observations are missing.

## Echo scope and incomplete-example follow-up

The user additionally relayed: “2d echo mentiones everything”, including “the flow the pattern of flow and the valve blockage”, and observed that C/D produce no prediction because their inputs are incomplete. This records the feedback as relayed; it does not assert that the reviewer defined every required echo field or endorsed a new model behavior.

An echo assessment can describe cardiac structure/function and valve findings, with Doppler assessing blood flow through chambers and valves. See [NHLBI heart tests](https://www.nhlbi.nih.gov/health/heart-tests). Valve narrowing/leakage and coronary-artery obstruction are separate findings; neither a full Doppler report nor measured LAD/LCX/RCA narrowing is recoverable from the app's three source echo fields (`EF-TTE`, `Region RWMA`, `VHD`). The existing broad valve category does not encode valve-specific flow velocities, gradients, valve areas or detailed narrowing/leakage severity. The original reports and detailed code dictionary remain unavailable. No new echo measurements, thresholds, required fields or model weights are inferred from this feedback.

Current C/D each have 45 supplied inputs and 10 unknowns: all seven ECG fields, RWMA, valve assessment and obesity. The required-field rule blocks them because the seven ECG fields and valve assessment are unknown, despite having more than 28 observations. C/D now show **Incomplete · input review only** before selection; selection loads the inputs for review without treating the expected block as a failed prediction request. A nearby explanation lists missing requirements and offers **Load complete recorded profile R1**. R1 has 55 recorded development-source inputs; it can demonstrate prediction but has no original complete echo report and provides no independent accuracy evidence. Changing back to an incomplete example clears previous predictions. The echo panel explicitly names the missing Doppler and detailed valve information. Prediction requirements and source observations are preserved.

Verification: 17 focused frontend tests passed across App, InvestigationContext and predictionReadiness; the final TypeScript/Vite build passed with the existing chunk-size advisory. Real Chrome against the rebuilt running review instance confirmed zero prediction requests when selecting C/D, one successful R1 request with all 55 non-null inputs, unknown observations retained, no error alert for the expected incomplete state and stale prediction/export clearing when returning to C. Mobile width was 390/390px with zero console errors/warnings. Desktop echo-scope and desktop/mobile incomplete-example screenshots were visually inspected: `output/playwright/2026-10-14-echo-scope-desktop.png`, `2026-10-14-echo-incomplete-explanation.png`, `2026-10-14-echo-incomplete-mobile.png`. No model or API completeness rule changed.

## Heart color follow-up

The user relayed that the large vessel beside the aorta should be blue and supplied a school heart diagram. The supplied picture swaps the pulmonary artery/vein labels: the pulmonary trunk/arteries carry oxygen-poor blood to the lungs (conventionally blue), while pulmonary veins return oxygen-rich blood (conventionally red). Checked against [NHLBI blood flow](https://www.nhlbi.nih.gov/health/heart/blood-flow) and [NHLBI anatomy/color convention](https://www.nhlbi.nih.gov/health/heart/anatomy).

The existing `pulmonary_trunk` was incorrectly included in the red-artery color group. It now renders blue in both anatomy and probability modes and remains visible with optional atlas detail disabled. Aorta/coronary arteries stay red; cardiac veins/coronary sinus stay blue; tissue stays pale red. The legend now describes conventional oxygen-rich/oxygen-poor vessel colors and explicitly distinguishes illustration from measured oxygenation. Pulmonary veins are not separately mapped in the current atlas. No geometry, target mapping, model, prediction or clinical claim changed.

Verification: all three focused `HeartViewer.test.tsx` tests passed; the final TypeScript/Vite production build passed (existing chunk-size advisory). Real Chrome checked the rebuilt app on the existing local review instance, anatomy/probability modes and atlas detail on/off. Desktop and 390px mobile screenshots were visually inspected; mobile document width was 390px, anatomy ready was true and the browser console had zero errors/warnings. Receipts: `output/playwright/2026-10-14-heart-flow-colors-desktop.png`, `-detail-off.png`, `-probability.png` and `-mobile.png`. This is a color correction and browser check, not anatomical or clinical sign-off.
