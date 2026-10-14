"""Frozen source-only 14-input comparison on the official PeerJ China cohort.

python -m ml.peerj_external fit
python -m ml.peerj_external evaluate
python -m ml.peerj_external verify
Optional interpret-core is loaded from the existing isolated research target.
"""
from __future__ import annotations

import os
for _key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.venv-ebm/site-packages'))
import joblib
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, confusion_matrix, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

from ml.schema import PROHIBITED, read_data

OUT = ROOT / 'output/research/peerj_v1'
RAW = ROOT / 'data/external_audit/peerj_v1/raw/peerj-10-14078-s001.csv'
SOURCE = ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'
PROTOCOL = ROOT / 'docs/peerj_external_protocol.md'
PROTOCOL_SHA = '40469f7e0557fa53659a7a1b07b15d3e20d2cf0c55682e319444f7281dcf6a47'
RAW_SHA = 'c94efdcd7aed7d2b02c242e405c3d07faffb66687ec119743648335299808cc5'
SOURCE_SHA = '739343245c2ba578b541370217531750d8e936022f928b83e0d91756caa3ff0b'
FEATURES = ['Age', 'Sex', 'BMI', 'DM', 'HTN', 'FBS', 'TG', 'LDL', 'HDL', 'HB', 'K', 'Na', 'WBC', 'PLT']
CAT = ['Sex', 'DM', 'HTN']
NUM = [f for f in FEATURES if f not in CAT]
MAPPING = {'Age': ('Age', 1), 'BMI': ('BMI', 1), 'FBS': ('Fasting blood glucose at admission', 1/.05551),
           'TG': ('Triglyceride', 1/.01129), 'LDL': ('LDLC', 1/.02586), 'HDL': ('HDLC', 1/.02586),
           'HB': ('HGB', .1), 'K': ('Blood potassium', 1), 'Na': ('Blood sodium', 1),
           'WBC': ('WBC', 1000), 'PLT': ('PLT', 1)}
PARAMS = dict(interactions=0, max_bins=64, outer_bags=8, learning_rate=.015, max_rounds=1000,
              early_stopping_rounds=100, early_stopping_tolerance=.00001, validation_size=.15,
              smoothing_rounds=75, min_samples_leaf=4, missing='separate', n_jobs=1, random_state=20261007)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def assert_inputs(require_external=True):
    assert sha(PROTOCOL) == PROTOCOL_SHA, 'Frozen protocol changed'
    assert sha(SOURCE) == SOURCE_SHA, 'Source workbook changed'
    assert len(FEATURES) == 14 and not set(FEATURES) & PROHIBITED
    if require_external:
        assert sha(RAW) == RAW_SHA, 'Official supplement changed'


def map_external(raw):
    """No inferred codes, labels, ids, fitted scaling or data repair enters X."""
    assert set(raw.Gender.unique()) <= {1, 2}
    assert set(raw.Diabetes.unique()) <= {0, 1}
    assert set(raw.Hypertension.unique()) <= {0, 1}
    x = pd.DataFrame({f: pd.to_numeric(raw[c], errors='raise') * factor for f, (c, factor) in MAPPING.items()})
    x['Sex'] = raw.Gender.map({1: 'Male', 2: 'Fmale'})
    x['DM'] = raw.Diabetes.astype(int).astype(str)
    x['HTN'] = raw.Hypertension.astype(int).astype(str)
    x = x[FEATURES]
    assert not x.isna().any().any() and np.isfinite(x[NUM].to_numpy()).all()
    return x


def external_raw():
    raw = pd.read_csv(RAW)
    assert raw.shape == (553, 45) and raw.id.is_unique and not raw.duplicated().any()
    assert raw.Group.value_counts().to_dict() == {0: 352, 1: 201}
    assert raw.Gender.value_counts().to_dict() == {1: 355, 2: 198}
    assert raw.Diabetes.value_counts().to_dict() == {0: 450, 1: 103}
    assert raw.Hypertension.value_counts().to_dict() == {1: 312, 0: 241}
    return raw


