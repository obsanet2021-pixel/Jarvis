import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const toast = message => { const t=$('#toast'); t.textContent=message; t.classList.add('show'); clearTimeout(toast.timer); toast.timer=setTimeout(()=>t.classList.remove('show'),2400); };
const now = () => new Date();
function updateClock(){const d=now();$('#clock').textContent=d.toLocaleTimeString([], {hour12:false});$('#date').textContent=d.toLocaleDateString([], {weekday:'long',year:'numeric',month:'short',day:'numeric'}).toUpperCase();}
updateClock();setInterval(updateClock,1000);

const tasks=[
 {name:'Run hologram projection diagnostics',priority:'HIGH',done:false},
 {name:'Review system telemetry report',priority:'NORMAL',done:false},
 {name:'Synchronize local asset library',priority:'NORMAL',done:true}
];
const events=[
 {time:'NOW',name:'Holographic interface initialized',type:'SYSTEM'},
 {time:'09:42',name:'Projection asset loaded successfully',type:'RENDER'},
 {time:'09:38',name:'Core connection established',type:'NETWORK'},
 {time:'09:31',name:'Telemetry monitor started',type:'MONITOR'}
];
function renderTasks(){
 const row=t=>`<div class="directive ${t.done?'done':''}"><input class="check" type="checkbox" ${t.done?'checked':''} aria-label="Complete ${escapeHTML(t.name)}"><span class="directive-name">${escapeHTML(t.name)}</span><span class="priority ${t.priority==='HIGH'?'high':''}">${t.done?'COMPLETE':t.priority}</span></div>`;
 $('#directiveList').innerHTML=tasks.slice(0,3).map(row).join('');
 $('#fullTasks').innerHTML=tasks.map((t,i)=>`<div class="task-full"><input class="check task-check" data-index="${i}" type="checkbox" ${t.done?'checked':''}><span class="task-label ${t.done?'done':''}">${escapeHTML(t.name)}</span><span class="priority ${t.priority==='HIGH'?'high':''}">${t.done?'COMPLETE':t.priority}</span></div>`).join('');
 $('#taskCount').textContent=`${tasks.filter(t=>!t.done).length} OPEN`;
 $$('#directiveList .check').forEach((c,i)=>c.addEventListener('change',()=>{tasks[i].done=c.checked;renderTasks();toast('Directive status updated.')}));
 $$('#fullTasks .task-check').forEach(c=>c.addEventListener('change',()=>{tasks[+c.dataset.index].done=c.checked;renderTasks();}));
}
function renderEvents(){
 const html=events.slice(0,4).map(e=>`<div class="activity-row"><span class="activity-time">${e.time}</span><span class="activity-name">${escapeHTML(e.name)}</span><span class="activity-type">${e.type}</span></div>`).join('');
 $('#activityList').innerHTML=html;
 $('#fullActivity').innerHTML=events.map(e=>`<div class="full-row"><span class="time">${e.time}</span><span class="desc">${escapeHTML(e.name)}</span><span class="kind">${e.type}</span></div>`).join('');
}
function escapeHTML(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
renderTasks();renderEvents();
function addEvent(name,type='COMMAND'){events.unshift({time:now().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}),name,type});renderEvents();}

function navigate(page){
 $$('.workspace').forEach(p=>p.classList.add('hidden'));
 $(`#page-${page}`).classList.remove('hidden');
 $$('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.page===page));
 $('#crumbPage').textContent=page.toUpperCase();
}
$$('.nav-item').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.page)));
$$('[data-goto]').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.goto)));
$('#addTask').addEventListener('click',()=>{const v=$('#newTask').value.trim();if(!v)return;tasks.unshift({name:v,priority:'NORMAL',done:false});$('#newTask').value='';renderTasks();addEvent(`Directive added: ${v}`,'TASK');toast('New directive added.');});
$('#newTask').addEventListener('keydown',e=>{if(e.key==='Enter')$('#addTask').click();});

