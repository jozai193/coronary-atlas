"""Publish every fixed multi-cohort arm from verified saved receipts."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.verify_multicohort import verify

verify()
folder=ROOT/'output/research/multicohort_v1'
r=json.loads((folder/'results.json').read_text(encoding='utf-8'))
prep=json.loads((folder/'prepared.json').read_text(encoding='utf-8'))
lines=['# Multi-cohort training results - 13 October 2026','',
       '**Executed research development; no live model replacement or demonstrated overall accuracy gain.**',
       '', '## What was trained', '',
       'A fixed logistic model was trained on additional public-cohort records, comparing single-cohort training, pooled patients, equal study weighting and equal study-specific probability averaging. CAD uses 11 shared clinical fields across UCI (303), AngioCAD (345) and Anhui (553): **1,201 eligible CAD records**. Each vessel uses 13 fields across UCI plus target-eligible AngioCAD (LAD 322, LCX 331, RCA 326). These target-specific counts overlap; they are not separate patients. The existing 55-input model and historical metrics remain unchanged.',
       '', 'All 54 specified cohort/within-cohort roles completed. Whole-cohort transport excludes the destination completely; five-fold augmentation excludes current held-out rows and exact matching input fingerprints from every training source. One duplicate-input row in some AngioCAD tasks was grouped with its match. No cross-cohort input-fingerprint matches were found; this is not global identity verification.',
       '', 'These cohorts and earlier outcomes were already inspected. This new training design is development on reused patients, not fresh validation. Clinical selection, timing, units and endpoint thresholds differ. CAD has three cohorts; vessels have only two. Raw data and fitted research models stay local. No ECG/echo values were fabricated to fill a larger feature contract.',
       '', '## Main findings', '',
       '- Adding cohorts did not reliably improve predictions. Study-balanced CAD Brier worsened in every cohort: UCI .1664 to .1757, AngioCAD .1182 to .1558, Anhui .1903 to .2423. AUC also fell in all three. Some accuracy/recall changes reflect a shifted decision balance rather than better probabilities.',
       '- LCX showed a small research signal: study-balanced AUC .7154 to .7250 and Brier .2083 to .2074 in UCI; AUC .7022 to .7125 and Brier .1815 to .1799 in AngioCAD. Both conditional Brier-difference intervals include zero. UCI sensitivity at .5 fell from 39.5% to 32.8% (72 versus 80 missed positives); AngioCAD sensitivity rose from 6.7% to 23.3% (84 versus 69 missed). This trade-off does not establish a better operating choice or justify promotion.',
       '- LAD/RCA did not show improved Brier and AUC in every cohort. Averaging study models was not a reliable cure for population shift. Whole-cohort CAD probability transport remained poor, particularly when learning outside Anhui.',
       '- The fixed engineering signal flag is true only for LCX; it is neither statistical significance nor a deployment gate. These reduced-input figures cannot replace the original 55-input model metrics.',
       '', '## Paired augmentation differences', '',
       'Study-balanced minus local-only; lower Brier and higher AUC are favorable. Conditional bootstrap intervals resample fixed patient errors, omitting refitting, study and post-search uncertainty.', '',
       '| Target | Cohort | Brier difference | Conditional 95% interval | AUC difference |',
       '|---|---|---:|---|---:|']
for d in r['augmentation_deltas']:
    if d['arm']=='study_balanced':
        lo,hi=d['conditional_brier_delta_95']
        lines.append(f'| {d["target"].upper()} | {d["cohort"]} | {d["brier_delta"]:+.6f} | {lo:+.6f} to {hi:+.6f} | {d["auc_delta"]:+.6f} |')
lines += ['', '## All fixed results', '',
          'No arm or unfavorable cohort is omitted. Fixed decision cutoff .5. Training-prevalence predictions are constants within each fold; their aggregate out-of-fold AUC can differ from .5 because fold prevalences differ. For vessel transport only one study remains for training, so pooled, balanced, ensemble and single-study predictions coincide.', '',
          '| Target | Destination | Design | Arm | N | AUC | Brier | Accuracy | Sensitivity | Specificity | FN | FP |',
          '|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for t,cohorts in r['scores'].items():
    for c,designs in cohorts.items():
        for design,arms in designs.items():
            for a,m in arms.items():
                lines.append(f'| {t.upper()} | {c} | {design} | {a} | {m["n"]} | {m["auc"]:.4f} | {m["brier"]:.4f} | {m["accuracy"]:.4f} | {m["sensitivity"]:.4f} | {m["specificity"]:.4f} | {m["confusion"]["fn"]} | {m["confusion"]["fp"]} |')
lines += ['', '## Reproduce and verify', '',
          'Run from the project root with the original locally acquired workbooks: `python -m ml.multicohort prepare`, `python -m ml.multicohort run`, `python -m ml.multicohort verify`, `python scripts/verify_multicohort.py`. Preparation/fitting refuse overwrite; preserve the frozen run. `python scripts/report_multicohort.py` regenerates this report without fitting.', '',
          'The runner checks raw/code/protocol/historical hashes, training roles, fitted prediction replay and saved metrics. A separate verifier recomputes 93 metric groups and checks exact one-time evaluation across 54 roles without reusing the runner metric function. Three focused multi-study tests and five existing cohort-mapping tests passed. All 53 protected historical files were unchanged.', '',
          'Evidence: [protocol](multicohort_protocol.md), [all metrics](../output/research/multicohort_v1/results.json), [indexed predictions](../output/research/multicohort_v1/predictions.csv), [partitions](../output/research/multicohort_v1/partitions.json), [fit receipt](../output/research/multicohort_v1/fit_receipt.json). Research fit artifact is local-only at `output/research/multicohort_v1/private/fitted.joblib`; it includes explicitly labeled all-data fits and must never be evaluated on its training patients as if unseen.', '',
          '## Decision', '',
          'Keep the current app unchanged. LCX multi-study training is a small follow-up lead, with uncertain probability benefit and worse source-cohort detection at .5. A new compatible cohort and an explicit reviewed missed-case/false-alarm objective are needed before selecting a revised predictor or operating point. More rows and higher recall alone are insufficient.', '',
          'Methods informed by [Patil and Parmigiani, PNAS](https://doi.org/10.1073/pnas.1708283115), [Guan et al., merging versus ensembling](https://arxiv.org/abs/1905.07382), [BMJ model evaluation](https://doi.org/10.1136/bmj-2023-074819), and [TRIPOD-Cluster](https://doi.org/10.1136/bmj-2022-071058). Dataset provenance and mapping caveats are in the linked protocol and original cohort protocols.']
(ROOT/'docs/multicohort_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
print('Published all fixed results and negative findings.')
