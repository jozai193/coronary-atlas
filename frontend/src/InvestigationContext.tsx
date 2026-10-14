import {type Field,type Features,type Result} from './types'
import {observationText} from './observations'
import {fieldContext} from './reviewWorksheet'

export default function InvestigationContext({result,features,fields,onFind}:{result?:Result|null;features?:Features;fields:Field[];onFind:(name:string)=>void}){
  const groups=['ECG','Echocardiography']
  const snapshot=result?.input_snapshot??features??{}
  const missingReviewEcho=['EF-TTE','VHD'].filter(name=>snapshot[name]==null)
  return <section tabIndex={-1} className="investigation-context" aria-label="ECG and echo observations">
    <div><span className="eyebrow">{result?'RECORDED FINDINGS · CURRENT PREDICTION SNAPSHOT':'DRAFT OBSERVATIONS · NO CURRENT PREDICTION'}</span><h2>ECG and echo observations</h2>
      <p>{result?'These are the values supplied for the current prediction.':'These are the current draft values; review them before generating a prediction.'} The app does not read an ECG tracing or an echo image. Echo EF, RWMA and valve findings describe different observations from the CAD/artery labels; they do not supply a confirmed coronary diagnosis or a rule that overrides the model.</p>
    </div>
    <p className="investigation-note"><strong>Selected echo inputs only — not a complete echo report.</strong> Only EF, an RWMA source code and a valve category are represented. Doppler blood-flow patterns, flow measurements and detailed valve narrowing or leakage findings are not captured by these three inputs. A complete report and its images are not attached; supplying all three fields does not make this a complete echocardiographic assessment. <a href="https://www.nhlbi.nih.gov/health/heart-tests" target="_blank" rel="noreferrer">Echo and Doppler explained ↗</a></p>
    {missingReviewEcho.length>0&&<p className="investigation-note" role="status"><strong>Incomplete echo information for clinical review.</strong> {missingReviewEcho.map(name=>name==='EF-TTE'?'Echo EF':'Valve assessment').join(' and ')} not supplied. The reviewer requested both EF and valve findings. Imputation is not a measured finding and does not establish a diagnosis.</p>}
    <div className="investigation-groups">{groups.map(group=>{
      const specs=fields.filter(f=>f.group===group)
      const known=specs.filter(f=>snapshot[f.name]!=null).length
      return <section key={group}><h3>{group==='Echocardiography'?'Selected echo inputs':group}<small>{known}/{specs.length} supplied</small></h3><dl>{specs.map(f=>{
        const value=snapshot[f.name]
        return <div key={f.name}><dt><button onClick={()=>onFind(f.name)}>{f.label} ↗</button>{fieldContext(f.name)&&<small className="field-context">{fieldContext(f.name)}</small>}</dt><dd>{observationText(f,value)}{value==null&&<small>{result?'Unknown · imputed for computation':'Not supplied'}</small>}</dd></div>
      })}</dl></section>
    })}</div>
    <p className="investigation-note">A dash (—) means unknown. A supplied 0 remains a source code, not an unknown or proof that a whole test was normal. ECG findings may be inconclusive; interpretation depends on the clinical question and other evidence. <a href="https://www.nice.org.uk/guidance/CG95/chapter/recommendations" target="_blank" rel="noreferrer">Clinical context ↗</a></p>
  </section>
}