function respond(command){
 const q=command.trim();if(!q)return;
 const s=q.toLowerCase();let reply='I can help with the dashboard preview. Try “system status”, “show tasks”, “open hardware”, or “rotate hologram”.';
 if(s.includes('status')||s.includes('system'))reply='All demo systems are nominal. The hologram is active, the core link is stable, and the sample power reserve is at 100 percent.';
 else if(s.includes('task')||s.includes('directive')){navigate('tasks');reply=`There are ${tasks.filter(t=>!t.done).length} open directives in the current queue.`;}
 else if(s.includes('activity')||s.includes('log')){navigate('activity');reply='Displaying the local session event stream.';}
 else if(s.includes('hardware')||s.includes('device')){navigate('devices');reply='Opening the connected hardware overview.';}
 else if(s.includes('memory')){navigate('memory');reply='Opening the sample session memory. No personal data is stored.';}
 else if(s.includes('rotate')){rotationEnabled=!rotationEnabled;$('#rotateBtn').classList.toggle('active',rotationEnabled);reply=`Hologram auto-rotation ${rotationEnabled?'enabled':'paused'}.`;}
 else if(s.includes('hello')||s.includes('hi jarvis'))reply='Hello. I am online and ready to assist.';
 $('#assistantMessage').textContent=reply;addEvent(`Command received: ${q}`);$('#commandInput').value='';toast('J.A.R.V.I.S. response ready.');
}
$('#sendCommand').addEventListener('click',()=>respond($('#commandInput').value));
$('#commandInput').addEventListener('keydown',e=>{if(e.key==='Enter')respond(e.target.value);});
$('#rotateBtn').addEventListener('click',()=>{rotationEnabled=!rotationEnabled;$('#rotateBtn').classList.toggle('active',rotationEnabled);toast(`Auto-rotation ${rotationEnabled?'enabled':'paused'}.`);});
$('#intensity').addEventListener('input',e=>{const v=+e.target.value;$('#intensityValue').textContent=`${v}%`;if(hologramMaterials.length)hologramMaterials.forEach(m=>{if(m.uniforms?.uIntensity)m.uniforms.uIntensity.value=v/78;});});
$('#soundBtn').addEventListener('click',()=>toast('Interface sound is not enabled in this preview.'));

