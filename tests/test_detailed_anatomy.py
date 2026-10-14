import json
from pathlib import Path
from ml.schema import ROOT,digest


def test_detailed_reference_parts_have_disjoint_verified_source_files():
    manifest_path=ROOT/'frontend/public/anatomy/manifest.json'
    manifest=json.loads(manifest_path.read_text())
    provenance=json.loads((ROOT/'assets/anatomy_provenance.json').read_text())
    assert digest(manifest_path)==provenance['manifest_sha256']
    files=[]
    for name,structure in manifest['structures'].items():
        assert structure['files'] and structure['fma']==provenance['mapping'][name]
        assert structure['predicted']==(name in ('lad','lcx','rca'))
        for item in structure['files']:
            path=ROOT/'frontend/public'/item['file'].lstrip('/')
            assert digest(path)==item['sha256'] and item['vertices']>0 and item['faces']>0
            files.append(item['file'])
    assert len(files)==len(set(files))
    for kind in ('cardiac_veins','atrial_chambers','ventricular_chambers','valve_leaflets','papillary_muscles'):
        assert not manifest['structures'][kind]['predicted']
