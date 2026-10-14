"""Read-only verification of frozen AngioCAD scoring artifacts."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, confusion_matrix, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/research/angiocad_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((OUT / 'frozen_manifest.json').read_text(encoding='utf-8'))
    result = json.loads((OUT / 'external_results.json').read_text(encoding='utf-8'))
    p = pd.read_csv(OUT / 'external_predictions.csv')
    oof = pd.read_csv(OUT / 'source_oof.csv')
    assert sha(OUT / 'frozen_source_models.joblib') == manifest['model_sha256']
    assert sha(OUT / 'source_oof.csv') == manifest['source_oof_sha256']
    assert sha(OUT / 'external_predictions.csv') == result['predictions_sha256']
    assert sha(OUT / 'frozen_manifest.json') == result['source_model_manifest_sha256']
    assert sha(ROOT / 'docs/angiocad_external_protocol.md') == result['protocol_sha256']
    assert len(p) == 377 and len(oof) == 303
    assert p.row_index.tolist() == list(range(377))
    assert oof.row_index.tolist() == list(range(303))
    settings = {'primary_main': ('primary', 'main'),
                'all_age_main': ('all_age_present', 'main'),
                'complete_main': ('complete_inputs', 'main'),
                'primary_branch': ('primary', 'branch_inclusive')}
    checked = 0
    for name, (cohort, endpoint) in settings.items():
        for target, recorded in result['scores'][name].items():
            selection = p[f'in_{cohort}'].astype(bool) & p[f'{endpoint}_{target}_y'].notna()
            y = p.loc[selection, f'{endpoint}_{target}_y'].astype(int).to_numpy()
            probs = p.loc[selection, f'{target}_p'].to_numpy()
            tn, fp, fn, tp = confusion_matrix(y, probs >= .5, labels=[0, 1]).ravel()
            assert len(y) == recorded['n'] and sum(y) == recorded['positives']
            assert np.isclose(roc_auc_score(y, probs), recorded['roc_auc'], atol=1e-12)
            assert np.isclose(brier_score_loss(y, probs), recorded['brier'], atol=1e-12)
            assert recorded['confusion'] == {'tn': int(tn), 'fp': int(fp),
                                              'fn': int(fn), 'tp': int(tp)}
            checked += 1
    for target, recorded in result['source_oof'].items():
        y = oof[f'{target}_y'].to_numpy()
        probs = oof[f'{target}_p'].to_numpy()
        assert len(oof[f'{target}_fold'].unique()) == 5
        assert np.isclose(roc_auc_score(y, probs), recorded['roc_auc'], atol=1e-12)
        assert np.isclose(brier_score_loss(y, probs), recorded['brier'], atol=1e-12)
    print(f'PASS: {checked} external target/cohort metrics and 4 source OOF pairs reproduced; hashes match')


if __name__ == '__main__':
    main()
