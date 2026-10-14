import type {Features,Field} from './types'
export const REQUIRED_OBSERVATIONS=['Age','EF-TTE','VHD','Q Wave','St Elevation','St Depression','Tinversion','LVH','Poor R Progression','BBB'] as const
export function completenessIssue(features:Features,fields:Field[]){
  const missing=REQUIRED_OBSERVATIONS.filter(name=>features[name]==null||features[name]==='')
  const labels:Record<string,string>={Age:'age','EF-TTE':'echo EF',VHD:'valve assessment'}
  const hasBMI=features.BMI!=null||(typeof features.Weight==='number'&&typeof features.Length==='number'&&features.Length>0)
  const supplied=fields.filter(f=>features[f.name]!=null&&features[f.name]!==''||(f.name==='BMI'&&hasBMI)).length
  const requirements=[missing.length?`Supply ${missing.map(n=>labels[n]??fields.find(f=>f.name===n)?.label??n).join(', ')}.`:'',supplied<28?`Add ${28-supplied} more observations (${supplied}/55 available; at least 28 required).`:''].filter(Boolean)
  return requirements.length?`Insufficient information — cannot generate a prediction. ${requirements.join(' ')}`:''
}
