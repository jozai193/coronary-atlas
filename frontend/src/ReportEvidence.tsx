import {useEffect,useRef,useState,type Dispatch,type SetStateAction} from 'react'
import type {Field} from './types'
import {candidateIssue} from './reportParser'
import {REPORT_KINDS,REPORT_NAMES,emptyReportEvidence,evidencePercent,reportFileIssue,echoInputDifference,hasReportSource,type ReportEvidence as Evidence,type ReportKind} from './evidenceRecord'
import './ReportEvidence.css'

function Attachment({file}:{file:File|null}){
  const [url,setUrl]=useState('')
  useEffect(()=>{if(!file){setUrl('');return}const next=URL.createObjectURL(file);setUrl(next);return()=>URL.revokeObjectURL(next)},[file])
  return file&&url?<a href={url} target="_blank" rel="noreferrer">Open attached {file.name}</a>:<span>No file attached</span>
}

export default function ReportEvidence({evidence,features,fields,busy=false,onChange,onUseEchoEf}:{evidence:Evidence;features:Record<string,unknown>;fields:Field[];busy?:boolean;onChange?:Dispatch<SetStateAction<Evidence>>;onUseEchoEf?:(value:number)=>void}){
  const [error,setError]=useState('')
  const mounted=useRef(true)
  useEffect(()=>{mounted.current=true;return()=>{mounted.current=false}},[])
  const editable=!!onChange
  const parsedEf=evidencePercent(evidence.echoEf)
  const modelEfIssue=parsedEf.value===null?'':candidateIssue(fields.find(f=>f.name==='EF-TTE'),parsedEf.value)
  const difference=echoInputDifference(evidence,features)
  function update(patch:Partial<Evidence>){onChange?.(current=>({...current,...patch,checked:false}))}
  function source(kind:ReportKind,patch:Partial<Evidence['reports'][ReportKind]>){onChange?.(current=>({...current,reports:{...current.reports,[kind]:{...current.reports[kind],...patch}},checked:false}))}
  async function attach(kind:ReportKind,file:File){
    const issue=reportFileIssue(file);setError(issue);if(issue)return
    source(kind,{file,sha256:''})
    try{
      const digest=await crypto.subtle.digest('SHA-256',await file.arrayBuffer())
      const sha256=Array.from(new Uint8Array(digest),n=>n.toString(16).padStart(2,'0')).join('')
      if(mounted.current)onChange?.(current=>current.reports[kind].file===file?{...current,reports:{...current.reports,[kind]:{...current.reports[kind],sha256}}}:current)
    }catch{if(mounted.current)setError('The report is attached locally, but its file checksum could not be calculated.')}
  }
  const text=(label:string,value:string,change:(value:string)=>void,multiline=false)=>editable?<label><span>{label}</span>{multiline?<textarea aria-label={label} maxLength={2000} value={value} placeholder="— Not supplied" onChange={e=>change(e.target.value)}/>:<input aria-label={label} maxLength={200} value={value} placeholder="— Not supplied" onChange={e=>change(e.target.value)}/>}</label>:<div><strong>{label}</strong><p>{value||'—'}</p></div>
  return <section className="report-evidence" aria-label="Source reports and recorded findings">
    <h2>Source reports and recorded findings</h2>
    <p>Public dataset examples have no original ECG, echo or angiography reports. Add only de-identified reports belonging to the current case. Attachments stay in browser memory and clear on refresh or when another case is loaded. Attachments are never uploaded. Report context stays outside prediction; only an EF you explicitly copy becomes a model input.</p>
    <details><summary>Review reports, flow findings and reported narrowing</summary>
      <fieldset disabled={busy}>
        <legend>Report sources · user supplied and unverified</legend>
        <div className="report-evidence-grid">{REPORT_KINDS.map(kind=>{const report=evidence.reports[kind];return <section key={kind}>
          <h3>{REPORT_NAMES[kind]}</h3>
          {text(`${REPORT_NAMES[kind]} source reference`,report.reference,value=>source(kind,{reference:value}))}
          {text(`${REPORT_NAMES[kind]} report date`,report.date,value=>source(kind,{date:value}))}
          {text(`${REPORT_NAMES[kind]} recorded findings`,report.notes,value=>source(kind,{notes:value}),true)}
          {editable&&<label><span>Attach {REPORT_NAMES[kind]} report</span><input type="file" aria-label={`Attach ${REPORT_NAMES[kind]} report`} accept="application/pdf,image/png,image/jpeg,image/webp" onChange={e=>{if(e.target.files?.[0])void attach(kind,e.target.files[0]);e.target.value=''}}/></label>}
          <Attachment file={report.file}/>
          {report.sha256&&<small className="report-checksum">SHA-256: {report.sha256}</small>}
          {editable&&report.file&&<button type="button" onClick={()=>source(kind,{file:null,sha256:''})}>Remove {REPORT_NAMES[kind]} attachment</button>}
        </section>})}</div>
        <div className="report-evidence-grid">
          <section><h3>Echo / Doppler transcription</h3>
            {text('Reported echo EF (%)',evidence.echoEf,value=>update({echoEf:value}))}
            {parsedEf.issue&&<p role="alert">{parsedEf.issue}</p>}
            {text('Reported blood-flow findings',evidence.echoFlow,value=>update({echoFlow:value}),true)}
            {text('Reported valve narrowing or leakage findings',evidence.echoValves,value=>update({echoValves:value}),true)}
            <p>Copy findings as written. Valve findings and coronary disease probabilities describe different outcomes; the app does not infer a diagnosis or force agreement.</p>
          </section>
          <section><h3>Reported coronary narrowing</h3><p>Only transcribe values explicitly reported by angiography or CCTA. Record the vessel segment, method, date and any qualification in the source findings. These are reported measurements, not model probabilities.</p>
            {(['lad','lcx','rca'] as const).map(v=>{const parsed=evidencePercent(evidence.narrowing[v]);return <div key={v}>{text(`${v.toUpperCase()} reported narrowing (%)`,evidence.narrowing[v],value=>update({narrowing:{...evidence.narrowing,[v]:value}}))}{parsed.issue&&<p role="alert">{parsed.issue}</p>}</div>})}
            {Object.values(evidence.narrowing).some(v=>v.trim())&&!hasReportSource(evidence.reports.angiography)&&<p role="status">Add the angiography/CCTA source reference or report. These entries are currently unlinked and unverified.</p>}
          </section>
        </div>
        {editable?<label className="report-checked"><input type="checkbox" aria-label="Report entries checked against sources for this case" checked={evidence.checked} onChange={e=>onChange?.(current=>({...current,checked:e.target.checked}))}/><span>I checked the entries against the sources and confirmed they belong to this case.</span></label>:<p>User transcription check: {evidence.checked?'Confirmed by user; not independently verified':'Pending'}</p>}
        {difference&&<p className="report-discrepancy" role="status">{difference}</p>}
        {modelEfIssue&&<p role="status">{modelEfIssue} The recorded report value remains unchanged.</p>}
        {editable&&onUseEchoEf&&<button type="button" disabled={!evidence.checked||!hasReportSource(evidence.reports.echo)||parsedEf.value===null||!!modelEfIssue||!!parsedEf.issue} onClick={()=>{if(parsedEf.value!==null)onUseEchoEf(parsedEf.value)}}>Use checked report EF as model input</button>}
        {editable&&<button type="button" onClick={()=>{onChange?.(emptyReportEvidence());setError('')}}>Clear report evidence</button>}
        {error&&<p role="alert">{error}</p>}
        <p>Report notes, attachments and narrowing measurements are excluded from prediction. Using the checked EF explicitly updates the existing EF input and clears the previous estimate. Exports contain report metadata and transcribed findings; file contents are not included.</p>
      </fieldset>
    </details>
  </section>
}
