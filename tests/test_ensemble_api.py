import json
import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from ml.schema import ROOT, FEATURES, TARGETS, GROUPS


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c


def test_research_ensemble_has_matching_evidence_and_own_attributions(client):
    info = client.get('/model/candidates').json()['ensemble']
    assert info['available']
    assert len(info['runs']) == 3
    saved = json.loads((ROOT / 'ml/experiments/accuracy_ensemble_v1/results.json').read_text())
    for run in info['runs']:
        for target in TARGETS:
            expected = next(r for r in saved['scores'] if r['repeat'] == run['repeat'] and r['target'] == target and r['arm'] == 'sigmoid_uniform_projected')
            assert run['targets'][target]['candidate'] == expected
    values = next(case['features'] for case in client.get('/review-profiles').json() if case['id']=='a')
    request = {'features': values, 'model_variant': 'calibrated_ensemble_v1'}
    response = client.post('/predict', json=request)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result == client.post('/api/predict', json=request).json()
    assert result['model_version'] == '1.0.0+calibrated-ensemble-v1'
    assert result['coherence_adjustment']['enabled']
    assert result['cad']['probability'] >= max(result[t]['probability'] for t in ('lad', 'lcx', 'rca'))
    assert response.headers['cache-control'] == 'no-store'
    for target in TARGETS:
        item = result[target]
        ex = item['explanation']
        assert ex['method'] == 'Sampled permutation attribution'
        assert {v['feature'] for v in ex['factors']} == set(FEATURES)
        assert ex['base_value'] + sum(v['contribution'] for v in ex['factors']) == pytest.approx(item['model_probability'], abs=1e-10)
        assert item['classification'] == int(item['probability'] >= .5)
    assert any('not independent clinical validation' in w for w in result['warnings'])


def test_ensemble_obeys_input_guards_and_blocks_core_only(client):
    values = next(case['features'] for case in client.get('/review-profiles').json() if case['id']=='a')
    invalid = client.post('/predict', json={'features': {**values, 'Cath': 'CAD'}, 'model_variant': 'calibrated_ensemble_v1'})
    assert invalid.status_code == 422
    from ml.schema import read_data
    values = read_data().iloc[0][FEATURES].to_dict()
    for field in GROUPS['Laboratory'] + GROUPS['Echocardiography'] + GROUPS['ECG']:
        values[field] = None
    response = client.post('/predict', json={'features': values, 'model_variant': 'calibrated_ensemble_v1'})
    assert response.status_code == 422, response.text
    assert 'echo EF' in response.json()['detail'] and 'valve assessment' in response.json()['detail']


def test_unavailable_ensemble_fails_explicitly(client, monkeypatch):
    monkeypatch.setattr(app.state, 'ensemble', None)
    values = next(case['features'] for case in client.get('/review-profiles').json() if case['id']=='a')
    response = client.post('/predict', json={'features': values, 'model_variant': 'calibrated_ensemble_v1'})
    assert response.status_code == 503
