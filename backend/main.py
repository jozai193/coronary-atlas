"""Local educational API. Input is ephemeral and never written to disk."""
from contextlib import asynccontextmanager
import json
import math
from typing import Any, Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, ConfigDict, Field
from ml.schema import ROOT, FEATURES, GROUPS, NUMERIC, PROHIBITED
from ml.predict import Predictor
from ml.coherence import project_probabilities
from backend.candidates import load_candidate
from backend.ensemble import load_ensemble
from backend.heldout import router as heldout_router

DISCLAIMER='This software is an educational/research decision-support prototype and is not a substitute for professional medical diagnosis, coronary angiography or other diagnostic imaging.'


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.predictor=Predictor()
    app.state.metrics=json.loads((ROOT/'ml/metrics/evaluation.json').read_text(encoding='utf-8'))
    app.state.coherence_evidence=json.loads((ROOT/'ml/experiments/coherence_v1/results.json').read_text(encoding='utf-8'))
    app.state.candidate,app.state.candidate_info=load_candidate(app.state.predictor)
    app.state.ensemble,ensemble_info=load_ensemble()
    app.state.candidate_info={**app.state.candidate_info,'ensemble':ensemble_info}
    yield


app=FastAPI(title='Coronary Atlas',version='1.0.0',lifespan=lifespan)
app.add_middleware(GZipMiddleware,minimum_size=1000)
app.include_router(heldout_router)


class PatientRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    features: dict[str, Any] = Field(description='Canonical field names from /model/info. Null means unknown.')
    model_variant: Literal['baseline','histgb_lcx_v2','calibrated_ensemble_v1'] = 'baseline'


class Factor(BaseModel):
    feature: str
    contribution: float


class Explanation(BaseModel):
    method: str
    unit: str
    base_value: float
    output_value: float
    additivity_error: float
    factors: list[Factor]
    note: str


class Prediction(BaseModel):
    probability: float = Field(ge=0,le=1)
    model_probability: float = Field(ge=0,le=1,description='Model output before coherence adjustment, reconstructed by the named attribution method.')
    classification: int = Field(ge=0,le=1)
    category: str
    model: str
    explanation: Explanation


class CoherenceAdjustment(BaseModel):
    enabled: bool
    method: Literal['euclidean_projection','none']
    changed_targets: list[Literal['cad','lad','lcx','rca']]
    max_absolute_change: float = Field(ge=0,le=1)
    note: str


class CoherenceEvidenceRepeat(BaseModel):
    repeat: int
    raw_mean_four_target_brier: float
    adjusted_mean_four_target_brier: float
    adjusted_rows: int
    discordant_rows_raw: int
    discordant_rows_adjusted: int


class CoherenceEvidence(BaseModel):
    scope: str
    rows: int
    method: Literal['euclidean_projection']
    repeats: list[CoherenceEvidenceRepeat]
    screen_passed: bool
    mean_four_target_brier_delta: float
    note: str


class PredictionResponse(BaseModel):
    cad: Prediction
    lad: Prediction
    lcx: Prediction
    rca: Prediction
    warnings: list[str]
    missing_features: list[str]
    input_snapshot: dict[str, Any]
    disclaimer: str
    model_version: str
    coherence_adjustment: CoherenceAdjustment


@app.middleware('http')
async def headers(request: Request, call_next):
    # The local API never persists requests; browser caches must not retain predictions.
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    if '/predict' in request.url.path or '/held-out/' in request.url.path:
        response.headers['Cache-Control']='no-store'
    return response


@app.get('/health')
@app.get('/api/health')
def health():
    return dict(status='ok',models=list(app.state.predictor.artifacts),version='1.0.0')


@app.get('/model/info')
@app.get('/api/model/info')
def model_info():
    m=app.state.predictor.metadata
    return dict(version='1.0.0',features=m['feature_schema'],rows=m['rows'],seed=m['seed'],models={k:v['selected']['kind'] for k,v in m['artifacts'].items()},disclaimer=DISCLAIMER,dataset='UCI Extension of Z-Alizadeh Sani (303 records)',source='https://doi.org/10.24432/C5461K',feature_count=len(FEATURES),threshold=.5,bands={'lower':[0,.3],'intermediate':[.3,.7],'higher':[.7,1]},limitations=['The served 55-input models have internal cross-validation only. Separate reduced-input transport studies do not externally validate this app.', 'Color bands are interface conventions, not clinical thresholds.', 'Probabilities concern supplied cross-sectional labels, not future heart attacks.', 'Baseline display probabilities use a disclosed CAD/vessel consistency adjustment; SHAP explains each unadjusted model output. The optional LCX candidate remains unadjusted.', 'Reference anatomy shows vessel-level risk, not lesion location.', 'Units are conventional interpretations; original feature documentation is incomplete.'])


@app.get('/model/metrics')
@app.get('/api/model/metrics')
def model_metrics():
    return app.state.metrics


