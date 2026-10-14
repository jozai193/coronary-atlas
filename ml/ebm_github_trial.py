"""Fixed, research-only InterpretML EBM comparison on saved broad_v2 outer folds.

Run: .venv/Scripts/python.exe ml/ebm_github_trial.py --run
Audit: .venv/Scripts/python.exe ml/ebm_github_trial.py --verify

interpret-core is installed only in ignored .venv-ebm/site-packages. This script
does not alter the app's model artifacts or requirements.txt.
"""

import os

for _name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
import hashlib
import importlib.metadata
import json
import multiprocessing as mp
from pathlib import Path
import platform
import sys
import time
import traceback
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".venv-ebm" / "site-packages"))

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

from ml.schema import FEATURES, NUMERIC, PROHIBITED, ROOT as SCHEMA_ROOT, TARGETS, read_data

OUT = ROOT / "ml" / "experiments" / "ebm_github_v1"
SOURCE = ROOT / "data" / "raw" / "extention of Z-Alizadeh sani dataset.xlsx"
BROAD = ROOT / "ml" / "experiments" / "broad_v2"
PROTOCOL = OUT / "protocol.json"
PROTOCOL_SHA256 = "e35309317ef62e94da4f00857976a6193f34f54ddb437980eac138658ef474e1"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def lf_text(path):
    # Git may checkout the same text with CRLF on Windows and LF elsewhere.
    return Path(path).read_bytes().replace(b"\r\n", b"\n")


def crlf_text(path):
    return lf_text(path).replace(b"\n", b"\r\n")


def combined_fold_hash(files):
    h = hashlib.sha256()
    for path in files:
        h.update(str(path.relative_to(BROAD)).encode())
        h.update(sha256_bytes(crlf_text(path)).encode())
    return h.hexdigest()


def combined_csv_hash(files):
    h = hashlib.sha256()
    for path in files:
        h.update(crlf_text(path))
    return h.hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False, ensure_ascii=False) + "\n", encoding="utf-8")


