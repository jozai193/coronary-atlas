"""Independent saved-output arithmetic and three-role audit; never refits."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score


def verify():
    out=ROOT/'ml/experiments/cohort_calibration_v1'
    prep=json.loads((out/'prepared.json').read_text(encoding='utf-8'))
    for group in ['dependencies','raw_hashes','historical']:
        for name,value in prep[group].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value,name
    partitions=json.loads((out/'partitions.json').read_text(encoding='utf-8'))
    metadata={m['key']:m for m in json.loads((out/'fit_metadata.json').read_text(encoding='utf-8'))}
    cal=pd.read_csv(out/'calibration_predictions.csv',float_precision='round_trip')
    table=pd.read_csv(out/'evaluation_predictions.csv',float_precision='round_trip')
    results=json.loads((out/'results.json').read_text(encoding='utf-8'))
    assert not table.duplicated(['target','cohort','repeat','arm','point','row_index']).any()
    assert not cal.duplicated(['key','arm','row_index']).any()
    assert np.isfinite(table.probability).all() and table.probability.between(0,1).all()
    count=0
    for t,cohorts in results['scores'].items():
        for c,reps in cohorts.items():
            n=prep['cohorts'][t][c]['n']
            for repeat,arms in reps.items():
                for arm,points in arms.items():
                    for point,m in points.items():
                        p=table[(table.target==t)&(table.cohort==c)&(table.repeat==int(repeat))&(table.arm==arm)&(table.point==point)]
                        assert len(p)==n and p.row_index.is_unique
                        y=p.y.to_numpy();prob=p.probability.to_numpy();d=prob>=p.cutoff.to_numpy()
                        tp=int(((y==1)&d).sum());fn=int(((y==1)&~d).sum());fp=int(((y==0)&d).sum());tn=int(((y==0)&~d).sum())
                        assert m['confusion']==dict(tn=tn,fp=fp,fn=fn,tp=tp)
                        values=dict(auc=roc_auc_score(y,prob),average_precision=average_precision_score(y,prob),
                            brier=np.mean((prob-y)**2),log_loss=-np.mean(y*np.log(np.clip(prob,1e-15,1-1e-15))+(1-y)*np.log(np.clip(1-prob,1e-15,1-1e-15))),
                            accuracy=(tp+tn)/n,sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),
                            precision=tp/(tp+fp) if tp+fp else 0.,f1=2*tp/(2*tp+fp+fn),
                            mean_within_fold_auc=np.mean([roc_auc_score(f.y,f.probability) for _,f in p.groupby('fold')]))
                        for key,value in values.items():assert abs(value-m[key])<1e-12,(t,c,repeat,arm,point,key)
                        count+=1
    # Check raw membership and duplicate exclusion independently of the runner's parts().
    from ml.multicohort import inputs
    data=inputs()
    for spec in partitions:
        c=data[spec['target']];dest=spec['destination'];item=c[dest]
        train=set(spec['training'][dest]);cal_ix=set(spec['calibration']);ev_ix=set(spec['evaluation'])
        assert not (train&cal_ix or train&ev_ix or cal_ix&ev_ix)
        assert train|cal_ix|ev_ix==set(range(len(item['y'])))
        blocked=set(item['fingerprints'][list(cal_ix|ev_ix)])
        for name,ix in spec['training'].items():assert not blocked&set(c[name]['fingerprints'][ix])
        for arm,points in metadata[spec['key']]['cutoffs'].items():
            p=cal[(cal.key==spec['key'])&(cal.arm==arm)].set_index('row_index').loc[item['rows'][spec['calibration']]]
            assert np.array_equal(p.y,item['y'][spec['calibration']])
            assert points['fixed_50']==.5
            if arm!='training_prevalence':
                positives=np.sort(p.loc[p.y==1,'probability'].to_numpy())[::-1]
                selected=positives[int(np.ceil(.9*len(positives)))-1]
                assert points['target_90']==selected
                assert (positives>=selected).mean()>=.9
            q=table[(table.target==spec['target'])&(table.cohort==dest)&(table.repeat==spec['repeat'])&(table.fold==spec['fold'])&(table.arm==arm)]
            for point,threshold in points.items():
                s=q[q.point==point].set_index('row_index').loc[item['rows'][spec['evaluation']]]
                assert np.array_equal(s.y,item['y'][spec['evaluation']]) and (s.cutoff==threshold).all()
    print(f'PASS: {count} independently reproduced metric groups; {len(partitions)} disjoint three-role splits, duplicate exclusions and calibration-only thresholds.')


if __name__=='__main__':verify()
