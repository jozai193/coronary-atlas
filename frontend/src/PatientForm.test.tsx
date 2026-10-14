// @vitest-environment jsdom
import {useState} from 'react'
import {afterEach,expect,it,vi} from 'vitest'
import {cleanup,fireEvent,render,screen} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import PatientForm from './PatientForm'
import {type Features,type Field} from './types'

afterEach(cleanup)

const special:Field[]=[
  {name:'Age',label:'Age',group:'Demographics',kind:'number',unit:'years',unit_note:'',minimum:30,maximum:86,options:null},
  {name:'Weight',label:'Weight',group:'Demographics',kind:'number',unit:'kg',unit_note:'',minimum:48,maximum:120,options:null},
  {name:'Length',label:'Height',group:'Demographics',kind:'number',unit:'cm',unit_note:'',minimum:140,maximum:188,options:null},
  {name:'BMI',label:'BMI',group:'Demographics',kind:'number',unit:'kg/m²',unit_note:'',minimum:62/(1.85**2),maximum:40.9,options:null},
]
const fields:Field[]=[...special,...Array.from({length:51},(_,i)=>({name:`field${i}`,label:`Field ${i}`,group:'Demographics',kind:'number' as const,unit:'test',unit_note:'',minimum:0,maximum:100,options:null}))]
const initial:Features=Object.fromEntries(fields.map(f=>[f.name,40]))
Object.assign(initial,{Age:42,Weight:74,Length:165,BMI:74/(1.65**2),'EF-TTE':55,VHD:'N',...Object.fromEntries(['Q Wave','St Elevation','St Depression','Tinversion','LVH','Poor R Progression','BBB'].map(n=>[n,'0']))})

function renderForm(onPredict=vi.fn(),formFields=fields,start=initial){
  function Harness(){
    const [features,setFeatures]=useState<Features>({...start})
    return <PatientForm fields={formFields} features={features} samples={[]} busy={false} onChange={setFeatures} onSample={()=>{}} onPredict={onPredict}/>
  }
  render(<Harness/>)
  return onPredict
}

it('blocks contradictory BMI and numeric extrapolation before submission',()=>{
  const predict=renderForm()
  fireEvent.change(screen.getByLabelText('Weight'),{target:{value:'100'}})
  expect(screen.getByText(/BMI does not match weight and height/)).toBeInTheDocument()
  expect(screen.getByRole('button',{name:'Generate prediction'})).toBeDisabled()
  fireEvent.change(screen.getByLabelText('BMI'),{target:{value:String(100/(1.65**2))}})
  expect(screen.getByRole('button',{name:'Generate prediction'})).toBeEnabled()
  fireEvent.change(screen.getByLabelText('Age'),{target:{value:'90'}})
  expect(screen.getByText(/Age is outside this model’s observed range/)).toBeInTheDocument()
  expect(screen.getByRole('button',{name:'Generate prediction'})).toBeDisabled()
  fireEvent.change(screen.getByLabelText('Age'),{target:{value:'42'}})
  fireEvent.click(screen.getByRole('button',{name:'Generate prediction'}))
  expect(predict).toHaveBeenCalledOnce()
})

it('counts BMI derived from weight and height as an available model input',()=>{
  renderForm()
  fireEvent.change(screen.getByLabelText('BMI'),{target:{value:''}})
  expect(screen.getByLabelText('BMI')).toHaveAttribute('placeholder','Calculated: 27.2')
  expect(screen.getByText(/54 supplied · BMI calculated · 0 will be imputed/)).toBeInTheDocument()
  expect(screen.getByRole('button',{name:'Generate prediction'})).toBeEnabled()
})

it('accepts one-decimal BMI rounding at the observed minimum',()=>{
  renderForm()
  fireEvent.change(screen.getByLabelText('Weight'),{target:{value:'62'}})
  fireEvent.change(screen.getByLabelText('Height'),{target:{value:'185'}})
  fireEvent.change(screen.getByLabelText('BMI'),{target:{value:'18.1'}})
  expect(screen.getByRole('button',{name:'Generate prediction'})).toBeEnabled()
})

it('displays an unknown numeric value as a dash and clearing never inserts zero',()=>{
  renderForm()
  fireEvent.change(screen.getByLabelText('Age'),{target:{value:''}})
  expect(screen.getByLabelText('Age')).toHaveValue(null)
  expect(screen.getByLabelText('Age')).toHaveAttribute('placeholder','—')
  expect(screen.getByRole('button',{name:'Generate prediction'})).toBeDisabled()
  expect(screen.getByText(/0 is a supplied value or source code/)).toBeInTheDocument()
})

it('warns before prediction only when a complete lab or echo group is absent',()=>{
  const grouped=fields.map(f=>({
    ...f,
    group:f.name==='field0'||f.name==='field2'?'Laboratory':f.name==='field1'?'Echocardiography':f.group,
  }))
  const start={...initial,field0:null,field1:null,field2:null}
  renderForm(vi.fn(),grouped,start)
  expect(screen.getByRole('button',{name:'Generate prediction'})).toBeEnabled()
  expect(screen.getByText(/All laboratory observations are missing/)).toHaveTextContent(/post-hoc internal test.*naturally incomplete records/)
  expect(screen.getByText(/All echocardiography observations are missing/)).toHaveTextContent(/LAD raw estimates/)

  fireEvent.change(screen.getByLabelText('Search observations'),{target:{value:'Field 0'}})
  fireEvent.change(screen.getByLabelText('Field 0'),{target:{value:'40'}})
  expect(screen.queryByText(/All laboratory observations are missing/)).not.toBeInTheDocument()
  expect(screen.getByText(/All echocardiography observations are missing/)).toBeInTheDocument()

  fireEvent.change(screen.getByLabelText('Search observations'),{target:{value:'Field 1'}})
  fireEvent.change(screen.getByLabelText('Field 1'),{target:{value:'40'}})
  expect(screen.queryByText(/All echocardiography observations are missing/)).not.toBeInTheDocument()
  fireEvent.click(screen.getByRole('button',{name:'Clear'}))
  expect(screen.queryByText(/observations are missing/)).not.toBeInTheDocument()
})