def score(y, p):
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    if len(y) != 303 or len(p) != 303 or not np.isfinite(p).all():
        raise AssertionError("Only a complete 303-row repeat may be scored")
    if ((p < 0) | (p > 1)).any():
        raise AssertionError("Out-of-range probabilities")
    positive = y == 1
    tp = int((positive & (p >= 0.5)).sum())
    fn = int((positive & (p < 0.5)).sum())
    return {
        "auc": float(roc_auc_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "sensitivity_at_0_5": tp / (tp + fn),
        "true_positives": tp,
        "false_negatives": fn,
    }


def load_and_check():
    if sha256_bytes(lf_text(PROTOCOL)) != PROTOCOL_SHA256:
        raise AssertionError("Frozen protocol digest changed")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if SCHEMA_ROOT != ROOT:
        raise AssertionError("Unexpected schema root")
    if sha256(SOURCE) != protocol["source_workbook_sha256"]:
        raise AssertionError("Source workbook digest changed")
    if sha256_bytes(lf_text(ROOT / "ml/schema.py")) != protocol["schema_py_sha256"]:
        raise AssertionError("Feature schema digest changed")
    folds = sorted(BROAD.glob("*_repeat_*_fold_*.json"))
    baseline_files = sorted(BROAD.glob("*_repeat_*.csv"))
    if len(folds) != protocol["fold_files"] or combined_fold_hash(folds) != protocol["fold_files_combined_sha256"]:
        raise AssertionError("Saved outer fold artifact digest changed")
    if len(baseline_files) != protocol["baseline_csv_files"] or combined_csv_hash(baseline_files) != protocol["baseline_csv_combined_sha256"]:
        raise AssertionError("Matched baseline prediction digest changed")
    if len(FEATURES) != 55 or set(FEATURES) & PROHIBITED or list(TARGETS) != protocol["targets"]:
        raise AssertionError("Unexpected feature or target contract")
    df = read_data()
    if len(df) != protocol["source_cohort_rows"] or list(df[FEATURES].columns) != FEATURES:
        raise AssertionError("Unexpected source rows or input order")
    validated = {}
    for target in protocol["targets"]:
        y = (df[TARGETS[target]] == ("CAD" if target == "cad" else "Stenotic")).astype(int).to_numpy()
        for repeat in (1, 2):
            key = (target, repeat)
            baseline = pd.read_csv(BROAD / f"{target}_repeat_{repeat}.csv").sort_values("row_index").reset_index(drop=True)
            if baseline["row_index"].tolist() != list(range(303)) or not np.array_equal(baseline["y"].to_numpy(), y):
                raise AssertionError(f"Baseline rows/labels mismatch: {key}")
            if baseline["baseline_selector"].isna().any():
                raise AssertionError(f"Missing baseline probabilities: {key}")
            seen = set()
            partition = []
            for fold in range(1, 6):
                obj = json.loads((BROAD / f"{target}_repeat_{repeat}_fold_{fold}.json").read_text(encoding="utf-8"))
                train = np.asarray(obj["train_indices"], dtype=int)
                test = np.asarray(obj["test_indices"], dtype=int)
                if obj["fold"] != fold - 1 or set(train) & set(test) or set(train) | set(test) != set(range(303)):
                    raise AssertionError(f"Invalid fold partition: {key}/{fold}")
                if seen & set(test) or not (baseline.loc[test, "outer_fold"] == fold - 1).all():
                    raise AssertionError(f"Fold overlap or baseline mismatch: {key}/{fold}")
                seen.update(test.tolist())
                partition.append((train, test))
            if seen != set(range(303)):
                raise AssertionError(f"Incomplete fold coverage: {key}")
            validated[key] = (y, baseline, partition)
    return protocol, df[FEATURES], validated


def _worker(conn, X_train, y_train, X_test, feature_types, params, seed):
    try:
        from interpret.glassbox import ExplainableBoostingClassifier
        from threadpoolctl import threadpool_limits

        start = time.perf_counter()
        with warnings.catch_warnings(record=True) as captured, threadpool_limits(limits=1):
            warnings.simplefilter("always")
            model = ExplainableBoostingClassifier(
                feature_types=feature_types, random_state=seed, **params
            )
            model.fit(X_train, y_train)
            proba = np.asarray(model.predict_proba(X_test)[:, 1], dtype=float)
        if proba.shape != (len(X_test),) or not np.isfinite(proba).all() or ((proba < 0) | (proba > 1)).any():
            raise AssertionError("Invalid EBM probabilities")
        if any(len(term) != 1 for term in model.term_features_):
            raise AssertionError("Unexpected EBM interaction term")
        conn.send({
            "status": "ok", "probabilities": proba.tolist(),
            "seconds": time.perf_counter() - start,
            "term_count": len(model.term_features_),
            "feature_count": len(model.feature_names_in_),
            "warning_count": len(captured),
            "warning_messages": list(dict.fromkeys(str(w.message) for w in captured))[:3],
        })
    except BaseException as exc:
        conn.send({"status": "error", "error_type": type(exc).__name__, "error": str(exc)[:600],
                   "traceback": traceback.format_exc()[-1800:]})
    finally:
        conn.close()


def fit_once(X_train, y_train, X_test, feature_types, params, seed, timeout):
    context = mp.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    process = context.Process(target=_worker, args=(send, X_train, y_train, X_test, feature_types, params, seed))
    process.start()
    send.close()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process.join(5)
        if process.is_alive():
            process.kill()
            process.join(5)
        receive.close()
        return {"status": "timeout", "seconds": timeout}
    if not receive.poll():
        receive.close()
        return {"status": "worker_exited_without_result", "exit_code": process.exitcode}
    result = receive.recv()
    receive.close()
    return result


def summarize(repeats):
    summary = {}
    for target in ("cad", "lad", "lcx", "rca"):
        rows = [r for r in repeats if r["target"] == target]
        ebm = [r["ebm"] for r in rows]
        baseline = [r["baseline"] for r in rows]
        auc_delta = [e["auc"] - b["auc"] for e, b in zip(ebm, baseline)]
        brier_delta = [e["brier"] - b["brier"] for e, b in zip(ebm, baseline)]
        sens_delta = [e["sensitivity_at_0_5"] - b["sensitivity_at_0_5"] for e, b in zip(ebm, baseline)]
        summary[target] = {
            "ebm_mean": {key: float(np.mean([m[key] for m in ebm])) for key in ("auc", "brier", "sensitivity_at_0_5")},
            "baseline_mean": {key: float(np.mean([m[key] for m in baseline])) for key in ("auc", "brier", "sensitivity_at_0_5")},
            "auc_delta_by_repeat": auc_delta,
            "brier_delta_by_repeat": brier_delta,
            "sensitivity_delta_by_repeat": sens_delta,
            "auc_screen": bool(np.mean(auc_delta) >= 0.015 and min(auc_delta) >= 0 and np.mean(brier_delta) <= 0.005),
            "probability_quality_screen": bool(np.mean(brier_delta) <= -0.005 and min(auc_delta) >= -0.01),
        }
    return summary


def run():
    if (OUT / "run_manifest.json").exists() or (OUT / "summary.json").exists():
        raise RuntimeError("A trial already exists; only --verify is permitted. Do not adapt the protocol after seeing results.")
    protocol, X, validated = load_and_check()
    version = importlib.metadata.version("interpret-core")
    if version != "0.7.8":
        raise AssertionError("Unexpected InterpretML core version")
    import interpret  # noqa: F401 - validates isolated optional installation

    if not Path(interpret.__file__).resolve().is_relative_to(ROOT / ".venv-ebm" / "site-packages"):
        raise AssertionError("Optional package was not imported from the isolated target")
    params = protocol["candidate"]["parameters"]
    feature_types = ["continuous" if f in NUMERIC else "nominal" for f in FEATURES]
    start = time.monotonic()
    manifest = {
        "status": "running", "protocol_sha256": PROTOCOL_SHA256,
        "runner_sha256": sha256(Path(__file__)),
        "python": platform.python_version(),
        "versions": {name: importlib.metadata.version(name) for name in ("interpret-core", "numpy", "pandas", "scikit-learn")},
        "completed_fits": [], "failure": None,
    }
    write_json(OUT / "run_manifest.json", manifest)
    repeats = []
    try:
        for target_index, target in enumerate(protocol["targets"]):
            for repeat_index, repeat in enumerate((1, 2)):
                y, baseline, partition = validated[(target, repeat)]
                table = baseline[["row_index", "y", "outer_fold", "baseline_selector"]].copy()
                table["ebm"] = np.nan
                for fold_index, (train, test) in enumerate(partition):
                    if time.monotonic() - start >= 1800:
                        raise TimeoutError("Thirty-minute stage budget exhausted")
                    seed = 20261007 + 10000 * target_index + 100 * repeat_index + fold_index
                    result = fit_once(X.iloc[train], y[train], X.iloc[test], feature_types, params, seed, 120)
                    if result["status"] != "ok":
                        raise RuntimeError(f"{target}/repeat{repeat}/fold{fold_index + 1}: {result}")
                    table.loc[test, "ebm"] = result.pop("probabilities")
                    table.to_csv(OUT / f"{target}_repeat_{repeat}.csv", index=False, float_format="%.17g")
                    manifest["completed_fits"].append({"target": target, "repeat": repeat, "fold": fold_index,
                                                        "seed": seed, **result})
                    write_json(OUT / "run_manifest.json", manifest)
                    print(f"{target} repeat {repeat} fold {fold_index + 1}/5 {result['seconds']:.1f}s", flush=True)
                ebm_metric = score(y, table["ebm"].to_numpy())
                base_metric = score(y, table["baseline_selector"].to_numpy())
                repeats.append({"target": target, "repeat": repeat, "ebm": ebm_metric, "baseline": base_metric})
        summary = summarize(repeats)
        write_json(OUT / "summary.json", {"status": "complete", "repeat_metrics": repeats, "target_summary": summary,
                                          "interpretation": "Repeated internal development check only; no independent validation or app change."})
        manifest["status"] = "complete"
        manifest["elapsed_seconds"] = time.monotonic() - start
        manifest["output_sha256"] = {p.name: sha256(p) for p in sorted(OUT.glob("*_repeat_*.csv"))}
        manifest["output_sha256"]["summary.json"] = sha256(OUT / "summary.json")
        write_json(OUT / "run_manifest.json", manifest)
    except BaseException as exc:
        manifest["status"] = "failed"
        manifest["elapsed_seconds"] = time.monotonic() - start
        manifest["failure"] = {"type": type(exc).__name__, "message": str(exc)[:1200]}
        write_json(OUT / "run_manifest.json", manifest)
        raise


def verify():
    protocol, _, validated = load_and_check()
    manifest = json.loads((OUT / "run_manifest.json").read_text(encoding="utf-8"))
    summary_path = OUT / "summary.json"
    # The exact fit runner is retained separately because the post-fit CSV
    # verifier needed a 5e-16 parser/serialization tolerance (2.22e-16 max).
    fit_snapshot = OUT / "fit_runner_snapshot.py"
    if manifest["protocol_sha256"] != PROTOCOL_SHA256 or manifest["runner_sha256"] != sha256_bytes(lf_text(fit_snapshot)):
        raise AssertionError("Protocol or executed fit-runner snapshot hash mismatch")
    if manifest["status"] != "complete" or len(manifest["completed_fits"]) != 40:
        raise AssertionError("Trial is incomplete")
    for item in manifest["completed_fits"]:
        if item["status"] != "ok" or item["feature_count"] != 55 or not 0 < item["term_count"] <= 55:
            raise AssertionError("A fit failed or was not the fixed main-effects EBM")
    for name, expected in manifest["output_sha256"].items():
        if sha256_bytes(crlf_text(OUT / name)) != expected:
            raise AssertionError(f"Output digest mismatch: {name}")
    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    repeated = []
    for target in protocol["targets"]:
        for repeat in (1, 2):
            y, baseline, partition = validated[(target, repeat)]
            table = pd.read_csv(OUT / f"{target}_repeat_{repeat}.csv").sort_values("row_index").reset_index(drop=True)
            if table["row_index"].tolist() != list(range(303)) or not np.array_equal(table["y"].to_numpy(), y):
                raise AssertionError("Prediction row or label mismatch")
            if not np.array_equal(table["outer_fold"].to_numpy(), baseline["outer_fold"].to_numpy()):
                raise AssertionError("Prediction fold mismatch")
            if not np.allclose(table["baseline_selector"].to_numpy(), baseline["baseline_selector"].to_numpy(), rtol=0, atol=5e-16):
                raise AssertionError("Matched baseline changed")
            for fold_index, (_, test) in enumerate(partition):
                if not (table.loc[test, "outer_fold"] == fold_index).all():
                    raise AssertionError("Fold prediction placement mismatch")
            repeated.append({"target": target, "repeat": repeat,
                             "ebm": score(y, table["ebm"].to_numpy()),
                             "baseline": score(y, table["baseline_selector"].to_numpy())})
    calculated = summarize(repeated)
    for target in protocol["targets"]:
        for section in ("ebm_mean", "baseline_mean"):
            for metric, value in calculated[target][section].items():
                if not np.isclose(value, saved["target_summary"][target][section][metric], rtol=0, atol=1e-12):
                    raise AssertionError(f"Summary metric mismatch: {target}/{section}/{metric}")
        for gate in ("auc_screen", "probability_quality_screen"):
            if calculated[target][gate] != saved["target_summary"][target][gate]:
                raise AssertionError(f"Screen mismatch: {target}/{gate}")
    print("Verified 40 fixed outer fits, eight 303-row prediction files, source/fold/baseline/output hashes, metrics and screens.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--run", action="store_true")
    operation.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.run:
        run()
    else:
        verify()