@app.get('/model/coherence',response_model=CoherenceEvidence)
@app.get('/api/model/coherence',response_model=CoherenceEvidence)
def model_coherence():
    evidence=app.state.coherence_evidence
    return dict(scope=evidence['scope'],rows=app.state.predictor.metadata['rows'],method='euclidean_projection',
        repeats=[dict(repeat=item['repeat'],
            raw_mean_four_target_brier=item['summary']['mean_four_target_brier_raw'],
            adjusted_mean_four_target_brier=item['summary']['mean_four_target_brier_projected'],
            adjusted_rows=item['summary']['changed_rows'],
            discordant_rows_raw=item['summary']['discordant_rows_raw'],
            discordant_rows_adjusted=item['summary']['discordant_rows_projected'])
            for item in evidence['repeats']],
        screen_passed=evidence['screen']['passed'],
        mean_four_target_brier_delta=evidence['screen']['mean_four_target_brier_delta'],
        note='Paired shared-fold internal comparison on the same 303 people; pilot informed this check. The original per-target validation tables use different folds and describe unadjusted models. No independent validation or clinical-use threshold follows from this result.')


@app.get('/sample-patients')
@app.get('/api/sample-patients')
def samples():
    return json.loads((ROOT/'data/processed/sample_patients.json').read_text(encoding='utf-8'))


@app.get('/review-profiles')
@app.get('/api/review-profiles')
def review_profiles():
    return json.loads((ROOT/'data/processed/reviewer_samples_v2.json').read_text(encoding='utf-8'))


@app.get('/model/candidates')
@app.get('/api/model/candidates')
def candidate_info():
    return app.state.candidate_info


def validate_features(features, schema):
    unknown=set(features)-set(FEATURES)
    if unknown:
        raise HTTPException(422,detail=f'Unknown or prohibited input fields: {", ".join(sorted(unknown))}. Labels are never inputs.')
    clean={}; warnings=[]
    for spec in schema:
        name=spec['name']; value=features.get(name)
        if value is None:
            clean[name]=None
            continue
        if name in NUMERIC:
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or value>1000000:
                raise HTTPException(422,detail=f'{name}: enter a finite nonnegative number or null.')
            clean[name]=float(value)
            # A rounded supplied BMI can sit just outside the exact observed
            # bounds; reconcile it with weight/height before its range check.
            bmi_with_components = name == 'BMI' and features.get('Weight') is not None and features.get('Length') is not None
            if (value<spec['minimum'] or value>spec['maximum']) and not bmi_with_components:
                raise HTTPException(422,detail=f'{name}: outside the observed training range ({spec["minimum"]:g}–{spec["maximum"]:g}). This prototype cannot provide a supported estimate for that input.')
        else:
            # Numeric source codes may be sent as JSON numbers, but booleans are ambiguous.
            if isinstance(value,bool) or not isinstance(value,(str,int,float)):
                raise HTTPException(422,detail=f'{name}: invalid category.')
            normalized=str(int(value)) if isinstance(value,(int,float)) and math.isfinite(value) and value==int(value) else str(value)
            if normalized not in spec['options']:
                raise HTTPException(422,detail=f'{name}: expected one of {spec["options"]}, or null.')
            clean[name]=normalized
    # BMI is an exact derived field in every source row. Never send a
    # contradictory weight/height/BMI triple to models trained on that relation.
    weight, height = clean['Weight'], clean['Length']
    if weight is not None and height is not None:
        calculated_bmi = weight / (height / 100) ** 2
        bmi_spec = next(spec for spec in schema if spec['name'] == 'BMI')
        if calculated_bmi < bmi_spec['minimum'] or calculated_bmi > bmi_spec['maximum']:
            raise HTTPException(422,detail=f'BMI calculated from Weight and Height is outside the observed training range ({bmi_spec["minimum"]:g}–{bmi_spec["maximum"]:g}).')
        supplied_bmi = clean['BMI']
        if supplied_bmi is not None and abs(supplied_bmi - calculated_bmi) > 0.2:
            raise HTTPException(422,detail='BMI does not match Weight (kg) and Height (cm). Check the three entries before predicting.')
        clean['BMI'] = calculated_bmi
        if supplied_bmi is None:
            warnings.append('BMI was calculated from the supplied weight and height; it was not measured separately.')
        elif not math.isclose(supplied_bmi, calculated_bmi, abs_tol=1e-6):
            warnings.append('BMI was recalculated from the supplied weight and height for a consistent model input.')
    missing=[k for k,v in clean.items() if v is None]
    required_missing=[name for name in ['Age','EF-TTE','VHD',*GROUPS['ECG']] if clean[name] is None]
    if required_missing or len(missing)>len(FEATURES)//2:
        labels={'Age':'age','EF-TTE':'echo EF','VHD':'valve assessment'}
        reasons=[]
        if required_missing:reasons.append('Supply '+', '.join(labels.get(name,next(spec['label'] for spec in schema if spec['name']==name)) for name in required_missing)+'.')
        if len(missing)>len(FEATURES)//2:reasons.append(f'Only {len(FEATURES)-len(missing)}/55 observations available; at least 28 are required.')
        raise HTTPException(422,detail='Insufficient information — cannot generate a prediction. '+' '.join(reasons)+' This review-completeness rule is not clinical validation.')
    if missing:
        warnings.append(f'{len(missing)} unknown inputs were imputed from training data. Explanations include imputed values, not measured findings.')
    if all(clean[name] is None for name in GROUPS['Laboratory']):
        warnings.append('All laboratory observations are missing. In a post-hoc internal test on complete records, masking this group changed LCX/RCA raw estimates. Performance on naturally incomplete records has not been validated.')
    if all(clean[name] is None for name in GROUPS['Echocardiography']):
        warnings.append('All echocardiography observations are missing. In a post-hoc internal test on complete records, masking this group changed LAD raw estimates. Performance on naturally incomplete records has not been validated.')
    if clean['Age'] is not None and clean['Age']<30:
        warnings.append('No patients below age 30 occurred in the training cohort.')
    return clean,missing,warnings


