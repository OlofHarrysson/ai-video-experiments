(() => {
  const $ = id => document.getElementById(id), form=$('plan'), video=$('video');
  const query=new URLSearchParams(location.search), source=query.get('source'), frame=Number(query.get('frame'));
  let summary=null, activeId=null, busy=false, epoch=0;
  async function api(path, body) {
    const response=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const result=await response.json();if(!response.ok)throw new Error(result.error||'Request failed');return result;
  }
  function status(text,error=false){$('status').textContent=text;$('status').classList.toggle('error',error);}
  function invalidate(){epoch++;activeId=null;$('save').disabled=true;$('saved').textContent='';if(summary){video.pause();$('play').textContent='Play';status('Settings changed. Preview again before saving.');$('phase').textContent='Previous preview · settings changed';}}
  form.addEventListener('input',invalidate);
  function inputs(){const data={source,frame};for(const [key,value] of new FormData(form))data[key]=['intent','prompt'].includes(key)?value:Number(value);data.match_speed=form.elements.match_speed.checked;return data;}
  function controls(){const f=Math.min(summary.frame_count-1,Math.floor(video.currentTime*24+1e-5));$('scrub').value=f;$('position').textContent=`${(f/24).toFixed(3)} s`;$('phase').textContent=activeId?(f/24<summary.lead_seconds?'Original lead-in':'Proposed motion · no diffusion'):'Previous preview · settings changed';$('play').textContent=video.paused?'Play':'Pause';}
  function seek(f){if(!summary)return;video.pause();const index=Math.max(0,Math.min(summary.frame_count-1,f));video.currentTime=(index+.5)/24;controls();}
  $('scrub').addEventListener('input',()=>seek(Number($('scrub').value)));
  $('back').onclick=()=>seek(Number($('scrub').value)-1);$('forward').onclick=()=>seek(Number($('scrub').value)+1);
  $('play').onclick=async()=>{if(video.paused){if(video.ended)video.currentTime=0;try{await video.play();}catch(e){status(e.message,true);}}else video.pause();controls();};
  video.addEventListener('timeupdate',()=>summary&&controls());video.addEventListener('ended',()=>summary&&controls());
  video.addEventListener('error',()=>{activeId=null;$('save').disabled=true;status('Preview could not be decoded. Render a fresh preview.',true);});
  document.addEventListener('keydown',event=>{if(!summary||event.target.closest('input,textarea,select,button,a,summary')||event.altKey||event.ctrlKey||event.metaKey)return;if(event.key==='ArrowLeft'||event.key==='ArrowRight'){event.preventDefault();seek(Number($('scrub').value)+(event.key==='ArrowRight'?1:-1));}if(event.code==='Space'){event.preventDefault();$('play').click();}});
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(busy)return;busy=true;const version=epoch;activeId=null;$('save').disabled=true;$('preview').disabled=true;video.pause();status('Rendering with the same spatial transforms as generation…');
    try{const result=await api('/api/branch/preview',inputs());if(epoch!==version){status('Settings changed during rendering. Preview again.');return;}summary=result;activeId=result.id;video.src=result.preview_url;
      await new Promise((resolve,reject)=>{video.onloadeddata=resolve;video.onerror=()=>reject(new Error('Cannot load preview'));video.load();});
      if(epoch!==version){activeId=null;status('Settings changed during loading. Preview again.');return;}
      $('painting').hidden=true;video.hidden=false;for(const id of ['play','back','forward','scrub'])$(id).disabled=false;
      $('scrub').max=result.frame_count-1;$('save').disabled=false;
      $('timing').replaceChildren();for(const label of [`Original lead-in: ${result.lead_seconds.toFixed(2)}s`,`Branch: ${result.lead_seconds.toFixed(2)}s`,`Move: ${result.duration.toFixed(2)}s`,`New text + noise ${form.elements.noise.value}: first painting +${result.timeline[0].after.toFixed(2)}s`]){const span=document.createElement('span');span.textContent=label;$('timing').append(span);}
      $('diagnostics').textContent=`Scale range ${result.zoom_min.toFixed(2)}–${result.zoom_max.toFixed(2)}×; finishes at ${result.zoom_end.toFixed(2)}×.\n${result.warnings.join('\n')}`;
      status('Preview ready. Saving creates a new draft; it does not run diffusion.');controls();
    }catch(e){activeId=null;status(e.message,true);}finally{busy=false;$('preview').disabled=false;}
  });
  $('save').onclick=async()=>{if(!activeId||busy)return;busy=true;$('save').disabled=true;try{const saved=await api('/api/branch/save',{id:activeId});$('saved').textContent=`Saved ${saved.paintings_preserved} original paintings and a continuation draft:\n${saved.path}\nNo diffusion has been generated.`;status('Branch saved. The original film is unchanged.');}catch(e){status(e.message,true);$('save').disabled=false;}finally{busy=false;}};
  async function start(){try{if(!source||!Number.isInteger(frame))throw new Error('Choose a painting from the reviewer.');const s=await api(`/api/branch/source?${new URLSearchParams({source,frame})}`);$('selection').textContent=`Branch at ${s.display_seconds.toFixed(3)} s · frame ${s.display_frame}`;$('source-time').textContent=`Saved painting at source frame ${s.source_frame}. Timing shown here is playback time.`;$('snap').textContent=s.snapped?`Frame ${frame} is between paintings. Using the earlier saved painting at frame ${s.display_frame}.`:'';form.elements.prompt.value=s.prompt;form.elements.noise.value=s.noise.toFixed(3);$('painting').src=`/api/branch/painting?${new URLSearchParams({source,frame})}`;$('preview').disabled=false;$('timing').textContent='Preview includes up to one second of the original film before this painting.';}catch(e){status(e.message,true);}}
  start();
})();
