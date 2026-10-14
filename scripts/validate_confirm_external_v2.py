"""Two-stage source-only fit and frozen external transport evaluation. No app edits."""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, brier_score_loss

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.schema import ROOT, read_data, digest, write_json, TARGETS
from ml.evaluate import metrics

FEATURES = ['Age', 'BMI', 'LDL', 'HDL']
MAPPING = dict(zip(FEATURES, ['age', 'bmi', 'ldl', 'hdl']))
LABELS = dict(zip(TARGETS, ['stenosis_50', 'lad_50', 'lcx_50', 'rca_50']))
OUT = ROOT/'ml/experiments/confirm_external_v1'
RAW = ROOT/'data/external_audit/v3/CONFIRM_ST_LOCKED2.xlsx'
PROTOCOL = ROOT/'docs/confirm_external_protocol.md'
SOURCE = ROOT/'data/raw/extention of Z-Alizadeh sani dataset.xlsx'


def model():
    return make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                         LogisticRegression(C=.03, max_iter=3000, random_state=20261007))


def app_unchanged():
    frozen=json.loads((ROOT/'data/external_audit/v3/frozen_models.json').read_text())
    for path, expected in frozen['sha256'].items():
        assert digest(ROOT/path)==expected, f'Application changed: {path}'


def fit():
    if (OUT/'fit_manifest.json').exists():
        raise RuntimeError('Frozen source fit already exists; do not overwrite it.')
    app_unchanged()
    OUT.mkdir(parents=True, exist_ok=True)
    source=read_data()
    X=source[FEATURES]
    manifest={'created_utc':datetime.now(timezone.utc).isoformat(), 'features':FEATURES,
              'source_sha256':digest(SOURCE), 'protocol_sha256':digest(PROTOCOL),
              'runner_sha256':digest(Path(__file__)), 'external_sha256':digest(RAW),
              'training_rows':len(source), 'external_rows_used_for_fit':0, 'targets':{}}
    for target, column in TARGETS.items():
        y=(source[column].str.lower() != 'normal').astype(int)
        estimator=model()
        oof=cross_val_predict(estimator,X,y,cv=StratifiedKFold(5,shuffle=True,random_state=20261007),method='predict_proba')[:,1]
        estimator.fit(X,y)
        file=OUT/f'{target}.joblib'
        joblib.dump(estimator,file)
        manifest['targets'][target]={'file':file.name,'sha256':digest(file),
                                    'source_prevalence':float(y.mean()),'source_oof':metrics(y,oof)}
    write_json(OUT/'fit_manifest.json',manifest)
    print('Frozen source-only models:', {k:v['source_oof']['roc_auc'] for k,v in manifest['targets'].items()})


def intervals(y,p):
    rng=np.random.default_rng(20261008)
    auc=[];brier=[]
    for _ in range(500):
        ix=rng.integers(0,len(y),len(y))
        if len(np.unique(y[ix]))!=2:
            continue
        auc.append(roc_auc_score(y[ix],p[ix]));brier.append(brier_score_loss(y[ix],p[ix]))
    return {'roc_auc_95':np.quantile(auc,[.025,.975]).tolist(),
            'brier_95':np.quantile(brier,[.025,.975]).tolist(),'valid_resamples':len(auc),
            'note':'Row bootstrap conditional on fitted model; excludes site clustering and source refit uncertainty.'}


