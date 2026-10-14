"""Exact selected A/B public benchmark rows for field review; never new evaluation."""
from pathlib import Path
import argparse
import html
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ml.schema import FEATURES,TARGETS,read_data,digest

DEST=ROOT/'frontend/public/review'
SOURCE=ROOT/'data/raw/extention of Z-Alizadeh sani dataset.xlsx'


def render(number,record,schema,source_hash,record_index=None):
    record_index=number-1 if record_index is None else record_index
    esc=lambda v:html.escape(str(v),quote=True)
    groups=list(dict.fromkeys(f['group'] for f in schema))
    body=[]
    for group in groups:
        rows=[]
        for f in schema:
            if f['group']!=group:continue
            value=record[f['name']]
            # Preserve supplied codes exactly instead of inventing clinical definitions.
            value=str(value)
            rows.append(f'<tr><th>{esc(f["label"])}</th><td>{esc(value)}</td><td>{esc(f["unit"]) if f["kind"]=="number" else "Source category/code"}</td></tr>')
        body.append(f'<section><h2>{esc(group)}</h2><table><thead><tr><th>Observation</th><th>Original value</th><th>Unit / coding</th></tr></thead><tbody>{"".join(rows)}</tbody></table></section>')
    labels=''.join(f'<tr><th>{esc(target.upper())}</th><td>{esc(record[name])}</td></tr>' for target,name in TARGETS.items())
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'"><title>Public benchmark record {number} — field review</title><style>body{{font:14px/1.6 system-ui;color:#19383e;background:#fff;max-width:950px;margin:30px auto;padding:0 20px}}h1,h2{{color:#12685e;line-height:1.3}}h1{{font-size:25px}}h2{{font-size:19px;margin-top:28px}}.context{{background:#edf6f2;border-left:4px solid #268c79;padding:16px}}table{{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12px}}th,td{{border:1px solid #ccdcd8;text-align:left;vertical-align:top;padding:9px;overflow-wrap:anywhere}}thead{{background:#edf6f2}}.hash{{overflow-wrap:anywhere;font-size:11px}}a{{color:#12685e}}@media print{{body{{margin:0;padding:0;font-size:11px}}tr{{break-inside:avoid}}thead{{display:table-header-group}}}}</style><body><h1>Public benchmark record {number}</h1><div class="context"><p><strong>Exact tabular source record — not an original hospital report.</strong></p><p>UCI Extension of Z-Alizadeh Sani, first two consecutive records selected by row order before any new scoring. This sheet contains row index {number-1}, worksheet row {number+1}, from Sheet 1 - Table 1. No identity, symptom narrative, ECG tracing or echo image is supplied.</p><p>All 303 source records were used for model development. The labels below are recorded dataset labels, not new predictions or independent validation. The full input values are reproduced without filling, recoding or selecting a case by model performance.</p><p>Numeric units follow the app's conventional interpretations; the original unit/code/timing dictionary is incomplete. A source code of 0 is preserved as a code and does not establish that an entire test was normal.</p></div>{''.join(body)}<section><h2>Recorded target labels — not predictions</h2><table><thead><tr><th>Target</th><th>Original label</th></tr></thead><tbody>{labels}</tbody></table></section><section><h2>What to review</h2><p>Which source-field definitions, units or combinations need clarification? Can the recorded ECG/echo findings and coronary labels be distinguished? Flag exact corrections and uncertainty; this sheet does not supply clinical sign-off or original investigation reports.</p></section><footer><p>Source: Alizadehsani, Roshanzamir and Sani, <a href="https://doi.org/10.24432/C5461K">UCI Extension of Z-Alizadeh Sani</a>, CC BY 4.0. Original values retained; layout and English field labels added by Coronary Atlas.</p><p class="hash">Original workbook SHA-256: {esc(source_hash)}</p></footer></body></html>'''


def generate(verify=False):
    expected=json.loads((ROOT/'models/metadata.json').read_text(encoding='utf-8'))['raw_sha256']
    assert digest(SOURCE)==expected
    frame=read_data();schema=json.loads((ROOT/'data/processed/feature_schema.json').read_text(encoding='utf-8'))
    assert [f['name'] for f in schema]==FEATURES
    from scripts.create_review_profiles import create
    profiles=create()
    documents={f'source-record-{i+1}.html':render(i+1,frame.iloc[s['source']['record_index']].to_dict(),schema,expected,s['source']['record_index']).replace('first two consecutive records selected by row order before any new scoring','profiles A/B selected by recorded outcome contrast and row order before scoring').replace(f'row index {i}, worksheet row {i+2}',f'row index {s["source"]["record_index"]}, worksheet row {s["source"]["worksheet_row"]}') for i,s in enumerate(profiles)}
    if verify:
        for name,content in documents.items():assert (DEST/name).read_text(encoding='utf-8')==content
        print('PASS: both sheets reproduce exact selected A/B source rows, supplied labels and attribution.')
    else:
        DEST.mkdir(parents=True,exist_ok=True)
        for name,content in documents.items():(DEST/name).write_text(content,encoding='utf-8',newline='\n')
        print('Built two deterministic public-source field-review sheets. No models fitted or scored.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true')
    generate(parser.parse_args().verify)
