import data from './generated/peerj-external-results.json'
import evidenceUrl from './generated/peerj-external-results.json?url'
import {percent} from './types'
import AdaptationEvidence from './AdaptationEvidence'
import OperatingEvidence from './OperatingEvidence'

const primary=data.scores.primary

export default function PeerjEvidence(){
  return <section className="external-evidence" aria-labelledby="peerj-evidence-title">
    <div className="external-evidence-head">
      <div><span className="eyebrow">CHINA / 553 PATIENTS / FROZEN COMPARISON</span><h3 id="peerj-evidence-title">Did the new model travel better?</h3></div>
      <span className="external-evidence-tag">Separate 14-input CAD task</span>
    </div>
    <p>Logistic regression and an Explainable Boosting Machine (EBM) were trained only on the original 303 patients, then frozen before testing on a Chinese hospital cohort. <strong>EBM did not improve ranking or probability error.</strong> This is a separate reduced-input comparison; it does not validate the live 55-input app or its 55-input EBM research candidate.</p>
    <p className="external-evidence-swipe">Scroll the table sideways to see error counts →</p>
    <div className="external-evidence-scroll" role="region" aria-label="China cohort model comparison" tabIndex={0}><table>
      <caption>553 patients · 201 with the study's CHD label · fixed 0.5 cutoff</caption>
      <thead><tr><th scope="col">Model</th><th scope="col">AUC ↑</th><th scope="col">Brier error ↓</th><th scope="col">Mean prediction</th><th scope="col">Missed positives</th><th scope="col">False alarms</th></tr></thead>
      <tbody>{(['logistic','ebm'] as const).map(kind=>{
        const r=primary[kind]
        return <tr key={kind}><th scope="row">{kind==='logistic'?'Logistic regression':'EBM'}</th><td>{r.auc.toFixed(3)}</td><td>{r.brier.toFixed(3)}</td><td>{percent(r.mean_probability)}</td><td>{r.confusion.fn} <small>of {r.positives}</small></td><td className="external-evidence-misses">{r.confusion.fp} <small>of {r.n-r.positives}</small></td></tr>
      })}</tbody>
    </table></div>
    <p className="external-evidence-interpretation">Observed disease prevalence was {percent(primary.logistic.prevalence)}. Both models substantially overpredicted it. The fixed anomaly and age sensitivity checks did not reverse the comparison. No model was promoted from this test.</p>
    <details className="external-evidence-details"><summary>Uncertainty and what this test cannot establish</summary>
      <p>EBM minus logistic AUC: {data.delta_auc.toFixed(3)} (conditional 95% interval {data.paired_bootstrap.conditional_intervals.delta_auc.map(v=>v.toFixed(3)).join(' to ')}). Brier error difference: +{data.delta_brier.toFixed(3)} (interval {data.paired_bootstrap.conditional_intervals.delta_brier.map(v=>v.toFixed(3)).join(' to ')}). These 1,000 paired row-bootstrap draws condition on the fitted models; they omit training and center uncertainty.</p>
      <p>The primary result retains the supplied extreme WBC value; excluding it changes neither conclusion. The study's CHD definition combines clinical assessment with &gt;50% stenosis; the source labels use a nominal ≥50% cutoff. Measurement timing and source units remain incompletely documented. This selected, younger hospital cohort supplies no individual vessel outcomes and cannot establish clinical usefulness or fairness.</p>
    </details>
    <AdaptationEvidence/>
    <OperatingEvidence/>
    <div className="external-evidence-footer"><p><strong>Decision:</strong> preserve the negative result. Better internal performance alone does not justify replacing the app's model. A further candidate needs a reviewed input contract and another untouched evaluation.</p><div className="external-evidence-links"><a href="https://doi.org/10.7717/peerj.14078" target="_blank" rel="noreferrer">Cao et al., PeerJ 2022 ↗</a><a href={evidenceUrl} download="peerj-external-results.json">Download full metrics ↓</a></div></div>
  </section>
}
