"""Three-role, cohort-aware development; never part of live inference."""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import argparse
from dataclasses import dataclass
from datetime import datetime,timezone
import importlib.metadata
import json
from pathlib import Path
import shutil
import time
import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit,logit
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from threadpoolctl import threadpool_limits
from ml import multicohort as mc
from ml.peerj_operating import cutoff

ROOT=mc.ROOT
OUT=ROOT/'ml/experiments/cohort_calibration_v1'
PROTOCOL=ROOT/'docs/cohort_calibration_protocol.md'
BASES=['local','pooled','cohort_intercepts','transfer_pooled']
ARMS=[a+s for a in BASES for s in ('','_sigmoid')]
SEED=20261013
sha,save=mc.sha,mc.save


@dataclass
class CohortLogit:
    preprocess:object
    studies:list[str]
    coef:np.ndarray
    intercepts:np.ndarray
    optimizer:dict

    def predict_proba(self,x,study):
        if study not in self.studies:raise ValueError('Unknown cohort: no validated intercept exists')
        z=self.preprocess.transform(x)
        p=expit(z@self.coef+self.intercepts[self.studies.index(study)])
        return np.column_stack([1-p,p])


def cohort_model(training):
    fields=list(next(iter(training.values()))[0]);studies=sorted(training)
    x=pd.concat([training[n][0] for n in studies],ignore_index=True)
    y=np.concatenate([training[n][1] for n in studies])
    groups=np.concatenate([np.repeat(i,len(training[n][1])) for i,n in enumerate(studies)])
    assert all(set(v[1])=={0,1} for v in training.values())
    pre=mc.model(fields).named_steps['preprocess'];z=np.asarray(pre.fit_transform(x),dtype=float)
    dim=z.shape[1]
    initial=np.r_[np.zeros(dim),[logit(np.mean(training[n][1])) for n in studies]]
    def objective(theta):
        beta,alpha=theta[:dim],theta[dim:];score=z@beta+alpha[groups]
        residual=expit(score)-y
        loss=float(np.sum(np.logaddexp(0,score)-y*score)+np.dot(beta,beta)/(2*.03))
        gradient=np.r_[z.T@residual+beta/.03,np.bincount(groups,weights=residual,minlength=len(studies))]
        return loss,gradient
    fitted=minimize(objective,initial,jac=True,method='L-BFGS-B',options=dict(maxiter=3000,ftol=1e-10,gtol=1e-6))
    if not fitted.success:raise RuntimeError('Fixed-intercept optimizer failed: '+str(fitted.message))
    return CohortLogit(pre,studies,fitted.x[:dim],fitted.x[dim:],
                       dict(iterations=int(fitted.nit),objective=float(fitted.fun),max_abs_gradient=float(np.max(np.abs(fitted.jac)))))


def parts(data):
    result=[]
    for target,cohorts in data.items():
        for destination,item in cohorts.items():
            x,y,groups=item['x'],item['y'],item['fingerprints']
            for rep,seed in enumerate((20261013,20261014)):
                outer=StratifiedGroupKFold(5,shuffle=True,random_state=seed)
                for fold,(pool,test) in enumerate(outer.split(x,y,groups)):
                    inner=StratifiedGroupKFold(4,shuffle=True,random_state=20261015+100*rep+fold)
                    tt,cc=next(inner.split(x.iloc[pool],y[pool],groups[pool]))
                    train,cal=pool[tt],pool[cc]
                    assert all(set(y[ix])=={0,1} for ix in [train,cal,test])
                    assert not (set(groups[train])&set(groups[cal]) or set(groups[train])&set(groups[test]) or set(groups[cal])&set(groups[test]))
                    blocked=set(groups[cal])|set(groups[test]);training={destination:train.tolist()};removed={}
                    for name,v in cohorts.items():
                        if name==destination:continue
                        ix=[i for i,f in enumerate(v['fingerprints']) if f not in blocked]
                        assert set(v['y'][ix])=={0,1}
                        training[name]=ix;removed[name]=len(v['y'])-len(ix)
                    result.append(dict(key=f'{target}_{destination}_r{rep+1}_f{fold}',target=target,destination=destination,
                         repeat=rep+1,fold=fold,training=training,calibration=cal.tolist(),evaluation=test.tolist(),removed=removed))
    return result