@app.post('/predict',response_model=PredictionResponse)
@app.post('/api/predict',response_model=PredictionResponse)
def predict(patient: PatientRequest):
    clean,missing,warnings=validate_features(patient.features,app.state.predictor.metadata['feature_schema'])
    predictor=app.state.predictor
    if patient.model_variant=='histgb_lcx_v2':
        if app.state.candidate is None:
            raise HTTPException(503,detail='The optional experimental LCX model is not installed.')
        predictor=app.state.candidate
        warnings.append('Experimental LCX model selected after a multi-family search on reused data. Only LCX uses this candidate. No independent validation; probability is not a measured blockage percentage.')
    elif patient.model_variant=='calibrated_ensemble_v1':
        if app.state.ensemble is None:
            raise HTTPException(503,detail='The optional calibrated ensemble is not installed.')
        predictor=app.state.ensemble
        warnings.append('Experimental calibrated ensemble: all four models change. Repeated internal development on 303 people is not independent clinical validation. Sampled permutation attributions explain calibrated probabilities before coherence adjustment; their allocation is approximate.')
        if missing:
            warnings.append('Ensemble missing-input behavior was checked by artificial masks of complete records. In the core-only scenario its probability-error advantage was uncertain; naturally incomplete patient performance is unvalidated.')
    result=predictor.predict(clean)
    targets=('cad','lad','lcx','rca')
    for target in targets:
        result[target]['model_probability']=result[target]['probability']
    if patient.model_variant in ('baseline','calibrated_ensemble_v1'):
        projected=project_probabilities([result[target]['model_probability'] for target in targets])
        changed=[]
        for target,probability in zip(targets,projected):
            probability=float(probability)
            raw=result[target]['model_probability']
            if abs(probability-raw)>1e-12:
                changed.append(target)
            result[target]['probability']=probability
            result[target]['classification']=int(probability>=.5)
            result[target]['category']='Lower' if probability<.3 else ('Intermediate' if probability<.7 else 'Higher')
        adjustment=dict(enabled=True,method='euclidean_projection',changed_targets=changed,
            max_absolute_change=max(abs(result[target]['probability']-result[target]['model_probability']) for target in targets),
            note='Displayed baseline probabilities are jointly adjusted so CAD is at least as high as each vessel estimate. SHAP explains the separately reported unadjusted model probabilities.' if patient.model_variant=='baseline' else 'Displayed ensemble probabilities are jointly adjusted so CAD is at least as high as each vessel estimate. Sampled permutation attributions explain the separately reported calibrated probabilities before this adjustment.')
        if changed:
            warnings.append('Displayed probabilities were adjusted for CAD/vessel consistency. SHAP factors explain the unadjusted model probabilities shown separately.' if patient.model_variant=='baseline' else 'Displayed probabilities were adjusted for CAD/vessel consistency. Sampled attributions explain calibrated model probabilities before adjustment, shown separately.')
    else:
        adjustment=dict(enabled=False,method='none',changed_targets=[],max_absolute_change=0.0,
            note='The opt-in LCX candidate was not included in the coherence evaluation. Its displayed probabilities are unadjusted model outputs.')
        if result['cad']['probability'] < max(result[v]['probability'] for v in ('lad','lcx','rca')):
            warnings.append('Independent model estimates are discordant: a vessel estimate exceeds CAD. These are not a coherent joint probability model.')
    version={'baseline':'1.0.0+coherence-v1','histgb_lcx_v2':'1.0.0+histgb-lcx-v2','calibrated_ensemble_v1':'1.0.0+calibrated-ensemble-v1'}[patient.model_variant]
    return dict(**result,warnings=warnings,missing_features=missing,input_snapshot=clean,disclaimer=DISCLAIMER,model_version=version,coherence_adjustment=adjustment)


# Register SPA last so API routes cannot be shadowed.
dist=ROOT/'frontend/dist'
if dist.is_dir():
    app.mount('/',StaticFiles(directory=dist,html=True),name='dashboard')
