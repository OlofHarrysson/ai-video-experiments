(() => {
 const canvas=document.querySelector('#art'),play=document.querySelector('#play'),seek=document.querySelector('#seek'),select=document.querySelector('#card');
 let playing=false,frame=0,origin=0,handle;
 for(const card of Editorial.cards)select.append(new Option(card.name,card.id));
 function draw(){try{
  if(select.value){Editorial.card(canvas,select.value,(frame%24)/23);document.querySelector('#description').textContent=Editorial.cards.find(c=>c.id===select.value).reason;}
  else {Editorial.draw(canvas,frame);document.querySelector('#description').textContent='';}
  seek.value=frame;document.querySelector('#time').value=(frame/24).toFixed(2)+' s';
 }catch(e){document.querySelector('#error').textContent=e.message;throw e;}}
 function tick(now){if(!playing)return;frame=Math.floor((now-origin)*24/1000)%288;draw();handle=requestAnimationFrame(tick);}
 function stop(){playing=false;cancelAnimationFrame(handle);play.textContent='Play';}
 play.onclick=()=>{if(playing)stop();else{playing=true;play.textContent='Pause';origin=performance.now()-frame/24*1000;handle=requestAnimationFrame(tick);}};
 seek.oninput=()=>{stop();frame=Number(seek.value);draw();};
 select.onchange=()=>{stop();frame=12;draw();};
 document.querySelector('#save').onclick=()=>canvas.toBlob(blob=>{const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=`make-it-move-${select.value||frame}.png`;a.click();setTimeout(()=>URL.revokeObjectURL(url),500);});
 draw();window.ready=true;
})();
