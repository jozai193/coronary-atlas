# External-data audit v2

This audit stores one read-only copy of the official UCI 412 workbook and a reproducible row-level comparison against the project’s existing UCI 411 source. No records were added to training, model evaluation, or production inputs.

## UCI 412 versus the project source

- Downloaded archive: [UCI Z-Alizadeh Sani, dataset 412](https://archive.ics.uci.edu/dataset/412/z), credited to Roohallah Alizadehsani, Mohamad Roshanzamir, and Zahra Sani; DOI `10.24432/C5Q31T`; CC BY 4.0. The archive is `uci412.zip` (123,772 bytes, SHA-256 `48210a6623fa6112423d9bc357f72fe3fca12ae77866e63e08632e15d95b724e`).
- Project source: [UCI extension 411](https://archive.ics.uci.edu/dataset/411/extention%2Bof%2Bz%2Balizadeh%2Bsani%2Bdataset), same credited authors; DOI `10.24432/C5461K`; CC BY 4.0. Local workbook SHA-256 is `739343245c2ba578b541370217531750d8e936022f928b83e0d91756caa3ff0b`.
- The populated UCI 412 sheet has 303 rows and 56 columns. The UCI 411 sheet has 303 rows and 59 columns. Their 55 shared input fields are identical cell-for-cell and in the same order. The 216 CAD labels differ only in capitalization (`CAD` versus `Cad`); the remaining 87 are `Normal`. UCI 411 adds LAD, LCX, and RCA target columns.
- The UCI page describes 54 features, while the workbook contains 55 input fields plus Cath. A second workbook sheet is empty (0 records). These metadata differences do not change the row-overlap result.
- **Decision:** UCI 412 is not an independent cohort. Do not pool it, split it across development and validation, or describe it as external validation.

## Reproduction

Run `python scripts/research_external_audit_v2.py` from the workspace root. It writes `uci412-audit.json`, records both workbook hashes, checks every shared input cell, and performs no model fit. Source script: [research_external_audit_v2.py](../../../scripts/research_external_audit_v2.py).

## Other public data considered

- [UCI Heart Disease, dataset 45](https://archive.ics.uci.edu/dataset/45/heart+disease) has multiple historical sites and raw angiographic vessel fields, but not the 55-field feature contract or matching labels. Its Cleveland raw file is explicitly flagged as corrupted by the local archived warning; Hungary has many missing vessel labels; units and label codes do not line up with this cohort. Existing audit: `data/external_audit/` and `scripts/audit_external_data.py`.
- The 2018 paper [Alizadehsani et al., DOI 10.1016/j.cmpb.2018.05.009](https://pubmed.ncbi.nlm.nih.gov/29903478/) describes a 500-patient extension and reports separate LAD/LCX/RCA models. The public UCI 411/412 workbooks audited here remain 303 rows. No matching 500-row workbook or explicit data-use terms were found in the public UCI records or reviewed article record. This is a promising provenance lead only; no data was obtained, and no author outreach was made.
- [ARCADE](https://zenodo.org/records/10390295) provides angiography images and expert annotations for vessel/lesion imaging tasks. It does not include the clinical 55-field inputs and four matching targets; the Zenodo rights/license field is blank.
- [CADICA](https://arxiv.org/abs/2402.00570) describes invasive angiography videos and disease-related metadata, a separate imaging task with no verified matching 55-field feature table or four target labels.
- [STAFF III](https://physionet.org/content/staffiii/1.0.0/) is an ECG response database from 104 patients undergoing controlled balloon occlusion, with 152 artery-specific occlusions. It is not the same pre-test clinical table or outcome definition.

None of these candidates was merged into the model data or used for external metrics.
