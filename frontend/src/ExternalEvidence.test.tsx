// @vitest-environment jsdom
import {afterEach,expect,it} from 'vitest'
import {cleanup,render,screen,within} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import source from './generated/angiocad-external-results.json'
import ExternalEvidence from './ExternalEvidence'

afterEach(cleanup)

it('ships the unmodified saved AngioCAD results',()=>{
  const original=JSON.parse(readFileSync(resolve(process.cwd(),'../output/research/angiocad_v1/external_results.json'),'utf8'))
  expect(source).toEqual(original)
  expect(source.not_validation_of_55_input_app).toBe(true)
})

it('separates the frozen research model from the app and displays primary misses for every target',()=>{
  render(<ExternalEvidence/>)
  expect(screen.getByText(/live 55-input app above was not externally tested here/i)).toBeInTheDocument()
  expect(screen.getByText(/13 shared clinical inputs/i)).toBeInTheDocument()
  expect(screen.getByText(/endpoint matching is imperfect/i)).toBeInTheDocument()
  const expected={
    'Overall CAD':{n:'345',auc:'0.781',detected:'93.1%',missed:'19'},
    LAD:{n:'322',auc:'0.723',detected:'74.6%',missed:'58'},
    LCX:{n:'331',auc:'0.709',detected:'40.0%',missed:'54'},
    RCA:{n:'326',auc:'0.687',detected:'31.6%',missed:'106'},
  }
  for(const [target,metrics] of Object.entries(expected)){
    const row=within(screen.getByRole('row',{name:new RegExp(`^${target} `)}))
    expect(row.getByText(metrics.n)).toBeInTheDocument()
    expect(row.getByText(metrics.auc)).toBeInTheDocument()
    expect(row.getByText(new RegExp(metrics.detected.replace('.','\\.')))).toBeInTheDocument()
    expect(row.getByText(metrics.missed)).toBeInTheDocument()
  }
  const angiocard=within(screen.getByRole('region',{name:'What happened at another center?'}))
  expect(angiocard.getByRole('link',{name:/Download full metrics/})).toHaveAttribute('download','angiocad-external-results.json')
})
