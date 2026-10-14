"""Render every completed accuracy-goal result into a reviewable Markdown report."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collections import Counter
import numpy as np
from ml import accuracy_ensemble as ensemble
from ml import accuracy_features as features


def main():
    report = ensemble.ROOT / 'docs/accuracy_goal_results.md'
    if report.exists():
        raise FileExistsError('Refusing report overwrite')
    lines = ['# Accuracy goal: executed results - 14 October 2026', '',
        'Two protocols were frozen before their new aggregate outcomes were inspected. Both use the same three repeated five-fold patient partitions of the already studied 303-person source cohort. All four targets share each outer test partition. These are internal development comparisons, not independent or clinical validation.', '',
        'The baseline refits the original model-selection procedure inside each outer training partition and applies the same coherence projection as the current app. Its scores here differ from historical target-specific splits; only within-table comparisons are paired. The baseline models and explanations were preserved. A separately packaged optional ensemble now has its own inference and attributions; see [delivery and verification](accuracy_goal_delivery.md).', '',
        'Primary ensemble candidate: sigmoid uniform. Primary feature candidate: selected ridge. All other procedures are secondary, and the secondary winner is not relabeled as a primary success.', '']
    for title, module in [('Ensemble experiment', ensemble), ('Feature experiment', features)]:
        module.check_receipt()
        result = ensemble.load(module.OUT / 'results.json')
        verification = ensemble.load(module.OUT / 'verification.json')
        if verification['status'] != 'passed' or verification['results_sha256'] != ensemble.digest(module.OUT / 'results.json'):
            raise ValueError('Unverified result')
        lines += [f'## {title}', '',
            '| Candidate | Primary? | Mean Brier difference | Conditional 95% interval | Three repeat differences | Engineering screen |',
            '|---|---|---:|---|---|---|']
        for name, comparison in result['comparisons'].items():
            lower, upper = comparison['brier']['conditional_95_interval']
            repeats = ' / '.join(f'{d:+.5f}' for d in comparison['per_repeat_brier_delta'])
            lines.append(f'| {name} | {comparison["primary"]} | {comparison["brier"]["mean"]:+.5f} | [{lower:+.5f}, {upper:+.5f}] | {repeats} | {"Pass" if comparison["engineering_screen_passed"] else "Fail"} |')
        lines += ['', 'Negative Brier differences favor the candidate. The conditional bootstrap resamples patients after averaging their repeat-level errors; it excludes retraining, prior-search and site uncertainty. Engineering screens are research nomination rules, not tests of clinical usefulness.', '',
            '### Mean projected performance', '',
            '| Target | Procedure | AUC | Brier | Accuracy | Sensitivity | Specificity |',
            '|---|---|---:|---:|---:|---:|---:|']
        arm_names = ['baseline'] + list(result['comparisons'])
        for target in ensemble.ORDER:
            for arm in arm_names:
                rows = [r for r in result['scores'] if r['target'] == target and r['arm'] == arm + '_projected']
                value = lambda key: np.mean([r[key] for r in rows])
                lines.append(f'| {target.upper()} | {arm} | {value("roc_auc"):.4f} | {value("brier"):.4f} | {value("accuracy"):.1%} | {value("recall"):.1%} | {value("specificity"):.1%} |')
        lines += ['', '### All repeats, raw and projected', '',
            '| Repeat | Target | Procedure | AUC | Brier | Average precision | Accuracy | Sensitivity | Specificity | Missed positives | False positives |',
            '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for row in result['scores']:
            cm = row['confusion_matrix']
            lines.append(f'| {row["repeat"]} | {row["target"]} | {row["arm"]} | {row["roc_auc"]:.4f} | {row["brier"]:.4f} | {row["average_precision"]:.4f} | {row["accuracy"]:.1%} | {row["recall"]:.1%} | {row["specificity"]:.1%} | {cm[1][0]} | {cm[0][1]} |')
        relative = module.OUT.relative_to(ensemble.ROOT).as_posix()
        lines += ['', f'Full probabilities, source/partition manifests, fit receipt, result JSON and fresh-process verification: `{relative}/`. Fitted models remain local in its ignored `private/` directory.', '']
    selections = ensemble.load(features.OUT / 'selections.json')
    lines += ['## Feature selection frequencies', '', '| Target | Procedure | Selected configuration | Outer folds |', '|---|---|---|---:|']
    counts = Counter((entry['role'].rsplit('_', 1)[1], arm, index) for entry in selections for arm, index in entry['selected'].items())
    for (target, arm, index), count in sorted(counts.items()):
        lines.append(f'| {target} | {arm} | {features.SPECS[index]} | {count} |')
    lines += ['', '## What remains unresolved', '',
        'Every repeat reuses the same people. The experiments cannot establish independent generalization, resolve undocumented source measurement timing, or pick a clinically appropriate missed-case/false-alarm tradeoff. Raising sensitivity alone is not a general accuracy gain. No target labels or angiography findings were added to model inputs.', '',
        'The new public 130-participant CTP workbook was acquired and audited, but missing demographic inputs and unresolved codes/endpoint definitions prevent treating it as compatible full-input validation. See [the data review](accuracy_goal_data_review.md).', '',
        'Reproduce with the existing research environment: `python -m ml.accuracy_ensemble prepare`, `fit`, `evaluate`; then `python scripts/verify_accuracy_ensemble.py`. For the second stage use `ml.accuracy_features` and `scripts/verify_accuracy_features.py`. Existing result directories are protected against overwrite; a genuinely fresh run needs a separately designated output location and recorded source version.', '']
    report.write_text('\n'.join(lines), encoding='utf-8')
    print(report)


if __name__ == '__main__':
    main()
