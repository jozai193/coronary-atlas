import { Component, Suspense, useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { Canvas, useFrame, useLoader, useThree } from '@react-three/fiber'
import { Html, OrbitControls } from '@react-three/drei'
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
import { Mesh, MeshStandardMaterial, DoubleSide, Vector3, Quaternion, Spherical } from 'three'
import { RotateCcw, Focus, Layers3, Move3D } from 'lucide-react'
import { percent, NAMES, type Result, type Target } from './types'
import anchors from './generated/anatomy-anchors.json'
import {ARTERY_COLOR,VEIN_COLOR,HEART_COLOR,INTERNAL_PARTS,DETAIL_PARTS,structureColor,coronaryShade,type AnatomyColorMode} from './anatomyDisplay'

interface Manifest { center:[number,number,number]; scale:number; structures:Record<string,{fma:string[];files:{file:string}[]}> }
type Tissue = 'surface'|'ghost'|'inside'|'vessels'
type View = 'front'|'back'|'side'|'free'|'focus'
const VESSELS:Target[]=['lad','lcx','rca']
const ABOUT:Record<Target,string>={
  cad:'CAD is the dataset’s overall coronary artery disease label.',
  lad:'Runs down the front of the heart. LAD stands for left anterior descending artery.',
  lcx:'Curves around the left side toward the back of the heart. LCX stands for left circumflex artery.',
  rca:'Courses along the right side of the heart. RCA stands for right coronary artery.',
}

class SceneBoundary extends Component<{children:ReactNode;onFail:()=>void},{failed:boolean}>{
  state={failed:false}
  static getDerivedStateFromError(){return {failed:true}}
  componentDidCatch(){this.props.onFail()}
  render(){return this.state.failed?<div className="scene-error">3D anatomy could not load. Reload to retry. All estimates remain available in the result cards.</div>:this.props.children}
}

function SceneReady({onReady}:{onReady:()=>void}){
  useEffect(onReady,[onReady])
  return null
}

function Part({file,kind,selected,result,onSelect,tissue,isolate,colorMode}:{file:string;kind:string;selected:Target;result:Result|null;onSelect:(t:Target)=>void;tissue:Tissue;isolate:boolean;colorMode:AnatomyColorMode}){
  const source=useLoader(OBJLoader,file)
  const isVessel=VESSELS.includes(kind as Target)
  const p=isVessel?result?.[kind as Target]?.probability:undefined
  const obj=useMemo(()=>{
    const clone=source.clone(true)
    const base=structureColor(kind,p,colorMode)
    const chamber=kind==='atrial_chambers'||kind==='ventricular_chambers'
    const opacity=kind==='heart'?(tissue==='ghost'?.15:tissue==='inside'?.045:1):chamber?.12:1
    clone.traverse(node=>{if(node instanceof Mesh){
      node.material=new MeshStandardMaterial({color:base,roughness:isVessel?.36:.52,metalness:0,transparent:opacity<1,opacity,depthWrite:opacity===1,side:DoubleSide,emissive:isVessel?base:'#000000',emissiveIntensity:isVessel?(selected===kind?.14:.035):0})
      node.renderOrder=isVessel?2:0
    }})
    return clone
  },[source,isVessel,p,selected,kind,tissue,colorMode])
  useEffect(()=>()=>{obj.traverse(n=>{if(n instanceof Mesh)(n.material as MeshStandardMaterial).dispose()})},[obj])
  const visible=(!isolate||kind===selected)&&(tissue!=='vessels'||isVessel||['context_branches','left_main','coronary_sinus','cardiac_veins'].includes(kind))&&(!INTERNAL_PARTS.includes(kind)||tissue==='ghost'||tissue==='inside')
  return <primitive object={obj} visible={visible} onClick={isVessel?(e:{stopPropagation:()=>void})=>{e.stopPropagation();onSelect(kind as Target)}:undefined}/>
}

function CameraRig({view,reset,onOrbit,selected}:{view:View;reset:number;onOrbit:()=>void;selected:Target}){
  const controls=useRef<OrbitControlsImpl>(null)
  const {camera,invalidate,gl,size}=useThree()
  const destination=useRef<{position:Vector3;target:Vector3}|null>(null)
  useEffect(()=>{
    const media=window.matchMedia?.('(prefers-reduced-motion: reduce)')
    function stopMotion(){const goal=destination.current;if(!media?.matches||!goal)return;camera.position.copy(goal.position);controls.current?.target.copy(goal.target);controls.current?.update();destination.current=null;gl.domElement.dataset.cameraMoving='false';invalidate()}
    media?.addEventListener('change',stopMotion)
    return()=>media?.removeEventListener('change',stopMotion)
  },[camera,gl,invalidate])
  useEffect(()=>{
    const canvas=gl.domElement
    canvas.tabIndex=0
    canvas.setAttribute('aria-label','Interactive heart. Arrow keys rotate; plus and minus zoom; Shift and arrow keys pan; Home returns to front.')
    function keyboard(e:KeyboardEvent){
      if(!controls.current||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','_','Home'].includes(e.key))return
      e.preventDefault();destination.current=null;gl.domElement.dataset.cameraMoving='false'
      const target=controls.current.target,offset=camera.position.clone().sub(target)
      if(e.key==='Home'){target.set(0,-.1,0);camera.position.set(.3,.25,7.8).sub(target).multiplyScalar(Math.max(1,1.05/(size.width/size.height))).add(target)}
      else if(e.key==='+'||e.key==='='){camera.position.copy(target).add(offset.setLength(Math.max(4.3,offset.length()*.9)))}
      else if(e.key==='-'||e.key==='_'){camera.position.copy(target).add(offset.setLength(Math.min(16,offset.length()/ .9)))}
      else if(e.shiftKey){const direction=new Vector3(e.key==='ArrowLeft'?-.18:e.key==='ArrowRight'?.18:0,e.key==='ArrowUp'?.18:e.key==='ArrowDown'?-.18:0,0).applyQuaternion(camera.quaternion);target.add(direction);camera.position.add(direction)}
      else {const spherical=new Spherical().setFromVector3(offset);spherical.theta+=e.key==='ArrowLeft'?.12:e.key==='ArrowRight'?-.12:0;spherical.phi+=e.key==='ArrowUp'?-.12:e.key==='ArrowDown'?.12:0;spherical.makeSafe();camera.position.copy(target).add(new Vector3().setFromSpherical(spherical))}
      controls.current.update();invalidate();onOrbit()
    }
    canvas.addEventListener('keydown',keyboard)
    return()=>canvas.removeEventListener('keydown',keyboard)
  },[camera,gl,invalidate,onOrbit,size.width,size.height])
  useEffect(()=>{
    if(view==='free'){destination.current=null;gl.domElement.dataset.cameraMoving='false';return}
    const positions={front:[.3,.25,7.8],back:[-.3,.25,-7.8],side:[7.8,.25,0]}
    const vessel=selected==='cad'?'lad':selected
    const target=view==='focus'?new Vector3(...anchors[vessel].anchor as [number,number,number]).multiplyScalar(.45):new Vector3(0,-.1,0)
    const direction=vessel==='lcx'?new Vector3(4.5,1,-5.8):vessel==='rca'?new Vector3(-4,1,5.9):new Vector3(1.6,.3,6.7)
    const position=view==='focus'?direction.add(target):new Vector3(...positions[view] as [number,number,number])
    // Preserve horizontal breathing room when the canvas becomes narrow.
    position.sub(target).multiplyScalar(Math.max(1,1.05/(size.width/size.height))).add(target)
    if(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches){camera.position.copy(position);controls.current?.target.copy(target);controls.current?.update();destination.current=null;gl.domElement.dataset.cameraMoving='false'}
    else {destination.current={position,target};gl.domElement.dataset.cameraMoving='true'}
    invalidate()
  },[view,reset,selected,camera,invalidate,gl,size.width,size.height])
  useFrame((_,dt)=>{const goal=destination.current;if(!goal||!controls.current)return
    const alpha=1-Math.exp(-Math.min(dt,.05)*8)
    // Orbit around the anatomy instead of interpolating a straight line through it.
    const offset=camera.position.clone().sub(controls.current.target),goalOffset=goal.position.clone().sub(goal.target)
    const radius=offset.length()+(goalOffset.length()-offset.length())*alpha
    const rotation=new Quaternion().setFromUnitVectors(offset.normalize(),goalOffset.normalize())
    offset.applyQuaternion(new Quaternion().slerp(rotation,alpha)).multiplyScalar(radius)
    controls.current.target.lerp(goal.target,alpha);camera.position.copy(controls.current.target).add(offset);controls.current.update()
    if(camera.position.distanceTo(goal.position)<.005&&controls.current.target.distanceTo(goal.target)<.005){camera.position.copy(goal.position);controls.current.target.copy(goal.target);controls.current.update();destination.current=null;gl.domElement.dataset.cameraMoving='false'}
    else invalidate()
  })
  return <OrbitControls ref={controls} makeDefault minDistance={4.3} maxDistance={16} enableDamping={false} zoomSpeed={.6} rotateSpeed={.65} onStart={()=>{destination.current=null;onOrbit()}}/>
}

function VesselLabels({selected,result,onSelect}:{selected:Target;result:Result|null;onSelect:(t:Target)=>void}){
  return <>{VESSELS.filter(v=>v===selected).map(v=><Html key={v} position={anchors[v as keyof typeof anchors].anchor as [number,number,number]} center zIndexRange={[8,1]}>
    <button className={`anatomy-anchor ${selected===v?'active':''}`} onClick={e=>{e.stopPropagation();onSelect(v)}} aria-label={`Focus ${NAMES[v]} on heart`} aria-pressed={selected===v}><span>{v.toUpperCase()}</span><small>{result?percent(result[v].probability):'Reference vessel'}</small><i/></button>
  </Html>)}</>
}

export default function HeartViewer({result,selected,onSelect}:{result:Result|null;selected:Target;onSelect:(t:Target)=>void}){
  const [manifest,setManifest]=useState<Manifest|null>(null),[failed,setFailed]=useState(false)
  const [tissue,setTissue]=useState<Tissue>('surface'),[detail,setDetail]=useState(true),[isolate,setIsolate]=useState(false)
  const [view,setView]=useState<View>('front'),[reset,setReset]=useState(0)
  const [labels,setLabels]=useState(true),[tour,setTour]=useState(false)
  const [colorMode,setColorMode]=useState<AnatomyColorMode>('probability')
  const [ready,setReady]=useState(false)
  const onReady=useCallback(()=>setReady(true),[])
  const vessel=selected==='cad'?'lad':selected
  const previousVessel=useRef(vessel)
  useEffect(()=>{if(previousVessel.current!==vessel){setView('focus');setReset(n=>n+1);previousVessel.current=vessel}},[vessel])
  useEffect(()=>{fetch('/anatomy/manifest.json').then(r=>{if(!r.ok)throw Error();return r.json()}).then(setManifest).catch(()=>setFailed(true))},[])
  function restore(){setView('front');setReset(n=>n+1);setIsolate(false);setTour(false)}
  function select(v:Target){onSelect(v);setView('focus');setReset(n=>n+1)}
  return <section tabIndex={-1} className="anatomy panel" aria-label="Interactive coronary anatomy" data-anatomy-ready={ready} data-camera-view={view}>
    <div className="panel-heading"><div><span className="eyebrow">02 / EXPLORE THE ANATOMY</span><h2>Inside the coronary network</h2></div><span className="reference-badge">REFERENCE HEART</span></div>
    <div className="scene-wrap">
      <div className="scene-label"><span className="tiny-dot"/>{result&&colorMode==='probability'?'Coronary probability shading':'Anatomy colors · no probability shading'}</div>
      <div className="view-switch" aria-label="Camera views">{(['front','back','side'] as const).map(v=><button key={v} aria-pressed={view===v} onClick={()=>{setView(v);setReset(n=>n+1)}}>{v[0].toUpperCase()+v.slice(1)}</button>)}<button onClick={restore} title="Reset 3D view" aria-label="Reset 3D view"><RotateCcw size={15}/></button></div>
      {!ready&&!failed&&<div className="anatomy-loading" role="status">Loading detailed reference anatomy…</div>}
      {failed?<div className="scene-error">Anatomy could not load. Reload to retry. {result?'Model estimates remain available.':'No probability is mapped to this view.'}</div>:manifest?<SceneBoundary onFail={()=>setFailed(true)}><Canvas aria-label="3D reference heart; drag to rotate and scroll to zoom" camera={{position:[.3,.4,7.4],fov:38}} dpr={[1,1.5]} frameloop="demand" gl={{antialias:true,alpha:true}}>
        <ambientLight intensity={.6}/><hemisphereLight args={['#fff0eb','#422a2c',.7]}/><directionalLight position={[3,5,6]} intensity={1.8}/><directionalLight position={[-4,1,-3]} color="#e4eaff" intensity={1.1}/><directionalLight position={[-3,-2,4]} color="#ffd2c4" intensity={.4}/>
        <Suspense fallback={null}><group rotation={[-Math.PI/2,0,0]} scale={manifest.scale}><group position={manifest.center.map(v=>-v) as [number,number,number]}>{Object.entries(manifest.structures).filter(([kind])=>detail||!DETAIL_PARTS.includes(kind)).flatMap(([kind,structure])=>structure.files.map(f=><Part key={f.file} file={f.file} kind={kind} selected={vessel} result={result} onSelect={select} tissue={tissue} isolate={isolate} colorMode={colorMode}/>))}</group></group>{labels&&<VesselLabels selected={vessel} result={result} onSelect={select}/>}<SceneReady onReady={onReady}/></Suspense>
        <CameraRig view={view} reset={reset} selected={vessel} onOrbit={()=>setView('free')}/>
      </Canvas></SceneBoundary>:null}
      <div className="orientation-label">{view==='focus'?`${vessel.toUpperCase()} focus · ${vessel==='lcx'?'back / left':'front / oblique'}`:view==='free'?'Free orbit':`${view[0].toUpperCase()+view.slice(1)} view`}<small>Shared anatomical reference</small></div>
      <div className="vessel-pills">{VESSELS.map(v=><button key={v} className={vessel===v?'selected':''} aria-pressed={vessel===v} onClick={()=>select(v)}><i style={{background:structureColor(v,result?.[v].probability,colorMode)}}/>{v.toUpperCase()}<strong>{result?percent(result[v].probability):'Explore'}</strong></button>)}</div>
      <div className="orbit-hint"><Move3D size={14}/>Drag to rotate · scroll to zoom · keyboard controls below</div>
    </div>
    <div className="anatomy-controls"><div className="tissue-switch" aria-label="Heart tissue display">{([['surface','Surface'],['ghost','See through'],['inside','Inside heart'],['vessels','Vessels only']] as const).map(([v,label])=><button key={v} aria-pressed={tissue===v} onClick={()=>{setTissue(v);setIsolate(false);if(v==='inside')setDetail(true)}}>{label}</button>)}</div><div className="detail-controls"><button aria-pressed={isolate} onClick={()=>setIsolate(!isolate)}><Focus size={14}/>{isolate?'Show all':`Isolate ${vessel.toUpperCase()}`}</button><button aria-pressed={detail} onClick={()=>setDetail(!detail)}><Layers3 size={14}/>Atlas detail</button></div></div>
    {tissue==='inside'&&<p className="anatomy-structure-note">Internal reference view: translucent walls reveal chamber cavities, valve leaflets and papillary muscles. These are shared atlas structures; their shape and color do not depict this profile’s echo findings or valve severity.</p>}
    <details className="anatomy-options"><summary>View, colour &amp; anatomy options</summary>
    <div className="anatomy-controls anatomy-palette"><div className="tissue-switch" aria-label="Vessel color meaning"><button aria-pressed={colorMode==='anatomy'} onClick={()=>setColorMode('anatomy')}>Anatomy colors</button><button disabled={!result} aria-pressed={colorMode==='probability'&&!!result} onClick={()=>setColorMode('probability')}>Probability shading</button></div><div className="legend"><span><i style={{background:HEART_COLOR}}/>Heart tissue</span><span><i style={{background:ARTERY_COLOR}}/>Oxygen-rich vessels</span><span><i style={{background:VEIN_COLOR}}/>Oxygen-poor vessels</span></div></div>
    <p className="anatomy-structure-note">Reference blood-flow colors: aorta and coronary arteries red; pulmonary trunk (pulmonary artery), cardiac veins and coronary sinus blue. Pulmonary veins carry oxygen-rich blood and are conventionally red; they are not separately shown here. Colors are illustrative, not measured oxygen levels.</p>
    <div className="anatomy-learning"><button aria-pressed={labels} onClick={()=>setLabels(!labels)}>{labels?'Hide':'Show'} selected label</button><button aria-pressed={tour} onClick={()=>{setTour(!tour);if(!tour){setLabels(true);setIsolate(false);select('lad')}}}>{tour?'End anatomy tour':'Take anatomy tour'}</button><button onClick={()=>select(vessel)}>Focus {vessel.toUpperCase()}</button></div>
    <details className="camera-help"><summary>Keyboard & pointer controls</summary><p>Focus the heart canvas with Tab. Arrow keys rotate, +/− zoom, Shift + arrow keys pan, and Home returns to the front. With a pointer, drag to rotate, scroll to zoom, and right-drag to pan. Camera transitions respect reduced motion.</p></details>
    <div className="vessel-guide"><span className="vessel-initial">{vessel.toUpperCase()}</span><div><h3>{NAMES[vessel]}</h3><p>{ABOUT[vessel]} {result?'Select a vessel to see its raw model explanation below.':'Select a vessel to explore its reference anatomy.'}</p></div></div>
    </details>
    {tour&&<div className="anatomy-tour" aria-live="polite"><div><span className="eyebrow">ANATOMY TOUR · {VESSELS.indexOf(vessel)+1} / 3</span><strong>{NAMES[vessel]}</strong><p>{ABOUT[vessel]} The label is anchored to this vessel’s reference mesh, not a lesion.</p></div><button onClick={()=>{if(vessel==='rca'){setTour(false)}else select(VESSELS[VESSELS.indexOf(vessel)+1])}}>{vessel==='rca'?'Finish tour':`Next: ${VESSELS[VESSELS.indexOf(vessel)+1].toUpperCase()} →`}</button></div>}
    <div className="anatomy-foot">{result&&colorMode==='probability'?<><div className="legend"><span><i style={{background:coronaryShade(.1)}}/>Lower &lt;30%</span><span><i style={{background:coronaryShade(.5)}}/>Intermediate</span><span><i style={{background:coronaryShade(.9)}}/>Higher ≥70%</span></div><p>Light-to-dark red shading shows displayed LAD, LCX and RCA probabilities. Shared reference anatomy; no plaque location or measured narrowing. Bands are display conventions.</p></>:<p>No probability is mapped in anatomy-color mode. Red and blue follow conventional blood-flow colours; pale red identifies heart tissue. Shared anatomy, not patient imaging.</p>}</div>
  </section>
}
