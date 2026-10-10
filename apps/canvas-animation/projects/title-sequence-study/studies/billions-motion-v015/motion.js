const W=1672,H=941,DURATION=3,FPS=24;
const clamp=(x)=>Math.max(0,Math.min(1,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
const smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
const back=x=>{x=clamp(x)-1;return 1+2.2*x*x*x+1.2*x*x};
window.poseFor=(layer,t)=>{
 const p={x:0,y:0,r:0,sx:1,sy:1,alpha:1,reveal:1};
 if(layer.role==='letter'){
  const i=['B','I1','L1','L2','I2','O','N','S'].indexOf(layer.id),start=i*.067,u=clamp((t-start)/.48),land=back(u);
  p.x=(1-land)*(i<4?-100:100);p.y=(1-land)*(i%2?-600:560);p.r=(1-land)*(i%2?-.25:.25);p.sx=.72+.28*ease(u);p.sy=1.35-.35*ease(u);p.alpha=clamp(u*6);
  // Keep each letter seated once landed; the ornaments carry the next beat.
  const exit=ease((t-(2.65+i*.018))/.29);p.y+=exit*(i%2?750:-750);p.x+=exit*(i-3.5)*65;p.r+=exit*(i%2?.3:-.3);
 }else if(layer.role==='seal'){
  const u=back((t-.40)/.86);p.sx=p.sy=Math.max(.04,u);p.r=(1-ease((t-.40)/1.55))*(layer.id.includes('left')?-2.3:2.3);p.alpha=clamp((t-.4)*8);
 }else if(layer.id==='crown'){
  const u=back((t-.30)/1.0);p.sy=Math.max(.01,u);p.sx=.45+.55*ease((t-.3)/.85);p.r=(1-ease((t-.3)/1.1))*.26;p.alpha=clamp((t-.3)*8);
 }else if(layer.role==='ribbon'){
  const u=ease((t-.72)/1.05);p.reveal=u;p.sy=.35+.65*back((t-.72)/1.05);p.r=(1-u)*(layer.id.includes('left')?-.15:.15);p.alpha=clamp((t-.72)*8);
 }else{p.reveal=ease((t-.92)/.70);p.alpha=smooth((t-.98)/.24);}
 if(layer.role!=='letter'){
  const exit=ease((t-2.69)/.31);p.sx*=1+exit*.28;p.sy*=1+exit*.5;p.alpha*=1-ease((t-2.52)/.18);
 }
 return p;
};
window.drawFrame=(frame,{assembled=false}={})=>{
 const t=frame/FPS,c=document.querySelector('canvas'),g=c.getContext('2d');g.setTransform(c.width/W,0,0,c.height/H,0,0);g.globalCompositeOperation='source-over';g.globalAlpha=1;g.fillStyle='black';g.fillRect(0,0,W,H);g.imageSmoothingEnabled=true;g.imageSmoothingQuality='high';
 for(const layer of [...window.layers.filter(l=>l.role!=='letter'),...window.layers.filter(l=>l.role==='letter')]){
  const p=assembled?{x:0,y:0,r:0,sx:1,sy:1,alpha:1,reveal:1}:poseFor(layer,t);if(p.alpha<=0||p.reveal<=0)continue;
  g.save();g.globalCompositeOperation=layer.role==='letter'?'source-over':'lighter';g.globalAlpha=p.alpha;g.translate(layer.pivot[0]+p.x,layer.pivot[1]+p.y);g.rotate(p.r);g.scale(p.sx,p.sy);g.translate(-layer.pivot[0],-layer.pivot[1]);
  if(p.reveal<1){g.beginPath();const cx=layer.pivot[0],cy=layer.pivot[1];g.ellipse(cx,cy,W*p.reveal,H*p.reveal,0,0,Math.PI*2);g.clip();}
  g.drawImage(layer.canvas,layer.x,layer.y);g.restore();
 }
 g.globalCompositeOperation='source-over';g.globalAlpha=1;window.currentFrame=frame;document.querySelector('#seek').value=frame;document.querySelector('#time').textContent=t.toFixed(2)+' s';
};
