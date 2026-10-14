# Track A official-source audit

Audited 7 October 2026. The workspace was empty: no existing application, README, Git repository, or AGENTS.md. The pasted URL was a placeholder; the event was located by name and verified against its linked Track A statement.

## Sources and access

- [Official overview](https://multimodal-ai-hackathon-2026-7.devpost.com/?ref_medium=portfolio): read, including eligibility badges, sponsors, requirements and prizes.
- [Rules](https://multimodal-ai-hackathon-2026-7.devpost.com/rules): official indexed text read; direct fetch intermittently returned 503. Recheck before submitting.
- [Schedule](https://multimodal-ai-hackathon-2026-7.devpost.com/details/dates), [updates](https://multimodal-ai-hackathon-2026-7.devpost.com/updates), [gallery](https://multimodal-ai-hackathon-2026-7.devpost.com/project-gallery): read. Gallery not published.
- [Problem statements](https://drive.google.com/file/d/1sPrF1CWyJMGk8c3JOwu08_sboeaAE5xc/view): downloaded original PDF; followed all six document links. Local PDFs and extracted text in `docs/sources/`. Tracks B, C and D were read for context; their domain requirements do not apply to this build.
- [Track A](https://drive.google.com/file/d/1T9Whog4kWF3mYB7ZMGyihGWpbJBJtsfz/view): four pages read in full.
- [Submission guidelines](https://drive.google.com/file/d/1HEy6MBO_BN_aID2Nik2woYLWfuawzwHN/view) and [prizes](https://drive.google.com/file/d/1GfOmWL6A4Q0KSNdwtpqRmaxneMbDMRAe/view): read in full.
- [Team formation clarification](https://multimodal-ai-hackathon-2026-7.devpost.com/forum_topics/45339-team-formation-on-devpost): one member creates the project and adds teammates when submissions open.
- No Track A starter repository, separate public FAQ or example submission was linked in the reviewed material. `/resources` and `/discussions` were inaccessible to the web tool. Discord is registration/community gated and has not been audited; no claim that private announcements were read.
- [UCI 411](https://archive.ics.uci.edu/dataset/411/extention+of+z+alizadeh+sani+dataset): original XLSX downloaded, CC BY 4.0 confirmed. DOI: 10.24432/C5461K.
- [BodyParts3D](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html), [current official license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html): CC BY 4.0, updated 27 February 2025. Older mirrors describe BY-SA 2.1 Japan; use the current official archive and retain attribution.

## Problem and scope

Predict the supplied CAD and LAD/LCX/RCA binary labels from tabular clinical observations. Display probabilities, feature attributions and measurements on an interactive anatomical heart. These are cross-sectional disease-label estimates in a selected cohort, not a validated future cardiovascular-event risk score, diagnosis or lesion-localization system. ECG and echo inputs are tabular findings, not raw signals/images.

## Requirements and deliverables

| Requirement | Planned evidence |
|---|---|
| Four classification targets; demographic, clinical, ECG, lab, echo inputs | Four saved sklearn pipelines; full feature schema |
| Exclude LAD, LCX, RCA, Cath from all model inputs | Explicit allowlist and regression test |
| Accuracy, precision, recall, F1, ROC-AUC | Executed nested cross-validation artifacts; confusion matrices, Brier scores and fold variance |
| Interactive 3D anatomy with independently colored arteries | Licensed OBJ anatomy with semantic FMA mappings; real probabilities drive colors |
| Rotate, zoom, select regions | Orbit controls, accessible vessel buttons and pointer selection |
| Overall and vessel probabilities beside heart | Integrated React dashboard |
| Interpretable contributions and physiological measurements | SHAP contributions, values and units/coding notes |
| Visible educational/decision-support disclaimer | Persistent app footer and report |
| Working web prototype integrated with model backend | FastAPI API, Vite production build, browser flow evidence |
| Trained weights and clean code | Versioned metadata, hashes, reproducible training script |
| Documentation max six pages | Concise technical report source; page count verified on exported report if produced |
| YouTube demo 3–10 minutes | Script and recording plan; actual upload remains outstanding |
| Public GitHub repository with prerequisites/setup/run instructions | README and release checklist; publication remains outstanding |
| Devpost description and full real-name team roster | Submission draft; user verifies account/roster |
| AI tool disclosure in Built With and README | Explicit Codex assistance disclosure |

An open-source mesh is permitted, not a particular mandatory file format or source. No required neural network, cloud, paid API, CSV upload, diagnostic certification or extra dataset is specified. CSV import and Docker are optional user-requested enhancements. A hosted URL is useful but not stated as a mandatory deliverable in the reviewed PDFs.

## Rubric (verified Track A PDF)

| Criterion | Weight | Meaning |
|---|---:|---|
| Predictive Performance | 30% | Classification, probability estimation, validation |
| 3D Visualization | 25% | Anatomy, spatial mapping, interaction |
| Clinical Interpretability | 20% | Attribution clarity, physiological breakdown |
| System Integration | 15% | Data pipeline, connected dashboard, updates |
| Technical Implementation | 10% | Architecture, code, reproducibility, public resources |

## Dates, eligibility and restrictions

Submissions: 30 September 2026 00:00 IST through **15 October 2026 00:15 IST** (14 October 18:45 UTC). Rules describe development through 14 October EOD. Judging: 15–20 October; announcement 21 October, schedule gives 15:00 IST. Online and free. Teams 1–4; inter-college teams permitted. Age 14+. Overview badges say students only and exclude companies/professional organizations; prose rules say primarily students but all eligible individuals may apply. Treat non-student eligibility as unresolved, not guaranteed.

One submitting team per individual; one track per team. Prior Track C work does not authorize a second submission. Final track/team decision is a user release prerequisite. Track A prizes: INR 15,000 first and INR 10,000 second per detailed prize PDF/overview; rules' one-winner-per-track wording conflicts with those surfaces.

AI coding assistance is allowed with disclosure. Judges may ask participants to explain their code. No explicit prior-work policy was found in the retrieved rules excerpt: do not invent one. Keep dates/provenance and recheck rules before publication.

Submission risks: missed deadline, missing public code or working video, private YouTube video, absent English audio/subtitles, incomplete real-name roster, undisclosed AI assistance, multiple teams/tracks, unresolved eligibility, unlicensed assets. Leakage, invented metrics and false lesion/diagnostic claims undermine technical validity and rubric compliance even where not explicitly described as disqualification clauses.

## Dataset and constraints

303 records, 59 columns including four labels; see dataset analysis for executed findings. No raw imaging or lesion coordinates. Small selected cohort, rare categories and label inconsistency limit generalization. Laptop/browser performance matters; no dedicated GPU should be needed. Preserve semantic vessel/output correspondence and modularity for future features/models/anatomy.
