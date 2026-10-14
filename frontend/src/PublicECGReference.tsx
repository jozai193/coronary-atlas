import {useEffect,useState} from 'react'
import './PublicECGReference.css'

interface ReferenceCase {
  ecg_id:number;provider_fold:number;age:number|null;age_note:string;sex_source_code:number|null
  report:string;validated_by_human:boolean;waveform:string;source_header:string;source_signal:string
  statements:{code:string;description:string;source_likelihood:number}[]
}
interface ReferenceIndex {source:string;version:string;license:string;citation:string;selection:string;signal_display:string;cases:ReferenceCase[]}

export default function PublicECGReference(){
  const [open,setOpen]=useState(false),[data,setData]=useState<ReferenceIndex|null>(null),[selected,setSelected]=useState(''),[error,setError]=useState(''),[retry,setRetry]=useState(0)
  useEffect(()=>{
    if(!open||data)return
    const controller=new AbortController()
    setError('')
    fetch('/reference-ecg/index.json',{signal:controller.signal}).then(response=>{if(!response.ok)throw Error('Public reference ECGs could not load.');return response.json()}).then((index:ReferenceIndex)=>{
      if(!Array.isArray(index.cases)||!index.cases.length)throw Error('The reference library is empty.')
      setData(index);setSelected(String(index.cases[0].ecg_id))
    }).catch(e=>{if(!controller.signal.aborted)setError((e as Error).message)})
    return()=>controller.abort()
  },[open,data,retry])
  const record=data?.cases.find(c=>String(c.ecg_id)===selected)??data?.cases[0]
  return <section id="public-ecg-library" className="public-ecg" aria-label="Public ECG reference library">
    <details onToggle={e=>setOpen(e.currentTarget.open)}>
      <summary>Explore real public ECG references <span>PTB-XL · separate source cases</span></summary>
      <p>These are real de-identified ECG source records from different people than the current profile. Selecting one changes only this reference viewer. It does not load patient inputs, generate a CAD prediction or supply echo findings or coronary blockage measurements.</p>
      {error?<p role="alert">{error} <button onClick={()=>setRetry(n=>n+1)}>Retry ECG library</button></p>:!data?<p role="status">Loading the attributed source reference library…</p>:record&&<>
        <label className="public-ecg-selector"><span>Choose a public ECG record</span><select aria-label="Choose a public ECG record" value={selected} onChange={e=>setSelected(e.target.value)}>{data.cases.map(c=><option key={c.ecg_id} value={c.ecg_id}>PTB-XL {c.ecg_id} · source fold {c.provider_fold}</option>)}</select></label>
        <div className="public-ecg-facts"><span>Source ECG: <strong>{record.ecg_id}</strong></span><span>{record.age_note}: <strong>{record.age??'—'}</strong></span><span>Sex source code: <strong>{record.sex_source_code??'—'}</strong></span><span>Provider split: <strong>{record.provider_fold===9?'Validation':record.provider_fold===10?'Test':'Training'} · fold {record.provider_fold}</strong></span></div>
        <p>Sex codes are retained without recoding. Privacy-protected or unavailable ages stay unknown. These provider splits identify the source records; this viewer does not train or evaluate a model.</p>
        <div className="public-ecg-trace" tabIndex={0} role="region" aria-label={`PTB-XL ${record.ecg_id} waveform; scroll horizontally on small screens`}><img src={record.waveform} alt={`Twelve calibrated source ECG leads for PTB-XL record ${record.ecg_id}, first 2.5 seconds of each lead`}/></div>
        <p>{data.signal_display} <a href={record.waveform} target="_blank" rel="noreferrer">Open full waveform figure ↗</a></p>
        <h3>Original source report string</h3><blockquote>{record.report}</blockquote><p>Preserved as published, without translation or new diagnostic interpretation. PTB-XL reports may originate from a clinician or ECG device. Source human-validation flag: {record.validated_by_human?'true':'false'}.</p>
        <div className="public-ecg-table"><table><caption>Original SCP-ECG statements · source annotations, not CAD model outputs</caption><thead><tr><th>Source code</th><th>Provider description</th><th>Source likelihood</th></tr></thead><tbody>{record.statements.map(s=><tr key={s.code}><th scope="row">{s.code}</th><td>{s.description}</td><td>{s.source_likelihood===0?'Unknown (source code 0)':`${s.source_likelihood}%`}</td></tr>)}</tbody></table></div>
        <p>Unlisted findings remain unknown. ECG annotations do not establish angiographic CAD or LAD/LCX/RCA narrowing. These records cannot be joined to an unrelated echo report or to the current profile.</p>
        <p className="public-ecg-credit">{data.citation} <a href={data.source} target="_blank" rel="noreferrer">Official dataset ↗</a> · <a href="/reference-ecg/LICENSE.txt" target="_blank" rel="noreferrer">{data.license}</a>. Waveform excerpts and layout prepared by Coronary Atlas.</p>
        <p>{data.selection}</p>
      </>}
    </details>
  </section>
}
