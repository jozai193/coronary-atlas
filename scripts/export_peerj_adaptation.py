"""Ship a compact derived summary and exact full metrics for development evidence."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'output/research/peerj_adaptation_v1'
manifest=json.loads((folder/'evidence_manifest.json').read_text())
source=folder/'results.json'
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['files']['results.json']
result=json.loads(source.read_text())
items=[('64','source','Frozen source'),('64','constant','Local prevalence'),('64','offset','Intercept adjustment'),
       ('64','sigmoid','Sigmoid recalibration'),('64','local_logistic','Local logistic'),('all','local_logistic','Local logistic')]
rows=[]
for budget,method,label in items:
    r=result['budgets'][budget]
    rows.append(dict(method=method,label=label,budget='0' if method=='source' else ('64' if budget=='64' else '442–443'),
                     **r['mean'][method],
                     false_negatives=[rep[method]['confusion']['fn'] for rep in r['repeats'].values()],
                     false_positives=[rep[method]['confusion']['fp'] for rep in r['repeats'].values()]))
summary=dict(scope=result['scope'],unique_people=553,repeats=2,source_sha256=manifest['files']['results.json'],rows=rows,
             primary=result['budgets']['64']['comparisons']['sigmoid'],primary_screen=result['budgets']['64']['followup_screen']['sigmoid'])
dest=ROOT/'frontend/src/generated'
(dest/'peerj-adaptation-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
(dest/'peerj-adaptation-results.json').write_bytes(source.read_bytes())
print('Exported frozen adaptation metrics and compact derived summary.')
