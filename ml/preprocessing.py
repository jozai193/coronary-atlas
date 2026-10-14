"""Fold-local transforms, never fitted on evaluation rows."""
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from ml.schema import NUMERIC, CATEGORICAL, FEATURES, PROHIBITED, SEED


def check_features(columns):
    if set(columns) & PROHIBITED or set(columns) != set(FEATURES):
        raise ValueError('Training inputs must exactly match the clinical feature allowlist.')


def pipeline(kind: str, strength: float = 0.1):
    numeric = Pipeline([('impute', SimpleImputer(strategy='median', keep_empty_features=True)), ('scale', StandardScaler())])
    category = Pipeline([('impute', SimpleImputer(strategy='most_frequent', keep_empty_features=True)), ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    pre = ColumnTransformer([('numeric', numeric, NUMERIC), ('categorical', category, CATEGORICAL)])
    if kind == 'logistic':
        model = LogisticRegression(C=strength, max_iter=3000, random_state=SEED)
    elif kind == 'forest':
        model = RandomForestClassifier(n_estimators=120, min_samples_leaf=5, max_features='sqrt', n_jobs=1, random_state=SEED)
    elif kind == 'boosting':
        model = GradientBoostingClassifier(n_estimators=80, learning_rate=0.035, max_depth=2, min_samples_leaf=8, random_state=SEED)
    else:
        raise ValueError(kind)
    return Pipeline([('preprocess', pre), ('model', model)])


def transformed_groups(pre):
    """Map every encoded column back to one original input."""
    encoder = pre.named_transformers_['categorical'].named_steps['encode']
    return NUMERIC + [name for name, categories in zip(CATEGORICAL, encoder.categories_) for _ in categories]
