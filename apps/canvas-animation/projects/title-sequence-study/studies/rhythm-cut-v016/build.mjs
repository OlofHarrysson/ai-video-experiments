import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';
const root=path.dirname(fileURLToPath(import.meta.url));
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const image=p=>fs.readFileSync(path.join(root,p)).toString('base64');
const pose=read('../billions-motion-v015/motion.js').split('window.drawFrame=')[0];
const next=gunzipSync(fs.readFileSync(path.join(root,'../identity-motion-v013/assets/next.json.gz'))).toString();
const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BILLIONS / NEXT / KEEP UP</title><style>*{box-sizing:border-box}body{margin:0;background:#090909;color:#ddd;font:15px system-ui}main{max-width:1600px;margin:auto}canvas{display:block;width:100%;height:auto}nav{display:flex;flex-wrap:wrap;gap:10px;padding:15px;align-items:center}button{background:#252525;color:white;border:1px solid #555;padding:9px 16px;font:inherit;cursor:pointer}input{width:100%;margin:0}</style><main><canvas width="3200" height="1800" aria-label="Six-second silent typography cut"></canvas><nav><button id="play">Play</button><button data-frame="34">BILLIONS</button><button data-frame="64">NEXT</button><button data-frame="128">KEEP UP</button><span id="time"></span></nav><input id="seek" aria-label="Frame" type="range" min="0" max="143" value="0"></main><script>
${read('../../../../tools/artwork/split-plate.js')}
const BILLIONS_POSE=(()=>{${pose}\nreturn window.poseFor})();
${read('motion.js')}
let playing=false,epoch=0;
async function load(src){const i=new Image();i.src=src;await i.decode();return i}
Promise.all([load('data:image/png;base64,${image('../fidelity-v014/assets/billions.png')}'),load('data:image/png;base64,${image('../fidelity-v014/assets/keep.png')}')]).then(([billions,keep])=>{
window.layers=splitArtworkPlate(billions,${read('../billions-motion-v015/rig.json')});
prepareNext(${next});keepPlate=keep;keepReveal=surface(WIDTH*2,HEIGHT*2);keepMask=surface(WIDTH*2,HEIGHT*2);drawFrame(34);window.ready=true;
});
const play=document.querySelector('#play');
function stop(){playing=false;play.textContent='Play'}
function tick(t){if(!playing)return;drawFrame(Math.min(143,Math.floor((t-epoch)*24/1000)));if(currentFrame===143){stop();play.textContent='Replay';return}requestAnimationFrame(tick)}
play.onclick=()=>{if(playing){stop();return}playing=true;play.textContent='Pause';epoch=performance.now();requestAnimationFrame(tick)};
document.querySelector('#seek').oninput=e=>{stop();drawFrame(+e.target.value)};
document.querySelectorAll('[data-frame]').forEach(b=>b.onclick=()=>{stop();drawFrame(+b.dataset.frame)});
</script></html>`;
fs.writeFileSync(path.join(root,'index.html'),html);
console.log(`Built ${html.length} bytes`);
