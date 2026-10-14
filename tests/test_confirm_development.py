"""Verify isolation, fit provenance, fixed selection and prediction evidence."""
import json
import joblib
import numpy as np
import pandas as pd
import pytest
from ml.schema import ROOT, digest
from ml.evaluate import metrics
from scripts.develop_confirm import OUT, NUM, CAT, RAW, cutoff90, split_role, load_inputs


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def test_cutoff_handles_ties_and_hits_requested_calibration_sensitivity():
    y = np.array([1]*11+[0]*7)
    p = np.array([.01, .02, .02, .1, .2, .3, .4, .5, .6, .7, .8]+[.1]*7)
    cutoff = cutoff90(y, p)
    assert cutoff == .02
    assert np.mean(p[y == 1] >= cutoff) >= .9
    assert split_role(42) == split_role(42.0) == split_role('42')


def test_development_evidence_and_frozen_app_snapshot_are_preserved():
    prepared = read(OUT/'prepared.json')
    assert digest(ROOT/'scripts/develop_confirm.py') == prepared['runner_sha256']
    assert digest(ROOT/'docs/confirm_development_protocol.md') == prepared['protocol_sha256']
    assert digest(OUT/'partitions.csv') == prepared['partition_sha256']
    for name, expected in read(OUT/'evidence_manifest.json').items():
        assert digest(OUT/name) == expected, name
    old = ROOT/'ml/experiments/confirm_external_v1'
    assert digest(old/'evidence_manifest.json') == prepared['historical_manifest_sha256']
    for name, expected in read(old/'evidence_manifest.json').items():
        assert digest(old/name) == expected
    for name, expected in read(ROOT/'data/external_audit/v3/frozen_models.json')['sha256'].items():
        path=ROOT/'data/external_audit/v3/frozen_backend_main.txt' if name=='backend/main.py' else ROOT/name
        assert digest(path) == expected


def test_partition_selection_thresholds_and_metrics_are_reproducible():
    split = pd.read_csv(OUT/'partitions.csv').set_index('workbook_row_index')
    assert split.index.is_unique and set(split.partition) == {'train', 'calibration', 'test'}
    fit = read(OUT/'fit_manifest.json')
    results = read(OUT/'results.json')
    for key, info in fit['experiments'].items():
        train, cal = set(info['train_rows']), set(info['calibration_rows'])
        test = pd.read_csv(OUT/f'{key}_test.csv', float_precision='round_trip')
        assert not train & cal and not (train | cal) & set(test.workbook_row_index)
        assert split.loc[list(train), 'partition'].eq('train').all()
        assert split.loc[list(cal), 'partition'].eq('calibration').all()
        assert split.loc[test.workbook_row_index, 'partition'].eq('test').all()
        assert info['selected_family'] == min(info['cv_brier'], key=lambda n: np.mean(info['cv_brier'][n]))
        calibration = pd.read_csv(OUT/f'{key}_calibration.csv', float_precision='round_trip')
        assert set(calibration.workbook_row_index) == cal
        for name, threshold in info['cutoffs_90'].items():
            assert cutoff90(calibration.observed, calibration[name]) == threshold
            p = test[name]
            assert p.between(0, 1).all()
            expected = results['experiments'][key]['models'][name]
            actual = metrics(test.observed, p)
            for metric in ['roc_auc', 'brier', 'log_loss', 'recall', 'specificity']:
                assert abs(actual[metric]-expected[metric]) < 1e-12
            assert actual['confusion_matrix'] == expected['confusion_matrix']
        if info['arm'] != 'clinical_available':
            assert split.loc[test.workbook_row_index, 'complete'].eq(1).all()
    for target in ['cad', 'lad', 'lcx', 'rca']:
        a = pd.read_csv(OUT/f'four_complete_{target}_test.csv')
        b = pd.read_csv(OUT/f'clinical_complete_{target}_test.csv')
        assert a.workbook_row_index.equals(b.workbook_row_index)
        assert a.observed.equals(b.observed)


@pytest.mark.skipif(not RAW.exists(), reason='Raw licensed workbook is local-only.')
def test_preprocessing_and_predictions_use_frozen_training_rows_only():
    d, x, _, _ = load_inputs()
    split = pd.read_csv(OUT/'partitions.csv').set_index('workbook_row_index')
    assert d.loc[split.index, 'confirm_id'].map(split_role).to_list() == split.partition.to_list()
    fit = read(OUT/'fit_manifest.json')
    for key, info in fit['experiments'].items():
        bundle = joblib.load(OUT/f'{key}.joblib')
        prep = bundle['selected'].steps[0][1]
        assert prep.remainder == 'drop'
        cols = [col for _, transformer, columns in prep.transformers_
                if transformer != 'drop' and isinstance(columns, list) for col in columns]
        assert cols == NUM + (CAT if info['arm'] != 'four_complete' else [])
        imputer = prep.named_transformers_['numeric'].steps[0][1]
        np.testing.assert_allclose(imputer.statistics_, x.loc[info['train_rows'], NUM].median().to_numpy())
        if info['selected_family'] == 'logistic':
            scaler = prep.named_transformers_['numeric'].steps[-1][1]
            assert scaler.n_samples_seen_ == len(info['train_rows'])
        test = pd.read_csv(OUT/f'{key}_test.csv', float_precision='round_trip')
        predicted = bundle['selected'].predict_proba(x.loc[test.workbook_row_index])[:, 1]
        np.testing.assert_allclose(predicted, test.selected_raw, atol=1e-12)
        if info['arm'] == 'four_complete':
            changed = x.loc[test.workbook_row_index].copy()
            changed[CAT] = -999
            np.testing.assert_array_equal(bundle['selected'].predict_proba(changed)[:, 1], predicted)
