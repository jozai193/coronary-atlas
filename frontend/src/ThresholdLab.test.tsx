// @vitest-environment jsdom
import {afterEach,it,expect} from 'vitest'
import {render,screen,fireEvent,within,cleanup} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import ThresholdLab from './ThresholdLab'

afterEach(cleanup)
it('shows the missed cases and false alarms for each selected target and repeat',()=>{
  render(<ThresholdLab/>);
  const baseline=within(screen.getByRole('article',{name:'Default cutoff'}))
  const recall=within(screen.getByRole('article',{name:'Aim for 80% detection'}))
  expect(baseline.getByText('71')).toBeInTheDocument()
  expect(recall.getByText('18')).toBeInTheDocument()
  expect(recall.getByText('81')).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Compare target'),{target:{value:'rca'}})
  fireEvent.change(screen.getByLabelText('Validation run'),{target:{value:'1'}})
  expect(recall.getByText('32')).toBeInTheDocument()
  expect(recall.getByText('87')).toBeInTheDocument()
  expect(baseline.getByText('74')).toBeInTheDocument()
  expect(screen.getByText(/both runs reuse the same 303 people/)).toBeInTheDocument()
})
