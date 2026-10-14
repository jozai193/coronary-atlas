import copy
import json
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from ml.schema import *
from ml.preprocessing import pipeline, check_features
from ml.predict import Predictor


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def features(client):
    # Explicit test-only valve category; historical sample fixtures remain unchanged.
    return next(case['features'] for case in client.get('/review-profiles').json() if case['id']=='a')


def test_no_target_leakage():
    assert not set(FEATURES)&PROHIBITED
    assert len(FEATURES)==55
    for target in PROHIBITED:
        with pytest.raises(ValueError):
            check_features(FEATURES+[target])
    check_features(read_data()[FEATURES].columns)


def test_imputation_is_fit_on_training_only():
    X=read_data()[FEATURES].iloc[:70].copy()
    X.loc[X.index[:10],'Age']=np.nan
    fitted=pipeline('logistic').fit(X,np.arange(len(X))%2)
    imp=fitted.named_steps['preprocess'].named_transformers_['numeric'].named_steps['impute']
    assert imp.statistics_[NUMERIC.index('Age')]==X.Age.median()
    test=X.iloc[[0]].copy(); test['Age']=10000; test['BBB']='UNSEEN'
    assert np.isfinite(fitted.predict_proba(test)).all()
    assert imp.statistics_[NUMERIC.index('Age')]==X.Age.median()


def test_saved_folds_are_disjoint_and_cover_every_row():
    evaluation=json.loads((ROOT/'ml/metrics/evaluation.json').read_text())
    for target in evaluation['targets'].values():
        seen=[]
        for fold in target['folds']:
            assert not set(fold['train_indices']) & set(fold['test_indices'])
            assert len(fold['train_indices'])+len(fold['test_indices'])==303
            seen+=fold['test_indices']
        assert sorted(seen)==list(range(303))


def test_prediction_contract_determinism_and_shap(client,features):
    a=client.post('/predict',json={'features':features}); b=client.post('/api/predict',json={'features':features})
    assert a.status_code==200, a.text
    assert a.json()==b.json()
    payload=a.json()
    assert payload['input_snapshot'].keys()==set(FEATURES)
    for target in TARGETS:
        result=payload[target]
        assert 0<=result['probability']<=1
        assert result['classification']==int(result['probability']>=.5)
        ex=result['explanation']
        assert ex['additivity_error']<1e-4
        assert {x['feature'] for x in ex['factors']}==set(FEATURES)
        value=ex['base_value']+sum(x['contribution'] for x in ex['factors'])
        reconstructed=value if ex['unit']=='probability' else 1/(1+np.exp(-value))
        assert abs(reconstructed-result['model_probability'])<1e-4
    assert payload['cad']['probability'] >= max(payload[v]['probability'] for v in ('lad','lcx','rca'))
    assert payload['coherence_adjustment']['enabled'] is True
    assert a.headers['cache-control']=='no-store'


def test_unknown_echo_stays_null_and_recorded_zero_ecg_is_not_missing(client,features):
    values=features.copy();values['Region RWMA']=None;values['Q Wave']='0'
    r=client.post('/api/predict',json={'features':values})
    assert r.status_code==200,r.text
    p=r.json()
    assert p['input_snapshot']['Region RWMA'] is None and 'Region RWMA' in p['missing_features']
    assert p['input_snapshot']['Q Wave']=='0' and 'Q Wave' not in p['missing_features']
    assert any('imputed' in note for note in p['warnings'])


@pytest.mark.parametrize('field,value',[('Cath','CAD'),('LAD','Normal'),('LCX','Normal'),('RCA','Normal'),('patient_name','Test'),('Sex','unknown'),('BP','120'),('Age',True),('Age',-2),('DM',2),('BBB',{}),('VHD',[])])
def test_bad_inputs(client,features,field,value):
    features[field]=value
    assert client.post('/predict',json={'features':features}).status_code==422


def test_empty_and_missing(client,features):
    assert client.post('/predict',json={'features':{}}).status_code==422
    features['Age']=None
    assert client.post('/predict',json={'features':features}).status_code==422
    features['Age']=42; features['BP']=None; features['FH']=None
    p=client.post('/predict',json={'features':features})
    assert p.status_code==200,p.text
    assert set(p.json()['missing_features'])=={name for name,value in features.items() if value is None}
    assert any('imputed' in w for w in p.json()['warnings'])