def model(kind):
    if kind == 'ebm':
        from interpret.glassbox import ExplainableBoostingClassifier
        assert importlib.metadata.version('interpret-core') == '0.7.8'
        return ExplainableBoostingClassifier(feature_types=['nominal' if f in CAT else 'continuous' for f in FEATURES], **PARAMS)
    pre = ColumnTransformer([
        ('numeric', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), NUM),
        ('category', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
                               ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), CAT)])
    return Pipeline([('preprocess', pre), ('model', LogisticRegression(C=.03, max_iter=3000, random_state=20261007))])


def metrics(y, p):
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    assert len(y) == len(p) and set(y) == {0, 1} and np.isfinite(p).all() and ((0 <= p) & (p <= 1)).all()
    tn, fp, fn, tp = [int(v) for v in confusion_matrix(y, p >= .5, labels=[0, 1]).ravel()]
    return dict(n=len(y), positives=int(y.sum()), prevalence=float(y.mean()), mean_probability=float(p.mean()),
                auc=float(roc_auc_score(y, p)), brier=float(brier_score_loss(y, p)), log_loss=float(log_loss(y, p)),
                accuracy=(tp+tn)/len(y), sensitivity=tp/(tp+fn), specificity=tn/(tn+fp),
                precision=tp/(tp+fp) if tp+fp else 0., f1=2*tp/(2*tp+fp+fn),
                confusion=dict(tn=tn, fp=fp, fn=fn, tp=tp),
                source_prevalence_constant_brier=float(np.mean((y-216/303)**2)))


def fit():
    assert_inputs()
    if OUT.exists():
        raise FileExistsError('Preserve the existing trial; fitting cannot overwrite it')
    # Validate mapping before fits, without computing destination predictions.
    map_external(external_raw())
    source = read_data(); x = source[FEATURES]; y = (source.Cath == 'CAD').astype(int).to_numpy()
    assert len(source) == 303 and not x.isna().any().any()
    OUT.mkdir(parents=True)
    shutil.copyfile(__file__, OUT / 'runner_snapshot.py')
    save(OUT / 'prefit_lock.json', dict(utc=datetime.now(timezone.utc).isoformat(),
         protocol_sha256=PROTOCOL_SHA, runner_sha256=sha(__file__), source_sha256=SOURCE_SHA, external_sha256=RAW_SHA))
    start = time.monotonic()
    table = pd.DataFrame({'row_index': np.arange(303), 'y': y, 'fold': -1, 'logistic': np.nan, 'ebm': np.nan})
    partitions, costs = [], []
    models = {}
    with threadpool_limits(limits=1):
        for fold, (train, test) in enumerate(StratifiedKFold(5, shuffle=True, random_state=20261007).split(x, y)):
            assert not set(train) & set(test)
            table.loc[test, 'fold'] = fold
            partitions.append(dict(fold=fold, train=train.tolist(), test=test.tolist()))
            for kind in ('logistic', 'ebm'):
                tick = time.monotonic(); est = model(kind).fit(x.iloc[train], y[train])
                table.loc[test, kind] = est.predict_proba(x.iloc[test])[:, 1]
                costs.append(dict(kind=kind, fold=fold, seconds=time.monotonic()-tick))
                assert time.monotonic()-start < 600, 'Fit stage budget exhausted'
        for kind in ('logistic', 'ebm'):
            tick = time.monotonic(); models[kind] = model(kind).fit(x, y)
            costs.append(dict(kind=kind, fold='all_source', seconds=time.monotonic()-tick))
            assert time.monotonic()-start < 600
    assert not table.isna().any().any() and set(table.fold) == set(range(5))
    table.to_csv(OUT / 'source_oof.csv', index=False, float_format='%.17g', lineterminator='\n')
    joblib.dump(models, OUT / 'source_models.joblib')
    save(OUT / 'fit_manifest.json', dict(status='frozen_before_external_scoring', protocol_sha256=PROTOCOL_SHA,
         source_sha256=SOURCE_SHA, external_sha256=RAW_SHA, runner_sha256=sha(OUT/'runner_snapshot.py'),
         features=FEATURES, ebm_parameters=PARAMS, train_rows=303, fit_costs=costs, folds=partitions,
         frozen_utc=datetime.now(timezone.utc).isoformat(), prefit_lock_sha256=sha(OUT/'prefit_lock.json'),
         elapsed_seconds=time.monotonic()-start,
         versions={name: importlib.metadata.version(name) for name in ('interpret-core','numpy','pandas','scikit-learn')},
         files={name: sha(OUT/name) for name in ('source_models.joblib','source_oof.csv')},
         source_oof={kind: metrics(y, table[kind]) for kind in models}))
    print('FROZEN: 12 source-only fits, 303 paired OOF predictions; destination unscored')


