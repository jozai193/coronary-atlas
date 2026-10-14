"""Prespecified feature-group and held-out missing-input audit.

Protocol: docs/modality_audit_protocol.md. This writes only to the new
ml/experiments/modality_v2/ evidence directory and never changes production.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import importlib.metadata
import json
import platform
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

from ml.evaluate import metrics
from ml.schema import (
    CATEGORICAL, FEATURES, GROUPS, NUMERIC, PROHIBITED, ROOT, SEED, TARGETS,
    digest, read_data,
)

SEEDS = [20261007, 20261108]
FOLDS = 5
LOGISTIC_C = 0.03
OUT = ROOT / 'ml/experiments/modality_v2'
OPTIONAL_GROUPS = ['ECG', 'Laboratory', 'Echocardiography']


def feature_sets():
    core_groups = ['Demographics', 'Vitals', 'History & examination']
    core = [name for group in core_groups for name in GROUPS[group]]
    all_features = list(FEATURES)
    scenarios = {
        'core': core,
        'core_plus_ecg': core + GROUPS['ECG'],
        'core_plus_laboratory': core + GROUPS['Laboratory'],
        'core_plus_echo': core + GROUPS['Echocardiography'],
        'all_features': all_features,
    }
    for group_name in GROUPS:
        omitted = [c for c in all_features if c not in GROUPS[group_name]]
        key = group_name.lower().replace(' & examination', '').replace(' ', '_')
        scenarios[f'all_minus_{key}'] = omitted
    for name, columns in scenarios.items():
        if not columns or len(columns) != len(set(columns)):
            raise ValueError(f'Invalid feature set: {name}')
        if set(columns) - set(FEATURES) or set(columns) & PROHIBITED:
            raise ValueError(f'Feature contract violation: {name}')
    if set(scenarios['all_features']) != set(FEATURES):
        raise ValueError('All-feature scenario must match the allowlist exactly.')
    return scenarios


def audit_pipeline(columns):
    """Build the production-equivalent transforms for the chosen allowlist slice."""
    columns = list(columns)
    if not columns or set(columns) - set(FEATURES) or set(columns) & PROHIBITED:
        raise ValueError('Audit pipeline received an invalid feature subset.')
    numeric = [c for c in NUMERIC if c in columns]
    categorical = [c for c in CATEGORICAL if c in columns]
    transformers = []
    if numeric:
        transformers.append(('numeric', Pipeline([
            ('impute', SimpleImputer(strategy='median', keep_empty_features=True)),
            ('scale', StandardScaler()),
        ]), numeric))
    if categorical:
        transformers.append(('categorical', Pipeline([
            ('impute', SimpleImputer(strategy='most_frequent', keep_empty_features=True)),
            ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
        ]), categorical))
    preprocess = ColumnTransformer(transformers)
    model = LogisticRegression(C=LOGISTIC_C, max_iter=3000, random_state=SEED)
    return Pipeline([('preprocess', preprocess), ('model', model)])


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def probability_metrics(y, probability):
    result = metrics(np.asarray(y), np.asarray(probability))
    result['average_precision'] = float(average_precision_score(y, probability))
    return jsonable(result)


def labels_for(df):
    labels = {}
    for target, column in TARGETS.items():
        positive = 'CAD' if target == 'cad' else 'Stenotic'
        labels[target] = (df[column] == positive).astype(int)
    return labels


def duplicate_audit(df):
    full_duplicate_rows = np.flatnonzero(df.duplicated(keep=False)).tolist()
    feature_duplicate_rows = np.flatnonzero(df[FEATURES].duplicated(keep=False)).tolist()
    duplicate_groups = []
    if feature_duplicate_rows:
        grouped = df.iloc[feature_duplicate_rows].groupby(
            FEATURES, sort=False, dropna=False, observed=False
        ).indices
        for positions in grouped.values():
            rows = [feature_duplicate_rows[position] for position in positions]
            if len(rows) > 1:
                targets = {name: df.loc[rows, col].astype(str).tolist()
                           for name, col in TARGETS.items()}
                duplicate_groups.append({
                    'row_indices': rows,
                    'target_values': targets,
                    'target_conflict': any(len(set(values)) > 1 for values in targets.values()),
                })
    return {
        'exact_full_row_duplicate_indices_zero_based': full_duplicate_rows,
        'exact_feature_vector_duplicate_indices_zero_based': feature_duplicate_rows,
        'duplicate_feature_vector_groups': duplicate_groups,
        'patient_identity_limit': 'No patient identifier is available; distinct rows cannot be confirmed to represent distinct people.',
    }


def integrity_audit(df, labels):
    feature_columns = list(df[FEATURES].columns)
    if len(FEATURES) != 55 or set(feature_columns) != set(FEATURES):
        raise ValueError('Input does not match the 55-field allowlist.')
    if set(feature_columns) & PROHIBITED or set(PROHIBITED) != set(TARGETS.values()):
        raise ValueError('A prohibited target entered the input contract.')

    missing = {c: int(df[c].isna().sum()) for c in FEATURES}
    target_counts = {}
    for target, y in labels.items():
        target_counts[target] = {
            'source_column': TARGETS[target],
            'positive': int(y.sum()),
            'negative': int((1 - y).sum()),
            'positive_fraction': float(y.mean()),
            'source_values': {str(k): int(v) for k, v in df[TARGETS[target]].value_counts().items()},
        }

    vessel_positive = df[['LAD', 'LCX', 'RCA']].eq('Stenotic')
    cath_positive = df['Cath'].eq('CAD')
    vessel_or = vessel_positive.any(axis=1)
    mismatch = cath_positive.ne(vessel_or)
    disagreement_indices = np.flatnonzero(mismatch).tolist()
    vessel_count = vessel_positive.sum(axis=1).value_counts().sort_index()

    exact_input_target_matches = []
    pure_common_levels = {target: {} for target in TARGETS}
    for feature in FEATURES:
        values = df[feature].astype(str)
        for target, y in labels.items():
            target_values = df[TARGETS[target]].astype(str)
            if values.equals(target_values):
                exact_input_target_matches.append({'feature': feature, 'target': target, 'relation': 'identity'})
            elif len(values.unique()) == 2:
                # Complement checks are meaningful only for binary 0/1-like values.
                mapped = values.map({str(v): i for i, v in enumerate(sorted(values.unique()))})
                if np.array_equal(mapped.to_numpy(), 1 - y.to_numpy()) or np.array_equal(mapped.to_numpy(), y.to_numpy()):
                    exact_input_target_matches.append({'feature': feature, 'target': target, 'relation': 'binary_encoding'})

            table = pd.DataFrame({'value': values, 'y': y.to_numpy()}).groupby('value', sort=False)['y'].agg(['size', 'nunique', 'mean'])
            pure = table[(table['size'] >= 10) & (table['nunique'] == 1)]
            if not pure.empty:
                pure_common_levels[target][feature] = [
                    {'value': str(level), 'n': int(row['size']), 'positive_fraction': float(row['mean'])}
                    for level, row in pure.iterrows()
                ]

    overlaps = {}
    for left, right in combinations(['LAD', 'LCX', 'RCA'], 2):
        overlaps[f'{left}&{right}'] = int((vessel_positive[left] & vessel_positive[right]).sum())

    groups = {name: list(values) for name, values in GROUPS.items()}
    groups['Core'] = [c for name in ['Demographics', 'Vitals', 'History & examination'] for c in GROUPS[name]]
    return {
        'rows': int(len(df)),
        'input_count': int(len(FEATURES)),
        'input_allowlist_sha256': __import__('hashlib').sha256('\n'.join(FEATURES).encode()).hexdigest(),
        'prohibited_targets': sorted(PROHIBITED),
        'missing_inputs_by_feature': missing,
        'missing_input_cells': int(sum(missing.values())),
        'target_counts': target_counts,
        'cath_vs_vessel_or': {
            'relation_checked': 'Cath == CAD iff at least one of LAD, LCX, or RCA == Stenotic',
            'matches': int((~mismatch).sum()),
            'mismatches': int(mismatch.sum()),
            'disagreement_row_indices_zero_based': disagreement_indices,
            'disagreement_worksheet_rows': [i + 2 for i in disagreement_indices],
            'positive_vessel_count_distribution': {str(int(k)): int(v) for k, v in vessel_count.items()},
            'pairwise_vessel_positive_overlaps': overlaps,
            'labels_changed': False,
        },
        'duplicates': duplicate_audit(df),
        'constant_features': [c for c in FEATURES if df[c].nunique(dropna=False) <= 1],
        'exact_input_target_matches_or_binary_encodings': exact_input_target_matches,
        'pure_feature_levels_n_at_least_10': pure_common_levels,
        'pure_level_note': 'These descriptive in-sample value counts are a leakage screen, not feature selection or evidence of a causal/deterministic mechanism.',
        'feature_groups': groups,
        'all_features_exactly_match_allowlist': set(FEATURES) == set(feature_columns),
    }


def fold_predictions(fitted, X_test, row_indices, y, target, repeat, seed, fold, scenario, columns):
    probability = fitted.predict_proba(X_test[columns])[:, 1]
    rows = []
    for idx, p in zip(row_indices, probability):
        rows.append({
            'target': target, 'repeat': repeat, 'seed': seed, 'fold': fold,
            'row_index': int(idx), 'y': int(y.loc[idx]),
            'probability': float(p), 'classification_at_0_5': int(p >= 0.5),
            'scenario': scenario,
        })
    return probability, rows


def heldout_mask(X_test, omitted_groups):
    masked = X_test.copy()
    for group in omitted_groups:
        for column in GROUPS[group]:
            masked[column] = np.nan
    return masked


def run_experiment(df, labels, sets):
    X = df[FEATURES]
    all_rows = []
    missing_rows = []
    target_results = {}
    for target, y in labels.items():
        target_results[target] = {'repeats': []}
        for repeat, seed in enumerate(SEEDS, start=1):
            split = StratifiedKFold(FOLDS, shuffle=True, random_state=seed)
            oof_ablation = {name: np.full(len(y), np.nan) for name in sets}
            missing_scenarios = ['complete', 'missing_ecg', 'missing_laboratory', 'missing_echocardiography', 'core_only']
            oof_missing = {name: np.full(len(y), np.nan) for name in missing_scenarios}
            folds = []
            for fold, (train_indices, test_indices) in enumerate(split.split(X, y), start=1):
                X_train = X.iloc[train_indices]
                X_test = X.iloc[test_indices]
                y_train = y.iloc[train_indices]
                y_test = y.iloc[test_indices]
                fold_record = {
                    'fold': fold - 1,
                    'train_indices': train_indices.tolist(),
                    'test_indices': test_indices.tolist(),
                    'ablation_metrics': {},
                    'missingness_metrics': {},
                }
                fitted_all = None
                for scenario, columns in sets.items():
                    fitted = audit_pipeline(columns).fit(X_train[columns], y_train)
                    probability = fitted.predict_proba(X_test[columns])[:, 1]
                    oof_ablation[scenario][test_indices] = probability
                    fold_record['ablation_metrics'][scenario] = probability_metrics(y_test, probability)
                    all_rows.extend({
                        'target': target, 'repeat': repeat, 'seed': seed, 'fold': fold - 1,
                        'row_index': int(idx), 'y': int(y.loc[idx]),
                        'probability': float(p), 'classification_at_0_5': int(p >= 0.5),
                        'scenario': scenario,
                    } for idx, p in zip(test_indices, probability))
                    if scenario == 'all_features':
                        fitted_all = fitted

                if fitted_all is None:
                    raise RuntimeError('All-feature model was not fitted in this fold.')
                masks = {
                    'complete': [],
                    'missing_ecg': ['ECG'],
                    'missing_laboratory': ['Laboratory'],
                    'missing_echocardiography': ['Echocardiography'],
                    'core_only': OPTIONAL_GROUPS,
                }
                for scenario, omitted_groups in masks.items():
                    test_frame = heldout_mask(X_test, omitted_groups) if omitted_groups else X_test
                    probability = fitted_all.predict_proba(test_frame[FEATURES])[:, 1]
                    oof_missing[scenario][test_indices] = probability
                    fold_record['missingness_metrics'][scenario] = probability_metrics(y_test, probability)
                    missing_rows.extend({
                        'target': target, 'repeat': repeat, 'seed': seed, 'fold': fold - 1,
                        'row_index': int(idx), 'y': int(y.loc[idx]),
                        'probability': float(p), 'classification_at_0_5': int(p >= 0.5),
                        'scenario': scenario,
                        'masked_groups': ','.join(omitted_groups),
                    } for idx, p in zip(test_indices, probability))
                folds.append(fold_record)

            for name, values in {**oof_ablation, **{f'missingness:{k}': v for k, v in oof_missing.items()}}.items():
                if not np.isfinite(values).all():
                    raise RuntimeError(f'Incomplete out-of-fold coverage for {target} repeat {repeat} {name}.')

            ablation_summary = {
                name: probability_metrics(y, probabilities)
                for name, probabilities in oof_ablation.items()
            }
            missing_summary = {
                name: probability_metrics(y, probabilities)
                for name, probabilities in oof_missing.items()
            }
            target_results[target]['repeats'].append({
                'repeat': repeat,
                'seed': seed,
                'n_rows': int(len(y)),
                'positive': int(y.sum()),
                'negative': int((1 - y).sum()),
                'ablation': ablation_summary,
                'missingness': missing_summary,
                'folds': folds,
            })
    return target_results, pd.DataFrame(all_rows), pd.DataFrame(missing_rows)


def subgroup_summary(df, labels, ablation_predictions):
    bands = pd.cut(df['Age'], [-np.inf, 50, 65, np.inf], right=False,
                   labels=['<50', '50-64', '65+'])
    strata = {
        'Sex': df['Sex'].astype(str),
        'Age band': bands.astype(str),
    }
    minimum_n = 30
    minimum_per_class = 10
    result = {}
    full = ablation_predictions[ablation_predictions['scenario'] == 'all_features']
    for stratum, values in strata.items():
        result[stratum] = {}
        for level in sorted(values.unique()):
            idx = np.flatnonzero(values.to_numpy() == level)
            result[stratum][str(level)] = {}
            for target, y in labels.items():
                pos = int(y.iloc[idx].sum())
                neg = int(len(idx) - pos)
                record = {'n': int(len(idx)), 'positive': pos, 'negative': neg,
                          'positive_fraction': float(pos / len(idx)) if len(idx) else None}
                if len(idx) >= minimum_n and pos >= minimum_per_class and neg >= minimum_per_class:
                    record['repeat_metrics'] = {}
                    for repeat in sorted(full['repeat'].unique()):
                        subset = full[(full['target'] == target) & (full['repeat'] == repeat) & full['row_index'].isin(idx)]
                        record['repeat_metrics'][str(int(repeat))] = probability_metrics(
                            subset['y'].to_numpy(), subset['probability'].to_numpy()
                        )
                    record['metric_status'] = 'computed_descriptively'
                else:
                    record['metric_status'] = 'counts_only_below_prespecified_minimum'
                result[stratum][str(level)][target] = record
    return {
        'minimum_total_n_for_metrics': minimum_n,
        'minimum_per_class_for_metrics': minimum_per_class,
        'strata': result,
        'interpretation': 'Descriptive cohort summaries only; not fairness analyses, independent validation, or reliable conclusions for small strata.',
    }


def source_and_runtime_manifest():
    paths = [
        'data/raw/extention of Z-Alizadeh sani dataset.xlsx',
        'ml/schema.py', 'ml/preprocessing.py', 'ml/train.py', 'ml/predict.py',
        'docs/dataset_analysis.md', 'docs/model_improvement_protocol.md',
        'docs/model_improvement_results.md', 'docs/modality_audit_protocol.md',
        'ml/modality_audit.py', 'ml/metrics/evaluation.json',
        'ml/metrics/sensitivity.json', 'models/metadata.json',
    ]
    for target in TARGETS:
        paths.extend([f'ml/metrics/{target}_oof.csv', f'models/{target}.joblib'])
    source_hashes = {path: digest(ROOT / path) for path in paths}
    versions = {'python': platform.python_version()}
    for package in ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'threadpoolctl']:
        versions[package] = importlib.metadata.version(package)
    return {
        'source_hashes_sha256': source_hashes,
        'runtime': versions,
        'cpu_thread_limit': 1,
    }


def main():
    if OUT.exists():
        raise FileExistsError(f'{OUT} already exists; preserve prior evidence and choose a new versioned output path.')
    df = read_data()
    labels = labels_for(df)
    sets = feature_sets()
    integrity = integrity_audit(df, labels)
    if integrity['missing_input_cells'] != 0:
        raise ValueError('Frozen source changed: protocol assumes a complete workbook.')
    target_results, ablation, missingness = run_experiment(df, labels, sets)
    subgroups = subgroup_summary(df, labels, ablation)
    manifest = source_and_runtime_manifest()
    results = {
        'protocol': 'docs/modality_audit_protocol.md',
        'method': {
            'outer_folds': FOLDS,
            'seeds': SEEDS,
            'estimator': 'fixed regularized logistic regression',
            'logistic_C': LOGISTIC_C,
            'preprocessing': 'training-fold median/mode imputation, numeric standard scaling, one-hot encoding; unseen categories ignored',
            'selection': 'none; fixed before outcome inspection',
            'threshold': 0.5,
            'repeats_are_independent_people': False,
        },
        'integrity': integrity,
        'feature_sets': {name: columns for name, columns in sets.items()},
        'targets': target_results,
        'subgroups': subgroups,
        'source_and_runtime': manifest,
        'interpretation_limits': [
            'Repeated internal cross-validation on the same 303-row cohort is not external validation.',
            'Group ablations describe this fixed logistic pipeline and do not establish causal contribution or production replacement.',
            'Held-out group masking evaluates inference-time imputation after training on complete data; it does not validate missingness generalization.',
            'No clinical or fairness claims follow from these small descriptive analyses.',
            'Feature measurement timing is undocumented; any post-test or workflow leakage requires clinical review.',
        ],
    }
    OUT.mkdir(parents=True)
    ablation.to_csv(OUT / 'ablation_predictions.csv', index=False, float_format='%.17g')
    missingness.to_csv(OUT / 'missingness_predictions.csv', index=False, float_format='%.17g')
    (OUT / 'results.json').write_text(json.dumps(jsonable(results), indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    print(f'Saved {len(ablation)} ablation and {len(missingness)} missingness held-out predictions to {OUT}')
    for target, data in target_results.items():
        for rep in data['repeats']:
            all_auc = rep['ablation']['all_features']['roc_auc']
            core_auc = rep['ablation']['core']['roc_auc']
            print(target, 'repeat', rep['repeat'], 'AUC all/core', round(all_auc, 4), round(core_auc, 4),
                  'core-only missing AUC', round(rep['missingness']['core_only']['roc_auc'], 4))


if __name__ == '__main__':
    with threadpool_limits(limits=1):
        main()
