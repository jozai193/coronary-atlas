"""Frozen source-only reduced model and independent AngioCAD transport check.

Run `fit` before `evaluate`. The fit artifact, source predictions and protocol
are hash-checked by evaluate. This module does not load or alter app models.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, brier_score_loss, confusion_matrix,
                             f1_score, precision_score, recall_score,
                             roc_auc_score)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.schema import ROOT, TARGETS, digest, read_data

SEED = 20261007
PROTOCOL = ROOT / 'docs/angiocad_external_protocol.md'
SOURCE = ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'
RAW = ROOT / 'data/external_audit/angiocad_v1'
OUT = ROOT / 'output/research/angiocad_v1'
EXPECTED_SOURCE = '739343245c2ba578b541370217531750d8e936022f928b83e0d91756caa3ff0b'
EXPECTED_RAW = {
    'AngioCAD_Features.xlsx': '978f2415ab52f11724e1ef00bb63597b8497487afd84b97f7112fc7975a33295',
    'AngioCAD_Labels.xlsx': '5bba3f4ba8bed0df0d2f412d5e2ca6deacca0eff20d531a599fe1b8f4d897425',
}
MAPPING = {
    'Age': 'Age', 'Sex': 'Sex', 'BMI': 'BMI', 'DM': 'DM', 'HTN': 'HTN',
    'Current Smoker': 'Current Smoker', 'FBS': 'FBS', 'CR': 'Cr',
    'TG': 'TG', 'LDL': 'LDL', 'HDL': 'HDL', 'WBC': 'leukocytes', 'PLT': 'PLT',
}
FEATURES = list(MAPPING)
NUMERIC = ['Age', 'BMI', 'FBS', 'CR', 'TG', 'LDL', 'HDL', 'WBC', 'PLT']
CATEGORICAL = ['Sex', 'DM', 'HTN', 'Current Smoker']
BOUNDS = {'Age': (18, 100), 'BMI': (14, 60), 'FBS': (40, 600),
          'CR': (0.3, 10), 'TG': (20, 2000), 'LDL': (5, 400),
          'HDL': (5, 150), 'WBC': (2000, 50000), 'PLT': (20, 1000)}
MAIN = {'lad': ['Prox LAD', 'Mid LAD', 'Dist LAD'],
        'lcx': ['Prox LCX', 'Mid LCX', 'Dist LCX'],
        'rca': ['Prox RCA', 'Mid RCA', 'Dist RCA']}
BRANCH = {'lad': MAIN['lad'] + ['1st dig', '2nd dig'],
          'lcx': MAIN['lcx'] + ['OM'],
          'rca': MAIN['rca'] + ['PDA', 'PLB']}
SEGMENTS = ['LM'] + BRANCH['lad'] + BRANCH['lcx'] + BRANCH['rca']
POSITIVE_BINS = {'51-75', '76-90', '91-99', '100'}
NEGATIVE_BINS = {'NL', '1-25'}
AMBIGUOUS_BINS = {'26-50'}
ALL_BINS = POSITIVE_BINS | NEGATIVE_BINS | AMBIGUOUS_BINS


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False,
                               allow_nan=False) + '\n', encoding='utf-8')


def pipeline() -> Pipeline:
    number = Pipeline([('impute', SimpleImputer(strategy='median', keep_empty_features=True)),
                       ('scale', StandardScaler())])
    category = Pipeline([('impute', SimpleImputer(strategy='most_frequent', keep_empty_features=True)),
                         ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    pre = ColumnTransformer([('numeric', number, NUMERIC),
                             ('categorical', category, CATEGORICAL)])
    return Pipeline([('preprocess', pre),
                     ('model', LogisticRegression(C=0.03, max_iter=3000,
                                                  random_state=SEED))])


def fixed_metrics(y: np.ndarray, p: np.ndarray, prevalence: float) -> dict:
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    if len(y) == 0 or len(np.unique(y)) != 2:
        raise ValueError('Both endpoint classes are required for the fixed metrics')
    decisions = p >= 0.5
    tn, fp, fn, tp = confusion_matrix(y, decisions, labels=[0, 1]).ravel()
    return {
        'n': int(len(y)), 'positives': int(y.sum()),
        'prevalence': float(y.mean()), 'mean_probability': float(p.mean()),
        'roc_auc': float(roc_auc_score(y, p)),
        'brier': float(brier_score_loss(y, p)),
        'source_prevalence_constant_brier': float(np.mean((y - prevalence) ** 2)),
        'accuracy': float(accuracy_score(y, decisions)),
        'sensitivity': float(recall_score(y, decisions, zero_division=0)),
        'specificity': float(tn / (tn + fp)),
        'precision': float(precision_score(y, decisions, zero_division=0)),
        'f1': float(f1_score(y, decisions, zero_division=0)),
        'confusion': {'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)},
    }


def fit_source() -> None:
    if OUT.exists():
        raise FileExistsError(f'Frozen experiment directory already exists: {OUT}')
    if digest(SOURCE) != EXPECTED_SOURCE:
        raise ValueError('Source workbook hash mismatch')
    source = read_data()
    X = source[FEATURES].copy()
    oof = pd.DataFrame({'row_index': np.arange(len(X))})
    models = {}
    source_metrics = {}
    for target, column in TARGETS.items():
        y = (source[column] == ('CAD' if target == 'cad' else 'Stenotic')).astype(int).to_numpy()
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
        probs = np.full(len(y), np.nan)
        folds = np.full(len(y), -1)
        for fold, (training, held_out) in enumerate(cv.split(X, y)):
            fitted = pipeline().fit(X.iloc[training], y[training])
            probs[held_out] = fitted.predict_proba(X.iloc[held_out])[:, 1]
            folds[held_out] = fold
        assert np.isfinite(probs).all() and (folds >= 0).all()
        models[target] = pipeline().fit(X, y)
        source_metrics[target] = fixed_metrics(y, probs, float(y.mean()))
        oof[f'{target}_y'] = y
        oof[f'{target}_p'] = probs
        oof[f'{target}_fold'] = folds
    OUT.mkdir(parents=True, exist_ok=False)
    models_path = OUT / 'frozen_source_models.joblib'
    oof_path = OUT / 'source_oof.csv'
    joblib.dump(models, models_path, compress=3)
    oof.to_csv(oof_path, index=False, float_format='%.17g')
    save_json(OUT / 'frozen_manifest.json', {
        'protocol_sha256': sha(PROTOCOL), 'runner_sha256': sha(Path(__file__)),
        'source_sha256': digest(SOURCE), 'source_rows': len(source),
        'features': FEATURES, 'categorical': CATEGORICAL, 'numeric': NUMERIC,
        'seed': SEED, 'model_sha256': sha(models_path), 'source_oof_sha256': sha(oof_path),
        'source_metrics': source_metrics,
        'versions': {'python': platform.python_version(), 'numpy': np.__version__,
                     'pandas': pd.__version__, 'sklearn': sklearn.__version__},
    })
    print(f'Frozen source fit: {len(source)} rows, {len(FEATURES)} features; {OUT}')


def normalize_bin(value: object) -> str:
    if pd.isna(value):
        raise ValueError('Missing segment label')
    result = str(value).strip()
    if result.endswith('.0') and result[:-2].isdigit():
        result = result[:-2]
    if result not in ALL_BINS:
        raise ValueError(f'Unknown stenosis bin: {result!r}')
    return result


def endpoint(values: list[str]) -> int | None:
    """Positive overrides boundary; boundary prevents a negative assignment."""
    bins = [normalize_bin(v) for v in values]
    if any(value in POSITIVE_BINS for value in bins):
        return 1
    if any(value in AMBIGUOUS_BINS for value in bins):
        return None
    return 0


def validate_binary(series: pd.Series, name: str) -> pd.Series:
    number = pd.to_numeric(series, errors='raise')
    if not number.dropna().isin([0, 1]).all():
        raise ValueError(f'Unexpected binary code in {name}')
    return number.map({0: '0', 1: '1'}).astype(object)


def external_features(frame: pd.DataFrame) -> pd.DataFrame:
    if any(field not in frame for field in MAPPING.values()):
        raise ValueError('Missing mapped external clinical field')
    X = pd.DataFrame(index=frame.index)
    for source, external in MAPPING.items():
        if source == 'Sex':
            codes = frame[external].map({'Male': 'Male', 'Female': 'Fmale'})
            if codes.isna().sum() != frame[external].isna().sum():
                raise ValueError('Unexpected sex code')
            X[source] = codes
        elif source in ['DM', 'HTN', 'Current Smoker']:
            X[source] = validate_binary(frame[external], external)
        else:
            X[source] = pd.to_numeric(frame[external], errors='raise')
    return X[FEATURES]


def eligibility(X: pd.DataFrame) -> tuple[dict[str, np.ndarray], dict]:
    age_present = X['Age'].notna().to_numpy()
    enough = (X.notna().sum(axis=1) >= 10).to_numpy()
    in_bounds = np.ones(len(X), dtype=bool)
    violation_by_field = {}
    for field, (low, high) in BOUNDS.items():
        observed = X[field].notna()
        bad = observed & ~X[field].between(low, high)
        violation_by_field[field] = int(bad.sum())
        in_bounds &= ~bad.to_numpy()
    primary = age_present & enough & in_bounds
    complete = primary & X.notna().all(axis=1).to_numpy()
    masks = {'primary': primary, 'all_age_present': age_present,
             'complete_inputs': complete}
    audit = {
        'matched_feature_rows': int(len(X)), 'primary_eligible': int(primary.sum()),
        'all_age_present': int(age_present.sum()), 'complete_inputs': int(complete.sum()),
        'missing_age': int((~age_present).sum()), 'fewer_than_10_observed': int((~enough).sum()),
        'any_range_violation': int((~in_bounds).sum()),
        'range_violations_by_field': violation_by_field,
        'input_missing_counts': {field: int(X[field].isna().sum()) for field in FEATURES},
        'primary_input_missing_counts': {field: int(X.loc[primary, field].isna().sum()) for field in FEATURES},
    }
    return masks, audit


def joined_external() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    for filename, expected in EXPECTED_RAW.items():
        if digest(RAW / filename) != expected:
            raise ValueError(f'External workbook hash mismatch: {filename}')
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Conditional Formatting extension is not supported')
        clinical = pd.read_excel(RAW / 'AngioCAD_Features.xlsx')
        labels = pd.read_excel(RAW / 'AngioCAD_Labels.xlsx')
    for name, frame in [('clinical', clinical), ('labels', labels)]:
        if frame['ID'].isna().any() or frame['ID'].duplicated().any():
            raise ValueError(f'{name} IDs must be complete and unique')
    if len(clinical) != 377 or len(labels) != 413:
        raise ValueError('Unexpected external cohort size')
    if not set(clinical.ID).issubset(set(labels.ID)):
        raise ValueError('Unmatched clinical patient ID')
    clinical = clinical.sort_values('ID').reset_index(drop=True)
    labels = labels.set_index('ID').loc[clinical.ID].reset_index()
    for segment in SEGMENTS:
        original = clinical[segment].map(normalize_bin)
        independent = labels[segment].map(normalize_bin)
        if not original.equals(independent):
            raise ValueError(f'Feature/label workbook disagreement in {segment}')
    X = external_features(clinical)
    # ID and duplicated outcome columns are gone before any model sees X.
    assert X.columns.tolist() == FEATURES and not set(X.columns) & set(SEGMENTS)
    return X, labels, clinical


def make_endpoints(labels: pd.DataFrame, branch: bool) -> pd.DataFrame:
    definitions = BRANCH if branch else MAIN
    result = pd.DataFrame(index=labels.index)
    for target in ['lad', 'lcx', 'rca']:
        result[target] = [endpoint([row[field] for field in definitions[target]])
                          for _, row in labels.iterrows()]
    cad_fields = ['LM'] + sum((definitions[t] for t in ['lad', 'lcx', 'rca']), [])
    result['cad'] = [endpoint([row[field] for field in cad_fields])
                     for _, row in labels.iterrows()]
    return result[['cad', 'lad', 'lcx', 'rca']]


def bootstrap_interval(y: np.ndarray, p: np.ndarray, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    aucs, briers = [], []
    for _ in range(1000):
        picked = rng.integers(0, len(y), len(y))
        yy, pp = y[picked], p[picked]
        briers.append(brier_score_loss(yy, pp))
        if len(np.unique(yy)) == 2:
            aucs.append(roc_auc_score(yy, pp))
    return {'roc_auc_95': np.quantile(aucs, [0.025, 0.975]).tolist(),
            'brier_95': np.quantile(briers, [0.025, 0.975]).tolist(),
            'valid_auc_resamples': len(aucs)}


def evaluate_external() -> None:
    if (OUT / 'external_results.json').exists():
        raise FileExistsError('External scoring already recorded; preserve the first result')
    manifest = json.loads((OUT / 'frozen_manifest.json').read_text(encoding='utf-8'))
    expected = {'protocol_sha256': sha(PROTOCOL), 'runner_sha256': sha(Path(__file__)),
                'source_sha256': digest(SOURCE), 'model_sha256': sha(OUT / 'frozen_source_models.joblib'),
                'source_oof_sha256': sha(OUT / 'source_oof.csv')}
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError('Frozen model/protocol/source identity changed before evaluation')
    if manifest['source_sha256'] != EXPECTED_SOURCE or manifest['features'] != FEATURES:
        raise ValueError('Unexpected source or feature contract')
    models = joblib.load(OUT / 'frozen_source_models.joblib')
    X, labels, clinical = joined_external()
    masks, audit = eligibility(X)
    if audit['primary_eligible'] != 363:
        raise ValueError('Primary eligibility count differs from pre-score QC')
    endpoint_sets = {'main': make_endpoints(labels, branch=False),
                     'branch_inclusive': make_endpoints(labels, branch=True)}
    score_sets = {'primary_main': ('primary', 'main'),
                  'all_age_main': ('all_age_present', 'main'),
                  'complete_main': ('complete_inputs', 'main'),
                  'primary_branch': ('primary', 'branch_inclusive')}
    predictions = pd.DataFrame({'row_index': np.arange(len(X))})
    for key, mask in masks.items():
        predictions[f'in_{key}'] = mask
    for kind, ends in endpoint_sets.items():
        for target in TARGETS:
            predictions[f'{kind}_{target}_y'] = ends[target]
    source_prev = {t: manifest['source_metrics'][t]['prevalence'] for t in TARGETS}
    scores = {}
    for index, target in enumerate(TARGETS):
        p = models[target].predict_proba(X)[:, 1]
        if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
            raise ValueError('Invalid model probability')
        predictions[f'{target}_p'] = p
        for name, (mask_name, endpoint_name) in score_sets.items():
            y_series = endpoint_sets[endpoint_name][target]
            selected = masks[mask_name] & y_series.notna().to_numpy()
            y = y_series.loc[selected].astype(int).to_numpy()
            pp = p[selected]
            stats = fixed_metrics(y, pp, source_prev[target])
            stats['bootstrap_conditional_95'] = bootstrap_interval(y, pp, SEED + index * 20 + list(score_sets).index(name))
            stats['ambiguous_excluded_from_cohort'] = int((masks[mask_name] & y_series.isna().to_numpy()).sum())
            scores.setdefault(name, {})[target] = stats
    predictions_path = OUT / 'external_predictions.csv'
    predictions.to_csv(predictions_path, index=False, float_format='%.17g')
    save_json(OUT / 'external_results.json', {
        'design': 'source-only frozen 13-input logistic; independent AngioCAD center; 0.5 cutoff',
        'not_validation_of_55_input_app': True,
        'source_model_manifest_sha256': sha(OUT / 'frozen_manifest.json'),
        'protocol_sha256': sha(PROTOCOL), 'runner_sha256': sha(Path(__file__)),
        'external_workbook_sha256': EXPECTED_RAW,
        'external_label_rows': 413, 'external_feature_rows': len(clinical),
        'source_oof': manifest['source_metrics'], 'eligibility': audit,
        'scores': scores, 'predictions_sha256': sha(predictions_path),
        'bootstrap_note': 'Fixed predictions; patient-row resampling only. No source-fit or endpoint uncertainty.',
    })
    print(f"AngioCAD scored once: {audit['primary_eligible']} primary input-eligible rows; {OUT}")
    for target, value in scores['primary_main'].items():
        print(target, 'n', value['n'], 'AUC', round(value['roc_auc'], 3),
              'Brier', round(value['brier'], 3), 'recall', round(value['sensitivity'], 3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['fit', 'evaluate'])
    args = parser.parse_args()
    if args.phase == 'fit':
        fit_source()
    else:
        evaluate_external()
