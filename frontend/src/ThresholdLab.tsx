import {useState} from 'react'
import data from './generated/improvement.json'
import evidenceUrl from './generated/improvement.json?url'
import {TARGETS,type Target,percent} from './types'

const policies = [
  {key:'fixed',title:'Default cutoff',detail:'Probability ≥50%'},
  {key:'balanced',title:'Balance detection & false alarms',detail:'Cutoff selected on training folds'},
  {key:'recall80',title:'Aim for 80% detection',detail:'Training target; held-out results may fall short'},
] as const

export default function ThresholdLab(){
  const [target,setTarget]=useState<Target>('lcx')
  const [repeat,setRepeat]=useState(0)
  const run=data.targets[target].runs[repeat]
  return <section className="threshold-lab" aria-labelledby="threshold-title">
    <div className="threshold-heading"><div><span className="eyebrow">EXPERIMENT / DECISION CUTOFFS</span><h2 id="threshold-title">Catch more cases. See the cost.</h2></div><a href={evidenceUrl} download="cardiofolio-cutoff-evidence.json">Download evidence ↓</a></div>
    <p>A lower decision cutoff can detect more positive cases while raising more false alarms. Compare three rules on held-out raw-model probabilities. This experiment does not measure the coherence-adjusted display or change the patient prediction above.</p>
    <div className="threshold-controls"><label>Compare target<select value={target} onChange={e=>setTarget(e.target.value as Target)}>{TARGETS.map(t=><option key={t} value={t}>{t.toUpperCase()}</option>)}</select></label><label>Validation run<select value={repeat} onChange={e=>setRepeat(Number(e.target.value))}><option value={0}>Run 1 · 303 records</option><option value={1}>Run 2 · same 303 records</option></select></label><span>ROC-AUC <b>{run.auc.toFixed(3)}</b><small>Same probabilities for all three rules</small></span></div>
    <div className="threshold-policies">{policies.map(policy=>{
      const m=run.policies[policy.key]
      const [[tn,fp],[fn,tp]]=m.confusion_matrix
      const range=policy.key==='fixed'?null:run.cutoff_ranges[policy.key]
      return <article key={policy.key} aria-label={policy.title}>
        <h3>{policy.title}</h3><p>{policy.detail}</p>
        <dl><div><dt>Positive cases detected</dt><dd>{percent(m.recall)}<small>{tp} / {tp+fn} positives</small></dd></div><div><dt>Negative cases cleared</dt><dd>{percent(m.specificity)}<small>{tn} / {tn+fp} negatives</small></dd></div><div><dt>Positive prediction precision</dt><dd>{percent(m.precision)}<small>{tp} / {tp+fp} flagged</small></dd></div><div><dt>Cases missed</dt><dd>{fn}<small>False negatives</small></dd></div><div><dt>False alarms</dt><dd>{fp}<small>False positives</small></dd></div></dl>
        <p className="cutoff-note">{range?`Training-selected cutoffs: ${percent(range[0])}–${percent(range[1])} across five outer folds.`:'One fixed 50% cutoff in every fold.'}</p>
      </article>
    })}</div>
    <p className="threshold-footnote">Exploratory internal validation: both runs reuse the same 303 people. Each alternative cutoff was chosen using only its outer training rows. The 80% target is an engineering experiment, not a clinical recommendation or a guaranteed detection rate. More complex models were also evaluated; none met our raw-model replacement criteria.</p>
  </section>
}
