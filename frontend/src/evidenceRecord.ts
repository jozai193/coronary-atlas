import {echoReviewNotes,type EchoTextReview} from './echoReportReview'
export const REPORT_KINDS=['ecg','echo','angiography'] as const
export type ReportKind=typeof REPORT_KINDS[number]
export const REPORT_NAMES:Record<ReportKind,string>={ecg:'ECG',echo:'Echo / Doppler',angiography:'Coronary angiography / CCTA'}
export interface SourceReport {file:File|null;sha256:string;reference:string;date:string;notes:string}
export interface ReportEvidence {
  reports:Record<ReportKind,SourceReport>
  echoEf:string
  echoFlow:string
  echoValves:string
  narrowing:Record<'lad'|'lcx'|'rca',string>
  checked:boolean
}
const blankReport=():SourceReport=>({file:null,sha256:'',reference:'',date:'',notes:''})
export const emptyReportEvidence=():ReportEvidence=>({reports:{ecg:blankReport(),echo:blankReport(),angiography:blankReport()},echoEf:'',echoFlow:'',echoValves:'',narrowing:{lad:'',lcx:'',rca:''},checked:false})
export function appendEchoReview(evidence:ReportEvidence,review:EchoTextReview){
  const append=(previous:string,next:string)=>!next||previous.includes(next)?previous:[previous,next].filter(Boolean).join('\n\n')
  const notes=append(evidence.reports.echo.notes,echoReviewNotes(review)),echoFlow=append(evidence.echoFlow,review.flow.join('\n')),echoValves=append(evidence.echoValves,review.valves.join('\n'))
  if([notes,echoFlow,echoValves].some(value=>value.length>2000))return {evidence,issue:'The combined echo notes exceed 2,000 characters in a field. Shorten the excerpts or copy the relevant findings manually; nothing was changed.'}
  return {evidence:{...evidence,echoFlow,echoValves,checked:false,reports:{...evidence.reports,echo:{...evidence.reports.echo,notes}}},issue:''}
}
export function evidencePercent(raw:string){
  if(!raw.trim())return {value:null,issue:''}
  const value=Number(raw)
  return /^\d+(?:\.\d+)?$/.test(raw.trim())&&Number.isFinite(value)&&value>=0&&value<=100
    ?{value,issue:''}:{value:null,issue:'Enter one reported percentage from 0 to 100. Keep ranges, comparators and uncertainty in the findings note.'}
}
export function reportFileIssue(file:Pick<File,'type'|'size'>){
  return !['application/pdf','image/png','image/jpeg','image/webp'].includes(file.type)?'Use a PDF, PNG, JPEG or WebP report.':file.size===0||file.size>10*1024*1024?'Use a nonempty report no larger than 10 MB.':''
}
export function hasReportSource(report:SourceReport){return !!report.file||!!report.reference.trim()}
export function echoInputDifference(evidence:ReportEvidence,features:Record<string,unknown>){
  const parsed=evidencePercent(evidence.echoEf)
  if(!evidence.checked||!hasReportSource(evidence.reports.echo)||parsed.value===null)return ''
  if(features['EF-TTE']==null)return `The checked report EF is ${parsed.value}%; no model EF has been supplied.`
  return Number(features['EF-TTE'])!==parsed.value?`The checked report EF is ${parsed.value}%; the model input EF is ${features['EF-TTE']}%. Review the source and collection date.`:''
}
export function serializeReportEvidence(evidence:ReportEvidence){
  return {
    used_by_model:false,
    provenance:'User-supplied report entries; source authenticity, case identity and clinical interpretation are not independently verified. Public dataset examples have no original reports.',
    checked_by_user:evidence.checked,
    reports:Object.fromEntries(REPORT_KINDS.map(kind=>{const report=evidence.reports[kind];return [kind,{reference:report.reference,date:report.date,notes:report.notes,attachment:report.file?{name:report.file.name,type:report.file.type,bytes:report.file.size,sha256:report.sha256||null}:null}]})),
    echo:{ef:evidencePercent(evidence.echoEf),ef_entered:evidence.echoEf,flow_findings:evidence.echoFlow,valve_findings:evidence.echoValves},
    reported_narrowing:Object.fromEntries(Object.entries(evidence.narrowing).map(([vessel,raw])=>[vessel,{entered:raw,...evidencePercent(raw)}])),
    attachment_contents_included:false,
  }
}
