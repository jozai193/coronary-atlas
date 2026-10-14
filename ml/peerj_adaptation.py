"""Prespecified development on an inspected cohort; never serves app predictions."""
from __future__ import annotations

import os
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import time

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import expit, logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from threadpoolctl import threadpool_limits

from ml.peerj_external import ROOT, RAW, RAW_SHA, FEATURES, map_external, model, metrics, sha, save

OUT = ROOT / 'output/research/peerj_adaptation_v1'
OLD = ROOT / 'output/research/peerj_v1'
PROTOCOL = ROOT / 'docs/peerj_adaptation_protocol.md'
PROTOCOL_SHA = '7c5e03c4963df498707ef19788228b498fcad77c94f2ae54f4b2eaf3857ee55d'
METHODS = ['source', 'constant', 'offset', 'sigmoid', 'local_logistic']


def utc():
    return datetime.now(timezone.utc).isoformat()


def logits(p):
    return logit(np.clip(np.asarray(p, dtype=float), 1e-6, 1-1e-6))


def history():
    paths = [p for folder in (OLD, ROOT/'models', ROOT/'ml/metrics') for p in folder.rglob('*') if p.is_file()]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}


def locked(verification=False):
    assert sha(PROTOCOL) == PROTOCOL_SHA, 'Protocol changed'
    prep = json.loads((OUT/'prepared.json').read_text())
    if not verification:
        assert sha(__file__) == prep['runner_sha256'], 'Fit/evaluate runner changed'
    assert sha(OUT/'runner_snapshot.py') == prep['runner_sha256']
    current, expected = history(), prep['history']
    if verification:
        # Post-fit portability repair: bytecode is generated, never evidence.
        # Preserve the executed snapshot and original inventory unchanged.
        durable = lambda items: {k:v for k,v in items.items() if '__pycache__' not in Path(k).parts and not k.endswith('.pyc')}
        current, expected = durable(current), durable(expected)
    assert current == expected, 'Historical evidence changed'
    assert sha(OUT/'partitions.json') == prep['partitions_sha256']
    return prep


def inputs():
    assert sha(RAW) == RAW_SHA
    raw = pd.read_csv(RAW)
    old = pd.read_csv(OLD/'external_predictions.csv', float_precision='round_trip')
    assert len(raw) == len(old) == 553 and np.array_equal(raw.Group, old.y)
    assert np.array_equal(old.row_index, np.arange(553))
    return map_external(raw), old.y.to_numpy(int), old.logistic.to_numpy(float)


def prepare():
    assert sha(PROTOCOL) == PROTOCOL_SHA
    assert not OUT.exists(), 'Preserve existing development experiment'
    x, y, p = inputs()
    assert list(x.columns) == FEATURES
    partitions = []
    for repeat, seed in enumerate((20261010, 20261011)):
        for fold, (train, test) in enumerate(StratifiedKFold(5, shuffle=True, random_state=seed).split(x, y)):
            ordered = np.random.default_rng(20261010+100*repeat+fold).permutation(train)
            for budget, rows in (('64', ordered[:64]), ('all', ordered)):
                assert set(y[rows]) == {0, 1}, 'Single-class adaptation set; stop without rerandomizing'
                assert not set(rows) & set(test)
                partitions.append(dict(key=f'r{repeat+1}_f{fold}_{budget}', repeat=repeat+1, fold=fold,
                                       budget=budget, train_pool=train.tolist(), adaptation=rows.tolist(), test=test.tolist()))
    OUT.mkdir(parents=True)
    shutil.copyfile(__file__, OUT/'runner_snapshot.py')
    save(OUT/'partitions.json', partitions)
    save(OUT/'prepared.json', dict(utc=utc(), protocol_sha256=PROTOCOL_SHA, runner_sha256=sha(__file__),
                                 raw_sha256=RAW_SHA, partitions_sha256=sha(OUT/'partitions.json'), history=history()))
    print('Prepared 20 fixed adaptation/test partitions; no models fitted.')


