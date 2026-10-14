"""Prespecified nested feature selection and spline research procedures."""
import os
for _key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'
import argparse
import time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectPercentile, f_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler
from threadpoolctl import threadpool_limits
from ml import accuracy_ensemble as base
from ml.preprocessing import pipeline
from ml.schema import ROOT, digest, write_json

OUT = ROOT / 'ml/experiments/accuracy_features_v1'
ARMS = ('selected_ridge', 'spline_ridge')
SPECS = ({'arm': 'selected_ridge', 'percentile': p, 'C': c} for p in (25, 50, 100) for c in (.01, .03, .1))
SPECS = list(SPECS) + [{'arm': 'spline_ridge', 'C': c} for c in (.01, .03, .1)]


def make_model(spec):
    model = pipeline('logistic', spec['C'])
    if spec['arm'] == 'selected_ridge':
        model.steps.insert(1, ('select', SelectPercentile(f_classif, percentile=spec['percentile'])))
    elif spec['arm'] == 'spline_ridge':
        numeric = Pipeline([('impute', SimpleImputer(strategy='median', keep_empty_features=True)),
            ('spline', SplineTransformer(n_knots=4, degree=2, include_bias=False,
                                         knots='quantile', extrapolation='linear')),
            ('scale', StandardScaler())])
        model.set_params(preprocess__numeric=numeric)
    else:
        raise ValueError('Unknown procedure')
    return model


def prepare():
    if OUT.exists():
        raise FileExistsError('Refusing overwrite')
    original = base.load(base.OUT / 'manifest.json')
    base.assert_hashes(original['input_hashes'])
    manifest = {'base_manifest_sha256': digest(base.OUT / 'manifest.json'),
        'input_hashes': {p.relative_to(ROOT).as_posix(): digest(p) for p in
                        (Path(__file__), ROOT / 'docs/accuracy_features_protocol.md')},
        'specs': SPECS, 'roles': original['roles'], 'scope': original['scope']}
    (OUT / 'private').mkdir(parents=True)
    write_json(OUT / 'manifest.json', manifest)
    print('Feature protocol and 60 roles frozen', flush=True)


def check_manifest():
    manifest = base.load(OUT / 'manifest.json')
    base.assert_hashes(manifest['input_hashes'])
    if digest(base.OUT / 'manifest.json') != manifest['base_manifest_sha256']:
        raise ValueError('Base partitions changed')
    base.check_receipt()
    return manifest


def fit():
    manifest = check_manifest()
    if any((OUT / 'private').iterdir()) or (OUT / 'fit_receipt.json').exists():
        raise FileExistsError('Refusing fit overwrite')
    X, y, _ = base.source_data()
    started = time.monotonic()
    files, rows, choices = {}, [], []
    import warnings
    with threadpool_limits(limits=1), warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        for ri, role in enumerate(manifest['roles'], 1):
            if time.monotonic() - started > 30 * 60:
                raise TimeoutError('Frozen fitting budget exceeded')
            ti = base.ORDER.index(role['target'])
            scores, inner_models = [], []
            for spec in SPECS:
                inner_scores, fitted = [], []
                for item in role['inner']:
                    tr, va = item['train'], item['test']
                    model = make_model(spec).fit(X.iloc[tr], y[tr, ti])
                    pp = model.predict_proba(X.iloc[va])[:, 1]
                    inner_scores.append(float(brier_score_loss(y[va, ti], pp)))
                    fitted.append(model)
                scores.append({'spec': spec, 'fold_brier': inner_scores, 'mean_brier': float(np.mean(inner_scores))})
                inner_models.append(fitted)
            selected, full = {}, {}
            tr, te = role['train'], role['test']
            prediction = {}
            for arm in ARMS:
                eligible = [i for i, spec in enumerate(SPECS) if spec['arm'] == arm]
                best = min(eligible, key=lambda i: scores[i]['mean_brier'])
                selected[arm] = best
                full[arm] = make_model(SPECS[best]).fit(X.iloc[tr], y[tr, ti])
                prediction[arm] = full[arm].predict_proba(X.iloc[te])[:, 1]
            path = OUT / 'private' / (base.role_name(role) + '.joblib')
            joblib.dump({'full': full, 'selected': selected, 'inner_models': inner_models}, path, compress=3)
            files[path.relative_to(OUT).as_posix()] = digest(path)
            choices.append({'role': base.role_name(role), 'selected': selected, 'scores': scores})
            for i, row in enumerate(te):
                rows.append({'repeat': role['repeat'], 'fold': role['fold'], 'target': role['target'],
                    'row': row, 'y': int(y[row, ti]), **{arm: float(prediction[arm][i]) for arm in ARMS}})
            print(f'{ri}/60 {base.role_name(role)} saved; {time.monotonic()-started:.1f}s', flush=True)
        warning_counts = {}
        for warning in caught:
            key = str(warning.message)
            warning_counts[key] = warning_counts.get(key, 0) + 1
    pd.DataFrame(rows).to_csv(OUT / 'predictions.csv', index=False)
    write_json(OUT / 'selections.json', choices)
    files.update({name: digest(OUT / name) for name in ('predictions.csv', 'selections.json')})
    write_json(OUT / 'fit_receipt.json', {'manifest_sha256': digest(OUT / 'manifest.json'), 'files': files,
        'baseline_predictions_sha256': digest(base.OUT / 'predictions.csv'),
        'completed_roles': len(manifest['roles']), 'seconds': time.monotonic()-started,
        'warning_counts': warning_counts})


def check_receipt():
    manifest = check_manifest()
    receipt = base.load(OUT / 'fit_receipt.json')
    if digest(OUT / 'manifest.json') != receipt['manifest_sha256']:
        raise ValueError('Feature manifest changed')
    if digest(base.OUT / 'predictions.csv') != receipt['baseline_predictions_sha256']:
        raise ValueError('Baseline changed')
    expected = {'predictions.csv', 'selections.json'} | {'private/' + base.role_name(r) + '.joblib' for r in manifest['roles']}
    if set(receipt['files']) != expected or receipt['completed_roles'] != 60:
        raise ValueError('Incomplete feature receipt')
    for name, sha in receipt['files'].items():
        if digest(OUT / name) != sha:
            raise ValueError(f'Feature artifact changed: {name}')
    return manifest, receipt


def results():
    f = pd.read_csv(OUT / 'predictions.csv', float_precision='round_trip')
    baseline = pd.read_csv(base.OUT / 'predictions.csv', float_precision='round_trip')
    keys = ['repeat', 'fold', 'target', 'row', 'y']
    joined = f.merge(baseline[keys + ['baseline']], on=keys, how='outer', validate='one_to_one', indicator=True)
    if not (joined._merge == 'both').all():
        raise ValueError('Unmatched baseline rows')
    joined = joined.drop(columns='_merge')
    # Reuse metric and bootstrap definitions with explicit stage-specific arms.
    original = base.ARMS
    try:
        base.ARMS = ('baseline',) + ARMS
        summary = base.summarize(joined)
    finally:
        base.ARMS = original
    for arm in ARMS:
        summary['comparisons'][arm]['primary'] = arm == 'selected_ridge'
    return summary


def evaluate():
    if (OUT / 'results.json').exists():
        raise FileExistsError('Refusing results overwrite')
    check_receipt()
    result = results()
    write_json(OUT / 'results.json', result)
    import json
    print(json.dumps(result['comparisons'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'fit', 'evaluate'])
    globals()[parser.parse_args().stage]()
