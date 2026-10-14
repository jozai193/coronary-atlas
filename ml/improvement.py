"""Bounded exploratory benchmark; never overwrites production artifacts.

Protocol: docs/model_improvement_protocol.md. Every fitted transform, calibrator
and cutoff is confined to outer training data. Repeated CV is not external data.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import time
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold
from threadpoolctl import threadpool_limits
from ml.schema import ROOT, FEATURES, TARGETS, SEED, read_data, digest, write_json
from ml.preprocessing import pipeline, check_features
from ml.evaluate import metrics

SEEDS = [20261007, 20261108]
BASE = ['logistic_003', 'logistic_03', 'forest', 'boosting']
CANDIDATES = BASE + ['logistic_0003', 'logistic_1', 'balanced_logistic_003',
                     'balanced_logistic_03', 'balanced_forest', 'extra', 'balanced_extra']
OUT = ROOT/'ml/experiments/improvement_v1'


def candidate(name):
    if 'logistic' in name:
        c = {'0003': .003, '003': .03, '03': .3, '1': 1.}[name.split('_')[-1]]
        estimator = pipeline('logistic', c)
        if name.startswith('balanced'):
            estimator.set_params(model__class_weight='balanced')
    elif name in ('forest', 'boosting'):
        estimator = pipeline(name)
    else:
        estimator = pipeline('forest')
        if name == 'balanced_forest':
            model = RandomForestClassifier(n_estimators=160, min_samples_leaf=3,
                max_features='sqrt', class_weight='balanced', n_jobs=1, random_state=SEED)
        else:
            model = ExtraTreesClassifier(n_estimators=160, min_samples_leaf=4,
                max_features='sqrt', class_weight='balanced' if name.startswith('balanced') else None,
                n_jobs=1, random_state=SEED)
        estimator.set_params(model=model)
    return estimator


def threshold_counts(y, p, threshold):
    """A threshold may be scalar or the per-row training-selected cutoffs."""
    pred = np.asarray(p) >= np.asarray(threshold)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    recall = tp/(tp+fn); specificity = tn/(tn+fp)
    return dict(threshold=float(threshold) if np.ndim(threshold)==0 else 'outer-training-selected',
                accuracy=float((tp+tn)/len(y)), precision=float(tp/max(tp+fp,1)),
                recall=float(recall), specificity=float(specificity),
                balanced_accuracy=float((recall+specificity)/2),
                f1=float(2*tp/max(2*tp+fp+fn,1)),
                confusion_matrix=[[int(tn),int(fp)],[int(fn),int(tp)]])


def choose_threshold(y, p, objective):
    """Train-only policy; tie-breaks fixed before viewing any outer outcome."""
    thresholds = np.unique(np.r_[0., .5, p, np.nextafter(np.max(p), np.inf)])
    options = [threshold_counts(y, p, t) for t in thresholds]
    if objective == 'recall80':
        eligible = [o for o in options if o['recall'] >= .8]
        chosen = max(eligible, key=lambda o:(o['specificity'], -abs(o['threshold']-.5)))
    elif objective == 'balanced':
        chosen = max(options, key=lambda o:(o['balanced_accuracy'], -abs(o['threshold']-.5)))
    else:
        raise ValueError(objective)
    return chosen


def inner_predictions(X, y, splits):
    scores = {}; probabilities = {}
    for name in CANDIDATES:
        p = np.zeros(len(y)); aucs = []
        for train, test in splits:
            fitted = candidate(name).fit(X.iloc[train], y.iloc[train])
            p[test] = fitted.predict_proba(X.iloc[test])[:,1]
            aucs.append(roc_auc_score(y.iloc[test], p[test]))
        scores[name] = dict(mean_auc=float(np.mean(aucs)), fold_auc=[float(x) for x in aucs])
        probabilities[name] = p
    return scores, probabilities


def evaluate_target(target, df):
    X = df[FEATURES]; check_features(X.columns)
    y = (df[TARGETS[target]] == ('CAD' if target=='cad' else 'Stenotic')).astype(int)
    repeats = []
    for repeat, seed in enumerate(SEEDS):
        table = pd.DataFrame(dict(row_index=np.arange(len(y)), y=y, fold=-1))
        folds = []
        for fold, (train, test) in enumerate(StratifiedKFold(5,shuffle=True,random_state=seed).split(X,y)):
            start=time.perf_counter()
            xt, yt = X.iloc[train], y.iloc[train]
            inner = list(StratifiedKFold(3,shuffle=True,random_state=seed+fold).split(xt,yt))
            scores, oofs = inner_predictions(xt, yt, inner)
            choices={'baseline':max(BASE,key=lambda n:scores[n]['mean_auc']),
                     'expanded':max(CANDIDATES,key=lambda n:scores[n]['mean_auc'])}
            log=dict(fold=fold,train_indices=train.tolist(),test_indices=test.tolist(),
                inner_splits=[dict(train_indices=train[a].tolist(),test_indices=train[b].tolist()) for a,b in inner],
                candidates=scores,selected=choices,cutoffs={})
            table.loc[test,'fold']=fold
            fitted_cache={}
            for method,name in choices.items():
                if name not in fitted_cache:
                    fitted_cache[name]=candidate(name).fit(xt,yt)
                pp=fitted_cache[name].predict_proba(X.iloc[test])[:,1]
                table.loc[test,method]=pp
                log['cutoffs'][method]={}
                for policy in ['balanced','recall80']:
                    chosen=choose_threshold(yt,oofs[name],policy)
                    log['cutoffs'][method][policy]=chosen
                    table.loc[test,f'{method}_{policy}_threshold']=chosen['threshold']
            calibrated=CalibratedClassifierCV(candidate(choices['expanded']),method='sigmoid',cv=inner,ensemble=True,n_jobs=1).fit(xt,yt)
            table.loc[test,'calibrated']=calibrated.predict_proba(X.iloc[test])[:,1]
            folds.append(log)
            print(target,repeat+1,fold+1,choices,'seconds',round(time.perf_counter()-start,1),flush=True)
        summaries={}
        for method in ['baseline','expanded','calibrated']:
            pp=table[method].to_numpy()
            summaries[method]=dict(metrics=metrics(y,pp),average_precision=float(average_precision_score(y,pp)),
                                   policies={'fixed':threshold_counts(y,pp,.5)})
            if method!='calibrated':
                for policy in ['balanced','recall80']:
                    summaries[method]['policies'][policy]=threshold_counts(y,pp,table[f'{method}_{policy}_threshold'].to_numpy())
        table.to_csv(OUT/f'{target}_repeat_{repeat+1}.csv',index=False)
        repeats.append(dict(seed=seed,folds=folds,summary=summaries))
        write_json(OUT/f'{target}.json',dict(target=target,repeats=repeats,complete=False))
        print(target,'repeat',repeat+1,{k:{m:round(v['metrics'][m],4) for m in ['roc_auc','brier','recall','specificity']} for k,v in summaries.items()},flush=True)
    mean={method:{m:float(np.mean([r['summary'][method]['metrics'][m] for r in repeats]))
                  for m in ['roc_auc','brier','recall','specificity','precision','f1','accuracy']}
          for method in ['baseline','expanded','calibrated']}
    auc_deltas=[r['summary']['expanded']['metrics']['roc_auc']-r['summary']['baseline']['metrics']['roc_auc'] for r in repeats]
    eligible=(np.mean(auc_deltas)>=.015 and min(auc_deltas)>=0 and mean['expanded']['brier']-mean['baseline']['brier']<=.005)
    calibration_eligible=(mean['expanded']['brier']-mean['calibrated']['brier']>=.005 and all(r['summary']['calibrated']['metrics']['roc_auc']-r['summary']['expanded']['metrics']['roc_auc']>=-.01 for r in repeats))
    result=dict(target=target,repeats=repeats,mean_metrics=mean,raw_candidate_eligible=bool(eligible),
                calibration_candidate_eligible=bool(calibration_eligible),complete=True)
    write_json(OUT/f'{target}.json',result)
    return result


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    df=read_data()
    write_json(OUT/'run_manifest.json',dict(protocol_sha256=digest(ROOT/'docs/model_improvement_protocol.md'),
        code_sha256=digest(Path(__file__)),raw_sha256=digest(ROOT/'data/raw/extention of Z-Alizadeh sani dataset.xlsx'),
        seeds=SEEDS,candidates=CANDIDATES,production_metadata_sha256=digest(ROOT/'models/metadata.json'),
        warning='Exploratory repeated internal validation of reused data. Not external validation.'))
    results={}
    with threadpool_limits(limits=1):
        for target in TARGETS:
            path=OUT/f'{target}.json'
            if path.exists() and json.loads(path.read_text()).get('complete'):
                results[target]=json.loads(path.read_text())
            else:
                results[target]=evaluate_target(target,df)
    write_json(OUT/'summary.json',{k:{n:v[n] for n in ['mean_metrics','raw_candidate_eligible','calibration_candidate_eligible']} for k,v in results.items()})
    print(json.dumps(json.loads((OUT/'summary.json').read_text()),indent=2),flush=True)


if __name__=='__main__':main()
