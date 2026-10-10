/* Style frames only. The approved storyboard will own animation and timing. */
window.KeepUpArt=(()=>{
 const shapes=Object.fromEntries(LetteringData.assets.map(a=>[a.id,Lettering.prepare(a)]));
 const words=Object.fromEntries(Object.entries(TypeOutlines).map(([k,v])=>[k,{...v,path:new Path2D(v.d)}]));
 const colors={black:'#08080b',ivory:'#fff2d3',acid:'#e3ff46',blue:'#254cff',coral:'#ff553c',pink:'#f936a1'};
 function placed(g,shape,box,fn){
  const [x,y,w,h]=shape.bounds,s=Math.min(box[2]/w,box[3]/h);
  g.save();g.translate(box[0]+(box[2]-w*s)/2,box[1]+(box[3]-h*s)/2);g.scale(s,s);g.translate(-x,-y);fn(shape,s);g.restore();
 }
 function text(g,id,box,ink=colors.ivory){placed(g,words[id],box,s=>{g.fillStyle=ink;g.fill(s.path)});}
 function keep(g,box){placed(g,shapes.keep,box,a=>{
  g.lineJoin='round';g.save();g.translate(14,20);g.fillStyle='#263bff';g.fill(a.path);g.restore();
  g.fillStyle='#fff2bc';g.fill(a.path);
  g.save();g.clip(a.path);
  for(const [width,color] of [[92,'#ffd130'],[62,'#ff8118'],[35,'#ff4738'],[13,'#e6298b']]){g.strokeStyle=color;g.lineWidth=width;g.stroke(a.path);}
  g.restore();
 });}
 function money(g,box){placed(g,shapes.money,box,a=>{
  g.lineJoin='round';g.save();g.translate(9,11);g.fillStyle=colors.blue;g.fill(a.path);g.restore();
  g.strokeStyle=colors.coral;g.lineWidth=13;g.stroke(a.path);g.fillStyle=colors.ivory;g.fill(a.path);
  g.save();g.clip(a.path);g.strokeStyle=colors.coral;g.lineWidth=8;g.stroke(a.path);g.restore();
 });}
 function breakthrough(g,box){placed(g,shapes.break,box,a=>{
  a.parts.forEach((part,i)=>{
   g.save();const shift=i===0?9:i===10?-8:0;g.translate(shift,-shift);
   g.save();g.translate(12,14);g.fillStyle=colors.blue;g.fill(part.path);g.restore();
   g.fillStyle=part.bounds[1]<550?(i%4===0?colors.ivory:colors.acid):colors.ivory;g.fill(part.path);g.restore();
  });
 });}
 const descriptions=[
  {id:'opening',label:'01 · The promise',time:'0–2 s',copy:'AI / EVERYTHING JUST CHANGED',motion:'Active opening. The announcement arrives in crisp word cuts.'},
  {id:'breakthrough',label:'02 · The next announcement',time:'2–5 s',copy:'BREAKTHROUGH / AGAIN',motion:'Angular parts lock together; AGAIN interrupts the resolved word.'},
  {id:'money',label:'03 · The money',time:'5–8 s',copy:'$40B / OPENAI · FUNDING ANNOUNCED · MAR 2025',motion:'Four grouped characters settle into a held, dated funding card.'},
  {id:'overload',label:'04 · The feed',time:'8–12 s',copy:'MORE / FASTER / NEXT / AGAIN',motion:'Short repeated calls, intercut with previous identities; quarter-second accents.'},
  {id:'question',label:'05 · The human turn',time:'12–14 s',copy:'AM I ALREADY BEHIND?',motion:'The busy layout cuts to a sparse, readable question.'},
  {id:'title',label:'06 · The command',time:'14–18 s',copy:'KEEP UP / A FILM ABOUT ARTIFICIAL INTELLIGENCE',motion:'Two words land independently; contour color moves within a stable composition.'}
 ];
 function draw(canvas,id){
  const g=canvas.getContext('2d');g.save();g.setTransform(canvas.width/1600,0,0,canvas.height/900,0,0);
  g.fillStyle=colors.black;g.fillRect(0,0,1600,900);
  if(id==='opening'){
   g.fillStyle=colors.blue;g.fillRect(0,0,1600,900);
   text(g,'ai',[155,75,1290,570]);
   text(g,'everything',[155,720,1290,77]);
  }else if(id==='breakthrough'){
   text(g,'again',[1150,60,340,64],colors.coral);
   breakthrough(g,[86,170,1428,590]);
  }else if(id==='money'){
   money(g,[105,145,1390,520]);
   text(g,'funding',[235,755,1130,45]);
  }else if(id==='overload'){
   text(g,'more',[72,35,760,232],colors.coral);
   text(g,'faster',[240,292,1280,245],colors.acid);
   text(g,'next',[76,557,920,268],colors.blue);
   text(g,'again',[1090,701,418,90],colors.ivory);
  }else if(id==='question'){
   text(g,'am-i',[140,127,283,91],colors.pink);
   text(g,'already',[140,300,770,120]);
   text(g,'behind',[132,478,1310,223]);
  }else if(id==='title'){
   keep(g,[135,75,1330,655]);
   text(g,'subtitle',[330,814,940,37]);
  }else throw Error('Unknown frame '+id);
  g.restore();return canvas;
 }
 return {draw,descriptions,shapes};
})();
