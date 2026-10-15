import { useEffect, useRef, useState } from 'react'
import Papa from 'papaparse'
import { ArrowUpRight, ChevronDown, FileUp, FlaskConical, RotateCcw, Search, Download } from 'lucide-react'
import { type Field,type Features,type Sample } from './types'
import {categoryLabel,parseCsvObservation,UNKNOWN_OBSERVATION} from './observations'
import {fieldContext} from './reviewWorksheet'
import {completenessIssue} from './predictionReadiness'
export {categoryLabel} from './observations'

export default function PatientForm({fields,features,samples,busy,onChange,onSample,onPredict,onNewCase,focusField}:{fields:Field[];features:Features;samples:Sample[];busy:boolean;onChange:(f:Features)=>void;onSample:(s:Sample)=>void;onPredict:()=>void;onNewCase?:(f:Features)=>void;focusField?:{name:string;revision:number}}){
  const [group,setGroup]=useState('Demographics'),[error,setError]=useState(''),[query,setQuery]=useState(''),[missingOnly,setMissingOnly]=useState(false)
  const [editing,setEditing]=useState(true)
  const upload=useRef<HTMLInputElement>(null)
  const root=useRef<HTMLElement>(null)
  useEffect(()=>{if(!focusField)return;setEditing(true);setQuery(focusField.name);setMissingOnly(false)
    const timer=setTimeout(()=>{const input=Array.from(root.current?.querySelectorAll<HTMLInputElement|HTMLSelectElement>('[data-field]')??[]).find(el=>el.dataset.field===focusField.name);input?.scrollIntoView?.({block:'center',behavior:'instant'});input?.focus({preventScroll:true})},0)
    return()=>clearTimeout(timer)
  },[focusField])
  const groups=[...new Set(fields.map(f=>f.group))]
  const count=fields.filter(f=>features[f.name]!==null&&features[f.name]!==undefined).length
  const weight=features.Weight, height=features.Length, suppliedBMI=features.BMI
  const calculatedBMI=typeof weight==='number'&&typeof height==='number'&&height>0?weight/(height/100)**2:null
  const bmiSpec=fields.find(f=>f.name==='BMI')
  const bmiConflict=calculatedBMI!==null&&typeof suppliedBMI==='number'&&Math.abs(suppliedBMI-calculatedBMI)>0.2
  const calculatedBMIOutside=calculatedBMI!==null&&bmiSpec!==undefined&&(calculatedBMI<bmiSpec.minimum!||calculatedBMI>bmiSpec.maximum!)
  const outOfRange=fields.find(f=>f.kind==='number'&&typeof features[f.name]==='number'&&!(f.name==='BMI'&&calculatedBMI!==null)&&(Number(features[f.name])<f.minimum!||Number(features[f.name])>f.maximum!))
  const availableCount=count+(calculatedBMI!==null&&suppliedBMI==null?1:0)
  const filled=(f:Field)=>features[f.name]!==null&&features[f.name]!==undefined||(f.name==='BMI'&&calculatedBMI!==null)
  const filtered=fields.filter(f=>(`${f.label} ${f.name} ${f.group}`).toLowerCase().includes(query.trim().toLowerCase())&&(!missingOnly||!filled(f)))
  const incomplete=completenessIssue(features,fields)
  const ready=!incomplete&&availableCount>=28&&features.Age!=null&&!outOfRange&&!bmiConflict&&!calculatedBMIOutside
  const entirelyMissing=(name:string)=>{
    const groupFields=fields.filter(f=>f.group===name)
    return groupFields.length>0&&groupFields.every(f=>!filled(f))
  }
  const missingGroupWarnings=ready?[
    entirelyMissing('Laboratory')?'All laboratory observations are missing. In a post-hoc internal test on complete records, masking this group changed LCX/RCA raw estimates. Performance on naturally incomplete records has not been validated.':null,
    entirelyMissing('Echocardiography')?'All echocardiography observations are missing. In a post-hoc internal test on complete records, masking this group changed LAD raw estimates. Performance on naturally incomplete records has not been validated.':null,
  ].filter((warning):warning is string=>warning!==null):[]
  const reason=outOfRange?`${outOfRange.label} is outside this model’s observed range (${outOfRange.minimum}–${outOfRange.maximum} ${outOfRange.unit}). Check the entry.`:calculatedBMIOutside?'BMI calculated from weight and height is outside this model’s observed range.':bmiConflict?'BMI does not match weight and height. Check the three entries.':incomplete?incomplete:availableCount<28?`Add ${28-availableCount} more observations, or load an example.`:`${count} supplied${calculatedBMI!==null&&suppliedBMI==null?' · BMI calculated':''} · ${fields.length-availableCount} will be imputed`
  function template(){const blob=new Blob([Papa.unparse([Object.fromEntries(fields.map(f=>[f.name,'']))])],{type:'text/csv'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='cardiofolio-input-template.csv';a.click();URL.revokeObjectURL(url)}
  function change(field:Field,value:string){onChange({...features,[field.name]:value===''?null:field.kind==='number'?Number(value):value})}
  function csv(file:File){
    setError('')
    if(file.size>100000){setError('CSV must be under 100 KB and contain one patient.');return}
    Papa.parse<Record<string,string>>(file,{header:true,skipEmptyLines:true,complete:r=>{
      if(r.errors.length||r.data.length!==1||r.meta.renamedHeaders&&Object.keys(r.meta.renamedHeaders).length){setError('Use one header row and exactly one patient row, with unique columns.');return}
      const unknown=Object.keys(r.data[0]).filter(k=>!fields.some(f=>f.name===k))
      if(unknown.length){setError(`Unknown/prohibited columns: ${unknown.join(', ')}`);return}
      const parsed:Features={}
      try{for(const f of fields)parsed[f.name]=parseCsvObservation(f,r.data[0][f.name])}catch(e){setError((e as Error).message);return}
      ;(onNewCase??onChange)(parsed)
    },error:e=>setError(e.message)})
  }
  return <aside ref={root} className="patient panel"><div className="panel-heading"><div><span className="eyebrow">01 / OBSERVATIONS</span><h2>Patient inputs</h2></div><span className="count">{count}<small>/55</small></span></div>
    <div className="sample-box"><FlaskConical size={17}/><div><label htmlFor="sample">Choose an example profile</label><select id="sample" disabled={busy} value="" onChange={e=>{const s=samples.find(s=>s.id===e.target.value);if(s){setError('');onSample(s)}}}><option value="">Choose a demonstration…</option>{samples.map(s=><option value={s.id} key={s.id}>{s.name}</option>)}</select></div></div>
    <div className="input-caption">Use synthetic or de-identified observations. A dash (—) means unknown; 0 is a supplied value or source code, never a missing-value substitute. Valvular disease is an input; the CAD estimate does not grade valve severity.</div>
    <button type="button" className="editor-toggle" aria-expanded={editing} onClick={()=>setEditing(!editing)}>{editing?'Hide input fields':'Edit observations'}<ChevronDown size={15} style={{transform:editing?'rotate(180deg)':''}}/></button>
    {editing&&<><div className="input-search"><Search size={15}/><input aria-label="Search observations" placeholder="Find a measurement…" value={query} onChange={e=>setQuery(e.target.value)}/>{query&&<button type="button" aria-label="Clear observation search" onClick={()=>setQuery('')}>×</button>}</div>
    <label className="missing-filter"><input type="checkbox" checked={missingOnly} onChange={e=>setMissingOnly(e.target.checked)}/>Show missing only <span>{fields.length-count}</span></label></>}
    <form onSubmit={e=>{e.preventDefault();if(ready)onPredict()}}>
      {editing&&<fieldset disabled={busy}>{groups.map((g,i)=>{const matching=filtered.filter(f=>f.group===g);const open=!!query||missingOnly||group===g;return matching.length>0&&<div className="field-group" key={g}>
        <button className="group-toggle" type="button" aria-expanded={open} onClick={()=>setGroup(group===g?'':g)}><span><small>{String(i+1).padStart(2,'0')}</small>{g}</span><span className="group-count">{fields.filter(f=>f.group===g&&filled(f)).length}/{fields.filter(f=>f.group===g).length}<ChevronDown size={14} style={{transform:open?'rotate(180deg)':''}}/></span></button>
        {open&&<div className="fields">{matching.map(f=><label key={f.name} className="field"><span>{f.label}<small title={f.unit_note}>{f.unit}</small></span>{f.kind==='number'?<input data-field={f.name} aria-label={f.label} type="number" min={f.name==='BMI'&&calculatedBMI!==null?undefined:f.minimum??0} max={f.name==='BMI'&&calculatedBMI!==null?undefined:f.maximum??1000000} step="any" value={features[f.name]??''} placeholder={f.name==='BMI'&&calculatedBMI!==null?`Calculated: ${calculatedBMI.toFixed(1)}`:UNKNOWN_OBSERVATION} title="A dash means unknown. Clear the field to leave it unknown." onChange={e=>change(f,e.target.value)}/>:<select data-field={f.name} aria-label={f.label} value={features[f.name]??''} onChange={e=>change(f,e.target.value)}><option value="">— Unknown</option>{f.options?.map(v=><option key={v} value={v}>{categoryLabel(v)}</option>)}</select>}{fieldContext(f.name)&&<small className="field-context">{fieldContext(f.name)}</small>}</label>)}</div>}
      </div>})}{filtered.length===0&&<p className="search-empty">{missingOnly&&count===fields.length?'All observations supplied.':'No matching observations.'}</p>}</fieldset>}
      <div className="form-bottom"><div className="completion-track" role="progressbar" aria-label="Observations supplied" aria-valuenow={count} aria-valuemin={0} aria-valuemax={fields.length}><span style={{width:`${count/fields.length*100}%`}}/></div><p className="readiness" aria-live="polite">{reason}</p>{missingGroupWarnings.length>0&&<div className="warnings input-missing-warnings" role="status">{missingGroupWarnings.map(warning=><p key={warning}>{warning}</p>)}</div>}<button className="primary" disabled={busy||!ready} type="submit">{busy?'Computing predictions…':'Generate prediction'}<ArrowUpRight size={19}/></button><div className="form-secondary"><button disabled={busy} type="button" onClick={()=>upload.current?.click()}><FileUp size={14}/>Import CSV</button><button type="button" onClick={template} title="Download a CSV template"><Download size={13}/>Template</button><button disabled={busy} type="button" onClick={()=>{setError('');(onNewCase??onChange)(Object.fromEntries(fields.map(f=>[f.name,null])))}}><RotateCcw size={13}/>Clear</button></div><input ref={upload} aria-label="Upload patient CSV" type="file" accept=".csv" hidden onChange={e=>{if(e.target.files?.[0])csv(e.target.files[0]);e.target.value=''}}/>{error&&<p role="alert" className="error">{error}</p>}<details className="input-help"><summary>Input and missing-value guidance</summary><p>Age, echo EF, valve assessment, all seven recorded ECG fields and at least 28 available observations are required by this prototype. These requirements do not constitute a complete echo report. This is an engineering guard, not a clinically validated minimum. BMI is calculated when weight and height are provided; conflicting entries cannot be used. Numeric values must be within the source cohort’s observed ranges. Missing values remain null in the input snapshot and are imputed from training data, never replaced by zero. CSV accepts blanks or dashes for unknown values, and displayed category choices or their source codes. Units use conventional interpretations; verify source coding before entering measurements.</p></details></div>
    </form>
  </aside>
}
