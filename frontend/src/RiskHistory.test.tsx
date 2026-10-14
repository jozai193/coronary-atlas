// @vitest-environment jsdom
import {useState} from 'react'
import {afterEach,it,expect,vi} from 'vitest'
import {render,screen,fireEvent,cleanup} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import metadata from '../../models/metadata.json'
import profiles from '../../data/processed/reviewer_samples_v2.json'
import type {Field} from './types'
import RiskHistory from './RiskHistory'
import {emptyClinicalContext,contextText,parseContextNumber} from './clinicalContext'
import {buildReviewWorksheet} from './reviewWorksheet'
const fields=metadata.feature_schema as Field[]
const sample={...profiles[0],features:{...profiles[0].features,LDL:155,HDL:30,TG:250}}
afterEach(cleanup)
it('shows existing model lipid/smoking fields and keeps new context initially unknown',()=>{
  const find=vi.fn()
  render(<RiskHistory fields={fields} features={sample.features} context={emptyClinicalContext()} onFind={find}/>)
  expect(screen.getByText('155 mg/dL')).toBeInTheDocument()
  expect(screen.getByText('30 mg/dL')).toBeInTheDocument()
  expect(screen.getByText('250 mg/dL')).toBeInTheDocument()
  expect(screen.getAllByText('—')).toHaveLength(8)
  fireEvent.click(screen.getByRole('button',{name:'Edit LDL cholesterol'}))
  expect(find).toHaveBeenCalledWith('LDL')
})
it('records reported context without rewriting any modeled observations',()=>{
  const original={...sample.features};const seen=vi.fn()
  function Harness(){const [context,setContext]=useState(emptyClinicalContext);return <RiskHistory fields={fields} features={sample.features} context={context} onChange={c=>{setContext(c);seen(c)}}/>}
  render(<Harness/>);
  fireEvent.change(screen.getByLabelText('Alcohol use history'),{target:{value:'current'}})
  fireEvent.change(screen.getByLabelText('Alcohol type, amount and frequency'),{target:{value:'Pattern supplied for review'}})
  fireEvent.change(screen.getByLabelText('Total cholesterol'),{target:{value:'220'}})
  expect(seen.mock.calls.at(-1)![0]).toMatchObject({alcohol_status:'current',alcohol_pattern:'Pattern supplied for review',total_cholesterol_mg_dl:220})
  expect(sample.features).toEqual(original)
})
it('exports escaped context separately from the 55 model inputs',()=>{
  const context={...emptyClinicalContext(),alcohol_status:'current' as const,alcohol_pattern:'<script>alert("x")</script>',total_cholesterol_mg_dl:220}
  const html=buildReviewWorksheet({profile:sample.name,fields,features:sample.features,result:null,clinicalContext:context})
  const doc=new DOMParser().parseFromString(html,'text/html')
  expect(doc.querySelectorAll('script')).toHaveLength(0)
  expect(doc.body.textContent).toContain(context.alcohol_pattern)
  expect(doc.body.textContent).toContain('Additional clinical context — not model inputs')
  expect(doc.body.textContent).toContain('220 mg/dL')
  expect(doc.body.textContent).toContain('55/55 entered values')
  expect(contextText(emptyClinicalContext(),'total_cholesterol_mg_dl')).toBe('—')
  expect(parseContextNumber('')).toBeNull()
  expect(parseContextNumber('-1')).toBeNull()
  expect(parseContextNumber('0')).toBe(0)
})
