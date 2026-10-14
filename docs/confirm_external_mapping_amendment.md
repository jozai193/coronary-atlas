# Outcome-mapping amendment before external scoring

The initial runner stopped before producing any external prediction or metric because `obstructive_cad` has three values. The frozen protocol, runner, fitted models and fit manifest remain unchanged. No model is retrained and no hyperparameter, threshold, feature or cohort rule changes.

The subsequent coding-only audit found `stenosis_50` is binary: all 19,320 rows with obstructive_cad 0 or 1 have stenosis_50=0, while all 6,969 rows with obstructive_cad=2 have stenosis_50=1. The three-valued field therefore must not be used as the binary endpoint. Use the existing explicitly named `stenosis_50` field for overall CAD, leaving LAD/LCX/RCA _50 fields unchanged. Compare it with the OR of four vessel indicators where all are observed and retain any disagreement as a diagnostic. Do not remap 1 to disease-positive from the three-class column.

The original registry paper documents normal, nonobstructive 1–49%, and obstructive >=50% categories, supporting this interpretation. The exact workbook codebook is still absent; the mapping is an explicit inference supported by column naming, the published endpoint and cross-column consistency, not author-confirmed code semantics. Report this qualification with the results.

The original runner remains frozen; `validate_confirm_external_v2.py` checks its hash plus the unchanged source/protocol/model hashes, and records its own hash and this amendment hash. All results are produced only after this amendment. There have been zero external performance results at the time of amendment.

Sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC3402246/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC7849944/ ; local outcome-coding-audit.json.
