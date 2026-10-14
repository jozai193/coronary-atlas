"""Package four coarse, de-identified teaching cases from saved outer-fold results.

The cases are deliberately selected across the CAD confusion matrix. They are
not a representative performance sample, and no fitted full-data model is run.
"""
import csv
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.schema import ROOT, TARGETS, digest, read_data, write_json

OUTPUT = ROOT / 'data/processed/heldout_cases.json'
SOURCE = ROOT / 'data/raw/extention of Z-Alizadeh sani dataset.xlsx'
EVALUATION = ROOT / 'ml/metrics/evaluation.json'


def band(value: float, width: int, unit: str) -> str:
    low = math.floor(float(value) / width) * width
    separator = '' if unit == '%' else ' '
    return f'{low}–{low + width - 1}{separator}{unit}'


def build_cases() -> dict:
    df = read_data()
    evaluation = json.loads(EVALUATION.read_text(encoding='utf-8'))
    if len(df) != 303 or evaluation['threshold'] != 0.5:
        raise ValueError('Unexpected source row count or evaluation threshold.')
    oof = {}
    oof_hashes = {}
    for target, column in TARGETS.items():
        path = ROOT / f'ml/metrics/{target}_oof.csv'
        oof_hashes[target] = digest(path)
        with path.open(newline='', encoding='utf-8') as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) != len(df) or {int(row['row_index']) for row in rows} != set(range(len(df))):
            raise ValueError(f'{target}: outer-fold rows do not cover the source exactly once.')
        expected_folds = {
            row_index: int(fold['fold'])
            for fold in evaluation['targets'][target]['folds']
            for row_index in fold['test_indices']
        }
        if len(expected_folds) != len(df):
            raise ValueError(f'{target}: evaluation folds are incomplete.')
        by_index = {}
        for row in rows:
            index = int(row['row_index'])
            probability = float(row['p'])
            label = int(row['y'])
            fold = int(row['fold'])
            source_label = int(df.iloc[index][column] == ('CAD' if target == 'cad' else 'Stenotic'))
            if not 0 <= probability <= 1 or not math.isfinite(probability) or label != source_label or fold != expected_folds[index]:
                raise ValueError(f'{target}: saved prediction, label, or fold does not match the source evidence.')
            by_index[index] = dict(probability=probability, label=label, fold=fold)
        oof[target] = by_index

    # Equal representation of TP, TN, FP and FN is intentional for teaching.
    # Median probability within each quadrant avoids picking its most dramatic row.
    quadrants = [(1, 1), (0, 0), (0, 1), (1, 0)]
    chosen = []
    for label, predicted in quadrants:
        indices = [i for i, item in oof['cad'].items()
                   if item['label'] == label and int(item['probability'] >= 0.5) == predicted]
        if not indices:
            raise ValueError(f'No CAD row in teaching quadrant {(label, predicted)}.')
        probabilities = sorted(oof['cad'][i]['probability'] for i in indices)
        middle = probabilities[len(probabilities) // 2]
        chosen.append(min(indices, key=lambda i: (abs(oof['cad'][i]['probability'] - middle), i)))

    cases = []
    for letter, index in zip('ABCD', chosen):
        row = df.iloc[index]
        cases.append(dict(
            id=letter,
            observations=[
                dict(label='Age band', value=band(row['Age'], 10, 'years')),
                dict(label='Blood pressure band', value=band(row['BP'], 20, 'mmHg')),
                dict(label='LDL band', value=band(row['LDL'], 25, 'mg/dL')),
                dict(label='Echo EF band', value=band(row['EF-TTE'], 10, '%')),
            ],
            targets={target: oof[target][index] for target in TARGETS},
        ))
    return dict(
        schema_version=1,
        source='UCI Extension of Z-Alizadeh Sani (303 records)',
        source_url='https://doi.org/10.24432/C5461K',
        source_sha256=digest(SOURCE),
        evaluation_sha256=digest(EVALUATION),
        oof_sha256=oof_hashes,
        method='Four rows deliberately chosen from the CAD true-positive, true-negative, false-positive and false-negative groups; median out-of-fold probability within each group.',
        note='Original source-cohort teaching cases. Each target uses its saved outer-fold raw probability and label; target folds may differ. Not a representative sample, independent validation, live inference or a SHAP explanation.',
        cases=cases,
    )


if __name__ == '__main__':
    write_json(OUTPUT, build_cases())
    print(f'Wrote {OUTPUT}')
