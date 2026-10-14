"""Independent role and saved-metric audit of the frozen LCX experiment."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd,joblib
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,accuracy_score,recall_score
from ml import full_input_transfer as experiment

experiment.locked()
cohorts,source=experiment.data();out=experiment.OUT
parts=json.loads((out/'partitions.json').read_text());results=json.loads((out/'results.json').read_text())
assert experiment.mc.sha(out/'evaluation_predictions.csv')==results['prediction_sha256']
assert experiment.mc.sha(out/'private/fitted.joblib')==json.loads((out/'fit_receipt.json').read_text())['sha256']
pred=pd.read_csv(out/'evaluation_predictions.csv',float_precision='round_trip')
fits=joblib.load(out/'private/fitted.joblib')
for part in parts:
    train,test=set(part['train']),set(part['test'])
    assert not train&test and train|test==set(range(303))
    blocked=set(cohorts['uci']['fingerprints'][part['test']])
    assert not blocked&set(cohorts['angiocad']['fingerprints'][part['extra']])
    for arm in experiment.ARMS:
        fitted=fits[part['key']+'_'+arm]
        common=list(cohorts['angiocad']['x'])
        shared_train=source.iloc[part['train']][common]
        if arm=='full_augmented':shared_train=pd.concat([shared_train,cohorts['angiocad']['x'].iloc[part['extra']]],ignore_index=True)
        for processor,training in [(fitted['shared'],shared_train),(fitted['private'],source.iloc[part['train']])]:
            if processor is None:continue
            numeric=processor.transformers_[0][2]
            values=training[numeric].astype(float)
            assert np.allclose(processor.named_transformers_['numeric'].named_steps['impute'].statistics_,values.median(),atol=1e-12,rtol=0)
            assert np.allclose(processor.named_transformers_['numeric'].named_steps['scale'].mean_,values.fillna(values.median()).mean(),atol=1e-10,rtol=0)
        subset=pred[(pred.repeat==part['repeat'])&(pred.fold==part['fold'])&(pred.arm==arm)].set_index('row').loc[part['test']]
        assert np.array_equal(subset.y,cohorts['uci']['y'][part['test']])
        assert np.allclose(subset.probability,experiment.predict(fits[part['key']+'_'+arm],source.iloc[part['test']]),atol=1e-14,rtol=0)
for (repeat,arm),p in pred.groupby(['repeat','arm']):
    assert set(p.row)==set(range(303)) and not p.row.duplicated().any()
    expected=results['scores'][str(repeat)][arm]
    measures=dict(auc=roc_auc_score(p.y,p.probability),average_precision=average_precision_score(p.y,p.probability),brier=brier_score_loss(p.y,p.probability),accuracy=accuracy_score(p.y,p.probability>=.5),sensitivity=recall_score(p.y,p.probability>=.5),specificity=recall_score(1-p.y,p.probability<.5))
    assert all(abs(v-expected[k])<1e-14 for k,v in measures.items())
a=pred[pred.arm=='full_augmented'].sort_values(['repeat','row']);b=pred[pred.arm=='full_local'].sort_values(['repeat','row'])
errors=pd.DataFrame(dict(row=a.row.to_numpy(),delta=(a.probability.to_numpy()-a.y.to_numpy())**2-(b.probability.to_numpy()-b.y.to_numpy())**2)).groupby('row').delta.mean().to_numpy()
assert abs(errors.mean()-results['paired_brier_delta'])<1e-14
rng=np.random.default_rng(20261013);boot=[np.mean(errors[rng.integers(0,303,303)]) for _ in range(1000)]
assert np.allclose(np.quantile(boot,[.025,.975]),results['conditional_delta_95'],atol=1e-14,rtol=0)
print('PASS: 30 saved model predictions, 6 metric groups, all source/extra role boundaries, paired interval and protected artifacts.')
