import numpy as np
import pytest
from ml import accuracy_features as exp


def test_selection_and_spline_fit_on_training_only():
    X, y, _ = exp.base.source_data()
    tr, te = X.iloc[:150].copy(), X.iloc[150:155].copy()
    # Extreme evaluation values cannot alter learned statistics or knots.
    te['Age'] = 10000
    te['Sex'] = 'EVALUATION_ONLY'
    selected = exp.make_model({'arm': 'selected_ridge', 'percentile': 25, 'C': .03}).fit(tr, y[:150, 0])
    scores_before = selected.named_steps['select'].scores_.copy()
    assert np.isfinite(selected.predict_proba(te)).all()
    np.testing.assert_array_equal(scores_before, selected.named_steps['select'].scores_)
    numeric = selected.named_steps['preprocess'].named_transformers_['numeric']
    assert numeric.named_steps['impute'].statistics_[0] == np.median(tr.Age)
    spline = exp.make_model({'arm': 'spline_ridge', 'C': .03}).fit(tr, y[:150, 0])
    transformer = spline.named_steps['preprocess'].named_transformers_['numeric'].named_steps['spline']
    # The base age knot range is training-only; padded boundary knots extrapolate.
    knots = transformer.bsplines_[0].t.copy()
    assert knots.max() < 1000
    assert np.isfinite(spline.predict_proba(te)).all()
    np.testing.assert_array_equal(knots, transformer.bsplines_[0].t)


def test_unknown_feature_procedure_rejected():
    with pytest.raises(ValueError, match='Unknown procedure'):
        exp.make_model({'arm': 'unsupported', 'C': .03})


def test_forged_feature_predictions_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(exp, 'OUT', tmp_path)
    role = {'repeat': 1, 'fold': 0, 'target': 'cad'}
    manifest = {'roles': [role]}
    monkeypatch.setattr(exp, 'check_manifest', lambda: manifest)
    exp.write_json(tmp_path / 'manifest.json', manifest)
    path = tmp_path / 'predictions.csv'
    path.write_text('original')
    (tmp_path / 'private').mkdir()
    model = tmp_path / 'private/r1_f0_cad.joblib'
    model.write_text('model')
    selections = tmp_path / 'selections.json'
    selections.write_text('{}')
    monkeypatch.setattr(exp.base, 'OUT', tmp_path)
    receipt = {'manifest_sha256': exp.digest(tmp_path / 'manifest.json'),
        'baseline_predictions_sha256': exp.digest(path), 'completed_roles': 60,
        'files': {p.relative_to(tmp_path).as_posix(): exp.digest(p) for p in (path, model, selections)}}
    exp.write_json(tmp_path / 'fit_receipt.json', receipt)
    selections.write_text('{"forged":true}')
    with pytest.raises(ValueError, match='artifact changed'):
        exp.check_receipt()
