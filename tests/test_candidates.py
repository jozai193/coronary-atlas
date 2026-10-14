import json

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.candidates import load_candidate
from backend.main import app
from ml.schema import FEATURES


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def features(client):
    # Explicit test-only valve category; historical sample fixtures remain unchanged.
    return next(case['features'] for case in client.get('/review-profiles').json() if case['id']=='a')


def test_default_variant_is_identical_to_explicit_baseline(client, features):
    default = client.post('/api/predict', json={'features': features})
    explicit = client.post('/api/predict', json={
        'features': features,
        'model_variant': 'baseline',
    })

    assert default.status_code == explicit.status_code == 200
    assert default.json() == explicit.json()


def test_candidate_changes_only_lcx_and_its_shap_reconstructs(client, features):
    candidate_info = client.get('/model/candidates').json()
    if not candidate_info.get('available'):
        pytest.skip('The optional LCX candidate is not installed.')

    baseline = client.post('/predict', json={'features': features})
    candidate = client.post('/predict', json={
        'features': features,
        'model_variant': 'histgb_lcx_v2',
    })
    assert baseline.status_code == candidate.status_code == 200

    baseline_result = baseline.json()
    candidate_result = candidate.json()
    changed_targets = {
        target for target in ('cad', 'lad', 'lcx', 'rca')
        if baseline_result[target]['model_probability'] != candidate_result[target]['model_probability']
    }
    assert changed_targets == {'lcx'}
    assert baseline_result['coherence_adjustment']['enabled'] is True
    assert candidate_result['coherence_adjustment']['enabled'] is False
    for target in ('cad', 'lad', 'lcx', 'rca'):
        assert candidate_result[target]['probability'] == candidate_result[target]['model_probability']
    assert candidate_result['lcx']['model'] == 'hist_gradient_boosting'
    assert candidate_result['model_version'] == '1.0.0+histgb-lcx-v2'
    assert candidate_info['target'] == 'lcx'

    explanation = candidate_result['lcx']['explanation']
    raw_output = explanation['base_value'] + sum(
        factor['contribution'] for factor in explanation['factors']
    )
    reconstructed = (
        raw_output if explanation['unit'] == 'probability'
        else 1 / (1 + np.exp(-raw_output))
    )
    assert explanation['additivity_error'] < 1e-4
    assert reconstructed == pytest.approx(candidate_result['lcx']['model_probability'], abs=1e-4)


def test_unknown_model_variant_is_rejected(client, features):
    response = client.post('/api/predict', json={
        'features': features,
        'model_variant': 'experimental_other',
    })

    assert response.status_code == 422


def test_unavailable_candidate_returns_503(client, features, monkeypatch):
    monkeypatch.setattr(app.state, 'candidate', None)

    response = client.post('/api/predict', json={
        'features': features,
        'model_variant': 'histgb_lcx_v2',
    })

    assert response.status_code == 503
    assert 'not installed' in response.json()['detail']


def test_candidate_hash_corruption_is_rejected(tmp_path):
    candidate_dir = tmp_path / 'candidate'
    candidate_dir.mkdir()
    (candidate_dir / 'manifest.json').write_text(json.dumps({
        'candidate_id': 'histgb_lcx_v2',
        'inference_verified': True,
        'feature_names': FEATURES,
        'nested_heldout_evidence': {'files': []},
        'artifact': {
            'file': 'histgb_lcx.joblib',
            'sha256': '0' * 64,
        },
    }), encoding='utf-8')
    (candidate_dir / 'histgb_lcx.joblib').write_bytes(b'corrupt candidate artifact')

    with pytest.raises(ValueError, match='integrity'):
        load_candidate(object(), candidate_dir)
