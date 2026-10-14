# Coronary Atlas — final narrated demo

Voice: Deepgram Aura 2 Orion, matching the configured Jarvis voice and the saved NextStep Orion demo. Synthetic narration; no voice cloning. Each numbered section is a separate audio segment.

## 01 — The problem

A cardiac prediction is difficult to understand when it is just a percentage in a table. Coronary Atlas connects clinical observations, four model estimates, and an interactive three dimensional reference heart. Built for Track A of the Multimodal AI Hackathon, it helps a learner inspect what the model received, where the named coronary arteries run, and which observations influenced the estimate. This is an educational research prototype, not a diagnostic system.

## 02 — Complete source cases

The judge can start immediately with profile A or profile B. Both contain all fifty five recorded model inputs, including ECG findings, echo ejection fraction and a valve assessment. A and B are contrasting public development records, selected by their recorded labels and original row order before scoring. They are deliberately chosen demonstrations, not independent tests. Selecting either computes four real outputs. The source labels remain separate from the model inputs and predictions. Original ECG and echo reports for these records are unavailable.

## 03 — Explore the heart

The heart uses licensed BodyParts3D anatomy. Rotate and zoom the model, choose a camera preset, or focus on the left anterior descending, circumflex and right coronary arteries. Vessel buttons provide an alternative to clicking a small structure. You can isolate a vessel or inspect internal anatomy. Probability mode colours the three named arteries using the displayed estimates. This is shared reference anatomy. A coloured vessel does not identify a plaque, a lesion location, or an actual percentage of narrowing. The anatomical colour legend is separate from the probability legend.

## 04 — Understand the estimate

The explanation panel shows the observations that raise or lower each raw model output. For the baseline, these are SHAP contributions, with their actual input values and units. Click a measurement to locate it in the form. The app also discloses its consistency adjustment: displayed coronary disease probability is kept at least as high as each vessel estimate. SHAP reconstructs the raw output, not that later adjustment. The optional research models are labelled separately and identify their own explanation methods. An association in an explanation is not a treatment recommendation.

## 05 — Check the evidence

The model evidence panel exposes performance, missed positive cases, false alarms and cutoff trade offs. The original dataset has three hundred and three records. Four coronary outcome columns are excluded from all fifty five inputs. Internal cross validation and later development experiments are reported with their limitations. Separate reduced input transport studies do not externally validate this full application. The four case challenge includes model successes and errors using saved held out probabilities. Selected examples, repeated splits and attractive screenshots cannot establish clinical accuracy.

## 06 — Reports and echo review

Report-photo assistance reads printed English text locally in the browser. It does not interpret ECG waveforms or echo scans. Every numerical proposal needs confirmation. Reference ranges, ambiguous values and conflicting occurrences require checking. Echo text can be reviewed as chamber, valve, flow and impression excerpts, then explicitly copied into source notes for the same case. The doctor supplied a partly completed template. Its photo was too degraded for reliable automatic EF extraction, so the app abstains. Corrected text checks preserve both the aortic root finding and the broad impression for review, without inventing measurements.

## 07 — Real ECG references

A separate reference library contains twelve real public PTB ECG records, with calibrated twelve lead excerpts, original report strings and source annotations. These belong to different people from the current case. Switching a reference cannot populate the patient form or change a coronary prediction. We verified the selected source files against provider checksums. This adds inspectable reference material, not paired patient evidence or an independently validated ECG interpreter.

## 08 — Review and implementation

The case summary brings entered observations, missing values, model outputs and separately recorded report evidence together. Download a worksheet or research result for review. Editing inputs clears stale predictions, and loading a different case clears report context and pending OCR. The implementation connects React, TypeScript and Three.js to a FastAPI backend with saved scikit learn models. Report images stay in browser memory. OpenAI Codex assisted research, implementation, testing and documentation; Deepgram supplies this synthetic narration. The source repository includes setup instructions, model artifacts and evidence.

## 09 — What judges should try

Try A and B, focus all three arteries, inspect the explanation and evidence, then open the case summary. You can also try report text and the separate ECG references. The app keeps probabilities, source findings and measured narrowing distinct. Independent clinical validation, complete original reports and suitable lifestyle outcome data remain future work. Coronary Atlas makes the model and its limits inspectable, while giving judges a working integrated system to explore.
