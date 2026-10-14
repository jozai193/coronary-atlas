"""Link the production inference function to frozen held-out predictions."""
import os
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_THREADS'):
    os.environ[key] = '1'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from ml import accuracy_ensemble as exp
from ml.accuracy_missingness import OUT as MASKED_OUT, SCENARIOS
from ml.ensemble_candidate import ResearchEnsemble, raw_probabilities, DIRECTORY
from ml.schema import ROOT, NUMERIC, TARGETS, digest, write_json


def main():
    manifest, _ = exp.check_receipt()
    for name, sha in exp.load(MASKED_OUT / 'receipt.json').items():
        if digest(MASKED_OUT / name) != sha:
            raise ValueError(f'Missingness evidence changed: {name}')
    exp.assert_hashes(exp.load(MASKED_OUT / 'manifest.json')['input_hashes'])
    packaged = ResearchEnsemble()
    if packaged.manifest['default_promoted']:
        raise ValueError('Unexpected default promotion')
    X, y, _ = exp.source_data()
    saved = pd.read_csv(MASKED_OUT / 'predictions.csv', float_precision='round_trip')
    if len(saved) != 303 * 4 * 3 * 4 or saved.duplicated(['scenario', 'repeat', 'target', 'row']).any():
        raise ValueError('Missing or duplicate held-out records')
    maximum_residual, count = 0., 0
    with threadpool_limits(limits=1):
        for repeat in range(1, 4):
            for fold in range(5):
                roles = [r for r in manifest['roles'] if r['repeat'] == repeat and r['fold'] == fold]
                if {r['target'] for r in roles} != set(TARGETS) or len(roles) != 4:
                    raise ValueError('Incomplete shared fold')
                te = roles[0]['test']
                for role in roles:
                    np.testing.assert_array_equal(role['test'], te)
                artifacts = {r['target']: joblib.load(exp.OUT / 'private' / (exp.role_name(r) + '.joblib')) for r in roles}
                for scenario, missing in SCENARIOS.items():
                    frame = X.iloc[te].copy()
                    for name in missing:
                        frame[name] = np.nan if name in NUMERIC else pd.Series(np.nan, index=frame.index, dtype=object)
                    actual = raw_probabilities(artifacts, frame)
                    for ti, target in enumerate(TARGETS):
                        expected = saved[(saved.scenario == scenario) & (saved.repeat == repeat) &
                                         (saved.fold == fold) & (saved.target == target)].sort_values('row')
                        np.testing.assert_array_equal(expected.row, te)
                        np.testing.assert_array_equal(expected.y, y[te, ti])
                        np.testing.assert_allclose(actual[:, ti], expected.sigmoid_uniform, atol=1e-12, rtol=0)
                        maximum_residual = max(maximum_residual, float(np.max(np.abs(actual[:, ti] - expected.sigmoid_uniform.to_numpy()))))
                        count += len(te)
            print(f'Production inference replayed repeat {repeat}/3', flush=True)
    if count != len(saved):
        raise ValueError('Incomplete replay')
    exp.assert_hashes(manifest['protected_hashes'])
    report = {'status': 'passed', 'held_out_target_predictions': count, 'shared_outer_folds': 15,
              'scenarios': list(SCENARIOS), 'maximum_probability_residual': maximum_residual,
              'packaged_artifact_and_evidence_integrity': 'passed',
              'protected_historical_files_unchanged': len(manifest['protected_hashes']),
              'scope': 'Production inference math replay with held-out fold models; full-data packaged models are not held-out validation.',
              'hashes': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__),
                  ROOT / 'ml/ensemble_candidate.py', DIRECTORY / 'manifest.json', MASKED_OUT / 'predictions.csv']}}
    write_json(ROOT / 'output/verification/2026-10-14-packaged-ensemble.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
