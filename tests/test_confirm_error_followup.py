import numpy as np
import pandas as pd
from scripts.confirm_error_followup import OUT,PREVIOUS,PROTOCOL,read_json,digest
from ml.evaluate import metrics
from scripts.develop_confirm import confusion

def test_frozen_followup_and_previous_artifacts():
    frozen=read_json(OUT/'frozen.json')
    assert digest(PROTOCOL)==frozen['protocol']
    assert digest(PROTOCOL.parents[1]/'scripts/confirm_error_followup.py')==frozen['runner']
    assert digest(PREVIOUS/'evidence_manifest.json')==frozen['previous_manifest']
    for folder in [OUT,PREVIOUS]:
        for file,sha in read_json(folder/'evidence_manifest.json').items():
            assert digest(folder/file)==sha

def test_only_training_patients_and_disjoint_validation():
    original=read_json(PREVIOUS/'fit_manifest.json')['experiments']
    for target,result in read_json(OUT/'results.json').items():
        evidence=pd.read_csv(OUT/f'{target}_training_oof.csv',float_precision='round_trip')
        expected=set(original['clinical_available_'+target]['train_rows'])
        assert evidence.row_index.is_unique and set(evidence.row_index)==expected
        all_validation=[]
        for fold in result['folds']:
            assert not set(fold['train'])&set(fold['validation'])
            assert set(fold['train'])|set(fold['validation'])==expected
            all_validation+=fold['validation']
        assert len(all_validation)==len(set(all_validation))==len(expected)
        for name,m in result['methods'].items():
            actual=metrics(evidence.observed,evidence[name])
            assert abs(actual['brier']-m['brier'])<1e-12
            assert abs(actual['roc_auc']-m['roc_auc'])<1e-12
            assert confusion(evidence.observed,evidence[name+'_decision'],.5)==m['nested_cutoff']
            for fold in result['folds']:
                rows=evidence.set_index('row_index').loc[fold['validation']]
                np.testing.assert_array_equal(rows[name]>=fold['cutoffs'][name],rows[name+'_decision'].astype(bool))
        for prefix in ['full','core']:
            np.testing.assert_allclose(evidence[prefix+'_average'],(evidence[prefix+'_linear']+evidence[prefix+'_spline'])/2)
