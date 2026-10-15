import {useEffect,useRef,useState} from 'react'
import {Activity,ArrowUpRight,BookOpen,Check,Download,Info,ShieldCheck,ArrowRight,Plus} from 'lucide-react'
import {api} from './api'
import {type CandidateInfo,type CoherenceEvidence,type ModelVariant,type Evaluation,type Features,type ModelInfo,type Result,type Sample,type Target,TARGETS,NAMES,color,percent} from './types'
import HeartViewer from './HeartViewer'
import PatientForm from './PatientForm'
import {completenessIssue} from './predictionReadiness'
import ExplanationPanel from './ExplanationPanel'
import Evidence from './Evidence'
import GuidedCase from './GuidedCase'
import ModelComparison from './ModelComparison'
import CoherenceNote from './CoherenceNote'
import HeldoutChallenge from './HeldoutChallenge'
import PublicECGReference from './PublicECGReference'
import DemoProfileContext from './DemoProfileContext'
import InvestigationContext from './InvestigationContext'
import ReviewWorkspace from './ReviewWorkspace'
import CadEstimate from './CadEstimate'
import CaseSummary from './CaseSummary'
import ReportImport from './ReportImport'
import RiskHistory from './RiskHistory'
import {emptyClinicalContext,type ClinicalContext} from './clinicalContext'
import ReportEvidence from './ReportEvidence'
import {emptyReportEvidence,serializeReportEvidence,appendEchoReview} from './evidenceRecord'

