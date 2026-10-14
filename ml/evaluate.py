"""Metrics computed from held-out probabilities, fixed threshold 0.5."""
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, brier_score_loss, log_loss, roc_curve
from sklearn.calibration import calibration_curve


def metrics(y, p):
    pred = np.asarray(p) >= .5
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return dict(accuracy=accuracy_score(y, pred), precision=precision_score(y, pred, zero_division=0), recall=recall_score(y, pred), f1=f1_score(y, pred), roc_auc=roc_auc_score(y, p), specificity=float(tn/(tn+fp)), brier=brier_score_loss(y, p), log_loss=log_loss(y, p), confusion_matrix=[[int(tn),int(fp)],[int(fn),int(tp)]])


def curves(y, p):
    fpr,tpr,_ = roc_curve(y,p)
    observed, predicted = calibration_curve(y,p,n_bins=5,strategy='quantile')
    return dict(roc=dict(fpr=fpr.tolist(),tpr=tpr.tolist()), calibration=dict(predicted=predicted.tolist(),observed=observed.tolist()))
