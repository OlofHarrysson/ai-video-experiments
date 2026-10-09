/* Original compound lettering. Sample language, not a film-theme decision. */
window.DesignStudy=(()=>{
 const W=1280,H=544,TAU=Math.PI*2;
 const make=()=>Object.assign(document.createElement('canvas'),{width:W,height:H});
 const random=n=>{const x=Math.sin(n*113.71+73.1)*43758.5453;return x-Math.floor(x)};
 const clamp=x=>Math.max(0,Math.min(1,x));
 function gradient(g,stops){return {stops}}
 function paint(g,fill,h){if(!fill?.stops)return fill;const a=g.createLinearGradient(0,0,0,h);fill.stops.forEach(([p,c])=>a.addColorStop(p,c));return a}
 function text(g,word,x,y,w,h,font,{fill='#fff',stroke=null,lw=1}={}){
  g.save();const prefix=font.match(/^(bold|italic) /)?.[0]||'';g.font=`${prefix}200px ${font.slice(prefix.length)}`;const m=g.measureText(word),mw=m.actualBoundingBoxLeft+m.actualBoundingBoxRight,mh=m.actualBoundingBoxAscent+m.actualBoundingBoxDescent;
  g.translate(x,y);g.scale(w/mw,h/mh);g.lineJoin='round';
  if(stroke){g.strokeStyle=stroke;g.lineWidth=lw;g.strokeText(word,m.actualBoundingBoxLeft,m.actualBoundingBoxAscent)}
  if(fill){g.fillStyle=paint(g,fill,mh);g.fillText(word,m.actualBoundingBoxLeft,m.actualBoundingBoxAscent)}g.restore();
 }
 function star(g,x,y,r,color,rot=0){g.save();g.translate(x,y);g.rotate(rot);g.beginPath();for(let i=0;i<8;i++){const a=i*TAU/8,rr=i%2?r*.13:r;g.lineTo(Math.cos(a)*rr,Math.sin(a)*rr)}g.closePath();g.fillStyle=color;g.fill();g.restore()}
 const names=['Night Fever · lacquer script','Overload · engineered lettering','All at Once · optical overprint'];
 const plates=new Map();
 function nightLayer(g,dx,dy,fill,stroke,lw){g.save();g.translate(640+dx,272+dy);g.rotate(-.075);g.translate(-640,-272);
   text(g,'Night',60,28,856,284,'"Snell Roundhand"',{fill,stroke,lw});
   text(g,'Fever',393,244,799,237,'"Snell Roundhand"',{fill,stroke,lw});
   // The lead-in grows into the N; the terminal follows the r exit stroke.
   g.beginPath();g.moveTo(120,202);g.bezierCurveTo(-16,273,55,445,254,380);g.bezierCurveTo(350,349,311,279,216,335);g.bezierCurveTo(167,363,219,407,339,389);
   g.moveTo(1119,446);g.bezierCurveTo(1237,446,1260,335,1144,319);g.bezierCurveTo(1085,310,1082,346,1121,357);
   g.strokeStyle=stroke||fill;g.lineWidth=lw?Math.max(3,lw*.8):7;g.lineCap='round';g.stroke();g.restore();}
 function script(g,variant=0){
  // Both words and their connecting strokes form one diagonal silhouette.
  const draw=(dx,dy,fill,stroke,lw)=>nightLayer(g,dx,dy,fill,stroke,lw);
  // Offset mass, broad dark separator, pale bevel and colored lacquer face.
  for(let i=19;i>0;i--)draw(i*.7,i*.7,'#302758','#302758',7);
  draw(0,0,null,'#08060e',18);draw(0,0,null,'#eb94c6',12);draw(-2,-2,null,'#fae8cf',8);
  draw(0,0,gradient(g,[[0,'#fff1d5'],[.2,'#ffdbef'],[.38,'#b21e6f'],[.48,'#ffb1d8'],[.57,'#611b53'],[.73,'#e54a9d'],[1,'#fbcce5']]),'#f3a8d3',1.5);
  for(const [x,y,r] of [[225,131,26],[751,80,20],[906,304,19],[1157,444,17]]){star(g,x,y,r,'#ffe9d6',.12);star(g,x,y,r*.42,'#fff')}
  // Sparse stars reinforce the diagonal, rather than surrounding a centered word.
  for(let i=0;i<24;i++){const x=55+random(i)*1170,y=35+random(i+50)*470;if((x>850&&y<200)||(x<390&&y>260))star(g,x,y,2+random(i+90)*5,i%2?'#bf538e':'#695a99',i)}
  if(variant){g.globalCompositeOperation='screen';g.fillStyle='#fd466528';g.fillRect(0,Math.floor(variant)*71%480,1280,24);g.globalCompositeOperation='source-over'}
 }
 const glyph={
  O:'M20 0H80Q100 0 100 22V118Q100 140 80 140H20Q0 140 0 118V22Q0 0 20 0ZM31 26Q24 26 24 34V106Q24 114 31 114H69Q76 114 76 106V34Q76 26 69 26Z',
  V:'M0 0H27L50 104L73 0H100L66 140H34Z',
  E:'M0 0H100V27H27V55H83V82H27V113H100V140H0Z',
  R:'M0 0H76Q100 0 100 24V57Q100 80 75 80L103 140H72L46 82H27V140H0ZM27 26V57H67Q75 57 75 49V34Q75 26 67 26Z',
  L:'M0 0H28V111H100V140H0Z',
  A:'M0 140V25L23 0H77L100 25V140H73V91H27V140ZM27 64H73V32L65 25H35L27 32Z',
  D:'M0 0H70L100 29V111L70 140H0ZM28 27V113H59L74 97V43L59 27Z',
 };
 function engineered(g,variant=0){
  const draw=(ox,oy,fill,stroke,width)=>{g.save();g.translate(67+ox,48+oy);g.transform(1,0,-.065,1,0,0);
   ['OVER','LOAD'].forEach((word,row)=>[...word].forEach((ch,i)=>{g.save();g.translate(i*291+(row?12:0),row*235);g.scale(2.61,1.35);const p=new Path2D(glyph[ch]);g.lineJoin='round';
    if(stroke){g.strokeStyle=stroke;g.lineWidth=width;g.stroke(p)}if(fill){g.fillStyle=paint(g,fill,140);g.fill(p,'evenodd')}
    g.restore()}));g.restore()};
  for(let i=13;i>0;i--)draw(i,i*.5,'#64080d','#64080d',7);
  draw(0,0,null,'#ed1430',12);draw(0,0,null,'#040307',8);draw(0,0,null,'#fff2d6',5.2);
  draw(0,0,gradient(g,[[0,'#fff2d3'],[.22,'#709aa1'],[.42,'#faf5da'],[.47,'#13191c'],[.53,'#81989d'],[.66,'#e3eee1'],[.72,'#171e24'],[1,'#d1e1db']]),'#bffff8',1.1);
  draw(0,0,null,'#13242a',.4);
  // Inlaid channels follow the letter edges, including counters, instead of floating above them.
  g.save();g.translate(67,48);g.transform(1,0,-.065,1,0,0);
  ['OVER','LOAD'].forEach((word,row)=>[...word].forEach((ch,i)=>{g.save();g.translate(i*291+(row?12:0),row*235);g.scale(2.61,1.35);const p=new Path2D(glyph[ch]);g.clip(p,'evenodd');g.lineJoin='round';
   for(const [color,width] of [['#15252d',10],['#daeede',8],['#7e1821',5.7],['#0b1418',4.2]]){g.strokeStyle=color;g.lineWidth=width;g.stroke(p)}
   g.restore()}));g.restore();
  g.fillStyle='#ff253f';g.fillRect(609,245,213,10);g.fillRect(70,260,390,5);g.fillRect(870,260,340,5);
  text(g,'SYSTEM AT CAPACITY',474,250,349,15,'"Helvetica Neue"',{fill:'#fff0d7'});
  // Two tiny registration cuts balance the enormous letter mass.
  for(const x of [35,1245]){g.strokeStyle='#ef3044';g.lineWidth=2;g.beginPath();g.moveTo(x,231);g.lineTo(x,278);g.stroke()}
  if(variant){g.save();g.globalCompositeOperation='screen';g.fillStyle='#f6001825';g.fillRect(0,0,W,H);g.restore()}
 }
 const dotMask=make();
 function overprint(g,variant=0){
  g.fillStyle='#e62b20';g.fillRect(0,0,W,H);
  // Oversized optical lettering provides texture and structure, rather than wallpaper.
  const m=dotMask.getContext('2d');m.clearRect(0,0,W,H);text(m,'ALL',32,-10,811,278,'bold "Rockwell"');text(m,'ONCE',20,251,1280,310,'bold "Rockwell"');
  const d=m.getImageData(0,0,W,H).data;
  for(let y=7;y<H;y+=14)for(let x=7;x<W;x+=14)if(d[(y*W+x)*4+3]>128){g.strokeStyle='#ffdc94';g.lineWidth=2.4;g.beginPath();g.arc(x,y,5.4,0,TAU);g.stroke()}
  // A solid letter mass collides with the open circle field.
  text(g,'ALL',32,-10,811,278,'bold "Rockwell"',{fill:null,stroke:'#ffdc94',lw:.65});
  text(g,'ONCE',2,258,1264,271,'bold "Rockwell"',{fill:'#111516',stroke:'#f3e8cd',lw:2});
  g.save();g.translate(645,251);g.rotate(-.19);g.translate(-645,-251);
  text(g,'at',615,157,188,124,'italic "Didot"',{fill:'#ffdc30',stroke:'#e62b20',lw:7});
  text(g,'Everything',230,218,837,130,'"Snell Roundhand"',{fill:'#ffeea2',stroke:'#b70c21',lw:7});g.restore();
  text(g,'TOO MUCH',883,46,299,48,'"Impact"',{fill:'#171717'});
  text(g,'IS NEVER ENOUGH',882,108,302,26,'"Helvetica Neue"',{fill:'#171717'});
  // Clipped print shadows echo word edges and keep the layout asymmetrical.
  g.strokeStyle='#ffe042';g.lineWidth=2;g.beginPath();g.moveTo(872,149);g.lineTo(1200,149);g.stroke();
  if(variant){g.globalCompositeOperation='multiply';g.fillStyle='#ffddaad0';g.fillRect(0,0,W,H);g.globalCompositeOperation='source-over'}
 }
 const draw=[script,engineered,overprint];
 function plate(id,v=0){const key=id+':'+v;if(!plates.has(key)){const c=make(),g=c.getContext('2d');g.fillStyle='#030305';g.fillRect(0,0,W,H);draw[id](g,v);plates.set(key,c)}return plates.get(key)}
 function render(id,t,c,still=false){const g=c.getContext('2d');g.resetTransform();g.globalCompositeOperation='source-over';g.globalAlpha=1;g.fillStyle='#030305';g.fillRect(0,0,W,H);
  if(still){g.drawImage(plate(id),0,0);return}
  // Discrete design states and impacts, with holds. No ambient sine-wave wobble.
  const frame=Math.floor(t*24),phase=frame<12?0:frame<25?1:frame<37?2:frame<49?3:frame<57?4:5;
  if(id===0){const scale=[1,1.13,1,1.07,1.25,1][phase],x=[0,-49,0,30,-110,0][phase],y=[0,21,0,-12,50,0][phase];g.translate(640+x,272+y);g.scale(scale,scale);g.drawImage(plate(id,phase===3?1:0),-640,-272)}
  if(id===1){const split=[0,36,-18,0,72,0][phase];const p=plate(id,phase===4?1:0);g.drawImage(p,0,0,W,272,split,0,W,272);g.drawImage(p,0,272,W,272,-split,272,W,272);if(phase===4){g.globalCompositeOperation='screen';g.globalAlpha=.45;g.drawImage(p,-24,0);g.globalAlpha=1;g.globalCompositeOperation='source-over'}}
  if(id===2){const p=plate(id,phase===3?1:0);const zoom=[1,1.05,1,1.12,1.35,1][phase];g.translate(640,272);g.scale(zoom,zoom);g.drawImage(p,-640,-272);if(phase===4){g.globalCompositeOperation='difference';g.fillStyle='#fff1a1';g.fillRect(-640,-272,W,H);g.globalCompositeOperation='source-over'}}
 }
 return {W,H,names,render,nightLayer};
})();
