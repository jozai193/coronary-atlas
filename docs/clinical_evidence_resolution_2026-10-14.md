# Clinical evidence issues: implementation and remaining data gaps

The user requested fixes to four unresolved issues and confirmed that only the public dataset examples are available. This limits what can actually be resolved. The source audit and implementation below do not constitute clinical validation.

Subsequent use of the suggested PhysioNet resources added twelve real PTB-XL ECG reference cases and a bounded 1,000-record MIMIC machine-text negative control. See [acquisition, implementation and remaining gaps](physionet_use_results_2026-10-14.md). These sources belong to different people than the UCI profiles. The original report/angiography and independent validation limitations below still apply; final frontend verification after this addition passed 71 tests.

| Issue | Implemented or checked | Still unresolved |
|---|---|---|
| Original ECG/echo reports and actual artery narrowing | Added ephemeral local PDF/image attachments, source reference/date/findings, separately recorded LAD/LCX/RCA narrowing, source-check status, report metadata in summary/worksheet/JSON export. Blank means unknown; percentages must be single values from 0 to 100. | No original report or measured narrowing was acquired for the public 303-person cohort. The source archive contains only the workbook; categorical labels cannot recover continuous percentages. User-entered reports are unverified and do not make the public examples independent or complete. |
| Prediction agreement with echo | Added comparison of checked reported EF with the actual model EF input. Explicit **Use checked report EF as model input** copies a supported value and clears the previous estimate. Changing report details invalidates the source check. | EF, valve narrowing/leakage and coronary labels are different outcomes. No justified rule makes their numbers equal or overrides CAD/vessel outputs. Additional Doppler/valve findings remain source-review context because the training table does not contain them. |
| Alcohol/lifestyle fields influencing prediction | Audited all eight additional context keys against the 55-input training contract and verified they are excluded. Existing smoking flags and LDL/HDL/TG remain modeled. UI now explains why additional fields cannot change this model. | A model using alcohol, activity, diet or lifestyle change requires compatible pre-outcome measurements and labels, versioned training and independent evaluation. No arbitrary weights, long-term risk score substitution or invented patient records were added. |
| Broader independent validation | Ran a frozen 11-page challenge from three additional official public specimen documents, fixed observed heading/commentary extraction problems, preserved the first evaluation and versioned development replay. Replayed existing AngioCAD and PeerJ external-study receipts and verified current workbook/model/anatomy artifacts. | Public specimen documents are not real camera photos, an independently adjudicated clinical OCR corpus or outcome-labeled model validation. Existing external studies use separate reduced-input models. The live 55-input baseline and ensemble still lack a compatible unused independent cohort. |

## Source and feature audit

`scripts/audit_clinical_evidence.py` reads the actual source workbook and archive, checks the feature/target exclusion contract, and emits only aggregate capability evidence. The durable receipt is `output/verification/clinical-evidence-capability-2026-10-14.json`. It confirms 303 rows, 55 modeled inputs, no original report files in the source archive and eight additional context keys absent from the model input list. No model was fitted or retrained in this work. `scripts/verify_artifacts.py` verified the raw workbook, four baseline models, anatomy manifest and all 104 source meshes.

