// Original lettering experiments. Pure canvas drawing, local fonts, no reference pixels.
// Geometry and masks stay in this study until the visual direction is approved.
const W = 1280, H = 544, TAU = Math.PI * 2;
const pink = '#ed16ac', lime = '#72ff50', cream = '#fff6e7';
const faces = {
  heavy: 'Impact', slab: 'Rockwell', script: 'Snell Roundhand',
  gothic: 'StudyBlackletter', serif: 'Didot', rounded: 'Arial Rounded MT Bold',
  condensed: 'Avenir Next Condensed', sans: 'Helvetica Neue',
};
const identity = [
  ['01', 'Architectural neon', 'Hand-drawn geometric letters · nested strokes · sign enclosure'],
  ['02', 'Perforated marquee', 'Text mask · hollow circular cells · contrasting script'],
  ['03', 'Varsity × signature', 'Outlined slab letters · script overlay · graphic rules'],
  ['04', 'Illuminated blackletter', 'OFL blackletter face · bevel-like strokes · drawn flourishes'],
  ['05', 'Chromatic signature', 'Calligraphic face · extrusion · gradient · star ornaments'],
  ['06', 'Emblem lettering', 'Slab letterforms · custom geometric centre · drawn sunburst'],
  ['07', 'Cut-metal stencil', 'Custom polygon alphabet · cutouts · offset inlay'],
  ['08', 'Contour turbulence', 'Repeated letter contours · rotation · displacement'],
  ['09', 'Rainbow wordmark', 'Rounded lettering · nested color bands · integrated rainbow'],
  ['10', 'Editorial collision', 'Condensed display type · thin serif layers · scale contrast'],
  ['11', 'RGB print screen', 'Three offset dot screens sampled through a text mask'],
  ['12', 'Bubble insignia', 'Rounded text · thick layered edging · orbital graphic'],
];

