"""Anchor labels to actual named-vessel vertices in the existing atlas geometry."""
from pathlib import Path
import json
import hashlib
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def generate():
    manifest=ROOT/'frontend/public/anatomy/manifest.json'
    m=json.loads(manifest.read_text(encoding='utf-8'))
    output={}
    for target in ['lad','lcx','rca']:
        points=[]
        for item in m['structures'][target]['files']:
            path=ROOT/'frontend/public'/item['file'].lstrip('/')
            points.extend([[float(v) for v in line.split()[1:4]]
                           for line in path.read_text().splitlines() if line.startswith('v ')])
        vertices=np.array(points)
        center=(vertices.min(0)+vertices.max(0))/2
        # The bounding-box center itself might not touch the artery. Use its
        # nearest mesh vertex, so the endpoint refers to actual source geometry.
        point=vertices[np.linalg.norm(vertices-center,axis=1).argmin()]
        local=(point-np.array(m['center']))*m['scale']
        world=[float(local[0]),float(local[2]),float(-local[1])]
        output[target]=dict(anchor=[round(v,5) for v in world],source_point=point.tolist(),
                            fma=m['structures'][target]['fma'])
    return output


if __name__=='__main__':
    out=ROOT/'frontend/src/generated/anatomy-anchors.json'
    out.write_text(json.dumps(generate(),indent=2),encoding='utf-8')
    print('Saved three anchors at actual atlas vertices; source transforms unchanged.')
