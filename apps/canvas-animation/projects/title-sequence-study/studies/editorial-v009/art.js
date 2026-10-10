/* Original compositions built from editable vector type. No raster references,
   live fonts, or remote resources enter the render. */
window.Editorial = (() => {
  const W=1600, H=900, FPS=24, FRAMES=288, TAU=Math.PI*2;
  const BLACK='#060609', CREAM='#fff2ce', RED='#f83235', LIME='#dcfa37';
  const paths=new Map();
  const clamp=v=>Math.max(0,Math.min(1,v));
  const ease=v=>1-Math.pow(1-clamp(v),3);
  function shape(font,word){
    const key=font+'|'+word;
    if(!paths.has(key)){
      const a=LetterOutlines[font][word];
      paths.set(key,{...a,path:new Path2D(a.d)});
    }
    return paths.get(key);
  }
  function type(g,word,font,x,y,w,h,fill,stroke=null,lw=1){
    const a=shape(font,word);g.save();g.translate(x,y);g.scale(w/a.w,h/a.h);g.translate(-a.x,-a.y);
    g.lineJoin='round';
    if(stroke){g.strokeStyle=stroke;g.lineWidth=lw*a.w/w;g.stroke(a.path);}
    if(fill){
      if(typeof fill==='string'){g.fillStyle=fill;g.fill(a.path);}
      else {g.restore();g.save();clipType(g,word,font,x,y,w,h);g.fillStyle=fill;g.fillRect(0,0,W,H);}
    }
    g.restore();
  }
  function clipType(g,word,font,x,y,w,h){
    const a=shape(font,word),m=new DOMMatrix().translate(x,y).scale(w/a.w,h/a.h).translate(-a.x,-a.y);
    const p=new Path2D();p.addPath(a.path,m);g.clip(p);
  }
  function line(g,d,color,width=1){g.strokeStyle=color;g.lineWidth=width;g.lineCap='round';g.stroke(new Path2D(d));}
  function star(g,x,y,r,color){g.fillStyle=color;g.beginPath();g.moveTo(x-r,y);g.quadraticCurveTo(x-3,y-3,x,y-r);g.quadraticCurveTo(x+3,y-3,x+r,y);g.quadraticCurveTo(x+3,y+3,x,y+r);g.quadraticCurveTo(x-3,y+3,x-r,y);g.fill();}
  function fill(g,color){g.fillStyle=color;g.fillRect(0,0,W,H);}
  function gradient(g,y,h,stops){const a=g.createLinearGradient(0,y,0,y+h);stops.forEach(([p,c])=>a.addColorStop(p,c));return a;}
  function slanted(g,angle,paint){g.save();g.translate(800,450);g.rotate(angle);g.translate(-800,-450);paint();g.restore();}

  // Each entry is an art-directed composition, not just a different palette.
  const cards=[];
  function add(id,name,draw,reason){cards.push({id,name,draw,reason});}

  function impact(g,p,v){
    fill(g,RED);
    if(!v){
      // A single monumental verb begins the phrase; IT arrives as a tiny cut.
      type(g,'MAKE','condensed',42,-40,1516,980,BLACK);
    }else{
      type(g,'M','slab',-310,-200,1480,1350,BLACK);
      slanted(g,-.17,()=>{
        type(g,'MAKE','race',635,205,832,156,CREAM,RED,7);
        type(g,'IT','race',701,396,190,110,CREAM);
        type(g,'MOVE','race',636,533,834,157,CREAM,RED,7);
      });
    }
  }
  add('impact','01 / Monument', (g,p)=>impact(g,p,0),'A single cropped black verb fills the red field.');
  add('impact-oblique','02 / Oblique monument',(g,p)=>impact(g,p,1),'Cropped slab M supports an oblique three-line phrase.');

  function chrome(g,p,v){
    fill(g,BLACK);
    const box=v?[158,257,1284,334]:[72,246,1456,390];
    const [x,y,w,h]=box,word='MOVE',font='wide';
    const dy=8*(1-ease(p*3));
    for(let i=22;i>0;i-=2)type(g,word,font,x+i*.8,y+i*.7+dy,w,h,'#49141e','#611926',4);
    type(g,word,font,x,y+dy,w,h,null,'#fc3b55',21);
    type(g,word,font,x,y+dy,w,h,null,'#090c10',14);
    type(g,word,font,x,y+dy,w,h,null,'#bcd9d6',8);
    const material=gradient(g,y,h,[[0,'#a5b9b9'],[.14,'#e9f6dd'],[.31,'#525d6d'],[.46,'#e9fffc'],[.49,'#ffffff'],[.50,'#102028'],[.65,'#9baab7'],[.77,'#1a2735'],[1,'#e5efe1']]);
    type(g,word,font,x,y+dy,w,h,material,'#effbe9',1);
    g.save();clipType(g,word,font,x,y+dy,w,h);

    // A local specular band moves over a fixed, edge-defined metal surface.
    const beam=g.createLinearGradient(x+p*w-120,0,x+p*w+160,0);beam.addColorStop(0,'#ffffff00');beam.addColorStop(.49,'#d8ffff00');beam.addColorStop(.5,'#efffffaa');beam.addColorStop(.58,'#d8ffff44');beam.addColorStop(1,'#ffffff00');g.fillStyle=beam;g.fillRect(x,y,w,h);g.restore();
    if(v){
      type(g,'Make it','serif',498,101,604,103,CREAM);
      line(g,'M254 720 C520 650 1080 650 1346 720','#ea4763',3);
    }else{

      for(const xx of [123,1474])star(g,xx,255,22,'#ffedda');
    }
  }
  add('chrome','03 / Redline metal',(g,p)=>chrome(g,p,0),'Wide metal lettering, red edge and local light travel.');
  add('chrome-sign','04 / Metal sign',(g,p)=>chrome(g,p,1),'Serif lead-in above a compact dimensional word.');

  function flourish(g,p,v){
    fill(g,'#06130f');
    const color='#9bedca';
    // Rails continue the ascenders and descenders, rather than orbiting a font.
    for(let k=0;k<8;k++){
      const o=k*9;
      line(g,`M${151+o} 650 C${-65+o} 346 ${162+o} 151 ${430+o} 237 C${698+o} 325 ${471+o} 377 ${321+o} 294`,k%3?'#296c59':color,k%3?1:2);
      line(g,`M${1110-o} 586 C${1352-o} 465 ${1600-o} 615 ${1440-o} 767 C${1306-o} 893 ${1063-o} 805 ${1060-o} 688`,k%3?'#296c59':color,k%3?1:2);
    }
    slanted(g,-.075,()=>{
      const draw=(dx,dy,c,s,l)=>{
        type(g,'Make it','serif',(v?303:205)+dx,(v?210:135)+dy,v?1030:1130,v?218:265,c,s,l);
        type(g,'Move','serif',(v?196:405)+dx,(v?389:420)+dy,v?1084:994,v?323:302,c,s,l);
      };
      draw(8,9,'#173e31','#173e31',12);draw(0,0,null,'#e4ffe5',7);draw(0,0,null,'#06130f',4);
      draw(0,0,gradient(g,100,660,[[0,'#fff8da'],[.42,'#a2d9b3'],[.5,'#faffd9'],[.65,'#4c9c80'],[1,'#fff7dc']]),null,0);
    });
    for(const [x,y,r]of [[263,175,17],[1240,385,21],[464,735,13]])star(g,x,y,r*(.85+.15*Math.cos(p*TAU)),CREAM);
    if(v){type(g,'IT','wide',1261,219,119,57,color);}
  }
  add('flourish','05 / Verdigris script',(g,p)=>flourish(g,p,0),'Asymmetric italic phrase with integrated ascending and descending rails.');
  add('flourish-stack','06 / Verdigris stack',(g,p)=>flourish(g,p,1),'Closer interlocked stack; smaller counters and heavier hierarchy.');

  function gothic(g,p,v){
    fill(g,BLACK);
    const face=v?'#f78e33':'#ffa4cb',edge=v?'#fa392c':'#8740c1';
    const rows=v?[['Make',130,62,1240,348],['Move',278,438,1200,350]]:[['Make it',288,112,1010,243],['Move',184,393,1230,340]];
    for(const [word,x,y,w,h]of rows){
      type(g,word,'gothic',x+12,y+10,w,h,edge,edge,12);
      type(g,word,'gothic',x,y,w,h,null,'#301329',17);
      type(g,word,'gothic',x,y,w,h,null,face,9);
      type(g,word,'gothic',x,y,w,h,v?face:'#f5e8e3','#fff6d4',1);
      g.save();clipType(g,word,'gothic',x,y,w,h);
      if(v)for(let i=0;i<10;i++){g.fillStyle=i%2?'#21121f22':'#fff4db22';g.fillRect(0,y+i*h/10+p*9,W,2);}
      g.restore();
    }
    if(v)type(g,'it','serif',765,350,111,105,CREAM);
    else{line(g,'M344 792 L1286 792',edge,2);star(g,815,792,18,face);}
  }
  add('gothic','07 / Rose blackletter',(g,p)=>gothic(g,p,0),'Compact lettering with sharp white edges and plum extrusion.');
  add('gothic-poster','08 / Orange blackletter',(g,p)=>gothic(g,p,1),'Oversized two-line silhouette with an italic bridge.');

  function tunnel(g,p,v){
    fill(g,'#070813');
    const van=[v?1060:800,v?350:450],layers=v?15:12;
    for(let i=layers;i>=0;i--){
      const z=(i+p*1.8)/layers,scale=Math.pow(.13,z),w=1450*scale,h=570*scale;
      const x=van[0]+(800-van[0])*scale-w/2,y=van[1]+(450-van[1])*scale-h/2;
      const color=i%4===0?'#fbf5d9':i%4===1?'#33bfd2':'#347d9f';
      type(g,'MOVE',v?'race':'wide',x,y,w,h,null,color,i===0?4:1.6);
    }
  }

  // MAKE IT is assembled from existing outlines for this one compact bridge.
  const combined=LetterOutlines.wide;
  if(!combined['MAKE IT']){
    const a=combined.MAKE,b=combined.IT,gap=120;
    const p=new Path2D(a.d),p2=new Path2D(b.d);p.addPath(p2,new DOMMatrix().translate(a.w+gap,0));
    paths.set('wide|MAKE IT',{x:a.x,y:Math.min(a.y,b.y),w:a.w+b.w+gap,h:Math.max(a.h,b.h),path:p});
  }
  add('tunnel','09 / Cathedral depth',(g,p)=>tunnel(g,p,0),'Perspective receding to a compact persistent phrase.');
  add('tunnel-oblique','10 / Off-axis depth',(g,p)=>tunnel(g,p,1),'Diagonal racing glyphs with an offset vanishing point.');

  const dotCache=new Map();
  function points(word,font,box,step){const key=[word,font,...box,step].join();if(!dotCache.has(key)){
    const c=document.createElement('canvas');c.width=W;c.height=H;const q=c.getContext('2d');type(q,word,font,...box,'#fff');const d=q.getImageData(0,0,W,H).data,a=[];
    for(let y=step/2|0;y<H;y+=step)for(let x=step/2|0;x<W;x+=step)if(d[(y*W+x)*4+3]>190)a.push([x,y]);dotCache.set(key,a);
  }return dotCache.get(key);}
  function lamps(g,p,v){
    fill(g,'#090610');const box=v?[192,218,1216,462]:[220,320,1160,268];
    if(!v){
      type(g,'Make it','serif',542,184,513,117,'#ffb0c0');
      for(let k=0;k<4;k++){line(g,`M${137+k*12} 473 C${58+k*12} 179 ${306+k*12} 61 ${550+k*12} 144`,'#7c314e',1.7);line(g,`M${1463-k*12} 473 C${1542-k*12} 711 ${1294-k*12} 824 ${1050-k*12} 751`,'#7c314e',1.7);}
    }
    const lampPoints=v?['M','O','V','E'].flatMap((ch,index)=>points(ch,'condensed',[216+index*304,218,256,462],13).map(([x,y])=>[x,y,index])):points('MOVE','slab',box,13).map(([x,y])=>[x,y,Math.min(3,Math.floor((x-box[0])/(box[2]/4)))]);
    for(const [x,y,letter]of lampPoints){
      const lit=letter!==(Math.floor(p*4)%4);
      g.fillStyle=lit?'#ff488d':'#491526';g.beginPath();g.arc(x,y,lit?4.9:2.8,0,TAU);g.fill();
      if(lit){g.fillStyle='#ffdcc5';g.beginPath();g.arc(x-1,y-1,1.7,0,TAU);g.fill();}
    }
    if(v){}
    else {line(g,'M380 648 Q800 704 1220 648','#f85d97',2);star(g,800,677,14,CREAM);}
  }
  add('lamps','11 / After-dark marquee',(g,p)=>lamps(g,p,0),'Bulb lettering and fine sign architecture, with travelling dark segments.');
  add('lamps-wall','12 / Lamp wall',(g,p)=>lamps(g,p,1),'Four individually drawn dot-matrix letters dim in succession.');

  function split(g,p,v){
    fill(g,v?'#181536':BLACK);
    const cols=v?['#a2a2fc','#f592a5']:['#e2f746','#e2f746'];
    const rows=[['MAKE',83,60,1434,370],['MOVE',83,474,1434,366]];
    for(const [word,x,y,w,h]of rows){
      for(let band=0;band<5;band++){
        const dx=band===2?(1-ease(p*3))*95:band===3?-17:0;
        g.save();g.beginPath();g.rect(0,y+band*h/5,W,h/5-4);g.clip();
        type(g,word,v?'wide':'condensed',x+dx,y,w,h,cols[band%2]);g.restore();
      }
    }
    if(v)type(g,'it','serif',727,340,166,182,'#fef1cf',BLACK,7);
    // These voids are designed through the letter mass, not a full-frame glitch.
    g.fillStyle=v?'#181536':BLACK;
    if(v)for(const x of [341,928,1360])g.fillRect(x,0,4,H);
  }
  add('split','13 / Cut-pressure',(g,p)=>split(g,p,0),'Tightly stacked condensed type fractured by unequal slats.');
  add('split-wide','14 / Violet shutters',(g,p)=>split(g,p,1),'Wide glyph construction and offset rows in a denser field.');

  function optical(g,p,v){
    fill(g,BLACK);
    const box=v?[100,96,1410,686]:[127,209,1346,475];
    const [x,y,w,h]=box;
    type(g,'MOVE',v?'serif':'slab',x,y,w,h,null,'#eee5cf',2);
    g.save();clipType(g,'MOVE',v?'serif':'slab',...box);
    g.fillStyle='#0a2028';g.fillRect(0,0,W,H);
    // Offset concentric ellipses carve an optical material inside the glyphs.
    for(let i=120;i>0;i--){g.beginPath();g.ellipse(v?485:804,435,i*13+p*65,i*8+p*40,-.12,0,TAU);g.strokeStyle=i%12===0?'#ff727c':i%3===1?'#76e4dc':'#fff0cb';g.lineWidth=i%3===1?4:2;g.stroke();}
    g.restore();

  }
  add('optical','15 / Carved interference',(g,p)=>optical(g,p,0),'Concentric inlaid geometry follows a heavy slab silhouette.');
  add('optical-serif','16 / Optical italic',(g,p)=>optical(g,p,1),'Fine italic counters cut through a dense curving line field.');

  function tiny(g,p,v){
    fill(g,BLACK);
    if(v){type(g,'M','slab',-340,-260,1330,1430,'#492180');type(g,'Move','serif',619,425,822,207,CREAM);type(g,'Make it','serif',833,321,364,82,'#f898b9');}
    else{
      type(g,'IT','wide',680,385,240,130,'#fe5140');
    }
  }
  add('small','17 / Small signal',(g,p)=>tiny(g,p,0),'The single word IT makes a brief, deliberate reduction of image area.');
  add('giant','18 / Glyph collision',(g,p)=>tiny(g,p,1),'Huge cropped purple slab contrasts with a precise ivory italic phrase.');

  const angular={M:'M0 180 V0 H26 L80 70 L134 0 H160 V180 H127 V59 L80 113 L33 59 V180 Z',O:'M30 0 H130 L160 30 V150 L130 180 H30 L0 150 V30 Z M35 40 V140 H125 V40 Z',V:'M0 0 H36 L80 128 L124 0 H160 L97 180 H63 Z',E:'M0 0 H160 V36 H36 V72 H132 V107 H36 V144 H160 V180 H0 Z'};
  function angularWord(g,x,y,w,h,fillColor,stroke=null,lw=1){g.save();g.translate(x,y);g.scale(w/710,h/180);g.transform(1,0,-.16,1,29,0);['M','O','V','E'].forEach((ch,i)=>{g.save();g.translate(i*183,0);const p=new Path2D(angular[ch]);if(stroke){g.strokeStyle=stroke;g.lineWidth=lw;g.stroke(p);}if(fillColor){g.fillStyle=fillColor;g.fill(p,'evenodd');}g.restore();});g.restore();}
  function razor(g,p,v){
    fill(g,BLACK);
    if(v){for(let i=10;i>=0;i--)angularWord(g,92+i*9,292-i*17,1340,328,null,i%2?'#732744':'#ff594b',1.2);angularWord(g,92,292,1340,328,'#f3dfc0');}
    else{
      angularWord(g,110,309,1350,288,null,'#c9fafa',1.6);
      angularWord(g,101,316,1350,288,null,'#9465cd',1.1);
      for(const x of [137,550,965,1390])line(g,`M${x} 298 L${x+57} 209 L${x+38} 298 Z`,'#fa7772',1.5);
      line(g,'M80 630 L1480 630','#829bba',1);
      type(g,'MAKE','wide',135,651,242,34,'#c9fafa');type(g,'IT','wide',1360,258,95,30,'#fa7772');
    }
  }
  add('razor','19 / Razor geometry',(g,p)=>razor(g,p,0),'Custom polygon lettering with spare knife-like terminals.');
  add('razor-solid','20 / Racing relief',(g,p)=>razor(g,p,1),'Custom solid lettering on a stepped extrusion.');

  // Main cut is deliberately non-escalating. At 24 fps the phrase alternates
  // 6–21-frame editorial units, with longer anchors and short local changes.
  let SHOTS=[];
  function setShots(shots){SHOTS=shots;}
  function shotAt(frame){const f=((Math.floor(frame)%FRAMES)+FRAMES)%FRAMES;let start=0;for(const s of SHOTS){if(f<start+s.frames)return {...s,start,local:f-start};start+=s.frames;}throw Error('Timeline does not cover frame '+f);}
  const stage=document.createElement('canvas');stage.width=W;stage.height=H;
  const lightIds=new Set(['gothic','lamps','lamps-wall','tunnel','tunnel-oblique']);
  function card(canvas,id,progress=.5){
    const q=stage.getContext('2d');q.resetTransform();q.globalAlpha=1;q.globalCompositeOperation='source-over';q.clearRect(0,0,W,H);
    cards.find(c=>c.id===id).draw(q,progress);
    const g=canvas.getContext('2d');g.save();g.setTransform(canvas.width/W,0,0,canvas.height/H,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';g.clearRect(0,0,W,H);g.drawImage(stage,0,0);
    if(lightIds.has(id)){
      g.globalCompositeOperation='screen';g.filter='blur(10px)';g.globalAlpha=id==='gothic'?.20:.42;g.drawImage(stage,0,0);g.filter='none';
    }
    g.restore();
  }

  function draw(canvas,frame){const s=shotAt(frame);card(canvas,s.id,s.local/Math.max(1,s.frames-1));return s;}
  return {W,H,FPS,FRAMES,cards,card,draw,setShots,shotAt};
})();
