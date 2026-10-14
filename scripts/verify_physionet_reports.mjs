// Actual public machine-ECG text replay, not waveform interpretation or OCR.
import {readFileSync,writeFileSync,existsSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {resolve,dirname} from 'node:path'
import {fileURLToPath} from 'node:url'
import {createServer} from '../frontend/node_modules/vite/dist/node/index.js'
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..')
const sha=path=>createHash('sha256').update(readFileSync(path)).digest('hex')
const protocolPath=resolve(root,'output/verification/physionet-report-parser-protocol.json')
const protocol=JSON.parse(readFileSync(protocolPath,'utf8'))
const reportsPath=resolve(root,protocol.reports)
if(sha(reportsPath)!==protocol.reports_sha256||sha(resolve(root,'frontend/src/reportParser.ts'))!==protocol.parser_sha256)throw Error('Frozen input/parser hash mismatch')
const reports=JSON.parse(readFileSync(reportsPath,'utf8'))
const metadata=JSON.parse(readFileSync(resolve(root,'models/metadata.json'),'utf8'))
const server=await createServer({root:resolve(root,'frontend'),configFile:false,server:{middlewareMode:true}})
try {
  const {parseReport}=await server.ssrLoadModule('/src/reportParser.ts')
  const fields={},proposals=[]
  for(const record of reports){
    const candidates=parseReport(record.report,metadata.feature_schema)
    for(const candidate of candidates){
      fields[candidate.field]=(fields[candidate.field]??0)+1
      proposals.push({study_id:record.study_id,field:candidate.field,issue:candidate.issue,confirmed:candidate.confirmed})
    }
  }
  const receipt={source:'https://physionet.org/content/mimic-iv-ecg/1.0/',protocol_sha256:sha(protocolPath),parser_sha256:protocol.parser_sha256,records_replayed:reports.length,proposals:proposals.length,unflagged_proposals:proposals.filter(p=>!p.issue).length,field_counts:fields,autoconfirmed:proposals.filter(p=>p.confirmed).length,scope:'Negative-control replay on public machine-generated ECG text. It does not evaluate diagnostic interpretation, photo OCR, sensitivity on positive lab/echo examples, or CAD accuracy.'}
  const output=resolve(root,'output/verification/physionet-report-parser-results.json')
  if(existsSync(output))throw Error('Preserve existing replay receipt')
  writeFileSync(output,JSON.stringify(receipt,null,2))
  console.log(JSON.stringify(receipt,null,2))
} finally {await server.close()}
