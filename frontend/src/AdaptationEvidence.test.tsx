// @vitest-environment jsdom
import {afterEach,expect,it} from 'vitest'
import {cleanup,render,screen,fireEvent,within} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import AdaptationEvidence from './AdaptationEvidence'
import summary from './generated/peerj-adaptation-summary.json'
import full from './generated/peerj-adaptation-results.json'

afterEach(cleanup)

it('keeps the derived summary tied to frozen results, including missed cases',()=>{
  const original=JSON.parse(readFileSync(resolve(process.cwd(),'../output/research/peerj_adaptation_v1/results.json'),'utf8'))
  expect(full).toEqual(original)
  for(const row of summary.rows){
    const budget=row.budget==='442–443'?'all':'64'
    const source=original.budgets[budget]
    expect(row.brier).toBe(source.mean[row.method].brier)
    expect(row.mean_within_fold_auc).toBe(source.mean[row.method].mean_within_fold_auc)
    expect(row.false_negatives).toEqual([source.repeats['1'][row.method].confusion.fn,source.repeats['2'][row.method].confusion.fn])
  }
})

it('shows the development boundary and lost detection alongside improved probability error',()=>{
  render(<AdaptationEvidence/>)
  fireEvent.click(screen.getByText('Development follow-up: can local examples improve the predictions?'))
  expect(screen.getByText(/Already inspected cohort/)).toBeInTheDocument()
  expect(screen.getByText(/not a fresh external test/)).toBeInTheDocument()
  expect(screen.getByText(/145 \/ 155 of 201/)).toBeInTheDocument()
  expect(screen.getByText(/App predictions remain unchanged/)).toBeInTheDocument()
  const row=within(screen.getByRole('row',{name:/^Sigmoid recalibration/}))
  expect(row.getByText('0.212')).toBeInTheDocument()
  expect(row.getByText('25.4%')).toBeInTheDocument()
  expect(screen.getByRole('link',{name:/Download development metrics/})).toHaveAttribute('download','peerj-adaptation-results.json')
})
