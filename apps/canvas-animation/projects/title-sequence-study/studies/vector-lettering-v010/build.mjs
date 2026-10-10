import fs from 'node:fs';
import path from 'node:path';
import{fileURLToPath}from'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const files=['../../node_modules/clipper-lib/clipper.js','../image-to-code-v006/vector-fields.js','geometry.js','highlights.js','art.js','edit.js'];
const script=files.map(f=>`/* ${f} */\n`+fs.readFileSync(path.join(here,f),'utf8')).join('\n');
const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Wild Hours — vector lettering</title>
<style>*{box-sizing:border-box}body{margin:0;background:#101013;color:#e8e5e0;font:15px system-ui,sans-serif}main{max-width:1300px;margin:30px auto;padding:0 20px}h1{font-size:20px;font-weight:550;margin:0 0 8px}p{color:#b7b5b0;font-size:14px}a{color:#e0d3ac}canvas{display:block;width:100%;height:auto;background:#000;margin:22px 0}nav{display:flex;gap:12px;align-items:center;flex-wrap:wrap}button{background:#29282d;border:1px solid #49474e;border-radius:5px;padding:9px 14px;color:inherit;font:inherit}input{flex:1;min-width:150px;accent-color:#e5c36a}output{font-size:13px;min-width:230px;color:#b9b7b1}#status{min-height:20px}</style>
<main><h1>Wild Hours</h1><p>Silent typography study. Editable vector lettering, procedural materials, and distinct construction events.</p><canvas id="stage" width="1600" height="900" aria-label="Animated typography preview"></canvas><nav><button id="play" disabled>Play</button><button id="prev" disabled>Previous shot</button><button id="next" disabled>Next shot</button><input id="seek" aria-label="Frame" type="range" min="0" max="287" value="0" disabled><output id="position"></output></nav><p id="status">Preparing vector surfaces…</p><p><a href="review.html">Video and study notes</a></p></main>
<script>addEventListener('error',e=>{document.querySelector('#status').textContent='Preview error: '+e.message;});</script>
<script>${script.replaceAll('</script','<\\/script')}</script>
<script>
const stage=document.querySelector('#stage'),play=document.querySelector('#play'),seek=document.querySelector('#seek'),position=document.querySelector('#position');let frame=0,playing=false,start=0;
window.renderFrame=n=>{frame=((Math.floor(n)%LetteringEdit.frames)+LetteringEdit.frames)%LetteringEdit.frames;const state=LetteringEdit.draw(stage,frame);seek.value=frame;position.textContent=(frame/24).toFixed(2)+' s · '+state.label;return state;};
function pause(){playing=false;play.textContent='Play';}
function tick(now){if(playing){renderFrame(Math.floor((now-start)/1000*24));requestAnimationFrame(tick);}}
play.onclick=()=>{if(playing){pause();return;}playing=true;play.textContent='Pause';start=performance.now()-frame/24*1000;requestAnimationFrame(tick);};
seek.oninput=()=>{pause();renderFrame(Number(seek.value));};
function step(direction){pause();const shots=LetteringEdit.shots,index=shots.findIndex(s=>frame<s.end);renderFrame(shots[(index+direction+shots.length)%shots.length].start);}
document.querySelector('#prev').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);
setTimeout(()=>{try{for(const id of ['script','tuscan','liquid'])LetteringArt.prepare(id);renderFrame(0);seek.max=LetteringEdit.frames-1;for(const el of document.querySelectorAll('button,input'))el.disabled=false;document.querySelector('#status').textContent=(LetteringEdit.frames/LetteringEdit.fps)+' seconds · 24 fps · silent';window.previewReady=true;}catch(error){document.querySelector('#status').textContent='Preview error: '+error.message;console.error(error);}},50);
</script></html>`;
fs.writeFileSync(path.join(here,'index.html'),html);
console.log('Built index.html:',Buffer.byteLength(html),'bytes');