export default function App(){
  const [explanationOpen,setExplanationOpen]=useState(true)
  const [challengeRequest,setChallengeRequest]=useState(0)
  const [view,setView]=useState<'explore'|'inputs'|'evidence'>('explore')
  const [info,setInfo]=useState<ModelInfo|null>(null),[samples,setSamples]=useState<Sample[]>([]),[evaluation,setEvaluation]=useState<Evaluation|null>(null)
  const [features,setFeatures]=useState<Features>({}),[result,setResult]=useState<Result|null>(null),[selected,setSelected]=useState<Target>('lad'),[busy,setBusy]=useState(false),[error,setError]=useState(''),[profile,setProfile]=useState('Manual observations'),[,setTab]=useState<'explain'|'evidence'>('explain'),[dirty,setDirty]=useState(false)
  const [guideStep,setGuideStep]=useState<number|null>(null),[focusField,setFocusField]=useState<{name:string;revision:number}>()
  const [guideProfile,setGuideProfile]=useState<string|null>(null)
  const [candidate,setCandidate]=useState<CandidateInfo|null>(null),[modelVariant,setModelVariant]=useState<ModelVariant>('baseline')
  const [coherence,setCoherence]=useState<CoherenceEvidence|null>(null)
  const [referenceCase,setReferenceCase]=useState<{caseId:string;target:Exclude<Target,'cad'>}|null>(null)
  const [reviewOpen,setReviewOpen]=useState(false)
  const [summaryOpen,setSummaryOpen]=useState(window.location.hash==='#summary'),[imported,setImported]=useState<string[]>([])
  useEffect(()=>{const change=()=>setSummaryOpen(window.location.hash==='#summary');window.addEventListener('hashchange',change);return()=>window.removeEventListener('hashchange',change)},[])
  function openSummary(){window.location.hash='summary';setSummaryOpen(true)}
  function closeSummary(){history.replaceState(null,'',window.location.pathname+window.location.search);setSummaryOpen(false);setTimeout(()=>focusSection('.summary-launch'),0)}
  const [clinicalContext,setClinicalContext]=useState<ClinicalContext>(emptyClinicalContext)
  const [reportEvidence,setReportEvidence]=useState(emptyReportEvidence)
  const [reportImportCase,setReportImportCase]=useState(0)
  function resetReportEvidence(){setFocusField(undefined);setReportEvidence(emptyReportEvidence());setReportImportCase(n=>n+1)}
  const revision=useRef(0)
  function findMeasurement(name:string){setView('inputs');setFocusField(f=>({name,revision:(f?.revision??0)+1}))}
  function openView(next:'explore'|'inputs'|'evidence'){setView(next);setTimeout(()=>focusSection(next==='explore'?'.explore-view':next==='inputs'?'.inputs-view':'.evidence-view'),0)}
  function focusSection(selector:string){const el=document.querySelector<HTMLElement>(selector);for(let parent=el?.parentElement;parent;parent=parent.parentElement){if(parent instanceof HTMLDetailsElement)parent.open=true}el?.scrollIntoView?.({block:'start',behavior:'instant'});el?.focus({preventScroll:true})}
  function returnToGuide(){focusSection('.guided-case')}
  function closeGuide(){setGuideStep(null);setTimeout(()=>document.querySelector<HTMLButtonElement>('.start-guide')?.focus(),0)}
  function guidedSelect(t:Target){setView('explore');setSelected(t);setTimeout(()=>focusSection('.anatomy'),0)}
  function inspectHeldoutVessel(target:Exclude<Target,'cad'>,caseId:string){setView('explore');setReferenceCase({caseId,target});setSelected(target);setGuideStep(null);setTimeout(()=>focusSection('.anatomy'),0)}
  function startGuide(){setView('explore');setGuideStep(0);setGuideProfile(null);setTimeout(()=>focusSection('.guided-case'),0)}
  function startReview(){setView('inputs');setReviewOpen(true);setGuideStep(null);setReferenceCase(null);setTimeout(()=>focusSection('.review-workspace'),0)}
  function reviewNavigate(section:'inputs'|'heart'|'estimate'|'references'){setView(section==='inputs'?'inputs':section==='references'?'evidence':'explore');setTimeout(()=>focusSection(section==='inputs'?'.patient':section==='heart'?'.anatomy':section==='references'?'#public-ecg-library':'.cad-card'),0)}
  async function initialize(){setError('');try{const [i,s,e,c,h]=await Promise.all([api<ModelInfo>('/model/info'),api<Sample[]>('/review-profiles').then(s=>Array.isArray(s)&&s.length?s:api<Sample[]>('/sample-patients')).catch(()=>api<Sample[]>('/sample-patients')),api<Evaluation>('/model/metrics'),api<CandidateInfo>('/model/candidates').catch(()=>null),api<CoherenceEvidence>('/model/coherence').catch(()=>null)]);setCandidate(c);setCoherence(h);setInfo(i);setSamples(s);setEvaluation(e);setFeatures(Object.fromEntries(i.features.map(f=>[f.name,null])))}catch(e){setError((e as Error).message)}}
  useEffect(()=>{void initialize()},[])
  function edit(f:Features){setView('inputs');setImported(names=>names.filter(n=>f[n]===features[n]));revision.current++;setReferenceCase(null);setFeatures(f);setResult(null);setDirty(true);setError('');setProfile('Edited observations');if(guideStep!==null){setGuideStep(0);setGuideProfile(null)}}
  function sample(s:Sample){setView('inputs');resetReportEvidence();setClinicalContext(emptyClinicalContext());setImported([]);revision.current++;setReferenceCase(null);setFeatures({...s.features});setResult(null);setDirty(true);setError('');setProfile(s.name);if(guideStep!==null){setGuideStep(0);setGuideProfile(null)}}
  function replaceCase(f:Features){resetReportEvidence();setClinicalContext(emptyClinicalContext());edit(f);setImported([])}
  async function predict(input:Features=features){const insufficient=info?completenessIssue(input,info.features):'Model schema is not loaded.';if(insufficient){setResult(null);setDirty(true);setError(insufficient);setTimeout(()=>focusSection('.patient'),0);return}const requestedRevision=revision.current;setReferenceCase(null);setBusy(true);setError('');setResult(null);try{const r=await api<Result>('/predict',{features:input,model_variant:modelVariant});if(revision.current===requestedRevision){setResult(r);setDirty(false);setView('explore')}}catch(e){if(revision.current===requestedRevision)setError((e as Error).message)}finally{setBusy(false)}}
  function changeModel(v:ModelVariant){revision.current++;setReferenceCase(null);setModelVariant(v);setResult(null);setDirty(true);setError('');if(guideStep!==null){setGuideStep(0);setGuideProfile(null)}}
  function explore(s:Sample){sample(s);if(info&&completenessIssue(s.features,info.features)){setTimeout(()=>focusSection('.patient'),0);return}setView('explore');void predict(s.features)}
  function guidedExplore(s:Sample){explore(s);setGuideProfile(s.id)}
  function showDetails(t:'explain'|'evidence'){setTab(t);setView(t==='evidence'?'evidence':'explore');setTimeout(()=>focusSection(t==='evidence'?'.evidence-view':'#model-details'),0)}
  function download(){if(!result)return;const blob=new Blob([JSON.stringify({...result,profile,clinical_context:clinicalContext,clinical_context_used_by_model:false,report_evidence:serializeReportEvidence(reportEvidence),educational_only:true},null,2)],{type:'application/json'});const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download='cardiofolio-research-result.json';a.click();URL.revokeObjectURL(u)}
  const loadedExample=samples.find(s=>s.name===profile)
  const incompleteExample=info&&loadedExample?completenessIssue(features,info.features):''
  const completeExample=info?samples.find(s=>!s.synthetic&&!completenessIssue(s.features,info.features)):undefined
  if(summaryOpen&&info)return <CaseSummary reportEvidence={reportEvidence} clinicalContext={clinicalContext} profile={profile} fields={info.features} features={features} result={referenceCase?null:result} sample={loadedExample} imported={imported} onBack={closeSummary}/>
  return <><header className="topbar">
    <a className="brand" href="/" aria-label="Cardiofolio home"><span className="brand-mark"><svg width="27" height="32" viewBox="0 0 32 36" fill="none" aria-hidden="true"><path d="M5 5l11 27L27 5M16 32V10m0 12L8 16m8 0l7-6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg></span>Cardio<span>folio</span></a>
    <nav aria-label="Workspace"><button className={view==='explore'?'nav-active':''} aria-current={view==='explore'?'page':undefined} onClick={()=>openView('explore')}>Explore</button><button className={view==='inputs'?'nav-active':''} aria-current={view==='inputs'?'page':undefined} onClick={()=>openView('inputs')}>Inputs &amp; reports</button><button className={view==='evidence'?'nav-active':''} aria-current={view==='evidence'?'page':undefined} onClick={()=>openView('evidence')}>Evidence</button></nav>
    <span className="research"><i/>Educational prototype</span>
  </header>
  <main className="atlas-workspace">
    <div className="workspace-intro"><div><span className="folio">CORONARY ANATOMY &amp; MODEL EVIDENCE</span><h1>Understand the heart <em>behind the estimate.</em></h1><p>A working atlas for medical learners and educators.</p></div><div className="intro-actions"><button className="start-guide text-action" disabled={busy} onClick={startGuide}><BookOpen size={15}/>Start guided case</button><button className="review-start text-action" disabled={busy} onClick={startReview}>Start clinician review<ArrowUpRight size={14}/></button></div></div>
    <section className="case-toolbar" aria-label="Example profiles">
      <div className="case-choices"><span>Start with a case</span>{samples.map(s=><button key={s.id} disabled={busy} aria-pressed={profile===s.name} onClick={()=>explore(s)} aria-label={`Explore profile ${s.id.toUpperCase()} Age ${s.features.Age??'unknown'} ${info&&completenessIssue(s.features,info.features)?'incomplete':'complete recorded example'}`}><span>{s.id.toUpperCase()}</span><strong>Profile {s.id.toUpperCase()}</strong><small>{s.features.Age??'—'} years</small><span className="sr-only">{info&&completenessIssue(s.features,info.features)?'Incomplete · input review only':'Required inputs supplied'}</span></button>)}</div>
      <button className="own-case" disabled={!info||busy} onClick={()=>{if(info){replaceCase(Object.fromEntries(info.features.map(f=>[f.name,null])));setProfile('Your own case');openView('inputs')}}}><Plus size={16}/>Start your own case</button>
      <div className="summary-launch" tabIndex={-1}><button disabled={!info||busy||referenceCase!==null} onClick={openSummary}>Open case summary<ArrowUpRight size={15}/></button></div>
    </section>
    <div className="case-strip"><div><span className="eyebrow">{referenceCase?'HELD-OUT CASE · REFERENCE VIEW':'CURRENT CASE'}</span><strong>{referenceCase?'Case '+referenceCase.caseId+' · linked '+referenceCase.target.toUpperCase()+' · viewing '+(selected==='cad'?'LAD':selected.toUpperCase()):profile}</strong><small>{referenceCase?'Saved fold result stays in the challenge; live estimates are hidden here.':modelVariant==='baseline'?'Baseline · coherence adjusted':modelVariant==='calibrated_ensemble_v1'?'Research ensemble · coherence adjusted':'Experimental LCX · unadjusted outputs'}</small></div><span className={referenceCase?'status':result?'status ready':'status'}>{referenceCase?'Reference heart':result?<><Check size={13}/>Prediction ready</>:busy?'Computing…':dirty?'Inputs changed · recompute':'Choose a case to begin'}</span></div>
    {incompleteExample&&<section className="warnings" role="status" aria-label="Incomplete example profile"><Info size={18}/><div><strong>{loadedExample?.name} · input review only</strong><p>{incompleteExample} Unknown observations have been left blank.</p>{completeExample&&<button disabled={busy} onClick={()=>explore(completeExample)}>Load complete recorded profile {completeExample.id.toUpperCase()}</button>}</div></section>}
    {error&&<div className="error-banner" role="alert"><strong>Unable to complete request.</strong> {error}{!info&&<button onClick={initialize}>Retry connection</button>}</div>}
    {info&&guideStep!==null&&<GuidedCase step={guideStep} setStep={setGuideStep} samples={samples} result={guideProfile?result:null} busy={busy} selected={selected} info={info} evaluation={evaluation} candidate={candidate} onExplore={guidedExplore} onSelect={guidedSelect} onFind={findMeasurement} onDetails={showDetails} onClose={closeGuide}/>}
    {!info?<div className="startup">{error?'The server may be waking up. Choose Retry connection in a moment.':'Loading the atlas…'}</div>:<>
      <section className="explore-view" aria-label="Explore workspace" tabIndex={-1} hidden={view!=='explore'}>
        <div className="workspace">
          <div className="center-column"><HeartViewer result={referenceCase?null:result} selected={selected} onSelect={setSelected}/>{guideStep!==null&&<button className="return-guide" onClick={returnToGuide}><BookOpen size={15}/>Return to guided case · step {guideStep+1} of 5 <ArrowRight size={15}/></button>}</div>
          <aside className="results" aria-label="Model estimates">
          {referenceCase?<div className="risk-card heldout-reference-card"><span className="eyebrow">HELD-OUT CASE {referenceCase.caseId} · ANATOMY ONLY</span><h2>Case {referenceCase.caseId} links to {NAMES[referenceCase.target]}</h2><p>Currently exploring {NAMES[selected==='cad'?'lad':selected]} on the shared reference heart. It does not show this patient’s anatomy, a lesion, or the saved fold probability.</p><p>The saved result remains in the challenge. Live-profile estimates are hidden here.</p><button onClick={()=>setReferenceCase(null)}>Return to live workspace <ArrowRight size={14}/></button><button onClick={()=>{setView('evidence');setTimeout(()=>focusSection('.heldout-challenge'),0)}}>Review saved case ↑</button></div>:<>
            <CadEstimate result={result} onInspectInputs={()=>reviewNavigate('inputs')}/>
            <div className="vessel-results">{(['lad','lcx','rca'] as Target[]).map(v=><button key={v} onClick={()=>setSelected(v)} aria-pressed={selected===v} className={`risk-card vessel-card ${selected===v?'active':''}`}><div className="vessel-head"><span><i style={{background:color(result?.[v].probability)}}/>{v.toUpperCase()}</span><ArrowUpRight size={15}/></div><p>{NAMES[v]}</p><div className="vessel-value"><strong style={{color:color(result?.[v].probability)}}>{result?percent(result[v].probability):'—'}</strong><span>{result?result[v].category:'Not computed'}</span></div></button>)}</div>
            <p className="estimate-boundary">Model probabilities, not measured artery narrowing.</p>
            {result&&<details className="adjustment-detail" open={result.coherence_adjustment.changed_targets.length>0}><summary>{result.coherence_adjustment.changed_targets.length?'Display adjustment applied':'About the displayed probabilities'}</summary><CoherenceNote result={result}/></details>}
            {result&&<div className="reliability-note"><p>{modelVariant==='baseline'?'Baseline LCX/RCA recall was about 40% in the original internal test.':modelVariant==='calibrated_ensemble_v1'?'Ensemble LCX/RCA sensitivity was 42.9% / 38.6% in reused-cohort internal runs.':'Experimental LCX recall was 52–55%; baseline RCA recall was about 40% internally.'} A low estimate cannot rule out disease.</p><button onClick={()=>showDetails('evidence')}>Read the evidence <ArrowRight size={13}/></button></div>}
            <button className="export" disabled={!result} onClick={download}><Download size={15}/>Export research result</button>
          </>}
          </aside>
        </div>
        {!referenceCase&&result&&result.warnings.length>0&&<div className="warnings"><Info size={18}/><div>{result.warnings.map(w=><p key={w}>{w}</p>)}</div></div>}
        {!referenceCase&&loadedExample?.synthetic&&<p className="synthetic-note">Synthetic demonstration profile. No ground-truth diagnosis; this example is not evaluation evidence.</p>}
        <div className="learning-route"><div><span className="folio">A LESSON IN UNCERTAINTY</span><strong>Can you spot a model error?</strong><p>Compare a saved held-out prediction with its recorded label.</p></div><button onClick={()=>{setChallengeRequest(n=>n+1);setView('evidence');setTimeout(()=>focusSection('.heldout-head button'),0)}}>Try the teaching challenge<ArrowRight size={16}/></button></div>
        <div tabIndex={-1} className="bottom-tabs" id="model-details"><button className="active" onClick={()=>{setTab('explain');setExplanationOpen(true)}}><Activity size={16}/>Prediction explanation</button><button onClick={()=>showDetails('evidence')}><BookOpen size={16}/>Validation &amp; model details<ArrowUpRight size={13}/></button></div>
        <details className="explanation-disclosure" open={explanationOpen} onToggle={e=>setExplanationOpen(e.currentTarget.open)}><summary><span>Read the model’s reasoning <small>{selected.toUpperCase()} · raw output &amp; contributing observations</small></span><span aria-hidden="true" className="disclosure-symbol"/></summary>
        <ExplanationPanel result={referenceCase?null:result} selected={selected} onSelect={setSelected} fields={info.features} onFind={findMeasurement}/>
        </details>
      </section>
      <section className="inputs-view" aria-label="Inputs and reports workspace" tabIndex={-1} hidden={view!=='inputs'}>
        <div className="section-intro"><div><span className="folio">01 / THE OBSERVATIONS</span><h2>Your case, your observations.</h2><p>Enter values, import a CSV, or review a report. Unknown values stay blank.</p></div><button className="text-action" onClick={()=>openView('explore')}>Back to the heart<ArrowRight size={15}/></button></div>
        {reviewOpen&&<ReviewWorkspace clinicalContext={clinicalContext} imported={imported} samples={samples} fields={info.features} features={features} profile={profile} result={referenceCase?null:result} busy={busy} onSample={s=>{sample(s);setTimeout(()=>focusSection('.demo-context'),0)}} onNavigate={reviewNavigate} onClose={()=>{setReviewOpen(false);setTimeout(()=>document.querySelector<HTMLButtonElement>('.review-start')?.focus(),0)}}/>}
        <div className="input-layout"><PatientForm key={reportImportCase} onNewCase={replaceCase} fields={info.features} features={features} samples={samples} busy={busy} onChange={edit} onSample={sample} onPredict={()=>void predict()} focusField={focusField}/><div className="case-tools">
          <ReportImport key={reportImportCase} fields={info.features} features={features} busy={busy} onEchoReview={review=>{const next=appendEchoReview(reportEvidence,review);if(!next.issue)setReportEvidence(next.evidence);return next.issue}} onApply={(f,names,mode)=>{if(mode==='replace'){setClinicalContext(emptyClinicalContext());resetReportEvidence()}edit(f);setImported(names);setProfile('Report observations · user confirmed')}}/>
          {!referenceCase&&<ReportEvidence evidence={reportEvidence} features={features} fields={info.features} busy={busy} onChange={setReportEvidence} onUseEchoEf={value=>edit({...features,'EF-TTE':value})}/>}
          {!referenceCase&&<details className="supporting-detail"><summary>Additional history <span>Smoking, alcohol &amp; lifestyle notes</span></summary><RiskHistory fields={info.features} features={features} context={clinicalContext} busy={busy} onChange={setClinicalContext} onFind={findMeasurement}/></details>}
          {!referenceCase&&loadedExample&&<details className="supporting-detail source-detail"><summary>About this example <span>Recorded values &amp; source labels</span></summary><DemoProfileContext reportEvidence={reportEvidence} clinicalContext={clinicalContext} sample={loadedExample} fields={info.features} onFind={findMeasurement}/></details>}
          {!referenceCase&&(features.Age!=null||result)&&<details className="supporting-detail"><summary>ECG &amp; echo observations <span>Review the entered findings</span></summary><InvestigationContext result={result} features={features} fields={info.features} onFind={findMeasurement}/></details>}
          <p className="local-note"><ShieldCheck size={14}/>Use de-identified data. Report files stay in this browser; confirmed observations are sent only when you generate a prediction.</p>
        </div></div>
      </section>
      <section className="evidence-view" aria-label="Evidence workspace" tabIndex={-1} hidden={view!=='evidence'}>
        <div className="section-intro"><div><span className="folio">03 / BEHIND THE ESTIMATE</span><h2>Evidence, including the limitations.</h2><p>Inspect evaluation results, compare research models, or explore separate public references.</p></div><button className="text-action" onClick={()=>openView('explore')}>Back to the heart<ArrowRight size={15}/></button></div>
        <ModelComparison info={candidate} variant={modelVariant} busy={busy} onChange={changeModel}/>
        <Evidence evaluation={evaluation} coherence={coherence} info={info} selected={selected}/>
        <div className="reference-section"><span className="folio">EXPLORE THE SOURCE MATERIAL</span><HeldoutChallenge openRequest={challengeRequest} onInspectVessel={inspectHeldoutVessel} onLeaveReference={()=>setReferenceCase(null)}/><PublicECGReference/></div>
      </section>
      <div aria-live="polite" className="prediction-announcement">{referenceCase?'Reference anatomy only. The saved fold result is in the challenge.':busy?'Computing four predictions and model explanations…':result?`Prediction complete. CAD ${percent(result.cad.probability)}. ${result.missing_features.length} imputed observations.`:dirty?'Previous results cleared. Generate a new prediction.':''}</div>
    </>}
    {guideStep!==null&&<button className="guide-resume" onClick={returnToGuide}><BookOpen size={14}/>Guided case · step {guideStep+1}/5 ↑</button>}
    <footer className="credits"><span>Cardiofolio · Educational research</span><span>BodyParts3D · The Database Center for Life Science · CC BY 4.0</span></footer>
  </main>
  <div className="disclaimer"><ShieldCheck size={15}/><p>Educational research prototype. Not a diagnosis, measured narrowing, or a substitute for diagnostic imaging. Independent clinical validation remains outstanding.</p></div>
  </>
}
