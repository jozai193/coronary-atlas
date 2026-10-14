// @vitest-environment jsdom
import {afterEach,describe,it,expect,vi} from 'vitest'
import {render,screen,fireEvent,cleanup} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import metadata from '../../models/metadata.json'
import type {Field} from './types'
import ReportImport from './ReportImport'
import {echoSampleText} from './echoSample.fixture'
afterEach(cleanup)
describe('Assisted report import',()=>{
  it('requires separate source/case confirmation for echo excerpts and invalidates it on text edits',()=>{
    const save=vi.fn(()=>''),apply=vi.fn()
    render(<ReportImport fields={metadata.feature_schema as Field[]} features={{'EF-TTE':50}} busy={false} onApply={apply} onEchoReview={save}/>)
    fireEvent.change(screen.getByLabelText('Report text'),{target:{value:echoSampleText}})
    fireEvent.click(screen.getByRole('button',{name:'Find proposed values'}))
    expect(screen.getByRole('region',{name:'Echo text for source review'})).toHaveTextContent('mildly dilated')
    const button=screen.getByRole('button',{name:'Append reviewed echo text to current case'})
    expect(button).toBeDisabled();expect(save).not.toHaveBeenCalled();expect(apply).not.toHaveBeenCalled()
    fireEvent.click(screen.getByLabelText('Echo excerpts checked and belong to the current case'))
    fireEvent.click(button);expect(save).toHaveBeenCalledTimes(1);expect(apply).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Echo excerpts checked and belong to the current case')).not.toBeChecked()
    fireEvent.click(screen.getByLabelText('Echo excerpts checked and belong to the current case'))
    fireEvent.change(screen.getByLabelText('Report text'),{target:{value:echoSampleText+'\nEdited'}})
    expect(screen.queryByRole('button',{name:'Append reviewed echo text to current case'})).not.toBeInTheDocument()
  })
  it('requires confirmation, clears synthetic carryover by default and never predicts',()=>{
    const apply=vi.fn()
    render(<ReportImport fields={metadata.feature_schema as Field[]} features={{Age:72,LDL:155,HTN:'1'}} busy={false} onApply={apply}/>)
    fireEvent.click(screen.getByText('Import a report photo · assisted autofill'))
    fireEvent.change(screen.getByLabelText('Report text'),{target:{value:'Age: 56\nLDL 110 mg/dL\nECG normal'}})
    fireEvent.click(screen.getByRole('button',{name:'Find proposed values'}))
    expect(screen.getByRole('button',{name:'Apply 0 confirmed observations'})).toBeDisabled()
    expect(apply).not.toHaveBeenCalled()
    fireEvent.click(screen.getByLabelText('Confirm LDL'))
    fireEvent.click(screen.getByRole('button',{name:'Apply 1 confirmed observations'}))
    expect(apply.mock.calls[0][0]).toMatchObject({LDL:110,Age:null,HTN:null,'St Depression':null})
    expect(apply.mock.calls[0][1]).toEqual(['LDL'])
    expect(screen.getByLabelText('Report text')).toHaveValue('')
  })
  it('invalidates confirmation when OCR text or a proposed value changes',()=>{
    render(<ReportImport fields={metadata.feature_schema as Field[]} features={{}} busy={false} onApply={vi.fn()}/>)
    fireEvent.click(screen.getByText('Import a report photo · assisted autofill'))
    fireEvent.change(screen.getByLabelText('Report text'),{target:{value:'LDL 110 mg/dL'}})
    fireEvent.click(screen.getByRole('button',{name:'Find proposed values'}));fireEvent.click(screen.getByLabelText('Confirm LDL'))
    fireEvent.change(screen.getByLabelText('Correct LDL'),{target:{value:'120'}})
    expect(screen.getByLabelText('Confirm LDL')).not.toBeChecked()
    fireEvent.change(screen.getByLabelText('Report text'),{target:{value:'LDL 130 mg/dL'}})
    expect(screen.queryByLabelText('Confirm LDL')).not.toBeInTheDocument()
  })
})
