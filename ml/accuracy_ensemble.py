"""Frozen ensemble follow-up. Research only; never changes served artifacts."""
import os
for _key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'

import argparse
import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from threadpoolctl import threadpool_limits

from ml.broad_search import make_candidate, ENSEMBLE_MEMBERS, BASELINE_CANDIDATES
from ml.coherence import project_probabilities
from ml.evaluate import metrics
from ml.schema import ROOT, FEATURES, CATEGORICAL, TARGETS, digest, read_data, write_json

OUT = ROOT / 'ml/experiments/accuracy_ensemble_v1'
SEEDS = (20261021, 20261022, 20261023)
ORDER = tuple(TARGETS)
ARMS = ('baseline', 'uniform', 'sigmoid_uniform', 'simplex')
PROTOCOL = ROOT / 'docs/accuracy_goal_protocol.md'


def source_data():
    df = read_data()
    X = df[FEATURES].copy()
    y = np.column_stack([(df[col] == ('CAD' if t == 'cad' else 'Stenotic')).astype(int)
                         for t, col in TARGETS.items()])
    if X.shape != (303, 55):
        raise ValueError('Source dimensions changed')
    groups = pd.util.hash_pandas_object(X, index=False).to_numpy()
    return X, y, groups


def protected_hashes():
    paths = []
    for folder in ('models', 'ml/metrics', 'ml/experiments'):
        paths.extend(p for p in (ROOT / folder).rglob('*') if p.is_file()
                     and OUT not in p.parents and 'private' not in p.parts
                     and '__pycache__' not in p.parts)
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(paths)}


