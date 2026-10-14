"""Training-boundary, optimizer and evidence-integrity regression checks."""
import numpy as np
import pytest
from ml import accuracy_ensemble as exp
from ml.preprocessing import pipeline


def test_identical_input_groups_cannot_cross_boundary():
    with pytest.raises(ValueError, match='Identical inputs'):
        exp.validate_splits([0, 1], [2, 3], np.array([8, 9, 8, 10]), range(4))
    with pytest.raises(ValueError, match='overlap'):
        exp.validate_splits([0, 1], [1, 2], np.arange(4), range(4))
    exp.validate_splits([0, 1], [2, 3], np.arange(4), range(4))


def test_simplex_never_uses_negative_or_unbounded_weights():
    y = np.tile([0, 1], 30)
    p = np.column_stack([.1 + .8 * y, .9 - .8 * y, np.full(len(y), .5)])
    weights = exp.blend_weights(p, y)
    assert np.all(weights >= -1e-10)
    assert weights.sum() == pytest.approx(1)
    assert weights[0] > .9
    assert np.mean((p @ weights - y) ** 2) < np.mean((p.mean(axis=1) - y) ** 2)


def test_fold_local_imputation_and_unseen_category():
    X, y, _ = exp.source_data()
    train = X.iloc[:100].copy()
    test = X.iloc[100:105].copy()
    train.loc[train.index[0], 'Age'] = np.nan
    test['Age'] = 1e8
    test['Sex'] = 'UNSEEN_TEST_CATEGORY'
    fitted = pipeline('logistic', .03).fit(train, y[:100, 0])
    numeric = fitted.named_steps['preprocess'].named_transformers_['numeric']
    assert numeric.named_steps['impute'].statistics_[0] == np.nanmedian(train.Age)
    encoder = fitted.named_steps['preprocess'].named_transformers_['categorical'].named_steps['encode']
    assert all('UNSEEN_TEST_CATEGORY' not in cats for cats in encoder.categories_)
    assert np.isfinite(fitted.predict_proba(test)).all()


def test_forged_saved_artifact_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(exp, 'OUT', tmp_path)
    monkeypatch.setattr(exp, 'assert_hashes', lambda mapping: None)
    manifest = {'input_hashes': {}, 'protected_hashes': {}, 'roles': []}
    exp.write_json(tmp_path / 'manifest.json', manifest)
    prediction = tmp_path / 'predictions.csv'
    prediction.write_text('original')
    exp.write_json(tmp_path / 'fit_receipt.json', {
        'manifest_sha256': exp.digest(tmp_path / 'manifest.json'), 'completed_roles': 0,
        'files': {'predictions.csv': exp.digest(prediction)}})
    prediction.write_text('forged')
    with pytest.raises(ValueError, match='artifact changed'):
        exp.check_receipt()


def test_repeat_bootstrap_does_not_multiply_patient_count():
    patient_deltas = np.array([-.1, .05, -.03, .01])
    summary = exp.bootstrap(patient_deltas)
    assert summary['mean'] == pytest.approx(patient_deltas.mean())
    assert summary == exp.bootstrap(patient_deltas)
