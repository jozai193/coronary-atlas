"""Nested cutoff diagnostics on existing training rows only. Never reads test labels."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.develop_confirm import (ROOT, RAW, OUT as PREVIOUS, NUM, candidates, load_inputs,
    read_json, verify_prepared, cutoff90, confusion)
from ml.schema import write_json, digest
from ml.evaluate import metrics

OUT=ROOT/'ml/experiments/confirm_error_followup_v1'
PROTOCOL=ROOT/'docs/confirm_error_followup_protocol.md'
CORE=['sex','htn','dm','chol','famhx','smokecurrent']


def run():
    if OUT.exists(): raise RuntimeError('Preserve existing follow-up outputs.')
    verify_prepared()
    oldhash=digest(PREVIOUS/'evidence_manifest.json')
    for file,sha in read_json(PREVIOUS/'evidence_manifest.json').items():
        assert digest(PREVIOUS/file)==sha
    manifest=read_json(PREVIOUS/'fit_manifest.json')
    _,x,_,_=load_inputs()
    # Read labels ONLY from prior training-row evidence: original fit did not export training labels.
    train_union=set()
    for t in ['cad','lad','lcx','rca']: train_union.update(manifest['experiments']['clinical_available_'+t]['train_rows'])
    # skiprows prevents reading records outside the training union into the label frame.
    selected=sorted(train_union)
    labels=pd.read_excel(RAW,usecols=['stenosis_50','lad_50','lcx_50','rca_50'],
                         skiprows=lambda row: row>0 and row-1 not in train_union)
    labels.index=selected
    headers=list(pd.read_excel(RAW,nrows=0).columns)
    possible=[c for c in headers if any(s in str(c).lower() for s in ['site','center','centre','date','year','hospital','country'])]
    OUT.mkdir(parents=True)
    write_json(OUT/'frozen.json',{'protocol':digest(PROTOCOL),'runner':digest(Path(__file__)),
        'previous_manifest':oldhash,'possible_group_or_time_headers':possible,
        'note':'Headers only; no site/time semantics inferred. No test evaluation.'})
    result={}
    for target,label in dict(cad='stenosis_50',lad='lad_50',lcx='lcx_50',rca='rca_50').items():
        ix=manifest['experiments']['clinical_available_'+target]['train_rows']
        xx=x.loc[ix]; y=labels.loc[ix,label].to_numpy(dtype=int)
        family=candidates(True)
        methods={'full_linear':family['logistic'],'full_spline':family['splines']}
        for name,base in [('core_linear',family['logistic']),('core_spline',family['splines'])]:
            model=clone(base); prep=model.steps[0][1]
            prep.transformers=[(n,tr,CORE if n=='categorical' else cols) for n,tr,cols in prep.transformers]
            methods[name]=model
        names=list(methods)+['full_average','core_average']
        pred={n:np.zeros(len(y)) for n in names}; decisions={n:np.zeros(len(y)) for n in names}
        folds=[]
        for fold,(tr,va) in enumerate(StratifiedKFold(3,shuffle=True,random_state=20261009).split(xx,y)):
            inner={}; outer={}
            for name,model in methods.items():
                inner[name]=cross_val_predict(clone(model),xx.iloc[tr],y[tr],
                    cv=StratifiedKFold(3,shuffle=True,random_state=20261009),method='predict_proba')[:,1]
                outer[name]=clone(model).fit(xx.iloc[tr],y[tr]).predict_proba(xx.iloc[va])[:,1]
            for prefix in ['full','core']:
                inner[prefix+'_average']=(inner[prefix+'_linear']+inner[prefix+'_spline'])/2
                outer[prefix+'_average']=(outer[prefix+'_linear']+outer[prefix+'_spline'])/2
            thresholds={}
            for name in names:
                threshold=cutoff90(y[tr],inner[name]); thresholds[name]=threshold
                pred[name][va]=outer[name]; decisions[name][va]=outer[name]>=threshold
            folds.append({'train':[ix[i] for i in tr],'validation':[ix[i] for i in va],'cutoffs':thresholds})
        reports={}
        reference=metrics(y,pred['full_spline'])
        for name in names:
            m=metrics(y,pred[name]); m['nested_cutoff']=confusion(y,decisions[name],.5)
            m['screen_pass']=bool(m['brier']<=reference['brier']-.002 and m['roc_auc']>=reference['roc_auc']-.01)
            groups={}
            for gn,mask in {'age_under60':xx.age.lt(60).to_numpy(),'age_60plus':xx.age.ge(60).to_numpy(),
                'numeric_missing':xx[NUM].isna().any(axis=1).to_numpy(),'numeric_complete':xx[NUM].notna().all(axis=1).to_numpy(),
                'sex_code0':xx.sex.eq(0).to_numpy(),'sex_code1':xx.sex.eq(1).to_numpy()}.items():
                groups[gn]={'rows':int(mask.sum()),'positives':int(y[mask].sum())}
                if mask.sum()>=100 and len(np.unique(y[mask]))==2:
                    groups[gn].update(metrics(y[mask],pred[name][mask]))
                    groups[gn]['nested_cutoff']=confusion(y[mask],decisions[name][mask],.5)
            m['subgroups']=groups;reports[name]=m
        result[target]={'rows':len(y),'methods':reports,'folds':folds}
        pd.DataFrame({'row_index':ix,'observed':y,**pred,**{n+'_decision':v for n,v in decisions.items()}}).to_csv(OUT/f'{target}_training_oof.csv',index=False)
        print(target,{n:round(v['brier'],4) for n,v in reports.items()},flush=True)
    assert digest(PREVIOUS/'evidence_manifest.json')==oldhash
    verify_prepared()
    write_json(OUT/'results.json',result)
    write_json(OUT/'evidence_manifest.json',{p.name:digest(p) for p in OUT.iterdir() if p.is_file()})
    lines=['# Focused training-only prediction-error audit','',
        'Executed 8 October 2026. All comparisons use only the existing CONFIRM development training partition. No new test evaluation or app promotion. Cutoffs use nested training-only OOF scores; validation labels never choose their own cutoff.','',
        '| Target | Method | AUC | Brier | Nested-cutoff recall | Specificity | FP / FN | Improvement screen |',
        '|---|---|---:|---:|---:|---:|---:|---|']
    for target,data in result.items():
        for name,m in data['methods'].items():
            c=m['nested_cutoff'];lines.append(f"| {target.upper()} | {name} | {m['roc_auc']:.3f} | {m['brier']:.4f} | {c['sensitivity']:.1%} | {c['specificity']:.1%} | {c['false_positives']} / {c['missed_cases']} | {m['screen_pass']} |")
    lines+=['','## Site/time availability','',f'Candidate headers: {possible}. Header names alone do not establish authoritative site definitions or measurement dates; no site/time split was claimed.',
        '', '## Interpretation','',
        'The improvement screen requires Brier improvement >=.002 and AUC loss <=.01 against full spline. It is an exploratory engineering screen, not statistical significance. All unsuccessful variants are retained. Subgroup errors are saved in results.json. OOF error patterns cannot establish causes of error or clinical fairness. Missing-input imputation does not recover unavailable measurements.',
        '', 'Original test outcomes remain known from the previous experiment; this training-only work preserves them and makes no fresh external claim. No pipeline was promoted. Further changes should require a specific data-quality or representation hypothesis and new evaluation evidence.',
        '', 'Reproduce with `python scripts/confirm_error_followup.py`; refuses overwrite. See `confirm_error_followup_protocol.md` and `ml/experiments/confirm_error_followup_v1/`.']
    (ROOT/'docs/confirm_error_followup_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':
    with threadpool_limits(limits=2): run()
