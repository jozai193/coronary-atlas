"""Read-only audit of the saved paired coherence experiment.

This checks source and code hashes, shared held-out partitions, recorded
metrics, and the convex projection optimality condition. It does not create a
new validation cohort or rerun model selection.
"""
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss, confusion_matrix, recall_score, roc_auc_score

from ml.schema import ROOT, TARGETS, digest, read_data

EXPERIMENT = ROOT / 'ml/experiments/coherence_v1'
ORDER = tuple(TARGETS)
VERTICES = np.array([[0, 0, 0, 0]] + [[1, *bits] for bits in itertools.product((0, 1), repeat=3)])


def close(actual, expected, description, tolerance=1e-10):
    if not np.isclose(actual, expected, rtol=0, atol=tolerance):
        raise AssertionError(f'{description}: {actual} != {expected}')


def main():
    record = json.loads((EXPERIMENT / 'results.json').read_text(encoding='utf-8'))
    if [item['seed'] for item in record['repeats']] != [20261007, 20261108]:
        raise AssertionError('Saved repeats or outer-fold seeds changed.')
    for key, path in {
        'protocol_sha256': ROOT / 'docs/coherence_projection_protocol.md',
        'runner_sha256': ROOT / 'ml/evaluate_coherence.py',
        'projection_sha256': ROOT / 'ml/coherence.py',
        'raw_sha256': ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx',
        'train_sha256': ROOT / 'ml/train.py',
        'preprocessing_sha256': ROOT / 'ml/preprocessing.py',
    }.items():
        if digest(path) != record[key]:
            raise AssertionError(f'Experiment dependency changed: {path}')

    source = read_data()
    labels = np.column_stack([
        (source[column] == ('CAD' if target == 'cad' else 'Stenotic')).astype(int).to_numpy()
        for target, column in TARGETS.items()
    ])
    if labels.shape != (303, 4):
        raise AssertionError(f'Unexpected source label shape: {labels.shape}')
    coherent = labels[:, 0] >= np.max(labels[:, 1:], axis=1)
    if np.flatnonzero(~coherent).tolist() != [93]:
        raise AssertionError('Source label anomaly changed.')

    deltas = []
    within_target_limits = True
    for repeat in record['repeats']:
        number = repeat['repeat']
        table = pd.read_csv(EXPERIMENT / f'repeat_{number}.csv', float_precision='round_trip')
        if table.row_index.tolist() != list(range(len(source))):
            raise AssertionError(f'Repeat {number} has missing or reordered source rows.')
        seen = set()
        for fold in repeat['folds']:
            train = set(fold['train_indices'])
            test = set(fold['test_indices'])
            if train & test or train | test != set(range(len(source))) or seen & test:
                raise AssertionError(f'Repeat {number} has invalid outer partitions.')
            if not np.all(table.loc[list(test), 'outer_fold'] == fold['fold']):
                raise AssertionError(f'Repeat {number} has inconsistent fold IDs.')
            if set(fold['selected']) != set(ORDER):
                raise AssertionError(f'Repeat {number} has incomplete target selections.')
            seen |= test
        if seen != set(range(len(source))):
            raise AssertionError(f'Repeat {number} did not hold out every row once.')

        stored_labels = table[[f'{target}_y' for target in ORDER]].to_numpy()
        if not np.array_equal(stored_labels, labels):
            raise AssertionError(f'Repeat {number} labels differ from the raw workbook.')
        raw = table[[f'{target}_raw' for target in ORDER]].to_numpy(float)
        projected = table[[f'{target}_projected' for target in ORDER]].to_numpy(float)
        if not np.isfinite(raw).all() or not np.isfinite(projected).all():
            raise AssertionError(f'Repeat {number} has nonfinite probabilities.')
        if np.any(raw < 0) or np.any(raw > 1) or np.any(projected < 0) or np.any(projected > 1):
            raise AssertionError(f'Repeat {number} has probabilities outside [0, 1].')
        if np.any(projected[:, 0, None] < projected[:, 1:] - 1e-12):
            raise AssertionError(f'Repeat {number} has discordant projected values.')

        # For closed convex C, q is the Euclidean projection of p iff
        # (p-q) dot (z-q) <= 0 for all z in C. A linear function reaches its
        # maximum at a vertex, so the nine binary vertices suffice here.
        optimality = np.einsum('ni,nvi->nv', raw - projected, VERTICES[None, :, :] - projected[:, None, :])
        if np.max(optimality) > 1e-10:
            raise AssertionError(f'Repeat {number} failed projection optimality.')
        raw_error = np.sum((raw - labels) ** 2, axis=1)
        projected_error = np.sum((projected - labels) ** 2, axis=1)
        if np.any(projected_error[coherent] > raw_error[coherent] + 1e-10):
            raise AssertionError(f'Repeat {number} worsened aggregate error for a coherent source row.')

        summary = repeat['summary']
        close(np.mean((raw - labels) ** 2), summary['mean_four_target_brier_raw'], f'repeat {number} raw Brier')
        close(np.mean((projected - labels) ** 2), summary['mean_four_target_brier_projected'], f'repeat {number} projected Brier')
        close(np.mean(raw_error), summary['mean_per_patient_sum_squared_error_raw'], f'repeat {number} raw sum error')
        close(np.mean(projected_error), summary['mean_per_patient_sum_squared_error_projected'], f'repeat {number} projected sum error')
        if int(np.sum(raw[:, 0] < np.max(raw[:, 1:], axis=1))) != summary['discordant_rows_raw']:
            raise AssertionError(f'Repeat {number} raw discordance count changed.')
        if int(np.sum(np.max(np.abs(projected - raw), axis=1) > 1e-12)) != summary['changed_rows']:
            raise AssertionError(f'Repeat {number} changed-row count changed.')
        close(np.max(np.abs(projected - raw)), summary['max_absolute_probability_adjustment'], f'repeat {number} max adjustment')
        for index, target in enumerate(ORDER):
            y = labels[:, index]
            for name, values in [('raw', raw[:, index]), ('projected', projected[:, index])]:
                saved = summary['target_metrics'][target][name]
                close(brier_score_loss(y, values), saved['brier'], f'repeat {number} {target} {name} Brier')
                close(roc_auc_score(y, values), saved['roc_auc'], f'repeat {number} {target} {name} AUC')
                close(recall_score(y, values >= .5), saved['recall'], f'repeat {number} {target} {name} recall')
                close(accuracy_score(y, values >= .5), saved['accuracy'], f'repeat {number} {target} {name} accuracy')
                if confusion_matrix(y, values >= .5).tolist() != saved['confusion_matrix']:
                    raise AssertionError(f'Repeat {number} {target} {name} confusion counts changed.')
            old = summary['target_metrics'][target]['raw']
            new = summary['target_metrics'][target]['projected']
            within_target_limits &= (new['brier'] - old['brier'] <= .005
                                     and new['roc_auc'] - old['roc_auc'] >= -.01
                                     and new['recall'] - old['recall'] >= -.02)
        deltas.append(summary['mean_four_target_brier_projected'] - summary['mean_four_target_brier_raw'])
        print(f'Repeat {number}: verified {len(source)} shared held-out rows, {summary["changed_rows"]} adjustments, Brier {summary["mean_four_target_brier_raw"]:.6f} -> {summary["mean_four_target_brier_projected"]:.6f}')
    close(np.mean(deltas), record['screen']['mean_four_target_brier_delta'], 'mean Brier delta')
    if record['screen']['passed'] != bool(all(delta < 0 for delta in deltas) and within_target_limits):
        raise AssertionError('Saved adoption screen is not supported by the paired Brier scores.')
    print('PASS: saved coherence evidence, geometric optimality, and reported metrics.')


if __name__ == '__main__':
    main()