def fit_subset(x, labels, source_probabilities, indices):
    """All learned state receives only explicitly selected rows."""
    indices = np.asarray(indices, dtype=int)
    xx = x.iloc[indices]
    yy = np.asarray(labels)[indices]
    zz = logits(np.asarray(source_probabilities)[indices])
    if set(yy) != {0, 1}:
        raise ValueError('Both outcome classes are required; do not rerandomize')
    prevalence = float(yy.mean())
    offset = float(brentq(lambda shift: np.mean(expit(zz+shift))-prevalence, -40, 40, xtol=1e-12))
    sigmoid = LogisticRegression(C=1, max_iter=3000, random_state=20261010).fit(zz.reshape(-1, 1), yy)
    local = model('logistic').fit(xx, yy)
    assert list(local.feature_names_in_) == FEATURES
    return dict(constant=prevalence, offset=offset, sigmoid=sigmoid, local_logistic=local)


def predict(fitted, x, p):
    zz = logits(p)
    return dict(source=np.asarray(p), constant=np.full(len(x), fitted['constant']),
                offset=expit(zz+fitted['offset']), sigmoid=fitted['sigmoid'].predict_proba(zz.reshape(-1, 1))[:, 1],
                local_logistic=fitted['local_logistic'].predict_proba(x)[:, 1])


def parameters(fitted):
    return dict(constant=fitted['constant'], offset=fitted['offset'],
                sigmoid_slope=float(fitted['sigmoid'].coef_[0, 0]),
                sigmoid_intercept=float(fitted['sigmoid'].intercept_[0]),
                local_feature_names=fitted['local_logistic'].named_steps['preprocess'].get_feature_names_out().tolist(),
                local_coefficients=fitted['local_logistic'].named_steps['model'].coef_[0].tolist(),
                local_intercept=float(fitted['local_logistic'].named_steps['model'].intercept_[0]))


def fit():
    prep = locked()
    assert not (OUT/'fitted.joblib').exists(), 'Cannot overwrite fits'
    x, y, p = inputs()
    partitions = json.loads((OUT/'partitions.json').read_text())
    fitted, details = {}, []
    start = time.monotonic()
    with threadpool_limits(limits=1):
        for part in partitions:
            tick = time.monotonic()
            fitted[part['key']] = fit_subset(x, y, p, part['adaptation'])
            details.append(dict(key=part['key'], adaptation_n=len(part['adaptation']),
                                adaptation_positives=int(y[part['adaptation']].sum()),
                                seconds=time.monotonic()-tick, parameters=parameters(fitted[part['key']])))
    joblib.dump(fitted, OUT/'fitted.joblib')
    save(OUT/'fit_manifest.json', dict(status='frozen_before_evaluation', utc=utc(), prepared_sha256=sha(OUT/'prepared.json'),
                                     fitted_sha256=sha(OUT/'fitted.joblib'), fits=60, details=details,
                                     seconds=time.monotonic()-start,
                                     versions={n:importlib.metadata.version(n) for n in ('numpy','pandas','scipy','scikit-learn')}))
    locked()
    print('Frozen 60 fits before scoring. Seconds:', round(time.monotonic()-start, 3))


def extended_metrics(rows, method):
    r = metrics(rows.y, rows[method])
    # This transported source constant is irrelevant to the local comparison.
    r.pop('source_prevalence_constant_brier')
    r['average_precision'] = float(average_precision_score(rows.y, rows[method]))
    r['mean_within_fold_auc'] = float(np.mean([roc_auc_score(group.y, group[method]) for _, group in rows.groupby('fold')]))
    bins = np.minimum((rows[method].to_numpy()*10).astype(int), 9)
    r['reliability'] = [dict(bin=i, n=int(sum(bins==i)), mean_probability=float(rows.loc[bins==i, method].mean()),
                             prevalence=float(rows.loc[bins==i, 'y'].mean())) for i in range(10) if (bins==i).any()]
    return r


