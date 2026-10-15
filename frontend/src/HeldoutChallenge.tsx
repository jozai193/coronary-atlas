import {useEffect,useRef,useState} from 'react'
import {ArrowRight,BookOpen,Info} from 'lucide-react'
import {api} from './api'
import {NAMES,percent,type Target,TARGETS} from './types'
import './HeldoutChallenge.css'

interface Observation {label:string;value:string}
interface TeachingCase {id:string;observations:Observation[]}
interface CaseIndex {source:string;source_url:string;method:string;note:string;cases:TeachingCase[]}
interface Reveal {case_id:string;target:Target;probability:number;label:0|1;predicted_label:0|1;fold:number;note:string}

type VesselTarget = Exclude<Target,'cad'>

export default function HeldoutChallenge({openRequest=0,onInspectVessel,onLeaveReference}:{openRequest?:number;onInspectVessel:(vessel:VesselTarget,caseId:string)=>void;onLeaveReference:()=>void}){
  const [open,setOpen]=useState(false)
  const [index,setIndex]=useState<CaseIndex|null>(null)
  const [caseId,setCaseId]=useState('A')
  const [target,setTarget]=useState<Target>('cad')
  const [guess,setGuess]=useState<0|1|null>(null)
  const [reveal,setReveal]=useState<Reveal|null>(null)
  const [busy,setBusy]=useState(false)
  const [error,setError]=useState('')
  const serial=useRef(0)
  const revealElement=useRef<HTMLDivElement>(null)
  useEffect(()=>{
    if(reveal&&window.innerWidth<=600){
      const reducedMotion=window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches
      revealElement.current?.scrollIntoView?.({block:'center',behavior:reducedMotion?'auto':'smooth'})
    }
  },[reveal])

  async function loadIndex(){
    setBusy(true);setError('')
    try{setIndex(await api<CaseIndex>('/held-out/cases'))}
    catch(e){setError((e as Error).message)}
    finally{setBusy(false)}
  }
  useEffect(()=>{if(openRequest>0){setOpen(true);if(!index)void loadIndex()}},[openRequest])
  function toggle(){const next=!open;setOpen(next);if(!next)onLeaveReference();if(next&&!index)void loadIndex()}
  function changeCase(id:string){serial.current++;onLeaveReference();setCaseId(id);setGuess(null);setReveal(null);setBusy(false);setError('')}
  function changeTarget(value:Target){serial.current++;onLeaveReference();setTarget(value);setGuess(null);setReveal(null);setBusy(false);setError('')}
  async function makeGuess(value:0|1){
    const current=++serial.current
    onLeaveReference()
    setGuess(value);setReveal(null);setBusy(true);setError('')
    try{const answer=await api<Reveal>(`/held-out/cases/${caseId}/${target}`);if(serial.current===current)setReveal(answer)}
    catch(e){if(serial.current===current)setError((e as Error).message)}
    finally{if(serial.current===current)setBusy(false)}
  }
  const active=index?.cases.find(item=>item.id===caseId)
  const modelCorrect=reveal?.label===reveal?.predicted_label
  return <section className="heldout-challenge" aria-label="Held-out case challenge">
    <div className="heldout-head"><div><span className="eyebrow">AN INTERACTIVE MODEL CHECK</span><h2>Can you read a held-out case?</h2><p>Choose a source-cohort case, make a guess, then compare it with the saved outer-fold result.</p></div><button onClick={toggle} aria-expanded={open}><BookOpen size={16}/>{open?'Close challenge':'Try four cases'}<ArrowRight size={15}/></button></div>
    {open&&<div className="heldout-body">
      {busy&&!index&&<p role="status">Loading saved evaluation cases…</p>}
      {error&&<p className="heldout-error" role="alert">{error} <button onClick={()=>{if(index&&guess!==null)void makeGuess(guess);else void loadIndex()}}>Retry</button></p>}
      {index&&<>
        <div className="heldout-controls"><div role="group" aria-label="Choose a teaching case">{index.cases.map(item=><button key={item.id} onClick={()=>changeCase(item.id)} aria-pressed={caseId===item.id}>Case {item.id}</button>)}</div><label>Dataset label to guess <select value={target} onChange={e=>changeTarget(e.target.value as Target)}>{TARGETS.map(item=><option key={item} value={item}>{item.toUpperCase()} · {NAMES[item]}</option>)}</select></label></div>
        <div className="heldout-stage"><div><span className="eyebrow">CASE {caseId} · LIMITED OBSERVATIONS</span><div className="heldout-observations">{active?.observations.map(item=><div key={item.label}><span>{item.label}</span><strong>{item.value}</strong></div>)}</div><p>These are broad bands from one anonymized source row. The model used all 55 observations; these four bands cannot explain its output.</p></div><div className="heldout-question"><h3>Was the {target.toUpperCase()} label positive?</h3><p>Make your own guess before seeing the original cohort’s angiography label and held-out model estimate.</p><div className="heldout-answers"><button disabled={busy} aria-pressed={guess===1} onClick={()=>void makeGuess(1)}>Yes</button><button disabled={busy} aria-pressed={guess===0} onClick={()=>void makeGuess(0)}>No</button></div>{busy&&<span role="status">Retrieving saved result…</span>}</div></div>
        {reveal&&<div ref={revealElement} className="heldout-reveal" aria-live="polite"><div><span className="eyebrow">SAVED OUTER-FOLD RESULT</span><strong>{percent(reveal.probability)}</strong><small>Raw {target.toUpperCase()} model probability · fold {reveal.fold} of 5</small></div><div><p>Your guess: <strong>{guess?'positive':'negative'}</strong> · Dataset label: <strong>{reveal.label?'positive':'negative'}</strong></p><p>At the fixed 0.5 cutoff, the model said <strong>{reveal.predicted_label?'positive':'negative'}</strong>. {modelCorrect?'It matched this row’s label.':reveal.label?'It missed this positive row.':'It raised a false alarm on this row.'}</p><small>{reveal.note}</small>{reveal.target==='cad'?<p className="heldout-anatomy-note">CAD is an overall disease label, so it has no single reference artery. Choose LAD, LCX or RCA above to inspect a named vessel.</p>:<button className="heldout-inspect" onClick={()=>onInspectVessel(reveal.target as VesselTarget,reveal.case_id)}>Inspect {reveal.target.toUpperCase()} on reference heart <ArrowRight size={14}/></button>}</div></div>}
        <div className="heldout-foot"><Info size={15}/><p>Four cases were intentionally chosen to show one true positive, true negative, false positive and false negative for CAD. They are <strong>not a random sample or external validation</strong>. Different targets may have different outer folds. Source units are conventional interpretations because the original unit dictionary is incomplete. <a href={index.source_url} target="_blank" rel="noreferrer">UCI source ↗</a></p></div>
      </>}
    </div>}
  </section>
}
