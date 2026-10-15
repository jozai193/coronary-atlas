## Inspiration
For medical learners and educators, a model result such as "LCX: 58.5%" is an incomplete explanation. It does not locate the artery, identify the observations behind the estimate or show how the model can be wrong.

Cardiofolio is an educational workspace for exploring those connections through named coronary anatomy, actual model explanations and visible prediction errors.

**Try it:** [Open the working application](https://coronary-atlas-production.up.railway.app) · [Watch the 3:40 narrated demo](https://youtu.be/opyfTMic1kc). No password, account or API key is required.

Conversations with my cousin, a doctor, shaped the project. Her feedback led to clearer vessel colours, complete demonstration cases and better source review for echo findings. This was advisory feedback, not clinical validation.

## What it does
Heart-disease prediction, SHAP explanations and interactive anatomy already exist. The contribution here is their connection within one educational workflow: follow a vessel estimate to its reference anatomy, inspect what influenced the live model, and separately examine saved held-out successes and failures.

The app estimates the dataset's CAD, LAD, LCX and RCA labels from clinical observations.

**Explore** connects the heart and estimates; **Inputs & reports** collects observations and reviewed report values; **Evidence** exposes evaluation and errors. A/B are complete recorded development examples, and judges can also enter their own de-identified observations. Echo excerpts and separate public ECG references retain their source context.

## A quick way to try it
1. Open the app and choose **Profile B** to generate four estimates.
2. Select **LCX**, locate the circumflex artery on the reference heart and try **Isolate LCX**.
3. Read its prediction explanation. Select an influencing observation to find the entered value behind it.
4. Choose **Try the teaching challenge** (also available under Evidence). In this separate teaching challenge, select **Case D** and **CAD**, make a guess and reveal the saved result: about **30.4%** raw model probability despite a positive source label. At the fixed 0.5 cutoff, the model missed that row.

The task is concrete: identify a vessel, trace an estimate to an observation and explain a model error. The challenge uses separate source cases and fold models; the live profile's explanation does not explain a saved held-out prediction.

## How I built it
React and React Three Fiber display licensed BodyParts3D anatomy. FastAPI validates inputs; scikit-learn and SHAP provide prediction and explanation. Tesseract.js reads printed report text locally, with individual confirmation of proposed values.

The main dataset contains 303 records and 55 model inputs. All four outcome labels are excluded from inputs, and preprocessing is fitted inside training folds. Raw-model explanations remain distinct from the disclosed consistency adjustment to displayed probabilities. Source, protocols, evaluation and negative results accompany the repository.

## Technical achievement
The Track A workflow runs four classifiers from demographic, clinical, ECG, lab and echo observations, maps vessel estimates to selectable 3D anatomy, and connects each live output to its actual-model contributions and entered measurements. A FastAPI backend serves the interactive web app; public source, trained weights and a six-page report make the implementation inspectable.

The 3D work goes beyond displaying a heart asset: 104 licensed BodyParts3D meshes retain source IDs and geometry, with named FMA mappings for LAD, LCX and RCA. Selection, camera focus, vessel isolation, internal reference views, probability shading and the explanation target stay connected. Shared anatomy remains separate from patient imaging; only the three target arteries receive probability shading.

## Evaluation, including the failures
Original baseline raw-model results: 303 source records, five outer test folds, three inner selection folds. These are internal pooled out-of-fold AUCs, before the displayed consistency adjustment.

| Target | ROC-AUC |
| --- | --- |
| CAD | 0.920 |
| LAD | 0.831 |
| LCX | 0.741 |
| RCA | 0.717 |

LCX/RCA sensitivity was only about 40% at the fixed 0.5 cutoff. A low estimate cannot rule out disease. Optional research variants have separate evidence and limitations; these baseline numbers do not validate the full application clinically or establish an educational benefit.

## Challenges
Keeping vessel selection, probability colours, explanations and exports synchronized took careful integration. Incomplete inputs and uncertain report text created another challenge. I replaced incomplete demo profiles with complete recorded examples and added proposal review. The supplied echo image was too degraded for reliable automatic extraction, so uncertain measurements stayed unknown.

Explaining the difference between raw predictions and adjusted display probabilities also required changes to both the interface and exported results.

## Accomplishments
I brought clinical observations, four model estimates, named coronary anatomy and actual-model explanations together in a deployed application. A learner can follow a number to a vessel and an input value, then inspect examples where a model makes mistakes.

I also turned my cousin's feedback into clearer vessel colours, complete demonstration cases and better source review for echo findings. Judges can explore the full application, enter their own observations and export a case summary without passwords or setup.

## What I learned
A strong model metric does not establish an educational benefit. The original internal nested evaluation achieved CAD AUC 0.920, while LCX/RCA sensitivity was only about 40% at the fixed 0.5 cutoff. Both strengths and failures need to be visible.

The working task is demonstrable, but no learner study or measured learning improvement has been completed. The full 55-input application also remains without independent clinical validation. Its shared reference anatomy and model probabilities do not locate lesions, measure narrowing or provide a diagnosis.

## What is next
Observe medical learners and educators completing the task above; record completion, time, interpretation errors and the resources they currently use. Compare approaches before claiming improved understanding or classroom value. Broader report-layout testing, compatible independent-cohort validation and clinical coding review are also needed.

## AI assistance and credits
OpenAI Codex / ChatGPT assisted research, engineering, testing and documentation. Deepgram Aura 2 Orion supplied stock synthetic narration; no clinician voice was cloned. Code is MIT; BodyParts3D and attributed UCI/PTB-XL resources retain source-specific CC BY 4.0 credits.

## Source and report
[Public repository, setup and judge walkthrough](https://github.com/jozai193/coronary-atlas) · [Six-page technical report](https://github.com/jozai193/coronary-atlas/blob/codex/submission-ready/output/pdf/technical_report.pdf).

The complete application runs on Railway independently of my laptop. Availability depends on the hosting account's remaining credits or plan.
