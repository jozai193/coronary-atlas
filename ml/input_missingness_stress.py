"""Exploratory held-out missing-group stress of saved target-specific folds.

Protocol: docs/input_missingness_stress_protocol.md. Does not change serving.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from ml.evaluate import metrics
from ml.preprocessing import pipeline
from ml.schema import FEATURES, GROUPS, ROOT, TARGETS, digest, read_data, write_json

OUT = ROOT / 'output/research/input_missingness_v1'
SCENARIOS = {
    'full': [],
    'no_lab': GROUPS['Laboratory'],
    'no_echo': GROUPS['Echocardiography'],
    'core_only': GROUPS['ECG'] + GROUPS['Laboratory'] + GROUPS['Echocardiography'],
}
PROBABILITY_COLUMNS = {name: f'p_{name}' for name in SCENARIOS}
SOURCE = 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'


def input_paths(metadata):
    paths = [SOURCE, 'ml/metrics/evaluation.json', 'models/metadata.json',
             'ml/schema.py', 'ml/preprocessing.py', 'ml/evaluate.py',
             'ml/input_missingness_stress.py',
             'docs/input_missingness_stress_protocol.md']
    for target in TARGETS:
        paths.append(f'ml/metrics/{target}_oof.csv')
        info = metadata['artifacts'][target]
        paths.append(f"models/{info['file']}")
    return paths


def validate_fold_partition(folds, count):
    all_rows = set(range(count))
    test_seen = set()
    ids = set()
    for fold in folds:
        fold_id = int(fold['fold'])
        if fold_id in ids:
            raise ValueError('Duplicate outer fold ID.')
        ids.add(fold_id)
        train, test = list(fold['train_indices']), list(fold['test_indices'])
        train_set, test_set = set(train), set(test)
        if (len(train) != len(train_set) or len(test) != len(test_set)
                or not train_set or not test_set or train_set & test_set
                or train_set | test_set != all_rows or test_seen & test_set):
            raise ValueError('Outer fold containment or coverage failure.')
        test_seen |= test_set
    if test_seen != all_rows or len(folds) != 5:
        raise ValueError('Outer folds do not cover every row exactly once.')


def main():
    df = read_data()
    X = df[FEATURES]
    count = len(df)
    saved = json.loads((ROOT / 'ml/metrics/evaluation.json').read_text(encoding='utf-8'))
    metadata = json.loads((ROOT / 'models/metadata.json').read_text(encoding='utf-8'))
    if metadata['features'] != FEATURES or metadata['rows'] != count:
        raise ValueError('Production metadata/input contract mismatch.')
    if len(FEATURES) - len(SCENARIOS['core_only']) != 31:
        raise ValueError('Unexpected core input count.')
    for target in TARGETS:
        info = metadata['artifacts'][target]
        if digest(ROOT / 'models' / info['file']) != info['sha256']:
            raise ValueError(f'Production model hash mismatch: {target}.')

    summaries = {}
    output_paths = []
    OUT.mkdir(parents=True, exist_ok=True)
    for target, label_column in TARGETS.items():
        y = (df[label_column] == ('CAD' if target == 'cad' else 'Stenotic')).astype(int)
        folds = saved['targets'][target]['folds']
        validate_fold_partition(folds, count)
        probabilities = {name: np.full(count, np.nan) for name in SCENARIOS}
        fold_ids = np.full(count, -1, dtype=int)
        for fold in folds:
            train = np.asarray(fold['train_indices'], dtype=int)
            test = np.asarray(fold['test_indices'], dtype=int)
            selected = fold['selected']
            fitted = pipeline(selected['kind'], selected['strength']).fit(
                X.iloc[train], y.iloc[train])
            fold_ids[test] = int(fold['fold'])
            for scenario, masked_columns in SCENARIOS.items():
                frame = X.iloc[test].copy()
                if masked_columns:
                    for column in masked_columns:
                        frame[column] = np.nan
                probabilities[scenario][test] = fitted.predict_proba(frame)[:, 1]
        if any(not np.isfinite(p).all() or np.any((p < 0) | (p > 1))
               for p in probabilities.values()):
            raise ValueError(f'Invalid or incomplete probabilities: {target}.')
        original = pd.read_csv(ROOT / f'ml/metrics/{target}_oof.csv',
                               float_precision='round_trip')
        if (original['row_index'].tolist() != list(range(count))
                or not np.array_equal(original['fold'].to_numpy(), fold_ids)
                or not np.array_equal(original['y'].to_numpy(), y.to_numpy())):
            raise ValueError(f'Original held-out row/label/fold mismatch: {target}.')
        residual = float(np.max(np.abs(probabilities['full'] - original['p'].to_numpy())))
        if residual > 1e-12:
            raise ValueError(f'Original held-out probabilities did not reproduce: {target}: {residual}.')
        frame = pd.DataFrame({'row_index': np.arange(count), 'fold': fold_ids,
                              'y': y.to_numpy()})
        for name, column in PROBABILITY_COLUMNS.items():
            frame[column] = probabilities[name]
        path = OUT / f'{target}_predictions.csv'
        frame.to_csv(path, index=False, float_format='%.17g')
        output_paths.append(path)
        summary = {}
        for scenario, p in probabilities.items():
            summary[scenario] = metrics(y, p)
            summary[scenario]['changed_0_5_decisions_from_full'] = int(np.sum(
                (p >= .5) != (probabilities['full'] >= .5)))
            summary[scenario]['mean_absolute_probability_change_from_full'] = float(
                np.mean(np.abs(p - probabilities['full'])))
        summaries[target] = {'max_saved_oof_probability_residual': residual,
                             'scenarios': summary}

    result = {
        'scope': 'Post-hoc internal held-out group-masking diagnostic on the original 303 complete source records; not external or real-world missing-data validation.',
        'rows': count,
        'target_count': len(TARGETS),
        'source_complete_input_cells': int(X.notna().sum().sum()),
        'feature_count': len(FEATURES),
        'core_only_observed_field_count': len(FEATURES) - len(SCENARIOS['core_only']),
        'scenario_masked_fields': SCENARIOS,
        'threshold': .5,
        'post_display_projection_included': False,
        'targets': summaries,
    }
    result_path = OUT / 'results.json'
    write_json(result_path, result)
    output_paths.append(result_path)
    manifest = {
        'inputs_sha256': {p: digest(ROOT / p) for p in input_paths(metadata)},
        'outputs_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p)
                           for p in output_paths},
    }
    write_json(OUT / 'manifest.json', manifest)
    print(f'Wrote exact-procedure missingness diagnostic: {OUT}')
    for target in TARGETS:
        values = summaries[target]['scenarios']
        print(target, 'full/no_lab/no_echo/core_only recall:',
              *[round(values[name]['recall'], 3) for name in SCENARIOS])


if __name__ == '__main__':
    main()