def paired_bootstrap(y, p0, p1):
    rng = np.random.default_rng(20261009); values=[]
    for _ in range(1000):
        rows = rng.integers(0, len(y), len(y)); yy=y[rows]
        if len(np.unique(yy)) < 2:
            continue
        a0, a1 = roc_auc_score(yy, p0[rows]), roc_auc_score(yy, p1[rows])
        b0, b1 = np.mean((yy-p0[rows])**2), np.mean((yy-p1[rows])**2)
        values.append([a0, a1, b0, b1, a1-a0, b1-b0])
    names=['logistic_auc','ebm_auc','logistic_brier','ebm_brier','delta_auc','delta_brier']
    return dict(draws=len(values), conditional_intervals={n: np.quantile(np.asarray(values)[:,i],[.025,.975]).tolist() for i,n in enumerate(names)})


def summaries(table):
    result={}
    for name, mask in {'primary': np.ones(len(table),dtype=bool), 'wbc_at_most_100': table.wbc_at_most_100.astype(bool),
                       'source_age_overlap': table.source_age_overlap.astype(bool)}.items():
        result[name]={kind: metrics(table.loc[mask,'y'], table.loc[mask,kind]) for kind in ('logistic','ebm')}
    return result


def evaluate():
    assert_inputs()
    assert not (OUT/'results.json').exists(), 'External result already exists; use verify'
    manifest=json.loads((OUT/'fit_manifest.json').read_text())
    assert manifest['status']=='frozen_before_external_scoring' and sha(__file__)==manifest['runner_sha256']
    for name, expected in manifest['files'].items(): assert sha(OUT/name)==expected
    raw=external_raw(); x=map_external(raw); y=raw.Group.to_numpy(int)
    models=joblib.load(OUT/'source_models.joblib')
    pred=pd.DataFrame(dict(row_index=np.arange(len(raw)), y=y, wbc_at_most_100=(raw.WBC<=100),
                          source_age_overlap=(raw.Age>=30), female=(raw.Gender==2), age_under_50=(raw.Age<50)))
    for kind, est in models.items(): pred[kind]=est.predict_proba(x)[:,1]
    pred.to_csv(OUT/'external_predictions.csv',index=False,float_format='%.17g',lineterminator='\n')
    source=read_data()[FEATURES]; ebm=models['ebm']; fidelity={}
    assert len(ebm.term_features_)==14 and all(len(t)==1 for t in ebm.term_features_)
    for label, frame in [('source',source),('external',x)]:
        terms=ebm.eval_terms(frame); reconstructed=terms.sum(axis=1)+float(np.asarray(ebm.intercept_).reshape(-1)[0])
        error=float(np.max(np.abs(reconstructed-ebm.decision_function(frame))))
        proba_error=float(np.max(np.abs(expit(reconstructed)-ebm.predict_proba(frame)[:,1])))
        assert error<1e-10 and proba_error<1e-10
        fidelity[label]=dict(rows=len(frame), max_logit_residual=error, max_probability_residual=proba_error)
    groups={}
    for name, mask in {'female':pred.female,'male':~pred.female,'under_50':pred.age_under_50,'age_50_plus':~pred.age_under_50}.items():
        yy=y[mask]; eligible=len(yy)>=30 and min(int(sum(yy)),len(yy)-int(sum(yy)))>=10
        groups[name]=dict(n=len(yy), positives=int(sum(yy)), eligible=eligible,
                         models={kind:metrics(yy,pred.loc[mask,kind]) for kind in models} if eligible else {})
    drift={f:dict(source_median=float(source[f].median()), external_median=float(x[f].median()),
                  source_iqr=[float(v) for v in source[f].quantile([.25,.75])],
                  external_iqr=[float(v) for v in x[f].quantile([.25,.75])],
                  outside_source_range=int(((x[f]<source[f].min())|(x[f]>source[f].max())).sum())) for f in NUM}
    reliability={}
    for kind in models:
        bins=np.minimum((pred[kind].to_numpy()*10).astype(int),9)
        reliability[kind]=[dict(bin=i,n=int(sum(bins==i)),mean_probability=float(pred.loc[bins==i,kind].mean()),
                                prevalence=float(pred.loc[bins==i,'y'].mean())) for i in range(10) if (bins==i).any()]
    scores=summaries(pred); p=scores['primary']; da=p['ebm']['auc']-p['logistic']['auc']; db=p['ebm']['brier']-p['logistic']['brier']
    result=dict(status='complete', task='separate_source_only_14_input_CAD_transport', primary_n=553,
                scored_utc=datetime.now(timezone.utc).isoformat(),
                scores=scores, paired_bootstrap=paired_bootstrap(y,pred.logistic.to_numpy(),pred.ebm.to_numpy()),
                delta_auc=da,delta_brier=db, engineering_screen=bool((da>=.015 and db<=0) or (db<=-.005 and da>=-.01)),
                subgroups=groups, distribution_shift=drift,reliability=reliability, native_ebm_fidelity=fidelity,
                fit_manifest_sha256=sha(OUT/'fit_manifest.json'), predictions_sha256=sha(OUT/'external_predictions.csv'),
                protocol_sha256=PROTOCOL_SHA, external_sha256=RAW_SHA,
                limitations='Different selected country/center, 14 inputs, CHD endpoint, incomplete source units/timing; not 55-input app validation.')
    save(OUT/'results.json',result)
    save(OUT/'evaluation_manifest.json',{name:sha(OUT/name) for name in ('results.json','external_predictions.csv','fit_manifest.json','runner_snapshot.py','prefit_lock.json')})
    print(json.dumps(dict(primary=p,delta_auc=da,delta_brier=db,screen=result['engineering_screen']),indent=2))