def history():
    paths=[]
    for folder in [ROOT/'models',ROOT/'ml/metrics',ROOT/'output/research']:
        paths += [p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    paths += [ROOT/'data/processed/sample_patients.json',ROOT/'frontend/public/anatomy/manifest.json']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}


def dependencies():
    paths=[Path(__file__),PROTOCOL,Path(mc.__file__),ROOT/'ml/peerj_operating.py',ROOT/'ml/angiocad_external.py',ROOT/'ml/peerj_external.py',ROOT/'ml/schema.py']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def prepare():
    assert not OUT.exists(),'Refuse overwrite'
    data=mc.inputs();partition=parts(data)
    OUT.mkdir(parents=True);(OUT/'private').mkdir();shutil.copyfile(__file__,OUT/'runner_snapshot.py')
    save(OUT/'partitions.json',partition)
    save(OUT/'prepared.json',dict(utc=datetime.now(timezone.utc).isoformat(),dependencies=dependencies(),raw_hashes=mc.raw_hashes(),
         historical=history(),partitions_sha256=sha(OUT/'partitions.json'),
         cohorts={t:{n:dict(n=len(v['y']),positives=int(v['y'].sum()),fields=list(v['x'])) for n,v in c.items()} for t,c in data.items()},
         versions={n:importlib.metadata.version(n) for n in ['numpy','pandas','scipy','scikit-learn','joblib']}))
    print('Prepared',len(partition),'disjoint training/calibration/evaluation roles; no fits or scores.')


def locked():
    p=json.loads((OUT/'prepared.json').read_text(encoding='utf-8'))
    assert p['dependencies']==dependencies() and p['raw_hashes']==mc.raw_hashes()
    assert p['historical']==history(),'Historical artifacts changed'
    assert p['partitions_sha256']==sha(OUT/'partitions.json') and sha(OUT/'runner_snapshot.py')==sha(__file__)
    return p


def base_predict(fitted,x,destination):
    return {name:est.predict_proba(x,destination)[:,1] if name=='cohort_intercepts' else est.predict_proba(x)[:,1]
            for name,est in fitted['bases'].items()}


def predict(fitted,x,destination):
    p=base_predict(fitted,x,destination)
    for name in BASES:p[name+'_sigmoid']=fitted['calibrators'][name].predict_proba(logit(np.clip(p[name],1e-6,1-1e-6)).reshape(-1,1))[:,1]
    p['training_prevalence']=np.full(len(x),fitted['prevalence'])
    return p


def fit_roles(training,cal_x,cal_y,destination):
    """No evaluation features or labels enter this fitting interface."""
    assert set(cal_y)=={0,1} and destination in training and len(training)>=2
    fields=list(cal_x)
    assert all(list(v[0])==fields for v in training.values()) and not set(fields)&mc.PROHIBITED
    local_x,local_y=training[destination]
    xx=pd.concat([v[0] for v in training.values()],ignore_index=True);yy=np.concatenate([v[1] for v in training.values()])
    other={n:v for n,v in training.items() if n!=destination}
    ox=pd.concat([v[0] for v in other.values()],ignore_index=True);oy=np.concatenate([v[1] for v in other.values()])
    fitted=dict(bases=dict(local=mc.model(fields).fit(local_x,local_y),pooled=mc.model(fields).fit(xx,yy),
                          cohort_intercepts=cohort_model(training),transfer_pooled=mc.model(fields).fit(ox,oy)),
                calibrators={},prevalence=float(np.mean(local_y)))
    raw=base_predict(fitted,cal_x,destination)
    for name,p in raw.items():
        fitted['calibrators'][name]=LogisticRegression(C=1,max_iter=3000,random_state=SEED).fit(logit(np.clip(p,1e-6,1-1e-6)).reshape(-1,1),cal_y)
    probs=predict(fitted,cal_x,destination)
    fitted['cutoffs']={name:dict(fixed_50=.5,target_90=cutoff(cal_y,probs[name],.9)) for name in ARMS}
    fitted['cutoffs']['training_prevalence']=dict(fixed_50=.5)
    return fitted,probs