def error_interval(rows, method, comparator):
    repeat_differences = []
    for _, part in rows.groupby('repeat'):
        part = part.sort_values('row_index')
        assert part.row_index.tolist() == list(range(553))
        repeat_differences.append((part.y.to_numpy()-part[method].to_numpy())**2 - (part.y.to_numpy()-part[comparator].to_numpy())**2)
    difference = np.mean(repeat_differences, axis=0)
    rng = np.random.default_rng(20261010)
    boot = [float(difference[rng.integers(0, 553, 553)].mean()) for _ in range(1000)]
    return dict(delta_brier=float(difference.mean()), conditional_95_interval=np.quantile(boot, [.025, .975]).tolist(), unique_people=553, draws=1000)


def summarize(rows):
    output = {}
    old = pd.read_csv(OLD/'external_predictions.csv', float_precision='round_trip').set_index('row_index')
    for budget, table in rows.groupby('budget', sort=False):
        repeats = {str(int(rep)): {m:extended_metrics(part, m) for m in METHODS} for rep, part in table.groupby('repeat')}
        mean = {m:{key:float(np.mean([r[m][key] for r in repeats.values()]))
                   for key in ('auc','mean_within_fold_auc','brier','log_loss','average_precision','mean_probability','accuracy','sensitivity','specificity')}
                for m in METHODS}
        comparisons = {m:{ref:error_interval(table,m,ref) for ref in ('source','constant')}
                       for m in ('offset','sigmoid','local_logistic')}
        screens = {m:bool(mean['source']['brier']-mean[m]['brier'] >= .01 and mean['constant']['brier']-mean[m]['brier'] >= .005
                          and mean[m]['mean_within_fold_auc'] >= mean['source']['mean_within_fold_auc']-.01)
                   for m in comparisons}
        subgroups = {}
        for name, mask in {'female':old.female, 'male':~old.female, 'under_50':old.age_under_50, 'age_50_plus':~old.age_under_50}.items():
            group_indices = old.index[mask]
            yy = old.loc[group_indices,'y']
            eligible = len(yy)>=30 and min(int(yy.sum()),len(yy)-int(yy.sum()))>=10
            subgroups[name] = dict(n=len(yy), positives=int(yy.sum()), eligible=eligible,
                                    repeats={str(int(rep)):{m:metrics(part.loc[part.row_index.isin(group_indices),'y'],
                                                                     part.loc[part.row_index.isin(group_indices),m]) for m in METHODS}
                                             for rep,part in table.groupby('repeat')} if eligible else {})
        output[str(budget)] = dict(repeats=repeats, mean=mean, comparisons=comparisons, followup_screen=screens, subgroups=subgroups)
    return dict(scope='retrospective development on already inspected China cohort; not independent validation or app predictions',
                unique_people=553, repeats=2, primary_arm='64/sigmoid', budgets=output)


def evaluate():
    locked()
    assert not (OUT/'results.json').exists(), 'Preserve results; use verify'
    fit_manifest = json.loads((OUT/'fit_manifest.json').read_text())
    assert sha(OUT/'fitted.joblib') == fit_manifest['fitted_sha256']
    x, y, p = inputs()
    fitted = joblib.load(OUT/'fitted.joblib')
    chunks = []
    for part in json.loads((OUT/'partitions.json').read_text()):
        test = part['test']
        chunk = pd.DataFrame(dict(row_index=test, repeat=part['repeat'], fold=part['fold'], budget=part['budget'], y=y[test]))
        for method, values in predict(fitted[part['key']], x.iloc[test], p[test]).items():
            chunk[method] = values
        chunks.append(chunk)
    rows = pd.concat(chunks, ignore_index=True).sort_values(['budget','repeat','row_index'])
    rows.to_csv(OUT/'predictions.csv', index=False, float_format='%.17g', lineterminator='\n')
    result = summarize(rows)
    save(OUT/'results.json', result)
    save(OUT/'evidence_manifest.json', dict(utc=utc(), files={name:sha(OUT/name) for name in
         ('runner_snapshot.py','prepared.json','partitions.json','fitted.joblib','fit_manifest.json','predictions.csv','results.json')}))
    locked()
    print(json.dumps({b:dict(mean=v['mean'], screen=v['followup_screen']) for b,v in result['budgets'].items()}, indent=2))


