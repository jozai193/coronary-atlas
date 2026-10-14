import json
import hashlib

import pandas as pd
import pytest

from ml.modality_audit import OUT, feature_sets
from ml.schema import FEATURES, PROHIBITED, ROOT, TARGETS, digest


def test_prespecified_feature_sets_stay_within_allowlist():
    sets = feature_sets()
    assert len(sets) == 11
    assert set(sets['all_features']) == set(FEATURES)
    assert set(sets['core']) < set(FEATURES)
    for columns in sets.values():
        assert len(columns) == len(set(columns))
        assert set(columns) <= set(FEATURES)
        assert not set(columns) & PROHIBITED


def test_saved_modality_audit_has_full_fold_and_prediction_evidence():
    results_path = OUT / 'results.json'
    if not results_path.exists():
        pytest.skip('The prespecified modality audit has not been executed.')
    results = json.loads(results_path.read_text(encoding='utf-8'))
    expected_ablation = {
        'core', 'core_plus_ecg', 'core_plus_laboratory', 'core_plus_echo', 'all_features',
        'all_minus_demographics', 'all_minus_vitals', 'all_minus_history',
        'all_minus_ecg', 'all_minus_laboratory', 'all_minus_echocardiography',
    }
    expected_missingness = {
        'complete', 'missing_ecg', 'missing_laboratory',
        'missing_echocardiography', 'core_only',
    }
    assert set(results['feature_sets']) == expected_ablation
    assert set(results['integrity']['prohibited_targets']) == PROHIBITED
    assert results['integrity']['all_features_exactly_match_allowlist']

    for target in TARGETS:
        repeats = results['targets'][target]['repeats']
        assert [repeat['repeat'] for repeat in repeats] == [1, 2]
        for repeat in repeats:
            assert repeat['n_rows'] == 303
            assert set(repeat['ablation']) == expected_ablation
            assert set(repeat['missingness']) == expected_missingness
            seen = []
            for fold in repeat['folds']:
                train = set(fold['train_indices'])
                test = set(fold['test_indices'])
                assert not train & test
                assert len(train) + len(test) == 303
                seen.extend(test)
                assert set(fold['ablation_metrics']) == expected_ablation
                assert set(fold['missingness_metrics']) == expected_missingness
            assert sorted(seen) == list(range(303))

    ablation = pd.read_csv(OUT / 'ablation_predictions.csv')
    missing = pd.read_csv(OUT / 'missingness_predictions.csv')
    assert len(ablation) == 4 * 2 * 303 * len(expected_ablation)
    assert len(missing) == 4 * 2 * 303 * len(expected_missingness)
    for table, scenarios in [(ablation, expected_ablation), (missing, expected_missingness)]:
        assert table['probability'].between(0, 1).all()
        assert (table['classification_at_0_5'] == (table['probability'] >= 0.5).astype(int)).all()
        counts = table.groupby(['target', 'repeat', 'scenario'])['row_index'].agg(['size', 'nunique'])
        assert (counts['size'] == 303).all()
        assert (counts['nunique'] == 303).all()
        assert set(table['scenario']) == scenarios


def test_modality_audit_source_hashes_match_current_sources():
    results_path = OUT / 'results.json'
    if not results_path.exists():
        pytest.skip('The prespecified modality audit has not been executed.')
    results = json.loads(results_path.read_text(encoding='utf-8'))
    for relative_path, expected in results['source_and_runtime']['source_hashes_sha256'].items():
        assert digest(ROOT / relative_path) == expected, relative_path
    ui_summary_path = OUT / 'ui_summary.json'
    ui_summary = json.loads(ui_summary_path.read_text(encoding='utf-8'))
    assert ui_summary['source_results_sha256'] == hashlib.sha256(results_path.read_bytes()).hexdigest()
    assert ui_summary['audit_code_sha256'] == results['source_and_runtime']['source_hashes_sha256']['ml/modality_audit.py']
    assert ui_summary['protocol_sha256'] == results['source_and_runtime']['source_hashes_sha256']['docs/modality_audit_protocol.md']