def test_missing_critical_echo_blocks_and_missing_labs_remain_disclosed(client,features):
    baseline=client.post('/predict',json={'features':features})
    assert baseline.status_code==200,baseline.text
    assert not any('laboratory observations are missing' in w or 'echocardiography observations are missing' in w
                   for w in baseline.json()['warnings'])

    incomplete=features.copy()
    for name in GROUPS['Laboratory']+GROUPS['Echocardiography']:
        incomplete[name]=None
    result=client.post('/predict',json={'features':incomplete})
    assert result.status_code==422,result.text
    assert 'echo EF' in result.json()['detail'] and 'valve assessment' in result.json()['detail']
    incomplete['EF-TTE']=features['EF-TTE']
    incomplete['VHD']=features['VHD']
    partial=client.post('/predict',json={'features':incomplete})
    assert partial.status_code==200,partial.text
    assert any('All laboratory observations are missing' in w for w in partial.json()['warnings'])
    incomplete[GROUPS['Laboratory'][0]]=features[GROUPS['Laboratory'][0]]
    partial=client.post('/predict',json={'features':incomplete})
    assert partial.status_code==200,partial.text
    assert not any('All laboratory observations are missing' in w or 'All echocardiography observations are missing' in w
                   for w in partial.json()['warnings'])


def test_schema_and_health(client):
    schema=client.get('/model/info').json()
    assert [f['name'] for f in schema['features']]==FEATURES
    assert client.get('/health').json()['models']==list(TARGETS)
    assert 'PredictionResponse' in client.get('/openapi.json').json()['components']['schemas']


def test_model_corruption_rejected(tmp_path):
    import shutil
    shutil.copytree(ROOT/'models',tmp_path/'models')
    path=tmp_path/'models/cad.joblib'; path.write_bytes(b'corrupt')
    with pytest.raises(ValueError,match='integrity'):
        Predictor(tmp_path/'models')


def test_out_of_range_inputs_are_rejected(client,features):
    features['Age']=90
    result=client.post('/predict',json={'features':features})
    assert result.status_code==422
    assert 'Age' in result.json()['detail']
    assert '30' in result.json()['detail']
    features['Age']=42
    features['WBC']=7.1  # A thousands-per-microliter entry in a cells-per-microliter field.
    result=client.post('/predict',json={'features':features})
    assert result.status_code==422
    assert 'WBC' in result.json()['detail']


def test_extreme_finite_inputs_do_not_receive_predictions(client,features):
    features['Age']=1000000
    result=client.post('/predict',json={'features':features})
    assert result.status_code==422
    assert 'supported estimate' in result.json()['detail']


def test_bmi_is_derived_and_conflicts_are_rejected(client,features):
    source=read_data()
    assert np.allclose(source['BMI'],source['Weight']/(source['Length']/100)**2,rtol=0,atol=1e-12)
    computed=features['Weight']/(features['Length']/100)**2
    features['BMI']=None
    derived=client.post('/predict',json={'features':features})
    assert derived.status_code==200,derived.text
    payload=derived.json()
    assert payload['input_snapshot']['BMI']==pytest.approx(computed)
    assert 'BMI' not in payload['missing_features']
    assert any('BMI was calculated' in w for w in payload['warnings'])

    features['BMI']=round(computed,1)
    rounded=client.post('/predict',json={'features':features})
    assert rounded.status_code==200,rounded.text
    assert rounded.json()['input_snapshot']['BMI']==pytest.approx(computed)

    # The actual source minimum BMI rounds just below its exact range bound.
    features.update({'Weight':62,'Length':185,'BMI':18.1})
    boundary=client.post('/predict',json={'features':features})
    assert boundary.status_code==200,boundary.text
    assert boundary.json()['input_snapshot']['BMI']==pytest.approx(62/(1.85**2))

    features['BMI']=computed+1
    conflict=client.post('/predict',json={'features':features})
    assert conflict.status_code==422
    assert 'does not match' in conflict.json()['detail']


def test_derived_bmi_must_also_be_in_observed_range(client,features):
    features.update({'Weight':120,'Length':140,'BMI':None})
    result=client.post('/predict',json={'features':features})
    assert result.status_code==422
    assert 'BMI calculated' in result.json()['detail']


def test_nonfinite_and_extra_top_level_fields(client,features):
    raw=json.dumps({'features':{**features,'Age':float('nan')}})
    assert client.post('/predict',content=raw,headers={'Content-Type':'application/json'}).status_code==422
    assert client.post('/predict',json={'features':features,'Cath':'Normal'}).status_code==422
