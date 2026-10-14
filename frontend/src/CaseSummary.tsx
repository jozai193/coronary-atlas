import {useEffect,useRef} from 'react'
import {type Field,type Features,type Result,type Sample,TARGETS,NAMES,percent} from './types'
import {observationText} from './observations'
import {downloadReviewWorksheet,inputOrigin,fieldContext} from './reviewWorksheet'
import './ReviewTools.css'
import RiskHistory from './RiskHistory'
import {emptyClinicalContext,type ClinicalContext} from './clinicalContext'
import ReportEvidence from './ReportEvidence'
import {emptyReportEvidence,type ReportEvidence as Evidence} from './evidenceRecord'

export default function CaseSummary({profile,fields,features,result,sample,imported=[],clinicalContext=emptyClinicalContext(),reportEvidence=emptyReportEvidence(),onBack}:{profile:string;fields:Field[];features:Features;result:Result|null;sample?:Sample;imported?:string[];clinicalContext?:ClinicalContext;reportEvidence?:Evidence;onBack:()=>void}){
  const heading=useRef<HTMLHeadingElement>(null)
  useEffect(()=>{heading.current?.focus();window.scrollTo({top:0,behavior:'instant'})},[])
  const snapshot=result?.input_snapshot??features
  const unknown=fields.filter(f=>snapshot[f.name]==null)
  const row=(f:Field)=><tr key={f.name}><th scope="row">{f.label}</th><td>{observationText(f,snapshot[f.name])}</td><td>{snapshot[f.name]==null?'Not supplied':imported.includes(f.name)?'Report extraction confirmed by user':inputOrigin(sample,f.name)}{fieldContext(f.name)&&<small>{fieldContext(f.name)}</small>}</td></tr>
  const table=(selected:Field[])=><div className="summary-scroll"><table><thead><tr><th>Observation</th><th>Entered value</th><th>Origin / context</th></tr></thead><tbody>{selected.map(row)}</tbody></table></div>
  return <main className="case-summary" aria-label="Case summary">
    <div className="summary-heading"><button onClick={onBack}>← Back to workspace</button><button onClick={()=>downloadReviewWorksheet({profile,fields,features,result,sample,imported,clinicalContext,reportEvidence})}>Download review worksheet</button></div>
    <span className="eyebrow">CURRENT CASE · RESEARCH REVIEW</span><h1 ref={heading} tabIndex={-1}>Case summary</h1><h2>{profile}</h2>
    <p>{sample?(sample.synthetic?'Synthetic example; no original ECG/echo images or confirmed outcome.':'Recorded public development-dataset example; not independent validation. Original ECG/echo reports are unavailable.'):'Entered observations; check their source and units. User-supplied report evidence, when available, appears separately below.'} {fields.length-unknown.length}/{fields.length} supplied · {unknown.length} unknown.</p>
    <section><h2>Key observations</h2>{table(fields.filter(f=>['Age','Sex','Weight','Length','BMI','BP','PR','DM','HTN','Current Smoker','EX-Smoker','Typical Chest Pain','Atypical','Dyspnea','FBS','LDL','HDL','TG'].includes(f.name)))}</section>
    <RiskHistory fields={fields} features={snapshot} context={clinicalContext}/>
    <ReportEvidence evidence={reportEvidence} features={snapshot} fields={fields}/>
    {sample?.recorded_outcomes&&<section><h2>Recorded source outcome labels</h2><p>Reference labels only; never prediction inputs. These are categories, not measured blockage percentages. This record was used in model development and is not an independent test.</p><div className="summary-scroll"><table><thead><tr><th>Target</th><th>Recorded label</th></tr></thead><tbody>{TARGETS.map(t=><tr key={t}><th>{t.toUpperCase()}</th><td>{sample.recorded_outcomes?.[t]}</td></tr>)}</tbody></table></div></section>}
    <section><h2>ECG and echo findings</h2><p>Selected echo inputs only — not a complete echo report. Only EF, an RWMA source code and a valve category are represented. Echo findings and CAD probabilities describe different quantities.</p>{['EF-TTE','VHD'].some(name=>snapshot[name]==null)&&<p><strong>Incomplete echo information for clinical review.</strong> Supply both EF and a valve assessment before prediction. Imputed values are not measured findings.</p>}{table(fields.filter(f=>['Electrocardiography','ECG','Echocardiography'].includes(f.group)))}</section>
    <section><h2>Model estimates</h2>{result?<><p>Probabilities for dataset labels; not measured narrowing or diagnostic certainty. Version {result.model_version}.</p><div className="summary-estimates">{TARGETS.map(t=><article key={t}><h3>{t.toUpperCase()}</h3><p>{NAMES[t]}</p><strong>{percent(result[t].probability)}</strong><small>Raw model: {percent(result[t].model_probability)}</small><p>Top raw model factors: {result[t].explanation.factors.slice(0,3).map(f=>`${fields.find(s=>s.name===f.feature)?.label??f.feature} (${f.contribution>0?'raises':'lowers'} output)`).join(', ')}.</p></article>)}</div><p>{result.coherence_adjustment.note}</p>{result.warnings.map(w=><p key={w}>{w}</p>)}</>:<p>No current prediction. Return to the workspace, check the inputs, then generate an estimate. Previous outputs are cleared when inputs change.</p>}</section>
    <section><h2>Missing information</h2>{unknown.length?<details open={unknown.length<=12}><summary>{unknown.length} unknown observations</summary><p>{unknown.map(f=>f.label).join(', ')}</p></details>:<p>No missing model inputs.</p>}<p>{result?(unknown.length?'The trained preprocessing imputed missing inputs for computation. Their actual values remain unknown.':'All model inputs were supplied; no missing-input imputation was needed.'):'Unknown values remain blank; they are never filled with zero.'} A low estimate cannot rule out disease. The served models have internal validation only.</p></section>
    <details><summary>All {fields.length} observations</summary>{table(fields)}</details>
    <p className="summary-limit">Educational research prototype. No treatment recommendations or clinical approval. Reference anatomy is shared, not patient imaging.</p>
  </main>
}
