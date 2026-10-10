const $=id=>document.getElementById(id),art=$('art');
let playing=false,base=0,start=0,raf;
function render(){AcidPrint.draw(art,+$('phase').value,{texture:$('texture').checked,intensity:+$('intensity').value,isolate:$('isolate').value});$('time').value=(+$('phase').value/30).toFixed(2)+' s';}
function stop(){playing=false;cancelAnimationFrame(raf);$('play').textContent='Play';}
function tick(now){if(!playing)return;$('phase').value=(base+Math.floor((now-start)*.03))%240;render();raf=requestAnimationFrame(tick);}
$('play').onclick=()=>{if(playing){stop();return}playing=true;base=+$('phase').value;start=performance.now();$('play').textContent='Pause';raf=requestAnimationFrame(tick);};
$('phase').oninput=()=>{stop();render();};for(const id of ['texture','intensity','isolate'])$(id).oninput=render;
$('compare').onclick=()=>{const on=$('stage').classList.toggle('compare');$('compare').textContent=on?'Hide reference':'Compare reference';};
function save(blob,name){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('save').onclick=()=>art.toBlob(blob=>save(blob,'wild-hours-acid-print.png'));
$('svg').onclick=()=>save(new Blob([AcidPrint.svg()],{type:'image/svg+xml'}),'wild-hours-letter-outlines.svg');
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
render();window.ready=true;
