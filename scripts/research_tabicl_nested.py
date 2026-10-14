"""Fixed, repeated outer-CV comparison of TabICLv2 with the saved baseline."""
from __future__ import annotations

import os

# Limit libraries that otherwise start their own pools before torch is imported.
for _thread_var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_var] = "1"

import hashlib
from importlib.metadata import version
import json
import platform
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
import sklearn
import torch
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold
from tabicl import TabICLClassifier
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.evaluate import metrics
from ml.preprocessing import check_features
from ml.schema import FEATURES, PROHIBITED, ROOT, TARGETS, digest, read_data, write_json


SEEDS = (20261007, 20261108)
OUTER_FOLDS = 5
THREADS = 2
N_ESTIMATORS = 8
BATCH_SIZE = 1
CHECKPOINT = ROOT / ".venv-tabicl" / "checkpoints" / "tabicl-classifier-v2-20260212.ckpt"
CHECKPOINT_SHA256 = "bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0"
RAW = ROOT / "data" / "raw" / "extention of Z-Alizadeh sani dataset.xlsx"
OUT = ROOT / "ml" / "experiments" / "tabicl_v2"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def model(seed: int) -> TabICLClassifier:
    return TabICLClassifier(
        n_estimators=N_ESTIMATORS,
        norm_methods=None,
        feat_shuffle_method="latin",
        class_shuffle_method="shift",
        outlier_threshold=4.0,
        softmax_temperature=0.9,
        average_logits=True,
        support_many_classes=True,
        batch_size=BATCH_SIZE,
        kv_cache=False,
        model_path=CHECKPOINT,
        allow_auto_download=False,
        checkpoint_version="tabicl-classifier-v2-20260212.ckpt",
        device="cpu",
        use_amp=False,
        use_fa3=False,
        offload_mode=False,
        random_state=seed,
        n_jobs=THREADS,
        verbose=False,
    )


def positive_probability(fitted: TabICLClassifier, X: pd.DataFrame) -> np.ndarray:
    probabilities = np.asarray(fitted.predict_proba(X), dtype=float)
    classes = np.asarray(fitted.classes_)
    positive = np.flatnonzero(classes == 1)
    if probabilities.shape != (len(X), len(classes)) or len(positive) != 1:
        raise ValueError(f"Unexpected TabICL class/probability output: {classes}, {probabilities.shape}")
    result = probabilities[:, int(positive[0])]
    if not np.isfinite(result).all() or ((result < 0) | (result > 1)).any():
        raise ValueError("TabICL returned invalid positive-class probabilities.")
    return result


def verify_baseline_reference(path: Path, X: pd.DataFrame, y: pd.Series, seed: int) -> tuple[pd.DataFrame, np.ndarray]:
    ref = pd.read_csv(path)
    if len(ref) != len(y) or not np.array_equal(ref["row_index"].to_numpy(), np.arange(len(y))):
        raise ValueError(f"Baseline row order/length mismatch in {path.name}.")
    if not np.array_equal(ref["y"].to_numpy(dtype=int), y.to_numpy(dtype=int)):
        raise ValueError(f"Baseline labels differ from the current source in {path.name}.")
    if ref["baseline"].isna().any() or not np.isfinite(ref["baseline"].to_numpy(dtype=float)).all():
        raise ValueError(f"Baseline probabilities are incomplete in {path.name}.")

    expected_fold = np.full(len(y), -1, dtype=int)
    for fold, (_, test) in enumerate(StratifiedKFold(OUTER_FOLDS, shuffle=True, random_state=seed).split(X, y)):
        expected_fold[test] = fold
    if not np.array_equal(ref["fold"].to_numpy(dtype=int), expected_fold):
        raise ValueError(f"Baseline outer folds do not match the frozen seed {seed} in {path.name}.")
    return ref, expected_fold


