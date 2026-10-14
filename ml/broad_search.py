"""Broad, nested-CV model search; all artifacts stay under ml/experiments/broad_v2.

The search is exploratory on the already inspected 303-row cohort. The process
pool gives each candidate/outer-fold job a hard wall-time limit; a hung job can
be terminated without leaving a native estimator running in the parent.
"""
import os

# Set before spawned workers import numerical libraries. One worker plus these
# limits keeps the benchmark within the requested two-CPU ceiling.
for _thread_var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_var] = "1"

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import importlib.metadata
import json
import multiprocessing as mp
import platform
import time
import warnings
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from ml.evaluate import metrics
from ml.preprocessing import pipeline, check_features
from ml.schema import (
    ROOT, CATEGORICAL, FEATURES, TARGETS, SEED, digest, read_data, write_json,
)


SEEDS = [20261007, 20261108]
BASELINE_CANDIDATES = ["logistic_003", "logistic_03", "forest", "boosting"]
CANDIDATE_SPECS = {
    # This first block exactly reproduces ml/improvement.py's baseline search.
    "logistic_003": {"family": "logistic", "parameters": {"C": 0.03},
                     "explanation_feasibility": "Existing grouped Linear SHAP path; candidate artifact still needs exact additivity verification."},
    "logistic_03": {"family": "logistic", "parameters": {"C": 0.3},
                    "explanation_feasibility": "Existing grouped Linear SHAP path; candidate artifact still needs exact additivity verification."},
    "forest": {"family": "random_forest", "parameters": {
        "n_estimators": 120, "min_samples_leaf": 5, "max_features": "sqrt"},
        "explanation_feasibility": "Existing grouped Tree SHAP path; candidate artifact still needs exact additivity verification."},
    "boosting": {"family": "gradient_boosting", "parameters": {
        "n_estimators": 80, "learning_rate": 0.035, "max_depth": 2,
        "min_samples_leaf": 8},
        "explanation_feasibility": "Existing grouped Tree SHAP path; candidate artifact still needs exact additivity verification."},
    # A small, fixed configuration list. No settings are added after results.
    "elasticnet_l1_025": {"family": "elastic_net_logistic", "parameters": {
        "C": 0.1, "l1_ratio": 0.25, "solver": "saga", "max_iter": 5000},
        "explanation_feasibility": "Linear SHAP is plausible in the transformed feature space; candidate-specific grouped additivity must be verified."},
    "elasticnet_l1_075": {"family": "elastic_net_logistic", "parameters": {
        "C": 0.1, "l1_ratio": 0.75, "solver": "saga", "max_iter": 5000},
        "explanation_feasibility": "Linear SHAP is plausible in the transformed feature space; candidate-specific grouped additivity must be verified."},
    "shrinkage_lda": {"family": "shrinkage_lda", "parameters": {
        "solver": "lsqr", "shrinkage": "auto"},
        "explanation_feasibility": "A linear posterior-margin decomposition is plausible; new mapping and reconstruction checks are required."},
    "hist_gradient_boosting": {"family": "hist_gradient_boosting", "parameters": {
        "max_iter": 100, "learning_rate": 0.05, "max_leaf_nodes": 7,
        "l2_regularization": 2.0},
        "explanation_feasibility": "Tree SHAP support is unverified for this estimator; a model-agnostic fallback may be costly."},
    "extra_trees": {"family": "extra_trees", "parameters": {
        "n_estimators": 160, "min_samples_leaf": 4, "max_features": "sqrt"},
        "explanation_feasibility": "Tree SHAP is plausible after one-hot preprocessing; candidate-specific grouped additivity must be verified."},
    "rbf_svm_sigmoid": {"family": "rbf_svm_with_nested_sigmoid_calibration", "parameters": {
        "C": 1.0, "kernel": "rbf", "calibration": "sigmoid", "calibration_folds": 3},
        "explanation_feasibility": "Model-agnostic explanation of calibrated probabilities is possible but approximate and likely more expensive."},
    "mlp_small": {"family": "small_mlp", "parameters": {
        "hidden_layer_sizes": [16, 8], "alpha": 0.05, "max_iter": 350,
        "early_stopping": True, "n_iter_no_change": 20},
        "explanation_feasibility": "Model-agnostic explanation is possible but approximate and likely more expensive."},
    "catboost_native": {"family": "catboost_native_categorical", "parameters": {
        "iterations": 180, "depth": 4, "learning_rate": 0.03,
        "l2_leaf_reg": 6.0, "thread_count": 1},
        "explanation_feasibility": "Native Tree SHAP is plausible; the native-category artifact and original-field grouping need a new verified path."},
}
CANDIDATES = list(CANDIDATE_SPECS)
ENSEMBLE_MEMBERS = [
    "logistic_003", "boosting", "extra_trees", "rbf_svm_sigmoid", "catboost_native",
]
ENSEMBLE_NAME = "uniform_ensemble"
ENSEMBLE_EXPLANATION = "An explanation of the averaged probability needs a model-agnostic or verified member-composition path; no additive result is established here."
OUT = ROOT / "ml/experiments/broad_v2"
JOB_TIMEOUT_SECONDS = 120
STAGE_BUDGET_SECONDS = 3 * 60 * 60
SLOW_FIT_SECONDS = 15


