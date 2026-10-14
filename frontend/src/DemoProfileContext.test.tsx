// @vitest-environment jsdom
import {afterEach,expect,it,vi} from 'vitest'
import {cleanup,render,screen,fireEvent,within} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import DemoProfileContext from './DemoProfileContext'
import {type Field,type Sample} from './types'
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
const samples:Sample[]=JSON.parse(readFileSync(resolve(process.cwd(),'../data/processed/sample_patients.json'),'utf8'))
const fields:Field[]=JSON.parse(readFileSync(resolve(process.cwd(),'../data/processed/feature_schema.json'),'utf8'))
afterEach(cleanup)

it('shows valve input provenance and limits alongside a synthetic profile',()=>{
  const onFind=vi.fn()
  render(<DemoProfileContext sample={samples[1]} fields={fields} onFind={onFind}/>)
  expect(screen.getByText('Valvular disease input: — · not supplied')).toBeInTheDocument()
  expect(screen.getByText(/does not measure artery narrowing or grade valve disease/)).toBeInTheDocument()
  expect(screen.getByText(/not received clinical sign-off/)).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button',{name:/Inspect the valvular input/}))
  expect(onFind).toHaveBeenCalledWith('VHD')
})

it('exposes all 55 actual inputs with explicit, calculated and inherited origins',()=>{
  render(<DemoProfileContext sample={samples[1]} fields={fields} onFind={()=>{}}/>)
  const details=screen.getByText('Review all 55 input values and their origins').closest('details')!
  details.open=true
  expect(within(details).getAllByRole('definition')).toHaveLength(55)
  expect(screen.getByRole('button',{name:'ST depression ↗'}).closest('div')).toHaveTextContent('Code 1Example choice')
  expect(screen.getByRole('button',{name:'Valvular disease ↗'}).closest('div')).toHaveTextContent('—Not supplied')
  expect(screen.getByRole('button',{name:'BMI ↗'}).closest('div')).toHaveTextContent('Calculated from weight/height')
  expect(screen.getByRole('button',{name:'Echo ejection fraction ↗'}).closest('div')).toHaveTextContent('35 %Example choice')
})