def fit():
    locked();assert not (OUT/'fit_receipt.json').exists() and not (OUT/'private/fitted.joblib').exists(),'Refuse overwrite'
    data=mc.inputs();partition=json.loads((OUT/'partitions.json').read_text(encoding='utf-8'))
    fits={};meta=[];cal_rows=[];start=time.monotonic()
    with threadpool_limits(limits=1):
        for spec in partition:
            tick=time.monotonic();c=data[spec['target']];item=c[spec['destination']]
            training={n:(c[n]['x'].iloc[ix],c[n]['y'][ix]) for n,ix in spec['training'].items()}
            f,p=fit_roles(training,item['x'].iloc[spec['calibration']],item['y'][spec['calibration']],spec['destination']);fits[spec['key']]=f
            for arm,prob in p.items():
                for i,v in zip(spec['calibration'],prob):cal_rows.append(dict(key=spec['key'],arm=arm,row_index=int(item['rows'][i]),y=int(item['y'][i]),probability=float(v)))
            ci=f['bases']['cohort_intercepts']
            meta.append(dict(key=spec['key'],seconds=time.monotonic()-tick,cutoffs=f['cutoffs'],optimizer=ci.optimizer,
                cohort_intercepts={n:float(v) for n,v in zip(ci.studies,ci.intercepts)},
                calibration={n:dict(slope=float(m.coef_[0,0]),intercept=float(m.intercept_[0])) for n,m in f['calibrators'].items()}))
            assert time.monotonic()-start<600,'Fixed fit budget exceeded'
    joblib.dump(fits,OUT/'private/fitted.joblib',compress=3)
    pd.DataFrame(cal_rows).to_csv(OUT/'calibration_predictions.csv',index=False,float_format='%.17g',lineterminator='\n')
    save(OUT/'fit_metadata.json',meta)
    save(OUT/'fit_receipt.json',dict(utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
         fitted_sha256=sha(OUT/'private/fitted.joblib'),metadata_sha256=sha(OUT/'fit_metadata.json'),calibration_sha256=sha(OUT/'calibration_predictions.csv')))
    locked();print('Frozen',len(fits),'fitted roles and calibration-selected cutoffs before evaluation in',round(time.monotonic()-start,2),'seconds.')


def fit_lock():
    locked();r=json.loads((OUT/'fit_receipt.json').read_text(encoding='utf-8'))
    for f,k in [('private/fitted.joblib','fitted_sha256'),('fit_metadata.json','metadata_sha256'),('calibration_predictions.csv','calibration_sha256')]:assert sha(OUT/f)==r[k]
    return r


def summarize(table):
    scores={};folds=[]
    for (target,cohort,rep,arm,point),part in table.groupby(['target','cohort','repeat','arm','point'],sort=True):
        m=mc.measures(part.y,part.probability)
        decision=part.probability.to_numpy()>=part.cutoff.to_numpy();y=part.y.to_numpy()
        tp=int(((y==1)&decision).sum());tn=int(((y==0)&~decision).sum());fp=int(((y==0)&decision).sum());fn=int(((y==1)&~decision).sum())
        m.update(accuracy=(tp+tn)/len(y),sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),precision=tp/(tp+fp) if tp+fp else 0.,
                 f1=2*tp/(2*tp+fp+fn),confusion=dict(tn=tn,fp=fp,fn=fn,tp=tp),cutoff_min=float(part.cutoff.min()),cutoff_max=float(part.cutoff.max()))
        fold_auc=[mc.measures(p.y,p.probability)['auc'] for _,p in part.groupby('fold')]
        m['mean_within_fold_auc']=float(np.mean(fold_auc))
        scores.setdefault(target,{}).setdefault(cohort,{}).setdefault(str(rep),{}).setdefault(arm,{})[point]=m
    comparisons=[]
    pairs=[('cohort_intercepts_sigmoid','local_sigmoid'),('cohort_intercepts','pooled')]+[(b+'_sigmoid',b) for b in BASES]
    fixed=table[table.point=='fixed_50']
    for (target,cohort),part in fixed.groupby(['target','cohort']):
        for a,b in pairs:
            aa=part[part.arm==a].sort_values(['repeat','row_index']);bb=part[part.arm==b].sort_values(['repeat','row_index'])
            assert np.array_equal(aa[['repeat','row_index','y']],bb[['repeat','row_index','y']])
            errors=pd.DataFrame(dict(row=aa.row_index.to_numpy(),delta=(aa.probability.to_numpy()-aa.y.to_numpy())**2-(bb.probability.to_numpy()-bb.y.to_numpy())**2)).groupby('row').delta.mean().to_numpy()
            rng=np.random.default_rng(SEED);boot=[errors[rng.integers(0,len(errors),len(errors))].mean() for _ in range(1000)]
            auc_delta=[scores[target][cohort][str(rep)][a]['fixed_50']['auc']-scores[target][cohort][str(rep)][b]['fixed_50']['auc'] for rep in [1,2]]
            comparisons.append(dict(target=target,cohort=cohort,arm=a,reference=b,brier_delta=float(errors.mean()),
                  conditional_brier_delta_95=np.quantile(boot,[.025,.975]).tolist(),auc_deltas_by_repeat=auc_delta))
    return dict(scope='Previously inspected populations; reduced-input local development/adaptation, not 55-input app validation.',scores=scores,comparisons=comparisons)


