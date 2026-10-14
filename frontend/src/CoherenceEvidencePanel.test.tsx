// @vitest-environment jsdom
import {it,expect} from 'vitest'
import {render,screen,within} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import CoherenceEvidencePanel from './CoherenceEvidencePanel'
import {type CoherenceEvidence} from './types'

it('keeps paired shared-fold adjustment evidence separate from raw baseline metrics',()=>{
  const evidence:CoherenceEvidence={scope:'paired shared-fold',rows:303,method:'euclidean_projection',screen_passed:true,mean_four_target_brier_delta:-.001,repeats:[{repeat:1,raw_mean_four_target_brier:.1712,adjusted_mean_four_target_brier:.1702,adjusted_rows:19,discordant_rows_raw:19,discordant_rows_adjusted:0}],note:'Internal comparison only.'}
  render(<CoherenceEvidencePanel evidence={evidence}/>)
  const section=within(screen.getByRole('region',{name:'Separate coherence adjustment study'}))
  expect(section.getByText('0.1712')).toBeInTheDocument()
  expect(section.getByText('0.1702')).toBeInTheDocument()
  expect(section.getByText('19 → 0')).toBeInTheDocument()
  expect(section.getByText(/distinct from the target-specific raw-model validation/)).toBeInTheDocument()
  expect(section.getByText(/does not establish a gain for every target/)).toBeInTheDocument()
})
