import {Mixer} from './engine.js';
const $ = id => document.getElementById(id);
const config = await fetch('/manifest.json').then(r => {if(!r.ok) throw Error('Missing player bundle'); return r.json();});
const context = new AudioContext();
const mixer = new Mixer(context, config.duration);
let palette, busy = false;
const cache = new Map();
const stamp = seconds => `${Math.floor(seconds/60)}:${String(Math.floor(seconds%60)).padStart(2,'0')}`;
const showError = error => {$('status').textContent = error.message; console.error(error);};
function reflect() {
  for (const track of config.tracks) {
    const row = document.querySelector(`[data-track="${track.id}"]`);
    if (!row) continue;
    row.classList.toggle('silent', !mixer.audible(track.id));
    row.querySelector('.mute').setAttribute('aria-pressed', mixer.muted.has(track.id));
    row.querySelector('.solo').setAttribute('aria-pressed', mixer.solo.has(track.id));
  }
  $('play').textContent = mixer.playing ? 'Pause' : 'Play';
}
function draw() {
  $('tracks').replaceChildren();
  for (const track of config.tracks) {
    const row = document.createElement('article'); row.className='track'; row.dataset.track=track.id;
    const label=document.createElement('div'), title=document.createElement('h3'), detail=document.createElement('p');
    title.textContent=track.name; detail.textContent=track.description; label.append(title,detail);
    const wave=document.createElement('div');wave.className='wave';wave.title='Click to seek';
    const values=palette.tracks[track.id].waveform, peak=Math.max(...values,.00001);
    const points=values.map((v,i)=>`${i},${15-Math.sqrt(v/peak)*14}`).join(' ')+' '+values.map((v,i)=>`${239-i},${15+Math.sqrt(values[239-i]/peak)*14}`).join(' ');
    wave.innerHTML=`<svg viewBox="0 0 239 30" preserveAspectRatio="none" aria-hidden="true"><polygon points="${points}" fill="currentColor"/></svg><span class="cursor"></span>`;
    wave.addEventListener('click',e=>seek((e.clientX-wave.getBoundingClientRect().left)/wave.clientWidth*config.duration).catch(showError));
    const controls=document.createElement('div');controls.className='track-controls';
    for(const [kind,text,action] of [['mute','Mute',()=>mixer.mute(track.id)],['solo','Solo',()=>mixer.isolate(track.id)]]){
      const b=document.createElement('button');b.className=kind;b.textContent=text;b.setAttribute('aria-label',`${text} ${track.name}`);b.setAttribute('aria-pressed','false');b.onclick=()=>{action();reflect();};controls.append(b);
    }
    row.append(label,wave,controls);$('tracks').append(row);
  }
  reflect();
}
async function load(id) {
  const running=mixer.playing; mixer.pause();busy=true;$('play').disabled=true;$('palette').disabled=true;
  $('status').textContent='Loading sounds…';
  try {
    const chosen=config.palettes.find(p=>p.id===id);
    if(!cache.has(id)){
      const entries=await Promise.all(config.tracks.map(async track=>{
        const r=await fetch(chosen.tracks[track.id].url); if(!r.ok)throw Error(`Could not load ${track.name}`);
        const buffer=await context.decodeAudioData(await r.arrayBuffer());
        if(Math.abs(buffer.duration-config.duration)>.001)throw Error(`Wrong length for ${track.name}`);
        return [track.id,buffer];
      }));cache.set(id,Object.fromEntries(entries));
    }
    palette=chosen;mixer.buffers=cache.get(id);mixer.paletteGain=chosen.gain;draw();
    $('status').textContent='';if(running)await mixer.play();
  } catch(e) {showError(e);if(palette)$('palette').value=palette.id;}
  finally {busy=false;$('play').disabled=!palette;$('palette').disabled=false;reflect();}
}
for(const p of config.palettes){const o=document.createElement('option');o.value=p.id;o.textContent=p.name;$('palette').append(o);}
$('palette').onchange=()=>load($('palette').value);
$('play').onclick=async()=>{if(busy)return;try{if(mixer.playing)mixer.pause();else await mixer.play();reflect();}catch(e){showError(e);}};
async function seek(value){await mixer.seek(value);reflect();}
$('restart').onclick=()=>seek(0).catch(showError);
$('seek').oninput=()=>seek(Number($('seek').value)).catch(showError);
$('loop').onchange=()=>mixer.setLoop($('loop').checked);
$('volume').oninput=()=>mixer.output.gain.setTargetAtTime(Number($('volume').value),context.currentTime,.01);
$('reset').onclick=()=>{mixer.reset();reflect();};
document.addEventListener('keydown',e=>{if(e.code==='Space'&&!['INPUT','TEXTAREA','SELECT','BUTTON'].includes(e.target.tagName)){e.preventDefault();$('play').click();}});
function tick(){
  const position=mixer.position();$('seek').value=position;$('time').textContent=`${stamp(position)} / ${stamp(config.duration)}`;
  document.querySelectorAll('.cursor').forEach(c=>c.style.left=`${position/config.duration*100}%`);
  if(mixer.playing&&!mixer.loop&&position>=config.duration){mixer.pause();reflect();}
  requestAnimationFrame(tick);
}
async function notes(){
  const r=await fetch('/api/feedback');if(!r.ok)throw Error('Could not read saved notes');
  const rows=await r.json();$('notes').replaceChildren();
  for(const item of rows.slice().reverse()){
    const el=document.createElement('div');el.className='saved-note';
    const summary=document.createElement('small');summary.textContent=`${config.palettes.find(p=>p.id===item.palette).name} · ${stamp(item.time)} · ${item.solo.length?'Solo: '+item.solo.join(', '):item.muted.length?'Muted: '+item.muted.join(', '):'All sounds'}`;
    const text=document.createElement('p');text.textContent=item.note;el.append(summary,text);$('notes').append(el);
  }
}
$('note-form').onsubmit=async e=>{
  e.preventDefault();if(!palette)return;$('save').disabled=true;
  try{
    const r=await fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({note:$('note').value,palette:palette.id,time:mixer.position(),muted:[...mixer.muted],solo:[...mixer.solo]})});
    if(!r.ok)throw Error((await r.json()).error);$('note').value='';$('note-context').textContent='Saved with this study.';await notes();
  }catch(e){$('note-context').textContent=e.message;}finally{$('save').disabled=false;}
};
await load(config.palettes[0].id);await notes().catch(showError);tick();
window.addEventListener('pagehide',()=>mixer.pause());
