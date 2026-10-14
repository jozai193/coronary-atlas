// @vitest-environment jsdom
import {afterEach,it,expect} from 'vitest'
import {render,screen,fireEvent,within,cleanup} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import ModalityEvidence from './ModalityEvidence'

afterEach(cleanup)
it('updates the fixed-estimator comparison for a different target and repeat',()=>{
  render(<ModalityEvidence/>);
  expect(within(screen.getByRole('row',{name:/Clinical core/})).getByText('0.783')).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Input-group target'),{target:{value:'rca'}})
  fireEvent.change(screen.getByLabelText('Input-group validation run'),{target:{value:'1'}})
  expect(within(screen.getByRole('row',{name:/Clinical core/})).getByText('0.702')).toBeInTheDocument()
  expect(screen.getByText(/not the deployed model comparison/)).toBeInTheDocument()
})
