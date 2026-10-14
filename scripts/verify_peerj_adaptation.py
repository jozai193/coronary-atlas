"""Independent arithmetic and training-preprocessing audit; no fitting or edits."""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import joblib
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.metrics import roc_auc_score, confusion_matrix, log_loss
from ml.peerj_external import FEATURES, CAT, NUM, RAW, RAW_SHA, map_external

folder=ROOT/'output/research/peerj_adaptation_v1'
old=ROOT/'output/research/peerj_v1'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(ROOT/'ml/peerj_external.py')==digest(old/'runner_snapshot.py'), 'Shared fitting dependency changed'
manifest=json.loads((folder/'evidence_manifest.json').read_text())
for name,expected in manifest['files'].items(): assert digest(folder/name)==expected
rows=pd.read_csv(folder/'predictions.csv',dtype={'budget':str},float_precision='round_trip')
result=json.loads((folder/'results.json').read_text())
parts=json.loads((folder/'partitions.json').read_text())
models=joblib.load(folder/'fitted.joblib')
base=pd.read_csv(old/'external_predictions.csv',float_precision='round_trip')
assert set(rows.y)=={0,1} and len(rows)==2212
for budget in ('64','all'):
    for repeat in (1,2):
        frame=rows[(rows.budget==budget)&(rows.repeat==repeat)].sort_values('row_index')
        assert frame.row_index.tolist()==list(range(553))
        assert np.array_equal(frame.y,base.y)
        for method in ('source','constant','offset','sigmoid','local_logistic'):
            y=frame.y.to_numpy();p=frame[method].to_numpy()
            saved=result['budgets'][budget]['repeats'][str(repeat)][method]
            tn,fp,fn,tp=confusion_matrix(y,p>=.5).ravel()
            checks=dict(brier=np.mean((y-p)**2),auc=roc_auc_score(y,p),log_loss=log_loss(y,p),
                        mean_probability=p.mean(),sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),
                        mean_within_fold_auc=np.mean([roc_auc_score(g.y,g[method]) for _,g in frame.groupby('fold')]))
            for key,value in checks.items(): assert np.isclose(value,saved[key],rtol=0,atol=1e-12),(budget,repeat,method,key)
            assert saved['confusion']==dict(tn=tn,fp=fp,fn=fn,tp=tp)
if RAW.exists():
    assert digest(RAW)==RAW_SHA
    x=map_external(pd.read_csv(RAW))
    for part in parts:
        train=part['adaptation'];test=part['test'];fitted=models[part['key']]
        assert len(train)==(64 if part['budget']=='64' else len(part['train_pool']))
        assert set(train)<=set(part['train_pool']) and not set(train)&set(test)
        local=fitted['local_logistic'];pre=local.named_steps['preprocess']
        assert list(local.feature_names_in_)==FEATURES
        assert local.named_steps['model'].C==.03
        num=pre.named_transformers_['numeric']
        np.testing.assert_allclose(num.named_steps['impute'].statistics_,x.iloc[train][NUM].median(),rtol=0,atol=1e-12)
        np.testing.assert_allclose(num.named_steps['scale'].mean_,x.iloc[train][NUM].mean(),rtol=0,atol=1e-10)
        expected_categories=[sorted(x.iloc[train][c].unique()) for c in CAT]
        actual_categories=pre.named_transformers_['category'].named_steps['encode'].categories_
        for a,b in zip(actual_categories,expected_categories): assert list(a)==b
        zz=logit(np.clip(base.iloc[train].logistic.to_numpy(),1e-6,1-1e-6))
        assert abs(expit(zz+fitted['offset']).mean()-base.iloc[train].y.mean())<1e-10
        assert fitted['sigmoid'].C==1 and fitted['sigmoid'].n_features_in_==1
    print('Passed training-subset medians/scaling/categories, fixed hyperparameters and offset balance on all 20 fits.')
else:
    print('Raw preprocessing audit not run: external raw data intentionally excluded.')
print('Passed independent Brier/AUC/log loss/confusion arithmetic for all 20 budget/repeat/method summaries and locked shared dependency.')
