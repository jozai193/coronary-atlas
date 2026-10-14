"""Fresh-process replay of every saved outer and inner fold prediction."""
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
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from threadpoolctl import threadpool_limits
from ml import accuracy_ensemble as exp


def main():
    manifest, receipt = exp.check_receipt()
    X, y, groups = exp.source_data()
    frame = pd.read_csv(exp.OUT / 'predictions.csv', float_precision='round_trip')
    if frame.duplicated(['repeat', 'target', 'row']).any() or len(frame) != 3 * 4 * 303:
        raise ValueError('Duplicate/missing prediction records')
    if set(frame.repeat) != {1, 2, 3} or set(frame.target) != set(exp.ORDER):
        raise ValueError('Unexpected prediction keys')
    expected_roles = [(r, f, t) for r in range(1, 4) for f in range(5) for t in exp.ORDER]
    if [(r['repeat'], r['fold'], r['target']) for r in manifest['roles']] != expected_roles:
        raise ValueError('Missing/duplicate/reordered roles')
    outer = {}
    for repeat, seed in enumerate(exp.SEEDS, 1):
        outer[repeat] = list(StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(X, y[:, 0], groups))
    max_residual = 0.
    inner_count = 0
    with threadpool_limits(limits=1):
        for index, role in enumerate(manifest['roles'], 1):
            tr, te = np.array(role['train']), np.array(role['test'])
            ti = exp.ORDER.index(role['target'])
            exp.validate_splits(tr, te, groups, np.arange(len(X)))
            np.testing.assert_array_equal(tr, outer[role['repeat']][role['fold']][0])
            np.testing.assert_array_equal(te, outer[role['repeat']][role['fold']][1])
            artifact = joblib.load(exp.OUT / 'private' / (exp.role_name(role) + '.joblib'))
            stored = frame[(frame.repeat == role['repeat']) & (frame.fold == role['fold']) &
                           (frame.target == role['target'])].sort_values('row')
            np.testing.assert_array_equal(stored.row, te)
            np.testing.assert_array_equal(stored.y, y[te, ti])
            replay = exp.predict_role(artifact, X.iloc[te])
            for arm in exp.ARMS:
                np.testing.assert_allclose(stored[arm], replay[arm], atol=1e-12, rtol=0)
                max_residual = max(max_residual, float(np.max(np.abs(stored[arm].to_numpy() - replay[arm]))))
            expected_inner = list(StratifiedGroupKFold(3, shuffle=True, random_state=role['seed']).split(
                X.iloc[tr], y[tr, ti], groups[tr]))
            rebuilt = np.full_like(artifact['oof'], np.nan)
            scores = {name: [] for name in exp.BASELINE_CANDIDATES}
            for k, (it, iv) in enumerate(expected_inner):
                np.testing.assert_array_equal(role['inner'][k]['train'], tr[it])
                np.testing.assert_array_equal(role['inner'][k]['test'], tr[iv])
                exp.validate_splits(tr[it], tr[iv], groups, tr)
                for ni, name in enumerate(artifact['names']):
                    model = artifact['inner_models'][k][name]
                    pp = model.predict_proba(X.iloc[tr[iv]])[:, 1]
                    rebuilt[iv, ni] = pp
                    if name in scores:
                        scores[name].append(roc_auc_score(y[tr[iv], ti], pp))
                    inner_count += 1
            np.testing.assert_allclose(rebuilt, artifact['oof'], atol=1e-12, rtol=0)
            selected = max(exp.BASELINE_CANDIDATES, key=lambda n: np.mean(scores[n]))
            if selected != artifact['selected']:
                raise ValueError('Baseline selection mismatch')
            member_oof = rebuilt[:, [artifact['names'].index(n) for n in exp.ENSEMBLE_MEMBERS]]
            weights = exp.blend_weights(member_oof, y[tr, ti])
            np.testing.assert_allclose(weights, artifact['weights'], atol=1e-10, rtol=0)
            recal = LogisticRegression(C=1, max_iter=3000, random_state=role['seed']).fit(
                logit(np.clip(member_oof.mean(axis=1), 1e-6, 1 - 1e-6))[:, None], y[tr, ti])
            np.testing.assert_allclose(recal.coef_, artifact['calibrator'].coef_, atol=1e-12, rtol=0)
            np.testing.assert_allclose(recal.intercept_, artifact['calibrator'].intercept_, atol=1e-12, rtol=0)
            if index % 10 == 0:
                print(f'Replayed {index}/60 roles', flush=True)
    rebuilt_result = exp.summarize(frame)
    if rebuilt_result != exp.load(exp.OUT / 'results.json'):
        raise ValueError('Results do not reproduce')
    exp.assert_hashes(manifest['protected_hashes'])
    report = {'status': 'passed', 'roles_replayed': len(manifest['roles']),
              'inner_member_predictions_replayed': inner_count,
              'prediction_rows': len(frame), 'metric_groups': len(rebuilt_result['scores']),
              'maximum_outer_probability_residual': max_residual,
              'protected_files_unchanged': len(manifest['protected_hashes']),
              'results_sha256': exp.digest(exp.OUT / 'results.json'),
              'fit_receipt_sha256': exp.digest(exp.OUT / 'fit_receipt.json'),
              'verifier_sha256': exp.digest(Path(__file__))}
    exp.write_json(exp.OUT / 'verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