def evaluate():
    if (OUT/'results.json').exists():
        raise RuntimeError('External evaluation already exists. Preserve it; no automatic retesting.')
    app_unchanged()
    manifest=json.loads((OUT/'fit_manifest.json').read_text())
    for p,key in [(RAW,'external_sha256'),(SOURCE,'source_sha256'),(PROTOCOL,'protocol_sha256'),(ROOT/'scripts/validate_confirm_external.py','runner_sha256')]:
        assert digest(p)==manifest[key], f'Frozen identity mismatch: {p}'
    d=pd.read_excel(RAW)
    assert d.confirm_id.notna().all() and d.confirm_id.is_unique
    X=d[list(MAPPING.values())].rename(columns={v:k for k,v in MAPPING.items()}).apply(pd.to_numeric,errors='coerce')
    source=read_data()[FEATURES]
    # Exact four-input overlap is only a conservative fingerprint, not an identity test.
    keys=set(map(tuple,source.to_numpy()))
    overlap=X.apply(lambda r:tuple(r) in keys,axis=1)
    complete=X.notna().all(axis=1)&np.isfinite(X).all(axis=1)
    sane=complete.copy()
    for c,(low,high) in zip(FEATURES,[(30,100),(10,80),(10,500),(5,200)]):
        sane &= X[c].between(low,high)
    no_history=d[['past_mi','past_pci','past_cabg']].eq(0).all(axis=1)
    base=sane&~overlap
    for c in LABELS.values():
        observed=set(d[c].dropna().unique())
        if not observed<= {0,1}:
            raise ValueError(f'Unmapped outcome codes: {c}: {observed}')
    checkcols=['lm_50','lad_50','lcx_50','rca_50']
    labelled=d[checkcols+['stenosis_50']].notna().all(axis=1)
    mismatch=(d.loc[labelled,checkcols].max(axis=1)!=d.loc[labelled,'stenosis_50']).sum()
    result={'evaluated_utc':datetime.now(timezone.utc).isoformat(),
            'role':'Separate reduced-input external CCTA transport experiment; NOT validation of the app.',
            'fit_manifest_sha256':digest(OUT/'fit_manifest.json'),
            'amended_runner_sha256':digest(Path(__file__)),
            'mapping_amendment_sha256':digest(ROOT/'docs/confirm_external_mapping_amendment.md'),
            'rows':len(d),'unique_study_ids':int(d.confirm_id.nunique()),
            'missing_per_input':X.isna().sum().astype(int).to_dict(),
            'exclusions':{'incomplete_inputs':int((~complete).sum()),'complete_but_outside_sanity_bounds':int((complete&~sane).sum()),
                          'exact_four_input_matches_to_source':int(overlap.sum()),'eligible_inputs':int(base.sum()),
                          'eligible_inputs_prior_history_or_unknown':int((base&~no_history).sum())},
            'label_diagnostic':{'complete_rows':int(labelled.sum()),'cad_vs_four_vessel_OR_mismatches':int(mismatch),
                                'action':'Labels retained as supplied; diagnostic only.'},
            'mapping_assumption':'CAD uses supplied stenosis_50 after a coding-only amendment. Formal codebook absent; semantics inferred from paper endpoint, headers and cross-column consistency. Binary 1 means named condition present, 0 absent; 50 suffix denotes nominal 50% CCTA threshold. Formal workbook codebook not supplied.',
            'cohorts':{}}
    for target,info in manifest['targets'].items():
        artifact=OUT/info['file'];assert digest(artifact)==info['sha256']
        estimator=joblib.load(artifact)
        for name,mask in [('primary',base&no_history),('secondary_all_history',base)]:
            eligible=mask&d[LABELS[target]].notna()
            xx=X.loc[eligible]; y=d.loc[eligible,LABELS[target]].to_numpy(dtype=int)
            assert len(np.unique(y))==2
            p=estimator.predict_proba(xx)[:,1]
            report={**metrics(y,p),'rows':len(y),'positive_rows':int(y.sum()),'prevalence':float(y.mean()),
                    'mean_predicted_probability':float(p.mean()),'intervals':intervals(y,p),
                    'source_prevalence_constant_brier':float(brier_score_loss(y,np.full(len(y),info['source_prevalence']))),
                    'excluded_missing_target':int((mask&d[LABELS[target]].isna()).sum())}
            result['cohorts'].setdefault(name,{})[target]=report
            pd.DataFrame({'workbook_row_index':xx.index,'observed':y,'probability':p}).to_csv(OUT/f'{name}_{target}.csv',index=False)
    app_unchanged()
    result['app_hashes_unchanged']=True
    write_json(OUT/'results.json',result)
    write_json(OUT/'evidence_manifest.json', {p.name:digest(p) for p in sorted(OUT.iterdir()) if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['evaluate']);args=parser.parse_args()
    fit() if args.stage=='fit' else evaluate()
