import type {Field} from './types'
import {observationText} from './observations'
import {CONTEXT_FIELDS,contextText,parseContextNumber,type ClinicalContext} from './clinicalContext'
import './RiskHistory.css'

export default function RiskHistory({fields,features,context,busy=false,onChange,onFind}:{fields:Field[];features:Record<string,unknown>;context:ClinicalContext;busy?:boolean;onChange?:(c:ClinicalContext)=>void;onFind?:(name:string)=>void}){
  const editable=!!onChange
  const modelFields=['Current Smoker','EX-Smoker','LDL','HDL','TG'].map(name=>fields.find(f=>f.name===name)).filter((f):f is Field=>!!f)
  return <section className="risk-history" aria-label="Smoking alcohol and lipid review">
    <h2>Smoking, alcohol and lipid profile</h2>
    <p>Current/former smoking, LDL, HDL and triglycerides are model inputs. Smoking duration, alcohol, total cholesterol and lifestyle details below are review context only; they do not change the prediction. The training dataset does not contain these additional variables. Using them to change a score requires a newly trained and independently evaluated model.</p>
    <div className="risk-model-facts">{modelFields.map(f=><div key={f.name}><span>{f.name==='EX-Smoker'?'Former smoking':f.label}</span><strong>{observationText(f,features[f.name])}</strong>{onFind&&<button disabled={busy} aria-label={`Edit ${f.label}`} onClick={()=>onFind(f.name)}>Edit model input ↗</button>}</div>)}</div>
    <p className="risk-history-note">Smoking flags are source codes, not a full smoking history. Check reported history against the current/former smoking inputs; notes do not change those flags. Unknown context stays as a dash. The public dataset does not provide alcohol history, lifestyle details or total cholesterol; values entered here have separate, unverified provenance.</p>
    {editable?<fieldset disabled={busy}><legend>Additional clinical context · excluded from prediction</legend><div className="risk-context-fields">{CONTEXT_FIELDS.map(f=><label key={f.key}><span>{f.label}{f.unit&&<small>{f.unit}</small>}</span>{f.kind==='alcohol'?<select aria-label={f.label} value={context.alcohol_status} onChange={e=>onChange?.({...context,alcohol_status:e.target.value as ClinicalContext['alcohol_status']})}><option value="">— Unknown</option><option value="never">Never used (reported)</option><option value="former">Former use (reported)</option><option value="current">Current use (reported)</option></select>:f.kind==='number'?<input aria-label={f.label} type="number" min="0" max="1000000" step="any" placeholder="—" value={context[f.key]??''} onChange={e=>onChange?.({...context,[f.key]:parseContextNumber(e.target.value)})}/>:<textarea aria-label={f.label} maxLength={500} placeholder="— Not supplied" value={context[f.key]??''} onChange={e=>onChange?.({...context,[f.key]:e.target.value})}/>}</label>)}</div></fieldset>:<dl className="risk-context-readonly">{CONTEXT_FIELDS.map(f=><div key={f.key}><dt>{f.label}</dt><dd>{contextText(context,f.key)}</dd></div>)}</dl>}
    <p className="risk-history-note">Record reported history and measurements, including the collection context where available. This prototype does not recommend lifestyle treatment or estimate the effect of a lifestyle change.</p>
  </section>
}
