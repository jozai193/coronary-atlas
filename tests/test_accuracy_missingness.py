import numpy as np
from ml import accuracy_missingness as exp
from ml.preprocessing import pipeline
from ml.schema import CATEGORICAL


def test_native_fill_uses_training_median_and_mode():
    X, y, _ = exp.exp.source_data()
    model = pipeline('logistic', .03).fit(X.iloc[:150], y[:150, 0])
    artifact = {'full': {'logistic_003': model}}
    complete = exp.native_frame(artifact, X.iloc[150:155])
    np.testing.assert_array_equal(complete.to_numpy(), X.iloc[150:155].to_numpy())
    missing = X.iloc[150:155].copy()
    missing['Age'] = np.nan
    missing['Sex'] = np.nan
    filled = exp.native_frame(artifact, missing)
    assert (filled.Age == X.iloc[:150].Age.median()).all()
    imputer = model.named_steps['preprocess'].named_transformers_['categorical'].named_steps['impute']
    assert (filled.Sex == imputer.statistics_[CATEGORICAL.index('Sex')]).all()
    assert not filled.isna().any().any()