def evaluate_target(target: str, df: pd.DataFrame) -> dict:
    X = df[FEATURES].copy()
    check_features(X.columns)
    if set(X.columns) & PROHIBITED:
        raise ValueError("Target columns entered X.")
    positive_label = "CAD" if target == "cad" else "Stenotic"
    y = (df[TARGETS[target]] == positive_label).astype(int)
    if y.nunique() != 2:
        raise ValueError(f"Target {target} is not binary in the current source.")

    repeats = []
    for repeat_index, seed in enumerate(SEEDS, start=1):
        reference_path = ROOT / "ml" / "experiments" / "improvement_v1" / f"{target}_repeat_{repeat_index}.csv"
        ref, expected_fold = verify_baseline_reference(reference_path, X, y, seed)
        row_probabilities = np.full(len(y), np.nan, dtype=float)
        fold_records = []

        with threadpool_limits(limits=1):
            for fold, (train, test) in enumerate(StratifiedKFold(OUTER_FOLDS, shuffle=True, random_state=seed).split(X, y)):
                fold_seed = int(seed + fold)
                estimator = model(fold_seed)
                started = time.perf_counter()
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    estimator.fit(X.iloc[train], y.iloc[train])
                    probabilities = positive_probability(estimator, X.iloc[test])
                elapsed = time.perf_counter() - started
                row_probabilities[test] = probabilities
                fold_records.append({
                    "fold": fold,
                    "model_random_state": fold_seed,
                    "train_indices": train.tolist(),
                    "test_indices": test.tolist(),
                    "train_rows": int(len(train)),
                    "test_rows": int(len(test)),
                    "fit_predict_seconds": round(float(elapsed), 4),
                    "warning_messages": list(dict.fromkeys(str(w.message) for w in caught))[:5],
                    "peak_process_rss_mib_after_fold": round(psutil.Process().memory_info().rss / (1024 ** 2), 2),
                })
                del estimator, probabilities
                print(target, f"repeat={repeat_index}", f"fold={fold + 1}/{OUTER_FOLDS}",
                      f"train={len(train)}", f"test={len(test)}", f"seconds={elapsed:.1f}", flush=True)

        if not np.isfinite(row_probabilities).all():
            raise ValueError(f"Incomplete outer predictions for {target}, repeat {repeat_index}.")
        if not np.array_equal(expected_fold, ref["fold"].to_numpy(dtype=int)):
            raise AssertionError("The baseline fold identity changed after verification.")

        baseline_p = ref["baseline"].to_numpy(dtype=float)
        tabicl_metrics = metrics(y.to_numpy(dtype=int), row_probabilities)
        baseline_metrics = metrics(y.to_numpy(dtype=int), baseline_p)
        tabicl_metrics["average_precision"] = float(average_precision_score(y, row_probabilities))
        baseline_metrics["average_precision"] = float(average_precision_score(y, baseline_p))

        out = pd.DataFrame({
            "row_index": np.arange(len(y), dtype=int),
            "y": y.to_numpy(dtype=int),
            "fold": expected_fold,
            "baseline": baseline_p,
            "tabicl_v2": row_probabilities,
        })
        out.to_csv(OUT / f"{target}_repeat_{repeat_index}.csv", index=False, float_format="%.12g")
        repeats.append({
            "repeat": repeat_index,
            "seed": seed,
            "baseline_reference": str(reference_path.relative_to(ROOT)),
            "baseline_reference_sha256": sha256(reference_path),
            "baseline_metrics": baseline_metrics,
            "tabicl_metrics": tabicl_metrics,
            "deltas_tabicl_minus_baseline": {
                "roc_auc": float(tabicl_metrics["roc_auc"] - baseline_metrics["roc_auc"]),
                "brier": float(tabicl_metrics["brier"] - baseline_metrics["brier"]),
            },
            "folds": fold_records,
        })
        write_json(OUT / f"{target}.json", {
            "target": target,
            "positive_label": positive_label,
            "repeats": repeats,
            "complete": False,
        })

    auc_deltas = [repeat["deltas_tabicl_minus_baseline"]["roc_auc"] for repeat in repeats]
    brier_deltas = [repeat["deltas_tabicl_minus_baseline"]["brier"] for repeat in repeats]
    mean_auc_delta = float(np.mean(auc_deltas))
    mean_brier_delta = float(np.mean(brier_deltas))
    summary = {
        "target": target,
        "mean_metrics": {
            key: {
                "baseline": float(np.mean([r["baseline_metrics"][key] for r in repeats])),
                "tabicl_v2": float(np.mean([r["tabicl_metrics"][key] for r in repeats])),
            }
            for key in ("roc_auc", "average_precision", "brier", "log_loss", "accuracy", "precision", "recall", "specificity", "f1")
        },
        "repeat_deltas": {
            "roc_auc": auc_deltas,
            "brier_tabicl_minus_baseline": brier_deltas,
        },
        "raw_predictor_screen": {
            "rule": "mean AUROC gain >= 0.015; neither repeat AUROC lower; mean Brier increase <= 0.005",
            "eligible": bool(mean_auc_delta >= 0.015 and min(auc_deltas) >= 0.0 and mean_brier_delta <= 0.005),
        },
        "probability_quality_screen": {
            "rule": "mean Brier improvement >= 0.005; neither repeat AUROC decrease > 0.01",
            "eligible": bool(mean_brier_delta <= -0.005 and min(auc_deltas) >= -0.01),
        },
        "repeats": repeats,
        "complete": True,
    }
    write_json(OUT / f"{target}.json", summary)
    return summary


