# Coronary Atlas — concise demo

Voice: Deepgram Aura 2 Orion. Fresh narration for the shorter cut. English captions accompany the narration. No track or submission instructions are spoken.

## 01 — See what a prediction means

What does a cardiac prediction actually mean? Coronary Atlas connects the inputs, the estimate, and the heart, so a learner can explore the result instead of staring at a percentage. Let me show you.

## 02 — Start with a complete case

One click loads profile A and runs four model outputs: coronary disease, and the three main coronary arteries. All fifty five recorded inputs are present. Now switch to profile B. The observations and estimates change together. These are contrasting public development records, not independent validation cases. Their original ECG and echo reports are unavailable, and recorded outcome labels stay outside the prediction inputs.

## 03 — Explore the heart

The interactive heart makes those artery names tangible. Focus the left anterior descending artery, look inside the heart, then select the circumflex artery and isolate it. Return to the surface and follow the right coronary artery. You can rotate, zoom, or use the camera buttons. Anatomy colours and probability shading have separate legends. This is shared reference anatomy: the colours show model estimates, not a patient's plaque location or measured percentage of narrowing.

## 04 — Ask why

Next, open the prediction explanation. The chart shows which entered observations push the raw estimate up or down, alongside their values and units. Selecting a factor takes you back to its input. The baseline uses SHAP, and the app separately explains any consistency adjustment applied to the displayed probabilities. That makes the result traceable without treating an association as medical advice.

## 05 — Review report text

Report assistance reduces typing while keeping the person in control. Here I'm using example echo text to demonstrate the review flow. The app separates chamber, valve, flow and impression excerpts, and proposes numerical values for confirmation. Blank measurements remain blank. A proposal only enters the form after explicit review. Printed report photos can also be read locally in the browser. This reads text; it does not interpret echo scans or ECG waveforms, and the example is not evidence for profile B.

## 06 — Inspect real ECG references

The separate ECG library offers twelve real public records with calibrated twelve lead excerpts, source annotations and original report text. Switch between records to inspect the trace and its source. These references belong to different people and never change the active case or its prediction.

## 07 — Check the model's limits

The evidence panel shows performance, missed positive cases, false alarms and cutoff trade offs. It also includes held out examples where the model succeeds and where it makes mistakes. The source dataset contains three hundred and three records. Internal evaluation is visible, but independent clinical validation of this full application remains outstanding. The evidence stays available alongside the attractive visualisation.

## 08 — Take the case away

Finally, the case summary brings the entered observations and model outputs together, with report evidence kept separate. Download the worksheet or research result for review. Editing an input clears stale predictions. Try profiles A and B, explore an artery, and ask why the estimate changed. Coronary Atlas makes the model inspectable. It is an educational research prototype, not a diagnostic system.
