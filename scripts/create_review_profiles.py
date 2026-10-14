"""Two complete, contrasting public-source demo cases; never new evaluation."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml.schema import ROOT,FEATURES,NUMERIC,TARGETS,read_data,write_json


def create():
    # Select by recorded labels and original row order, before model scoring.
    from backend.main import validate_features
    from fastapi import HTTPException
    frame=read_data()
    schema=json.loads((ROOT/'models/metadata.json').read_text(encoding='utf-8'))['feature_schema']
    chosen=[]
    for key,positive in [('a',False),('b',True)]:
        for index,row in frame.iterrows():
            labels={target:str(row[column]) for target,column in TARGETS.items()}
            matches=(labels['cad']=='CAD' and all(labels[t]=='Stenotic' for t in ['lad','lcx','rca'])) if positive else (labels['cad']=='Normal' and all(labels[t]=='Normal' for t in ['lad','lcx','rca']))
            if not matches or row[FEATURES].isna().any():continue
            features={name:float(row[name]) if name in NUMERIC else str(row[name]) for name in FEATURES}
            try:_,missing,_=validate_features(features,schema)
            except HTTPException:continue
            if missing:continue
            chosen.append(dict(id=key,name=f'Profile {key.upper()} · recorded source · age {int(row["Age"])}',synthetic=False,
                note='Complete public UCI development record, selected by recorded outcome contrast and source row order before scoring. All 55 inputs are recorded. No original ECG/echo report or measured narrowing is available. This deliberately selected demonstration is not independent validation or a representative performance sample.',
                features=features,recorded_outcomes=labels,
                source=dict(url='https://doi.org/10.24432/C5461K',record_index=int(index),worksheet_row=int(index)+2,license='CC BY 4.0',used_in_development=True),
                provenance=dict(recorded_fields=list(FEATURES),explicit_fields=[],derived_fields=[],default_fields=[],unknown_fields=[],default_method='Exact recorded source row; no synthetic defaults.',clinician_reviewed=False)))
            break
        else:raise ValueError(f'No complete supported source case for profile {key}')
    return chosen


if __name__=='__main__':write_json(ROOT/'data/processed/reviewer_samples_v2.json',create())
