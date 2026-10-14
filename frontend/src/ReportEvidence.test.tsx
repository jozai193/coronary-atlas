// @vitest-environment jsdom
import {useState} from 'react'
import {afterEach,expect,it,vi} from 'vitest'
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import metadata from '../../models/metadata.json'
import type {Field} from './types'
import ReportEvidence from './ReportEvidence'
import {emptyReportEvidence,evidencePercent,echoInputDifference,reportFileIssue,serializeReportEvidence} from './evidenceRecord'
import {buildReviewWorksheet} from './reviewWorksheet'
const fields=metadata.feature_schema as Field[]
afterEach(()=>{cleanup();vi.unstubAllGlobals()})

it('retains unknowns and blocks ranges, implausible percentages and unsupported attachments',()=>{
  expect(evidencePercent('')).toEqual({value:null,issue:''})
  expect(evidencePercent('0')).toEqual({value:0,issue:''})
  expect(evidencePercent('100').value).toBe(100)
  for(const raw of ['-1','101','70-80','>50','1e2','NaN'])expect(evidencePercent(raw).issue).not.toBe('')
  expect(reportFileIssue({type:'image/svg+xml',size:100})).not.toBe('')
  expect(reportFileIssue({type:'application/pdf',size:0})).not.toBe('')
  expect(reportFileIssue({type:'application/pdf',size:11*1024*1024})).not.toBe('')
  expect(reportFileIssue({type:'application/pdf',size:100})).toBe('')
})

it('requires source and a user check before reconciling EF and invalidates the check on edits',()=>{
  const useEf=vi.fn()
  function Harness(){const [evidence,setEvidence]=useState(emptyReportEvidence);return <ReportEvidence evidence={evidence} fields={fields} features={{'EF-TTE':50}} onChange={setEvidence} onUseEchoEf={useEf}/>}
  render(<Harness/>);fireEvent.click(screen.getByText('Review reports, flow findings and reported narrowing'))
  fireEvent.change(screen.getByLabelText('Reported echo EF (%)'),{target:{value:'55'}})
  expect(screen.getByRole('button',{name:'Use checked report EF as model input'})).toBeDisabled()
  fireEvent.change(screen.getByLabelText('Echo / Doppler source reference'),{target:{value:'De-identified report reference'}})
  fireEvent.click(screen.getByLabelText('Report entries checked against sources for this case'))
  expect(screen.getByText(/checked report EF is 55%; the model input EF is 50%/)).toBeInTheDocument()
  expect(useEf).not.toHaveBeenCalled()
  fireEvent.click(screen.getByRole('button',{name:'Use checked report EF as model input'}))
  expect(useEf).toHaveBeenCalledWith(55)
  fireEvent.change(screen.getByLabelText('Reported echo EF (%)'),{target:{value:'56'}})
  expect(screen.getByLabelText('Report entries checked against sources for this case')).not.toBeChecked()
  expect(screen.getByRole('button',{name:'Use checked report EF as model input'})).toBeDisabled()
  fireEvent.change(screen.getByLabelText('Reported echo EF (%)'),{target:{value:'100'}})
  fireEvent.click(screen.getByLabelText('Report entries checked against sources for this case'))
  expect(screen.getByRole('button',{name:'Use checked report EF as model input'})).toBeDisabled()
})

it('keeps files in memory and exports escaped metadata, never attachment contents or model targets',async()=>{
  vi.stubGlobal('crypto',{subtle:{digest:vi.fn(async()=>new Uint8Array(32).fill(1).buffer)}})
  const create=vi.fn(()=> 'blob:local-test'),revoke=vi.fn()
  vi.stubGlobal('URL',Object.assign(URL,{createObjectURL:create,revokeObjectURL:revoke}))
  let latest=emptyReportEvidence()
  function Harness(){const [evidence,setEvidence]=useState(emptyReportEvidence);latest=evidence;return <ReportEvidence evidence={evidence} fields={fields} features={{}} onChange={setEvidence}/>}
  const mounted=render(<Harness/>);fireEvent.click(screen.getByText('Review reports, flow findings and reported narrowing'))
  const file=new File(['private-report-bytes'],'deidentified.pdf',{type:'application/pdf'})
  Object.defineProperty(file,'arrayBuffer',{value:async()=>new Uint8Array([1,2,3]).buffer})
  fireEvent.change(screen.getByLabelText('Attach ECG report'),{target:{files:[file]}})
  await waitFor(()=>expect(latest.reports.ecg.sha256).toHaveLength(64))
  fireEvent.change(screen.getByLabelText('ECG recorded findings'),{target:{value:'<script>untrusted</script>'}})
  fireEvent.change(screen.getByLabelText('LAD reported narrowing (%)'),{target:{value:'70'}})
  const serialized=serializeReportEvidence(latest)
  expect(serialized.used_by_model).toBe(false)
  expect(serialized.attachment_contents_included).toBe(false)
  expect(JSON.stringify(serialized)).not.toContain('private-report-bytes')
  expect(serialized.reported_narrowing.lad.value).toBe(70)
  const html=buildReviewWorksheet({profile:'Test',fields,features:{},result:null,reportEvidence:latest})
  const doc=new DOMParser().parseFromString(html,'text/html')
  expect(doc.querySelectorAll('script')).toHaveLength(0)
  expect(doc.body.textContent).toContain('<script>untrusted</script>')
  expect(doc.body.textContent).toContain('File contents are not included')
  mounted.unmount();expect(revoke).toHaveBeenCalledWith('blob:local-test')
})

it('never treats a missing source or unconfirmed report value as a contradiction',()=>{
  const evidence=emptyReportEvidence();evidence.echoEf='55';evidence.checked=true
  expect(echoInputDifference(evidence,{'EF-TTE':50})).toBe('')
  evidence.reports.echo.reference='Source reference';evidence.checked=false
  expect(echoInputDifference(evidence,{'EF-TTE':50})).toBe('')
  evidence.checked=true
  expect(echoInputDifference(evidence,{'EF-TTE':55})).toBe('')
  expect(echoInputDifference(evidence,{'EF-TTE':null})).toMatch(/no model EF/)
})
