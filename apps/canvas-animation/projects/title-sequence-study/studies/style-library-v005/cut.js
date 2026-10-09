/* A silent same-word timing proof, not a selected film storyboard. */
window.TypeCut=(()=>{
  const FPS=24,WORD='SHIFT',shots=[];
  const add=(id,state,frames,opts={})=>shots.push({id,state,frames,...opts});
  // Held flat shapes establish scale, followed by an empty frame interval.
  add('monolith',1,36);add(null,0,6);add('wire',0,24,{scale:.66});add(null,0,6);
  // The geometry stays fixed while its native material changes.
  add('tube',0,24);add('tube',1,8);add('tube',2,24);add('tube',3,16);
  add('marquee',0,24);add('marquee',2,24);add(null,0,4);
  // Construction changes begin to outpace the word.
  for(const [id,state]of [['overprint',2],['ribbon',0],['slats',1],['modular',0],['relic',0],['wingline',3],['palace',1],['depth',0]])add(id,state,8);
  add('stack',1,14);add('pinboard',1,8);add(null,0,4);
  for(const [id,state]of [['monolith',2],['orbital',1],['slats',2],['marquee',2],['overprint',0],['tube',2],['ribbon',3],['depth',3],['stack',0],['modular',3],['relic',2],['wingline',2]])add(id,state,4);
  for(const [id,state]of [['depth',0],['slats',1],['palace',2],['overprint',3],['pinboard',3],['stack',1],['modular',1],['tube',0],['marquee',3],['ribbon',2],['chrome',3],['monolith',0]])add(id,state,2);
  add(null,0,6);add('wire',0,24,{scale:.42});add(null,0,12);
  let cursor=0;for(const shot of shots){shot.start=cursor;cursor+=shot.frames;shot.end=cursor}
  function render(frame,target,{word=WORD,label=false}={}){
    const f=Math.max(0,Math.min(cursor-1,Math.floor(frame))),shot=shots.find(x=>f>=x.start&&f<x.end),g=target.getContext('2d');g.fillStyle='#030305';g.fillRect(0,0,target.width,target.height);
    if(shot.id){const art=TypeLibrary.canvas();TypeLibrary.render(shot.id,word,shot.state,f-shot.start,art);const s=shot.scale||1;g.drawImage(art,640*(1-s),360*(1-s),1280*s,720*s)}
    if(label){g.fillStyle='#17171b';g.fillRect(0,720,1280,48);g.font='17px system-ui';g.fillStyle='#eee';g.fillText(`${(f/FPS).toFixed(2)} s · ${shot.id||'black pause'} · ${shot.frames} frames`,20,752)}
    return shot;
  }
  return {FPS,WORD,shots,frames:cursor,duration:cursor/FPS,render};
})();
