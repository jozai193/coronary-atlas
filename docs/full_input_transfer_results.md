# Full-input LCX transfer results

13 October 2026. Frozen protocol: `full_input_transfer_protocol.md`. Runner: `ml/full_input_transfer.py`; source-indexed predictions and model/partition receipts: `ml/experiments/full_input_transfer_v1/`. Fitted models and acquired workbooks are local only.

303 source participants, 331 eligible AngioCAD LCX records before fold-specific fingerprint exclusions. Two repeated five-fold internal source evaluations. Three fixed ridge-logistic arms; no tuning or operating-point search. The full-input arms retain all 55 source features; AngioCAD contributes only its 13 harmonized features and a separate intercept.

| Arm | AUC run 1 / 2 | Brier run 1 / 2 | Accuracy run 1 / 2 | Sensitivity run 1 / 2 |
|---|---|---|---|---|
| Common 13 local | .7155 / .7153 | .2083 / .2089 | 69.0% / 67.7% | 39.5% / 35.3% |
| Full 55 local | .7294 / .7046 | .2046 / .2110 | 66.3% / 64.0% | 40.3% / 37.8% |
| Full 55 augmented | .7458 / .7196 | .2002 / .2070 | 68.6% / 67.0% | 45.4% / 42.9% |

Accuracy and sensitivity use cutoff 0.5. Augmented versus full-local mean paired Brier difference: **−.00419**, conditional 95% row-bootstrap interval **[−.00884, +.00070]**. Both runs move in the favorable direction, but the interval includes no benefit. Full-local and augmented models use the same 55 observed source inputs; no unavailable AngioCAD echo/ECG values are fabricated.

The full-55 local control's modest result also shows why “more features” is not automatically better. These fixed logistic controls are not the app's deployed nested-selector forest; their scores cannot establish an improvement over the live model. All populations have already been inspected in previous work, the bootstrap does not include model retraining uncertainty, and there is no compatible independent 55-input validation. **No model promotion or new live accuracy claim.**

Independent verification reproduced all 30 saved fold-model predictions, six pooled metric groups, row bootstrap, source/extra fingerprint exclusions and protected historical bytes. Reproduce using `python -m ml.full_input_transfer prepare`, `fit`, `evaluate` in a fresh output location; existing output is protected against overwrite. Verify the saved run using `python scripts/verify_full_input_transfer.py` with the local acquired data and private fits available.
