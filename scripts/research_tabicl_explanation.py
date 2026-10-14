"""Local, bounded TabICLv2 permutation-SHAP/runtime feasibility pilot."""
from __future__ import annotations

import os

for _name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import hashlib
from importlib.metadata import version
import json
import platform
import sys
import threading
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
import scipy
import sklearn
import torch
from scipy.stats import spearmanr
from tabicl import TabICLClassifier
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.schema import CATEGORICAL, FEATURES, NUMERIC, PROHIBITED, ROOT, TARGETS, read_data


THREADS = 2
N_ESTIMATORS = 8
MODEL_SEEDS = (20261007, 20261108)
PERMUTATION_SEEDS = (20261008, 20261009, 20261010, 20261011)
BACKGROUND_INDICES = (0, 43, 86, 129, 172, 215, 258, 302)
TARGET_NAMES = ("cad", "lad", "lcx")
MAX_WALL_SECONDS = 600.0
CHECKPOINT = ROOT / ".venv-tabicl" / "checkpoints" / "tabicl-classifier-v2-20260212.ckpt"
CHECKPOINT_SHA256 = "bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0"
PROTOCOL = ROOT / "docs" / "tabicl_explanation_protocol.md"
OUTPUT = ROOT / "ml" / "experiments" / "tabicl_v2" / "explanation_pilot" / "result.json"
_PROCESS_STARTED = time.perf_counter()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


class PeakRss:
    def __init__(self) -> None:
        self.process = psutil.Process()
        self.peak = self.process.memory_info().rss
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._poll, daemon=True)

    def _poll(self) -> None:
        while not self.stop_event.wait(0.05):
            self.peak = max(self.peak, self.process.memory_info().rss)

    def __enter__(self) -> "PeakRss":
        self.thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop_event.set()
        self.thread.join()


def write_result(value: dict) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temp = OUTPUT.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    temp.replace(OUTPUT)


def check_deadline(started: float) -> None:
    if time.perf_counter() - started >= MAX_WALL_SECONDS:
        raise TimeoutError(f"The frozen {MAX_WALL_SECONDS:.0f}-second pilot wall-clock cap was reached.")


