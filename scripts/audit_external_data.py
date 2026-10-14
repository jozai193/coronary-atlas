"""Inspect the downloaded UCI 45 archive without making labels or training data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collections import Counter
from zipfile import ZipFile
from ml.schema import ROOT, digest, write_json

folder = ROOT/'data/external_audit'
archive = folder/'uci45.zip'
with ZipFile(archive) as z:
    result = dict(source='https://archive.ics.uci.edu/dataset/45/heart+disease',
                  download='https://archive.ics.uci.edu/static/public/45/heart%2Bdisease.zip',
                  archive_sha256=digest(archive), license='CC BY 4.0',
                  authors='Andras Janosi, William Steinbrunn, Matthias Pfisterer, Robert Detrano',
                  doi='10.24432/C52P4X', cohorts={})
    for name in ['WARNING', 'ask-detrano']:
        (folder/name).write_bytes(z.read(name))
    for name in ['cleveland.data', 'hungarian.data', 'switzerland.data', 'long-beach-va.data']:
        text = z.read(name).decode('utf-8', errors='replace')
        chunks = [r.split() for r in text.split('name') if r.strip()]
        records = [r for r in chunks if len(r) == 75]
        result['cohorts'][name] = dict(record_chunks=len(chunks), utf8_replacement_characters=text.count('\ufffd'),
            field_count_distribution=dict(Counter(len(r) for r in chunks)),
            shape_valid_records=len(records),
            warning='Token count checks do not establish clinical correctness or vessel code semantics.',
            vessel_values={label:dict(Counter(r[index-1] for r in records))
                for label,index in [('lmt',59),('ladprox',60),('laddist',61),('cxmain',63),('rcaprox',67),('rcadist',68)]})
    result['decision']='Do not merge or claim external validation. Cleveland raw data explicitly marked corrupted; input definitions/coverage and vessel code semantics require harmonization. Missing labels must not become normal labels.'
    write_json(folder/'audit.json', result)
    print(result['decision'])
