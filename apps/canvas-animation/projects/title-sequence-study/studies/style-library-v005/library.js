/* Original typography constructions; no reference pixels. Deterministic at any frame. */
window.TypeLibrary = (() => {
  const W=1280,H=720,TAU=Math.PI*2;
  const canvas=()=>Object.assign(document.createElement('canvas'),{width:W,height:H});
  const noise=n=>{const a=Math.sin(n*127.1+311.7)*43758.5453;return a-Math.floor(a)};
  const gradient=(g,y,h,stops)=>{const a=g.createLinearGradient(0,y,0,y+h);stops.forEach(([p,c])=>a.addColorStop(p,c));return a};
  function text(g,word,x,y,w,h,font='Anton',fill='#fff',stroke=null,lw=1){
    if(!word.trim())return;
    g.save();g.font=`${font==='Cormorant'?'700 ':''}200px ${font}`;const m=g.measureText(word),mw=m.actualBoundingBoxLeft+m.actualBoundingBoxRight,mh=m.actualBoundingBoxAscent+m.actualBoundingBoxDescent;
    g.translate(x,y);g.scale(w/mw,h/mh);g.lineJoin='round';g.textBaseline='alphabetic';
    if(stroke){g.lineWidth=lw;g.strokeStyle=stroke;g.strokeText(word,m.actualBoundingBoxLeft,m.actualBoundingBoxAscent)}
    if(fill){g.fillStyle=fill;g.fillText(word,m.actualBoundingBoxLeft,m.actualBoundingBoxAscent)}g.restore();
  }
  const masks=new Map();
  function mask(word,font,x,y,w,h){const key=[word,font,x,y,w,h].join('|');if(!masks.has(key)){const c=canvas();text(c.getContext('2d'),word,x,y,w,h,font);masks.set(key,c)}return masks.get(key)}
  const samples=new Map();
  function grid(word,font,box,step){const key=[word,font,...box,step].join('|');if(!samples.has(key)){const m=mask(word,font,...box),d=m.getContext('2d').getImageData(0,0,W,H).data,points=[];for(let y=step/2|0;y<H;y+=step)for(let x=step/2|0;x<W;x+=step)if(d[(y*W+x)*4+3]>180)points.push([x,y]);samples.set(key,points)}return samples.get(key)}
  function line(g,pts,c,w=1,close=false){g.beginPath();pts.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));if(close)g.closePath();g.strokeStyle=c;g.lineWidth=w;g.stroke()}
  function star(g,x,y,r,c,points=4,rot=0){g.beginPath();for(let i=0;i<points*2;i++){const a=i*Math.PI/points+rot,d=i%2?r*.22:r;g.lineTo(x+Math.cos(a)*d,y+Math.sin(a)*d)}g.closePath();g.fillStyle=c;g.fill()}
  function bulb(g,x,y,r,c,lit=true){g.fillStyle=lit?c:'#211712';g.beginPath();g.arc(x,y,r,0,TAU);g.fill();if(lit&&r>2){g.fillStyle='#fff4cf';g.beginPath();g.arc(x-r*.22,y-r*.25,r*.3,0,TAU);g.fill()}}
  function masked(g,m,paint){const c=canvas(),q=c.getContext('2d');paint(q);q.globalCompositeOperation='destination-in';q.drawImage(m,0,0);g.drawImage(c,0,0)}
  function outline(g,word,box,font,c,w=1){text(g,word,...box,font,null,c,w)}
  const families=[];
  function add(id,name,word,states,draw,opts={}){families.push({id,name,word,states,draw,...opts})}

  add('pinboard','01 · Pinboard','PULSE',['Incandescent','Dim pins','Letter wave','Negative matrix'],(g,word,s,f)=>{
    const box=[140,239,1000,240],pts=grid(word,'RubikMono',box,12),phase=Math.floor(f/3);
    if(s===3){const m=mask(word,'RubikMono',...box).getContext('2d').getImageData(0,0,W,H).data;for(let y=215;y<505;y+=12)for(let x=110;x<1170;x+=12){const inside=m[(y*W+x)*4+3]>180;bulb(g,x,y,inside?1.5:3.8,inside?'#502528':'#d63636',!inside)}return}
    for(const [x,y]of pts){const band=Math.floor((x-140)/180),on=s===0||s===2&&(band+phase)%4!==0;bulb(g,x,y,on?4.5:2.0,on?(s===2&&band%2?'#f64532':'#ffbc4a'):'#765044',true)}
    if(s===0){g.globalAlpha=.3;for(let i=0;i<5;i++){g.fillStyle='#ffae2b';g.fillRect(140,240+((phase*12+i*61)%240),1000,1)}g.globalAlpha=1}
  });

  add('slats','02 · Split frequency','SIGNAL',['Horizontal scan','Vertical comb','Offset shutter','Wire interference'],(g,word,s,f)=>{
    const m=mask(word,'Anton',95,176,1090,365),phase=Math.floor(f/2);
    const c=canvas(),q=c.getContext('2d');masked(q,m,z=>{z.fillStyle=['#d9fbf7','#c2c6de','#f52c45','#a2a5ce'][s];if(s===1||s===3){for(let x=0;x<W;x+=s===1?5:8)z.fillRect(x,100,s===1?1:2,530)}else for(let y=0;y<H;y+=s===0?9:18)z.fillRect(0,y,W,s===0?3:9)});
    if(s===2){for(let y=0;y<H;y+=30){const dx=y%90===0?18*Math.sin(phase+y):0;g.drawImage(c,0,y,W,30,dx,y,W,30)}}else{g.drawImage(c,0,0,W,358,0,0,W,358);g.drawImage(c,0,358,W,H-358,s===1?-36:14,358,W,H-358)}
    if(s===3){g.globalCompositeOperation='screen';g.globalAlpha=.55;g.drawImage(c,-7,3);g.globalCompositeOperation='source-over';g.globalAlpha=1}
  });

  function wingPath(g,side,mode=0){
    g.save();g.translate(640,356);g.scale(side,1);
    // Feather roots meet the word edge; tips step along one swept silhouette.
    for(let j=0;j<9;j++){
      const rootX=241+j*1.7,rootY=-16+j*6,tipX=516-j*19,tipY=-135+j*20;
      g.beginPath();g.moveTo(rootX,rootY);
      g.bezierCurveTo(312+j*2,rootY-4,tipX-21,tipY+17,tipX,tipY);
      g.bezierCurveTo(tipX-4,tipY+24,339-j*3,96-j*3,rootX,rootY+13);
      if(mode===2&&j%2===0)g.fill();g.stroke();
    }g.restore();
  }
  add('wingline','03 · Wingline','FLY',['Three-line enamel','Open quills','Hot core','Stamped foil'],(g,word,s,f)=>{
    const col=['#f42970','#8af4e0','#ff6a39','#f8d975'][s],box=[393,285,494,130];g.lineJoin='round';g.lineCap='round';
    for(const [width,c] of [[7,'#08090a'],[4.4,col],[1.5,s===3?'#48215a':'#040408']]){g.lineWidth=width;g.strokeStyle=c;g.fillStyle=c;wingPath(g,1,s===3?2:0);wingPath(g,-1,s===3?2:0);outline(g,word,box,'Audiowide',c,width*1.6)}
    if(s===2)text(g,word,...box,'Audiowide',col);
    if(s===3)text(g,word,...box,'Audiowide',gradient(g,0,180,[[0,'#fff7c6'],[.5,'#d89d42'],[.55,'#70493f'],[1,'#fff3a4']]));
    if(s===1){g.strokeStyle='#040408';g.lineWidth=4;for(let j=0;j<5;j++){line(g,[[125+j*27,250+j*19],[160+j*27,286+j*19]],'#040408',4);line(g,[[1155-j*27,250+j*19],[1120-j*27,286+j*19]],'#040408',4)}}
  });

  add('depth','04 · Depth engine','ECHO',['Spectrum tunnel','Red extrusion','Sparse ghost','White vanishing point'],(g,word,s,f)=>{
    const n=[17,11,4,21][s],phase=Math.floor(f/2)%8;g.lineJoin='miter';
    for(let i=n;i>=0;i--){const k=i===n?1:(i+phase/8)/n,scale=.24+k*.88,x=640-470*scale+(1-k)*80,y=355-137*scale-(1-k)*20;const col=s===0?`hsl(${12+k*210} 100% ${36+k*25}%)`:s===1?(i===n?'#f97665':'#9b132e'):s===2?['#f43577','#7539a9','#214777'][i%3]:`rgb(${100+k*155} ${110+k*145} ${130+k*125})`;g.globalAlpha=s===2?1:.55+k*.45;outline(g,word,[x,y,940*scale,274*scale],'Audiowide',col,i===n?2.6:1.15);}
    g.globalAlpha=1;if(s===1)text(g,word,170,218,1053,307,'Audiowide','#f24e45');
    if(s===3){g.globalAlpha=.3;outline(g,word,[80+phase*3,170,1100,374],'Audiowide','#ae33ec',3);g.globalAlpha=1}
  });

  // A full Latin single-line skeleton; each glyph uses open polylines, not a display-font effect.
  const glyph={A:[[0,140,45,0,90,140],[22,85,68,85]],B:[[0,140,0,0,61,0,90,24,90,45,61,69,0,69],[61,69,94,91,94,116,63,140,0,140]],C:[[90,10,72,0,20,0,0,22,0,118,20,140,72,140,90,130]],D:[[0,0,0,140,62,140,90,112,90,28,62,0,0,0]],E:[[90,0,0,0,0,140,90,140],[0,69,73,69]],F:[[90,0,0,0,0,140],[0,69,73,69]],G:[[90,20,70,0,20,0,0,20,0,120,20,140,90,140,90,75,52,75]],H:[[0,0,0,140],[90,0,90,140],[0,70,90,70]],I:[[0,0,90,0],[45,0,45,140],[0,140,90,140]],J:[[90,0,90,118,68,140,20,140,0,120,0,96]],K:[[0,0,0,140],[90,0,0,85],[30,60,90,140]],L:[[0,0,0,140,90,140]],M:[[0,140,0,0,45,63,90,0,90,140]],N:[[0,140,0,0,90,140,90,0]],O:[[20,0,70,0,90,20,90,120,70,140,20,140,0,120,0,20,20,0]],P:[[0,140,0,0,70,0,90,20,90,53,70,73,0,73]],Q:[[20,0,70,0,90,20,90,120,70,140,20,140,0,120,0,20,20,0],[55,105,100,150]],R:[[0,140,0,0,70,0,90,20,90,53,70,73,0,73],[48,73,98,140]],S:[[90,15,70,0,20,0,0,20,0,48,20,68,70,72,90,92,90,120,70,140,20,140,0,125]],T:[[0,0,90,0],[45,0,45,140]],U:[[0,0,0,120,20,140,70,140,90,120,90,0]],V:[[0,0,45,140,90,0]],W:[[0,0,18,140,45,75,72,140,90,0]],X:[[0,0,90,140],[90,0,0,140]],Y:[[0,0,45,70,90,0],[45,70,45,140]],Z:[[0,0,90,0,0,140,90,140]],' ':[[0,0,0,0]]};
  function wireWord(g,word,x,y,w,h,col,lw,inline=1){g.save();g.translate(x,y);g.scale(w/(word.length*115-25),h/140);g.transform(1,0,-.22,1,30,0);g.strokeStyle=col;g.lineWidth=lw;g.lineCap='square';for(let j=0;j<word.length;j++){for(let k=0;k<inline;k++){g.save();g.translate(j*115+k*5,k*4);for(const a of glyph[word[j]]||[]){g.beginPath();for(let i=0;i<a.length;i+=2)i?g.lineTo(a[i],a[i+1]):g.moveTo(a[i],a[i+1]);g.stroke()}g.restore()}}g.restore()}
  add('wire','05 · Razorwire','VELOCITY',['Bare skeleton','Parallel conductors','Shards','Cross-current'],(g,word,s,f)=>{
    const col=['#e6f2c7','#ba97fc','#6dedfa','#ff4567'][s];
    if(s===3){g.fillStyle='#3b135d';for(let i=0;i<7;i++)g.fillRect(150+noise(i)*680,230+i*36,160+noise(i+9)*180,4)}
    wireWord(g,word,115,267,1050,180,col,s===0?2.0:1.65,s===1?3:1);
    if(s===0||s===3){line(g,[[65,267],[1188,267]],col,.65);line(g,[[210,447],[1210,447]],col,.65)}
    if(s===2){for(let i=0;i<word.length;i++){const x=138+i*(1050/word.length),y=i%2?452:255,r=10+i%3*4;line(g,[[x,y],[x+r*2,y-30],[x+r,y-4]],i%2?'#7848a5':col,1.8,true);line(g,[[x+r*2,y-30],[x+r*3,y-62]],'#555481',1.5)}}
  },{accepts:'A–Z and spaces'});

  function signOrnament(g,col,phase){
    for(const side of [-1,1]){g.save();g.translate(640,360);g.scale(side,1);g.strokeStyle=col;
      // A fan of bent rails frames the text; lamp diamonds sit outside its knockout.
      for(let i=0;i<9;i++){g.lineWidth=i===0?3:1.5;g.beginPath();g.moveTo(262,182+i*10);g.bezierCurveTo(414,240+i*3,579,30,448,-72-i*11);g.bezierCurveTo(350,-137-i*10,370,-229-i*4,498,-209-i*8);g.stroke()}
      for(let j=0;j<12;j++)for(let i=0;i<7;i++){const x=336+i*32+(j%2)*16,y=-246+j*45;g.save();g.translate(x,y);g.rotate(Math.PI/4);g.fillStyle=(i+j+phase)%5===0?'#372621':'#c79956';g.fillRect(-2.5,-2.5,5,5);g.fillStyle='#ffefb6';g.fillRect(-1,-1,2,2);g.restore()}
      g.restore()}
    for(let i=0;i<3;i++){g.strokeStyle=i===1?'#b84654':col;g.lineWidth=1.5;g.beginPath();g.ellipse(640,355,557+i*10,285+i*8,0,0,TAU);g.stroke()}
  }
  add('palace','06 · Electric palace','After Hours',['Emerald enamel','Gilt outline','Ivory marquee','Rose lacquer'],(g,word,s,f)=>{
    const words=word.trim().split(/\s+/),a=words.shift(),b=words.join(' '),phase=Math.floor(f/3),col=['#83dfb0','#e7ce89','#fbedd1','#f186b4'][s];
    signOrnament(g,s===3?'#c761a3':'#429c89',phase);
    for(let i=0;i<8;i++){const angle=i*TAU/8+.4,x=640+535*Math.cos(angle),y=360+288*Math.sin(angle);star(g,x,y,18,col,4,.2);star(g,x,y,7,'#fff4d2')}
    g.save();g.translate(640,360);g.rotate(-.035);g.translate(-640,-360);
    const first=b?[310,162,700,170]:[205,247,875,243],second=[235,360,810,209];
    const draw=(fill,stroke,lw)=>{text(g,a,...first,'Cormorant',fill,stroke,lw);if(b)text(g,b,...second,'Cormorant',fill,stroke,lw)};
    draw('#030706','#030706',24);draw(null,s===3?'#723557':'#184f42',12);draw(null,col,5);
    draw(s===1?'#070b09':gradient(g,0,190,[[0,'#fff5d8'],[.25,col],[.48,col],[.5,'#183c37'],[.57,col],[1,s===3?'#a93772':'#56af91']]),'#020904',1.4);
    // A baseline curl terminates at the lower word rather than floating separately.
    g.strokeStyle=col;g.lineWidth=2.5;g.beginPath();g.moveTo(274,561);g.bezierCurveTo(201,550,198,610,300,601);g.bezierCurveTo(394,593,431,574,476,570);g.stroke();g.restore();
    for(let i=0;i<23;i++){const x=390+i*23,y=614+11*Math.sin(i/22*Math.PI);bulb(g,x,y,3.2,'#f8c55d',(i+phase)%4!==0)}
  });

  add('orbital','07 · Orbit dial','ORBIT',['Armillary','Dot transmission','Hot meridian','Instrument face'],(g,word,s,f)=>{
    const phase=Math.floor(f/3)*.055,box=[286,276,708,149],col=s===2?'#ff527e':'#a398ed';
    function rings(front){g.save();g.translate(640,354);g.transform(1,.09,-.25,.7,0,0);
      const count=s===3?2:6;for(let ring=0;ring<count;ring++){const r=184+ring*26,segments=s===3?80:28+ring*4;g.lineWidth=s===3?2:2+ring%3;for(let j=0;j<segments;j++){const a=j*TAU/segments+(ring%2?phase:-phase),isFront=Math.sin(a)>0;if(isFront!==front||(j+ring)%5===0)continue;g.strokeStyle=s===2?['#701935','#ff527e','#f9b4ad'][ring%3]:['#483391','#497ddd','#a66de8','#a1cdf0'][ring%4];g.beginPath();g.arc(0,0,r,a,a+TAU/segments*(s===3?.17:.6));g.stroke()}}
      g.restore()}
    rings(false);text(g,word,...box,'Audiowide','#080711','#080711',12);
    if(s===1){for(const[x,y]of grid(word,'Audiowide',box,6))bulb(g,x,y,1.9,'#f78fec')}else text(g,word,...box,'Audiowide',s===2?'#b72955':s===3?'#c7c4d7':'#201340',col,3);
    rings(true);
    if(s===3){for(let i=0;i<12;i++){const a=i*TAU/12;line(g,[[640+490*Math.cos(a),354+247*Math.sin(a)],[640+503*Math.cos(a),354+259*Math.sin(a)]],'#615d83',2)}}
  });

  add('monolith','08 · Counterform','ODD',['Split geometry','Solid vermilion','Cutout blue','Nested counterforms'],(g,word,s,f)=>{
    const box=[172,174,936,365];
    if(s===1){g.fillStyle='#ed3a22';g.fillRect(0,0,W,H);text(g,word,...box,'RubikMono','#0c0a10');return}
    if(s===2){g.fillStyle='#244bdc';g.fillRect(0,0,W,H);text(g,word,...box,'RubikMono','#efdfc1');g.fillStyle='#244bdc';g.fillRect(0,341,W,22);return}
    const m=mask(word,'RubikMono',...box);masked(g,m,q=>{q.fillStyle=s===0?'#f15a2b':'#e8e0bd';q.fillRect(0,0,W,350);q.fillStyle=s===0?'#7288de':'#b65ada';q.fillRect(0,350,W,H-350)});
    if(s===0){g.fillStyle='#020304';g.fillRect(0,348,W,9)}
    if(s===3){masked(g,m,q=>{for(let i=1;i<6;i++){q.save();q.translate(640,356);q.scale(1-i*.06,1-i*.1);q.translate(-640,-356);outline(q,word,box,'RubikMono',i%2?'#040508':'#e8d7bd',2);q.restore()}})}
  });

  add('relic','09 · Gilt relic','Rapture',['Gold leaf','Engraved steel','Scarlet initial','Fine seal'],(g,word,s,f)=>{
    const col=['#e4bf75','#b6ccd7','#efede1','#e0a3be'][s],box=[166,231,948,269];
    for(let i=0;i<3;i++){const r=209+i*17;g.strokeStyle=s===2?'#421729':'#655143';g.lineWidth=.6;g.beginPath();g.arc(640,365,r,0,TAU);g.stroke()}
    for(let i=0;i<48;i++){const a=i*TAU/48;line(g,[[640+242*Math.cos(a),365+242*Math.sin(a)],[640+(i%4?249:267)*Math.cos(a),365+(i%4?249:267)*Math.sin(a)]],col,.65)}
    text(g,word,...box,'Blackletter','#070609','#070609',14);text(g,word,...box,'Blackletter',s===3?null:s===0?gradient(g,0,200,[[0,'#fff2b6'],[.32,'#d9b562'],[.45,'#5a331f'],[.5,'#eed393'],[.8,'#e5b661'],[1,'#82513b']]):col,col,s===3?1.5:2);
    if(s===0||s===1){const m=mask(word,'Blackletter',...box);masked(g,m,q=>{q.globalAlpha=.7;q.strokeStyle=s===0?'#534224':'#253a4f';q.lineWidth=1;for(let x=-720;x<1600;x+=s===0?7:4)line(q,[[x,0],[x+720,720]],q.strokeStyle,1)})}
    if(s===2){g.save();g.beginPath();g.rect(0,0,170+948/word.length,W);g.clip();text(g,word,...box,'Blackletter','#be1f40');g.restore()}
    for(const x of [130,1150]){star(g,x,364,25,col,4);star(g,x,364,8,'#09070a')}
  });

  add('overprint','10 · Overprint','MORE',['Orange stock','Black ink','Misregistered blue','Hot negative'],(g,word,s,f)=>{
    const bg=['#eb6935','#e5d4af','#c1cfdd','#ec2147'][s],ink=['#241b24','#25272c','#123ddb','#fbe2b6'][s];g.fillStyle=bg;g.fillRect(0,0,W,H);
    g.save();g.translate(640,360);g.rotate(-.11);g.translate(-640,-360);
    text(g,word,-60,107,1410,526,'AlfaSlab',s===2?'#b72743':ink);
    if(s===2){g.globalCompositeOperation='multiply';text(g,word,-38,92,1410,526,'AlfaSlab',ink);g.globalCompositeOperation='source-over'}
    const m=mask(word,'AlfaSlab',-60,107,1410,526);masked(g,m,q=>{for(let y=0;y<H;y+=9)for(let x=0;x<W;x+=9){q.fillStyle=bg;q.beginPath();q.arc(x,y,1.15+noise(x+y)*.9,0,TAU);q.fill()}});g.restore();
    g.globalAlpha=.2;for(let i=0;i<1600;i++){const x=noise(i)*W,y=noise(i+3000)*H;g.fillStyle=i%2?'#fff6d0':'#160e18';g.fillRect(x,y,1.4,1.4)}g.globalAlpha=1;
  });

  add('chrome','11 · Mercury sport','RUSH',['Chrome face','Horizon split','Copper emboss','Wire mirror'],(g,word,s,f)=>{
    const c=canvas(),q=c.getContext('2d'),box=[163,208,954,264],col=['#deeaff','#678ffa','#efbd9a','#d6f2ff'][s];
    for(let i=15;i>=1;i--)text(q,word,box[0]+i,box[1]+i,...box.slice(2),'Racing',s===2?'#7c2b36':'#243865');
    text(q,word,...box,'Racing',s===3?'#03060a':gradient(q,0,200,[[0,'#fff7e4'],[.3,col],[.44,'#263950'],[.49,'#080c21'],[.51,'#f2ffff'],[.59,col],[.78,'#1f365c'],[1,'#dce8e6']]),col,2);
    line(q,[[149,489],[1125,489]],col,2);line(q,[[210,502],[1050,502]],s===2?'#a44935':'#325b8f',1);
    if(s===1){g.drawImage(c,0,0,W,352,0,0,W,352);g.drawImage(c,0,352,W,H-352,32,361,W,H-352)}else g.drawImage(c,0,0);g.save();g.translate(0,722);g.scale(1,-.43);g.globalAlpha=.24;g.drawImage(c,0,0);g.restore();
    for(const[x,y]of[[260,232],[912,283],[1060,426]])star(g,x,y,s===3?8:14,col);
  });

  add('stack','12 · Collision press','NOW',['Three voices','Giant ground','Offset rows','Thin afterimage'],(g,word,s,f)=>{
    if(s===1){text(g,word[0],111,52,722,611,'RubikMono','#591ca4');outline(g,word,[207,304,963,147],'Audiowide','#74d3df',1.2);return}
    if(s===3){for(let i=0;i<5;i++)outline(g,word,[158+i*4,150+i*70,963,210],'Anton',i%2?'#be1635':'#6e538f',.7);return}
    text(g,word,150,128,970,276,'Anton',s===2?'#df451f':'#af1461');outline(g,word,[97,245,1080,254],'Audiowide','#e3d5c5',1.4);outline(g,word,[192,358,923,231],'RubikMono',s===2?'#5c57da':'#e83739',1.1);
  });

  function skeleton(g,word,box,drawSegment,advance=115){
    const [x,y,w,h]=box,total=(word.length-1)*advance+90;
    g.save();g.translate(x,y);g.scale(w/total,h/140);
    for(let j=0;j<word.length;j++){
      g.save();g.translate(j*advance,0);
      for(const points of glyph[word[j]]||[])drawSegment(g,points,j);
      g.restore();
    }g.restore();
  }

  add('tube','13 · Glass circuit','Wild',['Pink gas','Cold glass','Phosphor chase','Broken electrode'],(g,word,s,f)=>{
    if(word==='Wild'){DrawnLettering.tube(g,s,f);return}
    const box=[190,217,900,283],phase=Math.floor(f/4);
    // The faint return cables make the tubes an assembled object.
    g.strokeStyle='#292430';g.lineWidth=1.5;
    for(const side of [-1,1]){g.beginPath();g.moveTo(640+side*466,464);g.bezierCurveTo(640+side*510,479,640+side*447,551,640+side*480,559);g.stroke()}
    skeleton(g,word,box,(q,a,j)=>{
      const cold=s===1||(s===3&&j===(phase%word.length)),col=s===2?['#51c1ec','#ed529b','#ff935d'][(j+phase)%3]:'#fb4c87';
      const path=()=>{q.beginPath();for(let i=0;i<a.length;i+=2)i?q.lineTo(a[i],a[i+1]):q.moveTo(a[i],a[i+1])};
      q.lineCap='round';q.lineJoin='round';
      for(const [width,c]of [[9.5,'#241929'],[6.8,cold?'#565061':col],[3.8,cold?'#090a13':'#ffd6e4'],[1.4,cold?'#514b61':'#fff8f2']]){path();q.lineWidth=width;q.strokeStyle=c;q.stroke()}
      for(const idx of [0,a.length-2]){q.fillStyle='#211f2a';q.fillRect(a[idx]-3,a[idx+1]-3,6,6);q.strokeStyle='#8a7986';q.lineWidth=.8;q.strokeRect(a[idx]-3,a[idx+1]-3,6,6)}
    });
    // A pair of tiny ceramic mounting clips on each vertical edge.
    for(const x of [185,1095])for(const y of [292,411]){g.fillStyle='#34303b';g.fillRect(x-5,y-9,10,18);g.fillStyle='#9c8a94';g.fillRect(x-1,y-5,2,10)}
  },{accepts:'A–Z and spaces'});

  function signFace(g,word,dx,dy,fill,stroke,lw){
    g.save();g.translate(640+dx,350+dy);g.transform(1,-.075,0,1,0,0);g.translate(-640,-350);
    text(g,word,184,250,930,216,'AlfaSlab',fill,stroke,lw);g.restore();
  }
  add('marquee','14 · Grand dynamo','DYNAMO',['Porcelain bulbs','Unlit copper','Chasing lamps','Cut-glass outline'],(g,word,s,f)=>{
    const phase=Math.floor(f/3),col=s===3?'#a7ebea':'#f1c46e';
    // Fan rails meet the sign's cap; each end has a visible socket.
    for(let i=-12;i<=12;i++){
      const a=i*.066-Math.PI/2,x=640+Math.cos(a)*250,y=246+Math.sin(a)*147;
      line(g,[[640+i*18,239],[x,y]],i%2?'#6d322d':'#bb8550',i%3?1.5:3);
      bulb(g,x,y,i%3?2.2:3.7,'#ffd892',s!==1&&(i+phase)%4!==0);
    }
    const plate=[[110,306],[212,236],[1065,179],[1170,253],[1107,484],[223,540],[111,465]];
    g.beginPath();plate.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));g.closePath();g.fillStyle='#0b1018';g.fill();g.strokeStyle=s===3?'#46688b':'#a8483f';g.lineWidth=11;g.stroke();g.strokeStyle=col;g.lineWidth=2;g.stroke();
    for(let d=16;d>=1;d--)signFace(g,word,d*.65,d*.65,'#572329','#572329',6);
    signFace(g,word,0,0,null,'#d87f51',9);signFace(g,word,0,0,s===3?'#070a10':s===2?'#164e5b':'#732f3a',col,3.4);
    const m=canvas(),q=m.getContext('2d');signFace(q,word,0,0,'#fff',null,0);
    if(s!==3){const pts=TypeSurface.lampCenters('marquee:'+word,m,16);for(const [x,y]of pts){const on=s!==1&&(s!==2||(Math.floor(x/16)+Math.floor(y/16)+phase)%5<3);bulb(g,x,y,on?5.0:3.5,on?'#fff0b6':'#745450',true)}}
    else{signFace(g,word,0,0,null,'#7ac4c6',1.2);signFace(g,word,0,3,null,'#efba80',.7)}
    for(let i=0;i<49;i++){const x=215+i*18,y=520-(x-215)*.068;bulb(g,x,y,2.7,'#edb565',s!==1&&(i+phase)%5!==0)}
    for(const[x,y]of[[120,309],[1160,255],[225,533],[1100,479]]){star(g,x,y,14,col);star(g,x,y,5,'#fff5cc')}
  });

  add('ribbon','15 · Folded current','FOLD',['Ivory and cobalt','Red folded stock','Bare creases','Prismatic strip'],(g,word,s,f)=>{
    if(word==='Wild'){DrawnLettering.ribbon(g,s,f);return}
    const box=[142,208,996,298],colors=s===1?['#f57046','#8c133d','#ffd2a4']:s===3?['#7abdbc','#6854c4','#df956a']:['#ead7ac','#3747a4','#fcf1ce'];
    skeleton(g,word,box,(q,a,j)=>{
      q.lineJoin='bevel';q.lineCap='butt';
      const path=()=>{q.beginPath();for(let k=0;k<a.length;k+=2)k?q.lineTo(a[k],a[k+1]):q.moveTo(a[k],a[k+1])};
      q.save();q.translate(5,7);path();q.lineWidth=21;q.strokeStyle='#20212d';q.stroke();q.restore();
      if(s===2){path();q.lineWidth=1.2;q.strokeStyle='#eedec0';q.stroke()}
      for(let k=0;k<a.length-2;k+=2){const x=a[k],y=a[k+1],ex=a[k+2],ey=a[k+3],dx=ex-x,dy=ey-y,len=Math.hypot(dx,dy);if(!len)continue;const nx=-dy/len*10,ny=dx/len*10;
        q.beginPath();q.moveTo(x+nx,y+ny);q.lineTo(ex+nx,ey+ny);q.lineTo(ex-nx,ey-ny);q.lineTo(x-nx,y-ny);q.closePath();
        if(s===2){q.strokeStyle='#b1afb7';q.lineWidth=.7;q.stroke();continue}
        q.fillStyle=colors[s===3?(k/2+j+Math.floor(f/4))%3:(k/2+j)%2];q.fill();
        q.beginPath();q.moveTo(x+nx,y+ny);q.lineTo(ex+nx,ey+ny);q.lineTo(ex,ey);q.lineTo(x,y);q.closePath();q.fillStyle=colors[2];q.globalAlpha=s===3?.75:.42;q.fill();q.globalAlpha=1;
        line(q,[[x+nx,y+ny],[ex+nx,ey+ny]],'#fff2d5',.65);
        // A sharp triangular fold at the inside of every change of direction.
        if(k>0){q.beginPath();q.moveTo(x+nx,y+ny);q.lineTo(x-nx,y-ny);q.lineTo(x-dx/len*17,y-dy/len*17);q.closePath();q.fillStyle=colors[1];q.fill()}
      }
    });
  },{accepts:'A–Z and spaces'});

  // Modular alphabet built from rectangles, quarter circles and diagonals.
  // The 5x7 occupancy maps are geometry instructions, never sampled font pixels.
  const modules={
    A:['01110','11011','11011','11111','11011','11011','11011'],B:['11110','11011','11011','11110','11011','11011','11110'],C:['01111','11000','11000','11000','11000','11000','01111'],D:['11110','11011','11011','11011','11011','11011','11110'],E:['11111','11000','11000','11110','11000','11000','11111'],F:['11111','11000','11000','11110','11000','11000','11000'],G:['01111','11000','11000','11011','11011','11011','01111'],H:['11011','11011','11011','11111','11011','11011','11011'],I:['11111','00100','00100','00100','00100','00100','11111'],J:['00111','00011','00011','00011','00011','11011','01110'],K:['11011','11010','11100','11100','11100','11010','11011'],L:['11000','11000','11000','11000','11000','11000','11111'],M:['10001','11011','11111','10101','10001','10001','10001'],N:['11001','11001','11101','11111','11011','11011','11001'],O:['01110','11011','11011','11011','11011','11011','01110'],P:['11110','11011','11011','11110','11000','11000','11000'],Q:['01110','11011','11011','11011','11111','11011','01111'],R:['11110','11011','11011','11110','11100','11010','11011'],S:['01111','11000','11000','01110','00011','00011','11110'],T:['11111','00100','00100','00100','00100','00100','00100'],U:['11011','11011','11011','11011','11011','11011','01110'],V:['11011','11011','11011','11011','01010','01010','00100'],W:['10001','10001','10001','10101','11111','11011','10001'],X:['11011','11011','01010','00100','01010','11011','11011'],Y:['11011','11011','01010','00100','00100','00100','00100'],Z:['11111','00011','00110','00100','01100','11000','11111'],' ':['00000','00000','00000','00000','00000','00000','00000']
  };
  add('modular','16 · Modular riot','ECHO',['Quarter-circle tiles','Negative blocks','Broken lattice','Two-plane weave'],(g,word,s,f)=>{
    const colors=s===1?['#f0dec0','#111523','#ee6142']:['#f3673d','#92a9d9','#e4daac'],total=word.length*6-1,unit=Math.min(58,1070/total),ox=(W-total*unit)/2,oy=(H-unit*7)/2;
    if(s===1){g.fillStyle=colors[0];g.fillRect(0,0,W,H)}
    for(let l=0;l<word.length;l++){const map=modules[word[l]];for(let y=0;y<7;y++)for(let x=0;x<5;x++){
      if(map[y][x]!=='1')continue;const px=ox+(l*6+x)*unit,py=oy+y*unit,k=(x+y+l+(s===3?Math.floor(f/4):0))%3;
      g.fillStyle=s===1?colors[1]:colors[k];
      if(s===2){g.strokeStyle=colors[k];g.lineWidth=1.8;g.strokeRect(px+1.5,py+1.5,unit-3,unit-3);if(k===1)line(g,[[px,py+unit],[px+unit,py]],colors[k],1.8);continue}
      g.fillRect(px,py,unit+.1,unit+.1);
      const exposed=!(map[y-1]?.[x]==='1'&&map[y+1]?.[x]==='1'&&map[y]?.[x-1]==='1'&&map[y]?.[x+1]==='1');
      if(exposed){g.save();g.beginPath();g.rect(px,py,unit,unit);g.clip();g.fillStyle=s===1?colors[2]:colors[(k+1)%3];g.beginPath();const right=(x+l)%2,down=(y+l)%2;g.arc(px+right*unit,py+down*unit,unit,0,TAU);g.fill();g.restore()}
      if(s===3){g.fillStyle='#07090f';g.fillRect(px,py+unit*.44,unit,unit*.12);g.fillStyle='#f1d09e';g.fillRect(px+unit*.42,py,unit*.16,unit)}
    }}
  },{accepts:'A–Z and spaces'});

  const softMasks=new Map();
  function softMask(word){
    if(softMasks.has(word))return softMasks.get(word);
    const c=canvas(),q=c.getContext('2d');
    const height=Math.min(249,958/((word.length-1)*135+90)*140);
    skeleton(q,word,[161,(720-height)/2,958,height],(g,a)=>{
      g.strokeStyle='#fff';g.lineWidth=29;g.lineJoin='round';g.lineCap='round';g.beginPath();g.moveTo(a[0],a[1]);
      for(let i=2;i<a.length-2;i+=2)g.quadraticCurveTo(a[i],a[i+1],(a[i]+a[i+2])/2,(a[i+1]+a[i+3])/2);
      if(a.length>2)g.lineTo(a.at(-2),a.at(-1));g.stroke();
    },135);
    softMasks.set(word,c);if(softMasks.size>8)softMasks.delete(softMasks.keys().next().value);return c;
  }
  add('softmetal','17 · Soft metal','Wild',['Liquid silver','Rose resin','Molten brass','Interference foil'],(g,word,s,f)=>{
    if(word==='Wild'){TypeSurface.draw(g,'drawn:Wild',DrawnLettering.mask(40),s,f,{bevel:17});return}
    const bevel=14.5*Math.min(958/((word.length-1)*135+90),249/140)*.92;
    TypeSurface.draw(g,'soft:'+word,softMask(word),s,f,{bevel});
  },{accepts:'A–Z and spaces'});

  function render(id,word,state,frame,target,{label=false,transparent=false}={}){
    const family=typeof id==='number'?families[id]:families.find(x=>x.id===id);if(!family)throw new Error('Unknown family '+id);
    word=(word||family.word).trim();if(!word||word.length>18)throw new Error('Use 1–18 characters');if(family.accepts&&!/^[A-Z ]+$/.test(word)&&!(['tube','ribbon','softmetal'].includes(family.id)&&word==='Wild'))throw new Error(family.name+' supports uppercase A–Z and spaces');
    const g=target.getContext('2d');g.save();g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';g.fillStyle='#030305';if(transparent)g.clearRect(0,0,target.width,target.height);else g.fillRect(0,0,target.width,target.height);const s=((state%4)+4)%4,layer=canvas(),q=layer.getContext('2d');family.draw(q,word,s,frame);
    const emission={pinboard:[.45,0,.4,0],slats:[0,0,.22,0],wingline:[.08,0,.42,0],depth:[.24,0,0,.22],wire:[0,.15,0,.22],orbital:[.12,.25,.25,0],tube:[.7,0,.6,.5],marquee:[.1,0,.2,.1]};
    const light=emission[family.id]?.[s]||0;
    if(light){g.globalCompositeOperation='lighter';g.globalAlpha=light*.55;g.filter='blur(14px)';g.drawImage(layer,0,0);g.globalAlpha=light;g.filter='blur(3px)';g.drawImage(layer,0,0);g.filter='none';g.globalAlpha=1;g.globalCompositeOperation='source-over'}
    g.drawImage(layer,0,0);g.restore();
    if(label){g.fillStyle='#17171b';g.fillRect(0,H,W,48);g.font='17px system-ui';g.fillStyle='#eee';g.fillText(`${family.name}  /  ${family.states[((state%4)+4)%4]}`,22,H+31)}
  }
  return {W,H,families,render,canvas,noise};
})();
