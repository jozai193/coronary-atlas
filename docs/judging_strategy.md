# Judging evidence strategy

Weights reverified against the current organizer Track A PDF on 9 October 2026.

| Criterion | Implementation and evidence | Location in demo/report | Remaining weakness |
|---|---|---|---|
| Prediction 30% | Four tasks; nested stratified CV and OOF plots; separate frozen 13-input AngioCAD transport test | Model evidence panel; validation/results sections; demo validation segment | Full 55-input app lacks a matched external test; LCX/RCA sensitivity remains weak |
| 3D 25% | Licensed anatomical meshes, explicit FMA artery mappings, probability colors, orbit/zoom/select | Center viewer; anatomy section; live interaction sequence | Shared reference anatomy; no patient geometry or lesion coordinates |
| Interpretability 20% | Actual selected-model SHAP, signed grouped factors, input measurements, base/output units | Attribution panel and report explanation section | Associations; correlated and rare features limit stability |
| Integration 15% | Manual/sample input through validated API to new predictions and scene colors; stale/error state tests | Full live workflow, browser receipts | Local performance evidence only until hosted verification |
| Technical 10% | Pinned dependencies, seeded scripts, integrity hashes, tests, clear setup and licenses | README, report reproduction section, final demo segment | Clean environment / platform checks limited to those actually run |

Allocate effort to validation and real anatomy first, then explanation clarity and usability. Strong evidence is reproducible output, not embellished percentages. No expected score, winner prediction or accuracy guarantee is made.

## Final evidence locations

- Prediction: `ml/metrics/evaluation.json`, four `*_oof.csv` files, `sensitivity.json`, `docs/figures/validation.png`, `confusion-matrices.png`. AUC 0.920/0.831/0.741/0.717; full metrics and limits in report pages 2-3.
- Anatomy: `frontend/public/anatomy/manifest.json`, `assets/anatomy_provenance.json`, browser screenshots including `output/playwright/redesign-report.png`; report page 4.
- Interpretability: actual-model SHAP chart, `output/verification/all_rows_shap.json` (all 303 rows, all four models), `lcx-explanation.png`; report page 3.
- Integration: `docs/verification.md` records real-browser manual/sample/CSV/result/export flows, mesh picking and mobile checks. The 234 ms observed interaction is not a latency benchmark.
- External transport: [AngioCAD protocol](angiocad_external_protocol.md), [results](angiocad_external_results.md), frozen model/hash manifest and read-only saved-prediction verifier. This is a separate 13-input model and does not validate the app.
- Technical: dependency locks, README, backend/OpenAPI types, current test receipts in `docs/verification.md`, fresh-environment install evidence, artifact hashes and the verified six-page report. Source package can be regenerated with `python scripts/package_source.py`.

Publication, video upload and clinical/anatomical expert review remain unperformed. The full 55-input app remains unvalidated externally; the separate reduced-model AngioCAD test and negative four-input CONFIRM test are reported with their scope. The app/report expose weak LCX/RCA sensitivity rather than hiding it behind overall CAD results.

The [GitHub opportunity audit](github_repo_opportunities.md) found existing open anatomy explorers and guided heart lessons. In the demo, demonstrate the linked held-out error, reference-only vessel view, separate live-model SHAP and honest AngioCAD transport evidence as one task; avoid a generic “first 3D heart plus AI” novelty claim. Repository code or published single-split metrics are not substitutes for an independently checked model result.
