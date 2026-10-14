import numpy as np
import pandas as pd
import pytest

from ml.peerj_external import FEATURES, MAPPING, map_external, metrics


def test_mapping_converts_units_and_never_uses_outcomes_or_unmapped_fields():
    raw = pd.DataFrame({column: [1., 2.] for column, _ in MAPPING.values()})
    raw['Gender'] = [1, 2]
    raw['Diabetes'] = [0, 1]
    raw['Hypertension'] = [1, 0]
    raw['Group'] = [1, 0]
    raw['id'] = [100, 200]
    raw['Diastolic blood pressure at admission'] = [888, 80]
    x = map_external(raw)
    assert list(x.columns) == FEATURES
    assert x.Sex.tolist() == ['Male', 'Fmale']
    assert x.DM.tolist() == ['0', '1']
    assert x.HTN.tolist() == ['1', '0']
    assert x.FBS.iloc[0] == pytest.approx(1/.05551)
    assert x.LDL.iloc[0] == pytest.approx(1/.02586)
    assert x.TG.iloc[0] == pytest.approx(1/.01129)
    assert x.HB.iloc[0] == .1
    assert x.WBC.iloc[0] == 1000
    assert x.PLT.iloc[0] == 1
    raw['Group'] = 42
    raw['id'] = -1
    raw['Diastolic blood pressure at admission'] = -999
    pd.testing.assert_frame_equal(x, map_external(raw))
    raw.loc[0, 'Gender'] = 3
    with pytest.raises(AssertionError):
        map_external(raw)


def test_metrics_report_misses_false_alarms_and_fixed_threshold():
    result = metrics(np.array([0, 0, 1, 1]), np.array([.1, .7, .4, .5]))
    assert result['confusion'] == dict(tn=1, fp=1, fn=1, tp=1)
    assert result['sensitivity'] == result['specificity'] == .5
    with pytest.raises(AssertionError):
        metrics([0, 1], [.1, float('nan')])
