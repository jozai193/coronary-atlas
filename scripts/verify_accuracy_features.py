"""Reconstruct all candidate scores and replay selected feature models."""
import os
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss
from threadpoolctl import threadpool_limits
from ml import accuracy_features as exp


def main():
    manifest, receipt = exp.check_receipt()
    original = exp.base.load(exp.base.OUT / 'manifest.json')
    if manifest['roles'] != original['roles'] or manifest['specs'] != exp.SPECS:
        raise ValueError('Feature roles/configurations differ from frozen source')
    frame = pd.read_csv(exp.OUT / 'predictions.csv', float_precision='round_trip')
    if len(frame) != 3636 or frame.duplicated(['repeat', 'target', 'row']).any():
        raise ValueError('Incomplete or duplicate prediction rows')
    selections = exp.base.load(exp.OUT / 'selections.json')
    if len(selections) != 60:
        raise ValueError('Incomplete selections')
    X, y, groups = exp.base.source_data()
    count = 0
    with threadpool_limits(limits=1):
        for i, role in enumerate(manifest['roles']):
            tr, te = role['train'], role['test']
            ti = exp.base.ORDER.index(role['target'])
            exp.base.validate_splits(tr, te, groups, range(len(X)))
            artifact = joblib.load(exp.OUT / 'private' / (exp.base.role_name(role) + '.joblib'))
            record = selections[i]
            if record['role'] != exp.base.role_name(role):
                raise ValueError('Wrong selection role')
            scores = []
            for si, spec in enumerate(exp.SPECS):
                inner_scores = []
                for j, inner in enumerate(role['inner']):
                    exp.base.validate_splits(inner['train'], inner['test'], groups, tr)
                    model = artifact['inner_models'][si][j]
                    pp = model.predict_proba(X.iloc[inner['test']])[:, 1]
                    inner_scores.append(float(brier_score_loss(y[inner['test'], ti], pp)))
                    count += 1
                expected = {'spec': spec, 'fold_brier': inner_scores, 'mean_brier': float(np.mean(inner_scores))}
                if expected != record['scores'][si]:
                    raise ValueError('Inner candidate scores differ')
                scores.append(expected)
            stored = frame[(frame.repeat == role['repeat']) & (frame.fold == role['fold']) &
                           (frame.target == role['target'])].sort_values('row')
            np.testing.assert_array_equal(stored.row, te)
            np.testing.assert_array_equal(stored.y, y[te, ti])
            for arm in exp.ARMS:
                candidates = [k for k, spec in enumerate(exp.SPECS) if spec['arm'] == arm]
                best = min(candidates, key=lambda k: scores[k]['mean_brier'])
                if best != artifact['selected'][arm] or best != record['selected'][arm]:
                    raise ValueError('Wrong selected candidate')
                pp = artifact['full'][arm].predict_proba(X.iloc[te])[:, 1]
                np.testing.assert_allclose(pp, stored[arm], atol=1e-12, rtol=0)
            if (i + 1) % 10 == 0:
                print(f'Replayed {i+1}/60 feature roles', flush=True)
    if exp.results() != exp.base.load(exp.OUT / 'results.json'):
        raise ValueError('Feature results do not reproduce')
    report = {'status': 'passed', 'roles': 60, 'inner_predictions_replayed': count,
        'outer_models_replayed': 120, 'prediction_rows': len(frame),
        'results_sha256': exp.digest(exp.OUT / 'results.json'),
        'fit_receipt_sha256': exp.digest(exp.OUT / 'fit_receipt.json'),
        'verifier_sha256': exp.digest(Path(__file__))}
    exp.write_json(exp.OUT / 'verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
