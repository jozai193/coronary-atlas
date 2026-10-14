"""Descriptive background sensitivity for fixed linear app models, not clinical validity."""
import sys
from pathlib import Path
import numpy as np
import shap
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml.predict import Predictor
from ml.schema import ROOT,read_data,FEATURES,write_json
from ml.preprocessing import transformed_groups

p=Predictor();x=read_data()[FEATURES];results={}
for target,artifact in p.artifacts.items():
    if artifact['kind']!='logistic':
        results[target]={'status':'Not varied: path-dependent tree background is fixed by the trained tree. Reconstruction audited separately; stability not established.'}
        continue
    pre=artifact['pipeline'].named_steps['preprocess'];model=artifact['pipeline'].named_steps['model']
    z=pre.transform(x);groups=np.asarray(transformed_groups(pre))
    rankings=[];arrays=[];max_error=0.
    for seed in [20261008,20261009,20261010,20261011,20261012]:
        background=z[np.random.default_rng(seed).choice(len(z),100,replace=False)]
        ex=shap.LinearExplainer(model,shap.maskers.Independent(background))(z)
        grouped=np.column_stack([ex.values[:,groups==f].sum(axis=1) for f in FEATURES])
        max_error=max(max_error,float(np.max(np.abs(ex.base_values+grouped.sum(axis=1)-model.decision_function(z)))))
        arrays.append(grouped);rankings.append(np.argsort(-np.abs(grouped),axis=1)[:,:5])
    overlap=[];flips=[]
    for a in range(5):
        for b in range(a+1,5):
            overlap.extend(len(set(aa)&set(bb))/5 for aa,bb in zip(rankings[a],rankings[b]))
            for row,indices in enumerate(rankings[a]):
                flips.extend((np.sign(arrays[a][row,indices])!=np.sign(arrays[b][row,indices])).tolist())
    results[target]={'rows':len(z),'backgrounds':5,'background_size':100,
        'mean_top5_overlap_fraction':float(np.mean(overlap)),
        'minimum_top5_overlap_fraction':float(np.min(overlap)),
        'top5_sign_disagreement_fraction':float(np.mean(flips)),
        'max_logit_reconstruction_error':max_error}
write_json(ROOT/'output/verification/explanation_background_stability.json',{
    'scope':'Fixed models on original source inputs; varied training-background choice only. No refit stability, causal or clinical validity claim.',
    'targets':results})
print(results)
