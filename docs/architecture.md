# Coronary Atlas architecture

React + TypeScript + Vite -> same-origin `/api` -> FastAPI/Pydantic -> validated canonical feature dictionary -> fitted sklearn preprocessing/classifier -> CAD/LAD/LCX/RCA probabilities + grouped SHAP -> dashboard and BodyParts3D coronary meshes.

The default is a local, stateless research app. No accounts, database, patient names, analytics or external inference APIs. Synthetic demonstration profiles are explicitly labeled; user-entered observations remain in memory. Production build is served by FastAPI, while Vite proxies the API during development. Public hosting requires a separate privacy/security review if real patient data will be entered.

## ML contract

- Immutable UCI workbook; deterministic seed 20261007.
- Explicit clinical feature allowlist, with LAD/LCX/RCA/Cath disallowed at ingestion, training and API boundary.
- Fold-local median/mode imputation, scaling, one-hot encoding and constant filtering where applicable.
- Four independent binary models. Compare regularized logistic regression, random forest and gradient boosting through 5 outer stratified folds and 3 inner folds. Select on inner ROC-AUC. Report outer predictions only as the main estimate. Compare a prevalence baseline; examine Brier score and reliability diagrams. No post-hoc threshold optimization; use 0.5 classification and explicitly nonclinical color bands at 0.3/0.7.
- Fit the final selected configuration using full-data inner CV after unbiased outer evaluation. Evaluation describes the selection procedure, not an externally validated deployed model.
- Independent predictions need not obey CAD >= every artery. Never silently reconcile or multiply vessel probabilities; explain this limitation.
- Save fold indices, predictions, candidate scores, configurations, package versions and source/model hashes.
- SHAP explains the actual selected model. Logistic output uses log-odds; tree output units are explicitly identified. Aggregate one-hot contributions back to original observations. Test local additivity.

## API and frontend

`GET /health`, `/model/info`, `/model/metrics`, `/sample-patients`; `POST /predict` accepts `{features: {...}}`. Dynamic field schema comes from the same backend metadata used for validation; Pydantic rejects unexpected top-level fields. Reject unknown feature names, prohibited labels, nonfinite values, invalid categories and malformed payloads. Missing values are allowed with visible imputation disclosure and a minimum completeness rule.

Manual input uses six clinical groups. The screen separates editable input from the last predicted snapshot; editing invalidates displayed probabilities until recomputed. Samples, API loading/errors, reset view, vessel selection and an evidence panel are first-class flows. The 3D scene uses local licensed geometry, capped device pixel ratio, demand rendering and accessible HTML controls. Color never replaces labels and percentages. A geometry-load failure is explicit, not a fake anatomy fallback.

## Anatomical correspondence

Use official BodyParts3D native-coordinate meshes and FMA names, not inferred arbitrary curves. Heart wall meshes provide context. LAD trunk corresponds to FMA74912, LCX to FMA3895, RCA trunk to FMA3802. Verify available archive members and geometry before locking the mapping. Colors apply to whole vessel meshes; geometry is shared reference anatomy, never a patient's scan or precise plaque map.

## Verification and boundaries

Tests cover leakage, fold isolation, category/missing handling, deterministic probabilities, model integrity/loading, API response schema, explanation additivity and UI state. Browser QA must exercise input-to-result, rotation/zoom/selection, responsive layout and error/stale states. Reproducibility includes dependency locks and a documented regeneration command. Public repository, video publication, team details and final submission are separate outstanding release actions.
