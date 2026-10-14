"""Integrity-checked model loading and deterministic inference."""
import json
import numpy as np
import pandas as pd
import joblib
from ml.schema import ROOT, FEATURES, CATEGORICAL, TARGETS, digest
from ml.explain import make_explainer, explain


class Predictor:
    def __init__(self, model_dir=None):
        directory = model_dir or ROOT/'models'
        self.metadata=json.loads((directory/'metadata.json').read_text(encoding='utf-8'))
        if self.metadata['features']!=FEATURES:
            raise ValueError('Model input contract mismatch.')
        self.artifacts={}
        self.explainers={}
        for target, info in self.metadata['artifacts'].items():
            path=directory/info['file']
            if digest(path)!=info['sha256']:
                raise ValueError(f'Model integrity check failed: {target}')
            artifact=joblib.load(path)  # Load only bundled trusted artifacts, never user uploads.
            if artifact['features'] != FEATURES or artifact['target'] != target:
                raise ValueError('Artifact contract mismatch.')
            self.artifacts[target]=artifact
            self.explainers[target]=make_explainer(artifact)

    def predict(self,features):
        frame=pd.DataFrame([{name: features.get(name, np.nan) if features.get(name) is not None else np.nan for name in FEATURES}],columns=FEATURES)
        # Explicit object columns keep missing categories as np.nan for sklearn imputation.
        for name in CATEGORICAL:
            frame[name]=frame[name].astype(object)
        result={}
        for target,artifact in self.artifacts.items():
            p=float(artifact['pipeline'].predict_proba(frame)[0,1])
            explanation=explain(artifact,*self.explainers[target],frame)
            result[target]=dict(probability=p,classification=int(p>=.5),category='Lower' if p<.3 else ('Intermediate' if p<.7 else 'Higher'),model=artifact['kind'],explanation=explanation)
        return result
