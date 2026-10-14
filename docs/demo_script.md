# Judge demo script — target 7 minutes 30 seconds

Preparation only: no video has been recorded or uploaded. Record the final production build at a legible desktop resolution. The official submission requires a 3–10-minute YouTube video, public or unlisted, with English narration or subtitles. Rehearse and read the live UI values; timings below are targets, not a completed recording.

## 0:00–0:35 — One problem, one task

“A good coronary model demo should show a mistake, not just a high score. Coronary Atlas lets a learner connect a saved held-out model decision, its real label, and the relevant reference vessel. The live predictor is an educational research prototype. It is not a diagnosis or a lesion map.”

Show the dashboard, disclaimer and the **Try four cases** button. Do not imply that the study measured learner benefit.

## 0:35–1:45 — Challenge on a real held-out error

Open **Try four cases**, choose **Case D**, target **CAD** and guess. The saved outer-fold probability should be about **30.4%** for a source row whose CAD label is positive; verify the exact current UI value before narration. “This is a false negative at the fixed 0.5 cutoff. The case was excluded from the model-fitting fold, and its outcome came from the original 303-record dataset.” Switch the same case to **LCX** if time permits: its separately held-out raw estimate is about **23.2%** despite a positive LCX label. Later, locate LCX on the reference heart, explicitly saying that the live heart color does not display this case's fold probability. Case C supplies a CAD false alarm if more time remains.

Point to the case footer: the four cases were **deliberately selected** to show one CAD TP, TN, FP and FN. They are not a random accuracy sample or independent population. Only coarse observations are exposed; they cannot explain the 55-input output. No final-model SHAP or coherence adjustment is attached to these fold predictions.

## 1:45–2:30 — What was trained

“The original UCI extension has 303 records, 55 input observations and four angiographic labels. ECG and echo findings are tabular here; no raw ECG, imaging or lesion coordinates are present. All four labels are excluded from predictors. Five outer folds give held-out results; three inner folds choose the model family, with preprocessing fitted inside training folds.”

Show the data audit, one fold artifact and the actual model evidence. Mention the single retained source-label inconsistency if asked. Do not call the original cohort multimodal imaging data.

## 2:30–3:25 — Live synthetic pipeline and reference anatomy

Load **synthetic Profile A**, generate the live response, and read the actual displayed values. Rotate/zoom the licensed BodyParts3D heart, select a coronary vessel, isolate it and reset. “This is shared reference geometry. A colored whole vessel reflects a dataset-label probability; it does not locate plaque or show measured narrowing.” Show the raw versus displayed probability card if the baseline consistency adjustment is active.

The synthetic profile demonstrates integration and UI behavior; it has no angiographic ground truth. Editing inputs clears old results until inference runs again.

## 3:25–4:15 — Explain only the model output that SHAP reconstructs

Select LAD or LCX and open its contribution table. “These signed factors reconstruct the fitted model's **raw** prediction, in probability units for a forest and log-odds for logistic regression. They are associations within this model, not causes of disease. The separate CAD–vessel consistency adjustment can change the displayed number, and these SHAP values do not explain that adjustment.” Show actual measurements and the raw-to-displayed delta; do not suggest this explanation belongs to Case D's outer-fold model.

## 4:15–5:10 — Quantify the weakness

Open **Validation & model details**. “The original nested held-out AUCs were CAD .920, LAD .831, LCX .741, RCA .717. At a fixed .5 cutoff, LCX and RCA detected only about 40% of positives. These are selected single-cohort results for the original raw-model procedure; the default displayed coherence adjustment had only a tiny pilot-informed same-cohort Brier gain.” Show confusion counts and probability calibration. A low vessel probability cannot rule out stenosis. AUC is discrimination, not accuracy or clinical utility.

## 5:10–6:20 — A new hospital and an honest boundary

Show page 6 of the six-page technical report and the [AngioCAD result](angiocad_external_results.md). “We found an open, independent-center invasive-angiography cohort: 413 labeled patients, with usable clinical fields for 377. Only **13** inputs could be mapped confidently, so we froze a **separate 13-input source-trained model** before scoring. Its external AUCs were CAD .781, LAD .723, LCX .709 and RCA .687. It still missed 54 of 90 LCX positives and 106 of 155 RCA positives at .5.” The 26–50% stenosis bin was excluded when it made a target ambiguous. This test does **not** validate the 55-input app.

“A separate four-input test on CONFIRM CCTA records had CAD AUC .656 and severe overprediction. We preserved that failure. Later CONFIRM-trained development models were evaluated on already inspected data, so their better numbers are not fresh external proof.” Do not compare .920 to .781 as an isolated population effect; the models and endpoints differ.

## 6:20–7:05 — Reproducibility and attribution

Show README setup commands, saved OOF predictions, model hashes, the AngioCAD frozen manifest/verifier and BodyParts3D attribution. “The app runs locally on CPU without a paid inference API. The 9 October regression pass has 74 Python tests passing with one optional skip, 22 frontend tests passing, and a production build. Independent read-only verifiers reproduced the new cohort and internal missingness-stress metrics from saved predictions.” Keep the screen on the six-page report briefly; do not claim a public release until its URL is live and verified.

## 7:05–7:30 — Close on the actual promise

“Our strongest claim is a reproducible teaching and research lab where you can inspect a coronary model's output, anatomy, errors and transport limits. We still need a qualified input/anatomy review and an observed learner comparison before claiming educational benefit. The full app needs a matched external cohort before any clinical accuracy claim.” State that OpenAI Codex assisted the work and is disclosed in README and Devpost Built With.

Before upload, verify actual duration, English audio/subtitles, public GitHub URL, license credits, no local paths or personal data shown, real-name team roster, eligibility and one-track constraint. The [official submission guidelines](https://drive.google.com/file/d/1HEy6MBO_BN_aID2Nik2woYLWfuawzwHN/view) govern the final deliverable. Do not publish claims stronger than the exact tested build.
