import {useEffect,useRef} from 'react'
import {ArrowRight,ArrowLeft,Check,Compass,X} from 'lucide-react'
import {type Sample,type Result,type Target,type ModelInfo,type Evaluation,type CandidateInfo,NAMES,percent} from './types'
import {observationText} from './observations'

const STEPS=['Choose a case','Read the inputs','Find the vessel','Explain the estimate','Check the evidence']
interface Props {step:number;setStep:(n:number)=>void;samples:Sample[];result:Result|null;busy:boolean;selected:Target;info:ModelInfo;evaluation:Evaluation|null;candidate?:CandidateInfo|null;onExplore:(s:Sample)=>void;onSelect:(t:Target)=>void;onFind:(name:string)=>void;onDetails:(tab:'explain'|'evidence')=>void;onClose:()=>void}

export default function GuidedCase({step,setStep,samples,result,busy,selected,info,evaluation,candidate,onExplore,onSelect,onFind,onDetails,onClose}:Props){
  const target=selected
  const heading=useRef<HTMLHeadingElement>(null)
  useEffect(()=>{heading.current?.focus({preventScroll:true})},[step])
  const prediction=result?.[target]
  const factors=prediction?.explanation.factors.slice(0,3)??[]
  const experimental=target==='lcx'&&result?.model_version==='1.0.0+histgb-lcx-v2'
  const ensemble=result?.model_version==='1.0.0+calibrated-ensemble-v1'
  const evidence=ensemble?candidate?.ensemble?.runs?.[0]?.targets[target]?.candidate:experimental?candidate?.runs?.[0]?.candidate:evaluation?.targets?.[target]?.metrics
  const observations=['Age','BP','Typical Chest Pain','LDL','EF-TTE'].filter(name=>info.features.some(f=>f.name===name))
  function change(n:number){setStep(n)}
  return <section tabIndex={-1} className="guided-case" aria-label="Guided case walkthrough">
    <div className="guide-top"><span><Compass size={17}/>GUIDED CASE · ABOUT 2 MINUTES</span><button onClick={onClose} aria-label="Close guided walkthrough"><X size={18}/></button></div>
    <ol className="guide-steps" aria-label="Walkthrough steps">{STEPS.map((s,i)=><li key={s}><button disabled={busy||i>0&&!result} aria-current={i===step?'step':undefined} onClick={()=>change(i)}><b>{i<step?<Check size={13}/>:i+1}</b><span>{s}</span></button></li>)}</ol>
    <div className="guide-content" aria-live="polite"><div className="guide-copy"><span className="eyebrow">STEP {step+1} OF 5</span><h2 tabIndex={-1} ref={heading}>{STEPS[step]}</h2>
      {step===0&&<p>Begin with an example profile. The four probabilities and explanations will be computed by the actual models. Synthetic profiles have no known diagnosis. Recorded source examples were used in development; they are not independent tests.</p>}
      {step===1&&<p>These are the observations the model receives. ECG and echo inputs are recorded findings; this dataset contains no scans. Select a measurement to find it in the form.</p>}
      {step===2&&<p>Select a coronary artery to focus the reference heart. LCX runs toward the back, so its focus view differs from LAD. The same selection controls the explanation below.</p>}
      {step===3&&<p>For {NAMES[target]}, the raw model assigns {prediction?percent(prediction.model_probability):'—'}; the displayed estimate is {prediction?percent(prediction.probability):'—'}. These contributions explain the raw model output before any coherence adjustment, not a treatment effect.</p>}
      {step===4&&<p>A prediction needs context. Check how often this model missed positive cases and raised false alarms on held-out rows. This selected demonstration case cannot establish accuracy.</p>}
    </div><div className="guide-interaction">
      {step===0&&<><div className="guide-options">{samples.map(s=><button disabled={busy} key={s.id} onClick={()=>onExplore(s)}><span>Load guided profile {s.id.toUpperCase()}</span><small>Age {s.features.Age??'—'} · {s.synthetic?'synthetic':'recorded source'}</small><ArrowRight size={17}/></button>)}</div><p className="guide-status">{busy?'Computing four predictions…':result?'Example ready. Continue to its observations.':'Choose either example to begin.'}</p></>}
      {step===1&&<div className="guide-observations">{observations.map(name=>{const field=info.features.find(f=>f.name===name)!;const value=result?.input_snapshot[name];return <button key={name} onClick={()=>onFind(name)}><span>{field.label}</span><strong>{observationText(field,value)}{value==null&&<small>Unknown · imputed</small>}</strong><small>Find in inputs ↗</small></button>})}</div>}
      {step===2&&<><div className="guide-vessels">{(['lad','lcx','rca'] as Target[]).map(t=><button key={t} aria-pressed={target===t} onClick={()=>onSelect(t)}><strong>{t.toUpperCase()}</strong><span>{NAMES[t]}</span><small>{result?percent(result[t].probability):'—'} displayed probability</small></button>)}</div><p className="guide-status">Whole-vessel predictions on shared anatomy. Baseline display values may be coherence adjusted; the raw model values remain available in the explanation. No plaque location or narrowing percentage.</p></>}
      {step===3&&<><div className="guide-factors">{factors.map(f=><button key={f.feature} onClick={()=>onFind(f.feature)}><b className={f.contribution>0?'positive':'negative'}>{f.contribution>0?'↑':f.contribution<0?'↓':'·'}</b><span>{info.features.find(s=>s.name===f.feature)?.label??f.feature}<small>{f.contribution>0?'Raises':f.contribution<0?'Lowers':'Does not change'} raw model output · inspect measurement ↗</small></span></button>)}</div><button className="guide-link" onClick={()=>onDetails('explain')}>Open the complete model explanation <ArrowRight size={14}/></button></>}
      {step===4&&<>{evidence&&<div className="guide-evidence"><div><strong>{percent(evidence.recall)}</strong><span>{target.toUpperCase()} positives detected</span></div><div><strong>{evidence.confusion_matrix[1][0]}</strong><span>Positive cases missed</span></div><div><strong>{evidence.confusion_matrix[0][1]}</strong><span>False alarms</span></div></div>}<p className="guide-status">{ensemble?'Research calibrated ensemble, coherence-adjusted internal run 1 on shared folds.':experimental?'Experimental LCX raw-model internal run 1 after a broad model search.':'Original raw baseline five-fold internal evaluation.'} Cutoff 0.5. The coherence-adjusted baseline was tested separately on shared folds. No independent clinical validation.</p><button className="guide-link" onClick={()=>onDetails('evidence')}>Compare cutoffs and review all evidence <ArrowRight size={14}/></button></>}
    </div></div>
    {!result&&step>0&&<p role="status" className="guide-stale">The inputs changed. Generate a new prediction or choose a guided example before continuing.</p>}
    <div className="guide-bottom"><button disabled={step===0||busy} onClick={()=>change(step-1)}><ArrowLeft size={15}/>Back</button><span>Selected example · real model outputs</span>{step<4?<button className="guide-next" disabled={busy||!result} onClick={()=>change(step+1)}>Next: {STEPS[step+1].toLowerCase()}<ArrowRight size={15}/></button>:<button className="guide-next" onClick={onClose}>Finish walkthrough<Check size={15}/></button>}</div>
  </section>
}
