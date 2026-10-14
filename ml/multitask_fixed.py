"""One prespecified shared-label forest against saved paired outer folds.

Protocol: docs/multitask_protocol.md. This runner never changes production models.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from threadpoolctl import threadpool_limits

from ml.evaluate import metrics
from ml.preprocessing import pipeline
from ml.schema import FEATURES, PROHIBITED, ROOT, SEED, TARGETS, digest, read_data, write_json

OUT = ROOT / 'ml/experiments/multitask_v1'
REPEATS = (1, 2)


def shared_model():
    preprocess = pipeline('forest').named_steps['preprocess']
    forest = RandomForestClassifier(
        n_estimators=120, min_samples_leaf=5, max_features='sqrt',
        n_jobs=1, random_state=SEED,
    )
    return Pipeline([('preprocess', preprocess), ('model', forest)])


def run():
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(f'Refusing to overwrite existing experiment: {OUT}')
    df = read_data()
    X = df[FEATURES]
    assert len(df) == 303 and not set(X.columns) & PROHIBITED
    Y = pd.DataFrame({
        target: (df[column] == ('CAD' if target == 'cad' else 'Stenotic')).astype(int)
        for target, column in TARGETS.items()
    })
    output = {
        'protocol_sha256': digest(ROOT / 'docs/multitask_protocol.md'),
        'runner_sha256': digest(ROOT / 'ml/multitask_fixed.py'),
        'raw_sha256': digest(ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'),
        'features': FEATURES,
        'targets': {},
    }
    csv_results = {}
    with threadpool_limits(limits=1):
        for target in TARGETS:
            source_path = ROOT / f'ml/experiments/broad_v2/{target}.json'
            source = json.loads(source_path.read_text(encoding='utf-8'))
            result = {'source_sha256': digest(source_path), 'repeats': []}
            for repeat in REPEATS:
                record = source['repeats'][repeat - 1]
                if record['repeat'] != repeat or len(record['outer_folds']) != 5:
                    raise ValueError(f'Unexpected saved folds for {target} repeat {repeat}.')
                csv_path = ROOT / f'ml/experiments/broad_v2/{target}_repeat_{repeat}.csv'
                baseline = pd.read_csv(csv_path, float_precision='round_trip').sort_values('row_index')
                if baseline['row_index'].tolist() != list(range(len(df))):
                    raise ValueError('Saved baseline row identities are incomplete.')
                if not np.array_equal(baseline['y'].to_numpy(), Y[target].to_numpy()):
                    raise ValueError('Saved baseline labels do not match source data.')
                if repeat == 1:
                    original = pd.read_csv(ROOT / f'ml/metrics/{target}_oof.csv', float_precision='round_trip')
                    if not np.allclose(baseline['baseline_selector'], original['p'], rtol=0, atol=1e-12):
                        raise ValueError('Repeat-one baseline does not reproduce original OOF evidence.')
                candidate = np.full(len(df), np.nan)
                fold_ids = np.full(len(df), -1, dtype=int)
                for fold in record['outer_folds']:
                    train = np.asarray(fold['train_indices'], dtype=int)
                    test = np.asarray(fold['test_indices'], dtype=int)
                    if len(set(train) & set(test)) or len(train) + len(test) != len(df):
                        raise ValueError('Outer fold does not partition source rows.')
                    if not np.all(baseline.iloc[test]['outer_fold'].to_numpy() == fold['fold']):
                        raise ValueError('Saved baseline fold assignments differ.')
                    fitted = shared_model().fit(X.iloc[train], Y.iloc[train])
                    classes = fitted.named_steps['model'].classes_
                    if any(not np.array_equal(class_values, [0, 1]) for class_values in classes):
                        raise ValueError('A training fold lacks a target class.')
                    target_position = list(TARGETS).index(target)
                    candidate[test] = fitted.predict_proba(X.iloc[test])[target_position][:, 1]
                    fold_ids[test] = fold['fold']
                if not np.isfinite(candidate).all() or not (candidate >= 0).all() or not (candidate <= 1).all():
                    raise ValueError('Candidate has incomplete or invalid held-out probabilities.')
                if not np.array_equal(fold_ids, baseline['outer_fold'].to_numpy()):
                    raise ValueError('Candidate fold coverage does not match baseline.')
                y = Y[target].to_numpy()
                old = metrics(y, baseline['baseline_selector'].to_numpy())
                new = metrics(y, candidate)
                delta = {name: float(new[name] - old[name]) for name in ['roc_auc', 'brier', 'accuracy', 'recall', 'specificity', 'f1']}
                result['repeats'].append({
                    'repeat': repeat, 'seed': record['seed'], 'baseline_csv_sha256': digest(csv_path),
                    'baseline': old, 'candidate': new, 'delta': delta,
                })
                csv_results[f'{target}_repeat_{repeat}.csv'] = pd.DataFrame({
                    'row_index': np.arange(len(df)), 'y': y, 'outer_fold': fold_ids,
                    'baseline': baseline['baseline_selector'].to_numpy(), 'candidate': candidate,
                })
            deltas = [item['delta'] for item in result['repeats']]
            result['screen'] = {
                'mean_auc_delta': float(np.mean([d['roc_auc'] for d in deltas])),
                'mean_brier_delta': float(np.mean([d['brier'] for d in deltas])),
                'nominated_for_independent_test': bool(
                    np.mean([d['roc_auc'] for d in deltas]) >= .015
                    and all(d['roc_auc'] >= -.005 for d in deltas)
                    and np.mean([d['brier'] for d in deltas]) <= 0
                    and all(d['brier'] <= .005 for d in deltas)
                    and all(d['recall'] >= -.05 for d in deltas)
                ),
            }
            output['targets'][target] = result
            print(target, 'mean AUC delta', round(result['screen']['mean_auc_delta'], 4),
                  'mean Brier delta', round(result['screen']['mean_brier_delta'], 4),
                  'screen', result['screen']['nominated_for_independent_test'], flush=True)
    OUT.mkdir(parents=True, exist_ok=False)
    for name, frame in csv_results.items():
        frame.to_csv(OUT / name, index=False)
    write_json(OUT / 'results.json', output)


if __name__ == '__main__':
    run()
