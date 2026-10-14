// @vitest-environment jsdom
import {afterEach,expect,it,vi} from 'vitest'
import {cleanup,render,screen,fireEvent,within} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import {type Field,type Result} from './types'
import InvestigationContext from './InvestigationContext'
const fields:Field[]=JSON.parse(readFileSync(resolve(process.cwd(),'../data/processed/feature_schema.json'),'utf8'))
afterEach(cleanup)

it('shows unknown echo as a dash while retaining an actual zero ECG source code',()=>{
  const onFind=vi.fn()
  const result={input_snapshot:{'Q Wave':'0','St Depression':'1','EF-TTE':null,'Region RWMA':null,VHD:null}} as unknown as Result
  render(<InvestigationContext result={result} fields={fields} onFind={onFind}/>)
  const ef=screen.getByRole('button',{name:'Echo ejection fraction ↗'}).closest('div')!
  expect(within(ef).getByText('—')).toBeInTheDocument()
  expect(within(ef).getByText('Unknown · imputed for computation')).toBeInTheDocument()
  expect(screen.getByRole('button',{name:'Q Wave ↗'}).closest('div')).toHaveTextContent('0')
  expect(screen.getByText('0/3 supplied')).toBeInTheDocument()
  expect(screen.getByText(/do not supply a confirmed coronary diagnosis/)).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button',{name:'Echo ejection fraction ↗'}))
  expect(onFind).toHaveBeenCalledWith('EF-TTE')
})

it('shows draft investigations before prediction without pretending missing fields were imputed',()=>{
  render(<InvestigationContext features={{'EF-TTE':35,'Region RWMA':'2',VHD:null}} fields={fields} onFind={()=>{}}/>)
  expect(screen.getByText('DRAFT OBSERVATIONS · NO CURRENT PREDICTION')).toBeInTheDocument()
  expect(screen.queryByText('Unknown · imputed for computation')).not.toBeInTheDocument()
  expect(screen.getByText('2/3 supplied')).toBeInTheDocument()
  expect(screen.getByText(/Doppler blood-flow patterns, flow measurements and detailed valve narrowing or leakage findings are not captured/)).toBeInTheDocument()
  expect(screen.getByText('35 %')).toBeInTheDocument()
  expect(screen.getByText('Code 2')).toBeInTheDocument()
})
