"""Resource-capped TabICLv2 input-size smoke test; never evaluates real labels."""
from __future__ import annotations

import hashlib
from importlib.metadata import version
import json
import platform
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psutil
import sklearn
import torch
import tabicl
from tabicl import TabICLClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.schema import FEATURES, ROOT, digest


SEED = 20261008
TRAIN_SIZES = (161, 242, 303)
THREADS = 2
N_ESTIMATORS = 8
CHECKPOINT = ROOT / ".venv-tabicl" / "checkpoints" / "tabicl-classifier-v2-20260212.ckpt"
CHECKPOINT_SHA256 = "bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0"
OUTPUT = ROOT / ".venv-tabicl" / "research-output" / "tabicl_feasibility.json"


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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    torch.set_num_threads(THREADS)
    torch.set_num_interop_threads(1)
    if not CHECKPOINT.is_file() or sha256(CHECKPOINT) != CHECKPOINT_SHA256:
        raise ValueError("The pinned TabICLv2 checkpoint is missing or has the wrong SHA-256.")
    rng = np.random.default_rng(SEED)

    workbook = ROOT / "data" / "raw" / "extention of Z-Alizadeh sani dataset.xlsx"
    raw = pd.read_excel(workbook, sheet_name="Sheet 1 - Table 1")
    X = raw[FEATURES].copy()
    del raw
    if X.shape != (303, 55):
        raise ValueError(f"Unexpected feature-only input shape: {X.shape}")

    runs = []
    for n_train in TRAIN_SIZES:
        # Synthetic labels are deliberately generated without inspecting any target column.
        y_fake = np.tile(np.array([0, 1], dtype=np.int64), (n_train + 1) // 2)[:n_train]
        rng.shuffle(y_fake)
        X_train = X.iloc[:n_train]
        X_predict = X.iloc[n_train:n_train + 12]
        if X_predict.empty:
            X_predict = X.iloc[:12]

        model = TabICLClassifier(
            n_estimators=N_ESTIMATORS,
            batch_size=1,
            device="cpu",
            n_jobs=THREADS,
            random_state=SEED,
            model_path=CHECKPOINT,
            allow_auto_download=False,
            verbose=False,
        )
        rss_start = psutil.Process().memory_info().rss
        t0 = time.perf_counter()
        with PeakRss() as monitor:
            model.fit(X_train, y_fake)
            probabilities = model.predict_proba(X_predict)
        elapsed = time.perf_counter() - t0

        if probabilities.shape != (len(X_predict), 2):
            raise ValueError(f"Unexpected probability shape {probabilities.shape}")
        if not np.isfinite(probabilities).all():
            raise ValueError("Non-finite probabilities in the API smoke test")

        runs.append({
            "train_rows": n_train,
            "feature_columns": X_train.shape[1],
            "predict_rows": len(X_predict),
            "synthetic_balanced_labels_only": True,
            "n_estimators": N_ESTIMATORS,
            "batch_size": 1,
            "device": "cpu",
            "fit_predict_seconds": round(elapsed, 4),
            "start_rss_mib": round(rss_start / (1024 ** 2), 2),
            "peak_rss_mib": round(monitor.peak / (1024 ** 2), 2),
            "api_shape_ok": True,
        })
        del model, probabilities, X_train, X_predict, y_fake

    result = {
        "purpose": "fit/predict feasibility only; no real target values, performance metrics, or test outcomes",
        "seed": SEED,
        "source_workbook_sha256": digest(workbook),
        "feature_only_input_shape": list(X.shape),
        "python": platform.python_version(),
        "tabicl": version("tabicl"),
        "torch": torch.__version__,
        "scikit_learn": sklearn.__version__,
        "cpu_threads": THREADS,
        "gpu_used": False,
        "checkpoint": {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "bytes": CHECKPOINT.stat().st_size,
            "sha256": sha256(CHECKPOINT),
        },
        "runs": runs,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
