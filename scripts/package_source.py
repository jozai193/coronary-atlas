"""Create a portable source/evidence bundle, excluding local environments and logs."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'output/release';out.mkdir(parents=True,exist_ok=True)
archive=out/'coronary-atlas-source.zip'
listed=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
paths=sorted(set(listed))
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for relative in paths:
        path=ROOT/relative
        if path.is_file():z.write(path,arcname='coronary-atlas/'+relative)
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
(out/'manifest.json').write_text(json.dumps(dict(file=archive.name,sha256=digest,files=len(paths),bytes=archive.stat().st_size),indent=2))
print(f'{archive}: {len(paths)} files, SHA256 {digest}')
