// @vitest-environment jsdom
import {afterEach,beforeEach,expect,it,vi} from 'vitest'
import {cleanup,render,screen,fireEvent} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import HeartViewer from './HeartViewer'
import {type Result} from './types'
import {structureColor,ARTERY_COLOR,VEIN_COLOR,HEART_COLOR,DETAIL_PARTS} from './anatomyDisplay'
vi.mock('@react-three/fiber',()=>({Canvas:()=> <div data-testid="canvas-placeholder"/>,useFrame:vi.fn(),useLoader:vi.fn(),useThree:vi.fn()}))
vi.mock('@react-three/drei',()=>({Html:()=>null,OrbitControls:()=>null}))
beforeEach(()=>{vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,json:async()=>({center:[0,0,0],scale:1,structures:{}})})))})
afterEach(()=>{cleanup();vi.unstubAllGlobals()})

it('keeps reference tissue and vessels distinct and restricts probability shading to targets',()=>{
  expect(structureColor('heart',undefined,'anatomy')).toBe(HEART_COLOR)
  expect(structureColor('cardiac_veins',undefined,'anatomy')).toBe(VEIN_COLOR)
  expect(structureColor('pulmonary_trunk',undefined,'anatomy')).toBe(VEIN_COLOR)
  expect(structureColor('aorta',undefined,'anatomy')).toBe(ARTERY_COLOR)
  expect(DETAIL_PARTS).not.toContain('pulmonary_trunk')
  expect(structureColor('lad',undefined,'anatomy')).toBe(ARTERY_COLOR)
  for(const kind of ['heart','aorta','pulmonary_trunk','coronary_sinus','cardiac_veins','valve_leaflets','papillary_muscles','context_branches','left_main']){
    expect(structureColor(kind,.1,'probability')).toBe(structureColor(kind,.9,'probability'))
    expect(structureColor(kind,.9,'probability')).toBe(structureColor(kind,undefined,'anatomy'))
  }
  expect(structureColor('lad',.1,'probability')).not.toBe(structureColor('lad',.9,'probability'))
  expect(structureColor('lad',.1,'anatomy')).toBe(structureColor('lad',.9,'anatomy'))
})

it('makes the internal view and anatomical color meaning explicit',async()=>{
  render(<HeartViewer result={null} selected="lad" onSelect={()=>{}}/>)
  fireEvent.click(screen.getByRole('button',{name:'Inside heart'}))
  expect(screen.getByText(/valve leaflets and papillary muscles/)).toBeInTheDocument()
  expect(screen.getByText(/not depict this profile’s echo findings/)).toBeInTheDocument()
  expect(screen.getByRole('button',{name:'Probability shading'})).toBeDisabled()
  expect(screen.getByRole('button',{name:'Vessels only'})).toBeInTheDocument()
  expect(screen.getByText('Oxygen-rich vessels')).toBeInTheDocument()
  expect(screen.getByText('Oxygen-poor vessels')).toBeInTheDocument()
  expect(screen.getByText(/pulmonary trunk \(pulmonary artery\), cardiac veins and coronary sinus blue/)).toBeInTheDocument()
})

it('lets anatomy colors hide probability shading while keeping the estimates available',()=>{
  const result={lad:{probability:.9},lcx:{probability:.5},rca:{probability:.1}} as Result
  render(<HeartViewer result={result} selected="lad" onSelect={()=>{}}/>)
  expect(screen.getByText(/Light-to-dark red shading/)).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button',{name:'Anatomy colors'}))
  expect(screen.queryByText(/Light-to-dark red shading/)).not.toBeInTheDocument()
  expect(screen.getByText(/No probability is mapped in anatomy-color mode/)).toBeInTheDocument()
  expect(screen.getByText('90.0%')).toBeInTheDocument()
})
