import copy
import numpy as np
import pandas as pd
import pytest
from ml.cohort_calibration import cohort_model,fit_roles,parts,predict
from ml.multicohort import fingerprints


def test_cohort_intercepts_fit_different_baselines_and_reject_unknown_site():
    x=pd.DataFrame({'Age':[50.]*40,'Sex':['Male']*40})
    est=cohort_model({'a':(x,np.array([1]*10+[0]*30)),'b':(x,np.array([1]*30+[0]*10))})
    assert est.predict_proba(x,'a')[:,1].mean()==pytest.approx(.25,abs=1e-5)
    assert est.predict_proba(x,'b')[:,1].mean()==pytest.approx(.75,abs=1e-5)
    with pytest.raises(ValueError,match='Unknown cohort'):est.predict_proba(x,'new_hospital')


def fixture_cohorts():
    result={}
    for name,offset in [('a',0),('b',.01)]:
        x=pd.DataFrame({'Age':np.arange(60,dtype=float)+30+offset,'Sex':['Male','Fmale']*30})
        result[name]=dict(x=x,y=np.array([0,1]*30),rows=np.arange(60),fingerprints=fingerprints(x))
    # A fingerprint in b matches one destination row, regardless of its label.
    result['b']['x'].iloc[0]=result['a']['x'].iloc[0]
    result['b']['fingerprints']=fingerprints(result['b']['x'])
    return result


def test_roles_group_all_calibration_and_evaluation_matches_out_of_training():
    c=fixture_cohorts();specs=parts({'cad':c})
    for s in specs:
        item=c[s['destination']]
        blocked=set(item['fingerprints'][s['calibration']])|set(item['fingerprints'][s['evaluation']])
        for name,ix in s['training'].items():assert not blocked&set(c[name]['fingerprints'][ix])
    for name in c:
        for rep in (1,2):
            ix=[i for s in specs if s['destination']==name and s['repeat']==rep for i in s['evaluation']]
            assert sorted(ix)==list(range(60))


def test_evaluation_feature_and_label_mutations_cannot_change_fits_calibration_or_cutoffs():
    c=fixture_cohorts();s=parts({'cad':c})[0];name=s['destination']
    def fit_from(cohorts):
        train={n:(cohorts[n]['x'].iloc[ix],cohorts[n]['y'][ix]) for n,ix in s['training'].items()}
        item=cohorts[name]
        return fit_roles(train,item['x'].iloc[s['calibration']],item['y'][s['calibration']],name)[0]
    original=fit_from(c);mutated=copy.deepcopy(c)
    mutated[name]['x'].loc[s['evaluation'],'Age']=1e9
    mutated[name]['x'].loc[s['evaluation'],'Sex']='Unseen'
    mutated[name]['y'][s['evaluation']]=1-mutated[name]['y'][s['evaluation']]
    changed=fit_from(mutated)
    assert original['cutoffs']==changed['cutoffs']
    for arm in original['calibrators']:
        np.testing.assert_array_equal(original['calibrators'][arm].coef_,changed['calibrators'][arm].coef_)
        np.testing.assert_array_equal(original['calibrators'][arm].intercept_,changed['calibrators'][arm].intercept_)
    probe=c[name]['x'].iloc[:3]
    before=predict(original,probe,name);after=predict(changed,probe,name)
    for arm in before:np.testing.assert_array_equal(before[arm],after[arm])