def main() -> None:
    torch.set_num_threads(THREADS)
    torch.set_num_interop_threads(1)
    if not CHECKPOINT.is_file() or sha256(CHECKPOINT) != CHECKPOINT_SHA256:
        raise ValueError("The pinned official TabICLv2 checkpoint is missing or has the wrong SHA-256.")
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(f"Refusing to overwrite existing experiment evidence in {OUT}.")

    df = read_data()
    X = df[FEATURES]
    if X.shape != (303, 55):
        raise ValueError(f"Unexpected feature-only input shape: {X.shape}.")
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "protocol_sha256": digest(ROOT / "docs" / "tabicl_protocol.md"),
        "runner_sha256": digest(Path(__file__)),
        "schema_sha256": digest(ROOT / "ml" / "schema.py"),
        "preprocessing_sha256": digest(ROOT / "ml" / "preprocessing.py"),
        "metrics_sha256": digest(ROOT / "ml" / "evaluate.py"),
        "raw_sha256": digest(RAW),
        "checkpoint": {
            "repository": "https://huggingface.co/jingang/TabICL",
            "filename": CHECKPOINT.name,
            "bytes": CHECKPOINT.stat().st_size,
            "sha256": sha256(CHECKPOINT),
            "license": "BSD-3-Clause (official model repository metadata)",
        },
        "runtime": {
            "python": platform.python_version(),
            "tabicl": version("tabicl"),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "cpu_threads": THREADS,
            "cuda_available": bool(torch.cuda.is_available()),
            "host_ram_gib": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        },
        "seeds": list(SEEDS),
        "outer_folds": OUTER_FOLDS,
        "targets": list(TARGETS),
        "inputs": FEATURES,
        "prohibited_inputs": sorted(PROHIBITED),
        "parameters": {
            "n_estimators": N_ESTIMATORS,
            "batch_size": BATCH_SIZE,
            "device": "cpu",
            "n_jobs": THREADS,
            "random_state": "outer_seed + outer_fold",
            "norm_methods": None,
            "feat_shuffle_method": "latin",
            "class_shuffle_method": "shift",
            "outlier_threshold": 4.0,
            "softmax_temperature": 0.9,
            "average_logits": True,
            "support_many_classes": True,
            "kv_cache": False,
            "allow_auto_download": False,
            "use_amp": False,
            "use_fa3": False,
            "offload_mode": False,
        },
        "baseline_source": "ml/experiments/improvement_v1/{target}_repeat_{1,2}.csv, baseline column; row/y/fold checked against regenerated splits",
        "warning": "Repeated internal validation of a previously inspected 303-row cohort; TabICLv2's authors have not tested generalization below 300 training rows; not external validation.",
        "complete": False,
    }
    write_json(OUT / "run_manifest.json", manifest)

    results = {}
    for target in TARGETS:
        results[target] = evaluate_target(target, df)
    write_json(OUT / "summary.json", {
        target: {key: result[key] for key in ("mean_metrics", "repeat_deltas", "raw_predictor_screen", "probability_quality_screen", "complete")}
        for target, result in results.items()
    })
    manifest["complete"] = True
    write_json(OUT / "run_manifest.json", manifest)
    print(json.dumps(json.loads((OUT / "summary.json").read_text(encoding="utf-8")), indent=2), flush=True)


if __name__ == "__main__":
    main()
