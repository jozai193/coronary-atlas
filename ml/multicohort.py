"""Frozen multi-study training experiment; never imported by prediction serving."""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss,confusion_matrix
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from threadpoolctl import threadpool_limits
from ml.schema import ROOT,TARGETS,PROHIBITED,read_data
from ml import angiocad_external as angio
from ml import peerj_external as china

OUT=ROOT/'output/research/multicohort_v1'
PROTOCOL=ROOT/'docs/multicohort_protocol.md'
SEED=20261013
CAD_FIELDS=['Age','Sex','BMI','DM','HTN','FBS','TG','LDL','HDL','WBC','PLT']
ARMS=['local_only','pooled','study_balanced','study_ensemble']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def utc():return datetime.now(timezone.utc).isoformat()


def inputs():
    assert sha(angio.SOURCE)==angio.EXPECTED_SOURCE
    source=read_data()
    ax,labels,_=angio.joined_external()
    masks,audit=angio.eligibility(ax)
    assert audit['primary_eligible']==363
    ay=angio.make_endpoints(labels,branch=False)
    assert sha(china.RAW)==china.RAW_SHA
    raw=china.external_raw();cx=china.map_external(raw)
    data={}
    for target,column in TARGETS.items():
        fields=CAD_FIELDS if target=='cad' else angio.FEATURES
        assert not set(fields)&PROHIBITED
        def frame(x,y,rows):
            return dict(x=x[fields].reset_index(drop=True),y=np.asarray(y,dtype=int),rows=np.asarray(rows,dtype=int))
        sy=(source[column]==('CAD' if target=='cad' else 'Stenotic')).astype(int)
        keep=masks['primary']&ay[target].notna().to_numpy()
        data[target]={'uci':frame(source,sy,np.arange(len(source))),
                      'angiocad':frame(ax.loc[keep],ay.loc[keep,target],np.where(keep)[0])}
        if target=='cad':data[target]['anhui']=frame(cx,raw.Group,np.arange(len(raw)))
        for item in data[target].values():
            item['fingerprints']=fingerprints(item['x'])
            assert set(item['y'])=={0,1}
    return data


def fingerprints(x):
    def value(v):
        if pd.isna(v):return None
        return float(v) if isinstance(v,(int,float,np.number)) else str(v)
    return np.array([hashlib.sha256(json.dumps([value(v) for v in row],separators=(',',':')).encode()).hexdigest()
                     for row in x.itertuples(index=False,name=None)])


def balance_weights(groups):
    groups=np.asarray(groups);names,counts=np.unique(groups,return_counts=True)
    weights={name:len(groups)/(len(names)*n) for name,n in zip(names,counts)}
    return np.array([weights[g] for g in groups])


