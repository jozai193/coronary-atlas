"""Isolated, staged development on previously inspected CONFIRM data; never app inference."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.schema import ROOT, digest, read_data, write_json
from ml.evaluate import metrics

OUT = ROOT/'ml/experiments/confirm_development_v1'
OLD = ROOT/'ml/experiments/confirm_external_v1'
RAW = ROOT/'data/external_audit/v3/CONFIRM_ST_LOCKED2.xlsx'
PROTOCOL = ROOT/'docs/confirm_development_protocol.md'
NUM = ['age', 'bmi', 'ldl', 'hdl']
CAT = ['sex', 'htn', 'dm', 'chol', 'famhx', 'smokecurrent', 'smokepast',
       'chest_pain', 'typicality', 'exertion', 'sob']
LABELS = dict(cad='stenosis_50', lad='lad_50', lcx='lcx_50', rca='rca_50')
ARMS = ['four_complete', 'clinical_complete', 'clinical_available']
SOURCE_FEATURES = ['Age', 'BMI', 'LDL', 'HDL']
SEED = 20261008


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify_history():
    for name, sha in read_json(OLD/'evidence_manifest.json').items():
        assert digest(OLD/name) == sha, name
    for name, sha in read_json(ROOT/'data/external_audit/v3/frozen_models.json')['sha256'].items():
        assert digest(ROOT/name) == sha, name


def split_role(identifier):
    # Excel numeric IDs are canonicalized to avoid float-string instability.
    value = str(int(identifier)) if isinstance(identifier, (int, float, np.number)) and float(identifier).is_integer() else str(identifier)
    fraction = int(hashlib.sha256(('confirm-development-v1:'+value).encode()).hexdigest()[:8], 16)/2**32
    return 'train' if fraction < .6 else 'calibration' if fraction < .8 else 'test'


def load_inputs():
    cols = ['confirm_id', *NUM, *CAT, 'past_mi', 'past_pci', 'past_cabg']
    d = pd.read_excel(RAW, usecols=cols)
    assert d.confirm_id.notna().all() and d.confirm_id.is_unique
    x = d[NUM+CAT].apply(pd.to_numeric, errors='raise')
    for c in CAT:
        allowed = {0, 1, 2, 3} if c == 'typicality' else {0, 1}
        assert set(x[c].dropna().unique()) <= allowed, c
    available = x.age.between(30, 100) & d[['past_mi', 'past_pci', 'past_cabg']].eq(0).all(axis=1)
    for c, (low, high) in zip(NUM[1:], [(10, 80), (10, 500), (5, 200)]):
        available &= x[c].isna() | x[c].between(low, high)
    source_keys = set(map(tuple, read_data()[SOURCE_FEATURES].to_numpy()))
    available &= ~x[NUM].apply(lambda r: tuple(r) in source_keys, axis=1)
    complete = available & x[NUM].notna().all(axis=1)
    return d, x, available, complete


def prepare():
    if OUT.exists():
        raise RuntimeError('Development directory already exists; do not overwrite.')
    verify_history()
    d, x, available, complete = load_inputs()
    OUT.mkdir(parents=True)
    split = pd.DataFrame({'workbook_row_index': d.index[available],
                          'partition': d.loc[available, 'confirm_id'].map(split_role),
                          'complete': complete.loc[available].astype(int)})
    split.to_csv(OUT/'partitions.csv', index=False)
    write_json(OUT/'prepared.json', {'role': 'Post-external-result development, not independent validation',
        'runner_sha256': digest(Path(__file__)), 'protocol_sha256': digest(PROTOCOL),
        'raw_sha256': digest(RAW), 'historical_manifest_sha256': digest(OLD/'evidence_manifest.json'),
        'partition_sha256': digest(OUT/'partitions.csv'), 'raw_rows': len(d),
        'eligible_available': int(available.sum()), 'eligible_complete': int(complete.sum()),
        'partition_counts': split.partition.value_counts().to_dict(),
        'features': {'numeric': NUM, 'categorical_opaque_codes': CAT},
        'missing_numeric_eligible': x.loc[available, NUM].isna().sum().to_dict()})
    print('Prepared inputs and label-independent partitions:', len(split), flush=True)


def verify_prepared():
    verify_history()
    m = read_json(OUT/'prepared.json')
    for p, key in [(Path(__file__), 'runner_sha256'), (PROTOCOL, 'protocol_sha256'),
                   (RAW, 'raw_sha256'), (OLD/'evidence_manifest.json', 'historical_manifest_sha256'),
                   (OUT/'partitions.csv', 'partition_sha256')]:
        assert digest(p) == m[key], str(p)
    return pd.read_csv(OUT/'partitions.csv').set_index('workbook_row_index')


def candidates(clinical):
    result = {}
    for name in ['logistic', 'splines', 'histgb', 'forest']:
        steps = [SimpleImputer(strategy='median', add_indicator=True)]
        if name == 'splines':
            steps.append(SplineTransformer(n_knots=4, degree=3, include_bias=False))
        steps.append(StandardScaler())
        transforms = [('numeric', make_pipeline(*steps), NUM)]
        if clinical:
            transforms.append(('categorical', make_pipeline(
                SimpleImputer(strategy='constant', fill_value=-1),
                OneHotEncoder(handle_unknown='ignore', sparse_output=False)), CAT))
        prep = ColumnTransformer(transforms)
        learner = (LogisticRegression(C=1, max_iter=3000) if name in ['logistic', 'splines'] else
            HistGradientBoostingClassifier(max_iter=150, learning_rate=.05, max_leaf_nodes=7,
                l2_regularization=10, min_samples_leaf=30, early_stopping=False, random_state=SEED) if name == 'histgb' else
            RandomForestClassifier(n_estimators=150, min_samples_leaf=20, max_features=1.0,
                n_jobs=2, random_state=SEED))
        result[name] = make_pipeline(prep, learner)
    return result


def logits(p):
    p = np.clip(p, 1e-6, 1-1e-6)
    return np.log(p/(1-p)).reshape(-1, 1)


def calibrator(p, y):
    return LogisticRegression(C=1e6, max_iter=3000).fit(logits(p), y)


def cutoff90(y, p):
    positive = np.sort(np.asarray(p)[np.asarray(y) == 1])
    if not len(positive):
        raise ValueError('No positive calibration cases.')
    # Largest positive score retaining at least ceil(.9 * positives) positives.
    return float(positive[len(positive)-int(np.ceil(.9*len(positive)))])


def fit():
    if (OUT/'fit_manifest.json').exists() or list(OUT.glob('*.joblib')):
        raise RuntimeError('Fit artifacts exist; preserve them.')
    split = verify_prepared()
    _, x, _, _ = load_inputs()
    # Test outcomes are explicitly excluded from the development-frame below.
    outcomes = pd.read_excel(RAW, usecols=list(LABELS.values()))
    development = outcomes.loc[split.index[split.partition != 'test']].copy()
    del outcomes
    manifest = {'prepared_sha256': digest(OUT/'prepared.json'), 'experiments': {}}
    for arm in ARMS:
        frame = split if arm == 'clinical_available' else split.loc[split.complete == 1]
        for target, label in LABELS.items():
            ix = {role: frame.index[frame.partition == role].intersection(development.index[development[label].notna()])
                  for role in ['train', 'calibration']}
            y = {role: development.loc[rows, label].to_numpy(dtype=int) for role, rows in ix.items()}
            assert all(set(v) == {0, 1} for v in y.values())
            cv = StratifiedKFold(3, shuffle=True, random_state=SEED)
            families = candidates(arm != 'four_complete')
            scores = {name: (-cross_val_score(model, x.loc[ix['train']], y['train'], cv=cv,
                scoring='neg_brier_score', n_jobs=1)).tolist() for name, model in families.items()}
            chosen = min(scores, key=lambda name: np.mean(scores[name]))
            selected = clone(families[chosen]).fit(x.loc[ix['train']], y['train'])
            pc = selected.predict_proba(x.loc[ix['calibration']])[:, 1]
            cal = calibrator(pc, y['calibration'])
            bundle = {'selected': selected, 'selected_calibrator': cal,
                      'constant': float(y['train'].mean())}
            calibration_probs = {'selected_raw': pc,
                'selected_calibrated': cal.predict_proba(logits(pc))[:, 1],
                'constant': np.full(len(pc), bundle['constant'])}
            if arm != 'clinical_available':
                source = joblib.load(OLD/f'{target}.joblib')
                sx = x.loc[ix['calibration'], NUM].set_axis(SOURCE_FEATURES, axis=1)
                ps = source.predict_proba(sx)[:, 1]
                sc = calibrator(ps, y['calibration'])
                bundle['source_calibrator'] = sc
                calibration_probs.update(source_raw=ps, source_calibrated=sc.predict_proba(logits(ps))[:, 1])
            thresholds = {name: cutoff90(y['calibration'], p) for name, p in calibration_probs.items()}
            key = f'{arm}_{target}'
            joblib.dump(bundle, OUT/f'{key}.joblib')
            pd.DataFrame({'workbook_row_index': ix['calibration'], 'observed': y['calibration'],
                          **calibration_probs}).to_csv(OUT/f'{key}_calibration.csv', index=False)
            manifest['experiments'][key] = {'arm': arm, 'target': target, 'selected_family': chosen,
                'cv_brier': scores, 'train_rows': ix['train'].tolist(),
                'calibration_rows': ix['calibration'].tolist(), 'cutoffs_90': thresholds,
                'artifact_sha256': digest(OUT/f'{key}.joblib'),
                'calibration_sha256': digest(OUT/f'{key}_calibration.csv')}
            print(key, chosen, 'train/cal', len(ix['train']), len(ix['calibration']), flush=True)
    verify_history()
    write_json(OUT/'fit_manifest.json', manifest)


def confusion(y, p, threshold):
    y = np.asarray(y); pred = np.asarray(p) >= threshold
    tn = int(((y == 0) & ~pred).sum()); fp = int(((y == 0) & pred).sum())
    fn = int(((y == 1) & ~pred).sum()); tp = int(((y == 1) & pred).sum())
    return {'threshold': threshold, 'sensitivity': tp/(tp+fn), 'specificity': tn/(tn+fp),
            'false_positives': fp, 'missed_cases': fn, 'true_positives': tp, 'true_negatives': tn}


def paired_intervals(y, first, second):
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(500):
        ix = rng.integers(len(y), size=len(y)); yy = y[ix]
        if len(np.unique(yy)) == 2:
            a, b = first[ix], second[ix]
            diffs.append([roc_auc_score(yy, a)-roc_auc_score(yy, b),
                          brier_score_loss(yy, a)-brier_score_loss(yy, b)])
    q = np.quantile(diffs, [.025, .975], axis=0)
    return {'auc_difference_95': q[:, 0].tolist(), 'brier_difference_95': q[:, 1].tolist(),
            'resamples': len(diffs)}


def summarize(y, p, threshold):
    bins = []
    for indices in np.array_split(np.argsort(p, kind='stable'), 5):
        bins.append({'n': len(indices), 'predicted': float(p[indices].mean()),
                     'observed': float(y[indices].mean()), 'min': float(p[indices].min()),
                     'max': float(p[indices].max())})
    return {**metrics(y, p), 'average_precision': float(average_precision_score(y, p)),
        'mean_probability': float(p.mean()), 'prevalence': float(y.mean()),
        'cutoff90': confusion(y, p, threshold), 'reliability_equal_count_bins': bins}


def evaluate():
    if (OUT/'results.json').exists() or list(OUT.glob('*_test.csv')):
        raise RuntimeError('Evaluation outputs exist; no automatic retesting.')
    split = verify_prepared()
    manifest = read_json(OUT/'fit_manifest.json')
    assert digest(OUT/'prepared.json') == manifest['prepared_sha256']
    _, x, _, _ = load_inputs()
    outcomes = pd.read_excel(RAW, usecols=list(LABELS.values()))
    result = {'role': 'Internal development test on previously inspected CONFIRM; not independent validation',
              'fit_manifest_sha256': digest(OUT/'fit_manifest.json'), 'experiments': {}, 'matched_feature_comparison': {}}
    for key, info in manifest['experiments'].items():
        assert digest(OUT/f'{key}.joblib') == info['artifact_sha256']
        assert digest(OUT/f'{key}_calibration.csv') == info['calibration_sha256']
        bundle = joblib.load(OUT/f'{key}.joblib')
        arm, target = info['arm'], info['target']
        frame = split if arm == 'clinical_available' else split.loc[split.complete == 1]
        ix = frame.index[frame.partition == 'test'].intersection(outcomes.index[outcomes[LABELS[target]].notna()])
        assert not (set(ix) & set(info['train_rows']+info['calibration_rows']))
        y = outcomes.loc[ix, LABELS[target]].to_numpy(dtype=int)
        assert set(y) == {0, 1}
        p = bundle['selected'].predict_proba(x.loc[ix])[:, 1]
        probs = {'selected_raw': p, 'selected_calibrated': bundle['selected_calibrator'].predict_proba(logits(p))[:, 1],
                 'constant': np.full(len(ix), bundle['constant'])}
        if arm != 'clinical_available':
            sx = x.loc[ix, NUM].set_axis(SOURCE_FEATURES, axis=1)
            ps = joblib.load(OLD/f'{target}.joblib').predict_proba(sx)[:, 1]
            probs.update(source_raw=ps, source_calibrated=bundle['source_calibrator'].predict_proba(logits(ps))[:, 1])
        groups = {'age_under60': x.loc[ix, 'age'].to_numpy() < 60,
                  'age_60plus': x.loc[ix, 'age'].to_numpy() >= 60,
                  'sex_code0': x.loc[ix, 'sex'].eq(0).to_numpy(),
                  'sex_code1': x.loc[ix, 'sex'].eq(1).to_numpy(),
                  'numeric_missing': x.loc[ix, NUM].isna().any(axis=1).to_numpy(),
                  'numeric_complete': x.loc[ix, NUM].notna().all(axis=1).to_numpy()}
        subgroup = {}
        pc = probs['selected_calibrated']
        for name, mask in groups.items():
            subgroup[name] = {'rows': int(mask.sum()), 'positives': int(y[mask].sum())}
            if mask.sum() >= 100 and len(np.unique(y[mask])) == 2:
                subgroup[name].update(summarize(y[mask], pc[mask], info['cutoffs_90']['selected_calibrated']))
            else:
                subgroup[name]['suppressed'] = 'Fewer than 100 rows or lacks both classes.'
        comparison = 'source_raw' if 'source_raw' in probs else 'constant'
        result['experiments'][key] = {'rows': len(ix), 'positives': int(y.sum()), 'selected_family': info['selected_family'],
            'models': {name: summarize(y, pp, info['cutoffs_90'][name]) for name, pp in probs.items()},
            'paired_selected_minus_'+comparison: paired_intervals(y, pc, probs[comparison]),
            'subgroups_selected_calibrated': subgroup}
        pd.DataFrame({'workbook_row_index': ix, 'observed': y, **probs}).to_csv(OUT/f'{key}_test.csv', index=False)
        print(key, 'AUC', round(roc_auc_score(y, pc), 4), 'Brier', round(brier_score_loss(y, pc), 4), flush=True)
    for target in LABELS:
        a = pd.read_csv(OUT/f'clinical_complete_{target}_test.csv', float_precision='round_trip')
        b = pd.read_csv(OUT/f'four_complete_{target}_test.csv', float_precision='round_trip')
        assert a.workbook_row_index.equals(b.workbook_row_index) and a.observed.equals(b.observed)
        result['matched_feature_comparison'][target] = paired_intervals(a.observed.to_numpy(),
            a.selected_calibrated.to_numpy(), b.selected_calibrated.to_numpy())
    verify_history()
    result['historical_and_app_hashes_unchanged'] = True
    write_json(OUT/'results.json', result)
    write_json(OUT/'evidence_manifest.json', {p.name: digest(p) for p in sorted(OUT.iterdir()) if p.is_file()})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'fit', 'evaluate'])
    with threadpool_limits(limits=2):
        globals()[parser.parse_args().stage]()
