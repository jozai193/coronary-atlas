import {useState} from 'react'
import data from './generated/modality.json'
import {TARGETS,type Target} from './types'

export default function ModalityEvidence(){
  const [target,setTarget]=useState<Target>('lad'),[run,setRun]=useState(0)
  const rows=data.targets[target][run].rows
  return <section className="modality-evidence" aria-labelledby="modality-title"><span className="eyebrow">EXPERIMENT / INPUT GROUPS</span><h2 id="modality-title">What does each source of information add?</h2><p>Compare the same regularized logistic model trained with different input groups. Each row below is a separately trained model with preprocessing fit only on its training folds. This is a diagnostic experiment, not the deployed model comparison.</p>
    <div className="threshold-controls"><label>Input-group target<select value={target} onChange={e=>setTarget(e.target.value as Target)}>{TARGETS.map(t=><option key={t} value={t}>{t.toUpperCase()}</option>)}</select></label><label>Input-group validation run<select value={run} onChange={e=>setRun(Number(e.target.value))}><option value={0}>Run 1 · 303 records</option><option value={1}>Run 2 · same 303 records</option></select></label></div>
    <div className="modality-table"><table><thead><tr><th>Available observations</th><th>ROC-AUC ↑</th><th>Change from core</th><th>Brier ↓</th></tr></thead><tbody>{rows.map(row=>{const delta=row.roc_auc-rows[0].roc_auc;return <tr key={row.name}><th>{row.name}</th><td>{row.roc_auc.toFixed(3)}</td><td>{row.name==='Clinical core'?'Reference':`${delta>0?'+':''}${delta.toFixed(3)}`}</td><td>{row.brier.toFixed(3)}</td></tr>})}</tbody></table></div>
    <p className="modality-note">Clinical core = demographics, vitals, history and examination. ECG and echo are recorded findings, not images or signals. The same 303 records appear in both runs. Differences are exploratory; they do not establish that a test causes better outcomes or can safely be omitted.</p></section>
}
