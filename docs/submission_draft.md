# Devpost draft - not submitted

## Title

Coronary Atlas

## Tagline

See when coronary AI is wrong: held-out errors, reference anatomy and transport evidence.

## What it does

Coronary Atlas accepts tabular demographic, clinical, ECG, laboratory and echocardiographic observations. Four models estimate the supplied CAD and LAD/LCX/RCA stenosis labels. For the default baseline, a disclosed consistency step can adjust displayed probabilities so overall CAD is no lower than any vessel estimate. The interface links displayed values to licensed reference anatomy and evidence, while signed SHAP contributions explain each unadjusted model output.

Users can try four deliberately selected original-cohort teaching cases: guess a CAD or vessel label, then reveal its saved raw outer-fold probability and actual supplied label. This challenge is separate from live inference; no full-data SHAP explanation is assigned to a fold prediction. Users can also enter observations manually, load a clearly labeled synthetic profile or import one CSV row. They can rotate and select arteries, compare live-model explanations, inspect calibration/error counts and export a research result. Old results clear as soon as inputs change.

## How we built it

Python, scikit-learn and SHAP provide fold-local preprocessing, nested cross-validation and model explanations. FastAPI validates requests and serves the production React/TypeScript/Vite dashboard. React Three Fiber/Three.js renders 56 BodyParts3D OBJ meshes using explicit FMA mappings. No paid inference API or dedicated GPU is required; the browser needs WebGL support.

## Evidence and limitations

Executed nested out-of-fold AUC for the original raw-model procedure on 303 records: CAD 0.920, LAD 0.831, LCX 0.741 and RCA 0.717. LCX/RCA sensitivity is about 40% at threshold 0.5, a major limitation. A later pilot-informed, same-cohort comparison found that the default consistency projection reduced mean four-target Brier by only 0.001198 across two repeats of those same 303 people. The raw-model AUCs are not adjusted-output validation. We retained and analyzed one inconsistent CAD/vessel label. We do not claim clinical validation, diagnosis, future-event prediction or lesion localization.

We subsequently acquired 27,125 public CONFIRM records and ran a separate shared-input transport experiment. It failed to transfer well: CAD AUC .656 with substantial overprediction. After preserving that result, a separate CONFIRM development model reached AUC .789 and Brier .119 on 1,402 complete-case CAD test patients. Additional-input and calibration gains were measured on matched patients. Missing-input handling expanded eligibility to 14,257 before outcome exclusions. These are separate research models, not the model serving the dashboard, and the later results are internal development evidence on a previously inspected cohort. False alarms remain substantial at high-sensitivity cutoffs. Full protocols, negative results and immutable artifacts accompany the code.

We then found AngioCAD, a new invasive-angiography cohort from another center: 413 patients have segment labels and 377 have clinical features. A fixed **13-input** source-trained logistic model was frozen before external scoring. After prespecified data-quality and ambiguous endpoint exclusions, external AUC was CAD .781 (n=345), LAD .723 (n=322), LCX .709 (n=331) and RCA .687 (n=326). At 0.5, LCX missed 54/90 positives and RCA 106/155. The outcome bins and smaller input set mean this result does **not** validate the dashboard's 55-input predictor. We verified all saved-prediction metrics and retained the mapping and cohort exclusions.

## What we learned

Correct input exclusion is necessary but does not remove every scientific uncertainty. Clinical measurement timing, rare categories and correlated features still matter. A clear visualization must distinguish probability from narrowing percentage and a displayed adjusted value from its raw model output. We tested SHAP reconstruction against the fitted raw output; SHAP does not reconstruct the separately adjusted probability.

## Next steps

Independent anatomical/clinical feature review, authoritative input codes and timing, a genuinely unused **55-input compatible** cohort for the dashboard, and a small observed learner comparison. These are future work, not completed validation. Training-only error and site-code robustness audits are documented separately; they do not make the existing test set independent again.

## Built With

Python; scikit-learn; pandas; NumPy; SHAP; FastAPI; Pydantic; React; TypeScript; Vite; Three.js; React Three Fiber; BodyParts3D; UCI; OpenAI Codex / ChatGPT.

## AI disclosure

OpenAI Codex assisted research, data analysis, architecture, implementation, tests, documentation and local browser verification. The participant remains responsible for reviewing, understanding and presenting the work.

## Attachments to complete

- Public GitHub URL: not published yet.
- YouTube URL: not recorded/uploaded yet; public or unlisted, 3-10 minutes, English audio/subtitles.
- Technical report: output/pdf/technical_report.pdf (rebuilt and visually verified at 6 pages on 9 October).
- Screenshots: output/playwright/heldout-case-desktop.png, heldout-case-mobile.png and existing overview/model/anatomy receipts. The challenge screenshots reflect the latest verified build; inspect all selected final images and exact final UI before submission.
- Team roster: real full names and Devpost accounts to be supplied/verified by the user.
- Eligibility and one-team/one-track compliance: user verification outstanding.

Do not submit placeholders as actual URLs. Final submission has not been authorized or performed by this draft.
