"""Download the exact public UCI source with an integrity check."""
import hashlib
import io
from pathlib import Path
import sys
import zipfile
import requests
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml.schema import ROOT

URL='https://archive.ics.uci.edu/static/public/411/extention+of+z+alizadeh+sani+dataset.zip'


def main():
    manifest=__import__('json').loads((ROOT/'data/provenance.json').read_text())
    raw=ROOT/'data/raw'; raw.mkdir(parents=True,exist_ok=True)
    existing=raw/manifest['workbook']
    if existing.exists():
        if hashlib.sha256(existing.read_bytes()).hexdigest()!=manifest['workbook_sha256']:
            raise RuntimeError('Existing raw file differs from manifest. Preserve and investigate it; do not overwrite.')
        print('Existing UCI workbook hash verified.'); return
    response=requests.get(URL,timeout=60);response.raise_for_status()
    if hashlib.sha256(response.content).hexdigest()!=manifest['zip_sha256']:
        raise RuntimeError('UCI archive changed; inspect the new source rather than accepting silently.')
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        content=archive.read(manifest['workbook'])
    if hashlib.sha256(content).hexdigest()!=manifest['workbook_sha256']:
        raise RuntimeError('Workbook hash mismatch.')
    (raw/'uci-411.zip').write_bytes(response.content);existing.write_bytes(content)
    print('UCI workbook downloaded and verified.')


if __name__=='__main__': main()