class StageBudgetExceeded(RuntimeError):
    pass


def _preprocessed_pipeline(model):
    """Reuse the production preprocessing pipeline with a research estimator."""
    estimator = pipeline("logistic", 0.03)
    estimator.set_params(model=model)
    return estimator


def make_candidate(name: str, seed: int = SEED):
    """Create one fixed candidate; called only inside a CV training partition."""
    if name in ("logistic_003", "logistic_03"):
        return pipeline("logistic", 0.03 if name == "logistic_003" else 0.3)
    if name == "forest":
        return pipeline("forest")
    if name == "boosting":
        return pipeline("boosting")

    if name in ("elasticnet_l1_025", "elasticnet_l1_075"):
        ratio = 0.25 if name.endswith("025") else 0.75
        model = LogisticRegression(
            C=0.1, penalty="elasticnet", solver="saga", l1_ratio=ratio,
            max_iter=5000, tol=1e-3, random_state=SEED,
        )
        return _preprocessed_pipeline(model)
    if name == "shrinkage_lda":
        model = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
        return _preprocessed_pipeline(model)
    if name == "hist_gradient_boosting":
        model = HistGradientBoostingClassifier(
            max_iter=100, learning_rate=0.05, max_leaf_nodes=7,
            l2_regularization=2.0, early_stopping=False, random_state=SEED,
        )
        return _preprocessed_pipeline(model)
    if name == "extra_trees":
        model = ExtraTreesClassifier(
            n_estimators=160, min_samples_leaf=4, max_features="sqrt",
            n_jobs=1, random_state=SEED,
        )
        return _preprocessed_pipeline(model)
    if name == "rbf_svm_sigmoid":
        # Calibration CV is created on the current fit input. Therefore it is
        # nested inside each inner fit and never sees that fit's validation rows.
        base = _preprocessed_pipeline(SVC(C=1.0, kernel="rbf"))
        return CalibratedClassifierCV(
            estimator=base, method="sigmoid",
            cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=int(seed)),
            ensemble=True, n_jobs=1,
        )
    if name == "mlp_small":
        model = MLPClassifier(
            hidden_layer_sizes=(16, 8), activation="relu", solver="adam",
            alpha=0.05, batch_size=32, learning_rate_init=0.001,
            max_iter=350, early_stopping=True, validation_fraction=0.15,
            n_iter_no_change=20, random_state=SEED,
        )
        return _preprocessed_pipeline(model)
    if name == "catboost_native":
        from catboost import CatBoostClassifier
        return CatBoostClassifier(
            iterations=180, depth=4, learning_rate=0.03, l2_leaf_reg=6.0,
            loss_function="Logloss", verbose=False, allow_writing_files=False,
            thread_count=1, random_seed=SEED,
        )
    raise KeyError(name)


def _fit_predict_once(name, X_train, y_train, X_eval, seed):
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = make_candidate(name, seed)
        if name == "catboost_native":
            model.fit(X_train, y_train, cat_features=CATEGORICAL)
        else:
            model.fit(X_train, y_train)
        probabilities = np.asarray(model.predict_proba(X_eval)[:, 1], dtype=float)
    elapsed = time.perf_counter() - start
    if probabilities.ndim != 1 or not np.isfinite(probabilities).all():
        raise ValueError("Candidate returned non-finite or non-vector probabilities.")
    if ((probabilities < 0.0) | (probabilities > 1.0)).any():
        raise ValueError("Candidate returned probabilities outside [0, 1].")
    warning_messages = list(dict.fromkeys(str(w.message) for w in caught))[:3]
    return {
        "status": "ok",
        "probabilities": probabilities.tolist(),
        "seconds": float(elapsed),
        "slow": bool(elapsed > SLOW_FIT_SECONDS),
        "warning_count": len(caught),
        "warning_messages": warning_messages,
    }


