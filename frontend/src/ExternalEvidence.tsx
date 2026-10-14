import data from './generated/angiocad-external-results.json'
import evidenceUrl from './generated/angiocad-external-results.json?url'
import {TARGETS,type Target,percent} from './types'
import './ExternalEvidence.css'
import PeerjEvidence from './PeerjEvidence'

const names:Record<Target,string>={cad:'Overall CAD',lad:'LAD',lcx:'LCX',rca:'RCA'}

export default function ExternalEvidence(){
  return <><section className="external-evidence" aria-labelledby="external-evidence-title">
    <div className="external-evidence-head">
      <div><span className="eyebrow">NEW PATIENT POPULATION / FROZEN TEST</span><h3 id="external-evidence-title">What happened at another center?</h3></div>
      <span className="external-evidence-tag">Separate 13-input model</span>
    </div>
    <p>A logistic model trained only on the original 303 patients was frozen before scoring AngioCAD. It used 13 shared clinical inputs. <strong>The live 55-input app above was not externally tested here.</strong> Its internal AUCs and these results cannot be compared as a change caused only by the patient population.</p>
    <p className="external-evidence-swipe">Scroll the table sideways to see detection and miss counts →</p>
    <div className="external-evidence-scroll" role="region" aria-label="AngioCAD score table" tabIndex={0}><table>
      <caption>Primary AngioCAD center test · fixed 0.5 decision cutoff</caption>
      <thead><tr><th scope="col">Target</th><th scope="col">Patients</th><th scope="col">AUC ↑</th><th scope="col">Detected positives</th><th scope="col">Missed positives</th></tr></thead>
      <tbody>{TARGETS.map(t=>{
        const result=data.scores.primary_main[t]
        const {fn,tp}=result.confusion
        return <tr key={t}>
          <th scope="row">{names[t]}</th>
          <td>{result.n}</td>
          <td>{result.roc_auc.toFixed(3)}</td>
          <td>{percent(result.sensitivity)} <small>({tp}/{tp+fn})</small></td>
          <td className={t==='lcx'||t==='rca'?'external-evidence-misses':''}>{fn} <small>of {tp+fn}</small></td>
        </tr>
      })}</tbody>
    </table></div>
    <p className="external-evidence-interpretation">The LCX model missed 54 of 90 positive records; RCA missed 106 of 155. CAD detected 257 of 276 positives, but also flagged 44 of 69 negatives. These are research results, not a clinical rule-out test.</p>
    <div className="external-evidence-footer"><p><strong>Endpoint limits:</strong> AngioCAD's main-vessel bins above 50% were positive; unresolved 26–50% bins were excluded per target. The source labels use a nominal ≥50% cutoff, so endpoint matching is imperfect. Counts vary by target. This was a selected angiography cohort, not a general screening population.</p><div className="external-evidence-links"><a href="https://doi.org/10.5281/zenodo.15826856" target="_blank" rel="noreferrer">AngioCAD dataset ↗</a><a href={evidenceUrl} download="angiocad-external-results.json">Download full metrics ↓</a></div></div>
  </section><PeerjEvidence/></>
}