def verify():
    assert_inputs(require_external=False)
    manifest=json.loads((OUT/'fit_manifest.json').read_text()); result=json.loads((OUT/'results.json').read_text())
    for name, expected in {**manifest['files'],**json.loads((OUT/'evaluation_manifest.json').read_text())}.items():
        assert sha(OUT/name)==expected, name
    assert manifest['runner_sha256']==sha(OUT/'runner_snapshot.py') and manifest['protocol_sha256']==PROTOCOL_SHA
    assert result['fit_manifest_sha256']==sha(OUT/'fit_manifest.json') and result['predictions_sha256']==sha(OUT/'external_predictions.csv')
    src=pd.read_csv(OUT/'source_oof.csv',float_precision='round_trip'); ext=pd.read_csv(OUT/'external_predictions.csv',float_precision='round_trip')
    assert list(src.row_index)==list(range(303)) and list(ext.row_index)==list(range(553))
    assert ext.y.value_counts().to_dict()=={0:352,1:201}
    seen=set()
    for fold in manifest['folds']:
        train,test=set(fold['train']),set(fold['test'])
        assert not train&test and train|test==set(range(303)) and not seen&test
        assert (src.loc[list(test),'fold']==fold['fold']).all();seen|=test
    assert seen==set(range(303))
    assert np.array_equal(src.y.to_numpy(),(read_data().Cath=='CAD').astype(int).to_numpy())
    for kind in ('logistic','ebm'):
        assert metrics(src.y,src[kind])==manifest['source_oof'][kind]
    assert summaries(ext)==result['scores']
    boot=paired_bootstrap(ext.y.to_numpy(),ext.logistic.to_numpy(),ext.ebm.to_numpy())
    for name, bounds in boot['conditional_intervals'].items():
        assert np.allclose(bounds,result['paired_bootstrap']['conditional_intervals'][name],rtol=0,atol=1e-12)
    if RAW.exists():
        assert sha(RAW)==RAW_SHA
        raw=external_raw(); assert np.array_equal(ext.y,raw.Group)
        for key, expected in {'female':raw.Gender==2,'age_under_50':raw.Age<50,
                              'source_age_overlap':raw.Age>=30,'wbc_at_most_100':raw.WBC<=100}.items():
            assert np.array_equal(ext[key],expected)
    print('Verified frozen models/protocol/runner, 303 source folds and 553 external rows, paired metrics and bootstrap intervals.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['fit','evaluate','verify'])
    globals()[parser.parse_args().stage]()