def _candidate_outer_job(payload):
    """Fit one algorithm through an outer fold's inner splits and outer test."""
    name = payload["candidate"]
    results = {"candidate": name, "inner": [], "outer": None}
    with threadpool_limits(limits=1):
        for inner_fold, (fit_idx, valid_idx) in enumerate(payload["inner_splits"]):
            try:
                result = _fit_predict_once(
                    name,
                    payload["X_train"].iloc[fit_idx],
                    payload["y_train"].iloc[fit_idx],
                    payload["X_train"].iloc[valid_idx],
                    payload["calibration_seed"] + inner_fold,
                )
            except Exception as exc:
                result = {
                    "status": "failed", "error_type": type(exc).__name__,
                    "error": str(exc)[:600],
                }
            result["fold"] = int(inner_fold)
            result["row_indices"] = payload["train_indices"][valid_idx].tolist()
            results["inner"].append(result)
        try:
            results["outer"] = _fit_predict_once(
                name, payload["X_train"], payload["y_train"],
                payload["X_test"], payload["calibration_seed"] + 1000,
            )
        except Exception as exc:
            results["outer"] = {
                "status": "failed", "error_type": type(exc).__name__,
                "error": str(exc)[:600],
            }
    return results


class CandidatePool:
    """One persistent worker with a kill-and-restart hard timeout."""
    def __init__(self, timeout_seconds=JOB_TIMEOUT_SECONDS):
        self.context = mp.get_context("spawn")
        self.timeout_seconds = timeout_seconds
        self.pool = None
        self._start()

    def _start(self):
        self.pool = self.context.Pool(processes=1, maxtasksperchild=100)

    def _kill(self):
        if self.pool is not None:
            self.pool.terminate()
            self.pool.join()
            self.pool = None

    def run(self, payload, deadline):
        if time.monotonic() >= deadline:
            raise StageBudgetExceeded
        pending = self.pool.apply_async(_candidate_outer_job, (payload,))
        remaining = max(0.1, deadline-time.monotonic())
        wait_seconds = min(self.timeout_seconds, remaining)
        try:
            return pending.get(timeout=wait_seconds)
        except mp.TimeoutError:
            self._kill()
            self._start()
            stage_limited = remaining < self.timeout_seconds
            return {
                "candidate": payload["candidate"],
                "job_status": "stage_deadline_worker_terminated" if stage_limited else "hard_timeout_worker_terminated",
                "timeout_seconds": float(wait_seconds),
                "inner": [], "outer": None,
                "error": "Candidate job exceeded its wall-time limit; worker process was terminated.",
            }
        except Exception as exc:
            self._kill()
            self._start()
            return {
                "candidate": payload["candidate"],
                "job_status": "worker_failure",
                "inner": [], "outer": None,
                "error_type": type(exc).__name__, "error": str(exc)[:600],
            }

    def close(self):
        if self.pool is not None:
            self.pool.close()
            self.pool.join()
            self.pool = None