def model(fields):
    cat=[f for f in fields if f in ['Sex','DM','HTN','Current Smoker']]
    num=[f for f in fields if f not in cat]
    pre=ColumnTransformer([
        ('numeric',Pipeline([('impute',SimpleImputer(strategy='median',keep_empty_features=True)),('scale',StandardScaler())]),num),
        ('category',Pipeline([('impute',SimpleImputer(strategy='most_frequent',keep_empty_features=True)),
                              ('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cat)])
    return Pipeline([('preprocess',pre),('model',LogisticRegression(C=.03,max_iter=3000,random_state=SEED))])


def roles(cohorts,destination,test,local_train=None):
    """Reject exact held-out fingerprints from every training cohort."""
    blocked=set(cohorts[destination]['fingerprints'][test])
    training={};removed={}
    for name,item in cohorts.items():
        if name==destination and local_train is None:continue
        indices=np.asarray(local_train if name==destination else np.arange(len(item['y'])),dtype=int)
        keep=np.array([i for i in indices if item['fingerprints'][i] not in blocked],dtype=int)
        training[name]=keep.tolist();removed[name]=int(len(indices)-len(keep))
        assert len(keep) and set(item['y'][keep])=={0,1}
        if name==destination:assert not set(test)&set(keep)
    return training,removed


def partitions(data):
    result=[]
    for target,cohorts in data.items():
        for destination,item in cohorts.items():
            test=np.arange(len(item['y']))
            train,removed=roles(cohorts,destination,test)
            result.append(dict(key=f'{target}_{destination}_transport',target=target,destination=destination,
                               design='transport',fold=None,test=test.tolist(),training=train,removed=removed))
            cv=StratifiedGroupKFold(5,shuffle=True,random_state=SEED)
            for fold,(local_train,test) in enumerate(cv.split(item['x'],item['y'],item['fingerprints'])):
                assert set(item['y'][test])=={0,1}
                train,removed=roles(cohorts,destination,test,local_train)
                result.append(dict(key=f'{target}_{destination}_f{fold}',target=target,destination=destination,
                                   design='augmentation',fold=fold,test=test.tolist(),training=train,removed=removed))
    return result


def protected():
    folders=[ROOT/'models',ROOT/'ml/metrics']
    files=[p for f in folders for p in f.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    for f in (ROOT/'output/research').glob('*'):
        if f.is_dir() and f!=OUT:
            files.extend(p for p in f.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    files += [ROOT/'data/processed/sample_patients.json',ROOT/'frontend/public/anatomy/manifest.json']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)}


def raw_hashes():
    paths=[angio.SOURCE,china.RAW]+[angio.RAW/name for name in angio.EXPECTED_RAW]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def dependencies():
    return {p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),PROTOCOL,Path(angio.__file__),Path(china.__file__),ROOT/'ml/schema.py']}


def prepare():
    assert not OUT.exists(),'Refuse to overwrite this experiment'
    data=inputs();parts=partitions(data)
    OUT.mkdir(parents=True);(OUT/'private').mkdir()
    shutil.copyfile(__file__,OUT/'runner_snapshot.py')
    save(OUT/'partitions.json',parts)
    audit={}
    for target,cohorts in data.items():
        audit[target]={name:dict(n=len(v['y']),positives=int(v['y'].sum()),
                         missing={f:int(v['x'][f].isna().sum()) for f in v['x']},
                         duplicate_input_rows=int(len(v['y'])-len(set(v['fingerprints'])))) for name,v in cohorts.items()}
        audit[target]['cross_cohort_fingerprint_matches']={a+'__'+b:len(set(cohorts[a]['fingerprints'])&set(cohorts[b]['fingerprints']))
                            for i,a in enumerate(cohorts) for b in list(cohorts)[i+1:]}
    save(OUT/'prepared.json',dict(utc=utc(),raw_hashes=raw_hashes(),dependencies=dependencies(),historical=protected(),
             partitions_sha256=sha(OUT/'partitions.json'),audit=audit,fields={t:list(next(iter(c.values()))['x']) for t,c in data.items()},
             versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','joblib']}))
    print('Prepared',len(parts),'cohort/within-cohort roles before fitting; no new scores.')


def locked():
    prep=json.loads((OUT/'prepared.json').read_text(encoding='utf-8'))
    assert raw_hashes()==prep['raw_hashes']
    assert dependencies()==prep['dependencies']
    assert sha(OUT/'runner_snapshot.py')==sha(__file__)
    assert sha(OUT/'partitions.json')==prep['partitions_sha256']
    assert protected()==prep['historical'],'Historical evidence changed'
    return prep


def fit_training(training):
    """Only explicitly selected training X/y are accepted; evaluation is absent."""
    fields=list(next(iter(training.values()))[0])
    assert not set(fields)&PROHIBITED
    for x,y in training.values():assert list(x)==fields and set(y)=={0,1}
    x=pd.concat([v[0] for v in training.values()],ignore_index=True)
    y=np.concatenate([v[1] for v in training.values()])
    groups=np.concatenate([np.repeat(name,len(v[1])) for name,v in training.items()])
    fitted={'pooled':model(fields).fit(x,y),
            'study_balanced':model(fields).fit(x,y,model__sample_weight=balance_weights(groups))}
    for name,(xx,yy) in training.items():fitted['single_'+name]=model(fields).fit(xx,yy)
    return fitted


def predict(fitted,x,destination,design):
    probs={name:est.predict_proba(x)[:,1] for name,est in fitted.items()}
    singles=[p for name,p in probs.items() if name.startswith('single_')]
    probs['study_ensemble']=np.mean(singles,axis=0)
    if design=='augmentation':
        probs['local_only']=probs['single_'+destination]
        probs={name:probs[name] for name in ARMS}
    return probs


def measures(y,p):
    y=np.asarray(y,dtype=int);p=np.asarray(p,dtype=float)
    assert set(y)=={0,1} and len(y)==len(p) and np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
    tn,fp,fn,tp=map(int,confusion_matrix(y,p>=.5,labels=[0,1]).ravel())
    bins=[]
    for i in range(5):
        mask=(p>=i/5)&(p<(i+1)/5 if i<4 else p<=1)
        bins.append(dict(n=int(mask.sum()),mean_probability=float(p[mask].mean()) if mask.any() else None,
                         observed_fraction=float(y[mask].mean()) if mask.any() else None))
    return dict(n=len(y),positives=int(y.sum()),prevalence=float(y.mean()),mean_probability=float(p.mean()),
                auc=float(roc_auc_score(y,p)),average_precision=float(average_precision_score(y,p)),brier=float(brier_score_loss(y,p)),
                log_loss=float(log_loss(y,p)),accuracy=(tn+tp)/len(y),sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),
                precision=tp/(tp+fp) if tp+fp else 0.,f1=2*tp/(2*tp+fp+fn),confusion=dict(tn=tn,fp=fp,fn=fn,tp=tp),reliability=bins)


def summarize(table):
    scores={};deltas=[]
    for (target,cohort,design,arm),part in table.groupby(['target','cohort','design','arm'],sort=True):
        scores.setdefault(target,{}).setdefault(cohort,{}).setdefault(design,{})[arm]=measures(part.y,part.probability)
    for target,cohorts in scores.items():
        for cohort,result in cohorts.items():
            source=table[(table.target==target)&(table.cohort==cohort)&(table.design=='augmentation')]
            base=source[source.arm=='local_only'].sort_values('row_index')
            y=base.y.to_numpy();p=base.probability.to_numpy()
            for arm in ARMS[1:]:
                other=source[source.arm==arm].sort_values('row_index')
                assert np.array_equal(base.row_index,other.row_index) and np.array_equal(base.y,other.y)
                q=other.probability.to_numpy();diff=(q-y)**2-(p-y)**2
                rng=np.random.default_rng(SEED);boot=np.array([diff[rng.integers(0,len(y),len(y))].mean() for _ in range(1000)])
                deltas.append(dict(target=target,cohort=cohort,arm=arm,brier_delta=float(diff.mean()),
                                   auc_delta=float(roc_auc_score(y,q)-roc_auc_score(y,p)),
                                   conditional_brier_delta_95=np.quantile(boot,[.025,.975]).tolist()))
    means={t:{a:{metric:float(np.mean([scores[t][c]['augmentation'][a][metric] for c in scores[t]]))
                for metric in ['auc','brier','accuracy','sensitivity','specificity']} for a in ARMS} for t in scores}
    return dict(scope='Reused-cohort reduced-input research development; not validation of the 55-input app.',
                scores=scores,augmentation_deltas=deltas,equal_cohort_augmentation_means=means,
                study_balanced_signal={t:all(d['brier_delta']<0 and d['auc_delta']>=0 for d in deltas if d['target']==t and d['arm']=='study_balanced') for t in scores})


def fit_evaluate():
    locked();assert not (OUT/'predictions.csv').exists() and not (OUT/'private/fitted.joblib').exists(),'No overwrite'
    data=inputs();parts=json.loads((OUT/'partitions.json').read_text(encoding='utf-8'))
    rows=[];fits={};costs=[];start=time.monotonic()
    with threadpool_limits(limits=1):
        for spec in parts:
            tick=time.monotonic();cohorts=data[spec['target']];destination=spec['destination'];item=cohorts[destination]
            training={name:(cohorts[name]['x'].iloc[ix],cohorts[name]['y'][ix]) for name,ix in spec['training'].items()}
            fitted=fit_training(training);fits[spec['key']]=fitted
            probs=predict(fitted,item['x'].iloc[spec['test']],destination,spec['design'])
            constant=float(np.concatenate([v[1] for v in training.values()]).mean())
            probs['training_prevalence']=np.full(len(spec['test']),constant)
            for arm,p in probs.items():
                for i,value in zip(spec['test'],p):rows.append(dict(target=spec['target'],cohort=destination,design=spec['design'],
                        arm=arm,row_index=int(item['rows'][i]),fold=spec['fold'] if spec['fold'] is not None else -1,
                        y=int(item['y'][i]),probability=float(value)))
            costs.append(dict(key=spec['key'],seconds=time.monotonic()-tick))
            assert time.monotonic()-start<600,'Fixed fit budget exceeded'
        final={t:fit_training({name:(v['x'],v['y']) for name,v in c.items()}) for t,c in data.items()}
    joblib.dump(dict(partitions=fits,all_data_research_only=final),OUT/'private/fitted.joblib',compress=3)
    table=pd.DataFrame(rows);assert not table.duplicated(['target','cohort','design','arm','row_index']).any()
    table.to_csv(OUT/'predictions.csv',index=False,float_format='%.17g',lineterminator='\n')
    # Re-read the serialized receipt used by the independent verifier.
    table=pd.read_csv(OUT/'predictions.csv',float_precision='round_trip')
    result=summarize(table);save(OUT/'results.json',result)
    save(OUT/'fit_receipt.json',dict(utc=utc(),elapsed_seconds=time.monotonic()-start,costs=costs,
             fitted_sha256=sha(OUT/'private/fitted.joblib'),predictions_sha256=sha(OUT/'predictions.csv'),results_sha256=sha(OUT/'results.json')))
    locked();print('Completed all',len(parts),'roles in',round(time.monotonic()-start,2),'seconds; all arms retained, no promotion.')


def verify():
    prep=locked();data=inputs();parts=json.loads((OUT/'partitions.json').read_text(encoding='utf-8'))
    assert parts==partitions(data)
    receipt=json.loads((OUT/'fit_receipt.json').read_text(encoding='utf-8'))
    for name,key in [('private/fitted.joblib','fitted_sha256'),('predictions.csv','predictions_sha256'),('results.json','results_sha256')]:assert sha(OUT/name)==receipt[key]
    bundle=joblib.load(OUT/'private/fitted.joblib');table=pd.read_csv(OUT/'predictions.csv',float_precision='round_trip')
    for spec in parts:
        cohorts=data[spec['target']];item=cohorts[spec['destination']]
        block=set(item['fingerprints'][spec['test']])
        for name,ix in spec['training'].items():assert not block&set(cohorts[name]['fingerprints'][ix])
        fits=bundle['partitions'][spec['key']]
        probs=predict(fits,item['x'].iloc[spec['test']],spec['destination'],spec['design'])
        subset=table[(table.target==spec['target'])&(table.cohort==spec['destination'])&(table.design==spec['design'])&
                     (table.fold==(spec['fold'] if spec['fold'] is not None else -1))]
        for arm,p in probs.items():
            saved=subset[subset.arm==arm].set_index('row_index').loc[item['rows'][spec['test']]]
            assert np.array_equal(saved.y,item['y'][spec['test']]) and np.allclose(saved.probability,p,atol=1e-14,rtol=0)
    assert json.loads((OUT/'results.json').read_text(encoding='utf-8'))==summarize(table)
    print('PASS: raw/code/protocol/history hashes, every training role and fitted prediction, all saved metrics; 55-input app unchanged.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','run','verify'])
    {'prepare':prepare,'run':fit_evaluate,'verify':verify}[parser.parse_args().stage]()
