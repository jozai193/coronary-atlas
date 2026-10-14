import {type CoherenceEvidence} from './types'
import './CoherenceNote.css'

export default function CoherenceEvidencePanel({evidence}:{evidence:CoherenceEvidence|null}){
  return <section className="coherence-evidence" aria-labelledby="coherence-evidence-title"><h3 id="coherence-evidence-title">Separate coherence adjustment study</h3>
    {!evidence?<p>The adjusted display is a deterministic CAD/vessel ordering rule. The original table above evaluates raw outputs; adjusted-output comparison data are unavailable here.</p>:<>
      <p>Two paired, shared-fold internal repeats refit the models within each training fold, then compare each raw four-output vector with its adjusted vector on the same held-out people. This is distinct from the target-specific raw-model validation above.</p>
      <div className="table-scroll"><table><caption>Mean Brier across four targets · same 303 people in each repeat</caption><thead><tr><th>Repeat</th><th>Raw ↓</th><th>Adjusted ↓</th><th>Rows adjusted</th><th>CAD/vessel conflicts, raw → adjusted</th></tr></thead><tbody>{evidence.repeats.map(run=><tr key={run.repeat}><th>{run.repeat}</th><td>{run.raw_mean_four_target_brier.toFixed(4)}</td><td>{run.adjusted_mean_four_target_brier.toFixed(4)}</td><td>{run.adjusted_rows} / {evidence.rows}</td><td>{run.discordant_rows_raw} → {run.discordant_rows_adjusted}</td></tr>)}</tbody></table></div>
      <p>{evidence.note} The adoption screen {evidence.screen_passed?'passed':'did not pass'} in this development experiment. A lower mean four-target Brier does not establish a gain for every target or a clinical performance claim.</p>
    </>}
  </section>
}