def calibration_metrics(y, probabilities):
    """Descriptive calibration summaries from held-out probabilities."""
    from sklearn.calibration import calibration_curve
    y = np.asarray(y, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    clipped = np.clip(p, 1e-6, 1.0-1e-6)
    logit = np.log(clipped/(1.0-clipped)).reshape(-1, 1)
    try:
        calibration_fit = LogisticRegression(C=1e6, max_iter=1000).fit(logit, y)
        intercept = float(calibration_fit.intercept_[0])
        slope = float(calibration_fit.coef_[0, 0])
    except Exception:
        intercept = None
        slope = None
    observed, predicted = calibration_curve(y, p, n_bins=5, strategy="quantile")
    edges = np.unique(np.quantile(p, np.linspace(0.0, 1.0, 6)))
    if len(edges) <= 2:
        ece = float(abs(float(p.mean()) - float(y.mean())))
    else:
        assignments = np.digitize(p, edges[1:-1], right=True)
        ece = 0.0
        for bin_id in np.unique(assignments):
            mask = assignments == bin_id
            ece += float(mask.mean()) * abs(float(p[mask].mean())-float(y[mask].mean()))
    return {
        "average_precision": float(average_precision_score(y, p)),
        "calibration_intercept": intercept,
        "calibration_slope": slope,
        "expected_calibration_error_5_quantile_bins": float(ece),
        "calibration_curve": {
            "mean_predicted": [float(v) for v in predicted],
            "observed_fraction": [float(v) for v in observed],
        },
    }


def summarize_predictions(y, probabilities):
    y = np.asarray(y, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    if len(y) == 0 or len(y) != len(p) or not np.isfinite(p).all():
        return None
    base = metrics(y, p)
    normalized = {}
    for key, value in base.items():
        if key == "confusion_matrix":
            normalized[key] = np.asarray(value).astype(int).tolist()
        else:
            normalized[key] = float(value)
    normalized.update(calibration_metrics(y, p))
    return normalized


def _mean_metric_dict(per_repeat):
    keys = [
        "accuracy", "precision", "recall", "f1", "roc_auc", "specificity",
        "brier", "log_loss", "average_precision", "calibration_intercept",
        "calibration_slope", "expected_calibration_error_5_quantile_bins",
    ]
    output = {}
    for key in keys:
        values = [item[key] for item in per_repeat if item is not None and item.get(key) is not None]
        output[key] = float(np.mean(values)) if values else None
    return output


def _fit_status(result):
    if result.get("job_status"):
        return result["job_status"]
    inner_ok = all(item.get("status") == "ok" for item in result.get("inner", []))
    outer_ok = result.get("outer", {}).get("status") == "ok"
    return "ok" if inner_ok and outer_ok else "partial_or_failed"


def _metrics_if_complete(y, values):
    values = pd.Series(values)
    if values.isna().any():
        return {"status": "incomplete_predictions", "available_rows": int(values.notna().sum()),
                "expected_rows": int(len(values)), "metrics": None}
    return {"status": "complete", "available_rows": int(len(values)),
            "expected_rows": int(len(values)), "metrics": summarize_predictions(y, values.to_numpy())}


def evaluate_target(target, df, pool, deadline, progress):
    X = df[FEATURES]
    check_features(X.columns)
    if set(X.columns) & set(TARGETS.values()):
        raise ValueError("Outcome leakage: target labels appeared in the model inputs.")
    y = (df[TARGETS[target]] == ("CAD" if target == "cad" else "Stenotic")).astype(int)
    target_result = {"target": target, "repeats": [], "complete": False}
    candidate_names = CANDIDATES + [ENSEMBLE_NAME]
    for repeat, outer_seed in enumerate(SEEDS):
        table = pd.DataFrame({"row_index": X.index, "y": y, "outer_fold": -1})
        for name in CANDIDATES:
            table[name] = np.nan
        for name in ("baseline_selector", "broad_selector", ENSEMBLE_NAME):
            table[name] = np.nan
        table["baseline_selected_candidate"] = ""
        table["broad_selected_candidate"] = ""
        outer_folds = []
        outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=outer_seed)
        for outer_fold, (train_idx, test_idx) in enumerate(outer_cv.split(X, y)):
            if time.monotonic() >= deadline:
                target_result["status"] = "stage_budget_exhausted"
                break
            X_train = X.iloc[train_idx]
            y_train = y.iloc[train_idx]
            inner_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=outer_seed+outer_fold)
            inner_splits = list(inner_cv.split(X_train, y_train))
            payload_common = {
                "X_train": X_train,
                "y_train": y_train,
                "X_test": X.iloc[test_idx],
                "train_indices": np.asarray(X_train.index),
                "inner_splits": [(a.astype(int), b.astype(int)) for a, b in inner_splits],
                "calibration_seed": int(outer_seed + outer_fold*100),
            }
            candidate_results = {}
            for name in CANDIDATES:
                payload = dict(payload_common, candidate=name)
                try:
                    candidate_results[name] = pool.run(payload, deadline)
                except StageBudgetExceeded:
                    candidate_results[name] = {
                        "candidate": name, "job_status": "not_run_stage_budget",
                        "inner": [], "outer": None,
                    }
                    for remaining in CANDIDATES[CANDIDATES.index(name)+1:]:
                        candidate_results[remaining] = {
                            "candidate": remaining, "job_status": "not_run_stage_budget",
                            "inner": [], "outer": None,
                        }
                    break
            candidate_scores = {}
            inner_detail = {}
            for name, result in candidate_results.items():
                aucs = []
                inner_records = []
                for item in result.get("inner", []):
                    row = {
                        "fold": item.get("fold"),
                        "row_indices": item.get("row_indices", []),
                        "status": item.get("status"),
                        "seconds": item.get("seconds"),
                        "slow": item.get("slow", False),
                        "warning_count": item.get("warning_count", 0),
                        "warning_messages": item.get("warning_messages", []),
                    }
                    if item.get("status") == "ok":
                        positions = next(b for a, b in inner_splits if len(b) and np.array_equal(X_train.index[b].to_numpy(), np.asarray(item["row_indices"])))
                        auc = float(roc_auc_score(y_train.iloc[positions], item["probabilities"]))
                        row["roc_auc"] = auc
                        row["probabilities"] = item["probabilities"]
                        aucs.append(auc)
                    else:
                        row["error_type"] = item.get("error_type")
                        row["error"] = item.get("error")
                    inner_records.append(row)
                complete_inner = len(inner_records) == 3 and len(aucs) == 3
                candidate_scores[name] = {
                    "status": result.get("job_status", "ok" if complete_inner else "inner_failure"),
                    "mean_auc": float(np.mean(aucs)) if complete_inner else None,
                    "fold_auc": aucs if complete_inner else [r.get("roc_auc") for r in inner_records],
                    "outer_status": result.get("outer", {}).get("status") if result.get("outer") else None,
                    "outer_seconds": result.get("outer", {}).get("seconds") if result.get("outer") else None,
                    "outer_slow": result.get("outer", {}).get("slow", False) if result.get("outer") else False,
                    "outer_warning_count": result.get("outer", {}).get("warning_count", 0) if result.get("outer") else 0,
                    "outer_error_type": result.get("outer", {}).get("error_type") if result.get("outer") else None,
                    "outer_error": result.get("outer", {}).get("error") if result.get("outer") else result.get("error"),
                    "job_status": result.get("job_status", "ok"),
                }
                inner_detail[name] = inner_records
            ensemble_inner_auc = []
            ensemble_inner_records = []
            members_complete = all(
                len(candidate_results.get(name, {}).get("inner", [])) == 3
                and all(x.get("status") == "ok" for x in candidate_results[name]["inner"])
                for name in ENSEMBLE_MEMBERS
            )
            if members_complete:
                member_folds = [candidate_results[n]["inner"] for n in ENSEMBLE_MEMBERS]
                for inner_fold in range(3):
                    row_sets = [m[inner_fold]["row_indices"] for m in member_folds]
                    if not all(rows == row_sets[0] for rows in row_sets[1:]):
                        raise ValueError("Ensemble member inner folds do not align.")
                    probs = np.mean(np.asarray([m[inner_fold]["probabilities"] for m in member_folds]), axis=0)
                    local_positions = next(b for a, b in inner_splits if np.array_equal(X_train.index[b].to_numpy(), np.asarray(row_sets[0])))
                    auc = float(roc_auc_score(y_train.iloc[local_positions], probs))
                    ensemble_inner_auc.append(auc)
                    ensemble_inner_records.append({
                        "fold": inner_fold, "row_indices": row_sets[0],
                        "probabilities": [float(v) for v in probs], "roc_auc": auc,
                    })
            candidate_scores[ENSEMBLE_NAME] = {
                "status": "ok" if len(ensemble_inner_auc) == 3 else "member_failure",
                "mean_auc": float(np.mean(ensemble_inner_auc)) if len(ensemble_inner_auc) == 3 else None,
                "fold_auc": ensemble_inner_auc,
                "members": ENSEMBLE_MEMBERS,
            }

            baseline_valid = [n for n in BASELINE_CANDIDATES if candidate_scores[n]["mean_auc"] is not None]
            broad_valid = [n for n in candidate_names if candidate_scores[n]["mean_auc"] is not None]
            selected = {
                "baseline_selector": max(baseline_valid, key=lambda n: candidate_scores[n]["mean_auc"]) if baseline_valid else None,
                "broad_selector": max(broad_valid, key=lambda n: candidate_scores[n]["mean_auc"]) if broad_valid else None,
            }
            outer_prediction_by_name = {}
            for name, result in candidate_results.items():
                outer = result.get("outer")
                if outer and outer.get("status") == "ok":
                    values = np.asarray(outer["probabilities"], dtype=float)
                    table.loc[test_idx, name] = values
                    outer_prediction_by_name[name] = values
                else:
                    outer_prediction_by_name[name] = None
            if all(outer_prediction_by_name.get(name) is not None for name in ENSEMBLE_MEMBERS):
                ensemble_outer = np.mean(np.asarray([outer_prediction_by_name[n] for n in ENSEMBLE_MEMBERS]), axis=0)
                table.loc[test_idx, ENSEMBLE_NAME] = ensemble_outer
                candidate_scores[ENSEMBLE_NAME]["outer_status"] = "ok"
            else:
                ensemble_outer = None
                candidate_scores[ENSEMBLE_NAME]["outer_status"] = "failed"
            prediction_for_choice = {
                **outer_prediction_by_name,
                ENSEMBLE_NAME: ensemble_outer,
            }
            for method, choice in selected.items():
                if choice is not None and prediction_for_choice.get(choice) is not None:
                    table.loc[test_idx, method] = prediction_for_choice[choice]
                    table.loc[test_idx, f"{method.replace('_selector', '')}_selected_candidate"] = choice
            table.loc[test_idx, "outer_fold"] = outer_fold

            outer_fold_record = {
                "fold": int(outer_fold),
                "train_indices": X.index[train_idx].tolist(),
                "test_indices": X.index[test_idx].tolist(),
                "inner_splits": [
                    {"train_indices": X.index[train_idx[a]].tolist(),
                     "test_indices": X.index[train_idx[b]].tolist()}
                    for a, b in inner_splits
                ],
                "candidate_scores": candidate_scores,
                "selected_by_inner_auc": selected,
                "inner_predictions": inner_detail,
                "ensemble_inner_predictions": ensemble_inner_records,
                "candidate_failures": {
                    name: {"job_status": record.get("job_status"),
                           "outer_error_type": candidate_scores[name].get("outer_error_type"),
                           "outer_error": candidate_scores[name].get("outer_error")}
                    for name, record in candidate_results.items()
                    if candidate_scores[name].get("status") != "ok" or candidate_scores[name].get("outer_status") != "ok"
                },
            }
            outer_folds.append(outer_fold_record)
            fold_path = OUT / f"{target}_repeat_{repeat+1}_fold_{outer_fold+1}.json"
            write_json(fold_path, outer_fold_record)
            progress["outer_folds_done"] += 1
            job_statuses = [result.get("job_status") for result in candidate_results.values()]
            progress["candidate_jobs_attempted"] += sum(status != "not_run_stage_budget" for status in job_statuses)
            progress["candidate_jobs_completed"] += sum(status is None for status in job_statuses)
            progress["candidate_jobs_terminated"] += sum(
                status in ("hard_timeout_worker_terminated", "stage_deadline_worker_terminated", "worker_failure")
                for status in job_statuses
            )
            progress["hard_timeouts"] += sum(
                status == "hard_timeout_worker_terminated" for status in job_statuses
            )
            progress["worker_failures"] += sum(status == "worker_failure" for status in job_statuses)
            progress["stage_deadline_terminations"] += sum(
                status == "stage_deadline_worker_terminated" for status in job_statuses
            )
            progress["budget_omissions"] += sum(
                status in ("not_run_stage_budget", "stage_deadline_worker_terminated")
                for status in job_statuses
            )
            progress["fit_failures"] += sum(
                sum(item.get("status") != "ok" for item in result.get("inner", []))
                + int(result.get("outer") is not None and result["outer"].get("status") != "ok")
                + int(result.get("job_status") == "worker_failure")
                for result in candidate_results.values()
            )
            progress["slow_fits"] += sum(
                sum(bool(item.get("slow", False)) for item in result.get("inner", []))
                + int(bool(result.get("outer") and result["outer"].get("slow", False)))
                for result in candidate_results.values()
            )
            progress["warnings"] += sum(
                sum(int(item.get("warning_count", 0)) for item in result.get("inner", []))
                + int(result.get("outer", {}).get("warning_count", 0))
                for result in candidate_results.values()
            )
            elapsed = time.monotonic() - progress["started"]
            print(f"{target} repeat {repeat+1} outer {outer_fold+1}/5: "
                  f"selected={selected}; elapsed={elapsed/60:.1f}m", flush=True)

        table.to_csv(OUT / f"{target}_repeat_{repeat+1}.csv", index=False)
        methods = {}
        for name in CANDIDATES + [ENSEMBLE_NAME, "baseline_selector", "broad_selector"]:
            methods[name] = _metrics_if_complete(y, table[name])
        repeat_record = {
            "repeat": repeat+1,
            "seed": outer_seed,
            "status": "complete" if len(outer_folds) == 5 and (table["outer_fold"] >= 0).all() else "partial",
            "outer_folds": outer_folds,
            "metrics": methods,
            "predictions_file": f"{target}_repeat_{repeat+1}.csv",
        }
        if repeat == 0:
            reference_path = ROOT / "ml/experiments/improvement_v1" / f"{target}_repeat_1.csv"
            if reference_path.exists() and table["baseline_selector"].notna().all():
                reference = pd.read_csv(reference_path)
                ref = reference.sort_values("row_index")["baseline"].to_numpy()
                current = table.sort_values("row_index")["baseline_selector"].to_numpy()
                max_abs = float(np.max(np.abs(ref-current)))
                repeat_record["baseline_repeat1_exact_reproduction"] = bool(np.array_equal(ref, current))
                repeat_record["baseline_repeat1_max_abs_probability_delta"] = max_abs
                repeat_record["baseline_repeat1_reference"] = str(reference_path.relative_to(ROOT))
            else:
                repeat_record["baseline_repeat1_exact_reproduction"] = None
                repeat_record["baseline_repeat1_reference"] = "unavailable"
        target_result["repeats"].append(repeat_record)
        write_json(OUT / f"{target}.json", target_result)
        if repeat_record["status"] != "complete":
            break

    target_result["complete"] = bool(
        len(target_result["repeats"]) == len(SEEDS)
        and all(r["status"] == "complete" for r in target_result["repeats"])
    )
    selected_counts = {"baseline_selector": Counter(), "broad_selector": Counter()}
    for repeat in target_result["repeats"]:
        for fold in repeat["outer_folds"]:
            for method in selected_counts:
                chosen = fold["selected_by_inner_auc"].get(method)
                if chosen:
                    selected_counts[method][chosen] += 1
    target_result["selection_frequency"] = {
        method: dict(sorted(counts.items())) for method, counts in selected_counts.items()
    }
    all_fold_records = [fold for repeat in target_result["repeats"] for fold in repeat["outer_folds"]]
    target_result["candidate_execution"] = {
        "hard_timeouts": sum(
            1 for fold in all_fold_records for item in fold["candidate_scores"].values()
            if "timeout" in str(item.get("job_status", ""))
        ),
        "failed_or_partial_candidate_outer_fits": sum(
            1 for fold in all_fold_records for item in fold["candidate_scores"].values()
            if item.get("status") != "ok" or item.get("outer_status") != "ok"
        ),
        "slow_individual_fits_over_seconds": SLOW_FIT_SECONDS,
        "note": "A full run can complete while an individual model family has a logged fit failure; each candidate metric exposes prediction completeness.",
    }
    target_result["candidate_comparison_to_baseline_selector"] = {}
    if target_result["complete"]:
        per_repeat_method_metrics = {
            method: [repeat["metrics"][method]["metrics"] for repeat in target_result["repeats"]]
            for method in CANDIDATES + [ENSEMBLE_NAME, "broad_selector"]
        }
        baseline_metrics = [r["metrics"]["baseline_selector"]["metrics"] for r in target_result["repeats"]]
        for method, values in per_repeat_method_metrics.items():
            complete = all(v is not None for v in values) and all(v is not None for v in baseline_metrics)
            deltas = None
            raw_gate = None
            quality_gate = None
            gate_details = None
            if complete:
                deltas = {}
                for metric in ("roc_auc", "brier", "log_loss", "calibration_slope", "calibration_intercept"):
                    deltas[metric] = [
                        (float(values[i][metric]-baseline_metrics[i][metric])
                         if values[i][metric] is not None and baseline_metrics[i][metric] is not None else None)
                        for i in range(len(SEEDS))
                    ]
                auc_deltas = deltas["roc_auc"]
                brier_deltas = deltas["brier"]
                mean_auc_gain = float(np.mean(auc_deltas))
                mean_brier_change = float(np.mean(brier_deltas))
                raw_gate = bool(
                    mean_auc_gain >= 0.015
                    and all(value >= 0.0 for value in auc_deltas)
                    and mean_brier_change <= 0.005
                )
                quality_gate = bool(
                    mean_brier_change <= -0.005
                    and all(value >= -0.01 for value in auc_deltas)
                )
                gate_details = {
                    "mean_two_repeat_auroc_gain": mean_auc_gain,
                    "mean_two_repeat_brier_change": mean_brier_change,
                    "per_repeat_auroc_gain": auc_deltas,
                    "per_repeat_brier_change": brier_deltas,
                }
            target_result["candidate_comparison_to_baseline_selector"][method] = {
                "metrics_mean_across_repeats": _mean_metric_dict(values) if complete else None,
                "per_repeat_deltas_vs_baseline": deltas,
                "preregistered_engineering_gate_inputs": gate_details,
                "raw_predictor_screen_pass": raw_gate,
                "probability_quality_screen_pass": quality_gate,
                "explanation_feasibility": (
                    ENSEMBLE_EXPLANATION if method == ENSEMBLE_NAME
                    else "Depends on the inner-selected candidate; see its explanation assessment."
                    if method == "broad_selector"
                    else CANDIDATE_SPECS.get(method, {}).get("explanation_feasibility")
                ),
                "interpretation": (
                    "nested broad-selector screen" if method == "broad_selector"
                    else "post-search fixed-candidate diagnostic; not an unbiased winner estimate"
                ) + "; thresholds are engineering screens only, not statistical or production-admission claims",
            }
    target_result["complete"] = bool(target_result["complete"])
    write_json(OUT / f"{target}.json", target_result)
    return target_result


