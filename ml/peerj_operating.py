"""Frozen three-role development experiment; never used by prediction serving."""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import shutil
import time
import joblib
import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import StratifiedKFold
from threadpoolctl import threadpool_limits
from ml.peerj_external import ROOT, RAW, RAW_SHA, FEATURES, model, map_external, metrics, sha, save

OUT = ROOT/'output/research/peerj_operating_v1'
OLD = ROOT/'output/research/peerj_v1'
PROTOCOL = ROOT/'docs/peerj_operating_protocol.md'
METHODS = ['source', 'source_sigmoid', 'local', 'local_sigmoid']
POINTS = {'fixed_50': None, 'target_80': .8, 'target_90': .9, 'target_95': .95}


def utc():
    return datetime.now(timezone.utc).isoformat()


def logits(p):
    return logit(np.clip(np.asarray(p, dtype=float), 1e-6, 1-1e-6)).reshape(-1, 1)


def cutoff(y, p, target):
    """Maximum calibration-positive cutoff meeting empirical recall, ties included."""
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    if set(y) != {0, 1} or len(y) != len(p) or not 0 < target <= 1:
        raise ValueError('Both classes, matching scores and target in (0,1] required')
    if not np.isfinite(p).all() or not ((p >= 0) & (p <= 1)).all():
        raise ValueError('Scores must be finite probabilities')
    positives = np.sort(p[y == 1])[::-1]
    return float(positives[int(np.ceil(target*len(positives)))-1])


def build_parts(y):
    parts = []
    for rep, seed in enumerate((20261010, 20261011)):
        for fold, (pool, test) in enumerate(StratifiedKFold(5, shuffle=True, random_state=seed).split(np.zeros(len(y)), y)):
            ordered = np.random.default_rng(20261012+100*rep+fold).permutation(pool)
            cal, train = ordered[:111], ordered[111:]
            assert all(set(np.asarray(y)[idx]) == {0, 1} for idx in (train, cal, test))
            parts.append(dict(key=f'r{rep+1}_f{fold}', repeat=rep+1, fold=fold,
                              train=train.tolist(), calibration=cal.tolist(), test=test.tolist()))
    return parts


def history():
    folders = [ROOT/'models', ROOT/'ml/metrics', OLD, ROOT/'output/research/peerj_adaptation_v1']
    paths = [p for folder in folders for p in folder.rglob('*')
             if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    paths += [ROOT/'ml/peerj_external.py', ROOT/'ml/schema.py', ROOT/'data/raw/extention of Z-Alizadeh sani dataset.xlsx']
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}


def inputs():
    assert sha(RAW) == RAW_SHA
    raw = pd.read_csv(RAW)
    prior = pd.read_csv(OLD/'external_predictions.csv', float_precision='round_trip')
    assert len(raw) == 553 and np.array_equal(raw.Group, prior.y)
    assert prior.row_index.tolist() == list(range(553))
    return map_external(raw), prior.y.to_numpy(int), prior.logistic.to_numpy(float)


def locked():
    prep = json.loads((OUT/'prepared.json').read_text())
    assert sha(PROTOCOL) == prep['protocol_sha256']
    assert sha(__file__) == sha(OUT/'runner_snapshot.py') == prep['runner_sha256']
    assert sha(OUT/'partitions.json') == prep['partitions_sha256']
    assert history() == prep['history'], 'Historical evidence changed'
    return prep


def prepare():
    assert not OUT.exists(), 'Do not overwrite a frozen experiment'
    x, y, p = inputs()
    assert list(x.columns) == FEATURES
    OUT.mkdir(parents=True)
    shutil.copyfile(__file__, OUT/'runner_snapshot.py')
    save(OUT/'partitions.json', build_parts(y))
    save(OUT/'prepared.json', dict(utc=utc(), protocol_sha256=sha(PROTOCOL), runner_sha256=sha(__file__),
                                 raw_sha256=RAW_SHA, partitions_sha256=sha(OUT/'partitions.json'), history=history()))
    print('Prepared ten disjoint training/calibration/evaluation partitions; no new fits.')


