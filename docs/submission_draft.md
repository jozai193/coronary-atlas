# Coronary Atlas — Devpost submission draft

Status: solo registration confirmed; Devpost draft saved through 4/5 steps on 14 October 2026. Final submission has not been authorized or performed. Track A. The official event page currently lists 15 October 2026, 12:15 PM IST.

## Project name
Coronary Atlas

## Elevator pitch
See the heart. Understand the estimate. Explore coronary AI through reference anatomy, source-reviewed observations and transparent model evidence.

## Inspiration
A probability in a table is hard to explain. A colourful heart can be even more misleading if it suggests that a model has found a blockage. I wanted a learner to move between the observations, the named arteries and the evidence, while seeing clearly what the model can and cannot establish. Doctor feedback helped identify confusing vessel colours, incomplete demo cases and the need to review echo findings in their original context. This feedback was advisory, not clinical validation.

## What it does
Coronary Atlas connects 55 demographic, clinical, ECG, laboratory and echo observations to four estimates: overall CAD and the supplied LAD, LCX and RCA labels. Users explore 104 licensed BodyParts3D meshes, focus or isolate an artery, switch camera and internal views, inspect explanations, compare model evidence and export a case summary.

Judges can start with profile A or B without passwords, API keys or accounts. Both contain all 55 recorded source inputs. They were chosen by contrasting source labels and original row order before model scoring. They are development examples, not independent evaluation. The incomplete C/D choices have been removed.

Report-photo OCR runs locally in the browser. It proposes readable observations for individual confirmation and keeps unreadable measurements unknown. Echo chamber, valve, flow and impression excerpts require source/case review; they do not automatically become coronary labels. A separate library presents 12 real public PTB-XL ECG references with original report strings and annotations. These are different people and cannot alter the active profile. A four-case teaching challenge exposes saved held-out successes and errors.

## How I built it
React, TypeScript, Vite and React Three Fiber/Three.js provide the interface and reference anatomy. FastAPI and Pydantic validate the exact input contract. Python, pandas, NumPy, scikit-learn and SHAP support preprocessing, nested cross-validation and explanations. Tesseract.js supplies browser OCR. The default baseline exposes SHAP for raw outputs and discloses a later consistency adjustment to displayed probabilities. Optional research variants identify their own methods and limits. No paid inference API or dedicated GPU is required to use the application.

The public dataset contains 303 records. All four outcome columns are excluded from the 55 inputs. Fold-local preprocessing and training avoid fitting transformations on test folds. The code, models, sources, protocols and negative results accompany the project. The hosted runtime is downloaded from a tagged public release with a SHA-256 integrity check.

## Challenges
The dataset has no original ECG/echo reports or measured artery narrowing percentages for these cases. I therefore kept tabular source labels, reviewed report evidence and predictions separate. Ordinary echo flow or valve findings cannot justify forcing a coronary prediction to agree with the report. Alcohol and other new lifestyle notes remain context because compatible training evidence is missing. The supplied echo image was too uncertain for reliable automatic EF extraction; the app abstains rather than substituting a reference range.

## Accomplishments
The result is an inspectable end-to-end prototype with complete judge cases, interactive coronary anatomy, explanations, local report review, a separate real ECG library and visible failure evidence. The final application passed 154 Python tests, 77 frontend tests and a production build. A standalone packaged runtime passed real prediction checks. These are engineering checks, not clinical accuracy or independent OCR validation.

## What I learned
The original raw-model nested out-of-fold AUCs were CAD 0.920, LAD 0.831, LCX 0.741 and RCA 0.717. At the fixed 0.5 threshold, LCX/RCA sensitivity was only about 40%. This weakness remains visible. Those results do not validate the later displayed adjustment or research variants. Separate reduced-input transport studies have both encouraging and poor results, but do not externally validate this 55-input dashboard. Selected demonstrations, repeated development experiments and compelling graphics cannot replace independent validation.

## What is next
Independent validation on a compatible, genuinely unused cohort; broader OCR testing on varied real report layouts; authoritative clinical coding/timing review; and observed learner/educator usability studies. Measured stenosis requires appropriate angiographic evidence. The current output is an educational disease-label estimate, not diagnosis, future-event risk, a lesion map or a percentage of narrowing.

## Built with
Python, pandas, NumPy, scikit-learn, SHAP, CatBoost, FastAPI, Pydantic, React, TypeScript, Vite, Three.js, React Three Fiber, Tesseract.js, BodyParts3D, UCI, PTB-XL, Hugging Face Spaces, Gradio, uv, OpenAI Codex / ChatGPT, Deepgram Aura 2 Orion, FFmpeg.

## AI tools disclosure
OpenAI Codex / ChatGPT assisted research, analysis, implementation, testing, documentation and demo preparation. Deepgram Aura 2 Orion generated the demo narration using the same stock voice configured in Jarvis and used for the previous NextStep demo. It is synthetic narration, not a cloned clinician voice. AI assistance is disclosed; I remain responsible for reviewing, understanding and presenting the work.

## Links and assets
- Source and setup: https://github.com/jozai193/coronary-atlas
- Public app: https://coronary-atlas-production.up.railway.app — anonymous API and desktop/mobile browser checks passed. Railway-hosted backend runs independently of the entrant's laptop; availability depends on account credits/plan. Stable static portal: https://huggingface.co/spaces/jozai182/coronary-atlas
- YouTube demo: https://youtu.be/93zRA3R-Mdo — unlisted, published and anonymous oEmbed verified; English synthetic narration and burned captions; local duration 357.24 seconds (YouTube rounds up to 5:58).
- Technical report: output/pdf/technical_report.pdf — 6 pages, rendered and visually reviewed 14 October
- Judge guide: docs/judge_guide.md
- Gallery: output/playwright/submission-overview.png, submission-heart.png, submission-explanation.png, submission-echo-review.png, submission-public-ecg.png
- Solo entrant: Aditya Jevoor (confirmed by user); Devpost jozai193. Team name Coronary Atlas, Track A. Private organizer email was entered with user confirmation and is deliberately absent from this public file.
- Devpost preview: https://devpost.com/software/coronary-atlas-tjy0d7

## Credits and boundaries
Code MIT. BodyParts3D anatomy and the attributed UCI/PTB-XL resources retain their source-specific CC BY 4.0 credits and provenance. No endorsement by a doctor, dataset author or institution is claimed. App observations and report images are not persisted by application code. No clinical validation or broad independent photo-autofill validation is claimed.
