# Doctor-supplied echo template: implementation and checks

The user supplied a partly completed 2-D/M-mode and colour-flow Doppler report template and asked us to use it. It has placeholder identity fields, numerous blank measurements, a visually readable EF of approximately 55%, normal valve/flow narrative, and a statement that the aortic root is mildly dilated alongside a broad normal-echo impression. It is an example for development, not an original report for a UCI participant, an independently adjudicated patient case or clinical validation.

## Changes

- **Echo text for source review** now groups matched source excerpts into structure/chamber, valve, flow/Doppler and impression text in the report-import screen. It preserves words and negations as supplied by OCR/paste; it does not translate prose into diagnoses, numerical measurements, valve grades or coronary outcomes. Broken/unrecognised lines can be missed, so the original image and editable raw text remain the source for checking.
- Reference-range tables get an explicit NORMAL/NORMALS warning. Blank numerical measurements stay unknown. Parenthetical `LVEF (est)` is recognised, but flattened dimension/reference tables require patient-column review before the proposed value can be confirmed. Pipe-delimited, ambiguous, comparator and range rows remain blocked. A user can manually re-enter a checked value; ordinary range/support checks still apply.
- A narrow wording check asks for review when a normal echo impression accompanies a specific matched finding such as dilation. Both source statements are retained. This is a heuristic reminder, not a complete contradiction detector or diagnostic interpretation.
- **Append reviewed echo text to current case** requires an explicit source/case checkbox. It appends to existing source notes, flow and valve text, preserving existing entries. The whole operation refuses overlong combined fields rather than silently truncating. Repeated identical excerpts are not duplicated. It does not set a source identity/date, reported EF, angiographic narrowing, model features or predictions; report verification returns to pending. The user must add the real source reference/date and check the report there.
- The supplied image is not bundled into the app or attached to a public profile. A manually checked text excerpt and synthetic layout variants are retained only as clearly labelled development test fixtures. Changing case resets pending OCR text and confirmations as well as report evidence, preventing cross-case carryover.

The app still uses only its existing numerical/categorical model contract. No added echo measurement, valve severity threshold, Doppler animation or model weight was invented. Echo/Doppler provides chamber, pumping, valve and flow information; this template contains no measured LAD/LCX/RCA narrowing. See [NHLBI echo/Doppler explanation](https://www.nhlbi.nih.gov/health/heart-valve-diseases/diagnosis).

## Actual photo versus corrected text

The supplied JPEG was passed through the existing local browser Tesseract OCR before and after the change. **It produced zero numerical model proposals in both runs.** Its OCR EF line was unreadable and the aortic-root dilation sentence was garbled. The app does not guess missing digits or silently replace those words with the manual transcription.

The new viewer grouped some readable valve, flow and impression excerpts and displayed the table/verification reminders. It did **not** recover the missing EF or reliably detect the specific dilation/impression wording from this low-quality photo. The specific wording reminder and EF column guard were checked separately using a manually corrected transcription and synthetic delimiter variants. These checks must not be described as successful automatic extraction from the photo, independent OCR validation or improved CAD accuracy.

Raw image bytes and complete OCR output stay outside packaged source. The durable sample receipt records the image hash, expected unknowns, parser/fixture hashes, baseline abstention and development scope. Original earlier OCR/MIMIC protocols and receipts remain unchanged and identify their historical parser versions.

## Verification

All **77 frontend tests in 24 files** passed, followed by the TypeScript/Vite production build with the existing Three.js chunk-size advisory. New tests check table reference-range abstention, parenthetical EF labels, unknown/range/comparator values, verbatim source findings, negations, the wording reminder, preservation/deduplication/length limits, explicit case confirmation, source-check invalidation, exclusion from prediction and case resets.

Real Chrome against the rebuilt local review app checked the actual photo separately from the corrected-text fixture. It observed zero non-GET requests and zero application page errors during these operations. The corrected-text exercise preserved existing notes and both source statements, kept EF/narrowing blank in evidence, retained pending verification, carried notes into the summary and cleared pending import/evidence on another case. Mobile viewport/document widths were both 390px. Desktop/mobile screenshots were visually inspected. The known injected antivirus domain was blocked only inside the test page; device settings were unchanged.

All eleven protected fitted-model/metadata/evaluation files matched their earlier hashes. Replaying the same 1,000 MIMIC machine summaries after this parser change again produced zero proposals and zero automatic confirmations. This was a development regression on already inspected text, not an independent clinical test.

Receipts: `output/verification/doctor-echo-sample-2026-10-14.json`, `doctor-echo-ui-2026-10-14.json`, `doctor-echo-negative-control-protocol.json`, `doctor-echo-negative-control-results.json`. Screenshots: `output/playwright/2026-10-14-echo-photo-ocr.png`, `2026-10-14-echo-review-desktop.png`, `2026-10-14-echo-review-mobile.png`. Regression fixture: `frontend/src/echoSample.fixture.ts`.
