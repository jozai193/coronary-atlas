"""Regenerate the complete follow-up report from independently checked receipts."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.verify_cohort_calibration import verify

verify()
out=ROOT/'ml/experiments/cohort_calibration_v1'
r=json.loads((out/'results.json').read_text(encoding='utf-8'))
def mean(t,c,a,p,key):return float(np.mean([r['scores'][t][c][rep][a][p][key] for rep in ['1','2']]))
lines=['# Cohort-aware training and calibration - 13 October 2026','',
 '**Executed follow-up development. No live model replacement or new clinical accuracy claim.**','',
 '## What changed in the experiment','',
 'The previous pooled study mixed cohorts with different outcome frequencies. This follow-up fits common clinical-feature slopes with separate cohort intercepts, then evaluates separately fitted local sigmoid calibration. It compares against local-only learning, ordinary pooling and base models trained with the entire destination omitted. CAD uses 11 shared inputs; vessel tasks use 13. The original 55-input app remains unchanged.',
 '', 'All 90 target/cohort/repeat/fold roles completed. Each destination separates about 60% ranker training, 20% calibration and 20% evaluation, with duplicate-input groups kept together. Additional-cohort training excludes any match to destination calibration/evaluation inputs. Two repeats reuse the same people. The imported cohort labels/mappings and all earlier endpoint/timing/unit limitations remain unchanged. Checking the new ICD workbook found no hidden dictionary, cell comments, named ranges or validation lists that establish its unresolved codes; neither ICD nor CM-CAD entered training.',
 '', '## What the results support','',
 '- **LCX remains a promising research lead:** the cohort-aware calibrated arm improved mean out-of-fold AUC and Brier over the equally calibrated local-only arm in both cohorts. Both conditional Brier-difference intervals include zero; this is not a confirmed accuracy gain.',
 '- **CAD did not benefit from sharing feature slopes:** the cohort-aware calibrated arm had worse Brier and AUC than locally calibrated learning in all three cohorts. Separate cohort intercepts improved over ordinary pooling but did not solve predictor/endpoint/population differences.',
 '- **Local calibration corrected much of the transferred probability mismatch.** For Anhui CAD, other-cohort-only pooled Brier .3435 became .1955 after local calibration, while local-only calibrated learning gave .1902. This improvement cannot be credited to adding patients. The calibrated transfer arm uses destination labels and is adaptation, not untouched external validation.',
 '- LAD/RCA results were mixed. No target-specific model was promoted. These figures evaluate reduced-input development procedures, not the served 55-input model or its previously reported accuracies.',
 '', '## LCX primary comparison','',
 'Means across two repeat-level metrics; fixed .5 cutoff. AUC summarizes out-of-fold scores from multiple fitted models; complete within-fold AUC values and both repeats are retained below.',
 '', '| Cohort | Arm | AUC | Brier (lower better) | Accuracy | Sensitivity | Specificity |',
 '|---|---|---:|---:|---:|---:|---:|']
for c in ['uci','angiocad']:
 for a in ['local_sigmoid','cohort_intercepts_sigmoid']:
  values=[mean('lcx',c,a,'fixed_50',key) for key in ['auc','brier','accuracy','sensitivity','specificity']]
  lines.append('| '+c+' | '+a+' | '+' | '.join(f'{v:.4f}' for v in values)+' |')
lines+=['','At .5, UCI LCX missed 71/66 positives with local calibration versus 67/66 with cohort-aware calibration, across repeats 1/2. False alarms were 28/27 versus 29/31. AngioCAD missed 82/80 versus 76/75, with false alarms 8/8 versus 14/14. More detections came with more false alarms; performance is still insufficient for a rule-out claim.',
 '', '## Additional-data probability comparison','',
 'Cohort-aware calibrated minus local-only calibrated. Bootstrap intervals average each patient\'s two repeat errors first and resample patients. They omit refitting, site, endpoint and post-search uncertainty.',
 '', '| Target | Cohort | Brier difference | Conditional 95% interval | AUC change repeat 1 / 2 |',
 '|---|---|---:|---|---|']
for d in r['comparisons']:
 if d['arm']=='cohort_intercepts_sigmoid' and d['reference']=='local_sigmoid':
  lo,hi=d['conditional_brier_delta_95'];a,b=d['auc_deltas_by_repeat']
  lines.append(f'| {d["target"].upper()} | {d["cohort"]} | {d["brier_delta"]:+.6f} | {lo:+.6f} to {hi:+.6f} | {a:+.6f} / {b:+.6f} |')
lines+=['','## Exploratory sensitivity illustration','',
 'A 90% empirical calibration sensitivity target is not a guarantee for evaluation patients, an approved clinical objective or a recommended cutoff. Thresholds were selected only on calibration positives after calibration fitting; evaluation remained separate. For UCI LCX, mean evaluation sensitivity was 83.2% local-calibrated versus 86.1% cohort-aware-calibrated, with specificity 40.5% versus 38.0%. For AngioCAD it was 88.9% versus 88.3%, with specificity 34.0% versus 31.3%. The latter comparison shows no operational advantage. All selected cutoffs/errors follow below.',
 '', '## All fixed results - both repeats','',
 'No unfavorable cohort, arm or operating point is omitted. The training-prevalence arm is constant within each fold; its aggregate out-of-fold AUC can differ from .5. Calibration slopes ranged .1713 to 2.4008, all positive: within a fold sigmoid retains ranking, while pooled AUC can change as score scales differ between folds. The cohort-intercept model requires a known training-cohort context and rejects unknown cohorts; it is not a general unknown-hospital model.',
 '', '| Target | Cohort | Repeat | Arm | Point | N | AUC | Mean fold AUC | Brier | Accuracy | Sensitivity | Specificity | FN | FP | Cutoff range |',
 '|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
for t,cohorts in r['scores'].items():
 for c,reps in cohorts.items():
  for rep,arms in reps.items():
   for a,points in arms.items():
    for point,m in points.items():
     lines.append(f'| {t.upper()} | {c} | {rep} | {a} | {point} | {m["n"]} | {m["auc"]:.4f} | {m["mean_within_fold_auc"]:.4f} | {m["brier"]:.4f} | {m["accuracy"]:.4f} | {m["sensitivity"]:.4f} | {m["specificity"]:.4f} | {m["confusion"]["fn"]} | {m["confusion"]["fp"]} | {m["cutoff_min"]:.5f}-{m["cutoff_max"]:.5f} |')
lines+=['','## Reproduction and checks','',
 'Canonical entry: `python scripts/run_cohort_calibration.py prepare`, then `fit`, `evaluate`, `verify`. Preparation/fitting/evaluation refuse overwrites; preserve the existing frozen trial. The wrapper imports the model module canonically so saved class names remain loadable. `python scripts/verify_cohort_calibration.py` independently checks saved evidence; `python scripts/report_cohort_calibration.py` regenerates this report without fitting. Raw cohort workbooks and private fitted objects must be available locally for full replay.',
 '', 'The runner verified all raw/code/protocol/history hashes, exact row roles, calibration/evaluation prediction replay, frozen cutoffs and metric regeneration. A separate script reproduced **306 metric groups** and independently checked all 90 disjoint three-role definitions, raw outcome/row coverage, duplicate exclusions and calibration-only cutoff selection. Metamorphic tests changed held-out features/labels and confirmed identical fits/calibrators/cutoffs. Cohort-intercept tests checked distinct baselines and unknown-cohort rejection. All 62 protected historical files remain unchanged.',
 '', 'Evidence: [frozen protocol](cohort_calibration_protocol.md), [all metrics](../ml/experiments/cohort_calibration_v1/results.json), [indexed evaluation predictions](../ml/experiments/cohort_calibration_v1/evaluation_predictions.csv), [partitions](../ml/experiments/cohort_calibration_v1/partitions.json), [calibration metadata](../ml/experiments/cohort_calibration_v1/fit_metadata.json). Fitted research objects remain local/ignored in `ml/experiments/cohort_calibration_v1/private/`.',
 '', '## Decision','',
 'Preserve LCX as a follow-up candidate; no production promotion. Benefit is small, uncertain and limited to reduced-input models on reused cohorts with a known cohort context and local labeled calibration records. New compatible data, clinical field/timing confirmation, exact explanation fidelity and an intended-use/error-cost objective remain necessary before any live replacement. Calibration is not a substitute for matching the clinical task.',
 '', 'Methods context: [Falconieri et al., multicenter model simulation](https://doi.org/10.1002/bimj.201900075) and [BMJ recalibration guidance](https://doi.org/10.1136/bmj.i3140). The simulation studies random intercepts; our fixed-intercept experiment is distinct. These sources motivate a comparison, not a claim that it must work.']
(ROOT/'docs/cohort_calibration_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
print('Published every arm, repeat, operating point and negative result.')
