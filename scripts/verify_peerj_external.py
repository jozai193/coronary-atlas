"""Read-only checks for the frozen trial's secondary summaries and UI evidence."""
from pathlib import Path
from datetime import datetime
import hashlib
import json

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'output/research/peerj_v1'
result = json.loads((folder / 'results.json').read_text())
fit = json.loads((folder / 'fit_manifest.json').read_text())
lock = json.loads((folder / 'prefit_lock.json').read_text())
rows = pd.read_csv(folder / 'external_predictions.csv', float_precision='round_trip')
assert datetime.fromisoformat(lock['utc']) < datetime.fromisoformat(fit['frozen_utc']) < datetime.fromisoformat(result['scored_utc'])
assert len(fit['fit_costs']) == 12 and fit['elapsed_seconds'] < 600
assert set(rows.columns) == {'row_index', 'y', 'wbc_at_most_100', 'source_age_overlap', 'female', 'age_under_50', 'logistic', 'ebm'}

for name, mask in {'female': rows.female, 'male': ~rows.female,
                   'under_50': rows.age_under_50, 'age_50_plus': ~rows.age_under_50}.items():
    part = rows[mask]
    group = result['subgroups'][name]
    assert group['n'] == len(part) and group['positives'] == int(part.y.sum())
    eligible = len(part) >= 30 and part.y.value_counts().min() >= 10
    assert group['eligible'] == eligible
    for kind in ('logistic', 'ebm'):
        saved = group['models'][kind]
        assert np.isclose(saved['auc'], roc_auc_score(part.y, part[kind]), atol=1e-12, rtol=0)
        assert np.isclose(saved['brier'], brier_score_loss(part.y, part[kind]), atol=1e-12, rtol=0)
        assert np.isclose(saved['log_loss'], log_loss(part.y, part[kind]), atol=1e-12, rtol=0)
        actual = dict(zip(('tn', 'fp', 'fn', 'tp'), confusion_matrix(part.y, part[kind] >= .5).ravel()))
        assert saved['confusion'] == actual
        tn, fp, fn, tp = (actual[k] for k in ('tn', 'fp', 'fn', 'tp'))
        expected = dict(accuracy=(tn+tp)/len(part), sensitivity=tp/(tp+fn), specificity=tn/(tn+fp),
                        precision=tp/(tp+fp), f1=2*tp/(2*tp+fp+fn), prevalence=part.y.mean(), mean_probability=part[kind].mean())
        for key, value in expected.items():
            assert np.isclose(saved[key], value, atol=1e-12, rtol=0), (name, kind, key)

for kind in ('logistic', 'ebm'):
    counts = 0
    for item in result['reliability'][kind]:
        lower = item['bin'] / 10
        upper = (item['bin'] + 1) / 10
        part = rows[(rows[kind] >= lower) & ((rows[kind] <= upper) if item['bin'] == 9 else (rows[kind] < upper))]
        assert len(part) == item['n']
        assert np.isclose(part[kind].mean(), item['mean_probability'], atol=1e-12, rtol=0)
        assert np.isclose(part.y.mean(), item['prevalence'], atol=1e-12, rtol=0)
        counts += len(part)
    assert counts == 553
primary = result['scores']['primary']
da = primary['ebm']['auc'] - primary['logistic']['auc']
db = primary['ebm']['brier'] - primary['logistic']['brier']
assert (da, db) == (result['delta_auc'], result['delta_brier'])
assert result['engineering_screen'] == ((da >= .015 and db <= 0) or (db <= -.005 and da >= -.01))
assert (ROOT / 'frontend/src/generated/peerj-external-results.json').read_bytes() == (folder / 'results.json').read_bytes()
print('Verified all four subgroup summaries, ten-bin reliability counts, frozen ordering, failed screen and exact UI evidence bytes.')
print('Result SHA256:', hashlib.sha256((folder / 'results.json').read_bytes()).hexdigest())
