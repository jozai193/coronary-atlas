import {type Field,type Sample} from './types'
import {observationText} from './observations'
import {inputOrigin,downloadReviewWorksheet} from './reviewWorksheet'
import './DemoProfileContext.css'
import type {ClinicalContext} from './clinicalContext'
import type {ReportEvidence} from './evidenceRecord'

export default function DemoProfileContext({sample,fields,onFind,clinicalContext,reportEvidence}:{sample:Sample;reportEvidence?:ReportEvidence;clinicalContext?:ClinicalContext;fields:Field[];onFind:(name:string)=>void}){
  const groups=[...new Set(fields.map(f=>f.group))]
  const facts=['Age','Sex','BP','PR','EF-TTE','VHD'].map(name=>fields.find(f=>f.name===name)).filter((f):f is Field=>!!f)
  function origin(name:string){return inputOrigin(sample,name)}
  function value(field:Field){
    return observationText(field,sample.features[field.name])
  }
  return <section tabIndex={-1} className="demo-context" aria-label={sample.synthetic?'Synthetic profile input context':'Recorded source profile input context'}>
    <div className="demo-context-head"><div><span className="eyebrow">{sample.synthetic?'SYNTHETIC EXAMPLE · NO ORIGINAL REPORTS':'RECORDED DEVELOPMENT EXAMPLE · ALL 55 MODEL INPUTS'}</span><h2>{sample.name}: input context</h2></div><span className="demo-context-tag">Clinical review pending</span></div>
    <p>{sample.synthetic?'Some values were chosen for this example; other supplied values use source-cohort defaults. Unspecified ECG flags and valve findings remain unknown (—). These combined values have no confirmed diagnosis, ECG tracing or echo report. This assembled profile has not received clinical sign-off.':'All 55 inputs are copied from the attributed public UCI development record, without invented findings. A/B were selected by recorded outcome contrast and original row order, before scoring. These curated cases were used in model development; they are not representative performance samples or independent accuracy evidence. Complete model inputs do not mean a complete clinical history or echo report is available.'}</p>
    {!sample.synthetic&&sample.source&&<p><a href={sample.source.url} target="_blank" rel="noreferrer">UCI source · CC BY 4.0 ↗</a> · Worksheet row {sample.source.worksheet_row}. Original ECG tracing and echo report images are unavailable. Supplied zero codes remain recorded codes; they do not establish that the whole ECG was normal.</p>}
    {sample.recorded_outcomes&&<p><strong>Recorded reference outcomes — not inputs or blockage percentages:</strong> {Object.entries(sample.recorded_outcomes).map(([target,label])=>`${target.toUpperCase()}: ${label}`).join(' · ')}. This development record does not independently validate the model.</p>}
    <dl className="case-facts" aria-label="Case overview">{facts.map(f=><div key={f.name}><dt>{f.label}</dt><dd>{value(f)}</dd></div>)}</dl>
    <div className="case-facts-note"><span>{fields.filter(f=>sample.features[f.name]!=null).length}/{fields.length} supplied</span>{sample.synthetic?<><span>{sample.provenance?.explicit_fields.length??'—'} explicit choices</span><span>{sample.provenance?.default_fields.length??'—'} cohort defaults</span></>:<span>{sample.provenance?.recorded_fields?.length??'—'} recorded source values</span>}<span>{fields.filter(f=>sample.features[f.name]==null).length} unknown</span><button onClick={()=>downloadReviewWorksheet({profile:sample.name,fields,features:sample.features,result:null,sample,clinicalContext,reportEvidence})}>Download input worksheet</button></div>
    {fields.some(f=>f.name==='VHD')&&<div className="demo-valve-context"><strong>Valvular disease input: {String(sample.features.VHD??'—')} · {origin('VHD').toLowerCase()}</strong><p>This is an input finding, not a prediction. The CAD percentage estimates the coronary artery disease label; it does not measure artery narrowing or grade valve disease. {sample.features.VHD==null?'No valve finding was supplied for this example. Prediction is blocked until a valve assessment is supplied.':sample.synthetic?'This synthetic valve value is not supported by an individual echo report.':'The valve category is recorded in the source table; the underlying complete echo report is unavailable.'}</p><button onClick={()=>onFind('VHD')}>Inspect the valvular input ↗</button></div>}
    <details><summary>Review all {fields.length} input values and their origins</summary><p>Recorded source value = observation copied from the public source table. Example choice = explicitly selected demo value. Cohort default = independently filled median or most frequent category. Not supplied = unknown, shown as —. Source codes such as 0/1 and RWMA are retained only for supplied values; a code is not an anatomical lesion description.</p>
      <div className="demo-context-groups">{groups.map(group=><section key={group}><h3>{group}</h3><dl>{fields.filter(f=>f.group===group).map(field=><div key={field.name}><dt><button onClick={()=>onFind(field.name)}>{field.label} ↗</button></dt><dd><strong>{value(field)}</strong><small>{origin(field.name)}</small></dd></div>)}</dl></section>)}</div>
    </details>
  </section>
}
