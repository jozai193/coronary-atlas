"""Publication-readable plots from executed OOF artifacts."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ml.schema import ROOT

evaluation=json.loads((ROOT/'ml/metrics/evaluation.json').read_text())
out=ROOT/'docs/figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#355452','text.color':'#243d3b','figure.facecolor':'white'})
colors=['#187e76','#c28b32','#aa6754','#5176a1']
fig,axes=plt.subplots(1,2,figsize=(10,4.1),layout='constrained')
for (target,e),color in zip(evaluation['targets'].items(),colors):
    c=e['curves'];axes[0].plot(c['roc']['fpr'],c['roc']['tpr'],label=f'{target.upper()} (AUC {e["metrics"]["roc_auc"]:.3f})',color=color)
    axes[1].plot(c['calibration']['predicted'],c['calibration']['observed'],'o-',color=color,label=target.upper())
for ax in axes:
    ax.plot([0,1],[0,1],':',color='#9caaa5');ax.set(xlim=(0,1),ylim=(0,1));ax.grid(alpha=.15);ax.legend(loc='lower right',fontsize=8)
axes[0].set(title='Held-out discrimination',xlabel='False-positive rate',ylabel='True-positive rate')
axes[1].set(title='Reliability: five quantile bins',xlabel='Mean predicted probability',ylabel='Observed positive fraction')
fig.savefig(out/'validation.png',dpi=180);plt.close(fig)
fig,axes=plt.subplots(1,4,figsize=(10,2.5),layout='constrained')
for ax,(target,e) in zip(axes,evaluation['targets'].items()):
    cm=e['metrics']['confusion_matrix'];ax.imshow(cm,cmap='Blues',vmin=0,vmax=200)
    for i in range(2):
        for j in range(2):ax.text(j,i,str(cm[i][j]),ha='center',va='center',color='white' if cm[i][j]>110 else '#183e44',fontsize=13)
    ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['Neg','Pos'],yticklabels=['Neg','Pos'],title=target.upper(),xlabel='Predicted')
axes[0].set_ylabel('Supplied label');fig.savefig(out/'confusion-matrices.png',dpi=180);plt.close(fig)
print('Saved ROC, calibration and confusion matrix plots.')
