import {describe,it,expect} from 'vitest'
import {parseReport,applyConfirmed} from './reportParser'
import type {Field} from './types'
import metadata from '../../models/metadata.json'
import {echoSampleText} from './echoSample.fixture'
const fields=metadata.feature_schema as Field[]
describe('Report extraction safeguards',()=>{
  it('keeps the template EF blocked for column review and never fills blank measurements from normal ranges',()=>{
    const sample=parseReport(echoSampleText,fields)
    // Pipes are preserved delimiters: the parser must not guess column layout.
    expect(sample).toHaveLength(1)
    expect(sample[0]).toMatchObject({field:'EF-TTE',value:null,confirmed:false})
    expect(sample[0].issue).not.toBe('')
    const flattened=parseReport(echoSampleText.replaceAll(' | ',' '),fields)
    expect(flattened).toHaveLength(1)
    expect(flattened[0]).toMatchObject({field:'EF-TTE',value:55,confirmed:false})
    expect(flattened[0].issue).toMatch(/reference-range table/)
    expect(applyConfirmed(flattened.map(c=>({...c,confirmed:true})),fields,{},'replace').imported).toEqual([])
    expect(parseReport('LVEF (est) 55% >50%',fields)[0]).toMatchObject({value:55,issue:'',confirmed:false})
    for(const line of ['LVEF (est) >50%','LVEF (est) 50-70%','LVEF (est) a%','LVEF (est) %'])expect(parseReport(line,fields)[0].issue).not.toBe('')
  })
  it('ignores repeated test headings and commentary without discarding genuine conflicting results',()=>{
    expect(parseReport('Hemoglobin\nHemoglobin 13.5 g/dL 11.1-15.9',fields).map(c=>[c.field,c.value,c.issue])).toEqual([['HB',13.5,'']])
    expect(parseReport('Potassium 3.8 mmol/L 3.5-5.2\nPotassium is within goal, 3.8 mmol/L.',fields).map(c=>[c.field,c.value,c.issue])).toEqual([['K',3.8,'']])
    expect(parseReport('Hemoglobin A1c 6.1 %\nHbA1c 6.1 %',fields)).toEqual([])
    expect(parseReport('Hemoglobin 13.5 g/dL\nHemoglobin 10.5 g/dL',fields)[0].issue).toMatch(/Conflicting/)
  })
  it('separates lab site footnotes, current results and reference intervals',()=>{
    const rows=parseReport('Triglycerides 01 175 High mg/dL 0-149\nHDL Cholesterol 01 45 mg/dL >39\nLDL Chol Calc (NIH) 213 High mg/dL 0-99\nVLDL Cholesterol Cal 33 mg/dL 5-40\nNon-HDL Cholesterol 246 mg/dL 0-129',fields)
    expect(rows.map(c=>[c.field,c.value,c.issue])).toEqual([['TG',175,''],['HDL',45,''],['LDL',213,'']])
    expect(rows.every(c=>!c.confirmed)).toBe(true)
  })
  it('does not choose a reference range, previous value, comparator, or uncertain decimal',()=>{
    for(const line of ['LDL: 90 110 mg/dL','LDL <40 mg/dL','LDL 100-129 mg/dL','LDL 1,10 mg/dL','LDL 1O0 mg/dL'])expect(parseReport(line,fields)[0].issue).not.toBe('')
    expect(parseReport('Reference LDL 100 mg/dL\nLDL-P 1400 nmol/L\nVLDL 33 mg/dL',fields)).toEqual([])
    expect(parseReport('LDL 2.5 mmol/L',fields)[0].value).toBeNull()
  })
  it('handles observed warning icons and footnote glyphs without consuming comments',()=>{
    const rows=parseReport('A Triglycerides 175 High mg/dL 0-149\nHDL Cholesterol ®* 45 mg/dL >39\nA LDL Chol Calc (NIH) 213 High mg/dL 0-99\nLDL Calc Comment:\nA Non-HDL Cholesterol 246 High mg/dL 0-129',fields)
    expect(rows.map(c=>[c.field,c.value,c.issue])).toEqual([['TG',175,''],['HDL',45,''],['LDL',213,'']])
  })
  it('does not infer fasting, ECG codes, targets or valve grades',()=>{
    expect(parseReport('Glucose 120 mg/dL\nRandom glucose 140 mg/dL\nECG normal\nCAD 99%\nLAD 85%\nVHD mild',fields)).toEqual([])
    expect(parseReport('LVEF: 55 %',fields).map(c=>c.field)).toEqual(['EF-TTE'])
  })
  it('blocks conflicting repeated results and out-of-support measurements',()=>{
    expect(parseReport('LDL 110 mg/dL\nLDL 130 mg/dL',fields)[0].issue).toMatch(/Conflicting/)
    expect(parseReport('Age: 22\nLDL 900 mg/dL',fields).every(c=>!!c.issue)).toBe(true)
    expect(parseReport('Age: 56\nAge: 56',fields)).toHaveLength(1)
  })
  it('requires confirmation, starts with unknowns, and clears stale BMI on component changes',()=>{
    const c=parseReport('Age: 56\nLDL 110 mg/dL\nHeight 174 cm',fields)
    expect(applyConfirmed(c,fields,{LDL:130,HTN:'1'},'replace').imported).toEqual([])
    c[1].confirmed=true;c[2].confirmed=true
    const fresh=applyConfirmed(c,fields,{LDL:130,HTN:'1'},'replace')
    expect(fresh.features).toMatchObject({LDL:110,HTN:null,Age:null,BMI:null,Length:174})
    expect(applyConfirmed(c,fields,{LDL:130,HTN:'1',BMI:30},'merge').features).toMatchObject({LDL:110,HTN:'1',BMI:null})
  })
})
