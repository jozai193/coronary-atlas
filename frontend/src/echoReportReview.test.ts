import {expect,it} from 'vitest'
import {reviewEchoText} from './echoReportReview'
import {appendEchoReview,emptyReportEvidence,serializeReportEvidence} from './evidenceRecord'
import {echoSampleText} from './echoSample.fixture'

it('preserves the template narrative and impression without converting them into diagnoses or measurements',()=>{
  const review=reviewEchoText(echoSampleText)
  expect(review.structure).toContain('Aortic root is mildly dilated')
  expect(review.impression).toContain('Normal echocardiogram, with normal contractility and valve function')
  expect(review.valves.join('\n')).toContain('No vegetations are seen')
  expect(review.flow.join('\n')).toContain('___ m/sec')
  expect(review.warnings.join(' ')).toMatch(/NORMAL\/NORMALS/)
  expect(review.warnings.join(' ')).toMatch(/Preserve both statements/)
  expect(reviewEchoText('LDL 110 mg/dL').structure).toEqual([])
})
it('does not infer a discrepancy from a negated finding',()=>{
  const review=reviewEchoText('Echocardiogram\nAortic valve without stenosis\nIMPRESSION:\nNormal echocardiogram')
  expect(review.warnings.join(' ')).not.toMatch(/normal echo impression appears alongside/)
})
it('appends source text without overwriting evidence or setting EF, narrowing, source identity or verification',()=>{
  const evidence=emptyReportEvidence();evidence.echoEf='60';evidence.echoValves='Existing manual note';evidence.checked=true;evidence.narrowing.lad='70'
  const saved=appendEchoReview(evidence,reviewEchoText(echoSampleText))
  expect(saved.issue).toBe('')
  expect(saved.evidence).toMatchObject({echoEf:'60',checked:false,narrowing:{lad:'70'},reports:{echo:{reference:'',file:null}}})
  expect(saved.evidence.echoValves).toMatch(/^Existing manual note/)
  expect(saved.evidence.reports.echo.notes).toContain('mildly dilated')
  expect(saved.evidence.reports.echo.notes).toContain('Normal echocardiogram')
  expect(serializeReportEvidence(saved.evidence).used_by_model).toBe(false)
  expect(appendEchoReview(saved.evidence,reviewEchoText(echoSampleText)).evidence).toEqual(saved.evidence)
  evidence.echoFlow='x'.repeat(2000)
  expect(appendEchoReview(evidence,reviewEchoText(echoSampleText))).toMatchObject({evidence,issue:expect.stringContaining('nothing was changed')})
})
