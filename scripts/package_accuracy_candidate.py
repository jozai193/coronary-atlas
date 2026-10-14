"""Fit the already nominated primary procedure for optional research inference."""
import os
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import time
import joblib
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from threadpoolctl import threadpool_limits
from ml import accuracy_ensemble as exp
from ml import accuracy_missingness as stress
from ml.ensemble_candidate import DIRECTORY, CANDIDATE_ID, MEMBERS, ResearchEnsemble, raw_probabilities


def main():
    if DIRECTORY.exists():
        raise FileExistsError('Refusing candidate overwrite')
    original, _ = exp.check_receipt()
    result = exp.load(exp.OUT / 'results.json')
    verification = exp.load(exp.OUT / 'verification.json')
    if not result['comparisons']['sigmoid_uniform']['engineering_screen_passed'] or verification['results_sha256'] != exp.digest(exp.OUT / 'results.json'):
        raise ValueError('Primary candidate did not pass its verified research screen')
    stress_verification = exp.load(stress.OUT / 'verification.json')
    if stress_verification['results_sha256'] != exp.digest(stress.OUT / 'results.json'):
        raise ValueError('Missingness verification changed')
    X, y, groups = exp.source_data()
    DIRECTORY.mkdir(parents=True)
    artifacts = {}
    partitions = {}
    with threadpool_limits(limits=1):
        for ti, target in enumerate(exp.ORDER):
            seed = 20261024 + ti * 100
            inner = list(StratifiedGroupKFold(3, shuffle=True, random_state=seed).split(X, y[:, ti], groups))
            fitted = exp.fit_role(X, y[:, ti], inner, seed)
            artifact = {'full': {name: fitted['full'][name] for name in MEMBERS}, 'calibrator': fitted['calibrator']}
            path = DIRECTORY / f'{target}.joblib'
            joblib.dump(artifact, path, compress=3)
            artifacts[target] = {'file': path.name, 'sha256': exp.digest(path)}
            partitions[target] = [{'train': tr.tolist(), 'calibration': va.tolist()} for tr, va in inner]
            print(f'Packaged {target}', flush=True)
    rows = np.random.default_rng(20261025).choice(len(X), 4, replace=False)
    path = DIRECTORY / 'background.joblib'
    joblib.dump(X.iloc[rows].copy(), path, compress=3)
    artifacts['background'] = {'file': path.name, 'sha256': exp.digest(path)}
    evidence = [exp.OUT / 'manifest.json', exp.OUT / 'results.json', exp.OUT / 'verification.json',
                stress.OUT / 'manifest.json', stress.OUT / 'results.json', stress.OUT / 'verification.json',
                exp.ROOT / 'ml/ensemble_candidate.py', Path(__file__), exp.ROOT / 'models/metadata.json']
    manifest = {'candidate_id': CANDIDATE_ID, 'features': exp.FEATURES, 'members': list(MEMBERS),
        'artifacts': artifacts, 'evidence_hashes': {p.relative_to(exp.ROOT).as_posix(): exp.digest(p) for p in evidence},
        'background_rows': rows.tolist(), 'calibration_partitions': partitions,
        'inference_verified': False, 'default_promoted': False,
        'scope': 'Optional research candidate nominated on repeated internal development, trained on all 303 source records. No independent or clinical validation. Full-data predictions are not evaluation evidence.'}
    exp.write_json(DIRECTORY / 'manifest.json', manifest)
    candidate = ResearchEnsemble(require_verified=False)
    timings, residuals = [], []
    profiles = [X.iloc[0].to_dict(), X.iloc[101].to_dict()]
    incomplete = X.iloc[202].to_dict()
    for name in stress.SCENARIOS['core_only']:
        incomplete[name] = None
    profiles.append(incomplete)
    for profile in profiles:
        started = time.perf_counter()
        prediction = candidate.predict(profile)
        timings.append(time.perf_counter()-started)
        residuals.extend(prediction[t]['explanation']['additivity_error'] for t in exp.ORDER)
    with threadpool_limits(limits=1):
        full = raw_probabilities(candidate.artifacts, X)
    if full.shape != (303, 4) or not np.isfinite(full).all() or full.min() < 0 or full.max() > 1:
        raise ValueError('Candidate probability contract failure')
    # Save no fitted-data accuracy. These checks establish engineering fidelity only.
    manifest['inference_verified'] = True
    manifest['runtime_check'] = {'profiles': len(profiles), 'seconds_per_profile': timings,
        'max_attribution_residual': max(residuals), 'full_source_predictions_finite': True,
        'note': 'In-sample engineering checks, not held-out or clinical evidence.'}
    exp.write_json(DIRECTORY / 'manifest.json', manifest)
    exp.assert_hashes(original['protected_hashes'])
    print(manifest['runtime_check'], flush=True)


if __name__ == '__main__':
    main()
