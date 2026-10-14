import numpy as np
import pandas as pd
import pytest
from ml import ensemble_candidate as candidate
from ml.schema import FEATURES, ROOT, read_data


def test_permutations_reconstruct_known_interaction(monkeypatch):
    frame = read_data()[FEATURES].iloc[[0]].copy()
    background = read_data()[FEATURES].iloc[1:5].copy()
    def nonlinear(_, X):
        age = X.Age.to_numpy(dtype=float) / 100
        weight = X.Weight.to_numpy(dtype=float) / 150
        p = .1 + .2 * age + .3 * age * weight
        return np.column_stack([p, p / 2, p / 3, p / 4])
    monkeypatch.setattr(candidate, 'raw_probabilities', nonlinear)
    base, values, output, residual = candidate.permutation_attributions({}, background, frame)
    np.testing.assert_allclose(base + values.sum(axis=0), output, atol=1e-12, rtol=0)
    other = [i for i, name in enumerate(FEATURES) if name not in ('Age', 'Weight')]
    np.testing.assert_allclose(values[other], 0, atol=1e-12, rtol=0)
    assert residual.max() < 1e-12


def test_unverified_candidate_rejected_before_loading(tmp_path):
    import json
    (tmp_path / 'manifest.json').write_text(json.dumps({'candidate_id': candidate.CANDIDATE_ID,
        'features': FEATURES, 'inference_verified': False}))
    with pytest.raises(ValueError, match='not verified'):
        candidate.ResearchEnsemble(tmp_path)


def test_optional_dependency_absence_keeps_baseline_available(monkeypatch):
    from backend import ensemble
    monkeypatch.setattr(ensemble, 'find_spec', lambda name: None)
    predictor, info = ensemble.load_ensemble()
    assert predictor is None
    assert info['available'] is False
