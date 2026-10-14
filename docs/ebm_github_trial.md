# InterpretML GitHub trial: fixed main-effects EBM

Completed 9 October 2026. This is a **research-only, repeated internal development check** on the same 303 Z-Alizadeh Sani patients and the same 40 saved `broad_v2` outer partitions previously inspected in this project. It is not new-patient validation, a clinical accuracy claim, or a change to Coronary Atlas's served models.

## Why this repository

[InterpretML](https://github.com/interpretml/interpret) is an MIT-licensed open-source library with an [ExplainableBoostingClassifier](https://interpret.ml/docs/python/api/ExplainableBoostingClassifier.html). Its [EBM guide](https://interpret.ml/docs/ebm.html) describes an additive model whose feature terms can be inspected directly. The fixed configuration here turns interactions off, limiting the fitted model to main effects. This makes it a plausible accuracy-plus-explanation candidate for a future research model, though the fitted terms describe model associations and do not establish clinical causes.

The optional `interpret-core==0.7.8` package was installed only under ignored `.venv-ebm/site-packages`; the application dependency set and four model artifacts were untouched.

## Protocol and audit

The [machine-readable protocol](../ml/experiments/ebm_github_v1/protocol.json) was written **before the first fit** and SHA-256 locked as `e35309317ef62e94da4f00857976a6193f34f54ddb437980eac138658ef474e1`. It fixes one configuration: all 55 original inputs, explicit numeric/nominal types, no interactions, 64 bins, eight outer bags, learning rate 0.015, at most 1,000 rounds, the specified early stopping, and one CPU thread. It fixes 0.5 as the sensitivity threshold and the existing AUROC/Brier engineering screens. No hyperparameter search or new threshold was conducted.

The runner checked the source workbook, schema, all 40 fold JSONs, and all eight baseline CSVs against hashes before fitting. Each fold used its saved outer training rows only and produced probabilities for its held-out rows. The comparison uses the saved `baseline_selector` probabilities on **identical people and folds**; unlike this fixed EBM, that baseline selected among four families inside each outer training partition. Each repeat produces one 303-row out-of-fold estimate; the two repeats are averaged as *two development views*, never as 606 independent people.

All 40 fixed fits completed in 105 seconds wall time, with no timeouts, fit failures, or estimator warnings. The maximum model-fit time was 1.52 seconds; worker startup accounts for the rest. All fitted models retained 55 single-feature terms and zero interactions. Eight [row-level prediction files](../ml/experiments/ebm_github_v1/) and a [run manifest](../ml/experiments/ebm_github_v1/run_manifest.json) are saved. Running `.venv/Scripts/python.exe ml/ebm_github_trial.py --verify` independently checked source/fold/baseline/output hashes, all 303 rows and five fold assignments in each file, recomputed metrics, and confirmed both predeclared screens.

The first verifier pass caught a CSV round-trip difference of at most `2.22e-16` in serialized *baseline* probabilities. The exact script that executed all fits is preserved as [fit_runner_snapshot.py](../ml/experiments/ebm_github_v1/fit_runner_snapshot.py) and matches the manifest's runner hash. The post-fit verifier tolerance changed to `5e-16`, and text-hash checks now normalize Git checkout line endings to the original byte convention. No fit, EBM probability, metric screen, or protocol was rerun or changed. Disposable LF and CRLF checkout simulations both passed verification.

## Results

Values average the two repeat-level raw OOF metrics. Higher AUROC and sensitivity are better; lower Brier is better. The fixed 0.5 sensitivity is not a tuned operating point.

| Target | Baseline AUROC | EBM AUROC | Δ AUROC | Baseline Brier | EBM Brier | Δ Brier | Baseline sensitivity | EBM sensitivity | AUROC screen | Probability screen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| CAD | 0.9098 | **0.9285** | **+0.0187** | 0.1045 | **0.0930** | **−0.0115** | 0.9097 | **0.9352** | Pass | Pass |
| LAD | 0.8287 | 0.8289 | +0.0002 | 0.1683 | **0.1617** | **−0.0067** | **0.8701** | 0.8588 | Fail | Pass |
| LCX | **0.7276** | 0.6966 | −0.0311 | **0.2061** | 0.2149 | +0.0089 | 0.3824 | **0.4160** | Fail | Fail |
| RCA | **0.7079** | 0.6957 | −0.0121 | **0.2080** | 0.2121 | +0.0041 | **0.3772** | 0.3377 | Fail | Fail |

CAD AUROC improved in both repeats by +0.0168 and +0.0207, and Brier improved in both by 0.0102 and 0.0127. At the fixed 0.5 threshold, CAD false negatives were 13 and 15 with EBM versus 21 and 18 with the matched baseline. Those are repeat-specific counts on the *same 303 people*, not independent reductions in patient harm. LAD's mean Brier improved, but its AUROC decreased in the first repeat and its mean sensitivity fell. LCX and RCA remain weak: EBM worsened mean AUROC and Brier for both. LCX sensitivity rose on average while its overall discrimination and probability quality worsened, so the sensitivity change does not justify a vessel-model replacement.

## Decision

The GitHub repository supplied a **real candidate for CAD research accuracy and direct additive explanations**, but the reused cohort and earlier family search mean the apparent CAD gain is vulnerable to model-selection optimism. It also fails as a general four-output replacement because LCX and RCA are worse. Keep the current app models unchanged. The strongest next accuracy experiment would use a separately frozen CAD EBM protocol on **compatible independent data**, then audit calibration, explanation fidelity, and the exact served API before considering replacement. Only 13 of these 55 inputs could be mapped confidently to the already tested AngioCAD cohort, so its separate 13-input results cannot validate this EBM or the present app.
