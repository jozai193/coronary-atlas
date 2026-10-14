import {expect,it} from 'vitest'
import {type Field} from './types'
import {observationText,parseCsvObservation} from './observations'
const number:Field={name:'WBC',label:'White blood cells',group:'Laboratory',kind:'number',unit:'/µL',unit_note:'',minimum:0,maximum:100000,options:null}
const category:Field={...number,name:'St Depression',label:'ST depression',group:'ECG',kind:'category',unit:'source code',options:['0','1']}

it('keeps unknown and genuine zero distinct through display and CSV import',()=>{
  for(const value of [undefined,'',' ','-','–','—']){
    expect(parseCsvObservation(number,value)).toBeNull()
    expect(parseCsvObservation(category,value)).toBeNull()
  }
  expect(parseCsvObservation(number,'0')).toBe(0)
  expect(parseCsvObservation(category,'0')).toBe('0')
  expect(observationText(number,null)).toBe('—')
  expect(observationText(category,undefined)).toBe('—')
  expect(observationText(number,0)).toBe('0 /µL')
  expect(observationText(category,'0')).toBe('Code 0')
  expect(parseCsvObservation(category,'Code 0')).toBe('0')
  expect(parseCsvObservation(category,'Code 1')).toBe('1')
})

it('rejects invalid measurements without converting them to zero or missing',()=>{
  expect(()=>parseCsvObservation(number,'not-known')).toThrow('invalid number')
  expect(()=>parseCsvObservation(number,'Infinity')).toThrow('invalid number')
  expect(()=>parseCsvObservation(category,'normal')).toThrow('unsupported category')
})
