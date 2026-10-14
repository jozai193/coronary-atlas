import numpy as np
import pandas as pd
import pytest
from scipy.special import expit

from ml.peerj_external import FEATURES, CAT
from ml.peerj_adaptation import fit_subset, predict, logits, parameters


def sample():
    rng=np.random.default_rng(39)
    x=pd.DataFrame({f:rng.normal(size=40) for f in FEATURES if f not in CAT})
    for f in CAT: x[f]=np.where(np.arange(40)%2,'1','0')
    x=x[FEATURES]
    y=(rng.random(40)>.6).astype(int)
    p=expit(x.Age.to_numpy()+1.5)
    return x,y,p


def test_fit_is_invariant_to_labels_and_features_outside_adaptation_subset():
    x,y,p=sample(); indices=np.arange(24)
    first=fit_subset(x,y,p,indices)
    changed_y=y.copy(); changed_y[24:]=1-changed_y[24:]
    changed_x=x.copy(); changed_x.loc[24:,'Age']=99999
    changed_p=p.copy(); changed_p[24:]=.99999
    second=fit_subset(changed_x,changed_y,changed_p,indices)
    assert parameters(first)==parameters(second)
    before=predict(first,x.iloc[24:],p[24:]);after=predict(second,x.iloc[24:],p[24:])
    for method in before: np.testing.assert_array_equal(before[method],after[method])


def test_offset_matches_fit_prevalence_and_preserves_rank_but_never_fits_single_class():
    x,y,p=sample();indices=np.arange(24)
    fitted=fit_subset(x,y,p,indices)
    assert np.mean(expit(logits(p[indices])+fitted['offset'])) == pytest.approx(y[indices].mean(),abs=1e-10)
    pred=predict(fitted,x,p)
    np.testing.assert_array_equal(np.argsort(pred['source']),np.argsort(pred['offset']))
    assert np.isfinite(logits([0.,1.])).all()
    with pytest.raises(ValueError,match='Both outcome classes'):
        fit_subset(x,np.zeros(len(y)),p,indices)
