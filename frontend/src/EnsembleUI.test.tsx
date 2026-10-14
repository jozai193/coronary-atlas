// @vitest-environment jsdom
import {afterEach,it,expect,vi} from 'vitest'
import {render,screen,fireEvent,cleanup} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import ModelComparison from './ModelComparison'
import ExplanationPanel from './ExplanationPanel'
import {type CandidateInfo,type Result,type Target} from './types'

afterEach(cleanup)
const metric={accuracy:.7,precision:.6,recall:.4,f1:.5,roc_auc:.73,specificity:.8,brier:.2,confusion_matrix:[[80,20],[60,40]]}
const targets=Object.fromEntries(['cad','lad','lcx','rca'].map(t=>[t,{baseline:metric,candidate:{...metric,accuracy:.75}}])) as Record<Target,{baseline:typeof metric;candidate:typeof metric}>
const info:CandidateInfo={available:false,candidate_id:'histgb_lcx_v2',ensemble:{available:true,candidate_id:'calibrated_ensemble_v1',note:'Repeated internal development; no independent clinical validation.',runs:[{repeat:1,targets},{repeat:2,targets},{repeat:3,targets}]}}

it('exposes an installed ensemble even when LCX candidate is absent and labels matched evidence',()=>{
  const change=vi.fn()
  render(<ModelComparison info={info} variant="calibrated_ensemble_v1" busy={false} onChange={change}/>)
  expect(screen.getByRole('option',{name:'Research calibrated ensemble · adjusted display'})).toBeInTheDocument()
  expect(screen.getAllByRole('row')).toHaveLength(7)
  expect(screen.getByText(/both coherence-adjusted/)).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Compare target'),{target:{value:'rca'}})
  expect(screen.getByText(/RCA · matched held-out rows/)).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Choose prediction model'),{target:{value:'baseline'}})
  expect(change).toHaveBeenCalledWith('baseline')
})

it('does not label ensemble permutation attributions as exact SHAP',()=>{
  const p={probability:.4,model_probability:.3,classification:0,category:'Intermediate',model:'calibrated_ensemble_v1',explanation:{method:'Sampled permutation attribution',unit:'probability',base_value:.2,output_value:.3,additivity_error:0,factors:[{feature:'Age',contribution:.1}],note:'Approximate allocation; exact reconstruction.'}}
  const result={cad:p,lad:p,lcx:p,rca:p,input_snapshot:{Age:50},model_version:'1.0.0+calibrated-ensemble-v1'} as unknown as Result
  render(<ExplanationPanel result={result} selected="cad" onSelect={vi.fn()} fields={[{name:'Age',label:'Age',kind:'number',group:'Demographics',unit:'years',unit_note:'',minimum:30,maximum:86,options:null}]}/>)
  expect(screen.getByText('Sampled permutation attribution')).toBeInTheDocument()
  expect(screen.getByLabelText('CAD Sampled permutation attribution contributions')).toBeInTheDocument()
  expect(screen.queryByText('SHAP')).not.toBeInTheDocument()
  expect(screen.getByText(/Approximate allocation/)).toBeInTheDocument()
})
