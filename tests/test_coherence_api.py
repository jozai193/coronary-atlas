"""API evidence and explanation boundaries for the coherence adjustment."""
import json

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from ml.coherence import project_probabilities
from ml.schema import ROOT


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_baseline_reports_both_adjusted_and_shap_explained_probabilities(client):
    # Complete explicit regression inputs, not a clinical example: preserve the
    # historical discordant synthetic vector and supply its missing fields.
    source = next(case['features'] for case in client.get('/review-profiles').json() if case['id']=='a')
    features = {name:value if value is not None else source[name]
                for name,value in client.get('/sample-patients').json()[0]['features'].items()}
    response = client.post('/api/predict', json={'features': features})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['model_version'] == '1.0.0+coherence-v1'
    targets = ('cad', 'lad', 'lcx', 'rca')
    original = app.state.predictor.predict(payload['input_snapshot'])
    raw = np.array([original[t]['probability'] for t in targets])
    expected = project_probabilities(raw)

    assert payload['coherence_adjustment']['enabled'] is True
    assert payload['coherence_adjustment']['method'] == 'euclidean_projection'
    assert payload['coherence_adjustment']['changed_targets']
    assert payload['coherence_adjustment']['changed_targets'] == [
        t for t, adjusted, unadjusted in zip(targets, expected, raw)
        if abs(adjusted - unadjusted) > 1e-12
    ]
    assert payload['coherence_adjustment']['max_absolute_change'] == pytest.approx(np.max(np.abs(expected - raw)))
    assert payload['cad']['probability'] >= max(payload[t]['probability'] for t in targets[1:])
    for index, target in enumerate(targets):
        prediction = payload[target]
        assert prediction['model_probability'] == pytest.approx(raw[index])
        assert prediction['probability'] == pytest.approx(expected[index])
        assert prediction['classification'] == int(expected[index] >= .5)
        assert prediction['category'] == ('Lower' if expected[index] < .3 else 'Intermediate' if expected[index] < .7 else 'Higher')
        explanation = prediction['explanation']
        raw_output = explanation['base_value'] + sum(f['contribution'] for f in explanation['factors'])
        reconstructed = raw_output if explanation['unit'] == 'probability' else 1 / (1 + np.exp(-raw_output))
        assert reconstructed == pytest.approx(prediction['model_probability'], abs=1e-4)
    assert any('SHAP factors explain the unadjusted' in warning for warning in payload['warnings'])


@pytest.mark.parametrize('cad_raw,lad_raw,boundary', [
    (.49, .53, 'classification'),
    (.29, .33, 'lower_band'),
    (.69, .73, 'higher_band'),
])
def test_displayed_class_and_category_follow_projection_across_boundary(client, monkeypatch,
                                                                          cad_raw, lad_raw, boundary):
    raw_probabilities = dict(cad=cad_raw, lad=lad_raw, lcx=.1, rca=.1)

    def fake_raw_models(_features):
        results = {}
        for target, probability in raw_probabilities.items():
            log_odds = float(np.log(probability / (1 - probability)))
            results[target] = {
                'probability': probability,
                'classification': int(probability >= .5),
                'category': 'Lower' if probability < .3 else 'Intermediate' if probability < .7 else 'Higher',
                'model': 'logistic',
                'explanation': {
                    'method': 'test raw-model attribution', 'unit': 'log-odds',
                    'base_value': log_odds, 'output_value': log_odds,
                    'additivity_error': 0, 'factors': [], 'note': 'Explains raw model output.',
                },
            }
        return results

    monkeypatch.setattr(app.state.predictor, 'predict', fake_raw_models)
    features = next(case['features'] for case in client.get('/review-profiles').json() if case['id']=='a')
    response = client.post('/predict', json={'features': features})
    assert response.status_code == 200, response.text
    prediction = response.json()['cad']
    expected = (cad_raw + lad_raw) / 2
    assert prediction['model_probability'] == pytest.approx(cad_raw)
    assert prediction['probability'] == pytest.approx(expected)
    assert prediction['classification'] == int(expected >= .5)
    assert prediction['category'] == ('Lower' if expected < .3 else 'Intermediate' if expected < .7 else 'Higher')
    reconstructed = 1 / (1 + np.exp(-prediction['explanation']['base_value']))
    assert reconstructed == pytest.approx(prediction['model_probability'])
    assert reconstructed != pytest.approx(prediction['probability'])
    if boundary == 'classification':
        assert cad_raw < .5 <= prediction['probability']
    elif boundary == 'lower_band':
        assert cad_raw < .3 <= prediction['probability']
    else:
        assert cad_raw < .7 <= prediction['probability']


def test_coherence_evidence_endpoint_is_compact_and_matches_saved_run(client):
    source = json.loads((ROOT / 'ml/experiments/coherence_v1/results.json').read_text(encoding='utf-8'))
    response = client.get('/model/coherence')
    assert response.status_code == 200, response.text
    evidence = response.json()
    assert evidence == client.get('/api/model/coherence').json()
    assert evidence['scope'] == source['scope']
    assert evidence['method'] == 'euclidean_projection'
    assert evidence['rows'] == 303
    assert evidence['screen_passed'] == source['screen']['passed']
    assert evidence['mean_four_target_brier_delta'] == source['screen']['mean_four_target_brier_delta']
    assert len(evidence['repeats']) == len(source['repeats']) == 2
    for displayed, saved in zip(evidence['repeats'], source['repeats']):
        summary = saved['summary']
        assert displayed == {
            'repeat': saved['repeat'],
            'raw_mean_four_target_brier': summary['mean_four_target_brier_raw'],
            'adjusted_mean_four_target_brier': summary['mean_four_target_brier_projected'],
            'adjusted_rows': summary['changed_rows'],
            'discordant_rows_raw': summary['discordant_rows_raw'],
            'discordant_rows_adjusted': summary['discordant_rows_projected'],
        }
    assert 'folds' not in evidence
    assert 'train_indices' not in response.text


def test_projection_cannot_raise_total_squared_error_for_coherent_labels():
    rng = np.random.default_rng(20261008)
    coherent_labels = [np.array([int(any(vessels)), *vessels])
                       for vessels in np.ndindex(2, 2, 2)]
    for probabilities in rng.random((100, 4)):
        adjusted = project_probabilities(probabilities)
        assert adjusted[0] >= max(adjusted[1:]) - 1e-12
        for labels in coherent_labels:
            assert np.sum((adjusted - labels) ** 2) <= np.sum((probabilities - labels) ** 2) + 1e-12