def fit_roles(x_train, y_train, x_cal, y_cal, source_cal):
    """Evaluation data are absent from this interface."""
    if any(set(y) != {0, 1} for y in (y_train, y_cal)):
        raise ValueError('Both classes required in each fitting role')
    local = model('logistic').fit(x_train, y_train)
    probs = dict(source=np.asarray(source_cal), local=local.predict_proba(x_cal)[:, 1])
    fitted = dict(local=local, constant=float(np.mean(y_train)))
    for base in ('source', 'local'):
        est = LogisticRegression(C=1, max_iter=3000, random_state=20261010).fit(logits(probs[base]), y_cal)
        fitted[base+'_sigmoid'] = est
        probs[base+'_sigmoid'] = est.predict_proba(logits(probs[base]))[:, 1]
    fitted['cutoffs'] = {m:{name:.5 if target is None else cutoff(y_cal, probs[m], target)
                            for name, target in POINTS.items()} for m in METHODS}
    return fitted, probs


def fit_partition(x, y, source, part):
    t, c = part['train'], part['calibration']
    assert not set(t)&set(c) and not (set(t)|set(c))&set(part['test'])
    return fit_roles(x.iloc[t], y[t], x.iloc[c], y[c], source[c])


def predict(fitted, x, source):
    probs = dict(source=np.asarray(source), local=fitted['local'].predict_proba(x)[:, 1],
                 constant=np.full(len(x), fitted['constant']))
    for base in ('source', 'local'):
        probs[base+'_sigmoid'] = fitted[base+'_sigmoid'].predict_proba(logits(probs[base]))[:, 1]
    return probs


def fit():
    locked()
    assert not (OUT/'fitted.joblib').exists(), 'Cannot overwrite fits'
    x, y, p = inputs()
    parts = json.loads((OUT/'partitions.json').read_text())
    fitted, details, tables = {}, [], []
    tick = time.monotonic()
    with threadpool_limits(limits=1):
        for part in parts:
            f, prob = fit_partition(x, y, p, part)
            fitted[part['key']] = f
            c = part['calibration']
            tables.append(pd.DataFrame(dict(key=part['key'], row_index=c, y=y[c], **prob)))
            details.append(dict(key=part['key'], train_n=len(part['train']), calibration_n=len(c),
                                train_positives=int(y[part['train']].sum()), calibration_positives=int(y[c].sum()),
                                cutoffs=f['cutoffs'], sigmoid_parameters={m:dict(slope=float(f[m].coef_[0, 0]),
                                intercept=float(f[m].intercept_[0])) for m in ('source_sigmoid', 'local_sigmoid')}))
    joblib.dump(fitted, OUT/'fitted.joblib')
    pd.concat(tables, ignore_index=True).to_csv(OUT/'calibration_predictions.csv', index=False, float_format='%.17g', lineterminator='\n')
    save(OUT/'fit_manifest.json', dict(status='frozen_before_evaluation', utc=utc(), prepared_sha256=sha(OUT/'prepared.json'),
         files={n:sha(OUT/n) for n in ('fitted.joblib','calibration_predictions.csv')}, details=details, fits=30,
         seconds=time.monotonic()-tick, versions={n:importlib.metadata.version(n) for n in ('numpy','pandas','scipy','scikit-learn')}))
    locked()
    print('Frozen 10 local models, 20 calibrators and all cutoffs before evaluation.')


def wilson(k, n):
    z = 1.959963984540054
    p = k/n; den = 1+z*z/n
    center = (p+z*z/(2*n))/den
    half = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [float(max(0, center-half)), float(min(1, center+half))]


def decision_metrics(y, decision):
    y, d = np.asarray(y, dtype=int), np.asarray(decision, dtype=bool)
    tp = int(np.sum((y == 1)&d)); fn = int(np.sum((y == 1)&~d))
    fp = int(np.sum((y == 0)&d)); tn = int(np.sum((y == 0)&~d))
    return dict(confusion=dict(tn=tn, fp=fp, fn=fn, tp=tp), sensitivity=tp/(tp+fn), specificity=tn/(tn+fp),
                precision=tp/(tp+fp) if tp+fp else None, negative_predictive_value=tn/(tn+fn) if tn+fn else None,
                fraction_flagged=(tp+fp)/len(y), sensitivity_wilson95=wilson(tp,tp+fn), specificity_wilson95=wilson(tn,tn+fp))


