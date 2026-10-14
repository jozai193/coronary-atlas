"""Optional four-target ensemble; unavailable installations retain the baseline."""
from ml.ensemble_candidate import DIRECTORY, CANDIDATE_ID, ResearchEnsemble
from ml.schema import ROOT, TARGETS
import json
from importlib.util import find_spec


def load_ensemble():
    unavailable = {'available': False, 'candidate_id': CANDIDATE_ID}
    if not (DIRECTORY / 'manifest.json').exists():
        return None, unavailable
    if find_spec('catboost') is None:
        return None, unavailable
    try:
        predictor = ResearchEnsemble()
    except ModuleNotFoundError as error:
        if error.name in {'catboost', 'graphviz', 'plotly'}:
            return None, unavailable
        raise
    results = json.loads((ROOT / 'ml/experiments/accuracy_ensemble_v1/results.json').read_text(encoding='utf-8'))
    scores = {(r['repeat'], r['target'], r['arm']): r for r in results['scores']}
    runs = [{'repeat': repeat, 'targets': {target: {
        'baseline': scores[(repeat, target, 'baseline_projected')],
        'candidate': scores[(repeat, target, 'sigmoid_uniform_projected')]}
        for target in TARGETS}} for repeat in (1, 2, 3)]
    return predictor, {'available': True, 'candidate_id': CANDIDATE_ID,
        'name': 'Calibrated ensemble · research', 'runs': runs,
        'note': 'All four models change. Matched repeated internal evaluation on the same 303 people showed lower mean probability error and higher mean accuracy. Both procedures include the same coherence adjustment. New splits are not new patients; this candidate has no independent clinical validation. Explanations are sampled permutation attributions of the calibrated ensemble before coherence adjustment.',
        'scope': results['scope']}
