"""Export the frozen research result byte-for-byte for the evidence panel."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'output/research/peerj_v1/results.json'
manifest = json.loads((source.parent / 'evaluation_manifest.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['results.json']
target = ROOT / 'frontend/src/generated/peerj-external-results.json'
target.write_bytes(source.read_bytes())
print(f'Exported {target.name}: {manifest["results.json"]}')
