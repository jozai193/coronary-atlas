export interface ClinicalContext {
  smoking_pack_years:number|null
  smoking_history:string
  alcohol_status:''|'never'|'former'|'current'
  alcohol_pattern:string
  total_cholesterol_mg_dl:number|null
  physical_activity:string
  diet:string
  lifestyle_changes:string
}
export const emptyClinicalContext=():ClinicalContext=>({smoking_pack_years:null,smoking_history:'',alcohol_status:'',alcohol_pattern:'',total_cholesterol_mg_dl:null,physical_activity:'',diet:'',lifestyle_changes:''})
export const CONTEXT_FIELDS:{key:keyof ClinicalContext;label:string;kind:'number'|'text'|'alcohol';unit?:string}[]=[
  {key:'smoking_pack_years',label:'Reported smoking exposure',kind:'number',unit:'pack-years'},
  {key:'smoking_history',label:'Smoking history details',kind:'text'},
  {key:'alcohol_status',label:'Alcohol use history',kind:'alcohol'},
  {key:'alcohol_pattern',label:'Alcohol type, amount and frequency',kind:'text'},
  {key:'total_cholesterol_mg_dl',label:'Total cholesterol',kind:'number',unit:'mg/dL'},
  {key:'physical_activity',label:'Physical activity',kind:'text'},
  {key:'diet',label:'Diet history',kind:'text'},
  {key:'lifestyle_changes',label:'Reported lifestyle changes',kind:'text'},
]
export function contextText(context:ClinicalContext,key:keyof ClinicalContext){
  const value=context[key]
  if(value==null||typeof value==='string'&&value.trim()==='')return '—'
  if(key==='alcohol_status')return ({never:'Never used (reported)',former:'Former use (reported)',current:'Current use (reported)'} as Record<string,string>)[String(value)]??String(value)
  const unit=CONTEXT_FIELDS.find(f=>f.key===key)?.unit
  return unit?`${value} ${unit}`:String(value)
}
export function parseContextNumber(raw:string){
  if(raw==='')return null
  const value=Number(raw)
  return Number.isFinite(value)&&value>=0&&value<=1000000?value:null
}
