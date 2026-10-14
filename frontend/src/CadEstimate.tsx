import {type Result,color,percent} from './types'

export default function CadEstimate({result,onInspectInputs}:{result:Result|null;onInspectInputs:()=>void}){
  const total=result?Object.keys(result.input_snapshot).length:0
  const missing=result?.missing_features.length??0
  return <div tabIndex={-1} className="risk-card cad-card"><span className="eyebrow">03 / DISPLAYED ESTIMATE</span><h2>Overall CAD</h2>
    <div className="cad-value" style={{color:color(result?.cad.probability)}}>{result?percent(result.cad.probability):'—'}<span>{result?`${result.cad.category} predicted probability`:'Awaiting observations'}</span></div>
    <p>{result?'Probability of the dataset’s CAD label.':'Choose A or B, or start your own case.'}</p>
    <div className="risk-meter"><span style={{left:`${(result?.cad.probability??0)*100}%`,opacity:result?1:0}}/></div><div className="meter-labels"><span>0%</span><span>100%</span></div>
    {result&&<><p className="model-classification">{result.coherence_adjustment.enabled?'Adjusted class at 0.5:':'Model class at 0.5:'} <strong>{result.cad.classification?'CAD positive':'CAD negative'}</strong></p>
      <div className="cad-input-context"><strong>Model estimate · not a diagnosis</strong><span>{total-missing} supplied · {missing} imputed</span><button onClick={onInspectInputs}>Review the inputs ↗</button></div></>}
  </div>
}
