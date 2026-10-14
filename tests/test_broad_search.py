import numpy as np
import pandas as pd
import pytest
import time
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from ml.broad_search import (
    BASELINE_CANDIDATES,
    CandidatePool,
    CANDIDATES,
    CANDIDATE_SPECS,
    ENSEMBLE_MEMBERS,
    _fit_predict_once,
    make_candidate,
)
from ml.schema import CATEGORICAL, FEATURES, NUMERIC, TARGETS


def _small_frame(rows=100):
    rng = np.random.default_rng(1206)
    values = {}
    for index, name in enumerate(NUMERIC):
        values[name] = rng.normal(loc=index / 7, scale=1 + index / 50, size=rows)
    for index, name in enumerate(CATEGORICAL):
        values[name] = np.asarray([f"level_{(row + index) % (2 + index % 3)}" for row in range(rows)])
    frame = pd.DataFrame(values, columns=FEATURES)
    labels = np.tile([0, 1], rows // 2 + 1)[:rows]
    rng.shuffle(labels)
    return frame, pd.Series(labels)


def test_candidate_allowlist_and_family_search_are_frozen():
    assert not set(FEATURES) & set(TARGETS.values())
    assert BASELINE_CANDIDATES == ["logistic_003", "logistic_03", "forest", "boosting"]
    assert set(CANDIDATES) == set(CANDIDATE_SPECS)
    families = {spec["family"] for spec in CANDIDATE_SPECS.values()}
    assert {
        "elastic_net_logistic", "shrinkage_lda", "hist_gradient_boosting",
        "extra_trees", "rbf_svm_with_nested_sigmoid_calibration", "small_mlp",
        "catboost_native_categorical",
    } <= families
    assert ENSEMBLE_MEMBERS == [
        "logistic_003", "boosting", "extra_trees", "rbf_svm_sigmoid", "catboost_native",
    ]


def test_svm_calibration_wraps_preprocessing_inside_three_fold_cv():
    calibrated = make_candidate("rbf_svm_sigmoid", seed=501)
    assert isinstance(calibrated, CalibratedClassifierCV)
    assert calibrated.method == "sigmoid"
    assert calibrated.cv.n_splits == 3
    assert isinstance(calibrated.estimator, Pipeline)
    assert isinstance(calibrated.estimator.named_steps["model"], SVC)
    assert "preprocess" in calibrated.estimator.named_steps


def test_spawned_candidate_worker_returns_inner_and_outer_predictions():
    frame, labels = _small_frame()
    X_train, y_train = frame.iloc[:80], labels.iloc[:80]
    splits = list(StratifiedKFold(n_splits=3, shuffle=True, random_state=91).split(X_train, y_train))
    pool = CandidatePool(timeout_seconds=30)
    try:
        result = pool.run({
            "candidate": "logistic_003",
            "X_train": X_train,
            "y_train": y_train,
            "X_test": frame.iloc[80:],
            "train_indices": np.asarray(X_train.index),
            "inner_splits": splits,
            "calibration_seed": 91,
        }, deadline=time.monotonic() + 60)
    finally:
        pool.close()
    assert result["candidate"] == "logistic_003"
    assert [fold["status"] for fold in result["inner"]] == ["ok", "ok", "ok"]
    assert all(len(fold["probabilities"]) == len(fold["row_indices"]) for fold in result["inner"])
    assert result["outer"]["status"] == "ok"
    assert len(result["outer"]["probabilities"]) == 20


@pytest.mark.parametrize("candidate", CANDIDATES)
def test_each_frozen_candidate_returns_valid_probabilities(candidate):
    if candidate == "catboost_native":
        pytest.importorskip("catboost")
    frame, labels = _small_frame()
    result = _fit_predict_once(
        candidate, frame.iloc[:80], labels.iloc[:80], frame.iloc[80:], seed=20261007,
    )
    probabilities = np.asarray(result["probabilities"])
    assert result["status"] == "ok"
    assert probabilities.shape == (20,)
    assert np.isfinite(probabilities).all()
    assert ((probabilities >= 0) & (probabilities <= 1)).all()
