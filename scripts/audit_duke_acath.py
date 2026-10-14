"""Download and summarize Duke ACATH public cohort without retaining row-level output."""
import hashlib, json
from io import BytesIO
from pathlib import Path
import requests
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]

URL = 'https://hbiostat.org/data/repo/acath.dta'
RAW = ROOT / 'data/external_audit/duke_acath_v1/raw/acath.dta'
OUT = ROOT / 'data/external_audit/duke_acath_v1/audit.json'

def main():
    RAW.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    RAW.write_bytes(response.content)
    digest = hashlib.sha256(response.content).hexdigest()
    frame = pd.read_stata(BytesIO(response.content), convert_categoricals=False)
    expected = {'sex', 'age', 'cad_dur', 'choleste', 'sigdz', 'tvdlm'}
    if set(frame.columns) != expected or len(frame) != 3504:
        raise ValueError(f'Unexpected source schema: {frame.shape}, {frame.columns.tolist()}')
    result = {
        'source': URL,
        'source_page': 'https://hbiostat.org/data/repo/acath',
        'download_bytes': len(response.content),
        'sha256': digest,
        'dimensions': {'rows': len(frame), 'columns': len(frame.columns)},
        'columns': list(frame.columns),
        'missing_counts': {k: int(v) for k, v in frame.isna().sum().items()},
        'sigdz_counts': {str(k): int(v) for k, v in frame.sigdz.value_counts(dropna=False).sort_index().items()},
        'tvdlm_counts': {str(k): int(v) for k, v in frame.tvdlm.value_counts(dropna=False).sort_index().items()},
        'sex_counts': {str(k): int(v) for k, v in frame.sex.value_counts(dropna=False).sort_index().items()},
        'age_summary': {k: float(frame.age.describe()[k]) for k in ('min','25%','50%','75%','max','mean')},
        'cholesterol_summary_observed': {k: float(frame.choleste.describe()[k]) for k in ('min','25%','50%','75%','max','mean')},
        'row_level_data_written': False,
        'decision': 'Usable for a separate reduced-input or severe-CAD study only; not compatible with the current 55-input model or same >=50%-stenosis target. Exact shared predictors: age and sex.'
    }
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
