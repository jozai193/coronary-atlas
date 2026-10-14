import data from './generated/peerj-operating-summary.json'
import evidenceUrl from './generated/peerj-operating-results.json?url'
import {percent} from './types'

export default function OperatingEvidence(){
  return <details className="external-evidence-details operating-evidence">
    <summary>Detection follow-up: what changes when the cutoff is chosen locally?</summary>
    <p><strong>Exploratory targets · no reviewer guidance yet.</strong> This separate 14-input development study reuses the same 553 people. Each split reserves 331–332 for model training, 111 for calibration and cutoff selection, and 110–111 for evaluation. Evaluation patients never choose their own cutoff. This is not fresh external validation.</p>
    <p>Local learning plus separate calibration reduced Brier error from {data.probabilities.source.brier.toFixed(3)} to {data.probabilities.local_sigmoid.brier.toFixed(3)}. Most of the gain came from local training alone ({data.probabilities.local.brier.toFixed(3)}); the added sigmoid benefit was small and uncertain.</p>
    <div className="external-evidence-scroll" role="region" aria-label="Exploratory cutoff trade-offs" tabIndex={0}><table>
      <caption>Two repeats of the same 553 people · counts shown as repeat 1 / repeat 2</caption>
      <thead><tr><th scope="col">Model / cutoff rule</th><th scope="col">Missed positives / 201</th><th scope="col">False alarms / 352</th><th scope="col">Mean sensitivity</th><th scope="col">Mean specificity</th></tr></thead>
      <tbody>{data.rows.map(r=><tr key={r.method+r.point}><th scope="row">{r.label}</th><td>{r.false_negatives.join(' / ')}</td><td>{r.false_positives.join(' / ')}</td><td>{percent(r.sensitivity)}</td><td>{percent(r.specificity)}</td></tr>)}</tbody>
    </table></div>
    <p><strong>A target is not a guarantee.</strong> The local 90% calibration target achieved {percent(data.rows[4].sensitivity)} evaluation sensitivity; {data.rows[4].folds_below_target} of 10 folds fell below 90%. Against source with the same calibration target, specificity improved by {(data.primary.operating.specificity.difference*100).toFixed(1)} percentage points, while the sensitivity-difference interval included zero. Sigmoid calibration preserved the target-based decisions; local learning provided the ranking improvement.</p>
    <p>Compared with the local model at 0.5, recovering more positives caused more false alarms. Compared with source at 0.5, the local 90% rule still missed more positives. <strong>No clinically preferred cutoff has been selected.</strong> App predictions remain unchanged. A new Beijing data source was left unscored because its published study subset and CAD endpoint could not be reconstructed reliably.</p>
    <a href={evidenceUrl} download="peerj-operating-results.json">Download all cutoff comparisons ↓</a>
  </details>
}
