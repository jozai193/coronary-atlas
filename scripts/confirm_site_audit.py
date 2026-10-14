"""Leave-site-code-out audit on development training patients only."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import brier_score_loss
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.develop_confirm import (ROOT,RAW,OUT as OLD,read_json,verify_prepared,load_inputs,
    LABELS,candidates,calibrator,logits,cutoff90,confusion)
from ml.evaluate import metrics
from ml.schema import digest,write_json
OUT=ROOT/'ml/experiments/confirm_site_v1'
PROTOCOL=ROOT/'docs/confirm_site_protocol.md'

def run():
    if OUT.exists():raise RuntimeError('Frozen site audit exists.')
    verify_prepared();manifest=read_json(OLD/'fit_manifest.json')
    old={file:digest(OLD/file) for file in read_json(OLD/'evidence_manifest.json')}
    _,x,_,_=load_inputs()
    union=set()
    for target in LABELS:union.update(manifest['experiments']['clinical_available_'+target]['train_rows'])
    d=pd.read_excel(RAW,usecols=['site',*LABELS.values()],skiprows=lambda row:row>0 and row-1 not in union)
    d.index=sorted(union)
    assert d.site.notna().all()
    OUT.mkdir(parents=True)
    write_json(OUT/'frozen.json',{'runner':digest(Path(__file__)),'protocol':digest(PROTOCOL),
        'previous_manifest':digest(OLD/'evidence_manifest.json'),'groups':'Opaque workbook site codes, identities unverified'})
    results={}
    for target,label in LABELS.items():
        ix=manifest['experiments']['clinical_available_'+target]['train_rows'];data=d.loc[ix]
        predictions=[];folds=[]
        for site in sorted(data.site.unique()):
            validation=data.index[data.site==site].tolist();others=data.index[data.site!=site].tolist()
            train,cal=train_test_split(others,test_size=.2,random_state=20261008,stratify=data.loc[others,label])
            model=candidates(True)['splines'].fit(x.loc[train],data.loc[train,label].astype(int))
            pc=model.predict_proba(x.loc[cal])[:,1];yc=data.loc[cal,label].to_numpy(dtype=int)
            fitted_cal=calibrator(pc,yc);pc=fitted_cal.predict_proba(logits(pc))[:,1];cutoff=cutoff90(yc,pc)
            raw=model.predict_proba(x.loc[validation])[:,1];p=fitted_cal.predict_proba(logits(raw))[:,1]
            y=data.loc[validation,label].to_numpy(dtype=int)
            summary={'site_code':int(site),'rows':len(y),'positives':int(y.sum()),'brier':float(brier_score_loss(y,p)),
                'fit_rows':train,'calibration_rows':cal,'validation_rows':validation,'cutoff':cutoff}
            if len(np.unique(y))==2:summary.update(metrics(y,p));summary['operating_point']=confusion(y,p,cutoff)
            else:summary['auc_unavailable']='Single-class validation site'
            folds.append(summary)
            predictions.append(pd.DataFrame({'row_index':validation,'site_code':int(site),'observed':y,
                'probability':p,'decision':(p>=cutoff).astype(int)}))
        allp=pd.concat(predictions,ignore_index=True);allp.to_csv(OUT/f'{target}_oof.csv',index=False)
        results[target]={'pooled':metrics(allp.observed,allp.probability),
            'operating_point':confusion(allp.observed,allp.decision,.5),'folds':folds}
        print(target,results[target]['pooled']['roc_auc'],results[target]['pooled']['brier'],flush=True)
    for file,sha in old.items():assert digest(OLD/file)==sha
    verify_prepared();write_json(OUT/'results.json',results)
    write_json(OUT/'evidence_manifest.json',{p.name:digest(p) for p in OUT.iterdir() if p.is_file()})
    lines=['# Leave-site-code-out robustness audit','',
        'Training partition only; fixed spline model, separate other-site calibration, 12 opaque site codes. Not fresh independent validation. Site code never enters predictors. Test and previous calibration patients excluded.','',
        '| Target | Pooled AUC | Brier | Sensitivity | Specificity | FP / FN |', '|---|---:|---:|---:|---:|---:|']
    for t,r in results.items():
        m=r['pooled'];c=r['operating_point'];lines.append(f"| {t.upper()} | {m['roc_auc']:.3f} | {m['brier']:.3f} | {c['sensitivity']:.1%} | {c['specificity']:.1%} | {c['false_positives']} / {c['missed_cases']} |")
    lines+=['','## Per-code results','','| Target | Site code | Rows | Positives | AUC | Brier |','|---|---:|---:|---:|---:|---:|']
    for t,r in results.items():
        for f in r['folds']:lines.append(f"| {t.upper()} | {f['site_code']} | {f['rows']} | {f['positives']} | {f.get('roc_auc',float('nan')):.3f} | {f['brier']:.3f} |")
    lines+=['','## Interpretation','',
        'The held-out code is absent from fitting and calibration. Pooled AUC blends within- and between-site discrimination; per-code values and class counts are necessary context. Small site groups have unstable estimates. No code-to-hospital mapping was verified. This uses sites already present in known development evidence and does not supply pristine independent validation. Calibration and training sizes differ from the random-fold follow-up, so a difference is not a causal estimate of site shift.',
        '', 'Dates inspected were lipid-panel and intervention/event dates, not a verified universal baseline enrollment date. No temporal split or future-event task was invented. All prior app and experiment artifacts remain unchanged.']
    (ROOT/'docs/confirm_site_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':
    with threadpool_limits(limits=2):run()
