// @vitest-environment jsdom
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest'
import {cleanup,fireEvent,render,screen,within} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import HeldoutChallenge from './HeldoutChallenge'

const index={source:'UCI source cohort',source_url:'https://doi.org/10.24432/C5461K',method:'Curated quadrants',note:'Internal only',cases:[{id:'A',observations:[{label:'Age band',value:'60–69 years'}]},{id:'B',observations:[{label:'Age band',value:'50–59 years'}]}]}
let fetchMock:ReturnType<typeof vi.fn>
const inspect=vi.fn(),leaveReference=vi.fn()
beforeEach(()=>{inspect.mockClear();leaveReference.mockClear();fetchMock=vi.fn(async(url:string)=>({ok:true,json:async()=>url.endsWith('/cases')?index:{case_id:'A',target:url.split('/').at(-1),probability:.42,label:1,predicted_label:0,fold:3,note:'Saved raw nested outer-fold prediction. No SHAP or coherence adjustment.'}}));vi.stubGlobal('fetch',fetchMock)})
afterEach(()=>{cleanup();vi.unstubAllGlobals()})

describe('Held-out teaching challenge',()=>{
  it('keeps the saved truth hidden until a guess and resets it after changing cases',async()=>{
    render(<HeldoutChallenge onInspectVessel={inspect} onLeaveReference={leaveReference}/>)
    expect(fetchMock).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button',{name:/Try four cases/}))
    const challenge=within(screen.getByRole('region',{name:'Held-out case challenge'}))
    await challenge.findByText('60–69 years')
    expect(challenge.queryByText('42.0%')).not.toBeInTheDocument()
    fireEvent.click(challenge.getByRole('button',{name:'Yes'}))
    await challenge.findByText('42.0%')
    expect(challenge.getByText(/It missed this positive row/)).toBeInTheDocument()
    expect(challenge.queryByRole('button',{name:/Inspect .* on reference heart/})).not.toBeInTheDocument()
    expect(challenge.getByText(/CAD is an overall disease label/)).toBeInTheDocument()
    expect(challenge.getByText(/not a random sample or external validation/)).toBeInTheDocument()
    fireEvent.click(challenge.getByRole('button',{name:'Case B'}))
    expect(challenge.queryByText('42.0%')).not.toBeInTheDocument()
    expect(challenge.getByText('50–59 years')).toBeInTheDocument()
    expect(fetchMock.mock.calls.map(([url])=>url)).toEqual(['/api/held-out/cases','/api/held-out/cases/A/cad'])
  })
  it('links revealed vessel cases to reference anatomy and clears that context on a new case',async()=>{
    render(<HeldoutChallenge onInspectVessel={inspect} onLeaveReference={leaveReference}/>)
    fireEvent.click(screen.getByRole('button',{name:/Try four cases/}))
    const challenge=within(screen.getByRole('region',{name:'Held-out case challenge'}))
    await challenge.findByText('60–69 years')
    fireEvent.change(challenge.getByLabelText('Dataset label to guess'),{target:{value:'lad'}})
    expect(challenge.queryByRole('button',{name:/Inspect LAD on reference heart/})).not.toBeInTheDocument()
    fireEvent.click(challenge.getByRole('button',{name:'Yes'}))
    const link=await challenge.findByRole('button',{name:/Inspect LAD on reference heart/})
    fireEvent.click(link)
    expect(inspect).toHaveBeenCalledExactlyOnceWith('lad','A')
    fireEvent.click(challenge.getByRole('button',{name:'Case B'}))
    expect(leaveReference).toHaveBeenCalled()
    expect(challenge.queryByRole('button',{name:/Inspect LAD on reference heart/})).not.toBeInTheDocument()
  })
})
