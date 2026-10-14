// @vitest-environment jsdom
import {afterEach,expect,it,vi} from 'vitest'
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import PublicECGReference from './PublicECGReference'
const source={source:'https://physionet.org/content/ptb-xl/1.0.3/',version:'1.0.3',license:'CC BY 4.0',citation:'Source citation',selection:'Deterministic source selection',signal_display:'Calibrated source voltage',cases:[{ecg_id:32,provider_fold:1,age:65,age_note:'Reported age at ECG',sex_source_code:0,report:'<script>source text</script>',validated_by_human:true,waveform:'/reference-ecg/ptbxl-00032.svg',source_header:'source',source_signal:'source',statements:[{code:'NORM',description:'Source description',source_likelihood:0}]},{ecg_id:8,provider_fold:9,age:null,age_note:'Age withheld or privacy protected',sex_source_code:1,report:'Second unchanged source report',validated_by_human:false,waveform:'/reference-ecg/ptbxl-00008.svg',source_header:'source',source_signal:'source',statements:[]}]}
afterEach(()=>{cleanup();vi.unstubAllGlobals()})
function open(){const details=screen.getByText(/Explore real public ECG references/).closest('details')!;details.open=true;fireEvent(details,new Event('toggle',{bubbles:true}))}
it('loads lazily, preserves source text and unknowns, and never requests a prediction',async()=>{
  const fetch=vi.fn(async(_url:string,_options?:RequestInit)=>({ok:true,json:async()=>source}));vi.stubGlobal('fetch',fetch)
  const rendered=render(<PublicECGReference/>);expect(fetch).not.toHaveBeenCalled()
  open();await screen.findByLabelText('Choose a public ECG record')
  expect(screen.getByText('<script>source text</script>')).toBeInTheDocument()
  expect(rendered.container.querySelector('script')).toBeNull()
  expect(screen.getByText('Unknown (source code 0)')).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Choose a public ECG record'),{target:{value:'8'}})
  expect(screen.getByText('Second unchanged source report')).toBeInTheDocument()
  expect(screen.getByText(/Age withheld or privacy protected/)).toHaveTextContent('—')
  expect(screen.getByRole('img')).toHaveAttribute('src','/reference-ecg/ptbxl-00008.svg')
  expect(fetch).toHaveBeenCalledTimes(1)
  expect(fetch.mock.calls[0][0]).toBe('/reference-ecg/index.json')
})
it('reports an unavailable library and retries without touching inference',async()=>{
  const fetch=vi.fn().mockResolvedValueOnce({ok:false}).mockResolvedValueOnce({ok:true,json:async()=>source});vi.stubGlobal('fetch',fetch)
  render(<PublicECGReference/>);open()
  await screen.findByRole('alert');fireEvent.click(screen.getByRole('button',{name:'Retry ECG library'}))
  await screen.findByLabelText('Choose a public ECG record')
  await waitFor(()=>expect(fetch).toHaveBeenCalledTimes(2))
  expect(screen.queryByRole('alert')).not.toBeInTheDocument()
})
