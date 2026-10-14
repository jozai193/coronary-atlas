"""Aggregate-only compatibility audit; does not fit or score any patients."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import openpyxl
import pandas as pd
from ml.schema import ROOT, digest, write_json


def main():
    folder = ROOT / 'data/external_audit/stress_ctp_v1'
    path = folder / 'raw/Database Blinded.xlsx'
    metadata = json.loads((folder / 'source_metadata.json').read_text(encoding='utf-8-sig'))
    expected = metadata['files'][0]['content_details']['sha256_hash']
    if digest(path) != expected:
        raise ValueError('Provider workbook hash mismatch')
    df = pd.read_excel(path)
    rows = df[df.ID.notna()]
    wb = openpyxl.load_workbook(path, data_only=True)
    columns = list(df.columns[1:13]) + ['LAD_ICA_summary', 'LCX_ICA_summary', 'RCA_ICA_summary', 'PTS_ICA_summary']
    audit = {'source': 'https://data.mendeley.com/datasets/smwx5gzvxn/1',
        'title': metadata['name'], 'contributor': 'Gianluca Pontone', 'license': 'CC BY 4.0',
        'sha256': digest(path), 'provider_hash_matches': True,
        'raw_sheet_rows_after_header': len(df), 'participant_rows_with_id': len(rows),
        'unique_ids': int(rows.ID.nunique()), 'worksheet_columns': len(df.columns),
        'sheets': [{'name': s.title, 'state': s.sheet_state} for s in wb],
        'cell_comments': sum(c.comment is not None for s in wb for r in s for c in r),
        'named_ranges': list(wb.defined_names),
        'data_validation_lists': sum(len(s.data_validations.dataValidation) for s in wb),
        'columns': {c: {'nonmissing': int(rows[c].notna().sum()), 'distinct': int(rows[c].nunique()),
            'counts': {str(k): int(v) for k, v in rows[c].value_counts().items()}} for c in columns},
        'decision': 'Not fitted or scored. No age/sex columns; demographic and clinical-history sections empty. Risk-factor and symptom code meanings are not established by a workbook dictionary. Imaging stress/procedure fields are not substitutes for pre-test app inputs. ICA summary labels require an explicit stenosis/branch definition before mapping; FFR and CTP outcomes are different endpoints.',
        'potential_followup': 'Authoritative code and endpoint definitions could support a separate limited-risk-factor transport study. This is not compatible independent validation of the 55-input app.',
        'trained': False, 'scored': False}
    write_json(folder / 'audit.json', audit)
    print(json.dumps({k: audit[k] for k in ('participant_rows_with_id', 'unique_ids', 'worksheet_columns', 'decision')}, indent=2))


if __name__ == '__main__':
    main()
