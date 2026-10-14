"""Read-only educational cases backed by saved nested outer-fold predictions."""
import json
import math
from typing import Literal

from fastapi import APIRouter, HTTPException

from ml.schema import ROOT, TARGETS, digest

router = APIRouter(prefix='/api/held-out', tags=['held-out teaching cases'])
DATA = ROOT / 'data/processed/heldout_cases.json'


def load_cases() -> dict:
    package = json.loads(DATA.read_text(encoding='utf-8'))
    if package['schema_version'] != 1 or package['evaluation_sha256'] != digest(ROOT / 'ml/metrics/evaluation.json'):
        raise ValueError('Held-out case package does not match the evaluation evidence.')
    for target in TARGETS:
        if package['oof_sha256'][target] != digest(ROOT / f'ml/metrics/{target}_oof.csv'):
            raise ValueError(f'Held-out case package does not match {target} outer-fold predictions.')
    cases = package['cases']
    if len(cases) != 4 or {case['id'] for case in cases} != set('ABCD'):
        raise ValueError('Held-out case set is incomplete.')
    quadrants = set()
    for case in cases:
        if set(case['targets']) != set(TARGETS):
            raise ValueError('Held-out case has incomplete targets.')
        observations = case['observations']
        if ([item.get('label') for item in observations] !=
                ['Age band', 'Blood pressure band', 'LDL band', 'Echo EF band']
                or any(set(item) != {'label', 'value'} or not isinstance(item['value'], str)
                       or '–' not in item['value'] for item in observations)):
            raise ValueError('Held-out case has invalid public observations.')
        for item in case['targets'].values():
            if (not math.isfinite(item['probability']) or not 0 <= item['probability'] <= 1
                    or item['label'] not in (0, 1) or item['fold'] not in range(5)):
                raise ValueError('Held-out case has invalid outer-fold evidence.')
        cad = case['targets']['cad']
        quadrants.add((cad['label'], int(cad['probability'] >= 0.5)))
    if quadrants != {(1, 1), (0, 0), (1, 0), (0, 1)}:
        raise ValueError('Held-out teaching cases must cover all four CAD outcomes.')
    return package


@router.get('/cases')
def case_list():
    package = load_cases()
    return dict(
        source=package['source'],
        source_url=package['source_url'],
        method=package['method'],
        note=package['note'],
        cases=[dict(id=case['id'], observations=case['observations']) for case in package['cases']],
    )


@router.get('/cases/{case_id}/{target}')
def case_reveal(case_id: str, target: Literal['cad', 'lad', 'lcx', 'rca']):
    package = load_cases()
    case = next((item for item in package['cases'] if item['id'] == case_id), None)
    if case is None:
        raise HTTPException(404, detail='Unknown held-out teaching case.')
    evidence = case['targets'][target]
    return dict(case_id=case_id, target=target, probability=evidence['probability'],
                label=evidence['label'], predicted_label=int(evidence['probability'] >= 0.5),
                fold=evidence['fold'] + 1,
                note='Saved raw nested outer-fold prediction for this original-cohort row. No full-data model, SHAP, or coherence adjustment was applied.')
