/* Project-owned primitives. No wall-clock state enters an exported frame. */
window.MotionKit=(()=>{
 const W=1280,H=544,TAU=Math.PI*2;
 const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
 const rand=n=>{const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
 const canvas=()=>Object.assign(document.createElement('canvas'),{width:W,height:H});
 function shape(g,contours,{fill=null,stroke=null,lineWidth=2,map=(x,y)=>[x,y]}={}){
  g.beginPath();for(const c of contours){c.forEach(([x,y],i)=>{const p=map(x,y);i?g.lineTo(...p):g.moveTo(...p)});g.closePath()}
  if(fill){g.fillStyle=fill;g.fill('evenodd')}if(stroke){g.strokeStyle=stroke;g.lineWidth=lineWidth;g.lineJoin='round';g.stroke()}
 }
 function timeline(){const state={entry:0,exit:0,burst:0,turn:0};const tl=gsap.timeline({paused:true});
  tl.fromTo(state,{entry:0},{entry:1,duration:.9,ease:'expo.out',immediateRender:false},0)
    .fromTo(state,{burst:0},{burst:1,duration:.9,ease:'power2.inOut',immediateRender:false},1.35)
    .fromTo(state,{turn:0},{turn:1,duration:3.2,ease:'none',immediateRender:false},0)
    .fromTo(state,{exit:0},{exit:1,duration:.65,ease:'power3.in',immediateRender:false},3.05);
  return {at(t){tl.totalTime(clamp(t,0,3.7),true);return state},tl};
 }
 const masks=new Map();function dots(key,step=15){const cache=key+step;if(masks.has(cache))return masks.get(cache);
 const c=canvas(),g=c.getContext('2d');g.translate(W/2,H/2);shape(g,MotionFonts[key].shape,{fill:'#fff'});const d=g.getImageData(0,0,W,H).data,pts=[];
 for(let y=20;y<H;y+=step)for(let x=20;x<W;x+=step)if(d[(y*W+x)*4+3]>128)pts.push([x-W/2,y-H/2]);masks.set(cache,pts);return pts;}
 function clear(g,color='#050507'){g.resetTransform();g.globalAlpha=1;g.globalCompositeOperation='source-over';g.shadowBlur=0;g.fillStyle=color;g.fillRect(0,0,W,H)}
 return {W,H,TAU,clamp,rand,canvas,shape,timeline,dots,clear};
})();
