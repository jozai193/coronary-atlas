"""Export the fixed-estimator input-group comparison without changing inference."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml.schema import ROOT,digest,write_json

source=ROOT/'ml/experiments/modality_v2/ui_summary.json'
data=json.loads(source.read_text())
assert data['source_results_sha256']==digest(ROOT/'ml/experiments/modality_v2/results.json')
assert data['audit_code_sha256']==digest(ROOT/'ml/modality_audit.py')
assert data['protocol_sha256']==digest(ROOT/'docs/modality_audit_protocol.md')
targets={}
for target,content in data['targets'].items():
    runs=[]
    for run in content['repeats']:
        rows=[dict(name='Clinical core',**run['core'])]
        for name,addition in run['core_additions'].items():
            rows.append(dict(name='Core + '+name,**addition['candidate']))
        rows.append(dict(name='All input groups',**run['all_features']))
        runs.append(dict(seed=run['seed'],rows=rows))
    targets[target]=runs
write_json(ROOT/'frontend/src/generated/modality.json',dict(version='modality_v2',source_sha256=digest(source),targets=targets))
print('Exported fixed-logistic modality evidence with verified source hashes.')
