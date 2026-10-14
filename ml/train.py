"""Run nested cross-validation then refit selected configurations. CPU only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import platform
import importlib.metadata
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from ml.schema import *
from ml.preprocessing import pipeline, check_features
from ml.evaluate import metrics, curves

CANDIDATES = [('logistic', .03), ('logistic', .3), ('forest', .1), ('boosting', .1)]


def select(X,y,seed):
    cv = StratifiedKFold(3,shuffle=True,random_state=seed)
    scores = []
    for kind, strength in CANDIDATES:
        s = cross_val_score(pipeline(kind,strength), X,y,cv=cv,scoring='roc_auc',n_jobs=1)
        scores.append(dict(kind=kind,strength=strength,mean_auc=float(s.mean()),fold_auc=s.tolist()))
    best = max(scores,key=lambda x:x['mean_auc'])
    return best, scores


def main():
    df = read_data()
    X = df[FEATURES]
    check_features(X.columns)
    output = ROOT/'ml/metrics'
    output.mkdir(exist_ok=True)
    models = ROOT/'models'
    models.mkdir(exist_ok=True)
    results = {}
    artifacts = {}
    for target, column in TARGETS.items():
        y = (df[column] == ('CAD' if target=='cad' else 'Stenotic')).astype(int)
        cv = StratifiedKFold(5,shuffle=True,random_state=SEED)
        p = np.zeros(len(y)); baseline = np.zeros(len(y)); fold_ids = np.zeros(len(y),int)
        folds=[]
        for i,(train,test) in enumerate(cv.split(X,y)):
            best,scores = select(X.iloc[train],y.iloc[train],SEED+i)
            fitted = pipeline(best['kind'],best['strength']).fit(X.iloc[train],y.iloc[train])
            p[test] = fitted.predict_proba(X.iloc[test])[:,1]
            baseline[test] = y.iloc[train].mean()
            fold_ids[test] = i
            folds.append(dict(fold=i,train_indices=train.tolist(),test_indices=test.tolist(),selected=best,candidates=scores,metrics=metrics(y.iloc[test],p[test])))
            print(target,'outer fold',i+1,best['kind'],'AUC',round(folds[-1]['metrics']['roc_auc'],3),flush=True)
        best,scores = select(X,y,SEED)
        fitted = pipeline(best['kind'],best['strength']).fit(X,y)
        transformed = fitted.named_steps['preprocess'].transform(X)
        rng = np.random.default_rng(SEED)
        background = transformed[rng.choice(len(X),size=100,replace=False)]
        artifact = dict(pipeline=fitted,background=background,features=FEATURES,target=target,kind=best['kind'])
        path = models/f'{target}.joblib'
        joblib.dump(artifact,path,compress=3)
        artifacts[target] = dict(file=path.name,sha256=digest(path),selected=best,parameters=fitted.named_steps['model'].get_params())
        pd.DataFrame(dict(row_index=np.arange(len(y)),fold=fold_ids,y=y,p=p,baseline=baseline)).to_csv(output/f'{target}_oof.csv',index=False)
        std = {k:float(np.std([f['metrics'][k] for f in folds],ddof=1)) for k in ['accuracy','precision','recall','f1','roc_auc','specificity','brier']}
        results[target] = dict(metrics=metrics(y,p),baseline=metrics(y,baseline),fold_sd=std,folds=folds,curves=curves(y,p),final_selection=best,full_data_candidates=scores)
        # Conditional bootstrap of fixed OOF predictions, not refitted-model confidence.
        aucs=[]
        for _ in range(1000):
            idx = rng.integers(0,len(y),len(y))
            if len(np.unique(y.iloc[idx]))==2:
                from sklearn.metrics import roc_auc_score
                aucs.append(roc_auc_score(y.iloc[idx],p[idx]))
        results[target]['auc_bootstrap_interval'] = np.quantile(aucs,[.025,.975]).tolist()
        results[target]['interval_note'] = 'Descriptive 95% bootstrap of fixed OOF predictions; does not include refitting/selection uncertainty.'
        print(target,'OOF',results[target]['metrics'],flush=True)
    mismatch = (df.Cath=='CAD') != (df[['LAD','LCX','RCA']]=='Stenotic').any(axis=1)
    sensitivity={}
    # Prespecified logistic-only diagnostic; not a second optimizable headline score.
    for target,column in TARGETS.items():
        y = (df[column] == ('CAD' if target=='cad' else 'Stenotic')).astype(int)
        sensitivity[target]={}
        for label,mask in [('all',np.ones(len(y),bool)),('consistent_only',~mismatch)]:
            pp=cross_val_predict(pipeline('logistic',.03),X.loc[mask],y.loc[mask],cv=StratifiedKFold(5,shuffle=True,random_state=SEED),method='predict_proba')[:,1]
            sensitivity[target][label]=metrics(y.loc[mask],pp)
    write_json(output/'sensitivity.json',sensitivity)
    write_json(output/'evaluation.json',dict(seed=SEED,method='5 outer / 3 inner stratified folds; inner ROC-AUC selection',threshold=.5,targets=results))
    versions = {p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','scipy','shap','joblib']}
    write_json(models/'metadata.json',dict(seed=SEED,rows=len(df),features=FEATURES,prohibited=sorted(PROHIBITED),python=platform.python_version(),versions=versions,raw_sha256=digest(ROOT/'data/raw/extention of Z-Alizadeh sani dataset.xlsx'),artifacts=artifacts,feature_schema=feature_metadata(df)))
    print('Saved evaluation and model metadata.',flush=True)


if __name__=='__main__':
    main()
