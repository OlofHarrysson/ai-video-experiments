/* A silent graphic study: fixed compositions, construction events and cuts.
   No camera drift, full-frame flashes, stochastic effects or soundtrack. */
window.LetteringShots=[
 {id:'machine',frames:10,view:'wild',mode:'flat',ink:'#f1f5ed',label:'WILD / first reading'},
 {id:'tuscan',frames:10,view:'hours',mode:'register',event:'register',label:'HOURS / registration'},
 {id:'liquid',frames:8,view:'liquid-counter',event:'flow',label:'Counter / contour flow'},
 {id:'machine',frames:16,event:'assemble',label:'Mechanical assembly'},
 {id:'script',frames:6,mode:'flat',ink:'#ff3a12',layout:{scale:.82,x:-210},label:'Red silhouette / left'},
 {id:'script',frames:18,event:'light',layout:{scale:.82,x:-210},label:'Enamel / left light pass'},
 {id:'tuscan',frames:14,view:'wild',mode:'register',event:'register',layout:{scale:.80,x:140,y:-160},label:'WILD / upper register'},
 {id:'machine',frames:10,mode:'wire',event:'wire',label:'Wire planes opening'},
 {id:'liquid',frames:16,event:'flow',label:'Psychedelic full reading'},
 {id:'hybrid',frames:18,event:'scan',label:'Dots / script overlap'},
 {id:'tuscan',frames:8,view:'diamond',mode:'flat',ink:'#fff0d1',label:'Diamond counter'},
 {id:'tuscan',frames:18,mode:'register',event:'register',label:'Printed title reading'},
 {id:'machine',frames:6,view:'machine-stem',mode:'flat',ink:'#b9fb08',label:'Angular detail'},
 {id:'script',frames:6,view:'script-swash',mode:'outline',ink:'#ffc64a',label:'Swash / gold outline'},
 {id:'machine',frames:8,view:'wild',mode:'flat',ink:'#d2ff0b',layout:{scale:1.0,x:180},label:'WILD / right flat'},
 {id:'machine',frames:12,view:'wild',mode:'wire',event:'wire',layout:{scale:1.0,x:180},label:'WILD / right wire'},
 {id:'liquid',frames:8,view:'liquid-d',event:'flow',label:'D / flowing detail'},
 {id:'script',frames:12,view:'script-hours',mode:'flat',ink:'#ffe6b2',label:'HOURS / small reading'},
 {id:'tuscan',frames:8,view:'hours',label:'HOURS / engraved accent'},
 {id:'script',frames:28,event:'light',label:'Final held hero'}
];
window.LetteringEdit=(()=>{
 const shots=LetteringShots;let end=0;for(const s of shots){s.start=end;end+=s.frames;s.end=end;}
 const views={
  wild:{scale:1.22,focus:[384,143],row:'wild'},
  hours:{scale:1.22,focus:[384,347],row:'hours'},
  tiny:{scale:.32},
  'script-swash':{scale:2.3,focus:[397,407]},
  diamond:{scale:3.4,focus:[273,325]},
  'machine-stem':{scale:3.1,focus:[250,190]},
  'liquid-counter':{scale:2.25,focus:[311,334]},
  'liquid-d':{scale:2.4,focus:[560,139]},
  'script-hours':{scale:.53,focus:[384,317],row:'hours',x:340,y:150}
 };
 function sample(target,s,n){
  const progress=Math.min(1,n/Math.max(1,s.frames-1)),phase=['flow','light','wire','scan'].includes(s.event)?progress:s.event==='register'?Math.min(1,n/7):.25;
  if(s.id==='hybrid'){LetteringArt.hybrid(target,phase);return;}
  const options={...(views[s.view]||{}),...(s.layout||{}),mode:s.mode||'material',ink:s.ink||'#fff',assembly:s.event==='assemble'?Math.min(1,Math.floor(n/2)*2/8):1};
  if(s.view==='wild')options.focus=[384,s.id==='machine'?167:135];
  if(s.view==='hours')options.focus=[384,s.id==='machine'?325:347];
  LetteringArt.card(target,s.id,phase,options);
 }
 function draw(target,frame){
  const f=((Math.floor(frame)%end)+end)%end,s=shots.find(s=>f<s.end),n=f-s.start;
  sample(target,s,n);
  return {frame:f,shot:shots.indexOf(s),label:s.label,progress:n/Math.max(1,s.frames-1)};
 }
 return {draw,shots,frames:end,fps:24,views};
})();
