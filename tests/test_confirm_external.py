"""Read-only audit of the completed external experiment; never fit or tune."""
import json
import joblib
import numpy as np
import pandas as pd
from ml.schema import ROOT, digest, read_data
from ml.evaluate import metrics

OUT=ROOT/'ml/experiments/confirm_external_v1'


def test_external_evidence_and_frozen_app_snapshot_are_preserved():
    manifest=json.loads((OUT/'evidence_manifest.json').read_text())
    for file, sha in manifest.items():
        assert digest(OUT/file)==sha
    frozen=json.loads((ROOT/'data/external_audit/v3/frozen_models.json').read_text())
    for file, sha in frozen['sha256'].items():
        path=ROOT/'data/external_audit/v3/frozen_backend_main.txt' if file=='backend/main.py' else ROOT/file
        assert digest(path)==sha


def test_shared_model_preprocessing_is_source_only():
    fit=json.loads((OUT/'fit_manifest.json').read_text())
    assert fit['training_rows']==303 and fit['external_rows_used_for_fit']==0
    assert fit['features']==['Age','BMI','LDL','HDL']
    x=read_data()[fit['features']].to_numpy()
    for info in fit['targets'].values():
        model=joblib.load(OUT/info['file'])
        scaler=model.named_steps['standardscaler']
        assert scaler.n_samples_seen_==303
        np.testing.assert_allclose(scaler.mean_,x.mean(axis=0))
        np.testing.assert_allclose(model.named_steps['simpleimputer'].statistics_,np.median(x,axis=0))


def test_external_counts_and_metrics_reproduce_without_model_changes():
    result=json.loads((OUT/'results.json').read_text())
    for cohort, targets in result['cohorts'].items():
        for target, saved in targets.items():
            d=pd.read_csv(OUT/f'{cohort}_{target}.csv',float_precision='round_trip')
            assert d.workbook_row_index.is_unique and d.probability.between(0,1).all()
            assert len(d)==saved['rows'] and int(d.observed.sum())==saved['positive_rows']
            actual=metrics(d.observed,d.probability)
            for key in ['roc_auc','brier','recall','specificity','precision']:
                assert abs(actual[key]-saved[key])<1e-12
            assert actual['confusion_matrix']==saved['confusion_matrix']


def test_pre_scoring_mapping_amendment_is_explicit_and_hashed():
    stopped=json.loads((OUT/'attempt_1_stopped.json').read_text())
    assert stopped['external_predictions']==0
    fit=json.loads((OUT/'fit_manifest.json').read_text())
    result=json.loads((OUT/'results.json').read_text())
    assert digest(ROOT/'scripts/validate_confirm_external.py')==fit['runner_sha256']
    assert digest(ROOT/'docs/confirm_external_protocol.md')==fit['protocol_sha256']
    assert digest(ROOT/'scripts/validate_confirm_external_v2.py')==result['amended_runner_sha256']
    assert digest(ROOT/'docs/confirm_external_mapping_amendment.md')==result['mapping_amendment_sha256']
    assert result['label_diagnostic']['cad_vs_four_vessel_OR_mismatches']==0
