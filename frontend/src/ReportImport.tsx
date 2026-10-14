import {useEffect,useRef,useState} from 'react'
import type {Worker} from 'tesseract.js'
import type {Field,Features} from './types'
import {parseReport,applyConfirmed,candidateIssue,type ReportCandidate} from './reportParser'
import {reviewEchoText,type EchoTextReview} from './echoReportReview'
import './ReviewTools.css'

export default function ReportImport({fields,features,busy,onApply,onEchoReview}:{fields:Field[];features:Features;busy:boolean;onApply:(f:Features,names:string[],mode:'replace'|'merge')=>void;onEchoReview?:(review:EchoTextReview)=>string}){
  const [text,setText]=useState(''),[candidates,setCandidates]=useState<ReportCandidate[]>([]),[running,setRunning]=useState(false),[status,setStatus]=useState(''),[error,setError]=useState(''),[preview,setPreview]=useState(''),[mode,setMode]=useState<'replace'|'merge'>('replace')
  const worker=useRef<Worker|null>(null),generation=useRef(0),url=useRef(''),mounted=useRef(true)
  const [echoReview,setEchoReview]=useState<EchoTextReview|null>(null),[echoChecked,setEchoChecked]=useState(false)
  useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;generation.current++;void worker.current?.terminate();if(url.current)URL.revokeObjectURL(url.current)}},[])
  function clear(){generation.current++;void worker.current?.terminate();worker.current=null;if(url.current)URL.revokeObjectURL(url.current);url.current='';setPreview('');setText('');setCandidates([]);setEchoReview(null);setEchoChecked(false);setStatus('');setError('');setRunning(false)}
  async function read(file:File){
    clear();const run=generation.current
    if(!['image/png','image/jpeg','image/webp'].includes(file.type)||file.size>10*1024*1024){setError('Use a PNG, JPEG or WebP image under 10 MB. For PDF, paste text or export one page as an image.');return}
    setRunning(true);setStatus('Checking image…')
    let own:Worker|null=null
    try{
      const bitmap=await createImageBitmap(file);const pixels=bitmap.width*bitmap.height;bitmap.close()
      if(pixels>16000000)throw Error('Use an image under 16 megapixels; crop to one report page.')
      if(generation.current!==run||!mounted.current)return
      url.current=URL.createObjectURL(file);setPreview(url.current)
      const {createWorker}=await import('tesseract.js')
      own=await createWorker('eng',1,{workerPath:'/ocr/worker.min.js',corePath:'/ocr/core',langPath:'/ocr/lang',cacheMethod:'none',workerBlobURL:false,logger:m=>{if(generation.current===run&&mounted.current)setStatus(`${m.status}${m.progress?` · ${Math.round(m.progress*100)}%`:''}`)}})
      if(generation.current!==run||!mounted.current)return
      worker.current=own
      const result=await own.recognize(file,{rotateAuto:true})
      if(generation.current!==run||!mounted.current)return
      setText(result.data.text);setCandidates(parseReport(result.data.text,fields));setEchoReview(reviewEchoText(result.data.text));setStatus('Text read. Check every proposed value against the image; OCR can misread digits and decimals.')
    }catch(e){if(generation.current===run&&mounted.current)setError((e as Error).message)}
    finally{if(own)await own.terminate();if(generation.current===run&&mounted.current){worker.current=null;setRunning(false)}}
  }
  const count=candidates.filter(c=>c.confirmed&&!c.issue).length
  function update(index:number,change:Partial<ReportCandidate>){setCandidates(cs=>cs.map((c,i)=>i===index?{...c,...change}:c))}
  function apply(){const selected=applyConfirmed(candidates,fields,features,mode);if(!selected.imported.length)return;onApply(selected.features,selected.imported,mode);clear();setStatus(`${selected.imported.length} confirmed observations applied. Check the input form before generating a prediction.`)}
  return <details className="report-import"><summary>Import a report photo · assisted autofill</summary>
    <p>Read one de-identified report page in English. Image OCR runs in this browser; images and text are not uploaded or saved by the app. It reads printed numbers, not ECG tracings or echo images. Missing fields remain unknown.</p>
    <fieldset disabled={busy} style={{border:0,padding:0,margin:0}}><label>Choose report image<input aria-label="Choose report image" type="file" accept="image/png,image/jpeg,image/webp" disabled={running} onChange={e=>{if(e.target.files?.[0])void read(e.target.files[0]);e.target.value=''}}/></label>
    {preview&&<img src={preview} alt="Selected report page for checking extracted values"/>}
    {running&&<button onClick={clear}>Cancel reading</button>}
    <label>Report text (paste or correct OCR)<textarea aria-label="Report text" value={text} maxLength={50000} disabled={running} placeholder={'LDL Cholesterol: 110 mg/dL\nEjection fraction: 55 %'} onChange={e=>{setText(e.target.value);setCandidates([]);setEchoReview(null);setEchoChecked(false);setStatus('');setError('')}}/></label>
    <div className="report-actions"><button disabled={!text.trim()||running} onClick={()=>{setCandidates(parseReport(text,fields));setEchoReview(reviewEchoText(text));setEchoChecked(false);setStatus('Review proposals against the original report. Nothing has been entered yet.')}}>Find proposed values</button><button onClick={clear}>Clear report</button></div>
    {echoReview&&Object.values(echoReview).some(lines=>lines.length>0)&&<section className="echo-text-review" aria-label="Echo text for source review"><h3>Echo text for source review</h3><p>Excerpts only; OCR can omit words or misread negations. Check and correct the report text above before copying. Blank measurements stay unknown. EF is reviewed separately below.</p>{echoReview.warnings.map(warning=><p className="report-error" key={warning}>{warning}</p>)}{([['Structure / chamber text',echoReview.structure],['Valve text',echoReview.valves],['Flow / Doppler text',echoReview.flow],['Impression text',echoReview.impression]] as const).map(([heading,lines])=>lines.length>0&&<div key={heading}><h4>{heading}</h4><pre>{lines.join('\n')}</pre></div>)}{onEchoReview&&<><label><input type="checkbox" aria-label="Echo excerpts checked and belong to the current case" checked={echoChecked} onChange={e=>setEchoChecked(e.target.checked)}/> I checked these excerpts against the source and confirmed they belong to the current case. A template/example must not be attached to an unrelated profile.</label><button type="button" disabled={!echoChecked||running} onClick={()=>{const issue=onEchoReview(echoReview);setError(issue);if(!issue){setEchoChecked(false);setStatus('Echo excerpts appended to source-review notes. Add the source reference/date and complete the report check there. Model inputs and predictions were not changed.')}}}>Append reviewed echo text to current case</button></>}</section>}
    {candidates.length>0&&<><div className="report-candidates">{candidates.map((c,i)=>{const f=fields.find(f=>f.name===c.field);return <div className="report-candidate" key={c.field}><label><input type="checkbox" aria-label={`Confirm ${c.field}`} checked={c.confirmed} disabled={!!c.issue} onChange={e=>update(i,{confirmed:e.target.checked})}/><strong>{f?.label??c.field}</strong> {c.value??'—'} {c.unit}</label><small>Source: {c.source}</small>{typeof c.value==='number'&&<label>Correct value<input aria-label={`Correct ${c.field}`} type="number" step="any" value={c.value} onChange={e=>{const value=e.target.value===''?null:Number(e.target.value);update(i,{value,confirmed:false,issue:candidateIssue(f,value)})}}/></label>}{c.issue&&<p className="report-error">{c.issue}</p>}{!c.issue&&features[c.field]!=null&&<small>Existing form value: {features[c.field]} · will change if confirmed.</small>}</div>})}</div>
    <label>Apply to<select aria-label="Report apply mode" value={mode} onChange={e=>setMode(e.target.value as 'replace'|'merge')}><option value="replace">New case · clear other inputs</option><option value="merge">Current case · keep other inputs</option></select></label><p>{mode==='replace'?'All unselected fields will become unknown.':'Use only when this report belongs to the current case and collection context. Existing unselected inputs will remain.'}</p><button disabled={!count||running} onClick={apply}>Apply {count} confirmed observations</button></>}
    {text&&!running&&candidates.length===0&&<p>No proposals yet. Use Find proposed values; unsupported or unreadable observations can be entered manually.</p>}
    <p role="status" className="report-message">{status}</p>{error&&<p role="alert" className="report-error">{error}</p>}
    <p>Supports explicit age/sex, selected labs in printed conventional units, height/weight, resting pulse and echo EF. No inferred diagnoses, disease labels, ECG categories or fasting status. English image prototype; PDF upload and handwriting are not supported. Confirm each value; there is no automatic prediction.</p></fieldset>
  </details>
}
