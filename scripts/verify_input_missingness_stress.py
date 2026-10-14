"""Verify saved exact-procedure missing-group diagnostic without refitting."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, brier_score_loss, confusion_matrix,
                             f1_score, log_loss, precision_score, recall_score,
                             roc_auc_score)

from ml.schema import FEATURES, GROUPS, ROOT, TARGETS, digest, read_data

OUT = ROOT / 'output/research/input_missingness_v1'
SCENARIOS = {
    'full': [],
    'no_lab': GROUPS['Laboratory'],
    'no_echo': GROUPS['Echocardiography'],
    'core_only': GROUPS['ECG'] + GROUPS['Laboratory'] + GROUPS['Echocardiography'],
}


def check_close(actual, expected, label):
    if not math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=1e-12):
        raise ValueError(f'{label}: {actual} != {expected}')


def main():
    manifest = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
    result = json.loads((OUT / 'results.json').read_text(encoding='utf-8'))
    metadata = json.loads((ROOT / 'models/metadata.json').read_text(encoding='utf-8'))
    evaluation = json.loads((ROOT / 'ml/metrics/evaluation.json').read_text(encoding='utf-8'))
    expected_inputs = {
        'data/raw/extention of Z-Alizadeh sani dataset.xlsx',
        'ml/metrics/evaluation.json', 'models/metadata.json',
        'ml/schema.py', 'ml/preprocessing.py', 'ml/evaluate.py',
        'ml/input_missingness_stress.py',
        'docs/input_missingness_stress_protocol.md',
    }
    for target in TARGETS:
        expected_inputs.add(f'ml/metrics/{target}_oof.csv')
        info = metadata['artifacts'][target]
        expected_inputs.add(f"models/{info['file']}")
        if digest(ROOT / 'models' / info['file']) != info['sha256']:
            raise ValueError(f'Production model hash mismatch: {target}')
    if set(manifest['inputs_sha256']) != expected_inputs:
        raise ValueError('Manifest input set changed.')
    for path, recorded in manifest['inputs_sha256'].items():
        if digest(ROOT / path) != recorded:
            raise ValueError(f'Input hash mismatch: {path}')
    expected_outputs = {
        f'output/research/input_missingness_v1/{target}_predictions.csv'
        for target in TARGETS
    } | {'output/research/input_missingness_v1/results.json'}
    if set(manifest['outputs_sha256']) != expected_outputs:
        raise ValueError('Manifest output set changed.')
    for path, recorded in manifest['outputs_sha256'].items():
        if digest(ROOT / path) != recorded:
            raise ValueError(f'Output hash mismatch: {path}')

    df = read_data()
    count = len(df)
    if (result['rows'] != count or result['feature_count'] != len(FEATURES)
            or result['scenario_masked_fields'] != SCENARIOS
            or result['core_only_observed_field_count'] != 31
            or result['source_complete_input_cells'] != count * len(FEATURES)
            or result['threshold'] != .5
            or result['post_display_projection_included'] is not False
            or metadata['features'] != FEATURES or metadata['rows'] != count):
        raise ValueError('Diagnostic contract changed.')
    if df[FEATURES].isna().any().any():
        raise ValueError('Source is not complete; missingness premise changed.')
    if set(result['targets']) != set(TARGETS):
        raise ValueError('Target set changed.')

    for target, label_column in TARGETS.items():
        y = (df[label_column] == ('CAD' if target == 'cad' else 'Stenotic')).astype(int).to_numpy()
        frame = pd.read_csv(OUT / f'{target}_predictions.csv', float_precision='round_trip')
        expected_columns = ['row_index', 'fold', 'y'] + [f'p_{name}' for name in SCENARIOS]
        if list(frame.columns) != expected_columns or len(frame) != count:
            raise ValueError(f'Prediction CSV schema/length mismatch: {target}')
        if (frame['row_index'].tolist() != list(range(count))
                or not np.array_equal(frame['y'].to_numpy(), y)):
            raise ValueError(f'Prediction row/label mismatch: {target}')
        folds = evaluation['targets'][target]['folds']
        fold_by_row = np.full(count, -1, dtype=int)
        test_seen = set()
        ids = set()
        for fold in folds:
            fold_id = int(fold['fold'])
            train, test = list(fold['train_indices']), list(fold['test_indices'])
            train_set, test_set = set(train), set(test)
            if (fold_id in ids or len(train) != len(train_set)
                    or len(test) != len(test_set) or not train_set or not test_set
                    or train_set & test_set or train_set | test_set != set(range(count))
                    or test_seen & test_set):
                raise ValueError(f'Fold containment failure: {target}')
            ids.add(fold_id)
            test_seen |= test_set
            fold_by_row[test] = fold_id
        if (len(folds) != 5 or test_seen != set(range(count))
                or not np.array_equal(frame['fold'].to_numpy(), fold_by_row)):
            raise ValueError(f'Fold coverage/identity failure: {target}')
        original = pd.read_csv(ROOT / f'ml/metrics/{target}_oof.csv',
                               float_precision='round_trip')
        if (original['row_index'].tolist() != list(range(count))
                or not np.array_equal(original['y'].to_numpy(), y)
                or not np.array_equal(original['fold'].to_numpy(), fold_by_row)):
            raise ValueError(f'Original OOF identity mismatch: {target}')
        full = frame['p_full'].to_numpy()
        residual = float(np.max(np.abs(full - original['p'].to_numpy())))
        if residual > 1e-12:
            raise ValueError(f'Full OOF reproduction failure: {target}: {residual}')
        check_close(result['targets'][target]['max_saved_oof_probability_residual'],
                    residual, f'{target} reproduction residual')
        recorded = result['targets'][target]['scenarios']
        if set(recorded) != set(SCENARIOS):
            raise ValueError(f'Scenario set changed: {target}')
        for scenario in SCENARIOS:
            p = frame[f'p_{scenario}'].to_numpy()
            if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
                raise ValueError(f'Invalid probabilities: {target}/{scenario}')
            predicted = p >= .5
            tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
            actual = {
                'accuracy': accuracy_score(y, predicted),
                'precision': precision_score(y, predicted, zero_division=0),
                'recall': recall_score(y, predicted),
                'f1': f1_score(y, predicted),
                'roc_auc': roc_auc_score(y, p),
                'specificity': tn / (tn + fp),
                'brier': brier_score_loss(y, p),
                'log_loss': log_loss(y, p),
                'changed_0_5_decisions_from_full': int(np.sum(predicted != (full >= .5))),
                'mean_absolute_probability_change_from_full': float(np.mean(np.abs(p - full))),
            }
            for key, value in actual.items():
                check_close(recorded[scenario][key], value, f'{target}/{scenario}/{key}')
            if recorded[scenario]['confusion_matrix'] != [[int(tn), int(fp)], [int(fn), int(tp)]]:
                raise ValueError(f'Confusion mismatch: {target}/{scenario}')
    print('Verified hashes, folds, 303 row-level predictions per target, full OOF reproduction, and all scenario metrics.')


if __name__ == '__main__':
    main()
