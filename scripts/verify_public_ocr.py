"""Replay a frozen public-specimen OCR protocol through the real browser UI.

Requires an authenticated local playwright-cli session and already rendered,
hash-checked inputs. Source PDFs/images/transcripts stay in ignored tmp/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocol', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--session', default='heart-colors')
    args = parser.parse_args()
    protocol_path = ROOT / args.protocol
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    if sha(ROOT / 'frontend/src/reportParser.ts') != protocol['parser_sha256']:
        raise ValueError('Parser changed after protocol freeze; create a new version, retain old results.')
    for case in protocol['cases']:
        if sha(ROOT / case['image']) != case['image_sha256']:
            raise ValueError(f"Image hash mismatch: {case['id']}")
    cases = [{**c, 'image': str(ROOT / c['image'])} for c in protocol['cases']]
    code = '''async (page) => {
      const cases=CASES;
      await page.route('**/*kaspersky-labs.com/**',route=>route.abort());
      await page.reload();
      await page.getByRole('button',{name:/Explore profile R1 Age/}).waitFor();
      const results=[],requests=[];
      const record=r=>{if(r.method()!=='GET')requests.push({method:r.method(),origin:new URL(r.url()).origin,path:new URL(r.url()).pathname})};
      page.on('request',record);
      try {
        const panel=page.locator('.report-import');
        if((await panel.getAttribute('open'))===null)await panel.locator('summary').click();
        for(const item of cases){
          await panel.getByRole('button',{name:'Clear report',exact:true}).click();
          const started=Date.now();
          await panel.getByLabel('Choose report image',{exact:true}).setInputFiles(item.image);
          await panel.locator('.report-message').filter({hasText:'Text read.'}).waitFor({timeout:60000});
          const proposals=await panel.locator('.report-candidate').evaluateAll(rows=>rows.map(row=>{
            const checkbox=row.querySelector('input[type=checkbox]');
            const numeric=row.querySelector('input[type=number]');
            const label=row.querySelector('label');
            const value=numeric?Number(numeric.value):Array.from(label.childNodes).filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim();
            return {field:checkbox.getAttribute('aria-label').replace('Confirm ',''),value,issue:row.querySelector('.report-error')?.textContent||'',confirmed:checkbox.checked};
          }));
          if(proposals.some(p=>p.confirmed))throw Error('Autoconfirmed OCR output');
          results.push({id:item.id,seconds:(Date.now()-started)/1000,proposals});
        }
        await panel.getByRole('button',{name:'Clear report',exact:true}).click();
        return {results,non_get_requests:requests,device_script_isolation:'Known antivirus-injected kaspersky-labs.com requests blocked only in this test page; device settings unchanged.'};
      } finally {page.off('request',record)}
    }'''.replace('CASES', json.dumps(cases))
    script = ROOT / 'tmp/verify-public-ocr.cjs'
    script.write_text(code, encoding='utf-8')
    completed = subprocess.run(['npx.cmd', '--yes', '--package', '@playwright/cli',
        'playwright-cli', f'-s={args.session}', 'run-code', '--filename', str(script)],
        cwd=ROOT, text=True, encoding='utf-8', capture_output=True, timeout=600)
    (ROOT / 'tmp/ocr-independent-20261014/browser-replay.txt').write_text(completed.stdout + completed.stderr, encoding='utf-8')
    if completed.returncode or '### Error' in completed.stdout:
        raise RuntimeError('Browser replay failed; inspect ignored browser-replay.txt')
    result_text = completed.stdout.split('### Result\n', 1)[1].split('\n### ', 1)[0]
    receipt = json.loads(result_text)
    correct = incorrect = eligible = 0
    for observed, case in zip(receipt['results'], protocol['cases'], strict=True):
        assert observed['id'] == case['id']
        unflagged = [p for p in observed['proposals'] if not p['issue']]
        observed['incorrect_unflagged'] = [p for p in unflagged if case['facts'].get(p['field']) != p['value']]
        observed['correct_unflagged'] = [p for p in unflagged if case['facts'].get(p['field']) == p['value']]
        found = {p['field'] for p in observed['correct_unflagged']}
        observed['missed_eligible'] = [f for f in case['eligible_fields'] if f not in found]
        correct += len(observed['correct_unflagged'])
        incorrect += len(observed['incorrect_unflagged'])
        eligible += len(case['eligible_fields'])
    receipt.update(protocol_sha256=sha(protocol_path),parser_sha256=protocol['parser_sha256'],
        pages=len(receipt['results']),source_documents=len(protocol['sources']),
        correct_unflagged=correct,incorrect_unflagged=incorrect,eligible_fields=eligible,
        coverage=correct/eligible if eligible else None,
        unflagged_precision=correct/(correct+incorrect) if correct+incorrect else None,
        scope=protocol['scope'],
        generalization='Pages cluster within three specimen documents, not independent patients. No clinical OCR or model-accuracy validation.')
    output = ROOT / args.output
    if output.exists():
        raise FileExistsError('Do not overwrite an existing evaluation receipt')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['pages','source_documents','correct_unflagged','incorrect_unflagged','eligible_fields','coverage','unflagged_precision','non_get_requests']},indent=2))


if __name__ == '__main__':
    main()
