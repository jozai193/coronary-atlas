import numpy as np
import pandas as pd
import pytest
from ml.multicohort import balance_weights,fingerprints,roles,fit_training,predict


def test_cross_cohort_duplicate_and_local_test_rows_cannot_reach_training():
    x=pd.DataFrame({'Age':[40,50,60,70,80,90], 'Sex':['Male']*6})
    item=lambda xx:dict(x=xx,y=np.array([0,1,0,1,0,1]),fingerprints=fingerprints(xx))
    other=x.copy();other.loc[5]=x.loc[0]
    cohorts={'a':item(x),'b':item(other)}
    training,removed=roles(cohorts,'a',np.array([0]),np.arange(1,6))
    assert 0 not in training['a'] and 5 not in training['b']
    assert removed=={'a':0,'b':2}  # b row 0 is also the same held-out fingerprint.
    # Every b row matched an omitted-cohort input: no valid fit is permitted.
    with pytest.raises(AssertionError):roles(cohorts,'a',np.arange(6))


def test_study_balancing_preserves_total_weight_and_equal_study_mass():
    groups=np.array(['a']*3+['b']*7)
    w=balance_weights(groups)
    assert w.sum()==pytest.approx(10)
    assert w[groups=='a'].sum()==pytest.approx(5)
    assert w[groups=='b'].sum()==pytest.approx(5)


def test_preprocessing_is_fit_only_on_explicit_training_and_targets_are_rejected():
    x=pd.DataFrame({'Age':[20.,30.,40.,50.], 'Sex':['Male','Fmale','Male','Fmale']})
    y=np.array([0,0,1,1])
    fits=fit_training({'a':(x,y)})
    for est in fits.values():
        assert est.named_steps['preprocess'].named_transformers_['numeric'].named_steps['scale'].mean_[0]==35
    out=predict(fits,pd.DataFrame({'Age':[95.], 'Sex':['Unseen']}),'a','augmentation')
    assert all(np.isfinite(p).all() for p in out.values())
    with pytest.raises(AssertionError):fit_training({'a':(x.assign(Cath=['CAD']*4),y)})