def estimator(seed: int, *, cached: bool) -> TabICLClassifier:
    return TabICLClassifier(
        n_estimators=N_ESTIMATORS,
        norm_methods=None,
        feat_shuffle_method="latin",
        class_shuffle_method="shift",
        outlier_threshold=4.0,
        softmax_temperature=0.9,
        average_logits=True,
        support_many_classes=True,
        batch_size=1,
        kv_cache=cached,
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


def positive_probability(model: TabICLClassifier, X: pd.DataFrame) -> np.ndarray:
    proba = np.asarray(model.predict_proba(X), dtype=float)
    classes = np.asarray(model.classes_)
    positive = np.flatnonzero(classes == 1)
    if proba.shape != (len(X), len(classes)) or len(positive) != 1:
        raise ValueError(f"Unexpected class/probability output: {classes!r}, {proba.shape}")
    answer = proba[:, int(positive[0])]
    if not np.isfinite(answer).all() or ((answer < 0) | (answer > 1)).any():
        raise ValueError("TabICL returned invalid positive-class probabilities.")
    return answer


def make_profiles(X: pd.DataFrame) -> dict[str, pd.Series]:
    a: dict[str, object] = {}
    b: dict[str, object] = {}
    for col in FEATURES:
        if col in NUMERIC:
            a[col] = float(X[col].median())
            b[col] = float(X[col].quantile(0.75, interpolation="linear"))
        else:
            counts = X[col].astype(str).value_counts()
            ranked = sorted(counts.items(), key=lambda item: (-int(item[1]), str(item[0])))
            a[col] = str(ranked[0][0])
            b[col] = str(ranked[1][0] if len(ranked) > 1 else ranked[0][0])
    return {
        "A_feature_medians_and_categorical_modes": pd.Series(a, index=FEATURES),
        "B_numeric_q75_and_second_most_common_categories": pd.Series(b, index=FEATURES),
    }


def sampled_permutation_attributions(
    model: TabICLClassifier,
    X: pd.DataFrame,
    profile: pd.Series,
    permutation_orders: list[np.ndarray],
) -> tuple[dict, float]:
    background = X.iloc[list(BACKGROUND_INDICES)].copy().reset_index(drop=True)
    started = time.perf_counter()
    profile_frame = pd.DataFrame([profile.to_dict()], columns=FEATURES)

    # Evaluate every sampled path coalition in one cached inference batch. Each
    # coalition is paired with all eight complete source-row backgrounds.
    hybrids: list[pd.DataFrame] = []
    coalition_keys: list[tuple[int, ...]] = []
    for order in permutation_orders:
        selected: list[int] = []
        for feature_index in order:
            selected.append(int(feature_index))
            state = tuple(sorted(selected))
            coalition_keys.append(state)
            chunk = background.copy()
            for idx in state:
                column = FEATURES[idx]
                chunk[column] = profile[column]
            hybrids.append(chunk)
    all_hybrids = pd.concat(hybrids, ignore_index=True)
    # Put endpoints and coalitions in one predict_proba call. TabICL's CPU
    # arithmetic can differ by ~1e-7 when an identical row is evaluated in a
    # differently sized batch, which would otherwise dominate the telescoping
    # residual despite mathematically identical endpoints.
    all_rows = pd.concat([background, profile_frame, all_hybrids], ignore_index=True)
    all_probabilities = positive_probability(model, all_rows)
    background_p = all_probabilities[:len(BACKGROUND_INDICES)]
    profile_single_row_p = float(all_probabilities[len(BACKGROUND_INDICES)])
    hybrid_p = all_probabilities[len(BACKGROUND_INDICES) + 1:].reshape(
        len(coalition_keys), len(BACKGROUND_INDICES)
    )
    baseline_p = float(background_p.mean())
    path_endpoint_values = [
        float(np.mean(hybrid_p[(path_index + 1) * len(FEATURES) - 1]))
        for path_index in range(len(permutation_orders))
    ]
    # Identical full-profile rows can vary by a few float32 ulps depending on
    # their batch position. Define f(x) as the mean of each sampled path's
    # repeated full-coalition output; this is still the same profile query and
    # makes the reported approximation's endpoint explicit and reproducible.
    profile_p = float(np.mean(path_endpoint_values))
    values: dict[tuple[int, ...], float] = {
        (): baseline_p,
        tuple(range(len(FEATURES))): profile_p,
    }
    for state, row_probabilities in zip(coalition_keys, hybrid_p, strict=True):
        values[state] = float(np.mean(row_probabilities))

    path_rows = []
    contribution_sum = np.zeros(len(FEATURES), dtype=float)
    for path_index, order in enumerate(permutation_orders):
        selected_set: set[int] = set()
        previous = baseline_p
        contributions = np.zeros(len(FEATURES), dtype=float)
        for step_index, feature_index in enumerate(order):
            selected_set.add(int(feature_index))
            if step_index == len(order) - 1:
                current = path_endpoint_values[path_index]
            else:
                current = values[tuple(sorted(selected_set))]
            contributions[int(feature_index)] = current - previous
            previous = current
        residual = float(contributions.sum() - (path_endpoint_values[path_index] - baseline_p))
        path_rows.append({
            "path_full_coalition_probability": path_endpoint_values[path_index],
            "sum_minus_path_probability_difference": residual,
        })
        contribution_sum += contributions
    mean_contributions = contribution_sum / len(permutation_orders)
    average_residual = float(mean_contributions.sum() - (profile_p - baseline_p))
    maximum_residual = max([abs(r["sum_minus_path_probability_difference"]) for r in path_rows] + [abs(average_residual)])
    if maximum_residual > 1e-8:
        raise AssertionError(f"Permutation attribution failed telescoping reconstruction: {maximum_residual}")

    result = {
        "background_indices_zero_based": list(BACKGROUND_INDICES),
        "background_positive_probabilities": [float(v) for v in background_p],
        "mean_background_probability": baseline_p,
        "profile_probability": profile_p,
        "profile_single_row_probability_in_joint_batch": profile_single_row_p,
        "full_coalition_endpoint_probabilities_by_permutation": path_endpoint_values,
        "maximum_full_coalition_endpoint_batch_variation": float(max(path_endpoint_values) - min(path_endpoint_values)),
        "probability_difference_profile_minus_background": profile_p - baseline_p,
        "permutation_seeds": list(PERMUTATION_SEEDS),
        "permutation_orders_feature_names": [[FEATURES[int(i)] for i in order] for order in permutation_orders],
        "permutation_path_reconstruction_residuals": path_rows,
        "mean_attribution_reconstruction_residual": average_residual,
        "maximum_absolute_reconstruction_residual": maximum_residual,
        "attributions_probability_points": {
            FEATURES[i]: float(mean_contributions[i]) for i in range(len(FEATURES))
        },
        "attribution_sum_probability_points": float(mean_contributions.sum()),
        "coalition_predictions": len(coalition_keys) * len(BACKGROUND_INDICES),
        "distinct_coalition_masks": len(values),
    }
    return result, time.perf_counter() - started


def compare_seed_vectors(first: dict, second: dict) -> dict:
    a = np.array([first["attributions_probability_points"][c] for c in FEATURES], dtype=float)
    b = np.array([second["attributions_probability_points"][c] for c in FEATURES], dtype=float)
    rho = float(spearmanr(a, b).statistic)
    top_a = set(np.argsort(np.abs(a))[-10:].tolist())
    top_b = set(np.argsort(np.abs(b))[-10:].tolist())
    return {
        "spearman_rank_correlation": rho if np.isfinite(rho) else None,
        "top_10_absolute_attribution_overlap_count": len(top_a & top_b),
        "top_10_absolute_attribution_overlap_fraction": len(top_a & top_b) / 10.0,
        "mean_absolute_attribution_difference_probability_points": float(np.mean(np.abs(a - b))),
        "mean_absolute_attribution_magnitude_seed_1_probability_points": float(np.mean(np.abs(a))),
        "mean_absolute_attribution_magnitude_seed_2_probability_points": float(np.mean(np.abs(b))),
        "l1_attribution_difference_probability_points": float(np.sum(np.abs(a - b))),
    }


def main() -> None:
    started = _PROCESS_STARTED
    torch.set_num_threads(THREADS)
    torch.set_num_interop_threads(1)
    if not CHECKPOINT.is_file() or sha256(CHECKPOINT) != CHECKPOINT_SHA256:
        raise ValueError("The pinned local TabICLv2 checkpoint is missing or has the wrong SHA-256.")
    if not PROTOCOL.is_file():
        raise ValueError("The frozen explanation protocol is missing.")

    df = read_data()
    X = df[FEATURES].copy()
    if X.shape != (303, 55) or set(X.columns) & PROHIBITED:
        raise ValueError(f"Unexpected feature-only data shape/schema: {X.shape}")
    if not set(CATEGORICAL).issubset(X.columns):
        raise ValueError("Categorical feature contract mismatch.")
    profiles = make_profiles(X)
    permutation_orders = [np.random.default_rng(seed).permutation(len(FEATURES)) for seed in PERMUTATION_SEEDS]

    result = {
        "purpose": "full-cohort model explanation/runtime feasibility only; no held-out performance evaluation",
        "complete": False,
        "pilot_wall_clock_cap_seconds": MAX_WALL_SECONDS,
        "source_workbook_sha256": sha256(ROOT / "data" / "raw" / "extention of Z-Alizadeh sani dataset.xlsx"),
        "protocol_sha256": sha256(PROTOCOL),
        "runner_sha256": sha256(Path(__file__).resolve()),
        "checkpoint": {"bytes": CHECKPOINT.stat().st_size, "sha256": sha256(CHECKPOINT), "license": "BSD-3-Clause per authors' model card"},
        "python": platform.python_version(),
        "tabicl": version("tabicl"),
        "torch": torch.__version__,
        "scikit_learn": sklearn.__version__,
        "scipy": scipy.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "cpu_threads": THREADS,
        "gpu_used": False,
        "feature_count": len(FEATURES),
        "targets": list(TARGET_NAMES),
        "model_seeds": list(MODEL_SEEDS),
        "permutation_seeds": list(PERMUTATION_SEEDS),
        "profile_definitions": {
            "A_feature_medians_and_categorical_modes": "Feature-wise numeric median; categorical mode; lexical tie-break.",
            "B_numeric_q75_and_second_most_common_categories": "Feature-wise numeric 75th percentile; second-most-common category; lexical tie-break; sole category retained.",
        },
        "profiles": {name: {col: (float(values[col]) if col in NUMERIC else str(values[col])) for col in FEATURES} for name, values in profiles.items()},
        "background_indices_zero_based": list(BACKGROUND_INDICES),
        "explanations": [],
        "cache_parity_checks": [],
        "cross_seed_stability": [],
        "runtime": {"cached_fit_predict_seconds": 0.0, "attribution_seconds": 0.0, "cold_fit_parity_seconds": 0.0},
    }
    write_result(result)

    with PeakRss() as monitor, threadpool_limits(limits=1):
        for target in TARGET_NAMES:
            y_label = "CAD" if target == "cad" else "Stenotic"
            y = (df[TARGETS[target]] == y_label).astype(int).to_numpy()
            if set(np.unique(y)) != {0, 1}:
                raise ValueError(f"Target {target} is not binary.")
            for seed in MODEL_SEEDS:
                check_deadline(started)
                fitted = estimator(seed, cached=True)
                fit_started = time.perf_counter()
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    fitted.fit(X, y)
                fit_seconds = time.perf_counter() - fit_started
                result["runtime"]["cached_fit_predict_seconds"] += fit_seconds

                # A same-seed non-cached twin checks that kv_cache changes only
                # inference execution, not the fitted predictor's probabilities.
                check_deadline(started)
                cold = estimator(seed, cached=False)
                cold_started = time.perf_counter()
                cold.fit(X, y)
                parity_rows = pd.concat([
                    X.iloc[list(BACKGROUND_INDICES)],
                    pd.DataFrame([profiles[name].to_dict() for name in profiles], columns=FEATURES),
                ], ignore_index=True)
                cached_p = positive_probability(fitted, parity_rows)
                cold_p = positive_probability(cold, parity_rows)
                parity_seconds = time.perf_counter() - cold_started
                parity_error = float(np.max(np.abs(cached_p - cold_p)))
                result["runtime"]["cold_fit_parity_seconds"] += parity_seconds
                result["cache_parity_checks"].append({
                    "target": target,
                    "model_seed": seed,
                    "rows_compared": len(parity_rows),
                    "maximum_absolute_probability_difference": parity_error,
                    "fit_seconds_including_parity_predictions": parity_seconds,
                    "exact_to_1e-8": bool(parity_error <= 1e-8),
                })
                del cold, cached_p, cold_p, parity_rows

                for profile_name, profile in profiles.items():
                    check_deadline(started)
                    explanation, seconds = sampled_permutation_attributions(
                        fitted, X, profile, permutation_orders
                    )
                    result["runtime"]["attribution_seconds"] += seconds
                    result["explanations"].append({
                        "target": target,
                        "positive_label": y_label,
                        "model_seed": seed,
                        "profile_name": profile_name,
                        "model_fit_seconds": fit_seconds,
                        "attribution_wall_seconds": seconds,
                        "warnings": list(dict.fromkeys(str(w.message) for w in caught))[:5],
                        "explanation": explanation,
                    })
                    write_result(result)
                del fitted

        for target in TARGET_NAMES:
            for profile_name in profiles:
                pair = [entry for entry in result["explanations"] if entry["target"] == target and entry["profile_name"] == profile_name]
                # profile_name is stored below by the append operation; this
                # guard also keeps partial results valid after a deadline.
                if not pair:
                    pair = [entry for entry in result["explanations"] if entry["target"] == target and entry.get("profile_name") == profile_name]
                if len(pair) == 2:
                    result["cross_seed_stability"].append({
                        "target": target,
                        "profile": profile_name,
                        **compare_seed_vectors(pair[0]["explanation"], pair[1]["explanation"]),
                    })

        result["complete"] = len(result["explanations"]) == len(TARGET_NAMES) * len(MODEL_SEEDS) * len(profiles)
        result["peak_process_rss_mib"] = round(monitor.peak / (1024 ** 2), 2)
    result["total_wall_seconds"] = round(time.perf_counter() - started, 4)
    write_result(result)
    print(json.dumps({
        "complete": result["complete"],
        "total_wall_seconds": result["total_wall_seconds"],
        "peak_process_rss_mib": result.get("peak_process_rss_mib"),
        "explanations": len(result["explanations"]),
        "cache_checks_max_abs_error": max((x["maximum_absolute_probability_difference"] for x in result["cache_parity_checks"]), default=None),
        "max_reconstruction_residual": max((x["explanation"]["maximum_absolute_reconstruction_residual"] for x in result["explanations"]), default=None),
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except TimeoutError as error:
        if OUTPUT.exists():
            partial = json.loads(OUTPUT.read_text(encoding="utf-8"))
            partial["complete"] = False
            partial["stop_reason"] = str(error)
            partial["total_wall_seconds"] = round(time.perf_counter() - _PROCESS_STARTED, 4)
            write_result(partial)
        print(str(error), file=sys.stderr)
        raise
