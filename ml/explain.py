"""SHAP explanations for the actual fitted classifier, grouped by source field."""
import numpy as np
import shap
from ml.preprocessing import transformed_groups


def make_explainer(artifact):
    model = artifact['pipeline'].named_steps['model']
    background = artifact['background']
    if artifact['kind'] == 'logistic':
        return shap.LinearExplainer(model, shap.maskers.Independent(background)), 'log-odds'
    # Path-dependent TreeSHAP exactly reconstructs this sklearn model. In the pinned
    # stack interventional TreeSHAP failed reconstruction on some split boundaries.
    return shap.TreeExplainer(model, feature_perturbation='tree_path_dependent', model_output='raw'), ('probability' if artifact['kind']=='forest' else 'log-odds')


def explain(artifact, explainer, unit, frame):
    pre = artifact['pipeline'].named_steps['preprocess']
    transformed = pre.transform(frame)
    explanation = explainer(transformed, check_additivity=True) if artifact['kind']!='logistic' else explainer(transformed)
    values = np.asarray(explanation.values)
    bases = np.asarray(explanation.base_values)
    if values.ndim == 3:
        values = values[:,:,1]
        base = float(bases[0,1])
    else:
        base = float(bases.reshape(-1)[0])
    grouped = {}
    for name, value in zip(transformed_groups(pre),values[0]):
        grouped[name] = grouped.get(name,0.) + float(value)
    probability = float(artifact['pipeline'].predict_proba(frame)[0,1])
    # decision_function is stable even when sigmoid rounds a probability to 0 or 1.
    expected = probability if unit=='probability' else float(artifact['pipeline'].decision_function(frame)[0])
    residual = abs(base+sum(grouped.values())-expected)
    if residual > 1e-4:
        raise RuntimeError('Explanation does not reconstruct model output.')
    return dict(method='SHAP',unit=unit,base_value=base,output_value=expected,additivity_error=residual,
                factors=sorted([dict(feature=name,contribution=value) for name,value in grouped.items()],key=lambda x:abs(x['contribution']),reverse=True),
                note='Factors contributing to this model prediction. Associations, not causes. Correlated inputs can share attribution. '+('Linear SHAP background: 100 deterministic training rows.' if artifact['kind']=='logistic' else 'TreeSHAP background: training path frequencies; tree-path-dependent attribution.'))
