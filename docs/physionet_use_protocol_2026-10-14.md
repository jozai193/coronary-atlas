# Bounded PhysioNet use protocol

Frozen before inspecting downloaded patient-level tables or selecting records. Purpose: use the supplied ECG/echo resources for source-grounded reference display and compatibility assessment. This task does not train or validate a CAD model, interpret ECG waveforms diagnostically, infer missing observations or link unrelated participants.

## Acquisition

- PTB-XL 1.0.3: acquire metadata, SCP statement dictionary, license and provider checksum list. Select exactly four records from each of provider folds 1, 9 and 10 by ascending ECG ID, taking at most one ECG per patient. Fold 1 is a small training-fold reference sample; folds 9/10 retain their provider validation/test identities. No selection by diagnosis, demographics or model performance. Download only the 100 Hz WFDB header/signal pairs for those twelve records, not the multi-gigabyte archive. Verify selected files and tables against the provider checksums.
- MIMIC-IV-ECG 1.0: acquire its public machine-measurement dictionary and license. Read at most the first 2 MiB of the machine-measurements CSV, then inspect the first 1,000 complete records from that bounded prefix. This is a source-order schema/content sample, not a random or complete cohort. Preserve the partial-file status and hash. Machine interpretations must not be described as cardiologist notes.
- MIMIC-IV-Echo 1.0.1, ECHO-NOTE2NUM 1.0.0 and EchoGraph annotations 1.0.0: inspect official public documentation and access requirements. Do not sign an agreement, claim completed credentialing, or retrieve protected records without existing approved access. Record documents versus data actually acquired.

## Use and boundaries

- A separate public ECG reference panel may show the selected PTB-XL waveform excerpts, source report strings, original SCP statements, provider fold identity, licensing and attribution. It must never populate the current patient form, inherit that profile's CAD estimates, depict an individual's coronary lesion, or claim this new source independently validates the app.
- Waveform rendering uses the original header calibration and lead order, verifies the sample count/format and per-channel checksum, and describes display scaling and excerpt duration. This is a reference viewer, not a diagnostic reader or newly trained ECG model.
- Missing labels mean unavailable/unknown, not negative. PTB-XL privacy-shifted ages must not become normal numeric ages. Do not infer absence of an ECG finding merely because its code is absent. Do not convert ECG RR intervals into the app's resting pulse without a reviewed measurement/timing definition.
- Echo-derived annotation resources sharing MIMIC-III source notes are overlapping resources, not independent cohorts. MIMIC-IV ECG/echo linkage requires shared subject identifiers plus compatible study timing and verified endpoint definitions; linkage is not established by similar patient characteristics.
- CAD/LAD/LCX/RCA target availability, the 55-feature contract, original report/scan availability and alcohol/lifestyle coverage must be audited independently. A dataset's size or ECG diagnostic labels do not substitute for coronary angiographic outcomes.
- All existing model artifacts and original evaluation evidence remain unchanged. Raw acquired research data stay local/ignored. Only a small attributed PTB-XL display derivative is packaged under its CC BY 4.0 terms.

## Verification

Require provider checksum matches, deterministic record selection, twelve distinct patients, fold separation, valid waveform calibration/checksums and exact report/code provenance. Test reference-panel loading/error states and case isolation, then inspect desktop/mobile rendering. Report every unavailable resource and unperformed clinical check explicitly.
