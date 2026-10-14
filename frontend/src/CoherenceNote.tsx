import {type Result,TARGETS} from './types'
import './CoherenceNote.css'

const score=(value:number)=>`${(value*100).toFixed(2)}%`

export default function CoherenceNote({result}:{result:Result}){
  const adjustment=result.coherence_adjustment
  if(!adjustment.enabled)return <section className="coherence-note" aria-label="Probability adjustment"><strong>Unadjusted model outputs</strong><p>{adjustment.note}</p></section>
  if(adjustment.changed_targets.length===0)return <section className="coherence-note" aria-label="Probability adjustment"><strong>No adjustment needed for this profile</strong><p>{adjustment.note} The raw estimates already place overall CAD at or above each vessel estimate, so displayed and raw probabilities are the same.</p></section>
  return <section className="coherence-note changed" aria-label="Probability adjustment"><strong>Coherence adjustment applied</strong><p>A raw vessel estimate exceeded CAD. The displayed values use a deterministic adjustment so CAD is at least as high as each vessel. Attributions explain the raw values; classes and colors use the displayed values.</p><div className="coherence-table"><span>Target</span><span>Raw model</span><span>Displayed</span>{TARGETS.filter(target=>adjustment.changed_targets.includes(target)).map(target=><div className="coherence-row" key={target}><b>{target.toUpperCase()}</b><span>{score(result[target].model_probability)}</span><strong>{score(result[target].probability)}</strong></div>)}</div><p>Largest change: {(adjustment.max_absolute_change*100).toFixed(2)} percentage points. This enforces an ordering rule; it does not add new clinical evidence or identify a blockage.</p></section>
}
