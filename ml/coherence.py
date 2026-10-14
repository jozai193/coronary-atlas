"""Transparent Euclidean projection of CAD and vessel probabilities."""
import numpy as np


def project_probabilities(probabilities):
    """Project [CAD, LAD, LCX, RCA] onto CAD >= each vessel probability.

    The four inputs must already be finite probabilities. No outcomes or fitted
    parameters are used. SHAP for the underlying models still explains the
    unprojected inputs, not this joint adjustment.
    """
    p = np.asarray(probabilities, dtype=float)
    if p.shape != (4,) or not np.isfinite(p).all() or (p < 0).any() or (p > 1).any():
        raise ValueError('Expected four finite probabilities in [0, 1].')
    if p[0] >= np.max(p[1:]):
        return p.copy()
    vessels = p[1:]
    sorted_vessels = np.sort(vessels)[::-1]
    pooled_sum = p[0]
    for count in range(1, 4):
        pooled_sum += sorted_vessels[count - 1]
        level = pooled_sum / (count + 1)
        if count == 3 or level >= sorted_vessels[count]:
            result = p.copy()
            result[0] = level
            result[1:] = np.minimum(vessels, level)
            return result
    raise AssertionError('The projection active set was not found.')
