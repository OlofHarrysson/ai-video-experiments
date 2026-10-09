window.MotionStudy=(()=>{
 const K=MotionKit,{W,H,TAU,clamp,rand,shape}=K,cream='#fff3da',pink='#ff278d',green='#8cff42';
 const names=['Neon ignition','Particle pressure','Elastic blackletter','Letter impact','Contour vortex','Cut and shear','RGB rupture','Poster collision'];
 const clocks=names.map(()=>K.timeline());
 const pathLetters={S:[[[90,0],[18,0],[0,18],[0,47],[18,65],[72,65],[90,83],[90,112],[72,130],[0,130]]],I:[[[0,0],[82,0]],[[41,0],[41,130]],[[0,130],[82,130]]],G:[[[90,18],[72,0],[18,0],[0,18],[0,112],[18,130],[90,130],[90,72],[52,72]]],N:[[[0,130],[0,0],[90,130],[90,0]]],A:[[[0,130],[0,32],[45,0],[90,32],[90,130]],[[0,76],[90,76]]],L:[[[0,0],[0,130],[90,130]]]};
 function poly(g,points,f){let lens=[],total=0;for(let i=1;i<points.length;i++){const d=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);lens.push(d);total+=d}let left=total*clamp(f);g.beginPath();g.moveTo(...points[0]);for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],q=Math.min(1,left/lens[i-1]);g.lineTo(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q);left-=lens[i-1];if(left<=0)break}g.stroke()}
 function center(g,scale=1){g.translate(W/2,H/2);g.scale(scale,scale)}
 function neon(g,t,s,e){center(g,1-s.exit*.3);const build=clamp(t/1.15),breakup=Math.sin(clamp((t-1.4)/1.8)*Math.PI)*e;
  [...'SIGNAL'].forEach((ch,i)=>{g.save();g.translate((i*120-345)*1.48,(Math.sin(i*1.9+t*3)*57*breakup));g.rotate(Math.sin(i+t*2)*.18*breakup);g.scale(1.48,1.48);g.translate(0,-65);
  const progress=clamp(build*1.7-i*.13);g.lineJoin='round';g.lineCap='round';
  for(const [color,lw] of [[green,23],['#072306',16],['#d9ffb3',6]]){g.strokeStyle=color;g.lineWidth=lw;pathLetters[ch].forEach(p=>poly(g,p,progress))}g.restore()});
  g.strokeStyle=green;g.lineWidth=2;g.setLineDash([130+300*s.entry,80]);g.lineDashOffset=-t*260;g.strokeRect(-585,-218,1170,436);g.setLineDash([]);
 }
 function particles(g,t,s,e){center(g);const assemble=clamp(t/.95),spread=(1-assemble)**3+Math.sin(clamp((t-1.35)/2.15)*Math.PI)*.62*e+s.exit*.6;
  K.dots('more',18).forEach(([x,y],i)=>{const a=rand(i)*TAU,r=140+rand(i+800)*470;const xx=x+Math.cos(a+t*.6)*r*spread,yy=y+Math.sin(a+t*.6)*r*spread;
  g.strokeStyle=i%4===0?cream:pink;g.lineWidth=2.6;g.beginPath();g.arc(xx,yy,5.5+spread*3,0,TAU);g.stroke()});
 }
 function elastic(g,t,s,e){center(g,.7+.3*s.entry);const bend=(18+55*s.burst)*e;
  for(let i=7;i>=0;i--){shape(g,MotionFonts.overdrive.shape,{fill:i===0?cream:null,stroke:i===0?'#be6cff':i%2?pink:'#4927a2',lineWidth:i===0?2:3,
  map:(x,y)=>[x+Math.sin(y*.019+t*3)*bend*.35+i*4,y+Math.sin(x*.009-t*3.5)*bend+i*7-(1-s.entry)*350+s.exit*320]})}
 }
 function letters(g,t,s,e){center(g);const chars=MotionFonts.faster.letters;chars.forEach((cs,i)=>{const enter=gsap.parseEase('back.out(1.8)')(clamp((t-i*.095)/.65)),out=clamp((t-2.8-i*.06)/.7);
  const flat=cs.flat(),cx=flat.reduce((a,p)=>a+p[0],0)/flat.length;
  g.save();g.translate(cx,0);g.rotate((1-enter)*(i%2?1:-1)*1.6+out*(i%2?1:-1)*2);g.translate(-cx,(1-enter)*(i%2?500:-500)+out*540);
  const stretch=1+Math.sin(t*6+i)*.12*s.burst*e;g.scale(1,stretch);shape(g,cs,{fill:i%2?cream:'#f72e53',stroke:'#080609',lineWidth:5});g.restore()});
 }
 function vortex(g,t,s,e){center(g);const n=17,swirl=(.08+.28*s.burst)*e;
  for(let i=n;i>=0;i--){g.save();const a=(i-n/2)*swirl*Math.sin(t*1.8);g.rotate(a);const sc=.65+i*.044+s.exit*.7;g.scale(sc,sc);g.translate(Math.sin(t*3+i*.5)*20*e,Math.cos(t*2+i*.4)*25*e);
  shape(g,MotionFonts.signal.shape,{stroke:['#ff3294','#35deef','#ffdb36','#acf3b0'][i%4],lineWidth:2,map:(x,y)=>[x+(1-s.entry)*Math.sin(i)*400,y+Math.sin(x*.018+t*3+i*.5)*12*e]});g.restore()}
 }
 const plate=K.canvas();
 function shear(g,t,s,e){const q=plate.getContext('2d');K.clear(q);center(q);shape(q,MotionFonts.becoming.shape,{fill:cream,stroke:'#bb6cff',lineWidth:3});
  for(let y=0;y<H;y+=17){const band=Math.floor(y/17),dx=(1-s.entry)*(band%2?800:-800)+Math.sin(t*9+band*.77)*65*s.burst*e+s.exit*(band%2?600:-600);
  g.drawImage(plate,0,y,W,17,dx,y,W,17);if(band%4===0){g.fillStyle=pink;g.globalAlpha=.5*s.burst;g.fillRect(0,y,W,2);g.globalAlpha=1}}
 }
 function rgb(g,t,s,e){center(g);g.rotate(-.09+Math.sin(t*2)*.12*e);const split=(12+90*Math.sin(t*3)**2*s.burst)*e;
  g.globalCompositeOperation='screen';['#ff174f','#25ffb5','#464cff'].forEach((color,ch)=>{g.fillStyle=color;const a=ch*TAU/3+t*2;
  K.dots('more',15).forEach(([x,y],i)=>{const disperse=(1-s.entry+s.exit)*400;g.beginPath();g.arc(x+Math.cos(a)*split+(rand(i)-.5)*disperse,y+Math.sin(a)*split+(rand(i+99)-.5)*disperse,3.9,0,TAU);g.fill()})});g.globalCompositeOperation='source-over';
 }
 function collision(g,t,s,e){center(g);const beats=[0,.48,.88,1.2,1.48,1.7,1.9,2.06,2.22,2.38,2.54,2.7,2.86,3.02];
  beats.forEach((at,i)=>{if(t<at)return;const age=t-at,p=gsap.parseEase('expo.out')(clamp(age/.25));g.save();g.translate((rand(i+4)-.5)*300*e,(rand(i+44)-.5)*300*e);g.rotate((rand(i+8)-.5)*.7*e);const scale=(.38+rand(i+1)*.5)*(1+(1-p)*2);g.scale(scale,scale);
  shape(g,MotionFonts[i%3===0?'everything':i%3===1?'more':'faster'].shape,{fill:i%3===0?'#f22b79':i%3===1?'#d5ff3f':cream,stroke:'#080809',lineWidth:5});g.restore()});
 }
 const scenes=[neon,particles,elastic,letters,vortex,shear,rgb,collision];
 // Frame boundaries are explicit: 4s -> 2s -> 1s -> half/quarter-second cuts.
 const durations=[4,2,2,1,1,1,1,.5,.5,.5,.5,.5,.5,.25,.25,.25,.25,.25,.25,.25,.25];
 let cursor=0;const order=[0,1,2,3,4,5,6,7,0,4,2,6,3,1,5,7,4,6,0,7,3];
 const cuts=durations.map((duration,i)=>{const c={start:cursor,duration,id:order[i],energy:.45+.85*i/(durations.length-1)};cursor+=duration;return c});
 function render(id,t,c,{energy=1,label=false}={}){const g=c.getContext('2d');K.clear(g);g.save();const s=clocks[id].at(t);scenes[id](g,t,s,energy);g.restore();
  if(label){g.fillStyle='#08080be6';g.fillRect(0,H-35,W,35);g.font='18px system-ui';g.fillStyle='#ddd';g.fillText(String(id+1).padStart(2,'0')+'  '+names[id],22,H-11)}}
 function montage(t,c){const shot=cuts.findLast(s=>t>=s.start)||cuts[0];const local=t-shot.start;
  // Fast shots enter at established shapes and traverse active portions of their motion.
  const st=shot.duration>=2?local*(3.65/shot.duration):.65+local/shot.duration*2.2;
  render(shot.id,st,c,{energy:shot.energy});return shot;}
 gsap.ticker.sleep();return {names,render,montage,cuts,duration:cursor};
})();