The source study remains [UCI 411](https://archive.ics.uci.edu/dataset/411/extention+of+z+alizadeh+sani+dataset). [NHLBI heart tests](https://www.nhlbi.nih.gov/health/heart-tests) distinguishes echo/Doppler's chamber and valve assessment from coronary angiography. Source findings, model inputs, reported narrowing and predicted probabilities are displayed separately.

## Local report handling

- Files are retained only in the current browser's memory. No upload endpoint, persistent store or external OCR service was added. Local object URLs are revoked when their preview unmounts or the file changes. Loading another example, clearing the case, replacing the case through report import or refreshing clears report evidence. Editing model observations for the same case preserves the report context.
- Only PDF/PNG/JPEG/WebP files, nonempty and at most 10 MB, are accepted. A SHA-256 checksum identifies the selected bytes; it does not verify clinical authenticity, identity or interpretation. PDFs are opened locally for inspection, not interpreted as images or waveforms.
- Echo flow/valve notes and narrowing are user-transcribed, unverified context. A single percentage is accepted only as an exact transcription; ranges/comparators stay in notes. Missing angiography source information is called out. No lesion geometry, artery grade or diagnosis is inferred.
- Inference still accepts only the existing canonical feature dictionary. The explicit EF-copy action updates only `EF-TTE`. Context, report attachments and narrowing never enter the prediction request. Worksheet and JSON exports include transcriptions and attachment metadata, never file contents.

## Frozen OCR challenge

Primary provider sources, downloaded and rendered at 160 DPI, then visually checked before OCR:

- [Labcorp comprehensive metabolic panel specimen](https://files.labcorp.com/testmenu-d8/sample_reports/322000.pdf): all six pages, including commentary and educational pages as negative/abstention controls.
- [Labcorp hemoglobin specimen](https://files.labcorp.com/testmenu-d8/sample_reports/005041.pdf): both pages, normal and abnormal.
- [Quest Diabetes Risk Panel specimen](https://www.questdiagnostics.com/content/dam/corporate/unrestricted/documents/other/drpws_sample_report/DRPwS_sample_report.pdf): all three pages, including charts and reference commentary.

All are provider-authored specimen/test reports, not original reports for the model's patients. The earlier Labcorp lipid development document was excluded. These eleven pages cluster within three source documents and do not represent eleven independent patients. Ground truth includes 27 eligible printed facts of the supported types; age 26 in the Hb example is outside model support and excluded from eligible automatic fields. Images, full PDF copies and OCR transcripts remain in ignored temporary storage. Durable protocols contain source URLs/hashes and limited expected facts, not full reports.

| Run | Correct unflagged / eligible fields | Incorrect unflagged proposals | Interpretation |
|---|---:|---:|---|
| Frozen first challenge | 8 / 27 (29.6%) | 0 | Small additional-source test of the then-frozen parser. Extensive abstention/missing fields. |
| After parser corrections | 11 / 27 (40.7%) | 0 | Development replay on already inspected cases; not an independent improvement estimate. |

The fixes skip isolated test-name headings and explanatory prose so they cannot falsely conflict with a valid result row, and exclude HbA1c from the hemoglobin rule. Genuine repeated conflicting values still block import; reference intervals, unsupported units and ambiguous table layouts still require manual entry. Every proposal remained unconfirmed and no prediction was triggered by OCR.

Receipts: `output/verification/ocr-public-v1-protocol.json`, `ocr-public-v1-results.json`, `ocr-public-v2-protocol.json`, `ocr-public-v2-results.json`. Replay: `scripts/verify_public_ocr.py --protocol ... --output ... --session heart-colors`. The script checks the frozen parser and input-image hashes and refuses to overwrite an existing evaluation receipt. Reproduction requires the specified local browser session and the hash-matching rendered source pages.

One first-run non-GET request came from the laptop's injected Kaspersky script (`gc.kis.v2.scr.kaspersky-labs.com`), not application OCR code. The development replay blocked that domain only inside the isolated test page, without changing antivirus settings; it observed zero non-GET requests during image reading. This distinguishes app-owned behavior from device software and is not a guarantee about another user's extensions.

## Model evidence

The existing AngioCAD verifier reproduced 16 external target/cohort metric groups and four source OOF pairs with matching hashes. The PeerJ verifier reproduced all subgroup summaries, ten-bin reliability counts, frozen ordering, the failed improvement screen and exact UI evidence bytes. These are rechecks of existing separate reduced-input studies, not new validation of the live 55-input model. The current data-search limitations are in `accuracy_goal_data_review.md`; this task did not send messages, apply for restricted data or acquire new participants.

The remaining substantial gains require paired original reports, compatible lifestyle/outcome records, and an unused independently reviewed validation cohort. The software now supports evidence review and records where it is missing; it cannot supply evidence that does not exist in the available source.

## Final engineering verification

All 69 frontend tests in 22 files passed, followed by the TypeScript/Vite production build (existing Three.js chunk-size advisory). New tests cover report file constraints, unknown/invalid percentages, source-check invalidation, explicit EF copying, stale result clearing, case resets, context/target exclusion from inference, attachment-content exclusion from exports and escaped worksheet content.

Real Chrome against the rebuilt running review app checked local attachment/checksum/remove behavior, zero upload requests during attachment handling, simulated EF reconciliation from model input 50% to explicitly copied 55%, no inference from context edits, a 55-field-only prediction request, summary retention, JSON export separation and new-case reset. The attachment was a public laboratory specimen used only as a file-handling fixture; the EF transcription was explicitly simulated for engineering QA, not a clinical report. No paired original reports were supplied. Mobile viewport width was 390px and document width 380px. Desktop/mobile screenshots were visually inspected at `output/playwright/2026-10-14-report-evidence-desktop.png` and `2026-10-14-report-evidence-mobile.png`. Refresh cleared the entered case. The only console error was the intentionally blocked injected antivirus script; no application error was observed.
