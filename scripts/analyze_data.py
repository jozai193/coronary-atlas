"""Write descriptive EDA; never modifies the original workbook."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from ml.schema import *


def main():
    df = read_data()
    out = ROOT / 'data/processed'
    out.mkdir(exist_ok=True)
    df.to_csv(out / 'clinical.csv', index=False)
    metadata = feature_metadata(df)
    write_json(out / 'feature_schema.json', metadata)
    rows = []
    for c in df:
        numeric = c in NUMERIC
        q1, q3 = (df[c].quantile([.25, .75]) if numeric else (0, 0))
        count = int(((df[c] < q1 - 1.5 * (q3-q1)) | (df[c] > q3 + 1.5 * (q3-q1))).sum()) if numeric else None
        rows.append(dict(column=c, dtype=str(df[c].dtype), missing=int(df[c].isna().sum()), distinct=int(df[c].nunique()), iqr_flags=count, values=f'{df[c].min():.3g} to {df[c].max():.3g}; median {df[c].median():.3g}' if numeric else str(df[c].value_counts().to_dict())))
    audit = pd.DataFrame(rows)
    audit.to_csv(out / 'column_audit.csv', index=False)
    numeric_df = df[NUMERIC]
    numeric_df.corr().to_csv(out / 'correlations.csv')
    numeric_df.describe().to_csv(out / 'numeric_summary.csv')
    mismatch = df.index[(df.Cath == 'CAD') != (df[['LAD','LCX','RCA']] == 'Stenotic').any(axis=1)].tolist()
    write_json(out / 'audit.json', dict(rows=len(df), columns=len(df.columns), missing=int(df.isna().sum().sum()), duplicates=int(df.duplicated().sum()), feature_duplicates=int(df[FEATURES].duplicated().sum()), inconsistent_row_indices=mismatch, raw_sha256=digest(ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx')))
    path = ROOT / 'docs/dataset_analysis.md'
    base = path.read_text(encoding='utf-8').split('<!-- GENERATED -->')[0]
    table = '\n'.join('| ' + ' | '.join(str(row[k]) for k in ['column','dtype','missing','distinct','iqr_flags','values']) + ' |' for row in rows)
    path.write_text(base + '\n<!-- GENERATED -->\n## Executed per-column audit\n\nIQR flags are descriptive, not deletion decisions. Numeric-coded categories use string representation for one-hot encoding.\n\n| Column | Pipeline dtype | Missing | Distinct | IQR flags | Range or counts |\n|---|---|---:|---:|---:|---|\n' + table + f'\n\nCAD/vessel disagreement, zero-based row indices: {mismatch}. Original worksheet row numbers are index + 2.\n\nRaw workbook SHA256: `{digest(ROOT / "data/raw/extention of Z-Alizadeh sani dataset.xlsx")}`.\n', encoding='utf-8')
    print('EDA complete:', df.shape, 'label discrepancy:', mismatch)


if __name__ == '__main__':
    main()
