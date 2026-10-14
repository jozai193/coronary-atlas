"""Extract only named structures from the official BodyParts3D archive."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import zipfile
import numpy as np
from ml.schema import ROOT,digest,write_json

MAPPING={
    'lad':['FMA74912'], 'lcx':['FMA3895'], 'rca':['FMA3802'],
    'heart':['FMA13884','FMA9457','FMA9531'], 'aorta':['FMA3736'],
    'left_main':['FMA3855'],
    # Atlas context only: no branch-level target labels exist in the dataset.
    'context_branches':['FMA3860','FMA3892','FMA3818','FMA3840','FMA3815','FMA3837','FMA3868'],
    'coronary_sinus':['FMA4706'], 'pulmonary_trunk':['FMA8612'],
    'cardiac_veins':['FMA4707','FMA4712','FMA4713','FMA4714','FMA76767'],
    'atrial_chambers':['FMA9465','FMA11359'],
    'ventricular_chambers':['FMA9291','FMA9466'],
    'valve_leaflets':['FMA7238','FMA7239','FMA7240','FMA7242','FMA7243','FMA7247','FMA7249','FMA7250','FMA7252','FMA7253','FMA7254'],
    'papillary_muscles':['FMA7260','FMA7261','FMA7262','FMA7264'],
}


def main():
    entries=[line.split('\t') for line in (ROOT/'docs/sources/bodyparts-elements.txt').read_text().splitlines() if line.startswith('FMA')]
    archive=ROOT/'data/raw/bodyparts3d.zip'
    out=ROOT/'frontend/public/anatomy'; out.mkdir(parents=True,exist_ok=True)
    manifest={}; allverts=[]; used=set()
    with zipfile.ZipFile(archive) as z:
        for label,ids in MAPPING.items():
            components=sorted(set(e[2] for e in entries if e[0] in ids))
            if not components: raise ValueError(f'No source geometry for {label}')
            files=[]
            for c in components:
                if c in used: raise ValueError(f'Duplicate mapped mesh {c}')
                used.add(c)
                name=f'isa_BP3D_4.0_obj_99/{c}.obj'
                raw=z.read(name)
                path=out/f'{c}.obj'; path.write_bytes(raw)
                vertices=np.array([[float(x) for x in line.split()[1:4]] for line in raw.decode().splitlines() if line.startswith('v ')])
                faces=sum(line.startswith('f ') for line in raw.decode().splitlines())
                if len(vertices)==0 or faces==0: raise ValueError(f'Empty geometry {c}')
                if label=='heart': allverts.extend(vertices.tolist())
                files.append(dict(file=f'/anatomy/{c}.obj',sha256=digest(path),vertices=len(vertices),faces=faces,bounds=[vertices.min(axis=0).tolist(),vertices.max(axis=0).tolist()]))
            manifest[label]=dict(fma=ids,files=files,predicted=label in ('lad','lcx','rca'))
    vertices=np.array(allverts)
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    scale=3.5/max(vertices.max(axis=0)-vertices.min(axis=0))
    write_json(out/'manifest.json',dict(source='https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html',license='CC BY 4.0',credit='BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International',center=center.tolist(),scale=float(scale),structures=manifest))
    write_json(ROOT/'assets/anatomy_provenance.json',dict(archive_sha256=digest(archive),manifest_sha256=digest(out/'manifest.json'),mapping=MAPPING))
    print('Extracted',sum(len(v['files']) for v in manifest.values()),'meshes; center',center,'scale',scale)


if __name__=='__main__': main()