def input_hashes():
    paths = [PROTOCOL, Path(__file__), ROOT / 'ml/broad_search.py', ROOT / 'ml/schema.py',
             ROOT / 'ml/preprocessing.py', ROOT / 'ml/coherence.py', ROOT / 'ml/evaluate.py',
             ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx']
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def assert_hashes(mapping):
    for name, expected in mapping.items():
        if digest(ROOT / name) != expected:
            raise ValueError(f'Hash mismatch: {name}')


def validate_splits(train, test, groups, universe):
    train, test, universe = map(lambda v: np.asarray(v, dtype=int), (train, test, universe))
    if len(np.unique(train)) != len(train) or len(np.unique(test)) != len(test):
        raise ValueError('Repeated partition rows')
    if set(train) & set(test) or set(train) | set(test) != set(universe):
        raise ValueError('Partition overlap or coverage failure')
    if set(groups[train]) & set(groups[test]):
        raise ValueError('Identical inputs cross partition boundary')


def prepare():
    if OUT.exists():
        raise FileExistsError(f'Refusing overwrite: {OUT}')
    X, y, groups = source_data()
    roles = []
    for repeat, seed in enumerate(SEEDS, 1):
        cv = StratifiedGroupKFold(5, shuffle=True, random_state=seed)
        for fold, (train, test) in enumerate(cv.split(X, y[:, 0], groups)):
            validate_splits(train, test, groups, np.arange(len(X)))
            for ti, target in enumerate(ORDER):
                inner_seed = seed + fold + ti * 100
                inner = []
                split = StratifiedGroupKFold(3, shuffle=True, random_state=inner_seed)
                for it, iv in split.split(X.iloc[train], y[train, ti], groups[train]):
                    validate_splits(train[it], train[iv], groups, train)
                    if len(np.unique(y[train[it], ti])) != 2 or len(np.unique(y[train[iv], ti])) != 2:
                        raise ValueError('Single-class inner partition')
                    inner.append({'train': train[it].tolist(), 'test': train[iv].tolist()})
                roles.append({'repeat': repeat, 'fold': fold, 'target': target,
                              'seed': inner_seed, 'train': train.tolist(), 'test': test.tolist(), 'inner': inner})
    manifest = {'input_hashes': input_hashes(), 'protected_hashes': protected_hashes(),
                'seeds': list(SEEDS), 'members': ENSEMBLE_MEMBERS, 'rows': len(X),
                'unique_input_groups': len(np.unique(groups)), 'roles': roles,
                'scope': 'Repeated internal development on previously inspected patients; no independent validation.'}
    (OUT / 'private').mkdir(parents=True)
    write_json(OUT / 'manifest.json', manifest)
    print(f'Prepared {len(roles)} roles; {len(manifest["protected_hashes"])} protected files', flush=True)


def fit_member(name, X, y, seed):
    model = make_candidate(name, seed)
    if name == 'catboost_native':
        model.fit(X, y, cat_features=CATEGORICAL)
    else:
        model.fit(X, y)
    return model


def blend_weights(p, y):
    p, y = np.asarray(p), np.asarray(y)
    n = p.shape[1]
    uniform = np.full(n, 1 / n)
    def fun(w):
        residual = p @ w - y
        return float(np.mean(residual ** 2) + .01 * np.sum((w - uniform) ** 2))
    def jac(w):
        return 2 * p.T @ (p @ w - y) / len(y) + .02 * (w - uniform)
    result = minimize(fun, uniform, jac=jac, method='SLSQP', bounds=[(0, 1)] * n,
                      constraints={'type': 'eq', 'fun': lambda w: w.sum() - 1,
                                   'jac': lambda w: np.ones(n)},
                      options={'ftol': 1e-10, 'maxiter': 1000})
    if not result.success or abs(result.x.sum() - 1) > 1e-8 or result.x.min() < -1e-8:
        raise RuntimeError(f'Weight optimization failed: {result.message}')
    return result.x


def fit_role(X_train, y_train, inner_local, seed):
    """Only training data/labels enter this boundary; test data are unavailable."""
    names = list(dict.fromkeys(BASELINE_CANDIDATES + ENSEMBLE_MEMBERS))
    oof = np.full((len(X_train), len(names)), np.nan)
    inner_scores = {name: [] for name in BASELINE_CANDIDATES}
    inner_models = []
    for it, iv in inner_local:
        fitted = {}
        for ni, name in enumerate(names):
            model = fit_member(name, X_train.iloc[it], y_train[it], seed)
            oof[iv, ni] = model.predict_proba(X_train.iloc[iv])[:, 1]
            fitted[name] = model
            if name in inner_scores:
                inner_scores[name].append(float(roc_auc_score(y_train[iv], oof[iv, ni])))
        inner_models.append(fitted)
    if not np.isfinite(oof).all():
        raise ValueError('Incomplete inner out-of-fold predictions')
    selected = max(BASELINE_CANDIDATES, key=lambda name: np.mean(inner_scores[name]))
    member_oof = oof[:, [names.index(name) for name in ENSEMBLE_MEMBERS]]
    calibrator = LogisticRegression(C=1, max_iter=3000, random_state=seed).fit(
        logit(np.clip(member_oof.mean(axis=1), 1e-6, 1 - 1e-6))[:, None], y_train)
    weights = blend_weights(member_oof, y_train)
    full = {name: fit_member(name, X_train, y_train, seed)
            for name in dict.fromkeys(ENSEMBLE_MEMBERS + [selected])}
    return {'full': full, 'inner_models': inner_models, 'names': names, 'oof': oof,
            'selected': selected, 'inner_scores': inner_scores,
            'calibrator': calibrator, 'weights': weights}


def predict_role(artifact, X):
    members = np.column_stack([artifact['full'][name].predict_proba(X)[:, 1] for name in ENSEMBLE_MEMBERS])
    uniform = members.mean(axis=1)
    return {'baseline': artifact['full'][artifact['selected']].predict_proba(X)[:, 1],
            'uniform': uniform,
            'sigmoid_uniform': artifact['calibrator'].predict_proba(
                logit(np.clip(uniform, 1e-6, 1 - 1e-6))[:, None])[:, 1],
            'simplex': members @ artifact['weights']}


def role_name(role):
    return f'r{role["repeat"]}_f{role["fold"]}_{role["target"]}'


def fit():
    manifest = load(OUT / 'manifest.json')
    assert_hashes(manifest['input_hashes'])
    assert_hashes(manifest['protected_hashes'])
    if any((OUT / 'private').iterdir()) or (OUT / 'fit_receipt.json').exists():
        raise FileExistsError('Refusing fit overwrite or partial-run resume')
    X, y, groups = source_data()
    started = time.monotonic()
    files, records = {}, []
    with threadpool_limits(limits=1):
        for number, role in enumerate(manifest['roles'], 1):
            if time.monotonic() - started > 45 * 60:
                raise TimeoutError('Frozen fitting time budget exceeded')
            tr, te = np.array(role['train']), np.array(role['test'])
            validate_splits(tr, te, groups, np.arange(len(X)))
            pos = {int(row): i for i, row in enumerate(tr)}
            inner = [(np.array([pos[row] for row in item['train']]),
                      np.array([pos[row] for row in item['test']])) for item in role['inner']]
            ti = ORDER.index(role['target'])
            artifact = fit_role(X.iloc[tr], y[tr, ti], inner, role['seed'])
            path = OUT / 'private' / (role_name(role) + '.joblib')
            joblib.dump(artifact, path, compress=3)
            files[path.relative_to(OUT).as_posix()] = digest(path)
            prediction = predict_role(artifact, X.iloc[te])
            for i, row in enumerate(te):
                records.append({'repeat': role['repeat'], 'fold': role['fold'], 'target': role['target'],
                                'row': int(row), 'y': int(y[row, ti]),
                                **{arm: float(prediction[arm][i]) for arm in ARMS}})
            print(f'{number}/{len(manifest["roles"])} {role_name(role)} saved; {time.monotonic()-started:.1f}s', flush=True)
    path = OUT / 'predictions.csv'
    pd.DataFrame(records).to_csv(path, index=False)
    files[path.name] = digest(path)
    assert_hashes(manifest['protected_hashes'])
    import sklearn, catboost
    write_json(OUT / 'fit_receipt.json', {'manifest_sha256': digest(OUT / 'manifest.json'),
               'files': files, 'seconds': time.monotonic() - started,
               'sklearn': sklearn.__version__, 'catboost': catboost.__version__, 'completed_roles': len(manifest['roles'])})


def check_receipt():
    manifest, receipt = load(OUT / 'manifest.json'), load(OUT / 'fit_receipt.json')
    if digest(OUT / 'manifest.json') != receipt['manifest_sha256']:
        raise ValueError('Manifest changed')
    assert_hashes(manifest['input_hashes'])
    assert_hashes(manifest['protected_hashes'])
    expected = {'predictions.csv'} | {'private/' + role_name(r) + '.joblib' for r in manifest['roles']}
    if set(receipt['files']) != expected or receipt['completed_roles'] != len(manifest['roles']):
        raise ValueError('Incomplete fit receipt')
    for name, sha in receipt['files'].items():
        if digest(OUT / name) != sha:
            raise ValueError(f'Fit artifact changed: {name}')
    return manifest, receipt


def bootstrap(values):
    rng = np.random.default_rng(20261024)
    means = [values[rng.integers(0, len(values), len(values))].mean() for _ in range(2000)]
    return {'mean': float(values.mean()), 'conditional_95_interval': np.quantile(means, [.025, .975]).tolist()}


def summarize(frame):
    _, y, _ = source_data()
    arrays, scores = {}, []
    for repeat in range(1, 4):
        f = frame[frame.repeat == repeat]
        for arm in ARMS:
            p = np.column_stack([f[f.target == target].sort_values('row')[arm].to_numpy() for target in ORDER])
            if p.shape != y.shape or not np.isfinite(p).all() or p.min() < 0 or p.max() > 1:
                raise ValueError('Invalid prediction matrix')
            for variant, pp in (('raw', p), ('projected', np.array([project_probabilities(v) for v in p]))):
                key = arm + '_' + variant
                arrays[(repeat, key)] = pp
                for ti, target in enumerate(ORDER):
                    scores.append({'repeat': repeat, 'arm': key, 'target': target,
                                   **metrics(y[:, ti], pp[:, ti]),
                                   'average_precision': float(average_precision_score(y[:, ti], pp[:, ti]))})
    summary = {'scope': 'Reused-cohort internal development; not an independent or clinical accuracy claim.',
               'scores': scores, 'comparisons': {}}
    base = np.array([arrays[(r, 'baseline_projected')] for r in range(1, 4)])
    for arm in ARMS[1:]:
        candidate = np.array([arrays[(r, arm + '_projected')] for r in range(1, 4)])
        diff = (candidate - y) ** 2 - (base - y) ** 2
        per_repeat = diff.mean(axis=(1, 2))
        per_target = {t: bootstrap(diff[:, :, i].mean(axis=0)) for i, t in enumerate(ORDER)}
        auc_delta = {t: float(np.mean([roc_auc_score(y[:, i], candidate[r, :, i]) -
                        roc_auc_score(y[:, i], base[r, :, i]) for r in range(3)])) for i, t in enumerate(ORDER)}
        screen = (diff.mean() <= -.005 and np.all(per_repeat < 0)
                  and all(v['mean'] <= .005 for v in per_target.values())
                  and all(v >= -.01 for v in auc_delta.values()))
        summary['comparisons'][arm] = {'primary': arm == 'sigmoid_uniform',
            'brier': bootstrap(diff.mean(axis=(0, 2))), 'per_repeat_brier_delta': per_repeat.tolist(),
            'per_target_brier': per_target, 'mean_auc_delta': auc_delta, 'engineering_screen_passed': bool(screen)}
    return summary


def evaluate():
    if (OUT / 'results.json').exists():
        raise FileExistsError('Refusing results overwrite')
    check_receipt()
    frame = pd.read_csv(OUT / 'predictions.csv', float_precision='round_trip')
    result = summarize(frame)
    write_json(OUT / 'results.json', result)
    print(json.dumps(result['comparisons'], indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'fit', 'evaluate'])
    globals()[parser.parse_args().stage]()
