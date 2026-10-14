import numpy as np
import pandas as pd
import pytest

from ml.angiocad_external import (BOUNDS, FEATURES, eligibility, endpoint,
                                  external_features, normalize_bin)


def test_bin_boundary_is_never_silently_assigned_negative():
    assert endpoint(['NL', '1-25']) == 0
    assert endpoint(['26-50', 'NL']) is None
    assert endpoint(['26-50', '51-75']) == 1
    assert normalize_bin(100.0) == '100'
    with pytest.raises(ValueError, match='Unknown stenosis bin'):
        endpoint(['25-50'])


def test_only_allowlisted_external_fields_reach_model_and_bad_codes_abort():
    raw = pd.DataFrame({
        'Age': [55], 'Sex': ['Female'], 'BMI': [27], 'DM': [1], 'HTN': [0],
        'Current Smoker': [np.nan], 'FBS': [100], 'Cr': [1.0], 'TG': [120],
        'LDL': [90], 'HDL': [45], 'leukocytes': [8500], 'PLT': [220],
        'Diagnosis': ['STEMI'], 'Prox LAD': ['100'], 'Gensini Score': [90],
    })
    X = external_features(raw)
    assert X.columns.tolist() == FEATURES
    assert X.loc[0, 'Sex'] == 'Fmale'
    assert X.loc[0, 'DM'] == '1'
    assert pd.isna(X.loc[0, 'Current Smoker'])
    assert eligibility(X)[0]['primary'].tolist() == [True]
    raw.loc[0, 'DM'] = 2
    with pytest.raises(ValueError, match='Unexpected binary code'):
        external_features(raw)


def test_extreme_external_measurement_is_excluded_by_frozen_bound():
    X = pd.DataFrame({name: [np.nan] for name in FEATURES})
    for name, value in {'Age': 55, 'BMI': 27, 'FBS': 100, 'CR': 1.0,
                        'TG': 120, 'LDL': 90, 'HDL': 45, 'WBC': 8500,
                        'PLT': 220, 'Sex': 'Male', 'DM': '0', 'HTN': '0',
                        'Current Smoker': '0'}.items():
        X[name] = [value]
    assert eligibility(X)[0]['primary'].tolist() == [True]
    X.loc[0, 'BMI'] = BOUNDS['BMI'][1] + 1
    masks, audit = eligibility(X)
    assert masks['primary'].tolist() == [False]
    assert audit['range_violations_by_field']['BMI'] == 1
