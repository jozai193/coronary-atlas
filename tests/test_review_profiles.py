import json
from fastapi.testclient import TestClient
from backend.main import app,validate_features
from ml.schema import ROOT,FEATURES,NUMERIC,read_data
from scripts.create_review_profiles import create


def test_judge_profiles_are_complete_exact_source_rows_with_disclosed_selection():
    profiles=create();saved=json.loads((ROOT/'data/processed/reviewer_samples_v2.json').read_text(encoding='utf-8'))
    assert profiles==saved and [s['id'] for s in profiles]==['a','b']
    frame=read_data();schema=json.loads((ROOT/'models/metadata.json').read_text(encoding='utf-8'))['feature_schema']
    assert [s['source']['record_index'] for s in profiles]==[3,5]
    for sample in profiles:
        row=frame.iloc[sample['source']['record_index']]
        assert sample['features']=={c:float(row[c]) if c in NUMERIC else str(row[c]) for c in FEATURES}
        assert not sample['synthetic'] and sample['source']['used_in_development']
        assert not validate_features(sample['features'],schema)[1]
        assert set(sample['provenance']['recorded_fields'])==set(FEATURES)
        assert sample['provenance']['default_fields']==sample['provenance']['unknown_fields']==[]
    assert profiles[0]['recorded_outcomes']==dict(cad='Normal',lad='Normal',lcx='Normal',rca='Normal')
    assert profiles[1]['recorded_outcomes']==dict(cad='CAD',lad='Stenotic',lcx='Stenotic',rca='Stenotic')
    with TestClient(app) as client:
        assert client.get('/api/review-profiles').json()==saved
        for sample in saved:
            response=client.post('/api/predict',json={'features':sample['features']})
            assert response.status_code==200,response.text
            assert not response.json()['missing_features']
