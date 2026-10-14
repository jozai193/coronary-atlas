import {type Field} from './types'
export const UNKNOWN_OBSERVATION='—'
export function categoryLabel(value:string){return value==='Fmale'?'Female':value==='Y'?'Yes':value==='N'?'No / absent':/^\d+$/.test(value)?`Code ${value}`:value}
export function observationText(field:Field,value:unknown){
  if(value==null)return UNKNOWN_OBSERVATION
  if(typeof value==='number')return `${Number(value.toFixed(2))} ${field.unit}`
  return typeof value==='string'?categoryLabel(value):UNKNOWN_OBSERVATION
}
export function parseCsvObservation(field:Field,raw:string|undefined){
  const value=raw?.trim()
  if(!value||['-','–','—'].includes(value))return null
  if(field.kind==='number'){
    const number=Number(value)
    if(!Number.isFinite(number))throw new Error(`${field.label}: invalid number`)
    return number
  }
  const canonical=field.options?.find(option=>option===value||categoryLabel(option).toLowerCase()===value.toLowerCase())
  if(canonical===undefined)throw new Error(`${field.label}: unsupported category ${value}`)
  return canonical
}
