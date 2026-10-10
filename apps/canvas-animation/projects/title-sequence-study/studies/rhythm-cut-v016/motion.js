/* Project-specific edit. The ornate surfaces stay intact; motion controls visibility. */
const WIDTH=1672,HEIGHT=941,FPS=24,FRAMES=144;
const clamp=x=>Math.max(0,Math.min(1,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
const smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
const surface=(w=WIDTH,h=HEIGHT)=>Object.assign(document.createElement('canvas'),{width:w,height:h});
let nextInks,keepPlate,keepReveal,keepMask;

function prepareNext(data){
  // Keep the vector drawing ordered, including its black counters, before separating ink.
  const scale=2,c=surface(WIDTH*scale,HEIGHT*scale),g=c.getContext('2d',{willReadFrequently:true});
  g.scale(scale,scale);
  for(const p of data.paths){const xy=p.transform.match(/[-\d.]+/g)||[0,0];g.save();g.translate(+xy[0],+xy[1]);g.fillStyle=p.fill;g.fill(new Path2D(p.d));g.restore()}
  const src=g.getImageData(0,0,c.width,c.height),keys=['cool','ivory','lime','red'];
  const buffers=Object.fromEntries(keys.map(k=>[k,new ImageData(c.width,c.height)]));
  for(let i=0;i<src.data.length;i+=4){
    const [r,v,b]=src.data.subarray(i,i+3);
    if(r+v+b<6)continue;
    const key=r>v*1.7&&r>b*1.7?'red':v>b*1.6&&r>b*1.6?'lime':r>80&&v>80&&b>60?'ivory':'cool';
    buffers[key].data.set(src.data.subarray(i,i+4),i);
  }
  nextInks=Object.fromEntries(keys.map(k=>{const ink=surface(c.width,c.height);ink.getContext('2d').putImageData(buffers[k],0,0);return[k,ink]}));
}

function drawBillions(g,f){
  // Compress the approved motion while retaining a short assembled hold.
  const t=f<32?.17+f/24*1.5:f<40?2.23:2.52+(f-40)/24*1.2;
  for(const layer of [...layers.filter(l=>l.role!=='letter'),...layers.filter(l=>l.role==='letter')]){
    const p=BILLIONS_POSE(layer,t);if(p.alpha<=0||p.reveal<=0)continue;
    g.save();g.globalCompositeOperation=layer.role==='letter'?'source-over':'lighter';g.globalAlpha=p.alpha;
    g.translate(layer.pivot[0]+p.x,layer.pivot[1]+p.y);g.rotate(p.r);g.scale(p.sx,p.sy);g.translate(-layer.pivot[0],-layer.pivot[1]);
    if(p.reveal<1){g.beginPath();g.ellipse(...layer.pivot,WIDTH*p.reveal,HEIGHT*p.reveal,0,0,Math.PI*2);g.clip()}
    g.drawImage(layer.canvas,layer.x,layer.y);g.restore();
  }
}

function drawNext(g,f){
  const n=f-43;if(n<0||f>98)return;
  // A pair of editorial punches provides a very different cadence from BILLIONS.
  const zoom=n>=22&&n<26?1.22:n>=26&&n<30?1.08:1;
  g.save();g.translate(WIDTH*.53,HEIGHT*.51);g.scale(zoom,zoom);g.translate(-WIDTH*.53,-HEIGHT*.51);
  const poses={
    cool:{dx:-(1-ease(n/8))*520,dy:0,a:clamp(n/3)},
    lime:{dx:-(1-ease((n-3)/9))*1500,dy:(1-ease((n-3)/9))*210,a:clamp((n-3)/2)},
    ivory:{dx:(1-ease((n-5)/8))*1500,dy:-(1-ease((n-5)/8))*210,a:clamp((n-5)/2)},
    red:{dx:(1-ease((n-10)/9))*1500,dy:(1-ease((n-10)/9))*300,a:clamp((n-10)/2)}
  };
  if(n>=31&&n<37){const u=1-ease((n-31)/6);poses.red.dx=-200*u;poses.red.dy=70*u;}
  const exit=ease((n-42)/10);
  for(const [id,p]of Object.entries(poses)){
    if(p.a<=0)continue;
    g.save();g.globalAlpha=p.a;
    const sign=id==='ivory'||id==='red'?1:-1;
    g.translate(p.dx+exit*sign*1800,p.dy-exit*sign*200);
    g.drawImage(nextInks[id],0,0,WIDTH,HEIGHT);g.restore();
  }
  g.restore();
}

const upperKeep=new Path2D('M0 0H1672V422C1200 354 610 430 0 502Z');
const lowerKeep=new Path2D('M0 502C610 430 1200 354 1672 422V941H0Z');
function curvedWipe(q,region,p,reverse){
  if(p<=0)return;
  q.save();q.clip(region);q.fillStyle='white';
  if(p>=1){q.fillRect(0,0,WIDTH,HEIGHT);q.restore();return}
  if(reverse){q.translate(WIDTH,HEIGHT);q.scale(-1,-1)}
  const x=-520+p*(WIDTH+1040);
  q.beginPath();q.moveTo(-1500,-100);q.lineTo(x,-100);
  q.bezierCurveTo(x+500,220,x-500,660,x,HEIGHT+100);
  q.lineTo(-1500,HEIGHT+100);q.closePath();q.fill();q.restore();
}
function drawKeep(g,f){
  const n=f-84;if(n<0)return;
  if(n>=40){g.drawImage(keepPlate,0,0,WIDTH,HEIGHT);return}
  const m=keepMask.getContext('2d');m.setTransform(2,0,0,2,0,0);m.clearRect(0,0,WIDTH,HEIGHT);
  curvedWipe(m,upperKeep,ease((n+1)/15),false);
  curvedWipe(m,lowerKeep,smooth((n-16)/24),true);
  const q=keepReveal.getContext('2d');q.setTransform(2,0,0,2,0,0);q.clearRect(0,0,WIDTH,HEIGHT);
  // Feather visibility only. Applying the artwork after resetting the filter keeps it sharp.
  q.filter='blur(24px)';q.drawImage(keepMask,0,0,WIDTH,HEIGHT);q.filter='none';
  q.globalCompositeOperation='source-in';q.drawImage(keepPlate,0,0,WIDTH,HEIGHT);q.globalCompositeOperation='source-over';
  // Black coverage hides outgoing NEXT only where the curved artwork arrives.
  g.drawImage(keepReveal,0,0,WIDTH,HEIGHT);
}

window.drawFrame=frame=>{
  frame=Math.max(0,Math.min(FRAMES-1,Math.floor(frame)));
  const c=document.querySelector('canvas'),g=c.getContext('2d');
  g.setTransform(c.width/WIDTH,0,0,c.height/HEIGHT,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';g.fillStyle='#000';g.fillRect(0,0,WIDTH,HEIGHT);g.imageSmoothingEnabled=true;g.imageSmoothingQuality='high';
  drawNext(g,frame);
  if(frame<52)drawBillions(g,frame);
  drawKeep(g,frame);
  window.currentFrame=frame;
  document.querySelector('#seek').value=frame;
  document.querySelector('#time').textContent=(frame/FPS).toFixed(2)+' / 6.00 s';
};