// The supplied Blender material graph is represented in the browser with its key visual cues:
// electric-blue emission, amber view-angle rim, blue secondary edge tint, transparent scanline body.
let renderer,scene,camera,modelRoot,raf=0,rotationEnabled=true,hologramMaterials=[];
const stage=$('#modelStage');
const vertexShader=`varying vec3 vNormal; varying vec3 vView; varying vec3 vPos; varying vec3 vLocal; void main(){vLocal=position; vec4 mv=modelViewMatrix*vec4(position,1.0); vNormal=normalize(normalMatrix*normal); vView=normalize(-mv.xyz); vPos=mv.xyz; gl_Position=projectionMatrix*mv;}`;
const fragmentShader=`uniform float uTime; uniform float uIntensity; uniform float uOpacity; uniform vec3 uBlue; uniform vec3 uAmber; uniform vec3 uAzure; varying vec3 vNormal; varying vec3 vView; varying vec3 vPos; varying vec3 vLocal;
float hash(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);} float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
void main(){vec3 N=normalize(vNormal),V=normalize(vView);float fres=pow(1.0-max(dot(N,V),0.0),2.0);float scan=0.72+0.28*sin(vLocal.y*42.0-uTime*2.2);float grain=0.82+0.18*noise(vLocal*5.0+uTime*.08);float band= smoothstep(.0,.035,abs(fract(vLocal.y*9.0-uTime*.16)-.5));float alpha=(.25+fres*.75)*scan*grain*(.62+.38*band)*uOpacity;vec3 col=mix(uBlue,uAzure,0.22+0.24*abs(N.z));col=mix(col,uAmber,pow(fres,3.0)*.68);col*=uIntensity*(.62+grain*.38);float core=pow(fres,5.0);col+=uBlue*core*1.8;gl_FragColor=vec4(col,clamp(alpha,0.08,.96));}`;
function makeHoloMaterial(index){const color=index===0?new THREE.Color(0x087eb0):new THREE.Color(0x12d6a0);const m=new THREE.ShaderMaterial({uniforms:{uTime:{value:0},uIntensity:{value:1},uOpacity:{value:index===0?.82:.46},uBlue:{value:color},uAmber:{value:new THREE.Color(0xffa94d)},uAzure:{value:new THREE.Color(0x167bff)}},vertexShader,fragmentShader,transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending});hologramMaterials.push(m);return m;}
function setupScene(){renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(stage.clientWidth,stage.clientHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;stage.insertBefore(renderer.domElement,stage.firstChild);scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(32,stage.clientWidth/stage.clientHeight,.01,100);camera.position.set(0,0,5);const grid=new THREE.GridHelper(5,28,0x23647a,0x123348);grid.position.y=-1.55;grid.material.transparent=true;grid.material.opacity=.28;scene.add(grid);const ring=new THREE.Mesh(new THREE.TorusGeometry(1.35,.003,4,160),new THREE.MeshBasicMaterial({color:0x2da9ca,transparent:true,opacity:.32}));ring.rotation.x=Math.PI/2;ring.position.y=-1.53;scene.add(ring);const ring2=ring.clone();ring2.scale.setScalar(1.12);ring2.material=ring.material.clone();ring2.material.opacity=.13;scene.add(ring2);}
function fitModel(root){const box=new THREE.Box3().setFromObject(root);const size=box.getSize(new THREE.Vector3());const center=box.getCenter(new THREE.Vector3());root.position.sub(center);const max=Math.max(size.x,size.y,size.z)||1;root.scale.setScalar(2.35/max);const fitted=new THREE.Box3().setFromObject(root);root.position.y-=fitted.min.y+1.1;modelRoot=root;scene.add(root);}
function applyHologram(root){hologramMaterials=[];let i=0;root.traverse(o=>{if(o.isMesh){const mats=Array.isArray(o.material)?o.material:[o.material];const converted=mats.map((_,j)=>makeHoloMaterial((i+j)%2));o.material=Array.isArray(o.material)?converted:converted[0];i++;}});}
function loadBuffer(buffer){const loader=new GLTFLoader();loader.parse(buffer,'',g=>{if(modelRoot)scene.remove(modelRoot);const root=g.scene;applyHologram(root);fitModel(root);$('#modelLoading').style.opacity='0';setTimeout(()=>$('#modelLoading').style.display='none',550);toast('Hologram projection loaded.');},e=>{console.error(e);$('#modelLoading').innerHTML='<b>MODEL LOAD FAILED</b><small>Try selecting the GLB file manually.</small>';});}
async function loadDefault(){try{const [modelRes,matRes]=await Promise.all([fetch('./assets/Hologram.glb'),fetch('./assets/materials.json')]);if(!modelRes.ok)throw Error('Could not fetch model');const materials=await matRes.json();const m=materials['Material.002']?.node_tree?.nodes?.find(n=>n.type==='ShaderNodeEmission'&&n.name==='Emission');if(m?.inputs?.Color?.value){const c=m.inputs.Color.value;console.info('Material palette loaded from materials.json:',c);}loadBuffer(await modelRes.arrayBuffer());}catch(e){console.warn(e);$('#modelLoading').innerHTML='<b>MODEL NOT FOUND</b><small>Use the + button to load Hologram.glb</small>';}}
function resetCamera(){if(!modelRoot)return;modelRoot.rotation.set(0,0,0);camera.position.set(0,0,5);camera.lookAt(0,0,0);toast('Projection view reset.');}
$('#resetBtn').addEventListener('click',resetCamera);
$('#uploadBtn').addEventListener('click',()=>$('#modelFile').click());
$('#modelFile').addEventListener('change',async e=>{const f=e.target.files[0];if(f){$('#modelLoading').style.display='flex';$('#modelLoading').style.opacity='1';$('#modelLoading').innerHTML='<div class="loader-ring"></div><b>LOADING CUSTOM MODEL</b>';loadBuffer(await f.arrayBuffer());e.target.value='';}});
setupScene();loadDefault();
let pointerDown=false,lastX=0,lastY=0;
stage.addEventListener('pointerdown',e=>{pointerDown=true;lastX=e.clientX;lastY=e.clientY;stage.setPointerCapture(e.pointerId);});
stage.addEventListener('pointerup',()=>pointerDown=false);stage.addEventListener('pointercancel',()=>pointerDown=false);
stage.addEventListener('pointermove',e=>{if(pointerDown&&modelRoot){modelRoot.rotation.y+=(e.clientX-lastX)*.008;modelRoot.rotation.x+=(e.clientY-lastY)*.008;lastX=e.clientX;lastY=e.clientY;}});
stage.addEventListener('wheel',e=>{camera.position.z=THREE.MathUtils.clamp(camera.position.z+e.deltaY*.003,2.3,9);},{passive:true});
function animate(t){raf=requestAnimationFrame(animate);if(modelRoot&&rotationEnabled)modelRoot.rotation.y+=.0025;hologramMaterials.forEach(m=>m.uniforms.uTime.value=t*.001);renderer.render(scene,camera);}
animate(0);
const resizeObserver=new ResizeObserver(()=>{if(!renderer)return;const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();});resizeObserver.observe(stage);

// Clearly labelled illustrative telemetry: values are intentionally not read from the host PC.
let telemetryTick=0;setInterval(()=>{telemetryTick++;const values={cpu:22+Math.round(10*Math.sin(telemetryTick*.65)),ram:46+Math.round(4*Math.sin(telemetryTick*.24)),temp:40+Math.round(3*Math.sin(telemetryTick*.42)),net:82+Math.round(8*Math.sin(telemetryTick*.3))};for(const [k,v] of Object.entries(values)){$(`#${k}Val`).textContent=k==='temp'?`${v}°C`:`${v}%`;$(`#${k}Bar`).style.width=`${v}%`; }},2600);
