// @vitest-environment jsdom
import {expect,it} from 'vitest'
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import {type Field,type Result,type Sample} from './types'
import {buildReviewWorksheet} from './reviewWorksheet'
const fields:Field[]=JSON.parse(readFileSync(resolve(process.cwd(),'../data/processed/feature_schema.json'),'utf8'))
const sample:Sample=JSON.parse(readFileSync(resolve(process.cwd(),'../data/processed/sample_patients.json'),'utf8'))[1]

it('exports every draft input and origin without manufacturing a report or diagnosis',()=>{
  const html=buildReviewWorksheet({profile:sample.name,fields,features:sample.features,result:null,sample})
  const doc=new DOMParser().parseFromString(html,'text/html')
  expect(doc.querySelectorAll('tbody tr')).toHaveLength(55)
  expect(doc.body.textContent).toContain('49/55 entered values; 6 unknown')
  expect(doc.body.textContent).toContain('No current prediction')
  expect(doc.body.textContent).toContain('No original ECG tracing, echo image or angiography report is attached')
  expect(doc.querySelectorAll('script,img,iframe')).toHaveLength(0)
  const valve=Array.from(doc.querySelectorAll('tbody tr')).find(r=>r.querySelector('th')?.textContent==='Valvular disease')!
  expect(valve.querySelector('td')?.textContent).toBe('—')
  expect(valve.textContent).toContain('Not supplied')
  expect(doc.body.textContent).not.toContain('Displayed probability')
  const bmi=Array.from(doc.querySelectorAll('tbody tr')).find(r=>r.querySelector('th')?.textContent==='BMI')!
  expect(bmi.querySelector('td')?.textContent).toBe(`${sample.features.BMI} kg/m²`)
})

it('uses the exact completed snapshot and keeps raw/displayed outputs separate',()=>{
  const pred={probability:.99,model_probability:.98}
  const result={cad:pred,lad:pred,lcx:pred,rca:pred,model_version:'test',missing_features:sample.provenance!.unknown_fields,
    input_snapshot:{...sample.features,'EF-TTE':35}} as unknown as Result
  const html=buildReviewWorksheet({profile:sample.name,fields,features:{...sample.features,'EF-TTE':60},result,sample})
  const doc=new DOMParser().parseFromString(html,'text/html')
  const ef=Array.from(doc.querySelectorAll('tbody tr')).find(r=>r.querySelector('th')?.textContent==='Echo ejection fraction')!
  expect(ef.querySelector('td')?.textContent).toBe('35 %')
  expect(doc.body.textContent).toContain('99.0%')
  expect(doc.body.textContent).toContain('98.0%')
  expect(doc.body.textContent).toContain('6 missing inputs')
})

it('escapes all user-visible content and clears original-case provenance after editing',()=>{
  const html=buildReviewWorksheet({profile:'<img src=x onerror=alert(1)>',fields,features:{...sample.features,VHD:'Severe'},result:null})
  const doc=new DOMParser().parseFromString(html,'text/html')
  expect(doc.querySelectorAll('img,script')).toHaveLength(0)
  expect(doc.body.textContent).toContain('<img src=x onerror=alert(1)>')
  expect(doc.body.textContent).toContain('Current entered/edited observations')
  expect(doc.body.textContent).not.toContain('Example choice')
  expect(doc.body.textContent).toContain('No current prediction')
})
