# PhysioNet use: delivered work and remaining gaps

The available sources now contribute real ECG reference material and a bounded parser check. They do not establish paired ECG/echo/angiography evidence for the app's original UCI patients, support invented artery narrowing percentages, or independently validate its CAD models. The [pre-acquisition protocol](physionet_use_protocol_2026-10-14.md) fixed selection and scope before inspecting patient tables.

## What was acquired and used

| Resource | Actual use | Limitation |
|---|---|---|
| [PTB-XL 1.0.3](https://physionet.org/content/ptb-xl/1.0.3/) | Audited the complete metadata table: 21,799 ECGs from 18,869 people. Packaged twelve real 12-lead waveform excerpts, exact source report strings and original SCP descriptions in **Explore real public ECG references**. | These are separate people and ECG annotations, not angiographic outcomes or missing reports for the current profiles. No diagnostic interpretation or CAD scoring was performed. |
| [MIMIC-IV-ECG 1.0](https://physionet.org/content/mimic-iv-ecg/1.0/) | Acquired its dictionary/license and first 2 MiB of the machine-measurements CSV. Audited/replayed the first 1,000 complete records, representing 191 subjects. | Source-order prefix, not a random sample or complete cohort. The report lines are machine-generated; clinician notes and waveforms were not acquired. |
| [MIMIC-IV-Echo 1.0.1](https://physionet.org/content/mimic-iv-echo/1.0.1/) | Reviewed official documentation, structured echo/Doppler content, identifiers/timing and access requirements. | Documentation only. Protected records require approved credentialing, training and a signed DUA. Compatible clinical outcomes and actual same-person/study linkage remain unverified. |
| [ECHO-NOTE2NUM 1.0.0](https://physionet.org/content/echo-note-to-num/1.0.0/) | Reviewed the documented echo-note/measurement resource and access requirements. | Documentation only; credentialed records were not acquired. |
| [EchoGraph annotations 1.0.0](https://physionet.org/content/echograph-note2num-annotations/1.0.0/) | Reviewed the documented entity/relation annotation resource and provenance. | Documentation only. Automatically generated annotations over related MIMIC-III notes are neither an independent cohort nor fully manually verified ground truth. |

PTB selection used ascending ECG ID and four distinct patients in each provider fold 1, 9 and 10, without selecting on diagnoses or performance. IDs: 32, 35, 36, 37; 8, 10, 17, 30; 9, 38, 40, 57. Provider validation/test identities remain visible, but no model was evaluated on these references. All patients in the full source table occupy a single provider fold.

The PTB acquisition used the official public S3 mirror after slow direct transfers. The metadata, statement dictionary, license and 24 selected header/signal files matched the provider's SHA-256 list (27 matches). The initial partial MIMIC transfer was retained; its 278,115 bytes exactly match the subsequently completed bounded 2 MiB prefix. This verifies consistency between the acquired prefixes, not a provider hash for the complete MIMIC file.

## App behavior

Refresh the review app and open **Explore real public ECG references** below the case-review sections. It loads the reference index only when opened. Selecting a record changes only this viewer, leaving the current profile, model inputs and predictions intact.

Each figure displays the first 250 samples per lead at the original 100 Hz rate: 2.5 seconds, calibrated to mV. The strict decoder verifies WFDB format, sample count, lead order, calibration, initial values and per-channel checksums. Display scaling is explicitly schematic, with a shared vertical range within each figure; this is not diagnostic ECG paper. Mobile users can scroll the trace horizontally or open the full figure.

Source text is preserved without translation. SCP likelihood 0 remains unknown, and unlisted codes do not become negative findings. Privacy-protected/unavailable age remains unknown, and source sex codes remain unrecoded. No ECG code was converted into the UCI input contract, and an RR interval was not substituted for resting pulse. Attribution and the CC BY 4.0 license accompany the small display derivative. Acquired raw tables/signals remain local and ignored; MIMIC report text is not packaged in the app.

## Parser check and verification

The parser protocol froze the input order and current parser hash before replay. Across 1,000 public machine-generated ECG summaries, the actual report parser produced **zero field proposals, zero unflagged proposals and zero automatic confirmations**. This is an abstention/negative-control check. It does not measure OCR accuracy, sensitivity on positive laboratory/echo reports, diagnostic interpretation or CAD performance. The original receipt is preserved rather than overwritten after inspection.

- All 71 frontend tests in 23 files passed; TypeScript/Vite production build passed, with the existing Three.js chunk-size advisory.
- Eight waveform decoder/selection tests passed, including corrupt checksum, byte length, units, encoding, gain and lead-order rejection.
- Source verification passed for all twelve records, deterministic selection, distinct patients, reports/codes and generated waveform hashes.
- Real Chrome loaded every waveform. Source selection made zero prediction POST requests, preserved the current profile/estimates and produced zero application page errors. Desktop and mobile screenshots were inspected. At a 390px mobile viewport, document width was 380px; the 850px trace scroll stayed within its container.
- All eleven protected model/evaluation files matched their pre-task SHA-256 hashes. No model was fitted, scored or replaced in this task.

Durable receipts: `data/external_audit/physionet_v1/ptbxl-audit.json`, `mimic-iv-ecg-audit.json`, `resource-registry.json`; `output/verification/physionet-report-parser-protocol.json`, `physionet-report-parser-results.json`, `physionet-ui-2026-10-14.json`, `physionet-final-2026-10-14.json`. Screenshots: `output/playwright/2026-10-14-physionet-reference-desktop.png`, `2026-10-14-physionet-reference-mobile.png`, and all twelve `2026-10-14-ptbxl-*.png` record views.

Recheck with `.venv\Scripts\python.exe scripts/physionet_reference.py verify` and `.venv\Scripts\python.exe -m pytest tests/test_physionet_reference.py -q`. The raw hash-matching acquisitions are required for source verification. `prepare` regenerates the display derivative from those sources and downloads only missing/corrupt selected signal pairs. `scripts/verify_physionet_reports.mjs` requires the local source prefix-derived sample and refuses to overwrite the preserved evaluation receipt.

## What the four original issues now mean

1. **Original reports and narrowing:** real public ECG references are now available, but original UCI ECG/echo reports and actual LAD/LCX/RCA narrowing remain unavailable. Different participants cannot be combined into one apparent case.
2. **Agreement with echo:** these resources do not justify forcing CAD estimates to match echo findings. Checked EF reconciliation remains explicit; valve/Doppler observations remain source-review context. No actual paired echo data were acquired here.
3. **Lifestyle influence:** none of the acquired sources establishes compatible lifestyle measurements plus the app's outcomes and full input contract. Alcohol, activity and diet remain documented context rather than arbitrarily weighted predictors.
4. **Independent validation:** source checks and negative controls improved the evidence available for engineering review. Full photo-autofill and live-model accuracy still require suitable independently reviewed, unused examples and compatible outcomes. These twelve references and the 1,000 text summaries do not meet those requirements.

The next data-dependent step is approved access to a suitable echo/clinical resource, followed by a field/timing/endpoint and participant-overlap audit before integration. Angiographic outcome availability must be established separately. No agreements were signed, access applications submitted or external messages sent during this work.
