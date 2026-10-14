"""Pilot-informed, leakage-safe shared-fold evaluation of coherence projection."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from threadpoolctl import threadpool_limits

from ml.coherence import project_probabilities
from ml.evaluate import metrics
from ml.preprocessing import pipeline
from ml.schema import FEATURES, ROOT, SEED, TARGETS, digest, read_data, write_json
from ml.train import select

OUT = ROOT / 'ml/experiments/coherence_v1'
SEEDS = (20261007, 20261108)
ORDER = tuple(TARGETS)


def summarize(y, raw, projected):
    target_metrics = {}
    for index, target in enumerate(ORDER):
        old = metrics(y[:, index], raw[:, index])
        new = metrics(y[:, index], projected[:, index])
        target_metrics[target] = {
            'raw': old, 'projected': new,
            'delta': {name: float(new[name] - old[name]) for name in
                      ['roc_auc', 'brier', 'accuracy', 'recall', 'specificity', 'f1']},
        }
    row_raw = np.sum((raw - y) ** 2, axis=1)
    row_projected = np.sum((projected - y) ** 2, axis=1)
    coherent = y[:, 0] >= np.max(y[:, 1:], axis=1)
    adjustment = np.sum((projected - raw) ** 2, axis=1)
    inequality = row_projected - row_raw + adjustment
    if np.max(inequality[coherent]) > 1e-12:
        raise ValueError('Projection did not satisfy the coherent-label loss guarantee.')
    if not np.all(projected[:, 0, None] >= projected[:, 1:] - 1e-12):
        raise ValueError('Projected probabilities are not coherent.')
    if np.sum(~coherent) != 1 or np.flatnonzero(~coherent).tolist() != [93]:
        raise ValueError('Source label inconsistency changed.')
    return {
        'mean_four_target_brier_raw': float(np.mean((raw - y) ** 2)),
        'mean_four_target_brier_projected': float(np.mean((projected - y) ** 2)),
        'mean_per_patient_sum_squared_error_raw': float(np.mean(row_raw)),
        'mean_per_patient_sum_squared_error_projected': float(np.mean(row_projected)),
        'discordant_rows_raw': int(np.sum(raw[:, 0] < np.max(raw[:, 1:], axis=1))),
        'discordant_rows_projected': int(np.sum(projected[:, 0] < np.max(projected[:, 1:], axis=1) - 1e-12)),
        'changed_rows': int(np.sum(np.max(np.abs(projected - raw), axis=1) > 1e-12)),
        'max_absolute_probability_adjustment': float(np.max(np.abs(projected - raw))),
        'max_coherent_row_projection_inequality_residual': float(np.max(inequality[coherent])),
        'inconsistent_row_93_sum_squared_error_delta': float(row_projected[93] - row_raw[93]),
        'target_metrics': target_metrics,
    }


def run():
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(f'Refusing to overwrite existing experiment: {OUT}')
    df = read_data()
    X = df[FEATURES]
    y = np.column_stack([
        (df[column] == ('CAD' if target == 'cad' else 'Stenotic')).astype(int).to_numpy()
        for target, column in TARGETS.items()
    ])
    if len(df) != 303 or X.shape[1] != 55:
        raise ValueError('Unexpected source data dimensions.')
    result = {
        'scope': 'Pilot-informed repeated internal shared-fold comparison; same 303 patients, no independent validation.',
        'protocol_sha256': digest(ROOT / 'docs/coherence_projection_protocol.md'),
        'runner_sha256': digest(ROOT / 'ml/evaluate_coherence.py'),
        'projection_sha256': digest(ROOT / 'ml/coherence.py'),
        'raw_sha256': digest(ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'),
        'train_sha256': digest(ROOT / 'ml/train.py'),
        'preprocessing_sha256': digest(ROOT / 'ml/preprocessing.py'),
        'repeats': [],
    }
    frames = {}
    with threadpool_limits(limits=1):
        for repeat, seed in enumerate(SEEDS, start=1):
            raw = np.full((len(df), 4), np.nan)
            fold_ids = np.full(len(df), -1, dtype=int)
            folds = []
            split = StratifiedKFold(5, shuffle=True, random_state=seed)
            for fold_id, (train, test) in enumerate(split.split(X, y[:, 0])):
                fold = {'fold': fold_id, 'train_indices': train.tolist(), 'test_indices': test.tolist(), 'selected': {}}
                for target_index, target in enumerate(ORDER):
                    best, _ = select(X.iloc[train], y[train, target_index], SEED + fold_id)
                    fitted = pipeline(best['kind'], best['strength']).fit(X.iloc[train], y[train, target_index])
                    raw[test, target_index] = fitted.predict_proba(X.iloc[test])[:, 1]
                    fold['selected'][target] = {'kind': best['kind'], 'strength': best['strength']}
                fold_ids[test] = fold_id
                folds.append(fold)
            if not np.isfinite(raw).all() or (fold_ids < 0).any():
                raise ValueError('Shared held-out predictions are incomplete.')
            projected = np.vstack([project_probabilities(row) for row in raw])
            summary = summarize(y, raw, projected)
            result['repeats'].append({'repeat': repeat, 'seed': seed, 'folds': folds, 'summary': summary})
            frames[f'repeat_{repeat}.csv'] = pd.DataFrame({
                'row_index': np.arange(len(df)), 'outer_fold': fold_ids,
                **{f'{target}_y': y[:, i] for i, target in enumerate(ORDER)},
                **{f'{target}_raw': raw[:, i] for i, target in enumerate(ORDER)},
                **{f'{target}_projected': projected[:, i] for i, target in enumerate(ORDER)},
            })
            print('repeat', repeat, 'Brier', round(summary['mean_four_target_brier_raw'], 6),
                  '->', round(summary['mean_four_target_brier_projected'], 6),
                  'discordant', summary['discordant_rows_raw'], '->', summary['discordant_rows_projected'], flush=True)
    summaries = [item['summary'] for item in result['repeats']]
    result['screen'] = {
        'passed': bool(
            all(s['mean_four_target_brier_projected'] < s['mean_four_target_brier_raw'] for s in summaries)
            and all(s['target_metrics'][target]['delta']['brier'] <= .005
                    and s['target_metrics'][target]['delta']['roc_auc'] >= -.01
                    and s['target_metrics'][target]['delta']['recall'] >= -.02
                    for s in summaries for target in ORDER)
        ),
        'mean_four_target_brier_delta': float(np.mean([
            s['mean_four_target_brier_projected'] - s['mean_four_target_brier_raw'] for s in summaries
        ])),
    }
    OUT.mkdir(parents=True, exist_ok=False)
    for name, frame in frames.items():
        frame.to_csv(OUT / name, index=False)
    write_json(OUT / 'results.json', result)


if __name__ == '__main__':
    run()
