# Optional later learner comparison — ready to run, not yet conducted

The feasible pre-submission human check is one doctor or coronary reviewer using the [15-minute review packet](clinical_review_packet.md). That review can catch concrete content and safety defects; it cannot measure learning benefit. The comparison below is an optional later protocol if learners become available, not a release gate for this submission.

Purpose: test the product hypothesis behind the new held-out challenge before claiming that Coronary Atlas teaches coronary anatomy or model uncertainty better than a static explanation. If feasible later, recruit 3–5 medical or ML learners who did not build the app, plus one educator if available. Do not describe convenience feedback as a clinical or randomized effectiveness study. No participants have been recruited or contacted.

## Materials and comparison

Use the exact final production build and its **Try four cases** section. For a simple comparison, prepare a static sheet from existing [technical report pages 2–3](../output/pdf/technical_report.pdf) and [case-method document](heldout_case_mode.md), with the same model result and limitations but no interactive guess/reveal or vessel control. Alternate which material participants see first. Do not use their responses to modify the fixed 303-patient metrics or AngioCAD experiment.

## Tasks to observe, without coaching

1. Locate LAD, LCX and RCA on the reference 3D heart; state whether a colored vessel gives lesion location.
2. Use Case D and explain what its ~30.4% **raw outer-fold CAD probability**, positive dataset label and 0.5 cutoff mean. Ask whether this negative model decision rules out disease. Then switch that case to LCX (also a saved false negative), find LCX on the reference heart without coaching, and ask whether the heart displays that case's fold probability. Record the navigation steps and any confusion caused by the challenge and viewer being separate.
3. Use a synthetic live profile and state what the SHAP contribution explains and what the separate coherence adjustment changes. Ask whether Case D's fold output has a displayed SHAP explanation.
4. Read the AngioCAD result summary and say whether the .781 CAD AUC validates the current 55-input app. Ask which extra differences matter besides hospital location.

Record each participant's initial answer, corrected answer after the material, time to completion, points of confusion, and exact wording that misled them. Rate each concept as correct, partly correct or incorrect against the answer key below. Record if they would use the lesson in a named class/workflow, what material they currently use, and why they would switch. Do not record names, medical histories or identifiable recordings without informed agreement.

## Answer key and decision rule

- The meshes are shared anatomy; whole-vessel color is a model estimate, not a patient's lesion site or percent narrowing.
- Case D is a deliberately selected original-cohort false negative. Its probability came from an outer-fold model that did not fit on that row; it is not a clinical rule-out or an estimate of the challenge set's accuracy.
- Live SHAP reconstructs the **raw final fitted-model output**, not the coherence-adjusted display, not a disease cause, and not Case D's different outer-fold model.
- AngioCAD tested a separately trained 13-input model with coarsened derived labels and a different selected catheterization population. It does not validate the 55-input app or prove clinical utility.

**Keep the teaching direction** only if most observed learners correctly explain the false negative and reference anatomy without coaching, and at least one educator or learner names a recurring use and a concrete advantage over their current material. If people repeatedly misread probability as stenosis percentage, treat the UI wording as defective and repair it before a benefit claim. If they find a static sheet equally clear and faster, keep the app as a research visualization demo rather than claiming a teaching advantage. With 3–5 convenience participants, report individual observations and counts, not a statistical improvement percentage.

For a separate qualified clinical/anatomy review, ask a cardiologist or coronary educator to inspect the source input timing/units, the 13-field AngioCAD mapping and 26–50% bin handling, LAD/LCX/RCA mesh mapping, and the distinction among measured stenosis, model probability and reference geometry. Record disagreements and corrections; no sign-off exists until that happens.

### If only one doctor/coronary reviewer is available

Use the focused [15-minute review packet](clinical_review_packet.md). Ask the reviewer to perform the anatomy and case-interpretation tasks cold, then check feature definitions and endpoint mapping. Record concrete defects and corrected wording. One expert's observations can repair the prototype, but cannot substitute for the 3–5 learner comparison or establish learning improvement, clinical performance or general acceptance. Do not report a study percentage from one person.
