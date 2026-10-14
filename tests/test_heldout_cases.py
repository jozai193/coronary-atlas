"""Check that the teaching UI presents actual saved outer-fold evidence."""
import json

from fastapi.testclient import TestClient

from backend.main import app
from ml.schema import ROOT, TARGETS
from scripts.build_heldout_cases import build_cases


def test_packaged_cases_reproduce_and_cover_cad_error_types():
    saved = json.loads((ROOT / 'data/processed/heldout_cases.json').read_text(encoding='utf-8'))
    assert saved == build_cases()
    assert len(saved['cases']) == 4
    assert {(item['targets']['cad']['label'], int(item['targets']['cad']['probability'] >= .5))
            for item in saved['cases']} == {(0, 0), (0, 1), (1, 0), (1, 1)}
    for item in saved['cases']:
        assert set(item['targets']) == set(TARGETS)
        assert len(item['observations']) == 4
        assert 'row_index' not in json.dumps(item)


def test_public_case_index_hides_truth_and_reveal_uses_saved_outer_fold(monkeypatch):
    def refuse_live_inference(*_args, **_kwargs):
        raise AssertionError('Held-out cases must not use the full-data predictor.')

    with TestClient(app) as client:
        monkeypatch.setattr(app.state.predictor, 'predict', refuse_live_inference)
        response = client.get('/api/held-out/cases')
        assert response.status_code == 200
        assert response.headers['cache-control'] == 'no-store'
        index = response.json()
        assert len(index['cases']) == 4
        assert all(set(case) == {'id', 'observations'} for case in index['cases'])
        assert 'probability' not in json.dumps(index['cases'])
        assert 'row_index' not in json.dumps(index)
        saved = json.loads((ROOT / 'data/processed/heldout_cases.json').read_text(encoding='utf-8'))
        for item in saved['cases']:
            for target in TARGETS:
                revealed = client.get(f'/api/held-out/cases/{item["id"]}/{target}')
                assert revealed.status_code == 200
                assert revealed.headers['cache-control'] == 'no-store'
                expected = item['targets'][target]
                assert revealed.json()['probability'] == expected['probability']
                assert revealed.json()['label'] == expected['label']
                assert revealed.json()['predicted_label'] == int(expected['probability'] >= .5)
                assert revealed.json()['fold'] == expected['fold'] + 1
                assert 'explanation' not in revealed.json()
        assert client.get('/api/held-out/cases/Z/cad').status_code == 404
        assert client.get('/api/held-out/cases/A/unknown').status_code == 422
