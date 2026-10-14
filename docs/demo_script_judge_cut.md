# Judge demo script — 4:35 target

This is a **recording plan**, not a recorded or validated video. Rehearse against the final build, read live numbers from the screen, and keep the finished video within the official 3–10 minute limit. Use only synthetic inputs in the live workspace. The [Track A brief](https://drive.google.com/file/d/1T9Whog4kWF3mYB7ZMGyihGWpbJBJtsfz/view) scores prediction 30%, 3D visualization 25%, interpretability 20%, integration 15%, and technical implementation 10%.

## 0:00–0:55 — Start with the model's miss

**Screen:** Open **Try four cases** → **Case D** → **LCX**. Guess **Yes**, then reveal. Keep the saved result and label legible.

**Say:** “This is where our model failed. On an original-cohort row held out of its training fold, the saved raw LCX estimate was **23.2%**. At the fixed 0.5 cutoff it said negative, but the dataset's LCX label is positive. These four teaching cases were deliberately chosen to show successes and errors. They are not a random accuracy sample, and their four visible observation bands cannot explain a 55-input model.”

## 0:55–1:35 — Connect the error to anatomy without inventing a lesion

**Screen:** Click **Inspect LCX on reference heart**. Show the LCX label; rotate briefly, use **Focus LCX** if needed, then **Isolate LCX**. Point to **HELD-OUT CASE · REFERENCE VIEW** and **Return to live workspace**.

**Say:** “LCX curves toward the back of this licensed reference heart. The jump deliberately hides live-profile estimates. It does **not** color this artery with the saved fold probability, and it does not locate this patient's plaque. This is a vessel-level error connected to reference anatomy.”

## 1:35–2:35 — Show the working prediction and an honest explanation

**Screen:** Click **Return to live workspace**, then **Explore profile A**. Wait for **Prediction ready**. Read the displayed CAD and vessel values from the running app; select one named vessel, rotate or zoom, and show its explanation. Open **Probability adjustment** and the **Raw model → displayed** line.

**Say:** “Profile A is synthetic: it tests the live 55-input pipeline, with no known diagnosis. ECG and echo are tabular findings here; we have no raw waveform, scan image or lesion coordinates. The backend returns four predictions and SHAP contributions; the 3D color follows each **displayed** vessel probability. SHAP reconstructs that target's **raw model output**. A separate consistency rule may change the displayed probability so overall CAD is at least as high as each vessel. When the two values match, no adjustment was needed. These factors show how the model used the observations; they are not disease causes or treatment effects.”

**Recording cue:** If the chosen profile has a nonzero adjustment, show its exact raw and displayed values. If it does not, show **No adjustment needed for this profile** and keep the same distinction in narration. Do not attach this live SHAP explanation to Case D's saved outer-fold estimate.

## 2:35–3:10 — Give the predictive score its denominator

**Screen:** Open **Validation & model details**; pause on the four target metrics and confusion counts.

**Say:** “On 303 source patients, nested held-out AUCs for the raw modeling procedure were CAD **.920**, LAD **.831**, LCX **.741**, and RCA **.717**. At the fixed cutoff, LCX and RCA each detected only about **40%** of positives. A low vessel estimate therefore cannot rule out disease. AUC measures ranking, not diagnostic safety.”

## 3:10–4:10 — Show the new population, naming the different model

**Screen:** Scroll to **What happened at another center?** in the same Model evidence panel. Keep its **Separate 13-input model** badge and primary table visible. The [six-page technical report](../output/pdf/technical_report.pdf) and [external results](angiocad_external_results.md) provide supporting detail if asked.

**Say:** “We then froze a **separate 13-input logistic model** trained only on the original source cohort and tested it at another invasive-angiography center. AngioCAD external AUCs were CAD **.781**, LAD **.723**, LCX **.709**, and RCA **.687**. At 0.5 it missed **54 of 90** LCX positives and **106 of 155** RCA positives. This is a useful transport stress test, but it is **not external validation of the served 55-input app**. Inputs and endpoint derivation differ, so the two AUC sets cannot be compared as a pure population effect.”

## 4:10–4:35 — Close on what is reproducible and what remains open

**Screen:** Show the disclaimer, README and frozen external protocol/verifier. End on the product with the reference heart in view.

**Say:** “Coronary Atlas is an educational research prototype: a reproducible way to inspect predictions, coronary anatomy, model errors and their limits. The source, weights, evaluation artifacts and frozen external test are documented. We have **not** established clinical readiness, patient-specific lesion localization, or measured learning benefit. Those need matched external validation and observed user and clinical review.”

Before publishing, verify the exact final build, visible source attribution, legible numbers, English narration or subtitles, public repository and video links, and required AI-tool disclosure. Record the actual duration; cut pauses before removing the failure and model-boundary statements.
