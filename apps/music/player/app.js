import {Mixer} from './engine.js';
const $ = id => document.getElementById(id);
const config = await fetch('/manifest.json').then(r => {if(!r.ok) throw Error('Missing player bundle'); return r.json();});
const context = new AudioContext();
const mixer = new Mixer(context, config.duration);
let ready = false, session, lastCommand = 0, lastError = null;
const stamp = seconds => `${Math.floor(seconds/60)}:${String(Math.floor(seconds%60)).padStart(2,'0')}`;
const showError = error => {lastError=error.message;$('status').textContent=error.message;console.error(error);};
function resetMix() {
  mixer.reset();
  for(const track of config.tracks)if(track.enabled===false)mixer.muted.add(track.id);
  mixer.updateGains();
}
function setEnabled(id, enabled) {
  mixer.solo.clear();
  const track=config.tracks.find(t=>t.id===id);
  if(enabled){
    mixer.muted.delete(id);
    if(track.alternativeGroup)for(const other of config.tracks){
      if(other.id!==id && other.alternativeGroup===track.alternativeGroup)mixer.muted.add(other.id);
    }
  }else mixer.muted.add(id);
  mixer.updateGains();
}
function reflect() {
  for(const track of config.tracks){
    const row=document.querySelector(`[data-track="${track.id}"]`);
    if(!row)continue;
    row.classList.toggle('silent',!mixer.audible(track.id));
    const on=!mixer.muted.has(track.id);
    row.querySelector('.sound-toggle').setAttribute('aria-checked',on);
    row.querySelector('.toggle-label').textContent=on?'On':'Off';
    row.querySelector('.solo').setAttribute('aria-pressed',mixer.solo.has(track.id));
  }
  $('play').textContent=mixer.playing?'Pause':'Play';
}
function draw() {
  $('tracks').replaceChildren();
  for(const track of config.tracks){
    const row=document.createElement('article');row.className='track';row.dataset.track=track.id;
    const title=document.createElement('h3');title.textContent=track.name;
    const wave=document.createElement('div');wave.className='wave';wave.title='Click to seek';
    const values=track.waveform, peak=Math.max(...values,.00001), last=values.length-1;
    const points=values.map((v,i)=>`${i},${15-Math.sqrt(v/peak)*14}`).join(' ')+' '+values.map((v,i)=>`${last-i},${15+Math.sqrt(values[last-i]/peak)*14}`).join(' ');
    wave.innerHTML=`<svg viewBox="0 0 ${last} 30" preserveAspectRatio="none" aria-hidden="true"><polygon points="${points}" fill="currentColor"/></svg><span class="cursor"></span>`;
    wave.onclick=e=>seek((e.clientX-wave.getBoundingClientRect().left)/wave.clientWidth*config.duration).catch(showError);
    const controls=document.createElement('div');controls.className='track-controls';
    const toggle=document.createElement('button');toggle.className='sound-toggle';toggle.setAttribute('role','switch');toggle.setAttribute('aria-label',`Sound on/off ${track.name}`);
    toggle.innerHTML='<span class="switch" aria-hidden="true"></span><span class="toggle-label"></span>';
    toggle.onclick=()=>{setEnabled(track.id,mixer.muted.has(track.id));reflect();};
    const only=document.createElement('button');only.className='solo';only.textContent='Only';only.setAttribute('aria-label',`Only ${track.name}`);
    only.onclick=()=>{mixer.isolate(track.id);reflect();};
    controls.append(toggle,only);row.append(title,wave,controls);$('tracks').append(row);
  }
  reflect();
}
async function seek(value){await mixer.seek(value);reflect();}
$('play').onclick=async()=>{try{if(mixer.playing)mixer.pause();else await mixer.play();reflect();}catch(e){showError(e);}};
$('restart').onclick=()=>seek(0).catch(showError);
$('seek').max=config.duration;
$('seek').oninput=()=>seek(Number($('seek').value)).catch(showError);
$('loop').onchange=()=>mixer.setLoop($('loop').checked);
$('volume').oninput=()=>mixer.output.gain.setTargetAtTime(Number($('volume').value),context.currentTime,.01);
$('reset').onclick=()=>{resetMix();reflect();};
document.addEventListener('keydown',e=>{if(e.code==='Space'&&!['INPUT','TEXTAREA','SELECT','BUTTON'].includes(e.target.tagName)){e.preventDefault();$('play').click();}});
function tick(){
  const position=mixer.position();$('seek').value=position;$('time').textContent=`${stamp(position)} / ${stamp(config.duration)}`;
  document.querySelectorAll('.cursor').forEach(c=>c.style.left=`${position/config.duration*100}%`);
  if(mixer.playing&&!mixer.loop&&position>=config.duration){mixer.pause();reflect();}
  requestAnimationFrame(tick);
}
async function post(path,payload){
  const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const result=await r.json();if(!r.ok)throw Error(result.error||'Player connection failed');return result;
}
function snapshot(){return {
  ready,playing:mixer.playing,time:mixer.position(),duration:config.duration,loop:mixer.loop,volume:Number($('volume').value),
  only:[...mixer.solo][0]||null,error:lastError,
  tracks:config.tracks.map(t=>({id:t.id,name:t.name,enabled:!mixer.muted.has(t.id),audible:mixer.audible(t.id)})),
};}
async function apply(command){
  switch(command.action){
    case 'play':if(context.state==='suspended' && !navigator.userActivation.hasBeenActive)throw Error('Press Play once to allow audio in this browser');await mixer.play();if(context.state!=='running')throw Error('Press Play once to allow audio in this browser');break;
    case 'pause':mixer.pause();break;
    case 'seek':await mixer.seek(command.value);break;
    case 'only':mixer.solo.clear();if(command.track)mixer.solo.add(command.track);mixer.updateGains();break;
    case 'enabled':setEnabled(command.track,command.value);break;
    case 'reset':resetMix();break;
    case 'volume':$('volume').value=command.value;$('volume').oninput();break;
    case 'loop':$('loop').checked=command.value;mixer.setLoop(command.value);break;
  }
  reflect();
}
async function sync(){
  try {
    const result=await post('/api/sync',{session,lastCommand,state:snapshot()});
    for(const command of result.commands){
      try{lastError=null;$('status').textContent='';await apply(command);}catch(e){showError(e);}
      lastCommand=command.sequence;
    }
    setTimeout(sync,350);
  } catch(e){showError(e);}
}
try {
  $('status').textContent='Loading sounds…';
  const entries=await Promise.all(config.tracks.map(async track=>{
    const r=await fetch(track.url);if(!r.ok)throw Error(`Could not load ${track.name}`);
    const buffer=await context.decodeAudioData(await r.arrayBuffer());
    if(Math.abs(buffer.duration-config.duration)>.001)throw Error(`Wrong length for ${track.name}`);
    return [track.id,buffer];
  }));
  mixer.buffers=Object.fromEntries(entries);mixer.paletteGain=config.gain;resetMix();draw();
  session=(await post('/api/connect',{})).session;
  ready=true;$('play').disabled=false;$('status').textContent='';sync();tick();
}catch(e){showError(e);}
window.addEventListener('pagehide',()=>mixer.pause());
