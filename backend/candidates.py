"""Explicit opt-in experimental models; never replace the baseline registry."""
import json
import copy
import joblib
from ml.schema import ROOT,FEATURES,digest
from ml.explain import make_explainer

DIRECTORY=ROOT/'models/candidates/histgb_lcx'
CANDIDATE_ID='histgb_lcx_v2'


def load_candidate(baseline,directory=DIRECTORY):
    manifest_path=directory/'manifest.json'
    if not manifest_path.exists():
        return None,dict(available=False,candidate_id=CANDIDATE_ID)
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('candidate_id')!=CANDIDATE_ID or manifest.get('inference_verified') is not True or manifest.get('feature_names')!=FEATURES:
        raise ValueError('Experimental manifest contract mismatch.')
    for evidence in manifest['nested_heldout_evidence']['files']:
        evidence_path=(ROOT/evidence['path']).resolve()
        if not evidence_path.is_relative_to(ROOT.resolve()) or digest(evidence_path)!=evidence['sha256']:
            raise ValueError('Experimental evidence integrity check failed.')
    artifact_info=manifest['artifact']
    if artifact_info['file']!='histgb_lcx.joblib':
        raise ValueError('Unexpected experimental artifact filename.')
    path=directory/artifact_info['file']
    if digest(path)!=artifact_info['sha256']:
        raise ValueError('Experimental artifact integrity check failed.')
    artifact=joblib.load(path)  # Only the packaged, hash-checked local artifact.
    if artifact['features']!=FEATURES or artifact['target']!='lcx' or artifact['kind']!='hist_gradient_boosting':
        raise ValueError('Experimental artifact contract mismatch.')
    predictor=copy.copy(baseline)
    predictor.artifacts={**baseline.artifacts,'lcx':artifact}
    predictor.explainers={**baseline.explainers,'lcx':make_explainer(artifact)}
    source=ROOT/'ml/experiments/broad_v2/lcx.json'
    # Published evidence is the saved fixed-candidate outer evaluation, not a
    # re-evaluation of the fitted-on-all-rows artifact loaded above.
    runs=[]
    for repeat in [1,2]:
        import pandas as pd
        from ml.evaluate import metrics
        table=pd.read_csv(ROOT/f'ml/experiments/broad_v2/lcx_repeat_{repeat}.csv',float_precision='round_trip')
        runs.append(dict(repeat=repeat,baseline=metrics(table.y,table.baseline_selector),
                         candidate=metrics(table.y,table.hist_gradient_boosting)))
    return predictor,dict(available=True,candidate_id=CANDIDATE_ID,target='lcx',
        name='Experimental LCX · histogram gradient boosting',
        note='Opt-in research comparison selected after exploring multiple families on the same 303 records. Only the fitted LCX model changes; this variant skips coherence projection, so displayed CAD/LAD/RCA values may differ from the adjusted baseline. These internal results are exploratory, not independent validation.',
        rows=303,runs=runs,artifact_sha256=artifact_info['sha256'],source_sha256=digest(source))
