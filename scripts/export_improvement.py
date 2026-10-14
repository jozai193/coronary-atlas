"""Publish a compact, traceable view of the bounded experiment to the UI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from ml.schema import ROOT, TARGETS, digest, write_json


def export():
    folder = ROOT/'ml/experiments/improvement_v1'
    manifest = json.loads((folder/'run_manifest.json').read_text())
    assert manifest['code_sha256'] == digest(ROOT/'ml/improvement.py')
    assert manifest['protocol_sha256'] == digest(ROOT/'docs/model_improvement_protocol.md')
    assert manifest['production_metadata_sha256'] == digest(ROOT/'models/metadata.json')
    targets = {}
    for target in TARGETS:
        path = folder/f'{target}.json'
        source = json.loads(path.read_text())
        assert source['complete'] and len(source['repeats']) == 2
        targets[target] = dict(source_sha256=digest(path), runs=[
            dict(seed=r['seed'], policies=r['summary']['baseline']['policies'],
                 auc=r['summary']['baseline']['metrics']['roc_auc'],
                 cutoff_ranges={policy: [min(f['cutoffs']['baseline'][policy]['threshold'] for f in r['folds']),
                                        max(f['cutoffs']['baseline'][policy]['threshold'] for f in r['folds'])]
                                for policy in ['balanced', 'recall80']})
            for r in source['repeats']])
    payload = dict(version='improvement_v1', rows=303, repeats=2,
                   note='Exploratory repeated internal validation; both runs reuse the same 303 people. Cutoffs selected only within each outer training partition. No clinical threshold recommendation.',
                   manifest=manifest, targets=targets)
    write_json(ROOT/'frontend/src/generated/improvement.json', payload)
    print('Exported four targets, two repeats and three cutoff policies; source hashes checked.')
    return payload


if __name__ == '__main__':
    export()
