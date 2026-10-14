"""Frozen bounded LCX training experiment; never imported by live prediction."""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import argparse,json,time,shutil
from datetime import datetime,timezone
import joblib,numpy as np,pandas as pd
from scipy.optimize import minimize
from scipy.special import expit,logit
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.model_selection import StratifiedGroupKFold
from threadpoolctl import threadpool_limits
from ml import multicohort as mc
from ml import cohort_calibration as cc
from ml.schema import ROOT,FEATURES,NUMERIC,read_data

OUT=ROOT/'ml/experiments/full_input_transfer_v1'
PROTOCOL=ROOT/'docs/full_input_transfer_protocol.md'
ARMS=['common_local','full_local','full_augmented']

def pre(fields):
    numeric=[f for f in fields if f in NUMERIC];category=[f for f in fields if f not in NUMERIC]
    return ColumnTransformer([
        ('numeric',Pipeline([('impute',SimpleImputer(strategy='median',keep_empty_features=True)),('scale',StandardScaler())]),numeric),
        ('category',Pipeline([('impute',SimpleImputer(strategy='most_frequent',keep_empty_features=True)),('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),category)])

def data():
    cohorts=mc.inputs()['lcx'];source=read_data()[FEATURES]
    assert np.array_equal(cohorts['uci']['x'].to_numpy(),source[list(cohorts['uci']['x'])].to_numpy())
    return cohorts,source

def dependencies():
    paths=[__file__,PROTOCOL,mc.__file__,cc.__file__,ROOT/'ml/angiocad_external.py',ROOT/'ml/schema.py']
    return {Path(p).relative_to(ROOT).as_posix():mc.sha(p) for p in paths}

from pathlib import Path
def prepare():
    assert not OUT.exists(),'Refuse overwrite'
    cohorts,source=data();s=cohorts['uci'];parts=[]
    for repeat,seed in enumerate([20261013,20261014],1):
        for fold,(train,test) in enumerate(StratifiedGroupKFold(5,shuffle=True,random_state=seed).split(source,s['y'],s['fingerprints'])):
            blocked=set(s['fingerprints'][test]);extra=[i for i,f in enumerate(cohorts['angiocad']['fingerprints']) if f not in blocked]
            assert not set(s['fingerprints'][train])&blocked
            parts.append(dict(key=f'r{repeat}_f{fold}',repeat=repeat,fold=fold,train=train.tolist(),test=test.tolist(),extra=extra))
    OUT.mkdir(parents=True);(OUT/'private').mkdir();shutil.copyfile(__file__,OUT/'runner_snapshot.py')
    mc.save(OUT/'partitions.json',parts)
    mc.save(OUT/'prepared.json',dict(utc=datetime.now(timezone.utc).isoformat(),dependencies=dependencies(),history=cc.history(),raw_hashes=mc.raw_hashes(),partitions_sha256=mc.sha(OUT/'partitions.json'),rows={n:len(v['y']) for n,v in cohorts.items()}))
    print('Prepared 10 fixed source folds; no fits or evaluation scores.')

def locked():
    receipt=json.loads((OUT/'prepared.json').read_text())
    assert receipt['dependencies']==dependencies() and receipt['history']==cc.history()
    assert receipt['raw_hashes']==mc.raw_hashes() and receipt['partitions_sha256']==mc.sha(OUT/'partitions.json')
    assert mc.sha(OUT/'runner_snapshot.py')==mc.sha(__file__)
    return receipt

def train_one(local_x,local_y,extra_x,extra_y,arm):
    common=list(extra_x);private=[f for f in FEATURES if f not in common]
    augmented=arm=='full_augmented';full=arm!='common_local'
    shared=pre(common)
    shared.fit(pd.concat([local_x[common],extra_x],ignore_index=True) if augmented else local_x[common])
    source_z=shared.transform(local_x)
    own=pre(private) if full else None
    if own is not None:source_z=np.column_stack([source_z,own.fit_transform(local_x)])
    y=np.asarray(local_y);groups=np.zeros(len(y),dtype=int);z=source_z
    if augmented:
        extra_z=np.column_stack([shared.transform(extra_x),np.zeros((len(extra_x),source_z.shape[1]-shared.transform(extra_x).shape[1]))])
        z=np.vstack([source_z,extra_z]);y=np.r_[y,extra_y];groups=np.r_[groups,np.ones(len(extra_y),dtype=int)]
    dim=z.shape[1];initial=np.r_[np.zeros(dim),[logit(np.mean(y[groups==i])) for i in range(groups.max()+1)]]
    def objective(theta):
        beta,alpha=theta[:dim],theta[dim:];score=z@beta+alpha[groups];residual=expit(score)-y
        return float(np.sum(np.logaddexp(0,score)-y*score)+np.dot(beta,beta)/(2*.03)),np.r_[z.T@residual+beta/.03,np.bincount(groups,weights=residual,minlength=len(alpha))]
    fit=minimize(objective,initial,jac=True,method='L-BFGS-B',options=dict(maxiter=3000,ftol=1e-10,gtol=1e-6))
    if not fit.success:raise RuntimeError(str(fit.message))
    return dict(shared=shared,private=own,coef=fit.x[:dim],intercepts=fit.x[dim:],iterations=int(fit.nit))

def predict(fit,x):
    z=fit['shared'].transform(x)
    if fit['private'] is not None:z=np.column_stack([z,fit['private'].transform(x)])
    return expit(z@fit['coef']+fit['intercepts'][0])

def fit():
    locked();assert not (OUT/'fit_receipt.json').exists()
    cohorts,source=data();parts=json.loads((OUT/'partitions.json').read_text());fits={};start=time.monotonic()
    with threadpool_limits(limits=1):
        for s in parts:
            for arm in ARMS:
                fits[s['key']+'_'+arm]=train_one(source.iloc[s['train']],cohorts['uci']['y'][s['train']],cohorts['angiocad']['x'].iloc[s['extra']],cohorts['angiocad']['y'][s['extra']],arm)
                assert time.monotonic()-start<300,'Fit budget exceeded'
    joblib.dump(fits,OUT/'private/fitted.joblib',compress=3)
    mc.save(OUT/'fit_receipt.json',dict(utc=datetime.now(timezone.utc).isoformat(),seconds=time.monotonic()-start,sha256=mc.sha(OUT/'private/fitted.joblib')))
    locked();print('Frozen 30 models before evaluation.')

def metrics(frame):
    return {str(rep):{arm:mc.measures(p.y,p.probability) for arm,p in group.groupby('arm')} for rep,group in frame.groupby('repeat')}

def evaluate():
    locked();assert not (OUT/'evaluation_predictions.csv').exists()
    assert mc.sha(OUT/'private/fitted.joblib')==json.loads((OUT/'fit_receipt.json').read_text())['sha256']
    cohorts,source=data();fits=joblib.load(OUT/'private/fitted.joblib');rows=[]
    for s in json.loads((OUT/'partitions.json').read_text()):
        for arm in ARMS:
            p=predict(fits[s['key']+'_'+arm],source.iloc[s['test']])
            rows += [dict(repeat=s['repeat'],fold=s['fold'],arm=arm,row=int(i),y=int(cohorts['uci']['y'][i]),probability=float(v)) for i,v in zip(s['test'],p)]
    frame=pd.DataFrame(rows);frame.to_csv(OUT/'evaluation_predictions.csv',index=False,float_format='%.17g',lineterminator='\n')
    aa=frame[frame.arm=='full_augmented'].sort_values(['repeat','row']);bb=frame[frame.arm=='full_local'].sort_values(['repeat','row'])
    assert np.array_equal(aa[['repeat','row','y']],bb[['repeat','row','y']])
    errors=pd.DataFrame(dict(row=aa.row.to_numpy(),delta=(aa.probability.to_numpy()-aa.y.to_numpy())**2-(bb.probability.to_numpy()-bb.y.to_numpy())**2)).groupby('row').delta.mean().to_numpy()
    rng=np.random.default_rng(20261013);boot=[errors[rng.integers(0,len(errors),len(errors))].mean() for _ in range(1000)]
    mc.save(OUT/'results.json',dict(scope='Previously inspected cohorts; full-input local development, no independent validation.',scores=metrics(frame),paired_brier_delta=float(errors.mean()),conditional_delta_95=np.quantile(boot,[.025,.975]).tolist(),prediction_sha256=mc.sha(OUT/'evaluation_predictions.csv')))
    locked();print(json.dumps(json.loads((OUT/'results.json').read_text()),indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','fit','evaluate']);globals()[parser.parse_args().action]()
