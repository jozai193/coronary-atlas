import copy,json
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from ml.schema import ROOT,FEATURES,PROHIBITED,NUMERIC,read_data

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:yield c

@pytest.fixture
def full(client):
    return next(s for s in client.get('/review-profiles').json() if s['id']=='a')['features']

@pytest.mark.parametrize('variant',['baseline','histgb_lcx_v2','calibrated_ensemble_v1'])
@pytest.mark.parametrize('missing',['Age','EF-TTE','VHD','Q Wave','St Elevation','St Depression','Tinversion','LVH','Poor R Progression','BBB'])
def test_critical_omission_blocks_every_model_before_inference(client,full,variant,missing,monkeypatch):
    called=[]
    monkeypatch.setattr(app.state.predictor,'predict',lambda _:called.append(True))
    full[missing]=None
    response=client.post('/api/predict',json={'features':full,'model_variant':variant})
    assert response.status_code==422 and 'Insufficient information' in response.json()['detail']
    assert not called

def test_complete_record_is_exact_source_and_can_predict(client,full):
    source=read_data().iloc[3]
    assert set(full)==set(FEATURES) and not set(full)&PROHIBITED
    assert all(full[f]==(float(source[f]) if f in NUMERIC else str(source[f])) for f in FEATURES)
    assert all(v is not None for v in full.values())
    response=client.post('/api/predict',json={'features':full})
    assert response.status_code==200,response.text
    assert response.json()['missing_features']==[]

def test_majority_required_even_with_critical_fields(client,full):
    keep=['Age','EF-TTE','VHD']+[n for n in FEATURES if n not in ['Age','EF-TTE','VHD','BMI','Weight','Length']][:24]
    partial={n:v if n in keep else None for n,v in full.items()}
    response=client.post('/predict',json={'features':partial})
    assert response.status_code==422
    assert '27/55' in response.json()['detail']

def test_incomplete_demo_is_not_silently_completed(client):
    for case in client.get('/review-profiles').json():
        incomplete={**case['features'],'VHD':None}
        response=client.post('/predict',json={'features':incomplete})
        assert response.status_code==422 and 'valve assessment' in response.json()['detail']
