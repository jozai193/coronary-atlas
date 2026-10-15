import type {components} from './generated/api'
export type Target = 'cad' | 'lad' | 'lcx' | 'rca'
export type Features = Record<string,string|number|null>
export interface Field {name:string;label:string;group:string;kind:'number'|'category';unit:string;unit_note:string;minimum:number|null;maximum:number|null;options:string[]|null}
export interface ModelInfo {version:string;features:Field[];rows:number;seed:number;models:Record<Target,string>;limitations:string[];disclaimer:string;source:string}
export interface Sample {id:string;name:string;synthetic:boolean;note:string;features:Features;recorded_outcomes?:Partial<Record<Target,string>>;source?:{url:string;record_index:number;worksheet_row:number;license:string;used_in_development:boolean};provenance?:{recorded_fields?:string[];explicit_fields:string[];derived_fields:string[];default_fields:string[];unknown_fields?:string[];default_method:string;clinician_reviewed:boolean}}
export type Factor = components['schemas']['Factor']
export type Prediction = components['schemas']['Prediction']
export type Result = components['schemas']['PredictionResponse']
export type CoherenceEvidence = components['schemas']['CoherenceEvidence']
export interface Metrics {accuracy:number;precision:number;recall:number;f1:number;roc_auc:number;specificity:number;brier:number;confusion_matrix:number[][]}
export type ModelVariant = 'baseline'|'histgb_lcx_v2'|'calibrated_ensemble_v1'
export interface CandidateInfo {available:boolean;candidate_id:string;name?:string;note?:string;runs?:{repeat:number;baseline:Metrics;candidate:Metrics}[];artifact_sha256?:string;ensemble?:{available:boolean;candidate_id:string;name?:string;note?:string;runs?:{repeat:number;targets:Record<Target,{baseline:Metrics;candidate:Metrics}>}[]}}
export interface Evaluation {method:string;threshold:number;targets:Record<Target,{metrics:Metrics;baseline:Metrics;fold_sd:Metrics;auc_bootstrap_interval:number[];interval_note:string;curves:{roc:{fpr:number[];tpr:number[]};calibration:{predicted:number[];observed:number[]}}}>}
export const TARGETS:Target[]=['cad','lad','lcx','rca']
export const NAMES:Record<Target,string>={cad:'Overall coronary artery disease',lad:'Left anterior descending',lcx:'Left circumflex',rca:'Right coronary artery'}
export const color=(p:number|undefined)=>p===undefined?'#606A70':p<.3?'#526851':p<.7?'#805C28':'#8A413A'
export const percent=(p:number)=>`${(p*100).toFixed(1)}%`