def build_manifest(df):
    packages = [
        "numpy", "pandas", "scikit-learn", "scipy", "joblib", "openpyxl",
        "threadpoolctl", "catboost", "torch", "tabicl",
    ]
    versions = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    raw_path = ROOT / "data/raw/extention of Z-Alizadeh sani dataset.xlsx"
    production_metadata = ROOT / "models/metadata.json"
    preprocessing_path = ROOT / "ml/preprocessing.py"
    evaluate_path = ROOT / "ml/evaluate.py"
    schema_path = ROOT / "ml/schema.py"
    baseline_runner_path = ROOT / "ml/improvement.py"
    baseline_references = {}
    for target in TARGETS:
        reference = ROOT / "ml/experiments/improvement_v1" / f"{target}_repeat_1.csv"
        baseline_references[target] = {
            "path": str(reference.relative_to(ROOT)),
            "sha256": digest(reference) if reference.exists() else None,
        }
    return {
        "protocol": "docs/broad_search_protocol.md",
        "protocol_sha256": digest(ROOT / "docs/broad_search_protocol.md"),
        "runner_sha256": digest(Path(__file__)),
        "raw_sha256": digest(raw_path),
        "production_metadata_sha256": digest(production_metadata),
        "schema_sha256": digest(schema_path),
        "preprocessing_sha256": digest(preprocessing_path),
        "metrics_sha256": digest(evaluate_path),
        "baseline_runner_sha256": digest(baseline_runner_path),
        "baseline_repeat1_reference_files": baseline_references,
        "rows": int(len(df)),
        "features": FEATURES,
        "prohibited_target_columns": sorted(set(TARGETS.values())),
        "targets": list(TARGETS),
        "repeat_seeds": SEEDS,
        "outer_cv": "5-fold StratifiedKFold, shuffle=True, repeat seed 20261007/20261108",
        "inner_cv": "3-fold StratifiedKFold on each outer-training partition, seed repeat_seed + outer_fold",
        "baseline_candidates": BASELINE_CANDIDATES,
        "candidates": CANDIDATE_SPECS,
        "uniform_ensemble_members": ENSEMBLE_MEMBERS,
        "ensemble_rule": "fixed equal average of held-out probabilities; members and weights frozen before results",
        "selection_rule": "mean inner-fold ROC-AUC; stable candidate-list order breaks exact ties",
        "calibration_rule": "RBF SVC sigmoid CalibratedClassifierCV with 3-fold CV entirely inside each fit input",
        "hard_job_timeout_seconds": JOB_TIMEOUT_SECONDS,
        "stage_budget_seconds": STAGE_BUDGET_SECONDS,
        "worker_processes": 1,
        "thread_limit": 1,
        "python": platform.python_version(),
        "versions": versions,
        "warning": "Exploratory repeated internal validation of reused data; repeats reuse the same people and are not independent. No production model or metric is changed.",
    }


