"""Build and verify the isolated LCX HistGradientBoosting research artifact.

This saves an opt-in candidate only. It does not write or register production
models. The nested held-out predictions referenced by its manifest are the
search evidence; fitting on all 303 rows is only for a usable local artifact.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from ml.explain import explain, make_explainer  # noqa: E402
from ml.preprocessing import check_features, pipeline  # noqa: E402
from ml.schema import FEATURES, SEED, TARGETS, digest, read_data, write_json  # noqa: E402

CANDIDATE_ID = "histgb_lcx_v2"
TARGET = "lcx"
OUT = Path(__file__).resolve().parent
ARTIFACT_PATH = OUT / "histgb_lcx.joblib"
VALIDATION_PATH = OUT / "validation.json"
MANIFEST_PATH = OUT / "manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric_snapshot(metrics: dict) -> dict:
    keys = (
        "roc_auc", "brier", "log_loss", "recall", "specificity", "precision",
        "f1", "calibration_intercept", "calibration_slope",
        "expected_calibration_error_5_quantile_bins",
    )
    return {key: float(metrics[key]) for key in keys}


def verify_explanations(artifact: dict, X: pd.DataFrame) -> dict:
    explainer, unit = make_explainer(artifact)
    if unit != "log-odds":
        raise AssertionError(f"Unexpected HistGradientBoosting explanation unit: {unit}")

    started = time.perf_counter()
    explanations = [explain(artifact, explainer, unit, X.iloc[[i]]) for i in range(len(X))]
    all_rows_seconds = time.perf_counter() - started
    residuals = np.asarray([item["additivity_error"] for item in explanations], dtype=float)
    if len(explanations) != len(X) or not np.isfinite(residuals).all() or residuals.max(initial=0.0) > 1e-4:
        raise AssertionError("One or more full-cohort SHAP explanations failed reconstruction.")

    expected = artifact["pipeline"].decision_function(X)
    explained = np.asarray([item["output_value"] for item in explanations], dtype=float)
    output_delta = float(np.max(np.abs(expected - explained)))
    if output_delta > 1e-12:
        raise AssertionError(f"SHAP output differs from the model decision function by {output_delta}.")

    # Synthetic missing-field and out-of-training-range inputs exercise the
    # same pipeline and explanation code used by the application.
    null_case = X.iloc[[0]].copy()
    null_case["Age"] = null_case["Age"].astype(float)
    null_case.loc[:, "Age"] = np.nan
    null_case["Sex"] = null_case["Sex"].astype(object)
    null_case.loc[:, "Sex"] = np.nan

    range_case = X.iloc[[1]].copy()
    range_case["Age"] = range_case["Age"].astype(float)
    range_case["BMI"] = range_case["BMI"].astype(float)
    range_case.loc[:, "Age"] = float(X["Age"].max()) + 25.0
    range_case.loc[:, "BMI"] = float(X["BMI"].min()) - 10.0

    synthetic = []
    for label, frame in (("null_numeric_and_category", null_case), ("numeric_out_of_range", range_case)):
        if list(frame.columns) != FEATURES:
            raise AssertionError(f"{label} input columns differ from the feature contract.")
        result = explain(artifact, explainer, unit, frame)
        probability = float(artifact["pipeline"].predict_proba(frame)[0, 1])
        if not np.isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise AssertionError(f"{label} returned an invalid probability.")
        synthetic.append({
            "case": label,
            "probability": probability,
            "output_value": float(result["output_value"]),
            "additivity_error": float(result["additivity_error"]),
            "finite_grouped_factors": bool(all(np.isfinite(f["contribution"]) for f in result["factors"])),
        })

    repeated = explain(artifact, explainer, unit, X.iloc[[0]])
    if explanations[0] != repeated:
        raise AssertionError("Repeated explanation was not deterministic.")

    return {
        "inference_verified": True,
        "explanation_method": "existing ml.explain TreeSHAP path-dependent raw-margin path",
        "explanation_unit": unit,
        "full_cohort_rows_reconstructed": len(explanations),
        "full_cohort_max_additivity_error": float(residuals.max(initial=0.0)),
        "full_cohort_max_explained_vs_decision_function_delta": output_delta,
        "full_cohort_explanations_seconds": float(all_rows_seconds),
        "full_cohort_mean_explanation_ms_per_row": float(1000.0 * all_rows_seconds / len(X)),
        "repeated_explanation_exactly_equal": True,
        "synthetic_cases": synthetic,
        "note": "All-cohort explanation is a fidelity check on the fitted artifact, not held-out performance evidence.",
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_data()
    X = df[FEATURES]
    check_features(X.columns)
    y = (df[TARGETS[TARGET]] == "Stenotic").astype(int)
    if len(df) != 303 or len(X) != len(y):
        raise ValueError(f"Unexpected source size: {len(df)} rows")

    estimator = HistGradientBoostingClassifier(
        max_iter=100, learning_rate=0.05, max_leaf_nodes=7,
        l2_regularization=2.0, early_stopping=False, random_state=SEED,
    )
    fitted = pipeline("logistic", 0.03)
    fitted.set_params(model=estimator)
    with threadpool_limits(limits=1):
        started = time.perf_counter()
        fitted.fit(X, y)
        fit_seconds = time.perf_counter() - started
        transformed = fitted.named_steps["preprocess"].transform(X)
        rng = np.random.default_rng(SEED)
        background = transformed[rng.choice(len(X), size=100, replace=False)]
        artifact = {
            "pipeline": fitted,
            "background": background,
            "features": FEATURES,
            "target": TARGET,
            "kind": "hist_gradient_boosting",
        }
        joblib.dump(artifact, ARTIFACT_PATH, compress=3)
        artifact = joblib.load(ARTIFACT_PATH)
        if artifact["target"] != TARGET or artifact["kind"] != "hist_gradient_boosting" or artifact["features"] != FEATURES:
            raise AssertionError("Serialized artifact does not satisfy the candidate contract.")

        started = time.perf_counter()
        all_probabilities = fitted.predict_proba(X)[:, 1]
        prediction_seconds = time.perf_counter() - started

        # Fit a second identical pipeline and compare probabilities exactly.
        second = pipeline("logistic", 0.03)
        second.set_params(model=HistGradientBoostingClassifier(
            max_iter=100, learning_rate=0.05, max_leaf_nodes=7,
            l2_regularization=2.0, early_stopping=False, random_state=SEED,
        ))
        second.fit(X, y)
        repeated_probabilities = second.predict_proba(X)[:, 1]
        deterministic_delta = float(np.max(np.abs(all_probabilities - repeated_probabilities)))
        if deterministic_delta != 0.0:
            raise AssertionError(f"Repeated model fits differ by {deterministic_delta}.")

        validation = verify_explanations(artifact, X)

    validation.update({
        "fit_rows": int(len(X)),
        "fit_seconds": float(fit_seconds),
        "batch_prediction_rows": int(len(X)),
        "batch_prediction_seconds": float(prediction_seconds),
        "mean_batch_prediction_ms_per_row": float(1000.0 * prediction_seconds / len(X)),
        "repeat_fit_probability_max_delta": deterministic_delta,
        "artifact_probability_range": [
            float(np.min(all_probabilities)),
            float(np.max(all_probabilities)),
        ],
        "sklearn_version": importlib.metadata.version("scikit-learn"),
        "shap_version": importlib.metadata.version("shap"),
        "thread_limit": 1,
    })
    write_json(VALIDATION_PATH, validation)

    target_result_path = ROOT / "ml/experiments/broad_v2/lcx.json"
    target_result = json.loads(target_result_path.read_text(encoding="utf-8"))
    fixed = target_result["candidate_comparison_to_baseline_selector"]["hist_gradient_boosting"]
    if not (fixed["raw_predictor_screen_pass"] and fixed["probability_quality_screen_pass"]):
        raise AssertionError("Candidate no longer passes both frozen eligibility screens.")

    prior_run = json.loads((ROOT / "ml/experiments/broad_v2/run_manifest.json").read_text(encoding="utf-8"))
    production_metadata_path = ROOT / "models/metadata.json"
    production_metadata = json.loads(production_metadata_path.read_text(encoding="utf-8"))
    production_lcx_path = ROOT / "models/lcx.joblib"
    production_metadata_hash = digest(production_metadata_path)
    production_lcx_hash = digest(production_lcx_path)
    if production_metadata_hash != prior_run["production_metadata_sha256"]:
        raise AssertionError("Production metadata differs from the frozen search manifest.")
    if production_lcx_hash != production_metadata["artifacts"][TARGET]["sha256"]:
        raise AssertionError("Production LCX artifact no longer matches its production metadata.")

    repeat_evidence = []
    for repeat in target_result["repeats"]:
        candidate = repeat["metrics"]["hist_gradient_boosting"]["metrics"]
        baseline = repeat["metrics"]["baseline_selector"]["metrics"]
        repeat_evidence.append({
            "repeat": int(repeat["repeat"]),
            "seed": int(repeat["seed"]),
            "rows": int(repeat["metrics"]["hist_gradient_boosting"]["available_rows"]),
            "candidate": metric_snapshot(candidate),
            "baseline_selector": metric_snapshot(baseline),
            "delta_candidate_minus_baseline": {
                key: float(candidate[key] - baseline[key])
                for key in ("roc_auc", "brier", "log_loss", "calibration_intercept", "calibration_slope")
            },
        })

    evidence_files = []
    for rel in (
        "ml/experiments/broad_v2/lcx.json",
        "ml/experiments/broad_v2/lcx_repeat_1.csv",
        "ml/experiments/broad_v2/lcx_repeat_2.csv",
        "ml/experiments/improvement_v1/lcx_repeat_1.csv",
    ):
        path = ROOT / rel
        evidence_files.append({"path": rel, "sha256": sha256(path)})

    artifact_hash = sha256(ARTIFACT_PATH)
    manifest = {
        "candidate_id": CANDIDATE_ID,
        "candidate_status": "isolated_research_candidate_not_registered_or_promoted",
        "target": TARGET,
        "feature_names": FEATURES,
        "artifact": {"file": ARTIFACT_PATH.name, "sha256": artifact_hash},
        "inference_verified": bool(validation["inference_verified"]),
        "validation_file": {"file": VALIDATION_PATH.name, "sha256": sha256(VALIDATION_PATH)},
        "model": {
            "family": "HistGradientBoostingClassifier",
            "parameters": {
                "max_iter": 100, "learning_rate": 0.05, "max_leaf_nodes": 7,
                "l2_regularization": 2.0, "early_stopping": False,
                "random_state": SEED,
            },
            "preprocessing": "Existing ml.preprocessing.pipeline preprocessing, fitted on all 303 source records for the candidate artifact only.",
            "background_rows": 100,
            "background_sampling": "default_rng(seed=20261007), without replacement from transformed full-cohort inputs",
        },
        "source": {
            "dataset": "data/raw/extention of Z-Alizadeh sani dataset.xlsx",
            "dataset_sha256": digest(ROOT / "data/raw/extention of Z-Alizadeh sani dataset.xlsx"),
            "rows": int(len(df)),
            "target_column": TARGETS[TARGET],
            "positive_label": "Stenotic",
            "excluded_outcomes": ["Cath", "LAD", "LCX", "RCA"],
            "feature_allowlist_path": "ml/schema.py::FEATURES",
            "training_uses_only_features": True,
        },
        "eligibility": {
            "raw_predictor_screen_pass": bool(fixed["raw_predictor_screen_pass"]),
            "probability_quality_screen_pass": bool(fixed["probability_quality_screen_pass"]),
            "thresholds_path": "docs/broad_search_protocol.md",
            "status_note": "Post-search fixed-candidate diagnostic; engineering gates are not statistical, clinical, external-validation, or production approval criteria.",
        },
        "production_baseline_unchanged": {
            "metadata_path": "models/metadata.json",
            "metadata_sha256": production_metadata_hash,
            "lcx_artifact_path": "models/lcx.joblib",
            "lcx_artifact_sha256": production_lcx_hash,
            "matches_frozen_broad_search_metadata": True,
            "matches_production_metadata_artifact_hash": True,
        },
        "nested_heldout_evidence": {
            "evidence_role": "Two-repeat nested repeated-CV row predictions, source-matched to baseline_selector on identical rows/folds.",
            "protocol_path": "docs/broad_search_protocol.md",
            "protocol_sha256": digest(ROOT / "docs/broad_search_protocol.md"),
            "runner_path": "ml/broad_search.py",
            "runner_sha256": digest(ROOT / "ml/broad_search.py"),
            "repeated_results": repeat_evidence,
            "mean_two_repeat_auroc_gain": float(fixed["preregistered_engineering_gate_inputs"]["mean_two_repeat_auroc_gain"]),
            "mean_two_repeat_brier_change": float(fixed["preregistered_engineering_gate_inputs"]["mean_two_repeat_brier_change"]),
            "per_repeat_auroc_gain": fixed["preregistered_engineering_gate_inputs"]["per_repeat_auroc_gain"],
            "per_repeat_brier_change": fixed["preregistered_engineering_gate_inputs"]["per_repeat_brier_change"],
            "baseline_reference": "The primary comparison baseline_selector was selected using inner CV and predicted on the same outer held-out rows in broad_v2; improvement_v1/lcx_repeat_1.csv is additionally retained as the exact-repeat-one baseline provenance check.",
            "files": evidence_files,
            "post_search_caveat": "The fixed family/configuration passed after a broad family scan on reused data. Its metrics are exploratory post-search diagnostics, not an unbiased winner estimate or an independent test.",
        },
        "fit_environment": {
            "python": platform.python_version(),
            "numpy": importlib.metadata.version("numpy"),
            "pandas": importlib.metadata.version("pandas"),
            "scikit_learn": importlib.metadata.version("scikit-learn"),
            "shap": importlib.metadata.version("shap"),
            "joblib": importlib.metadata.version("joblib"),
            "cpu_thread_limit": 1,
            "fit_seconds": float(fit_seconds),
        },
        "implementation_hashes": {
            "build_script": sha256(Path(__file__).resolve()),
            "preprocessing": digest(ROOT / "ml/preprocessing.py"),
            "explanation": digest(ROOT / "ml/explain.py"),
            "metrics": digest(ROOT / "ml/evaluate.py"),
        },
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    write_json(MANIFEST_PATH, manifest)
    print(json.dumps({
        "candidate_id": CANDIDATE_ID,
        "artifact": str(ARTIFACT_PATH.relative_to(ROOT)),
        "sha256": artifact_hash,
        "inference_verified": manifest["inference_verified"],
        "full_cohort_max_additivity_error": validation["full_cohort_max_additivity_error"],
        "validation_file": str(VALIDATION_PATH.relative_to(ROOT)),
        "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
