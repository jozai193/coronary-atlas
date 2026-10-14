import numpy as np
import pytest
from ml.peerj_operating import cutoff, fit_partition, predict, build_parts
from tests.test_peerj_adaptation import sample


def test_cutoff_maximality_ties_and_invalid_inputs():
    y=np.array([1,1,1,1,0,0]);p=np.array([.9,.7,.7,.2,.8,.1])
    assert cutoff(y,p,.75)==.7
    assert (p[y==1]>=cutoff(y,p,.75)).mean()>=.75
    assert (p[y==1]>.7).mean()<.75
    assert cutoff(y,p,1)==.2
    with pytest.raises(ValueError): cutoff(np.ones(6),p,.9)
    with pytest.raises(ValueError): cutoff(y,p,0)
    with pytest.raises(ValueError): cutoff(y,np.full(6,np.nan),.9)


def test_evaluation_mutation_cannot_change_training_calibration_or_cutoffs():
    x,y,p=sample();part=dict(train=list(range(20)),calibration=list(range(20,32)),test=list(range(32,40)))
    before,_=fit_partition(x,y,p,part)
    xx=x.copy();yy=y.copy();pp=p.copy()
    xx.loc[32:,'Age']=999999;yy[32:]=1-yy[32:];pp[32:]=.00001
    after,_=fit_partition(xx,yy,pp,part)
    assert before['cutoffs']==after['cutoffs'] and before['constant']==after['constant']
    for key in ('source_sigmoid','local_sigmoid'):
        np.testing.assert_array_equal(before[key].coef_,after[key].coef_)
        np.testing.assert_array_equal(before[key].intercept_,after[key].intercept_)
    a=predict(before,x,p);b=predict(after,x,p)
    for key in a: np.testing.assert_array_equal(a[key],b[key])


def test_calibration_does_not_retrain_ranker_or_preprocessing():
    x,y,p=sample();part=dict(train=list(range(20)),calibration=list(range(20,32)),test=list(range(32,40)))
    first,_=fit_partition(x,y,p,part)
    x2=x.copy();y2=y.copy();x2.loc[20:31,'Age']=888;y2[20:32]=1-y2[20:32]
    second,_=fit_partition(x2,y2,p,part)
    np.testing.assert_array_equal(first['local'].predict_proba(x),second['local'].predict_proba(x))


def test_three_roles_disjoint_and_two_complete_evaluation_repeats():
    y=np.array([0]*352+[1]*201);parts=build_parts(y)
    for part in parts:
        a,b,c=map(set,(part['train'],part['calibration'],part['test']))
        assert not a&b and not a&c and not b&c and len(a|b|c)==553
        assert len(b)==111 and len(a) in (331,332)
    for rep in (1,2):
        assert sorted(i for p in parts if p['repeat']==rep for i in p['test'])==list(range(553))
