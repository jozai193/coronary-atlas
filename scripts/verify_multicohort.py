"""Independent saved-receipt audit; no fitting or runner metric reuse."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import json
import hashlib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score


def verify(folder=ROOT/'output/research/multicohort_v1'):
    prep=json.loads((folder/'prepared.json').read_text(encoding='utf-8'))
    for group in ['raw_hashes','dependencies','historical']:
        for name,expected in prep[group].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    parts=json.loads((folder/'partitions.json').read_text(encoding='utf-8'))
    table=pd.read_csv(folder/'predictions.csv',float_precision='round_trip')
    result=json.loads((folder/'results.json').read_text(encoding='utf-8'))
    assert not table.duplicated(['target','cohort','design','arm','row_index']).any()
    assert np.isfinite(table.probability).all() and table.probability.between(0,1).all()
    expected_groups=0
    for target,cohorts in result['scores'].items():
        for cohort,designs in cohorts.items():
            n=prep['audit'][target][cohort]['n']
            for design,arms in designs.items():
                for arm,m in arms.items():
                    part=table[(table.target==target)&(table.cohort==cohort)&(table.design==design)&(table.arm==arm)]
                    assert len(part)==n and part.row_index.is_unique
                    y=part.y.to_numpy();p=part.probability.to_numpy();d=p>=.5
                    tp=int(((y==1)&d).sum());fn=int(((y==1)&~d).sum())
                    fp=int(((y==0)&d).sum());tn=int(((y==0)&~d).sum())
                    assert m['confusion']==dict(tn=tn,fp=fp,fn=fn,tp=tp)
                    assert m['n']==n and m['positives']==int(y.sum())
                    values=dict(auc=roc_auc_score(y,p),average_precision=average_precision_score(y,p),
                                brier=np.mean((y-p)**2),log_loss=-np.mean(y*np.log(np.clip(p,1e-15,1-1e-15))+(1-y)*np.log(np.clip(1-p,1e-15,1-1e-15))),
                                sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),accuracy=(tp+tn)/n,
                                precision=tp/(tp+fp) if tp+fp else 0.,f1=2*tp/(2*tp+fp+fn))
                    for key,value in values.items():assert abs(value-m[key])<1e-12,(target,cohort,design,arm,key)
                    expected_groups+=1
    for spec in parts:
        test=set(spec['test'])
        if spec['design']=='transport':assert spec['destination'] not in spec['training']
        else:assert not test&set(spec['training'][spec['destination']])
    for target,cohort in table[['target','cohort']].drop_duplicates().itertuples(index=False,name=None):
        specs=[s for s in parts if s['target']==target and s['destination']==cohort and s['design']=='augmentation']
        ix=[i for s in specs for i in s['test']]
        assert len(ix)==len(set(ix))==prep['audit'][target][cohort]['n']
    print(f'PASS: {expected_groups} independent metric groups, {len(parts)} held-out role definitions, exact one-time evaluation, no target rows in training roles.')


if __name__=='__main__':verify()
