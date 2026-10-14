import pandas as pd
from scripts.confirm_site_audit import OUT,OLD,PROTOCOL,read_json,digest
from ml.evaluate import metrics
from scripts.develop_confirm import confusion

def test_site_audit_integrity_partitions_and_metrics():
    frozen=read_json(OUT/'frozen.json')
    assert digest(PROTOCOL)==frozen['protocol']
    assert digest(PROTOCOL.parents[1]/'scripts/confirm_site_audit.py')==frozen['runner']
    assert digest(OLD/'evidence_manifest.json')==frozen['previous_manifest']
    for name,sha in read_json(OUT/'evidence_manifest.json').items():assert digest(OUT/name)==sha
    old=read_json(OLD/'fit_manifest.json')['experiments']
    for target,r in read_json(OUT/'results.json').items():
        d=pd.read_csv(OUT/f'{target}_oof.csv',float_precision='round_trip').set_index('row_index')
        assert d.index.is_unique
        assert set(d.index)==set(old['clinical_available_'+target]['train_rows'])
        assert abs(metrics(d.observed,d.probability)['roc_auc']-r['pooled']['roc_auc'])<1e-12
        assert abs(metrics(d.observed,d.probability)['brier']-r['pooled']['brier'])<1e-12
        assert confusion(d.observed,d.decision,.5)==r['operating_point']
        seen=[]
        for f in r['folds']:
            fit,cal,val=map(set,[f['fit_rows'],f['calibration_rows'],f['validation_rows']])
            assert not fit&cal and not (fit|cal)&val
            assert fit|cal|val==set(d.index)
            assert d.loc[list(val),'site_code'].eq(f['site_code']).all()
            assert d.loc[list(fit|cal),'site_code'].ne(f['site_code']).all()
            scored=d.loc[list(val)]
            assert ((scored.probability>=f['cutoff']).astype(int)==scored.decision).all()
            seen+=f['validation_rows']
        assert len(seen)==len(set(seen))==len(d)
