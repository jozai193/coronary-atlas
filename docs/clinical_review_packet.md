# Coronary Atlas: 15-minute coronary expert review

**Status:** partial informal doctor feedback has now been relayed by the user; see [13 October notes](doctor_feedback_2026-10-13.md). Specialty, completed scope and revised-screen review remain unconfirmed. No completed sign-off or clinical validation is recorded. This packet remains available for the focused content and safety check. Do not enter identifiable patient information.

## Send before the call

- [Working prototype and setup](../README.md) or the authenticated temporary review link. Select **Start clinician review**, then **Review profile R1 inputs** for all 55 recorded model inputs. C/D demonstrate the incomplete-input block. This loads observations without running a prediction; no typing is required.
- Use **Open case summary** or **View case summary** for important findings, four estimates, origins and unknowns. Download the current worksheet from there. R1 is a public development-dataset row with 55 supplied inputs and separately labeled reference outcomes, not an independent test or a complete echo report. C/D are incomplete synthetic cases (45 supplied, 10 unknown); required missing fields block prediction. Historical A/B worksheets remain for reproducibility.
- Try **Import a report photo · assisted autofill** using a public specimen page or pasted text. Confirm each proposal. New-case mode clears unselected inputs. Ask whether this review step and supported units are clear; do not treat OCR as waveform interpretation. [Feature and public-test notes](report_autofill_and_summary.md).
- [Six-page technical report](../output/pdf/technical_report.pdf), especially the 3D mapping and new-population sections.
- [Original source-field audit](dataset_analysis.md) and [13-field AngioCAD mapping](angiocad_external_protocol.md). The original field unit/code dictionary and measurement timing remain incomplete.

## During the call

Start with the case overview and **Inspect ECG / echo inputs**. Ask her to identify the exact field and correction, or say that the available information is insufficient. Then inspect the 3D heart, including **Inside heart**. Only after checking the observations, use **Generate prediction** and inspect its meaning. C/D have ten unknown inputs; their missing ECG and valve observations block prediction and remain dashes. Use recorded R1 for the complete-input demonstration. The three source echo fields do not capture Doppler flow patterns or detailed valve narrowing/leakage; all 55 model inputs being supplied does not constitute a full echo report. CAD probability is distinct from EF, valve category and measured stenosis. See the [14 October relayed feedback](doctor_feedback_2026-10-14.md).

The review guide contains an A/B difference table and **Review actual tabular source records**. Those optional sheets reproduce the first two consecutive UCI records, all 55 values and four supplied labels, with attribution. They are development records, have no original ECG/echo images, and are not new accuracy evidence. Use them for source-field questions; do not infer missing clinical narrative or unverified code definitions.

Download a fresh worksheet after any edits. Editing clears prior results; a draft worksheet contains no previous prediction. Record the reviewer role, exact screen inspected and unresolved questions. The app does not collect or transmit review feedback.

For a 15-minute call, allow two minutes for anatomy, three each for number meaning, input definitions and new-cohort mapping, two for the error lesson, and two for exact corrections. Let the reviewer say **unknown**. Record their actual words, the screen or field they refer to, and whether a claim should be withdrawn; do not translate uncertainty into approval.

| Check | Show and ask | A result that requires action |
|---|---|---|
| **1. Anatomy** | Rotate front/back views, select and isolate LAD, LCX and RCA. “Do these labels, vessel paths and orientation look correct for a reference teaching heart? Is any contextual branch misleading?” | Wrong vessel mapping, implausible orientation or a label that suggests a specific lesion. Fix or remove the claim and recheck the exact render. |
| **2. Number meaning** | Show a synthetic live result, legend, disclaimer and raw-to-displayed note. “Could a learner or clinician read the color as plaque location or the probability as percent narrowing? Is the CAD/stenosis wording accurate?” | Any plausible diagnostic or lesion-location misreading. Change nearby UI wording; a footer disclaimer alone is insufficient. |
| **3. Input contract** | Show Age, BP, FBS, CR, WBC, PLT, EF-TTE, Region RWMA and symptom/history controls. “Which units, categories, or timing relative to angiography can you verify from these sources, and which remain unknown?” | Unsupported unit expansion, ambiguous code or post-test observation presented as pre-test. Document the uncertainty or restrict that claim; do not infer a codebook from typical clinical practice. |
| **4. New cohort** | Show the [AngioCAD result](angiocad_external_results.md): separate 13-input source-only model, 26–50% ambiguous bin excluded, LCX 54/90 and RCA 106/155 positives missed at .5. “Does the endpoint mapping seem clinically defensible as a sensitivity test? What difference prevents it from validating the 55-input app?” | A major mapping disagreement or missing qualifier. Preserve the frozen numerical result as a historical experiment but revise the interpretation and presentation. |
| **5. Error lesson** | Reveal Case D CAD (~30.4% raw outer-fold probability, supplied positive label), then Case D LCX (~23.2%, also positive). “Would you trust a negative decision here? Is it clear that these are selected original-cohort fold outputs, separate from live heart colors and SHAP?” | Any impression that a negative rules out disease or that the 3D heart shows this patient's lesion or fold estimate. Repair the teaching flow and retest it. |

## Record the outcome without inflating it

| Field | Actual notes after review |
|---|---|
| Date, duration, reviewer role and relevant experience (no unnecessary personal details) | Pending |
| What they personally inspected (screens/files) | Pending |
| Anatomy findings and exact corrections | Pending |
| Field coding/timing verified, unresolved or disputed | Pending |
| Case/probability misunderstandings | Pending |
| Existing teaching material and whether this would replace a named task | Pending |
| Actions taken and exact build rechecked afterward | Pending |

One reviewer can identify defects and improve wording. One positive review cannot establish anatomical completeness, model accuracy, safety, fairness, learning improvement or demand. Keep the response as feedback until corrections are made and the revised screen is shown back to the reviewer where feasible.
