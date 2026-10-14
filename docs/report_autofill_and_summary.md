# Summary and assisted report autofill

13 October 2026. These features improve input review and reduce typing; they do not establish higher model accuracy.

Echo-template follow-up: [source-text review and sample checks](echo_template_review_2026-10-14.md) adds chamber/valve/flow/impression excerpts, NORMAL/NORMALS table safeguards, and explicit current-case confirmation before appending notes. Choose the intended case before copying; a subsequent **New case** numerical import clears previous report evidence. The supplied photo's OCR could not reliably read EF or the dilation sentence, so manual correction is still required. Corrected-text regression results are separate from actual-photo results.

14 October update: [clinical evidence work](clinical_evidence_resolution_2026-10-14.md) adds optional local report attachments and separate reported findings/artery narrowing, checked-EF reconciliation, and an additional frozen 11-page specimen challenge. The original reports and percentages for the public source cohort remain unavailable. The first challenge recovered 8/27 eligible fields without an incorrect unflagged proposal; after heading/commentary fixes, the same-case development replay recovered 11/27. This low coverage and three-document sample do not establish reliable clinical OCR or independent model accuracy. The original two lipid pages below remain historical development fixtures.

## Doctor's next review

1. For the latest review, choose **Start clinician review → Review profile R1 inputs** for all 55 recorded model inputs. Source labels are reference outcomes, never model inputs or blockage percentages. Original ECG/echo reports are unavailable. C/D remain incomplete synthetic examples; missing required fields block prediction. Earlier C/D walkthrough: choose **Review profile C inputs**, then inspect the case facts. Repeat with **Profile D**. These are new synthetic cases (ages 56 and 64), chosen before scoring. Each supplies 45 of 55 inputs; nine unchosen ECG/echo flags and the obesity category remain unknown. Explicit choices, calculated BMI and cohort defaults are labeled. There are no original images or known outcomes.
2. Choose **Open case summary** at the top or **View case summary** beside the results. It shows important observations, ECG/echo, all four current probabilities, separate raw outputs, top SHAP factors, unknowns and model limitations. A draft shows no stale predictions. Back navigation retains the current draft; refresh clears it. The worksheet preserves full precision and input origins.
3. Try **Import a report photo · assisted autofill** with one English, de-identified PNG/JPEG/WebP page. Paste report text as a fallback. Compare each proposal and unit against the source, correct OCR errors and confirm individual values. **New case** clears all unselected observations by default. **Current case** explicitly retains them and should be used only for the same patient and collection context. Nothing predicts automatically.

Supported extraction: explicit age/sex, LDL/HDL/TG, fasting glucose only when labeled fasting, creatinine, hemoglobin, sodium/potassium, height/weight, resting pulse and echo EF. A printed conventional unit is required for numerical measurements. Unsupported units, multiple numbers, ranges/comparators, conflicts and unreadable results are flagged for manual entry. Printed ranges, previous values, comments, non-HDL/VLDL and LDL-particle counts must not become the supported lipid result. No fasting status, ECG category, valve grade or diagnosis is inferred. Missing details remain unknown.

Limitations: English printed-image prototype, maximum 10 MB / 16 megapixels. No direct PDF upload, handwriting support, ECG-waveform interpretation or echo-image interpretation. It cannot fill all 55 observations from a report that contains only a few. No clinical OCR validation or low error-rate claim follows from two pages. Entering fewer than the prototype's minimum supported observations keeps prediction disabled.

## Public specimen test

Official source: [Labcorp LP+Non-HDL Cholesterol sample report](https://files.labcorp.com/testmenu-d8/sample_reports/343925.pdf), linked from [its test information page](https://www.labcorp.com/tests/343925/lipid-profile-with-non-hdl-cholesterol). It is explicitly a fictional Sample Report with normal and abnormal specimen pages, not an identified patient's record. Downloaded locally 13 October 2026; SHA256 `34cab7d846ccd31194db99ed3f09b7383679ff75d0d10d4e4931a903089216f7`. Rendered each page at 160 DPI for a browser-image test. The original copyrighted PDF, page images and full OCR transcript stay in ignored temporary storage; they are not redistributed in the source archive.

Expected facts, checked against the PDF's printed current-result columns:

| Page | Age / sex | TG (mg/dL) | HDL (mg/dL) | LDL (mg/dL) |
|---|---|---|---|---|
| Normal specimen | 32 / male | 55 | 60 | 27 |
| Abnormal specimen | 32 / male | 175 | 45 | 213 |

Final authenticated public-site browser check recovered all three lab values on each page, with five proposals per page including age/sex. Every proposal started unconfirmed. An earlier test exposed warning-icon / superscript-footnote handling; a focused parser regression now covers those observed artifacts. Reference values and non-HDL/VLDL results were excluded. These are development fixtures for the parser, not an unseen OCR benchmark or training data for the disease model.

Separate browser checks applied only LDL from the abnormal specimen to a new case: 1/55 supplied, 54 unknown, old prediction cleared and Generate prediction disabled. Browser back retained that draft; reload cleared entered values. Desktop and 390px summary layouts were inspected; final layout has no page overflow. Parser tests cover conflicting occurrences, uncertain decimals, multiple results, unsupported units, range bounds, fasting status, ECG/target non-inference and BMI invalidation.

## Processing and distribution

[Tesseract.js](https://github.com/naptha/tesseract.js) runs in a local browser worker. Worker, baseline/SIMD/relaxed-SIMD LSTM core and English language data are self-hosted under `/ocr/`, loaded only on image import. Package versions, file hashes and license copies are included. No OCR server, remote inference API or runtime CDN is used. Cache writes are disabled; preview URLs and worker memory are released on clear/unmount. The app does not store or upload the image or OCR text. Confirmed observations enter the existing prediction request only if the user later generates a result; an explicit worksheet export saves selected observations locally.

The test laptop's antivirus injects a separate web script, which was observed in the network trace. For the final browser test its requests were blocked in that isolated test page only; antivirus settings were not changed. Application-owned OCR requests were same-origin GET requests for assets, with no report uploads or external service requests. This is an app behavior check, not a guarantee about a user's browser extensions or device software.

Regenerate runtime assets with `node frontend/scripts/vendor-ocr.mjs` after `npm --prefix frontend ci`. Check `frontend/public/ocr/manifest.json` and license/NOTICE files. New fixture generator: `python scripts/create_review_profiles.py`; historical A/B fixtures remain unchanged for experiment reproducibility.
