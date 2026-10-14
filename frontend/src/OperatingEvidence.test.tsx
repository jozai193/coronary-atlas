// @vitest-environment jsdom
import {afterEach,expect,it} from 'vitest'
import {cleanup,render,screen,within} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import OperatingEvidence from './OperatingEvidence'
import summary from './generated/peerj-operating-summary.json'
import full from './generated/peerj-operating-results.json'
afterEach(cleanup)

it('keeps every displayed trade-off tied to the frozen evidence',()=>{
  const original=JSON.parse(readFileSync(resolve(process.cwd(),'../output/research/peerj_operating_v1/results.json'),'utf8'))
  expect(full).toEqual(original)
  for(const r of summary.rows){
    expect(r.sensitivity).toBe(original.mean_operating[r.method][r.point].sensitivity)
    expect(r.specificity).toBe(original.mean_operating[r.method][r.point].specificity)
    expect(r.false_negatives).toEqual([1,2].map(i=>original.repeats[i].operating[r.method][r.point].confusion.fn))
    expect(r.false_positives).toEqual([1,2].map(i=>original.repeats[i].operating[r.method][r.point].confusion.fp))
  }
})

it('shows missed cases, false alarms and the unapproved development boundary together',()=>{
  render(<OperatingEvidence/>);screen.getByText(/Detection follow-up/).closest('details')!.open=true
  expect(screen.getByText(/no reviewer guidance yet/)).toBeInTheDocument()
  expect(screen.getByText(/not fresh external validation/)).toBeInTheDocument()
  expect(screen.getByText(/No clinically preferred cutoff/)).toBeInTheDocument()
  const row=within(screen.getByRole('row',{name:/^Local \+ calibration: 90% target/}))
  expect(row.getByText('27 / 17')).toBeInTheDocument()
  expect(row.getByText('191 / 208')).toBeInTheDocument()
  expect(row.getByText('89.1%')).toBeInTheDocument()
  expect(screen.getByRole('link',{name:/Download all cutoff/})).toHaveAttribute('download','peerj-operating-results.json')
})