def assert_close(left, right):
    if isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left: assert_close(left[key],right[key])
    elif isinstance(left, list):
        assert len(left) == len(right)
        for a,b in zip(left,right): assert_close(a,b)
    elif isinstance(left, float):
        assert np.isclose(left,right,rtol=0,atol=1e-12), (left,right)
    else:
        assert left == right, (left,right)


def verify():
    prep = locked(verification=True)
    evidence = json.loads((OUT/'evidence_manifest.json').read_text())
    fit_manifest = json.loads((OUT/'fit_manifest.json').read_text())
    for name,digest in evidence['files'].items(): assert sha(OUT/name)==digest, name
    assert fit_manifest['prepared_sha256'] == sha(OUT/'prepared.json')
    assert fit_manifest['fitted_sha256'] == sha(OUT/'fitted.joblib')
    assert prep['utc'] < fit_manifest['utc'] < evidence['utc']
    rows = pd.read_csv(OUT/'predictions.csv', dtype={'budget':str}, float_precision='round_trip')
    old = pd.read_csv(OLD/'external_predictions.csv',float_precision='round_trip')
    assert len(rows) == 553*4
    assert set(rows.columns) == {'row_index','repeat','fold','budget','y',*METHODS}
    fitted = joblib.load(OUT/'fitted.joblib')
    partitions = json.loads((OUT/'partitions.json').read_text())
    assert len(partitions) == 20 and len(fitted) == 20 and fit_manifest['fits'] == 60
    expected_splits = {}
    for repeat,seed in enumerate((20261010,20261011),start=1):
        for fold,(train,test) in enumerate(StratifiedKFold(5,shuffle=True,random_state=seed).split(old,old.y)):
            ordered=np.random.default_rng(20261010+100*(repeat-1)+fold).permutation(train)
            expected_splits[(repeat,fold)] = train.tolist(),test.tolist(),ordered.tolist()
    raw_inputs = inputs() if RAW.exists() else None
    for part in partitions:
        train,test,ordered = expected_splits[(part['repeat'],part['fold'])]
        assert part['train_pool']==train and part['test']==test
        assert part['adaptation'] == (ordered[:64] if part['budget']=='64' else ordered)
        assert not set(part['adaptation']) & set(test)
        saved = rows[(rows.repeat==part['repeat']) & (rows.fold==part['fold']) & (rows.budget==part['budget'])].sort_values('row_index')
        assert saved.row_index.tolist() == sorted(test)
        assert np.array_equal(saved.y,old.iloc[sorted(test)].y)
        assert np.array_equal(saved.source,old.iloc[sorted(test)].logistic)
        detail=next(d for d in fit_manifest['details'] if d['key']==part['key'])
        assert_close(parameters(fitted[part['key']]),detail['parameters'])
        assert fitted[part['key']]['constant'] == float(old.iloc[part['adaptation']].y.mean())
        if raw_inputs is not None:
            x,y,p = raw_inputs
            predicted=predict(fitted[part['key']],x.iloc[sorted(test)],p[sorted(test)])
            for method in METHODS:
                assert np.allclose(predicted[method],saved[method],rtol=0,atol=1e-12)
    assert_close(summarize(rows),json.loads((OUT/'results.json').read_text()))
    print('Verified 20 disjoint fixed subsets, 60 fit parameter records, 2212 predictions, all metrics/intervals and unchanged historical artifacts.')
    print('Raw pipeline prediction reproduction:', 'passed' if raw_inputs is not None else 'not run; raw external data excluded')


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['prepare','fit','evaluate','verify'])
    globals()[parser.parse_args().stage]()
