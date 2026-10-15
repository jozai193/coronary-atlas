# Coronary Atlas - Devpost draft

Status: saved draft, 4/5 steps. Final submission remains unperformed at the user request.

Demo: https://youtu.be/opyfTMic1kc

## Inspiration
Connecting cardiac predictions with interactive anatomy—became more meaningful through conversations with my cousin, a doctor. Her feedback reinforced that a percentage alone needs context: which coronary vessel does it concern, which observations influenced it, and what can the model actually establish?
That shaped Coronary Atlas: a system that connects clinical inputs, CAD and vessel-specific estimates, interactive 3D anatomy, and understandable explanations. Her review helped improve demonstration cases and the handling of echo findings. I wanted to make the relationship between the data, the prediction and the heart easier to inspect, while keeping the prototype’s limitations visible.

## What it does
Coronary Atlas connects 55 demographic, clinical, ECG, laboratory and echo observations to four model estimates: CAD and the supplied LAD, LCX and RCA labels. Users explore 104 licensed BodyParts3D meshes, focus or isolate a vessel, switch cameras and internal views, inspect explanations, review model evidence and export a case summary.

The workspace has three clear views: Explore for the heart and estimates, Inputs & reports for observations and report review, and Evidence for model evaluation and separate source references. Judges can start their own case, import a CSV or review report text; A/B are optional shortcuts.

Start with profile A or B: both have all 55 recorded inputs and immediately compute four outputs. These contrasting development records were selected by source labels and original row order before scoring. They are demonstrations, not independent tests.

Report-photo OCR runs locally in the browser. Numerical proposals need individual confirmation; unreadable values remain unknown. Echo chamber, valve, flow and impression excerpts require source/case review and do not automatically become coronary labels. A separate library presents 12 real public PTB-XL ECG references, original report strings and annotations. They concern different people and cannot change the active profile. The four-case teaching challenge exposes saved held-out successes and errors.

## How I built it
React, TypeScript, Vite and React Three Fiber/Three.js provide the interface and reference anatomy. FastAPI and Pydantic validate the input contract. Python, pandas, NumPy, scikit-learn and SHAP support preprocessing, nested cross-validation and explanations. Tesseract.js supplies local OCR. Baseline explanations reconstruct raw model outputs; a later consistency adjustment to displayed probabilities is disclosed separately. Optional research variants identify their methods and limitations.

The source dataset contains 303 records. All four outcomes are excluded from the 55 inputs. Preprocessing is fitted within training folds. Code, models, provenance, protocols and negative results accompany the public repository. No paid inference API or dedicated GPU is required.

## Challenges
Connecting the prediction pipeline to the interactive heart was a major challenge. The LAD, LCX and RCA outputs needed to stay consistent across vessel selection, probability colours, explanations and case summaries.
Handling incomplete inputs and report text was another difficulty. Doctor feedback exposed gaps in the demonstration cases and confusing vessel colours. I replaced the incomplete cases with complete recorded examples and added explicit review of proposed report values. The supplied echo image was too degraded for reliable automatic extraction, so uncertain measurements had to remain unknown.
I also needed to distinguish raw model outputs from the later consistency adjustment, so the explanations accurately described what the model calculated.

## Accomplishments
I’m proud of bringing clinical inputs, four model estimates and an interactive 3D heart together in one working application. Users can explore the coronary arteries, inspect the observations behind an estimate and review a case summary.
I also turned my cousin’s feedback as a doctor into concrete improvements: clearer vessel colours, complete demonstration cases and better presentation of echo findings. Report-text assistance and a separate public ECG library added more ways to inspect information while keeping source findings distinct from predictions.
Finally, I deployed the complete application so judges can explore it directly without passwords or setup. The result is a working prototype that makes both the model’s reasoning and its limitations visible.

## What I learned
The original raw-model nested out-of-fold AUCs were CAD 0.920, LAD 0.831, LCX 0.741 and RCA 0.717. At the fixed 0.5 cutoff, LCX/RCA sensitivity was only about 40%; that weakness remains visible. These results do not validate the later display adjustment or research variants. Separate reduced-input transport studies include encouraging and poor results but do not externally validate the full 55-input app. Chosen examples and attractive graphics cannot establish clinical accuracy.

## What is next
Independent validation on a genuinely unused compatible cohort, broader OCR tests across real report layouts, clinical coding/timing review, and observed learner/educator usability studies. Measured narrowing needs appropriate angiographic evidence. Current outputs are educational disease-label estimates, not diagnoses, future-event risks, lesion maps or percentages of narrowing.

## AI assistance and credits
OpenAI Codex / ChatGPT assisted research, analysis, implementation, tests, documentation and demo preparation. Deepgram Aura 2 Orion generated stock synthetic narration; no clinician voice was cloned. I remain responsible for reviewing and presenting the work. Code is MIT. BodyParts3D anatomy and attributed UCI/PTB-XL resources retain source-specific CC BY 4.0 credits in the repository.

## Judge links
[Source, setup and judge walkthrough](https://github.com/jozai193/coronary-atlas) · [Six-page technical report](https://github.com/jozai193/coronary-atlas/blob/codex/submission-ready/output/pdf/technical_report.pdf)

The complete application runs on Railway independently of my laptop. Judges need no password, account or API key. Anonymous A/B predictions passed for all three model variants, together with desktop/mobile, source-review, local OCR and export checks. Availability depends on the hosting account’s remaining credits/plan.
