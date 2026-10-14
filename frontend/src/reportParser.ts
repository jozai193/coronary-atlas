import type {Field,Features} from './types'

export interface ReportCandidate {field:string;value:number|string|null;unit:string;source:string;issue:string;confirmed:boolean}
const labRules:[string,RegExp][]=[
  ['LDL',/^LDL(?:[- ]C)?(?:\s+Chol(?:esterol)?(?:\s+Calc(?:ulated)?)?(?:\s*\(NIH\))?)?(?=\s|:|=|$)/i],
  ['HDL',/^HDL(?:[- ]C)?(?:\s+Chol(?:esterol)?)?\b/i],
  ['TG',/^(?:Triglycerides|Triglyceride|TG)\b/i],
  ['FBS',/^(?:Fasting\s+(?:blood\s+)?(?:glucose|sugar)|Glucose,?\s*fasting|FBS)\b/i],
  ['CR',/^(?:Creatinine|Serum\s+creatinine)\b/i],
  ['HB',/^(?:Hemoglobin|Haemoglobin|Hb)(?!\s*A1c)\b/i],
  ['Na',/^(?:Sodium|Na)\b/i],['K',/^(?:Potassium|K)\b/i],
  ['EF-TTE',/^(?:LVEF|EF[- ]TTE|Ejection\s+fraction|Left\s+ventricular\s+ejection\s+fraction)\b/i],
  ['Weight',/^Weight\b/i],['Length',/^Height\b/i],['PR',/^(?:Resting\s+(?:heart\s+rate|pulse)|Pulse\s+rate)\b/i],
]
const units:Record<string,RegExp>={LDL:/mg\s*\/\s*d[l1]/i,HDL:/mg\s*\/\s*d[l1]/i,TG:/mg\s*\/\s*d[l1]/i,FBS:/mg\s*\/\s*d[l1]/i,CR:/mg\s*\/\s*d[l1]/i,HB:/g\s*\/\s*d[l1]/i,Na:/m(?:mol|eq)\s*\/\s*l/i,K:/m(?:mol|eq)\s*\/\s*l/i,'EF-TTE':/%/,Weight:/\bkg\b/i,Length:/\bcm\b/i,PR:/\b(?:bpm|beats\s*\/\s*min)\b/i}

export function candidateIssue(field:Field|undefined,value:number|string|null){
  if(!field)return 'This field is not supported by the model.'
  if(value==null)return 'No unambiguous result found.'
  if(field.kind==='category')return field.options?.includes(String(value))?'':'Unrecognized category.'
  if(typeof value!=='number'||!Number.isFinite(value))return 'Enter a finite number.'
  if(value<field.minimum!||value>field.maximum!)return `Outside model support (${field.minimum}–${field.maximum} ${field.unit}). Check the source; do not alter a real result to fit the model.`
  return ''
}

export function parseReport(text:string,fields:Field[]):ReportCandidate[]{
  const found:ReportCandidate[]=[]
  const echoTable=/\bDIMENSIONS?\b/i.test(text)&&/\bNORMALS?\b/i.test(text)&&/echocardiog|doppler|\bLVEF\b/i.test(text)
  const add=(field:string,value:number|string|null,unit:string,source:string,issue='')=>found.push({field,value,unit,source,issue:issue||candidateIssue(fields.find(f=>f.name===field),value),confirmed:false})
  for(const raw of text.slice(0,50000).split(/\r?\n/)){
    const line=raw.trim().replace(/[−–]/g,'-')
    if(!line||/^(?:reference|normal\s+range|previous|target|goal|desired|optimal|LDL[- ]P|HDL[- ]P|LDL\s+(?:Calc\s+)?Comment)\b/i.test(line))continue
    const age=line.match(/\bAge\s*:\s*(\d{1,3})(?!\d)(?:\s*(?:years|yrs|Y))?/i)
    if(age)add('Age',Number(age[1]),'years',line)
    const sex=line.match(/\bSex\s*:\s*(Female|Male)\b/i)
    if(sex)add('Sex',sex[1].toLowerCase()==='female'?'Fmale':'Male','',line)
    for(const [name,rule] of labRules){
      // A printed triangle warning icon can be recognized as a leading A.
      // Removing this marker does not interpret the abnormality or alter digits.
      const measurement=line.replace(/^[▲△A]\s+/,'')
      const label=measurement.match(rule)
      if(!label)continue
      let tail=measurement.slice(label[0].length).replace(/^\s*[:=]?\s*/,'')
      if(name==='EF-TTE')tail=tail.replace(/^\((?:est\.?|estimated)\)\s*/i,'')
      // Test-name headings and explanatory prose are not result rows. They
      // must not turn an otherwise unambiguous measurement into a conflict.
      if(!tail||/^(?:is|helps|ref(?:erence)?\b|goal\b)/i.test(tail))continue
      // Require a printed unit and a single current value before it. Do not
      // choose a reference interval, previous result, comparator or code.
      const unitMatch=tail.match(units[name])
      if(!unitMatch){add(name,null,'',line,'Required unit not found. Enter this observation manually after checking the report.');continue}
      let before=tail.slice(0,unitMatch.index).trim().replace(/\b(?:High|Low|H|L)\b/gi,'').trim()
      before=before.replace(/^01\s+/,'').replace(/^[®©*†‡]+\s+/,'') // Printed laboratory superscript, not a result.
      if(!/^\d+(?:\.\d+)?$/.test(before)){add(name,null,unitMatch[0],line,'Ambiguous result, range, comparator or multiple numbers. Enter manually after checking the report.');continue}
      add(name,Number(before),unitMatch[0],line,name==='EF-TTE'&&echoTable?'Echo reference-range table: check the patient result column against the image, then re-enter the checked value. Do not use the NORMAL/NORMALS column.':'')
    }
  }
  const grouped=new Map<string,ReportCandidate[]>()
  for(const c of found)grouped.set(c.field,[...(grouped.get(c.field)??[]),c])
  return [...grouped.values()].map(items=>{
    const first={...items[0]}
    if(items.some(c=>c.value!==first.value||c.issue!==first.issue)){first.issue='Conflicting occurrences. Use one report, one patient and one collection date; resolve manually.';first.source=items.map(c=>c.source).join(' | ')}
    return first
  })
}

export function applyConfirmed(candidates:ReportCandidate[],fields:Field[],current:Features,mode:'replace'|'merge'){
  const accepted=candidates.filter(c=>c.confirmed&&!c.issue&&!candidateIssue(fields.find(f=>f.name===c.field),c.value))
  const features:Features=mode==='replace'?Object.fromEntries(fields.map(f=>[f.name,null])):{...current}
  for(const c of accepted)features[c.field]=c.value
  if(accepted.some(c=>['Weight','Length'].includes(c.field)))features.BMI=null
  return {features,imported:accepted.map(c=>c.field)}
}
