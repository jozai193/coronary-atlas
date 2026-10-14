export const CORONARY_TARGETS=['lad','lcx','rca'] as const
export const ARTERY_COLOR='#dc3447'
export const VEIN_COLOR='#398fdd'
export const HEART_COLOR='#efa69f'
export const INTERNAL_PARTS=['atrial_chambers','ventricular_chambers','valve_leaflets','papillary_muscles']
export const DETAIL_PARTS=['context_branches','coronary_sinus','cardiac_veins',...INTERNAL_PARTS]
export type AnatomyColorMode='anatomy'|'probability'
export function coronaryShade(p:number){return p<.3?'#f25e6a':p<.7?'#df344b':'#bd1636'}
export function structureColor(kind:string,p:number|undefined,mode:AnatomyColorMode){
  if(CORONARY_TARGETS.some(k=>k===kind))return mode==='probability'&&p!==undefined?coronaryShade(p):ARTERY_COLOR
  // Blood-flow convention: the pulmonary trunk carries oxygen-poor blood,
  // despite being an artery. Pulmonary veins carry oxygen-rich blood.
  if(['pulmonary_trunk','coronary_sinus','cardiac_veins'].includes(kind))return VEIN_COLOR
  if(['aorta','left_main','context_branches'].includes(kind))return ARTERY_COLOR
  if(kind==='valve_leaflets')return '#f5dbbf'
  if(kind==='papillary_muscles')return '#d5827e'
  if(INTERNAL_PARTS.includes(kind))return '#e9a29d'
  return HEART_COLOR
}
