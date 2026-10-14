"""Check bundled models, dataset and anatomical mesh identities."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml.schema import ROOT,digest

def main():
    metadata=json.loads((ROOT/'models/metadata.json').read_text())
    assert digest(ROOT/'data/raw/extention of Z-Alizadeh sani dataset.xlsx')==metadata['raw_sha256']
    for item in metadata['artifacts'].values():
        assert digest(ROOT/'models'/item['file'])==item['sha256']
    manifest_path=ROOT/'frontend/public/anatomy/manifest.json'
    provenance=json.loads((ROOT/'assets/anatomy_provenance.json').read_text())
    assert digest(manifest_path)==provenance['manifest_sha256']
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    for structure in manifest['structures'].values():
        for item in structure['files']:
            assert digest(ROOT/'frontend/public'/item['file'].lstrip('/'))==item['sha256']
    count=sum(len(s['files']) for s in manifest['structures'].values())
    print(f'Verified raw workbook, four models, anatomical manifest and all {count} meshes.')

if __name__=='__main__': main()