def probability_metrics(rows, m):
    result = metrics(rows.y, rows[m])
    result.pop('source_prevalence_constant_brier')
    result['mean_within_fold_auc'] = float(np.mean([roc_auc_score(g.y, g[m]) for _,g in rows.groupby('fold')]))
    result['average_precision'] = float(average_precision_score(rows.y, rows[m]))
    bins = np.minimum((rows[m].to_numpy()*10).astype(int),9)
    result['reliability'] = [dict(bin=i, n=int(sum(bins==i)), mean_probability=float(rows.loc[bins==i,m].mean()),
                                 prevalence=float(rows.loc[bins==i,'y'].mean())) for i in range(10) if sum(bins==i)]
    return result


def paired_interval(rows, method, ref, metric):
    contributions = []
    for _,r in rows.groupby('repeat'):
        r = r.sort_values('row_index')
        assert r.row_index.tolist() == list(range(553))
        if metric == 'brier':
            a = (r.y.to_numpy()-r[method].to_numpy())**2 - (r.y.to_numpy()-r[ref].to_numpy())**2
        else:
            mask = r.y.to_numpy() == (1 if metric == 'sensitivity' else 0)
            a = r[method].to_numpy(int)[mask]-r[ref].to_numpy(int)[mask]
            if metric == 'specificity': a = -a
        contributions.append(a)
    d = np.mean(contributions, axis=0)
    rng = np.random.default_rng(20261012)
    draws = [float(d[rng.integers(0,len(d),len(d))].mean()) for _ in range(1000)]
    return dict(difference=float(d.mean()), conditional_95_interval=np.quantile(draws,[.025,.975]).tolist(),
                unique_people=len(d), bootstrap_draws=1000)


def summarize(rows):
    repeats = {}
    for rep, table in rows.groupby('repeat'):
        probs = {m:probability_metrics(table,m) for m in METHODS+['constant']}
        operating = {m:{} for m in METHODS}
        for m in METHODS:
            for point, target in POINTS.items():
                col=f'{m}__{point}'
                r=decision_metrics(table.y,table[col])
                r['folds']=[dict(fold=int(fold), **decision_metrics(g.y,g[col])) for fold,g in table.groupby('fold')]
                r['folds_below_calibration_target']=None if target is None else sum(f['sensitivity']<target for f in r['folds'])
                operating[m][point]=r
        repeats[str(rep)] = dict(probabilities=probs, operating=operating)
    mean_probs = {m:{k:float(np.mean([r['probabilities'][m][k] for r in repeats.values()]))
                    for k in ('brier','auc','mean_within_fold_auc','log_loss','mean_probability','average_precision')}
                  for m in METHODS+['constant']}
    mean_operating = {m:{point:{k:float(np.mean([r['operating'][m][point][k] for r in repeats.values()]))
                                for k in ('sensitivity','specificity','fraction_flagged')} for point in POINTS} for m in METHODS}
    primary = dict(probability={ref:paired_interval(rows,'local_sigmoid',ref,'brier') for ref in ('source','constant','local')},
                   operating={k:paired_interval(rows,'local_sigmoid__target_90','source__target_90',k)
                              for k in ('sensitivity','specificity')})
    return dict(scope='Retrospective development; already inspected 553-person cohort; separate 14-input CAD task.',
                reviewer_guidance='None. All sensitivity targets are exploratory and unapproved.', unique_people=553,
                repeats=repeats, mean_probabilities=mean_probs, mean_operating=mean_operating, primary=primary)


