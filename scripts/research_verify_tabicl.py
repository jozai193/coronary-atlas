"""Recompute and validate saved TabICLv2 evidence without refitting models."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.evaluate import metrics
from ml.schema import FEATURES, PROHIBITED, ROOT, TARGETS, digest, read_data


OUT = ROOT / "ml" / "experiments" / "tabicl_v2"
SEEDS = (20261007, 20261108)


def close(a: float, b: float) -> bool:
    return bool(np.isclose(a, b, rtol=0.0, atol=1e-12))


def main() -> None:
    manifest = json.loads((OUT / "run_manifest.json").read_text(encoding="utf-8"))
    if not manifest["complete"]:
        raise ValueError("Run manifest is incomplete.")
    hash_checks = {
        "protocol_sha256": ROOT / "docs" / "tabicl_protocol.md",
        "runner_sha256": ROOT / "scripts" / "research_tabicl_nested.py",
        "schema_sha256": ROOT / "ml" / "schema.py",
        "preprocessing_sha256": ROOT / "ml" / "preprocessing.py",
        "metrics_sha256": ROOT / "ml" / "evaluate.py",
        "raw_sha256": ROOT / "data" / "raw" / "extention of Z-Alizadeh sani dataset.xlsx",
    }
    for field, path in hash_checks.items():
        if digest(path) != manifest[field]:
            raise ValueError(f"Current {path.relative_to(ROOT)} does not match the recorded {field}.")
    checkpoint = ROOT / ".venv-tabicl" / "checkpoints" / manifest["checkpoint"]["filename"]
    if digest(checkpoint) != manifest["checkpoint"]["sha256"]:
        raise ValueError("Checkpoint hash mismatch.")

    df = read_data()
    X = df[FEATURES]
    if set(X.columns) & PROHIBITED:
        raise ValueError("A label appears in the feature allowlist.")
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    for target, outcome in TARGETS.items():
        target_file = json.loads((OUT / f"{target}.json").read_text(encoding="utf-8"))
        if not target_file["complete"] or len(target_file["repeats"]) != 2:
            raise ValueError(f"Incomplete target artifact: {target}.")
        y = (df[outcome] == ("CAD" if target == "cad" else "Stenotic")).astype(int).to_numpy()
        for repeat_index, seed in enumerate(SEEDS, start=1):
            reference_path = ROOT / "ml" / "experiments" / "improvement_v1" / f"{target}_repeat_{repeat_index}.csv"
            repeat = target_file["repeats"][repeat_index - 1]
            if repeat["seed"] != seed or digest(reference_path) != repeat["baseline_reference_sha256"]:
                raise ValueError(f"Baseline source/seed mismatch: {target} repeat {repeat_index}.")
            saved = pd.read_csv(OUT / f"{target}_repeat_{repeat_index}.csv")
            baseline = pd.read_csv(reference_path)
            expected_fold = np.full(len(y), -1, dtype=int)
            for fold, (_, test) in enumerate(StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y)):
                expected_fold[test] = fold
            if not np.array_equal(saved["row_index"].to_numpy(), np.arange(len(y))):
                raise ValueError(f"Row ordering mismatch: {target} repeat {repeat_index}.")
            if not np.array_equal(saved["y"].to_numpy(dtype=int), y):
                raise ValueError(f"Current source labels mismatch: {target} repeat {repeat_index}.")
            if not np.array_equal(saved["y"].to_numpy(), baseline["y"].to_numpy()):
                raise ValueError(f"Baseline labels mismatch: {target} repeat {repeat_index}.")
            if not np.array_equal(saved["fold"].to_numpy(dtype=int), expected_fold):
                raise ValueError(f"Saved fold mismatch: {target} repeat {repeat_index}.")
            if not np.array_equal(saved["fold"].to_numpy(), baseline["fold"].to_numpy()):
                raise ValueError(f"Baseline fold mismatch: {target} repeat {repeat_index}.")
            p = saved["tabicl_v2"].to_numpy(dtype=float)
            if not np.isfinite(p).all() or ((p < 0.0) | (p > 1.0)).any():
                raise ValueError(f"Invalid probability: {target} repeat {repeat_index}.")
            computed = metrics(y, p)
            computed["average_precision"] = float(average_precision_score(y, p))
            for metric_name, value in computed.items():
                if isinstance(value, (list, tuple)):
                    if value != repeat["tabicl_metrics"][metric_name]:
                        raise ValueError(f"Metric mismatch {target}/{repeat_index}/{metric_name}.")
                elif not close(float(value), float(repeat["tabicl_metrics"][metric_name])):
                    raise ValueError(f"Metric mismatch {target}/{repeat_index}/{metric_name}.")
            if len(repeat["folds"]) != 5 or sum(f["test_rows"] for f in repeat["folds"]) != 303:
                raise ValueError(f"Fold coverage mismatch: {target} repeat {repeat_index}.")

        entry = summary[target]
        auc_deltas = entry["repeat_deltas"]["roc_auc"]
        brier_deltas = entry["repeat_deltas"]["brier_tabicl_minus_baseline"]
        mean_auc = float(np.mean(auc_deltas))
        mean_brier = float(np.mean(brier_deltas))
        raw_pass = mean_auc >= 0.015 and min(auc_deltas) >= 0.0 and mean_brier <= 0.005
        quality_pass = mean_brier <= -0.005 and min(auc_deltas) >= -0.01
        if entry["raw_predictor_screen"]["eligible"] != raw_pass:
            raise ValueError(f"Raw screen mismatch: {target}.")
        if entry["probability_quality_screen"]["eligible"] != quality_pass:
            raise ValueError(f"Quality screen mismatch: {target}.")
        print(f"{target}: saved rows, labels, folds, metrics, and screens verified; raw={raw_pass}, quality={quality_pass}")
    print("Manifest source/protocol/runner/runtime/checkpoint hashes verified; no estimator was fit.")


if __name__ == "__main__":
    main()
