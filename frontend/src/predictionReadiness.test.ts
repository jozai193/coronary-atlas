import {it,expect} from 'vitest'
import metadata from '../../models/metadata.json'
import type {Field} from './types'
import {completenessIssue} from './predictionReadiness'
import profiles from '../../data/processed/reviewer_samples_v2.json'
const fields=metadata.feature_schema as Field[]
it('requires the critical echo findings independently of a high completion count',()=>{
  for(const sample of profiles){expect(completenessIssue(sample.features,fields)).toBe('');expect(completenessIssue({...sample.features,VHD:null},fields)).toMatch(/valve assessment/)}
  expect(completenessIssue({...profiles[0].features,'EF-TTE':null},fields)).toMatch(/echo EF/)
  expect(completenessIssue({Age:53,'EF-TTE':50,VHD:'N'},fields)).toMatch(/Add 25 more/)
})
