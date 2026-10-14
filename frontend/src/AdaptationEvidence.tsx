import data from './generated/peerj-adaptation-summary.json'
import evidenceUrl from './generated/peerj-adaptation-results.json?url'
import {percent} from './types'

export default function AdaptationEvidence(){
  return <details className="external-evidence-details adaptation-evidence">
    <summary>Development follow-up: can local examples improve the predictions?</summary>
    <p><strong>Already inspected cohort · separate 14-input CAD task.</strong> We reused these 553 people for a fixed development study. In two five-fold repetitions, each evaluated row was excluded from its own fitting and preprocessing. The small-data fits each used 64 locally labeled rows. This does not mean the whole study used only 64 people, and it is not a fresh external test.</p>
    <p>With 64 labels per fit, sigmoid recalibration reduced mean Brier error from {data.rows[0].brier.toFixed(3)} to {data.rows[3].brier.toFixed(3)}, beyond the local-prevalence baseline ({data.rows[1].brier.toFixed(3)}). Calibration preserved within-fold ranking. Training a local model improved ranking too, particularly with more data.</p>
    <div className="external-evidence-scroll" role="region" aria-label="Local adaptation development comparison" tabIndex={0}><table>
      <caption>Means across two repetitions · same 553 people · 0.5 cutoff</caption>
      <thead><tr><th scope="col">Method</th><th scope="col">Local labels per fit</th><th scope="col">Within-fold AUC ↑</th><th scope="col">Brier error ↓</th><th scope="col">Detection sensitivity</th></tr></thead>
      <tbody>{data.rows.map((r,i)=><tr key={i}><th scope="row">{r.label}</th><td>{r.budget}</td><td>{r.mean_within_fold_auc.toFixed(3)}</td><td>{r.brier.toFixed(3)}</td><td>{percent(r.sensitivity)}</td></tr>)}</tbody>
    </table></div>
    <p><strong>The missed-case cost is substantial.</strong> At 0.5, the primary recalibrated model missed {data.rows[3].false_negatives.join(' / ')} of 201 positives across the two repetitions, versus 16 with the frozen source model. False alarms fell from 294 to {data.rows[3].false_positives.join(' / ')} of 352 negatives. Better probability error does not make this a safe rule-out test.</p>
    <p>Primary Brier difference versus source: {data.primary.source.delta_brier.toFixed(3)} (conditional 95% interval {data.primary.source.conditional_95_interval.map(v=>v.toFixed(3)).join(' to ')}). The bootstrap resamples 553 people after averaging their repeat errors, not 1,106 independent patients. These estimates omit fitting, model-selection and center uncertainty.</p>
    <p><strong>Research decision:</strong> local calibration and local training merit a new untouched evaluation. App predictions remain unchanged. A usable operating point, clinical review and generalization to another center remain unestablished. Calibration here changes probability scale; the AUC column averages within-fold rankings to avoid artifacts from pooling different calibrators.</p>
    <a href={evidenceUrl} download="peerj-adaptation-results.json">Download development metrics ↓</a>
  </details>
}
