"""Fixed BMI-missing stress check of the saved outer-fold model procedure.

The source has complete BMI values derived exactly from weight and height.
This diagnostic reuses the original folds and their already selected models;
it does not select or promote a model or estimate external performance.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from ml.evaluate import metrics
from ml.preprocessing import pipeline
from ml.schema import FEATURES, ROOT, TARGETS, digest, read_data, write_json


def main():
    df = read_data()
    X = df[FEATURES]
    calculated = X['Weight'] / (X['Length'] / 100) ** 2
    if not np.allclose(X['BMI'], calculated, rtol=0, atol=1e-12):
        raise ValueError('Source BMI relation changed; review before interpreting this audit.')
    saved = json.loads((ROOT / 'ml/metrics/evaluation.json').read_text(encoding='utf-8'))
    targets = {}
    for target, column in TARGETS.items():
        y = (df[column] == ('CAD' if target == 'cad' else 'Stenotic')).astype(int)
        original = pd.read_csv(ROOT / f'ml/metrics/{target}_oof.csv', float_precision='round_trip')
        full = np.full(len(df), np.nan)
        masked = np.full(len(df), np.nan)
        for fold in saved['targets'][target]['folds']:
            train, test = fold['train_indices'], fold['test_indices']
            selected = fold['selected']
            fitted = pipeline(selected['kind'], selected['strength']).fit(X.iloc[train], y.iloc[train])
            held_out = X.iloc[test]
            missing_bmi = held_out.copy()
            missing_bmi['BMI'] = np.nan
            full[test] = fitted.predict_proba(held_out)[:, 1]
            masked[test] = fitted.predict_proba(missing_bmi)[:, 1]
        if not np.isfinite(full).all() or not np.isfinite(masked).all():
            raise ValueError(f'Incomplete held-out predictions for {target}.')
        residual = float(np.max(np.abs(full - original['p'].to_numpy())))
        if residual > 1e-12:
            raise ValueError(f'Original held-out predictions did not reproduce for {target}: {residual}')
        a, b = metrics(y, full), metrics(y, masked)
        targets[target] = {
            'full': {key: a[key] for key in ['roc_auc', 'brier', 'accuracy', 'recall', 'specificity']},
            'bmi_missing_and_imputed': {key: b[key] for key in ['roc_auc', 'brier', 'accuracy', 'recall', 'specificity']},
            'max_saved_oof_probability_residual': residual,
            'changed_binary_decisions': int(np.sum((full >= .5) != (masked >= .5))),
            'mean_absolute_probability_change': float(np.mean(np.abs(full - masked))),
        }
    out = {
        'scope': 'Internal held-out BMI-missing stress on original 303 source rows; not external validation.',
        'source_rows': len(df),
        'source_bmi_max_absolute_formula_error': float(np.max(np.abs(X['BMI'] - calculated))),
        'raw_sha256': digest(ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'),
        'evaluation_sha256': digest(ROOT / 'ml/metrics/evaluation.json'),
        'targets': targets,
    }
    write_json(ROOT / 'output/verification/input_accuracy_guard.json', out)
    for target, result in targets.items():
        print(target, 'Brier full/missing', round(result['full']['brier'], 4), round(result['bmi_missing_and_imputed']['brier'], 4), 'decision changes', result['changed_binary_decisions'])


if __name__ == '__main__':
    main()