def evaluate():
    fit_lock();assert not (OUT/'evaluation_predictions.csv').exists(),'Refuse overwrite'
    fits=joblib.load(OUT/'private/fitted.joblib');data=mc.inputs();partition=json.loads((OUT/'partitions.json').read_text(encoding='utf-8'));rows=[]
    for s in partition:
        item=data[s['target']][s['destination']];f=fits[s['key']]
        prob=predict(f,item['x'].iloc[s['evaluation']],s['destination'])
        for arm,p in prob.items():
            for point,value in f['cutoffs'][arm].items():
                for i,v in zip(s['evaluation'],p):rows.append(dict(target=s['target'],cohort=s['destination'],repeat=s['repeat'],fold=s['fold'],arm=arm,point=point,
                     row_index=int(item['rows'][i]),y=int(item['y'][i]),probability=float(v),cutoff=value))
    table=pd.DataFrame(rows);assert not table.duplicated(['target','cohort','repeat','arm','point','row_index']).any()
    table.to_csv(OUT/'evaluation_predictions.csv',index=False,float_format='%.17g',lineterminator='\n')
    table=pd.read_csv(OUT/'evaluation_predictions.csv',float_precision='round_trip');save(OUT/'results.json',summarize(table))
    save(OUT/'evaluation_receipt.json',dict(utc=datetime.now(timezone.utc).isoformat(),predictions_sha256=sha(OUT/'evaluation_predictions.csv'),results_sha256=sha(OUT/'results.json')))
    fit_lock();print('Evaluated all frozen arms/cutoffs; no refits, thresholds changed or live promotion.')


def verify():
    fit_lock();data=mc.inputs();partition=json.loads((OUT/'partitions.json').read_text(encoding='utf-8'));assert partition==parts(data)
    fits=joblib.load(OUT/'private/fitted.joblib');cal=pd.read_csv(OUT/'calibration_predictions.csv',float_precision='round_trip');ev=pd.read_csv(OUT/'evaluation_predictions.csv',float_precision='round_trip')
    for s in partition:
        item=data[s['target']][s['destination']];f=fits[s['key']]
        for role,table in [('calibration',cal),('evaluation',ev)]:
            p=predict(f,item['x'].iloc[s[role]],s['destination'])
            if role=='calibration':sub=table[table.key==s['key']]
            else:sub=table[(table.target==s['target'])&(table.cohort==s['destination'])&(table.repeat==s['repeat'])&(table.fold==s['fold'])&(table.point=='fixed_50')]
            for arm,prob in p.items():
                saved=sub[sub.arm==arm].set_index('row_index').loc[item['rows'][s[role]]]
                assert np.array_equal(saved.y,item['y'][s[role]]) and np.allclose(saved.probability,prob,rtol=0,atol=1e-14)
                if role=='calibration' and arm!='training_prevalence':assert f['cutoffs'][arm]['target_90']==cutoff(saved.y,saved.probability,.9)
    receipt=json.loads((OUT/'evaluation_receipt.json').read_text(encoding='utf-8'))
    assert sha(OUT/'evaluation_predictions.csv')==receipt['predictions_sha256'] and sha(OUT/'results.json')==receipt['results_sha256']
    assert json.loads((OUT/'results.json').read_text(encoding='utf-8'))==summarize(ev)
    print('PASS: all raw/code/protocol/history hashes, disjoint roles, frozen calibration/cutoffs, fitted prediction replay and metrics.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','fit','evaluate','verify'])
    {'prepare':prepare,'fit':fit,'evaluate':evaluate,'verify':verify}[p.parse_args().stage]()
