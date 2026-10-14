"""Schema/provenance audit only. Deliberately does not derive a CAD label or score."""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data/external_audit/beijing_v1/raw'
EXPECTED = {
    'peerj-12-17012-s002.xlsx': 'e47714c34fa62dd5afb4c39f6ae0d24eaad059e9ac4cfb88fc63419d710ff54f',
    'peerj-12-17012-s003.docx': 'f78f4fe84c6f844bac8d2e1952b3b7df8d7dd29e05bc91662773b3b435bef025',
    'PMC10921929.1.xml': '4d41c351f0b6b3fc696857f76b37ac9c75e5dc7058a99b9f8502333005fac040',
}
for name, digest in EXPECTED.items():
    assert hashlib.sha256((RAW/name).read_bytes()).hexdigest() == digest
df = pd.read_excel(RAW/'peerj-12-17012-s002.xlsx')
with zipfile.ZipFile(RAW/'peerj-12-17012-s003.docx') as z:
    root = ET.fromstring(z.read('word/document.xml'))
    codebook = [''.join(n.itertext()) for n in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')]
vessels = next(c for c in df if c.startswith('Number of diseased vessels:'))
out = dict(status='not_scored_population_and_endpoint_unresolved', paper_doi='10.7717/peerj.17012',
           acquired_utc_date='2026-10-10', official_base='https://pmc-oa-opendata.s3.amazonaws.com/PMC10921929.1/',
           sha256=EXPECTED, workbook_rows=len(df), paper_enrolled=2970, paper_final_analysis=2045,
           paper_previous_pci_exclusions=923, columns=list(df), missing=df.isna().sum().to_dict(),
           exact_duplicate_rows=int(df.duplicated().sum()), vessel_codes={str(k):int(v) for k,v in df[vessels].value_counts(dropna=False).items()},
           codebook_text=''.join(codebook),
           blockers=['No participant identifier or prior-PCI/analysis-inclusion flag to reconstruct the published 2045 subset.',
                     'Vessel code 2 is described only as 0.5; a binary CAD endpoint is not explicitly supplied.',
                     'Thirty rows lack vessel counts; 2970 minus 923 is 2047 rather than the reported 2045.',
                     'The prior 14-input contract lacks HB, K, Na and PLT in this workbook.'])
dest=ROOT/'data/external_audit/beijing_v1/schema_audit.json'
dest.write_text(json.dumps(out,indent=2,ensure_ascii=True,allow_nan=False)+'\n',encoding='utf-8')
print('Schema audit saved; no CAD labels derived, no patients scored.')
