// Self-host OCR runtime; patient pixels/text never go to a remote OCR service.
import {mkdir,copyFile,readFile,writeFile,readdir} from 'node:fs/promises'
import {createHash} from 'node:crypto'
import {fileURLToPath} from 'node:url'
import path from 'node:path'
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..')
const out=path.join(root,'public/ocr')
await mkdir(path.join(out,'core'),{recursive:true})
await mkdir(path.join(out,'lang'),{recursive:true})
await copyFile(path.join(root,'node_modules/tesseract.js/dist/worker.min.js'),path.join(out,'worker.min.js'))
await copyFile(path.join(root,'node_modules/tesseract.js/LICENSE.md'),path.join(out,'LICENSE-tesseract-js.md'))
await copyFile(path.join(root,'node_modules/tesseract.js-core/LICENSE'),path.join(out,'LICENSE-core.txt'))
// OEM 1 uses LSTM only. Include baseline, SIMD and relaxed SIMD variants.
for(const name of await readdir(path.join(root,'node_modules/tesseract.js-core'))){
  if(/-lstm\.wasm\.js$/.test(name))await copyFile(path.join(root,'node_modules/tesseract.js-core',name),path.join(out,'core',name))
}
await copyFile(path.join(root,'node_modules/@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz'),path.join(out,'lang/eng.traineddata.gz'))
// naptha/tessdata's upstream trained data is Apache-2.0 (the npm wrapper
// declares MIT). Preserve the upstream standard license and attribution.
await copyFile(path.join(root,'node_modules/tesseract.js-core/LICENSE'),path.join(out,'LICENSE-language.txt'))
const hashes={}
for(const folder of ['','core','lang'])for(const name of await readdir(path.join(out,folder))){
  if(name==='manifest.json'||!name.includes('.'))continue
  const relative=path.posix.join(folder,name)
  const bytes=await readFile(path.join(out,relative));hashes[relative]={bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')}
}
const pkg=async name=>JSON.parse(await readFile(path.join(root,'node_modules',name,'package.json'),'utf8')).version
await writeFile(path.join(out,'manifest.json'),JSON.stringify({tesseract:await pkg('tesseract.js'),core:await pkg('tesseract.js-core'),language:await pkg('@tesseract.js-data/eng'),language_variant:'4.0.0_best_int',files:hashes},null,2)+'\n')
console.log(`Vendored ${Object.keys(hashes).length} OCR files.`)
