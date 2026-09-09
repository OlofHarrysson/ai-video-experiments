import fs from 'node:fs/promises';
await fs.copyFile('node_modules/gsap/dist/gsap.min.js','assets/gsap.min.js');
const manifest=JSON.parse(await fs.readFile('assets/cels/manifest.json','utf8'));
const celHTML=Object.entries(manifest).map(([name,m])=>`<img id="${name}" class="cel" src="assets/cels/${name}.png" width="${m.width}" height="${m.height}" alt="${name}">`).join('\n');
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080"><title>Big Softie</title><script src="assets/gsap.min.js"></script><style>
*{box-sizing:border-box;margin:0}html,body{width:1920px;height:1080px;overflow:hidden;background:#273522}#film{width:1920px;height:1080px;position:relative;overflow:hidden}#world{position:absolute;width:1920px;height:1080px;transform-origin:0 0}.plate{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}.cel{position:absolute;left:0;top:0;transform-origin:0 0;opacity:0}.shadow{position:absolute;left:0;top:0;width:100px;height:24px;border-radius:50%;background:rgba(36,37,19,.24);filter:blur(9px);transform-origin:50% 50%}#ball{position:absolute;left:0;top:0;width:66px;height:66px;border-radius:50%;background:radial-gradient(circle at 33% 28%,#da9274 0%,#b86048 55%,#834538 100%);border:3px solid #6b4935;box-shadow:inset -7px -8px 0 #934f3b;transform-origin:center}#ball:after{content:'';position:absolute;inset:9px;border:2px dashed #9c5942;border-radius:50%;opacity:.5}#title{position:absolute;left:120px;top:155px;color:#263a2e;font-family:Georgia,serif;font-size:98px;font-weight:normal;line-height:1.1;letter-spacing:-3px;text-shadow:0 1px 5px #f6deb6;opacity:0}
</style></head><body><div id="film" data-composition-id="big-softie" data-width="1920" data-height="1080" data-duration="19.5"><div id="picture" class="clip" data-start="0" data-duration="19.5" data-track-index="0" data-layout-allow-overflow><div id="world"><img class="plate" src="assets/source/park.png" alt="Sunlit dog park"><div id="puppy-shadow" class="shadow"></div><div id="rott-shadow" class="shadow"></div><div id="ball-shadow" class="shadow"></div>${celHTML}<div id="ball"></div></div><div id="title" data-layout-allow-overlap>Big Softie</div></div><audio id="score" src="assets/score-master.wav" data-start="0" data-duration="19.5" data-track-index="5" data-volume="0.8"></audio></div><script>
const M=${JSON.stringify(manifest)};
const E=Object.fromEntries(Object.keys(M).map(k=>[k,document.getElementById(k)]));
const el=id=>document.getElementById(id), clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), mix=(a,b,t)=>a+(b-a)*t, smooth=t=>{t=clamp(t);return t*t*(3-2*t)};
function draw(name,x,y,s,flip=false,rotation=0){if(flip)name=name+'-left';const m=M[name],e=E[name];e.style.opacity=1;const xx=x-m.width*s/2;const yy=y-m.height*s;e.style.transform='translate('+ xx+'px,'+yy+'px) scale('+s+','+s+')';}
function shadow(id,x,y,w,air=0){const e=el(id);e.style.opacity=.9-air*.007;e.style.transform='translate('+(x-50)+'px,'+(y-12)+'px) scale('+w/100+','+(1-air*.006)+')';}
function camera(scale,x,y){el('world').style.transform='translate('+x+'px,'+y+'px) scale('+scale+')';}
function film(t){
 const q=Math.floor((t+0.00001)*12)/12;
 Object.values(E).forEach(e=>e.style.opacity=0);
 ['puppy-shadow','rott-shadow','ball-shadow','ball'].forEach(id=>el(id).style.opacity=0);
 el('world').style.opacity=1;el('title').style.opacity=0;
 const py=855,ry=840;
 let px=520,rx=1330,pp='puppy-acting-0',rp='rott-bow-0',ps=.65,rs=1.30,pair=0,rair=0,ballx=900,bally=857,flipP=false,flipR=false;
 camera(1,0,0);
 if(q<2.25){ // Puppy enters from the gate; distant big dog waits in same position.
  px=mix(-170,510,smooth(q/2.0));
  if(q<1.92){const f=Math.floor(q*6)%4;pp='puppy-run-'+f;ps=.68;pair=[75,0,0,20][f];}
  rx=1330;rs=1.30;shadow('rott-shadow',rx,ry,460);draw(rp,rx,ry,rs);
  camera(1.06,-25,-35);
 }else if(q<3.75){ // Reveal the height difference; hold the line of action.
  px=520;rx=1330;
  pp=q<2.75?'puppy-acting-0':'puppy-acting-1';
  if(q>=2.75)px=520-18*smooth((q-2.75)/.4);
  shadow('rott-shadow',rx,ry,460);draw(rp,rx,ry,rs);
 }else if(q<5.0){ // A close reaction preserves puppy on left looking right.
  pp='puppy-acting-1';px=500;camera(1.8,-380,-570);
  shadow('rott-shadow',rx,ry,460);draw(rp,rx,ry,rs);
 }else if(q<7.25){ // The large dog lowers himself to invite play.
  const u=q-5;rp=u<.35?'rott-bow-0':u<.6?'rott-bow-1':'rott-bow-'+(2+Math.floor((u-.6)*4)%2);
  pp=u<1.1?'puppy-acting-1':'puppy-acting-2';px=510;
  camera(1.10,-155,-85);
  shadow('rott-shadow',rx,ry,460);draw(rp,rx,ry,rs);
 }else if(q<8.5){ // Puppy answers the bow, with anticipation before the chase.
  rp='rott-bow-'+(2+Math.floor(q*4)%2);pp=q<7.58?'puppy-acting-2':'puppy-acting-3';
  px=540;camera(1.04,-35,-35);
  shadow('rott-shadow',rx,ry,460);draw(rp,rx,ry,rs);
 }else if(q<10.5){ // Puppy turns left and invites pursuit; Rottweiler follows from his established position.
  const u=q-8.5;const f=Math.floor(u*6)%4;
  px=540-1000*u;rx=1330-1000*u;flipP=true;
  pp='puppy-run-'+f;ps=.68;pair=[75,0,0,20][f];
  rp='rott-run-'+((f+2)%4);rs=1.04;rair=[88,0,0,15][(f+2)%4];
  ballx=px+240;bally=850-50*Math.abs(Math.sin(u*Math.PI*2));
  shadow('rott-shadow',rx,ry,450,rair);draw(rp,rx,ry-rair,rs,true);
  camera(1,0,0);
 }else if(q<13.25){ // Return right, then each dog eases to a planted stop.
  const u=q-10.5;
  const travel=(t,delay)=>{const d=2.75-delay,v=clamp(t-delay,0,d);return 870*(Math.min(t,delay)+v-v*v/(2*d));};
  px=-140+travel(u,.6);rx=-860+travel(u,1.25);
  const pf=Math.floor(travel(u,.6)/145)%4,rf=(Math.floor(travel(u,1.25)/145)+2)%4;
  const lift=1-smooth((u-1.9)/.65);
  pp='puppy-run-'+pf;ps=.68;pair=[75,0,0,20][pf]*lift;
  rp='rott-run-'+rf;rs=1.04;rair=[88,0,0,15][rf]*lift;
  shadow('rott-shadow',rx,ry,450,rair);draw(rp,rx,ry-rair,rs);
  camera(1.04,-38,-35);
 }
 if(q<13.25){shadow('puppy-shadow',px,py,250,pair);draw(pp,px,py-pair,ps,flipP);el('ball').style.opacity=q<8.5?1:0;el('ball').style.transform='translate('+(ballx-33)+'px,'+(bally-66)+'px) rotate('+(q>=8.5?(q-8.5)*330:0)+'deg)';if(q<8.5)shadow('ball-shadow',ballx,857,62,857-bally);}
 else {
  // Full-body intermediate drawings stay on the same park plate and ground line.
  const poses=[[13.25,'a',850],[13.75,'b',795],[14.0,'c',790],[14.5,'d',790],[14.75,'e',790],[15.25,'f',790],[15.5,'g',815]];
  const pose=poses.filter(p=>q>=p[0]).at(-1),name='settle-'+pose[1],e=E[name];
  shadow('rott-shadow',875,840,650);shadow('puppy-shadow',1315,842,300);
  e.style.opacity=1;e.style.transform='translate(450px,'+(840-pose[2]*.64)+'px) scale(.64)';
  const push=smooth((t-15.5)/3.5),z=mix(1.04,1.12,push);
  camera(z,-38-1200*(z-1.04),-35-800*(z-1.04));
  el('title').style.opacity=smooth((t-16.5)/.8);
 }
}
const driver={t:0};const tl=gsap.timeline({paused:true});tl.to(driver,{t:19.5,duration:19.5,ease:'none',onUpdate:()=>film(driver.t)});window.renderFilm=film;film(0);window.__timelines=window.__timelines||{};window.__timelines['big-softie']=tl;
</script></body></html>`;
await fs.writeFile('index.html',html);
console.log('Built 19.5-second composition with',Object.keys(manifest).length,'cels');
