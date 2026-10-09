const art=document.querySelector('#art'),phase=document.querySelector('#phase'),depth=document.querySelector('#depth'),mode=document.querySelector('#mode'),glyph=document.querySelector('#glyph'),glints=document.querySelector('#glints');
let playing=false,origin=0,lastFrame=-1;
function options(){return {depth:Number(depth.value),flat:mode.value==='flat',palette:mode.value==='blue'?1:0,glyph:glyph.value||null,glints:glints.checked,quality:playing?.5:2}}
function render(){WildRenderer.draw(art,Number(phase.value),options());document.querySelector('#depthValue').value=depth.value}
function download(name,url){const a=document.createElement('a');a.download=name;a.href=url;a.click()}
function tick(now){if(!playing)return;const frame=Math.floor((now-origin)/1000*24)%144;if(frame!==lastFrame){phase.value=frame;render();lastFrame=frame}requestAnimationFrame(tick)}
for(const shape of WildGeometry){const option=document.createElement('option');option.value=shape.id;option.textContent=shape.id;glyph.append(option)}
phase.oninput=()=>{origin=performance.now()-Number(phase.value)/24*1000;render()};depth.oninput=mode.onchange=glyph.onchange=glints.onchange=render;
document.querySelector('#play').onclick=()=>{playing=!playing;origin=performance.now()-Number(phase.value)/24*1000;document.querySelector('#play').textContent=playing?'Pause':'Play light';if(playing)requestAnimationFrame(tick);else render()};
document.querySelector('#compare').onclick=event=>{const solo=document.querySelector('main').classList.toggle('solo');event.target.textContent=solo?'Reference off':'Reference on';event.target.setAttribute('aria-pressed',String(!solo))};
document.querySelector('#save').onclick=()=>{const exported=Object.assign(document.createElement('canvas'),{width:1536,height:1024});WildRenderer.draw(exported,Number(phase.value),{...options(),quality:2});download('wild-hours-code.png',exported.toDataURL())};
function svgOutlines(){
  const shapes=WildGeometry.filter(shape=>!glyph.value||shape.id===glyph.value);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024"><title>Wild Hours editable silhouettes</title><desc>Authored vector outlines. Procedural enamel and light are provided separately by renderer.js.</desc>${shapes.map(shape=>`<g id="${shape.id}" data-material="${shape.material}"><path fill="${shape.material==='pink'?'#ff2583':shape.material==='ivory'?'#ffefcc':'#b88738'}" fill-rule="evenodd" d="${shape.d}"/></g>`).join('')}</svg>`;
}
document.querySelector('#svg').onclick=()=>{const url=URL.createObjectURL(new Blob([svgOutlines()],{type:'image/svg+xml'}));download('wild-hours-outlines.svg',url);setTimeout(()=>URL.revokeObjectURL(url),1000)};
render();for(const control of document.querySelectorAll('[disabled]'))control.disabled=false;document.querySelector('#status').textContent='';window.ready=true;