def evaluate():
    locked()
    assert not (OUT/'results.json').exists(), 'Cannot overwrite results'
    manifest=json.loads((OUT/'fit_manifest.json').read_text())
    for name,digest in manifest['files'].items(): assert sha(OUT/name)==digest
    assert sha(OUT/'prepared.json')==manifest['prepared_sha256']
    x,y,p=inputs(); fitted=joblib.load(OUT/'fitted.joblib')
    chunks=[]
    for part in json.loads((OUT/'partitions.json').read_text()):
        idx=part['test']; f=fitted[part['key']]
        prob=predict(f,x.iloc[idx],p[idx])
        table=pd.DataFrame(dict(row_index=idx,repeat=part['repeat'],fold=part['fold'],y=y[idx],**prob))
        for m in METHODS:
            for point,t in f['cutoffs'][m].items(): table[f'{m}__{point}']=(prob[m]>=t).astype(int)
        chunks.append(table)
    rows=pd.concat(chunks,ignore_index=True).sort_values(['repeat','row_index'])
    rows.to_csv(OUT/'predictions.csv',index=False,float_format='%.17g',lineterminator='\n')
    save(OUT/'results.json',summarize(rows))
    files=['runner_snapshot.py','prepared.json','partitions.json','fitted.joblib','calibration_predictions.csv',
           'fit_manifest.json','predictions.csv','results.json']
    save(OUT/'evidence_manifest.json',dict(utc=utc(),files={n:sha(OUT/n) for n in files}))
    locked()
    print('All arms and cutoffs evaluated and frozen; no app model promotion.')


def close(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a: close(a[k],b[k])
    elif isinstance(a,list):
        assert len(a)==len(b)
        for x,y in zip(a,b): close(x,y)
    elif isinstance(a,float): assert np.isclose(a,b,atol=1e-12,rtol=0),(a,b)
    else: assert a==b,(a,b)


def verify():
    locked()
    evidence=json.loads((OUT/'evidence_manifest.json').read_text())
    for name,digest in evidence['files'].items(): assert sha(OUT/name)==digest
    rows=pd.read_csv(OUT/'predictions.csv',float_precision='round_trip')
    cal=pd.read_csv(OUT/'calibration_predictions.csv',float_precision='round_trip')
    prior=pd.read_csv(OLD/'external_predictions.csv',float_precision='round_trip')
    parts=json.loads((OUT/'partitions.json').read_text())
    assert parts==build_parts(prior.y.to_numpy())
    assert len(rows)==1106 and len(cal)==1110
    fitted=joblib.load(OUT/'fitted.joblib')
    for part in parts:
        t,c,e=map(set,(part['train'],part['calibration'],part['test']))
        assert not t&c and not t&e and not c&e and t|c|e==set(range(553))
        group=rows[(rows.repeat==part['repeat'])&(rows.fold==part['fold'])]
        cc=cal[cal.key==part['key']]; f=fitted[part['key']]
        assert set(group.row_index)==e and cc.row_index.tolist()==part['calibration']
        np.testing.assert_array_equal(group.y,prior.y.iloc[group.row_index])
        np.testing.assert_array_equal(cc.y,prior.y.iloc[cc.row_index])
        np.testing.assert_array_equal(group.source,prior.logistic.iloc[group.row_index])
        for m in METHODS:
            for name,target in POINTS.items():
                threshold=.5 if target is None else cutoff(cc.y,cc[m],target)
                assert threshold==f['cutoffs'][m][name]
                np.testing.assert_array_equal(group[f'{m}__{name}'],group[m]>=threshold)
        if RAW.exists():
            x,y,p=inputs()
            for indices,actual in ((group.row_index.to_numpy(),group),(cc.row_index.to_numpy(),cc)):
                predicted=predict(f,x.iloc[indices],p[indices])
                for m in METHODS: np.testing.assert_allclose(actual[m],predicted[m],atol=1e-12,rtol=0)
    close(summarize(rows),json.loads((OUT/'results.json').read_text()))
    print('PASS: hashes, historical preservation, three roles, cutoffs, all decisions/metrics/bootstrap; raw prediction checks '+('passed.' if RAW.exists() else 'SKIPPED (raw not packaged).'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('stage',choices=['prepare','fit','evaluate','verify'])
    globals()[parser.parse_args().stage]()
