"""Explicit input contract. Source spellings are intentionally preserved."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261007
TARGETS = {'cad': 'Cath', 'lad': 'LAD', 'lcx': 'LCX', 'rca': 'RCA'}
PROHIBITED = frozenset(TARGETS.values())
GROUPS = {
    'Demographics': ['Age', 'Sex', 'Weight', 'Length', 'BMI'],
    'Vitals': ['BP', 'PR'],
    'History & examination': ['DM', 'HTN', 'Current Smoker', 'EX-Smoker', 'FH', 'Obesity', 'CRF', 'CVA', 'Airway disease', 'Thyroid Disease', 'CHF', 'DLP', 'Edema', 'Weak Peripheral Pulse', 'Lung rales', 'Systolic Murmur', 'Diastolic Murmur', 'Typical Chest Pain', 'Dyspnea', 'Function Class', 'Atypical', 'Nonanginal', 'Exertional CP', 'LowTH Ang'],
    'ECG': ['Q Wave', 'St Elevation', 'St Depression', 'Tinversion', 'LVH', 'Poor R Progression', 'BBB'],
    'Laboratory': ['FBS', 'CR', 'TG', 'LDL', 'HDL', 'BUN', 'ESR', 'HB', 'K', 'Na', 'WBC', 'Lymph', 'Neut', 'PLT'],
    'Echocardiography': ['EF-TTE', 'Region RWMA', 'VHD'],
}
FEATURES = [c for group in GROUPS.values() for c in group]
NUMERIC = ['Age', 'Weight', 'Length', 'BMI', 'BP', 'PR', 'FBS', 'CR', 'TG', 'LDL', 'HDL', 'BUN', 'ESR', 'HB', 'K', 'Na', 'WBC', 'Lymph', 'Neut', 'PLT', 'EF-TTE']
CATEGORICAL = [c for c in FEATURES if c not in NUMERIC]
LABELS = {'Length': 'Height', 'DM': 'Diabetes mellitus', 'HTN': 'Hypertension history', 'FH': 'Family history', 'CRF': 'Chronic renal failure', 'CVA': 'Cerebrovascular history', 'CHF': 'Heart failure history', 'DLP': 'Dyslipidemia', 'BP': 'Blood pressure', 'PR': 'Pulse rate', 'FBS': 'Fasting blood sugar', 'CR': 'Creatinine', 'TG': 'Triglycerides', 'LDL': 'LDL cholesterol', 'HDL': 'HDL cholesterol', 'BUN': 'Blood urea nitrogen', 'ESR': 'Erythrocyte sedimentation rate', 'HB': 'Hemoglobin', 'K': 'Potassium', 'Na': 'Sodium', 'WBC': 'White blood cells', 'Lymph': 'Lymphocytes', 'Neut': 'Neutrophils', 'PLT': 'Platelets', 'EF-TTE': 'Echo ejection fraction', 'Region RWMA': 'RWMA region code', 'VHD': 'Valvular disease', 'Tinversion': 'T-wave inversion', 'LVH': 'Left ventricular hypertrophy', 'BBB': 'Bundle branch block', 'LowTH Ang': 'Low-threshold angina', 'Function Class': 'Functional class code', 'St Elevation': 'ST elevation', 'St Depression': 'ST depression'}
UNITS = {'Age': 'years', 'Weight': 'kg', 'Length': 'cm', 'BMI': 'kg/m²', 'BP': 'mmHg', 'PR': 'beats/min', 'FBS': 'mg/dL', 'CR': 'mg/dL', 'TG': 'mg/dL', 'LDL': 'mg/dL', 'HDL': 'mg/dL', 'BUN': 'mg/dL', 'ESR': 'mm/h', 'HB': 'g/dL', 'K': 'mEq/L', 'Na': 'mEq/L', 'WBC': '/µL', 'Lymph': '%', 'Neut': '%', 'PLT': '10³/µL', 'EF-TTE': '%'}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_data():
    import pandas as pd
    path = ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'
    df = pd.read_excel(path, sheet_name='Sheet 1 - Table 1')
    if set(df.columns) != set(FEATURES) | PROHIBITED:
        raise ValueError('Unexpected dataset schema; inspect source before training.')
    for c in CATEGORICAL:
        df[c] = df[c].astype(str)
    return df


def feature_metadata(df):
    return [dict(name=c, label=LABELS.get(c, c), group=g,
                 kind='number' if c in NUMERIC else 'category',
                 unit=UNITS.get(c, 'source code'),
                 unit_note='Conventional interpretation; original UCI unit dictionary incomplete.',
                 minimum=float(df[c].min()) if c in NUMERIC else None,
                 maximum=float(df[c].max()) if c in NUMERIC else None,
                 options=None if c in NUMERIC else sorted(df[c].unique().tolist()))
            for g, cols in GROUPS.items() for c in cols]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
