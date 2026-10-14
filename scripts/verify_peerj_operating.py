"""Independent read-only threshold, arithmetic and preprocessing verification."""
from pathlib import Path
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import joblib
import numpy as np
import pandas as pd
from scipy.special import expit,logit
from sklearn.metrics import roc_auc_score,log_loss
from ml.peerj_external import RAW,RAW_SHA,NUM,CAT,FEATURES,map_external

folder=ROOT/'output/research/peerj_operating_v1'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((folder/'evidence_manifest.json').read_text())
for name,expected in manifest['files'].items(): assert digest(folder/name)==expected
prep=json.loads((folder/'prepared.json').read_text())
assert digest(ROOT/'docs/peerj_operating_protocol.md')==prep['protocol_sha256']
for name,expected in prep['history'].items(): assert digest(ROOT/name)==expected
fit=json.loads((folder/'fit_manifest.json').read_text())
assert digest(folder/'prepared.json')==fit['prepared_sha256']
for name,expected in fit['files'].items(): assert digest(folder/name)==expected
rows=pd.read_csv(folder/'predictions.csv',float_precision='round_trip')
cal=pd.read_csv(folder/'calibration_predictions.csv',float_precision='round_trip')
parts=json.loads((folder/'partitions.json').read_text())
fitted=joblib.load(folder/'fitted.joblib')
results=json.loads((folder/'results.json').read_text())
base=pd.read_csv(ROOT/'output/research/peerj_v1/external_predictions.csv',float_precision='round_trip')
methods=['source','source_sigmoid','local','local_sigmoid']
targets=dict(fixed_50=None,target_80=.8,target_90=.9,target_95=.95)
for rep in (1,2):
    frame=rows[rows.repeat==rep].sort_values('row_index')
    assert frame.row_index.tolist()==list(range(553))
    np.testing.assert_array_equal(frame.y,base.y)
    for method in methods+['constant']:
        y=frame.y.to_numpy();p=frame[method].to_numpy()
        saved=results['repeats'][str(rep)]['probabilities'][method]
        for k,v in dict(auc=roc_auc_score(y,p),brier=np.mean((y-p)**2),log_loss=log_loss(y,p),
                        mean_within_fold_auc=np.mean([roc_auc_score(g.y,g[method]) for _,g in frame.groupby('fold')])).items():
            assert np.isclose(v,saved[k],atol=1e-12,rtol=0)
        if method=='constant': continue
        for point in targets:
            d=frame[f'{method}__{point}'].to_numpy(bool)
            confusion=dict(tn=int(sum((y==0)&~d)),fp=int(sum((y==0)&d)),fn=int(sum((y==1)&~d)),tp=int(sum((y==1)&d)))
            got=results['repeats'][str(rep)]['operating'][method][point]
            assert confusion==got['confusion']
            assert got['sensitivity']==confusion['tp']/201
            assert got['specificity']==confusion['tn']/352
for part in parts:
    t,c,e=map(set,(part['train'],part['calibration'],part['test']))
    assert not t&c and not t&e and not c&e and t|c|e==set(range(553))
    cc=cal[cal.key==part['key']];ff=rows[(rows.repeat==part['repeat'])&(rows.fold==part['fold'])]
    assert cc.row_index.tolist()==part['calibration'] and set(ff.row_index)==e
    f=fitted[part['key']]
    info=next(d for d in fit['details'] if d['key']==part['key'])
    assert info['cutoffs']==f['cutoffs']
    assert f['constant']==base.y.iloc[part['train']].mean()
    np.testing.assert_array_equal(ff.constant,np.full(len(ff),f['constant']))
    for method in methods:
        for point,target in targets.items():
            threshold=f['cutoffs'][method][point]
            if target is None: assert threshold==.5
            else:
                positive=cc.loc[cc.y==1,method].to_numpy()
                feasible=[float(v) for v in np.unique(positive) if np.mean(positive>=v)>=target]
                assert threshold==max(feasible), 'Threshold must be largest feasible calibration score'
            np.testing.assert_array_equal(ff[f'{method}__{point}'],ff[method]>=threshold)
    for frame in (cc,ff):
        for method in ('source','local'):
            est=f[method+'_sigmoid']
            p=expit(est.intercept_[0]+est.coef_[0,0]*logit(np.clip(frame[method],1e-6,1-1e-6)))
            np.testing.assert_allclose(p,frame[method+'_sigmoid'],atol=1e-12,rtol=0)
if RAW.exists():
    assert digest(RAW)==RAW_SHA
    x=map_external(pd.read_csv(RAW))
    for part in parts:
        f=fitted[part['key']];local=f['local'];pre=local.named_steps['preprocess'];train=part['train']
        assert list(local.feature_names_in_)==FEATURES and local.named_steps['model'].C==.03
        num=pre.named_transformers_['numeric']
        np.testing.assert_allclose(num.named_steps['impute'].statistics_,x.iloc[train][NUM].median(),atol=1e-12,rtol=0)
        np.testing.assert_allclose(num.named_steps['scale'].mean_,x.iloc[train][NUM].mean(),atol=1e-10,rtol=0)
        for col,values in zip(CAT,pre.named_transformers_['category'].named_steps['encode'].categories_):
            assert list(values)==sorted(x.iloc[train][col].unique())
        for frame in (cal[cal.key==part['key']],rows[(rows.repeat==part['repeat'])&(rows.fold==part['fold'])]):
            transformed=pre.transform(x.iloc[frame.row_index])
            p=expit(transformed@local.named_steps['model'].coef_[0]+local.named_steps['model'].intercept_[0])
            np.testing.assert_allclose(p,frame.local,atol=1e-12,rtol=0)
print('PASS: independent saved metrics, threshold maximality, role separation, calibration algebra; raw preprocessing/predictions '+('passed.' if RAW.exists() else 'SKIPPED (raw not packaged).'))
