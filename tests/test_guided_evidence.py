import json
from ml.schema import ROOT,digest
from scripts.prepare_anatomy_anchors import generate


def test_selected_vessel_labels_are_anchored_to_actual_source_vertices():
    stored=json.loads((ROOT/'frontend/src/generated/anatomy-anchors.json').read_text())
    assert stored==generate()
    assert stored['lad']['fma']==['FMA74912']
    assert stored['lcx']['fma']==['FMA3895']
    assert stored['rca']['fma']==['FMA3802']


def test_input_group_ui_matches_saved_repeat_metrics():
    source=ROOT/'ml/experiments/modality_v2/ui_summary.json'
    data=json.loads(source.read_text())
    ui=json.loads((ROOT/'frontend/src/generated/modality.json').read_text())
    assert ui['source_sha256']==digest(source)
    for target in data['targets']:
        for r,run in enumerate(data['targets'][target]['repeats']):
            rows=ui['targets'][target][r]['rows']
            assert ui['targets'][target][r]['seed']==run['seed']
            assert {k:rows[0][k] for k in ['roc_auc','brier']}==run['core']
            assert {k:rows[-1][k] for k in ['roc_auc','brier']}==run['all_features']
            for row in rows[1:-1]:
                name=row['name'].removeprefix('Core + ')
                assert {k:row[k] for k in ['roc_auc','brier']}==run['core_additions'][name]['candidate']
