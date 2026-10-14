// @vitest-environment jsdom
import {afterEach,describe,it,expect,vi} from 'vitest'
import {render,screen,cleanup,within} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import CaseSummary from './CaseSummary'
import metadata from '../../models/metadata.json'
import type {Field,Result} from './types'
afterEach(cleanup)
describe('Case summary',()=>{
  it('shows unknown ECG/echo values without inventing a result or a whole-test interpretation',()=>{
    vi.stubGlobal('scrollTo',vi.fn())
    render(<CaseSummary profile="New case" fields={metadata.feature_schema as Field[]} features={{Age:56,'EF-TTE':55}} result={null} onBack={vi.fn()}/>)
    expect(screen.getByText(/No current prediction/)).toBeInTheDocument()
    expect(screen.getAllByText('—').length).toBeGreaterThan(7)
    const echo=screen.getByRole('heading',{name:'ECG and echo findings'}).closest('section')!
    expect(within(echo).getByText('55 %')).toBeInTheDocument()
    expect(echo).toHaveTextContent('valve')
    expect(screen.queryByText('99.0%')).not.toBeInTheDocument()
  })
  it('uses the completed snapshot and discloses raw versus adjusted probabilities',()=>{
    const p={probability:.6,model_probability:.5,explanation:{factors:[]}}
    const result={cad:p,lad:p,lcx:p,rca:p,input_snapshot:{Age:64,LDL:130},warnings:[],coherence_adjustment:{note:'Separate projection'},model_version:'test'} as unknown as Result
    render(<CaseSummary profile="Report observations" fields={metadata.feature_schema as Field[]} features={{Age:56,LDL:110}} result={result} imported={['LDL']} onBack={vi.fn()}/>)
    expect(screen.getAllByText('64 years')).toHaveLength(2)
    expect(screen.getAllByText('60.0%')).toHaveLength(4)
    expect(screen.getAllByText('Raw model: 50.0%')).toHaveLength(4)
    expect(screen.getAllByText('Report extraction confirmed by user')).toHaveLength(2)
  })
})
