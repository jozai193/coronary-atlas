"""Optional calibrated ensemble inference and sampled permutation attributions.

This module performs no training and never reads user-supplied model files.
"""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy.special import logit
from threadpoolctl import threadpool_limits
from ml.schema import ROOT, FEATURES, NUMERIC, CATEGORICAL, TARGETS, digest

CANDIDATE_ID = 'calibrated_ensemble_v1'
DIRECTORY = ROOT / 'models/candidates' / CANDIDATE_ID
MEMBERS = ('logistic_003', 'boosting', 'extra_trees', 'rbf_svm_sigmoid', 'catboost_native')


def native_frame(artifact, frame):
    pre = artifact['full']['logistic_003'].named_steps['preprocess']
    result = frame.copy()
    numeric = pre.named_transformers_['numeric'].named_steps['impute'].transform(frame[NUMERIC])
    category = pre.named_transformers_['categorical'].named_steps['impute'].transform(frame[CATEGORICAL])
    for i, name in enumerate(NUMERIC):
        result[name] = numeric[:, i]
    for i, name in enumerate(CATEGORICAL):
        result[name] = category[:, i].astype(str)
    return result[FEATURES]


def raw_probabilities(artifacts, frame):
    result = []
    for target in TARGETS:
        artifact = artifacts[target]
        native = native_frame(artifact, frame)
        members = np.column_stack([artifact['full'][name].predict_proba(
            native if name == 'catboost_native' else frame)[:, 1] for name in MEMBERS])
        uniform = members.mean(axis=1)
        result.append(artifact['calibrator'].predict_proba(logit(np.clip(uniform, 1e-6, 1-1e-6))[:, None])[:, 1])
    return np.column_stack(result)


def permutation_attributions(artifacts, background, frame, seed=20261025):
    """Paired permutations telescope exactly; attribution allocation is approximate."""
    if len(frame) != 1 or background.shape != (4, len(FEATURES)):
        raise ValueError('Expected one profile and four frozen background rows')
    rng = np.random.default_rng(seed)
    orders = []
    for _ in range(4):
        order = rng.permutation(len(FEATURES))
        orders.extend([order, order[::-1]])
    x = frame.iloc[0].to_numpy(dtype=object)
    paths = []
    for reference in background.to_numpy(dtype=object):
        for order in orders:
            row = reference.copy()
            path = [row.copy()]
            for feature in order:
                row[feature] = x[feature]
                path.append(row.copy())
            paths.extend(path)
    synthetic = pd.DataFrame(paths, columns=FEATURES)
    # Keep temporary hybrids in memory only. They are not additional patients.
    predictions = raw_probabilities(artifacts, synthetic).reshape(len(background), len(orders), len(FEATURES)+1, 4)
    values = np.zeros((len(FEATURES), 4))
    for bi in range(len(background)):
        for oi, order in enumerate(orders):
            values[order] += np.diff(predictions[bi, oi], axis=0)
    values /= len(background) * len(orders)
    base = predictions[:, :, 0].mean(axis=(0, 1))
    output = raw_probabilities(artifacts, frame)[0]
    residual = np.abs(base + values.sum(axis=0) - output)
    if not np.isfinite(values).all() or residual.max() > 1e-10:
        raise ValueError('Permutation attributions do not reconstruct raw calibrated output')
    return base, values, output, residual


class ResearchEnsemble:
    def __init__(self, directory=DIRECTORY, require_verified=True):
        directory = Path(directory)
        manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        if manifest.get('candidate_id') != CANDIDATE_ID or manifest.get('features') != FEATURES:
            raise ValueError('Ensemble candidate contract mismatch')
        if require_verified and manifest.get('inference_verified') is not True:
            raise ValueError('Ensemble candidate not verified for inference')
        for name, sha in manifest['evidence_hashes'].items():
            if digest(ROOT / name) != sha:
                raise ValueError(f'Candidate evidence changed: {name}')
        if set(manifest['artifacts']) != set(TARGETS) | {'background'}:
            raise ValueError('Incomplete candidate artifacts')
        loaded = {}
        for key, info in manifest['artifacts'].items():
            expected = f'{key}.joblib'
            if info['file'] != expected or digest(directory / expected) != info['sha256']:
                raise ValueError(f'Candidate artifact integrity failure: {key}')
            loaded[key] = joblib.load(directory / expected)
        self.background = loaded.pop('background')
        self.artifacts = loaded
        self.manifest = manifest

    def predict(self, features):
        frame = pd.DataFrame([{name: features.get(name) if features.get(name) is not None else np.nan
                               for name in FEATURES}], columns=FEATURES)
        for name in CATEGORICAL:
            frame[name] = frame[name].astype(object)
        with threadpool_limits(limits=1):
            base, values, p, residual = permutation_attributions(self.artifacts, self.background, frame)
        result = {}
        for i, target in enumerate(TARGETS):
            result[target] = {'probability': float(p[i]), 'classification': int(p[i] >= .5),
                'category': 'Lower' if p[i] < .3 else ('Intermediate' if p[i] < .7 else 'Higher'),
                'model': CANDIDATE_ID,
                'explanation': {'method': 'Sampled permutation attribution', 'unit': 'probability',
                    'base_value': float(base[i]), 'output_value': float(p[i]), 'additivity_error': float(residual[i]),
                    'factors': sorted([{'feature': name, 'contribution': float(values[j, i])}
                                       for j, name in enumerate(FEATURES)], key=lambda item: abs(item['contribution']), reverse=True),
                    'note': 'Approximate Shapley-style allocation using four fixed training reference rows and eight paired feature orders. Contributions telescope to this calibrated ensemble probability before coherence adjustment. Exact reconstruction does not make the allocation exact or clinically causal. Correlated-feature hybrids may be unrealistic; naturally missing inputs and attribution stability remain unvalidated.'}}
        return result
