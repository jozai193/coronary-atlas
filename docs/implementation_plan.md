# Implementation plan and risk register

Created before application code. Work in descending dependency order, with checks at each boundary.

1. Archive official sources, inspect both workbook sheets, record licenses and hashes. Gate: six planning documents exist.
2. Build deterministic EDA and feature metadata. Gate: 303x59 verified; forbidden targets absent from input allowlist; exhaustive column audit saved.
3. Build sklearn pipelines, nested evaluation and saved artifacts. Gate: executed metrics, fold predictions, calibration, baseline, variance and label-disagreement sensitivity evidence. No claimed score before execution.
4. Add SHAP explanations and validated FastAPI interface. Gate: tests for input semantics, missingness, model reload, probability ranges, reproducibility and attribution reconstruction.
5. Extract licensed heart/coronary meshes with explicit semantic IDs. Gate: local OBJ load and shared coordinate inspection; credits visible.
6. Implement React input/results/3D/explanation/evidence dashboard. Gate: TypeScript and production build pass; schema originates in backend.
7. Run real browser desktop/mobile workflow, fix issues, capture screenshots. Gate: actual model predictions and dynamic vessel states; no mock success screenshots.
8. Finish README, report, demo script, judging evidence map, setup verification and progress ledger. Gate: commands exercised locally; final limitations explicit.

## Major risks

| Risk | Mitigation / honest boundary |
|---|---|
| Optimistic metrics on 303 patients | Nested selection, OOF predictions, fold dispersion, baseline and calibration; no external-validation claim |
| Target or acquisition leakage | Hard exclude all four labels; inspect constant/derived fields; retain clinical-timing uncertainty |
| Cath-vessel inconsistency | Retain source; exclusion sensitivity analysis, record row index |
| Rare categories and missing inputs | Controlled schema, fold-local imputation, completion warnings; reject overwhelmingly missing inputs |
| Unclear units/codes | Source labels plus conventional expansions, marked unverified; avoid invented features |
| Misleading SHAP | Explain association to model output with units/background and correlated-feature caveat |
| False precise anatomy | Reference mesh, whole-vessel coloring, explicit no-lesion-location statement |
| Asset licensing / attribution | Official archive and current license snapshot; preserve file hashes and credits |
| Rendering on laptops | Low-poly models, demand rendering, DPR cap, browser measurement |
| Stale results after edits / request races | Clear results immediately, request identity or disable edit while pending |
| Small-data fairness | Descriptive subgroup diagnostics only; do not claim fairness or clinical utility |
| Event rules conflicts/private updates | Record conflicts, public-source coverage and final rule check |
| Unfinished publication | Separate local completion from public GitHub, YouTube and actual submission |

Optional CSV upload and Docker follow the essential integrated workflow. No paid services or unnecessary deep learning.