def main():
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(f"Preserving existing broad-v2 evidence; choose an empty output directory: {OUT}")
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_data()
    check_features(df[FEATURES].columns)
    manifest = build_manifest(df)
    manifest["started_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write_json(OUT / "run_manifest.json", manifest)
    progress = {
        "started": time.monotonic(), "outer_folds_done": 0,
        "candidate_jobs_attempted": 0, "candidate_jobs_completed": 0,
        "candidate_jobs_terminated": 0, "worker_failures": 0,
        "stage_deadline_terminations": 0,
        "hard_timeouts": 0, "fit_failures": 0, "slow_fits": 0,
        "warnings": 0, "budget_omissions": 0,
    }
    deadline = progress["started"] + STAGE_BUDGET_SECONDS
    results = {}
    pool = None
    fatal_error = None
    try:
        pool = CandidatePool()
        with threadpool_limits(limits=1):
            for target in TARGETS:
                if time.monotonic() >= deadline:
                    break
                results[target] = evaluate_target(target, df, pool, deadline, progress)
                if not results[target]["complete"]:
                    break
    except Exception as exc:
        fatal_error = {"type": type(exc).__name__, "message": str(exc)[:1000]}
    finally:
        if pool is not None:
            pool.close()
    complete = len(results) == len(TARGETS) and all(r["complete"] for r in results.values())
    manifest["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["elapsed_seconds"] = float(time.monotonic()-progress["started"])
    manifest["outer_folds_completed"] = progress["outer_folds_done"]
    manifest["candidate_jobs_attempted"] = progress["candidate_jobs_attempted"]
    manifest["candidate_jobs_completed"] = progress["candidate_jobs_completed"]
    manifest["candidate_jobs_terminated"] = progress["candidate_jobs_terminated"]
    manifest["candidate_worker_failures"] = progress["worker_failures"]
    manifest["stage_deadline_terminations"] = progress["stage_deadline_terminations"]
    manifest["candidate_job_timeouts"] = progress["hard_timeouts"]
    manifest["candidate_fit_failures"] = progress["fit_failures"]
    manifest["slow_individual_fits"] = progress["slow_fits"]
    manifest["estimator_warnings"] = progress["warnings"]
    manifest["stage_budget_omissions"] = progress["budget_omissions"]
    manifest["fatal_error"] = fatal_error
    manifest["run_complete"] = bool(complete)
    write_json(OUT / "run_manifest.json", manifest)
    summary = {
        "complete": bool(complete),
        "fatal_error": fatal_error,
        "warning": manifest["warning"],
        "targets": {
            target: {
                "complete": result["complete"],
                "candidate_execution": result.get("candidate_execution", {}),
                "selection_frequency": result.get("selection_frequency", {}),
                "candidate_comparison_to_baseline_selector": result.get("candidate_comparison_to_baseline_selector", {}),
                "repeats": [
                    {"repeat": r["repeat"], "seed": r["seed"], "status": r["status"],
                     "metrics": {name: value for name, value in r["metrics"].items()
                                 if name in ("baseline_selector", "broad_selector", ENSEMBLE_NAME)}}
                    for r in result["repeats"]
                ],
            }
            for target, result in results.items()
        },
    }
    write_json(OUT / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    if fatal_error:
        raise RuntimeError(f"Broad-v2 failed after saving partial evidence: {fatal_error['type']}: {fatal_error['message']}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
