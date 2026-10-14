"""Audit saved experimental evidence without searching again on the same data."""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_auc_score
from ml.schema import ROOT, TARGETS, digest

FOLDER = ROOT/'ml/experiments/improvement_v1'


def test_experiment_provenance_and_unchanged_production():
    manifest = json.loads((FOLDER/'run_manifest.json').read_text())
    for key, path in [('code_sha256', 'ml/improvement.py'),
                      ('protocol_sha256', 'docs/model_improvement_protocol.md'),
                      ('production_metadata_sha256', 'models/metadata.json'),
                      ('raw_sha256', 'data/raw/extention of Z-Alizadeh sani dataset.xlsx')]:
        assert manifest[key] == digest(ROOT/path)


def test_saved_nested_splits_and_displayed_error_counts():
    display = json.loads((ROOT/'frontend/src/generated/improvement.json').read_text())
    for target in TARGETS:
        path = FOLDER/f'{target}.json'
        source = json.loads(path.read_text())
        assert source['complete']
        assert display['targets'][target]['source_sha256'] == digest(path)
        for repeat, run in enumerate(source['repeats']):
            rows = pd.read_csv(FOLDER/f'{target}_repeat_{repeat+1}.csv', float_precision='round_trip')
            assert sorted(rows.row_index) == list(range(303))
            seen = []
            for fold in run['folds']:
                train, test = set(fold['train_indices']), set(fold['test_indices'])
                assert not train & test and train | test == set(range(303))
                seen.extend(test)
                inner_seen = []
                for inner in fold['inner_splits']:
                    a, b = set(inner['train_indices']), set(inner['test_indices'])
                    assert not a & b and a | b == train and not (a | b) & test
                    inner_seen.extend(b)
                assert sorted(inner_seen) == sorted(train)
                for method in ['baseline', 'expanded']:
                    for policy in ['balanced', 'recall80']:
                        cutoff = fold['cutoffs'][method][policy]['threshold']
                        assert np.all(rows.loc[rows.row_index.isin(test), f'{method}_{policy}_threshold'] == cutoff)
            assert sorted(seen) == list(range(303))
            shown = display['targets'][target]['runs'][repeat]
            assert abs(shown['auc'] - roc_auc_score(rows.y, rows.baseline)) < 1e-12
            for policy in ['fixed', 'balanced', 'recall80']:
                cutoff = .5 if policy == 'fixed' else rows[f'baseline_{policy}_threshold']
                cm = confusion_matrix(rows.y, rows.baseline >= cutoff, labels=[0, 1])
                metric = shown['policies'][policy]
                assert cm.tolist() == metric['confusion_matrix']
                tn, fp, fn, tp = cm.ravel()
                assert abs(metric['recall'] - tp/(tp+fn)) < 1e-12
                assert abs(metric['specificity'] - tn/(tn+fp)) < 1e-12
                assert abs(metric['precision'] - tp/(tp+fp)) < 1e-12


def test_first_repeat_reproduces_original_baseline():
    original = json.loads((ROOT/'ml/metrics/evaluation.json').read_text())
    for target in TARGETS:
        run = json.loads((FOLDER/f'{target}.json').read_text())['repeats'][0]
        for name in ['roc_auc', 'brier', 'recall', 'specificity']:
            assert abs(run['summary']['baseline']['metrics'][name] - original['targets'][target]['metrics'][name]) < 1e-12
