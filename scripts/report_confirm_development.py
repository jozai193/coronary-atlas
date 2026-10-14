"""Render results from frozen evidence; does not train, tune or change model artifacts."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'ml/experiments/confirm_development_v1'


def main():
    result = json.loads((OUT/'results.json').read_text(encoding='utf-8'))
    fit = json.loads((OUT/'fit_manifest.json').read_text(encoding='utf-8'))
    prepared = json.loads((OUT/'prepared.json').read_text(encoding='utf-8'))
    report = ROOT/'docs/confirm_development_results.md'
    lines = ['# CONFIRM development improvements', '',
        'Completed 8 October 2026. **Separate research models only; the app and the original external experiment are unchanged.**', '',
        'This experiment follows the negative external transport result. CONFIRM is now development data. '
        'These are internal test results from a previously inspected registry, not fresh independent validation or evidence of clinical readiness.', '',
        '## What changed', '',
        '- Recalibrated the frozen four-input source model using a dedicated CONFIRM calibration partition.',
        '- Trained new models on more records and compared logistic, additive spline, histogram boosting and random forest pipelines using training-only cross-validation.',
        '- Tested 11 additional nominal clinical fields on exactly the same complete-case patients, then tested missing-input handling in a separately reported wider cohort.',
        '- Froze diagnostic cutoffs targeting 90% sensitivity on calibration rows, and measured the resulting false alarms and misses on test rows.', '',
        f"Before missing outcomes are excluded: {prepared['eligible_complete']:,} complete-case records and {prepared['eligible_available']:,} available-input records. "
        f"The wider cohort partitions contain {prepared['partition_counts']['train']:,} training, {prepared['partition_counts']['calibration']:,} calibration and {prepared['partition_counts']['test']:,} test rows. "
        'Every registry ID has the same partition across all arms and targets. Neither model selection nor calibration uses test labels.', '',
        '## Matched complete-case comparison', '',
        'All columns for a target use the same test patients. Brier measures probability error (lower is better); AUC measures ranking (higher is better). '
        'The constant baseline uses training prevalence. New-model values below are after the prespecified calibration step; raw results are retained in JSON.', '',
        '| Target | Test n | Source AUC / Brier | Source recalibrated AUC / Brier | New four-input AUC / Brier | New 15-input AUC / Brier | Constant Brier |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for target in ['cad', 'lad', 'lcx', 'rca']:
        four = result['experiments'][f'four_complete_{target}']
        clinical = result['experiments'][f'clinical_complete_{target}']
        names = [four['models']['source_raw'], four['models']['source_calibrated'],
                 four['models']['selected_calibrated'], clinical['models']['selected_calibrated']]
        values = ' | '.join(f"{m['roc_auc']:.3f} / {m['brier']:.3f}" for m in names)
        lines.append(f"| {target.upper()} | {four['rows']:,} | {values} | {four['models']['constant']['brier']:.3f} |")
    cad = result['experiments']['clinical_complete_cad']
    before = cad['models']['source_raw']; after = cad['models']['selected_calibrated']
    lines += ['', f"For matched CAD test patients, average predicted probability changed from {before['mean_probability']:.1%} "
        f"to {after['mean_probability']:.1%}; observed prevalence was {after['prevalence']:.1%}. "
        'Average agreement alone is insufficient: the reliability chart and bin tables show how probabilities vary across risk groups.', '',
        '## Additional-feature comparison uncertainty', '',
        'Paired 500-resample row bootstrap, calibrated 15-input minus calibrated four-input model on the same patients. '
        'Positive AUC and negative Brier differences favor additional fields. These intervals condition on the fitted pipelines, '
        'omit site clustering and training/selection uncertainty, and are not adjusted for multiple comparisons.', '',
        '| Target | AUC difference 95% interval | Brier difference 95% interval |',
        '|---|---:|---:|']
    for target, stats in result['matched_feature_comparison'].items():
        a, b = stats['auc_difference_95'], stats['brier_difference_95']
        lines.append(f'| {target.upper()} | {a[0]:+.3f} to {a[1]:+.3f} | {b[0]:+.4f} to {b[1]:+.4f} |')
    lines += ['', '## Wider coverage, separately evaluated', '',
        'Missing BMI/LDL/HDL is imputed using training-only medians with missingness indicators. '
        'Age is required. Observed out-of-bounds values and prior/unknown MI/PCI/CABG remain excluded. '
        'This is a different patient mix; its performance cannot be treated as a matched improvement over the complete-case experiment.', '',
        '| Target | Train / calibration / test | Selected family | AUC | Brier / constant Brier | Predicted / observed prevalence |',
        '|---|---:|---|---:|---:|---:|']
    for target in ['cad', 'lad', 'lcx', 'rca']:
        key = f'clinical_available_{target}'; exp = result['experiments'][key]; info = fit['experiments'][key]
        m = exp['models']['selected_calibrated']
        lines.append(f"| {target.upper()} | {len(info['train_rows']):,} / {len(info['calibration_rows']):,} / {exp['rows']:,} | "
            f"{exp['selected_family']} | {m['roc_auc']:.3f} | {m['brier']:.3f} / {exp['models']['constant']['brier']:.3f} | "
            f"{m['mean_probability']:.1%} / {m['prevalence']:.1%} |")
    lines += ['', '## Cutoff tradeoff on the wider cohort', '',
        'The diagnostic cutoff was selected on calibration patients to reach at least 90% sensitivity there. '
        'It is not a recommended clinical threshold; test sensitivity can fall below 90%. '
        'The fixed .5 results remain in the full evidence to avoid hiding poor sensitivity at default classification.', '',
        '| Target | Cutoff | Test sensitivity | Specificity | Missed cases / positives | False alarms / negatives |',
        '|---|---:|---:|---:|---:|---:|']
    for target in ['cad', 'lad', 'lcx', 'rca']:
        e = result['experiments'][f'clinical_available_{target}']; m = e['models']['selected_calibrated']['cutoff90']
        lines.append(f"| {target.upper()} | {m['threshold']:.3f} | {m['sensitivity']:.1%} | {m['specificity']:.1%} | "
            f"{m['missed_cases']} / {e['positives']} | {m['false_positives']} / {e['rows']-e['positives']} |")
    lines += ['', '## Decision and limitations', '',
        'Keep these as separate research candidates. More appropriate training data and calibration can address the measured failure, '
        'but the experiment does not validate the 55-input app or demonstrate reliable use in another population. '
        'The original source-only transport failure remains preserved.', '',
        'The 15 inputs comprise age, BMI, LDL, HDL and opaque nominal codes for sex, hypertension, diabetes, '
        'cholesterol history, family history, current/past smoking, chest pain, typicality, exertion and shortness of breath. '
        'Category meanings have not been guessed or converted into a user-facing input form. '
        'Authoritative code definitions and availability before the prediction point remain review requirements. '
        'CT calcium, imaging function, stenosis and follow-up fields are excluded from predictors.', '',
        'This random patient split does not test a new site or time period. Input missingness can encode site/workflow differences; '
        'the wider-cohort missingness subgroup is descriptive, not a transportability guarantee. '
        'Subgroup metrics by age, sex code and missing numeric input are saved, with small/single-class groups suppressed. '
        'CCTA labels and the original invasive-angiography labels have different reference standards. '
        'The inherited endpoint mapping is inferred from headers, papers and internal consistency, without a formal workbook codebook.', '',
        'Next evidence step: a genuinely unused, compatible cohort with reviewed field definitions and prediction timing. '
        'Do not optimize against these test results and call the next pass independent validation.', '',
        '## Artifacts and reproduction', '',
        '- Protocol: [frozen development design](confirm_development_protocol.md).',
        '- Runner stages: `python scripts/develop_confirm.py prepare`, then `fit`, then `evaluate`. Each refuses to overwrite its outputs.',
        '- Saved pipelines, calibration models, partitions, CV losses, cutoffs, test predictions, bin/subgroup tables and hashes: `ml/experiments/confirm_development_v1/`.',
        '- Read-only evidence checks: `python -m pytest tests/test_confirm_development.py tests/test_confirm_external.py -q`.',
        '- Verification on the delivered artifacts: **8 passed**. These audit both experiment manifests, source/app preservation, partition separation, selected-family rules, calibration-only cutoffs, reproduced metrics, training-only imputation and serialized-model predictions. One read-only workbook-extension warning; no workbook was saved.',
        '- Plot/report reproduction: `python scripts/report_confirm_development.py`.',
        '- [CONFIRM data, Filippo Cademartiri, CC BY 4.0](https://data.mendeley.com/datasets/shntp48zv9/1). Raw workbook and registry IDs are excluded from the source bundle.',
        '- Methods: [probability calibration](https://scikit-learn.org/stable/modules/calibration.html), [threshold selection](https://scikit-learn.org/stable/modules/classification_threshold.html).', '',
        '![CAD development results](../output/research/confirm-development.png)', '']
    report.write_text('\n'.join(lines), encoding='utf-8')
    figure_dir = ROOT/'output/research'; figure_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), layout='constrained')
    colors = ['#ac3b45', '#b2770a', '#3883a1', '#167b66']
    four = result['experiments']['four_complete_cad']['models']
    models = [four['source_raw'], four['source_calibrated'], four['selected_calibrated'], after]
    labels = ['Source unchanged', 'Source recalibrated', 'New four inputs', 'New 15 inputs']
    for m, label, color in zip(models, labels, colors):
        bins = m['reliability_equal_count_bins']
        axes[0].plot([b['predicted'] for b in bins], [b['observed'] for b in bins], 'o-', color=color, label=label)
    axes[0].plot([0, 1], [0, 1], '--', color='#777', linewidth=1)
    axes[0].set(xlabel='Mean predicted probability in bin', ylabel='Observed fraction with CAD',
                title='Reliability: same CAD test patients', xlim=(0, 1), ylim=(0, 1))
    axes[0].legend(fontsize=8, loc='upper left')
    axes[1].barh(labels[::-1], [m['brier'] for m in models][::-1], color=colors[::-1])
    axes[1].axvline(four['constant']['brier'], color='#555', linestyle='--', label='Training-prevalence constant')
    axes[1].set(xlabel='Brier probability error (lower is better)', title='Probability error on matched patients', xlim=(0, .5))
    axes[1].legend(fontsize=8, loc='lower right')
    for index, model in enumerate(models[::-1]):
        axes[1].text(model['brier']+.008, index, f"{model['brier']:.3f}", va='center')
    fig.suptitle('CONFIRM development — research only, not independent validation', fontsize=14)
    fig.savefig(figure_dir/'confirm-development.png', dpi=170)
    fig.savefig(figure_dir/'confirm-development.svg')
    plt.close(fig)
    print(report)


if __name__ == '__main__':
    main()
