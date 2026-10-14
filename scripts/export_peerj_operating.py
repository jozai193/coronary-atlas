"""Derived UI summary and exact immutable operating-point metrics download."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'output/research/peerj_operating_v1'
source=folder/'results.json'
manifest=json.loads((folder/'evidence_manifest.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['files']['results.json']
r=json.loads(source.read_text())
items=[('source','fixed_50','Source: fixed 0.5'),('source','target_90','Source: 90% calibration target'),
       ('local_sigmoid','fixed_50','Local + calibration: fixed 0.5'),
       ('local_sigmoid','target_80','Local + calibration: 80% target'),
       ('local_sigmoid','target_90','Local + calibration: 90% target'),
       ('local_sigmoid','target_95','Local + calibration: 95% target')]
rows=[]
for method,point,label in items:
    reps=[v['operating'][method][point] for v in r['repeats'].values()]
    rows.append(dict(method=method,point=point,label=label,**r['mean_operating'][method][point],
                     false_negatives=[v['confusion']['fn'] for v in reps],false_positives=[v['confusion']['fp'] for v in reps],
                     folds_below_target=sum(v['folds_below_calibration_target'] for v in reps) if point!='fixed_50' else None))
summary=dict(scope=r['scope'],reviewer_guidance=r['reviewer_guidance'],source_sha256=manifest['files']['results.json'],
             rows=rows,probabilities=r['mean_probabilities'],primary=r['primary'])
dest=ROOT/'frontend/src/generated'
(dest/'peerj-operating-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
(dest/'peerj-operating-results.json').write_bytes(source.read_bytes())
print('Exported operating-point development summary and exact full metrics.')
