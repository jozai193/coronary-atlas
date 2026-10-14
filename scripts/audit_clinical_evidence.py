"""Aggregate source-capability receipt; never fits models or exports patient rows."""
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.schema import ROOT, FEATURES, PROHIBITED, read_data


def main():
    df = read_data()
    context = (ROOT / 'frontend/src/clinicalContext.ts').read_text(encoding='utf-8')
    context_keys = re.findall(r'^  (\w+):', context, re.M)
    assert len(FEATURES) == 55 and not set(FEATURES) & PROHIBITED
    assert len(context_keys) == 8 and not set(context_keys) & set(FEATURES)
    with zipfile.ZipFile(ROOT / 'data/raw/uci-411.zip') as archive:
        members = archive.namelist()
    workbook = ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'
    receipt = {
        'source': 'https://archive.ics.uci.edu/dataset/411/extention+of+z+alizadeh+sani+dataset',
        'workbook_sha256': hashlib.sha256(workbook.read_bytes()).hexdigest(),
        'rows': len(df), 'model_input_count': len(FEATURES),
        'original_source_archive_members': members,
        'source_archive_report_files': [n for n in members if Path(n).suffix.lower() in ('.pdf', '.png', '.jpg', '.dcm', '.edf', '.hea')],
        'outcome_categories': {c: {str(k): int(v) for k, v in df[c].value_counts().items()} for c in ['Cath', 'LAD', 'LCX', 'RCA']},
        'additional_context_not_in_training_inputs': context_keys,
        'model_weights_modified': False,
        'new_participants_acquired': 0,
        'full_app_independent_validation': 'Not established. Replayed reduced-input external-study receipts are separate experiments.',
        'remaining_requirements': {
            'original_reports_and_narrowing': 'Paired original ECG/echo and angiography/CCTA records with reviewed source definitions. User confirms only public examples are available.',
            'forced_echo_agreement': 'No supported rule: EF, valve findings and CAD/vessel probabilities describe different outcomes. Reconcile source input errors explicitly instead.',
            'alcohol_lifestyle_prediction': 'Compatible pre-outcome alcohol/lifestyle variables and CAD/vessel labels, followed by versioned training and independent validation.',
            'independent_model_validation': 'Unused participants with compatible predictors/endpoints, permissions, timing and participant separation reviewed before scoring.',
        },
        'claim': 'This verifies source/input capability and records remaining evidence gaps. It does not establish clinical performance or prove that no suitable dataset exists elsewhere.',
    }
    output = ROOT / 'output/verification/clinical-evidence-capability-2026-10-14.json'
    if output.exists():
        raise FileExistsError('Preserve the existing capability receipt')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ['rows', 'model_input_count', 'source_archive_report_files', 'additional_context_not_in_training_inputs', 'new_participants_acquired', 'full_app_independent_validation']}, indent=2))


if __name__ == '__main__':
    main()
