"""Batch-check SHAP reconstruction for every original input and export receipts."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from ml.schema import *
from ml.predict import Predictor

def main():
    predictor=Predictor();X=read_data()[FEATURES];receipt={}
    for target,artifact in predictor.artifacts.items():
        pre=artifact['pipeline'].named_steps['preprocess'];model=artifact['pipeline'].named_steps['model']
        transformed=pre.transform(X);explainer,unit=predictor.explainers[target]
        ex=explainer(transformed)
        value=ex.base_values+ex.values.sum(axis=1)
        if value.ndim==2:value=value[:,1]
        actual=model.predict_proba(transformed)[:,1]
        reconstructed=value if unit=='probability' else 1/(1+np.exp(-value))
        error=float(np.max(np.abs(actual-reconstructed)))
        assert error<1e-4,(target,error)
        receipt[target]=dict(rows=len(X),max_reconstruction_error=error,unit=unit)
    write_json(ROOT/'output/verification/all_rows_shap.json',receipt)
    print(receipt)

if __name__=='__main__':main()