function makeCanvas() { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; }
function clear(g) { g.resetTransform(); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.shadowBlur = 0; g.fillStyle = '#000'; g.fillRect(0, 0, W, H); }
function text(g, word, x, y, size, face, { fill = cream, strokes = [], width = 1100, weight = 'normal', italic = false, skew = 0, rotate = 0, stretch = false } = {}) {
  g.save(); g.font = `${italic ? 'italic ' : ''}${weight} ${size}px "${face}"`;
  const m = g.measureText(word), ww = m.actualBoundingBoxLeft + m.actualBoundingBoxRight;
  g.translate(x, y); g.rotate(rotate); g.transform(1, 0, skew, 1, 0, 0);
  g.scale(stretch ? width / ww : Math.min(1, width / ww), 1);
  g.textAlign = 'left'; g.textBaseline = 'alphabetic'; g.lineJoin = 'round';
  const tx = (m.actualBoundingBoxLeft - m.actualBoundingBoxRight) / 2;
  const ty = (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2;
  for (const [color, lineWidth] of strokes) { g.strokeStyle = color; g.lineWidth = lineWidth; g.strokeText(word, tx, ty); }
  if (fill) {
    if (fill.colors) { const gr=g.createLinearGradient(0,-(m.actualBoundingBoxAscent+m.actualBoundingBoxDescent)/2,0,(m.actualBoundingBoxAscent+m.actualBoundingBoxDescent)/2);fill.colors.forEach((c,i)=>gr.addColorStop(i/(fill.colors.length-1),c));g.fillStyle=gr; } else g.fillStyle=fill;
    g.fillText(word,tx,ty);
  }
  g.restore();
}
function gradient(g, colors) { return { colors }; }

function stroke(g, pts, color, width, close = false) {
  g.save(); g.beginPath(); g.moveTo(...pts[0]); pts.slice(1).forEach(p => g.lineTo(...p)); if (close) g.closePath();
  g.lineJoin = 'round'; g.lineCap = 'round'; g.strokeStyle = color; g.lineWidth = width; g.stroke(); g.restore();
}
function star(g, x, y, r, color, angle = 0, rays = 4) {
  g.save(); g.translate(x,y); g.rotate(angle); g.beginPath();
  for (let i=0;i<rays*2;i++) { const a=i*Math.PI/rays, rr=i%2?r*.23:r; g.lineTo(Math.cos(a)*rr,Math.sin(a)*rr); }
  g.closePath(); g.fillStyle=color; g.fill(); g.restore();
}
function flourish(g, x, y, s, color, flip = 1) {
  g.save();g.translate(x,y);g.scale(s*flip,s);g.beginPath();
  g.moveTo(-170,0);g.bezierCurveTo(-100,50,100,30,175,-8);g.bezierCurveTo(250,-48,120,-65,115,-8);
  g.bezierCurveTo(105,50,-30,20,-55,-5);g.strokeStyle=color;g.lineWidth=3;g.stroke();g.restore();
}
// Single-line paths for SIGNAL, deliberately designed rather than font-derived.
const paths = {
 S: [[[90,0],[18,0],[0,18],[0,47],[18,65],[72,65],[90,83],[90,112],[72,130],[0,130]]],
 I: [[[0,0],[82,0]],[[41,0],[41,130]],[[0,130],[82,130]]],
 G: [[[90,18],[72,0],[18,0],[0,18],[0,112],[18,130],[90,130],[90,72],[52,72]]],
 N: [[[0,130],[0,0],[90,130],[90,0]]],
 A: [[[0,130],[0,32],[45,0],[90,32],[90,130]],[[0,76],[90,76]]],
 L: [[[0,0],[0,130],[90,130]]],
};
function signal(g, x, y, scale, color, width) {
  g.save();g.translate(x-((6*120-30)*scale)/2,y-65*scale);g.scale(scale,scale);
  [...'SIGNAL'].forEach((ch,i)=>{g.save();g.translate(i*120,0);paths[ch].forEach(p=>stroke(g,p,color,width));g.restore();});g.restore();
}
const masks = new Map();
function mask(key, draw) {
  if (!masks.has(key)) { const c=makeCanvas();draw(c.getContext('2d'));masks.set(key,c.getContext('2d').getImageData(0,0,W,H).data); }
  return masks.get(key);
}
function alpha(data,x,y) { const xx=Math.round(x), yy=Math.round(y);return xx<0||xx>=W||yy<0||yy>=H?0:data[(yy*W+xx)*4+3]; }

function neon(g,t) {
  const flicker=.85+.15*Math.sin(t*2);
  g.globalAlpha=flicker;
  [48,35,22,9].forEach((lw,i)=>signal(g,640,274,1.45,[lime,'#000','#b7ffa5','#000'][i],lw/1.45));
  g.globalAlpha=1;
  for (const [r,c,lw] of [[0,lime,3],[12,'#227e28',2]]) {
    g.beginPath();g.roundRect(71+r,87+r,1138-r*2,366-r*2,62-r);g.strokeStyle=c;g.lineWidth=lw;g.stroke();
  }
  g.fillStyle='#000';g.fillRect(446,424,388,45);
  text(g,'TRANSMISSION',640,445,28,faces.condensed,{fill:'#acff9c',weight:'600',width:360});
}
function marquee(g,t) {
  const d=mask('more-dots',m=>text(m,'MORE',640,232,410,faces.heavy,{fill:'#fff',width:1090,stretch:true}));
  for(let y=60;y<406;y+=28)for(let x=75;x<1200;x+=28)if(alpha(d,x,y)>160){
    g.strokeStyle=`hsl(${311+10*Math.sin(x*.015+t)},95%,${43+9*Math.sin(y*.04+t)}%)`;g.lineWidth=3.3;
    g.beginPath();g.arc(x,y,11,0,TAU);g.stroke();
  }
  text(g,'and more',775,381,142,faces.script,{fill:'#000',strokes:[[cream,5]],width:720});
  flourish(g,805,446,.95,cream);
}
function varsity(g,t) {
  text(g,'MORE',620,246,343,faces.slab,{fill:'#070306',strokes:[[pink,8]],weight:'bold',width:1100});
  text(g,'and more',680+Math.sin(t)*8,354,175,faces.script,{fill:'#e6cadc',strokes:[['#000',17],['#be1379',9],['#f6d9ef',2]],width:840});
  stroke(g,[[120,432],[434,432]],pink,2);stroke(g,[[877,432],[1150,432]],pink,2);
  star(g,640,455,13,pink,0,8);
}
function gothic(g,t) {
  const fill=gradient(g,['#fff9f5','#d6a7ec','#6a318d','#f4d0ff'],130,364);
  text(g,'Becoming',640,249,239,faces.gothic,{fill,strokes:[['#472058',12],['#a660cb',7],['#f6dcff',2]],width:1100});
  flourish(g,342,407,1.1,'#9d63b3');flourish(g,936,407,1.1,'#9d63b3',-1);
  star(g,640,419,25,'#d0a3e8',Math.sin(t)*.08,8);
  stroke(g,[[615,419],[473,419]],'#9d63b3',1);stroke(g,[[665,419],[805,419]],'#9d63b3',1);
}
function signature(g,t) {
  for(let i=0;i<18;i++) { const x=85+(i*197)%1110,y=72+(i*83)%390;star(g,x,y,3+(i%4)*2,'#9e679c',t*.08+i); }
  for(let i=15;i>0;i-=2)text(g,'Overdrive',640+i,269+i*.65,260,faces.script,{fill:'#68214c',width:1070});
  const fill=gradient(g,['#fff6ec','#eea4d2','#7d447f','#f8c8e4'],140,360);
  text(g,'Overdrive',640,269,260,faces.script,{fill,strokes:[['#8d274f',17],['#6cd6e6',10],['#382343',6],['#fff1df',2]],width:1070});
  flourish(g,650,439,1.7,'#d070ab');star(g,1030,198,20,cream,t*.1);
}
function emblem(g,t) {
  // Two text blocks surround a designed sunburst O; the emblem participates in the lettering.
  text(g,'M',265,277,302,faces.slab,{fill:'#f3ebe0',weight:'bold',width:245});
  text(g,'RE',886,277,302,faces.slab,{fill:'#f3ebe0',weight:'bold',width:447});
  g.save();g.translate(527,277);g.rotate(t*.12);
  star(g,0,0,147,'#ed368d',0,24);g.fillStyle='#000';g.beginPath();g.arc(0,0,111,0,TAU);g.fill();
  g.strokeStyle='#f1d8e1';g.lineWidth=3;g.beginPath();g.arc(0,0,96,0,TAU);g.stroke();
  star(g,0,0,58,cream,0,8);g.restore();
  text(g,'THAN BEFORE',640,464,30,faces.serif,{fill:'#f2ccdb',width:420});
}
function stencil(g,t) {
  // Original polygon glyphs, not a filtered font. Defined alphabet is SIGNAL only.
  const glyphs={
    S:['M0 0H94V26H30V48H94V130H0V104H65V78H0Z'],
    I:['M0 0H90V25H59V105H90V130H0V105H30V25H0Z'],
    G:['M0 0H94V26H29V104H65V80H49V55H94V130H0Z'],
    N:['M0 130V0H27L66 70V0H94V130H67L28 60V130Z'],
    A:['M0 130V28L27 0H67L94 28V130H65V81H29V130ZM29 54H65V28H29Z'],
    L:['M0 0H29V104H94V130H0Z'],
  };
  g.save();g.translate(94,169);g.transform(1.56,0,-.20,1.56,0,0);
  [...'SIGNAL'].forEach((ch,i)=>{
    g.save();g.translate(i*117,0);const p=new Path2D(glyphs[ch][0]);g.fillStyle=cream;g.fill(p,'evenodd');
    g.globalCompositeOperation='destination-out';g.fillStyle='#000';g.beginPath();g.moveTo(-8,112);g.lineTo(96,8);g.lineTo(96,16);g.lineTo(-8,120);g.fill();g.restore();
  });g.restore();
  text(g,'TRANSMISSION / SIGNAL',640,425,28,faces.sans,{fill:'#ef1644',weight:'bold',width:690});
}
function contours(g,t) {
  const c=makeCanvas(),q=c.getContext('2d');
  for(let i=11;i>=0;i--){
    const x=640+Math.sin(i*.85+t)*57, y=272+Math.cos(i*.7+t)*43;
    q.save();q.translate(640,272);q.rotate((i-5)*.014);q.scale(1+(i-5)*.022,1+(i-5)*.035);q.translate(-640,-272);
    text(q,'SIGNAL',x,y,284,faces.rounded,{fill:null,strokes:[[['#ba245f','#4478c5','#c6b844','#589d69'][i%4],1.7]],width:1030,stretch:true});q.restore();
  }
  text(q,'SIGNAL',640,272,284,faces.rounded,{fill:null,strokes:[['#dddace',3]],width:1030,stretch:true});
  for(let y=0;y<H;y+=2){ const dx=Math.sin(y*.036+t*1.8)*7+Math.sin(y*.067-t)*4;g.drawImage(c,0,y,W,2,dx,y,W,2); }
}

function rainbow(g,t) {
  const colors=['#d03cba','#4248a0','#38a9c1','#41cb71','#d5c332','#db6350'];
  g.save();g.translate(883,272);g.rotate(Math.sin(t)*.025);
  colors.forEach((col,i)=>{g.beginPath();g.arc(0,0,173-i*16,Math.PI,0);g.strokeStyle=col;g.lineWidth=3;g.stroke();});g.restore();
  text(g,'Human',568,225,201,faces.rounded,{fill:'#000',strokes:[['#ac35a0',21],['#000',16],['#52cda8',11],['#000',6],['#efdfa4',2]],width:870});
  text(g,'after all',656,385,167,faces.rounded,{fill:'#000',strokes:[['#ac35a0',20],['#000',15],['#52cda8',10],['#000',5],['#efdfa4',2]],width:985});
  [0,1,2].forEach(i=>star(g,1060+i*27,83+(i%2)*21,7,colors[i+1],t*.2,5));
}
function collision(g,t) {
  const xx=Math.sin(t)*12;
  text(g,'EVERY',394+xx,183,221,faces.heavy,{fill:'#d09b1c',width:680});
  text(g,'THING',784-xx,341,239,faces.heavy,{fill:'#bf078f',width:800});
  text(g,'Everything',683,241,98,faces.serif,{fill:'#eedcdb',width:595});
  text(g,'EVERYTHING',770,299,47,faces.serif,{fill:'#a66c72',width:600});
  stroke(g,[[198,250],[1116,250]],'#a97187',1);
  text(g,'all at once',381,422,68,faces.script,{fill:'#dfaf59',width:426});
}
function screen(g,t) {
  const d=mask('rgb-more',m=>{text(m,'MORE',640,270,370,faces.heavy,{fill:'#fff',width:1040});});
  g.save();g.translate(640,272);g.rotate(-.12+.015*Math.sin(t));g.translate(-640,-272);g.globalCompositeOperation='screen';
  const channels=[['#ff1954',-4,-3],['#1ee69a',4,1],['#4748ff',0,5]];
  channels.forEach(([c,ox,oy],i)=>{
    g.fillStyle=c;
    for(let y=78;y<469;y+=13)for(let x=98;x<1170;x+=13){if(alpha(d,x,y)>150){
      const r=2.4+.5*Math.sin(x*.012+y*.014+t+i);g.beginPath();g.arc(x+ox,y+oy,r,0,TAU);g.fill();
    }}
  });g.restore();
}
function bubble(g,t) {
  g.save();g.translate(640,277);g.rotate(-.06);g.translate(-640,-277);
  text(g,'MORE',640,267,305,faces.rounded,{fill:'#c82e90',strokes:[['#741968',32],['#e7c5d3',24],['#933d76',12],['#f8dcec',5]],width:1050});
  text(g,'and more',723,351,117,faces.script,{fill:'#eed440',strokes:[['#5d1734',13],['#ffe9a5',4]],width:766});
  g.restore();
  g.save();g.translate(1050,129);g.rotate(t*.16);star(g,0,0,49,'#f4cce6',0,4);star(g,0,0,31,'#bb2d89',0,4);g.restore();
  g.save();g.translate(215,383);g.rotate(-.45);g.beginPath();g.ellipse(0,0,97,24,0,0,TAU);g.strokeStyle='#f1c460';g.lineWidth=4;g.stroke();g.restore();
}
const draw = [neon,marquee,varsity,gothic,signature,emblem,stencil,contours,rainbow,collision,screen,bubble];
function render(index,t=0,canvas) {
  const g=canvas.getContext('2d');clear(g);draw[index](g,t);
  // Flatten transparent cutouts onto black, including custom stencil counters.
  g.save();g.globalCompositeOperation='destination-over';g.fillStyle='#000';g.fillRect(0,0,W,H);g.restore();
}
window.TypographyStudy={W,H,identity,faces,render};
