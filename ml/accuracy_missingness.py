"""Saved-fold missingness stress test, with training-only native-model imputation."""
import os
for _key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'
import argparse
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy.special import logit
from threadpoolctl import threadpool_limits
from ml import accuracy_ensemble as exp
from ml.schema import ROOT, FEATURES, NUMERIC, CATEGORICAL, GROUPS, digest, write_json

OUT = ROOT / 'ml/experiments/accuracy_missingness_v1'
SCENARIOS = {'complete': [], 'no_laboratory': GROUPS['Laboratory'],
             'no_echo': GROUPS['Echocardiography'],
             'core_only': GROUPS['Laboratory'] + GROUPS['Echocardiography'] + GROUPS['ECG']}


def native_frame(artifact, frame):
    """Reuse same-training-row imputers; never fit on an inference frame."""
    pre = artifact['full']['logistic_003'].named_steps['preprocess']
    result = frame.copy()
    numeric = pre.named_transformers_['numeric'].named_steps['impute'].transform(frame[NUMERIC])
    category = pre.named_transformers_['categorical'].named_steps['impute'].transform(frame[CATEGORICAL])
    for i, name in enumerate(NUMERIC):
        result[name] = numeric[:, i]
    for i, name in enumerate(CATEGORICAL):
        result[name] = category[:, i].astype(str)
    return result[FEATURES]


def predict(artifact, frame):
    native = native_frame(artifact, frame)
    members = np.column_stack([artifact['full'][name].predict_proba(
        native if name == 'catboost_native' else frame)[:, 1] for name in exp.ENSEMBLE_MEMBERS])
    uniform = members.mean(axis=1)
    return {'baseline': artifact['full'][artifact['selected']].predict_proba(frame)[:, 1],
        'sigmoid_uniform': artifact['calibrator'].predict_proba(
            logit(np.clip(uniform, 1e-6, 1 - 1e-6))[:, None])[:, 1]}


def prepare():
    if OUT.exists():
        raise FileExistsError('Refusing missingness overwrite')
    exp.check_receipt()
    inputs = [Path(__file__), ROOT / 'docs/accuracy_missingness_protocol.md',
              exp.OUT / 'manifest.json', exp.OUT / 'fit_receipt.json', exp.OUT / 'results.json']
    write_json(OUT / 'manifest.json', {'input_hashes': {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs},
        'scenarios': SCENARIOS, 'scope': 'Post-search artificial missingness; no naturally incomplete validation.'})
    print('Missingness protocol frozen')


def generate():
    exp.assert_hashes(exp.load(OUT / 'manifest.json')['input_hashes'])
    manifest, _ = exp.check_receipt()
    X, y, _ = exp.source_data()
    historical = pd.read_csv(exp.OUT / 'predictions.csv', float_precision='round_trip')
    rows = []
    with threadpool_limits(limits=1):
        for i, role in enumerate(manifest['roles'], 1):
            artifact = joblib.load(exp.OUT / 'private' / (exp.role_name(role) + '.joblib'))
            te, ti = role['test'], exp.ORDER.index(role['target'])
            old = historical[(historical.repeat == role['repeat']) & (historical.fold == role['fold']) &
                             (historical.target == role['target'])].sort_values('row')
            for scenario, missing in SCENARIOS.items():
                frame = X.iloc[te].copy()
                for name in missing:
                    frame[name] = np.nan if name in NUMERIC else pd.Series(np.nan, index=frame.index, dtype=object)
                prediction = predict(artifact, frame)
                if scenario == 'complete':
                    for arm in prediction:
                        np.testing.assert_allclose(prediction[arm], old[arm], atol=1e-12, rtol=0)
                for j, row in enumerate(te):
                    rows.append({'scenario': scenario, 'repeat': role['repeat'], 'fold': role['fold'],
                        'target': role['target'], 'row': row, 'y': int(y[row, ti]),
                        **{arm: float(p[j]) for arm, p in prediction.items()}})
            if i % 10 == 0:
                print(f'Masked replay {i}/60', flush=True)
    return pd.DataFrame(rows)


def summarize(frame):
    result = {'scope': 'Post-search artificial masks of originally complete source records; no clinical completeness claim.',
              'scenarios': {}}
    original = exp.ARMS
    try:
        exp.ARMS = ('baseline', 'sigmoid_uniform')
        for name in SCENARIOS:
            summary = exp.summarize(frame[frame.scenario == name])
            # The earlier engineering screen was declared for complete inputs only.
            summary['comparisons']['sigmoid_uniform'].pop('engineering_screen_passed')
            result['scenarios'][name] = summary
    finally:
        exp.ARMS = original
    return result


def run():
    if (OUT / 'predictions.csv').exists():
        raise FileExistsError('Refusing missingness result overwrite')
    frame = generate()
    frame.to_csv(OUT / 'predictions.csv', index=False)
    result = summarize(frame)
    write_json(OUT / 'results.json', result)
    write_json(OUT / 'receipt.json', {name: digest(OUT / name) for name in ('manifest.json', 'predictions.csv', 'results.json')})
    print(json.dumps({name: r['comparisons']['sigmoid_uniform']['brier'] for name, r in result['scenarios'].items()}, indent=2))


def verify():
    for name, sha in exp.load(OUT / 'receipt.json').items():
        if digest(OUT / name) != sha:
            raise ValueError(f'Missingness evidence changed: {name}')
    saved = pd.read_csv(OUT / 'predictions.csv', float_precision='round_trip')
    replay = generate()
    pd.testing.assert_frame_equal(saved, replay, check_exact=True)
    if summarize(saved) != exp.load(OUT / 'results.json'):
        raise ValueError('Missingness metrics differ')
    report = {'status': 'passed', 'prediction_rows_replayed': len(saved),
        'model_scenario_roles': 60 * len(SCENARIOS),
        'results_sha256': digest(OUT / 'results.json')}
    write_json(OUT / 'verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'run', 'verify'])
    globals()[parser.parse_args().stage]()
