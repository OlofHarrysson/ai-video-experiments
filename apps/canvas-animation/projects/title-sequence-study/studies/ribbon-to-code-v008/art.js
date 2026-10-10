window.RibbonArt=(()=>{
 const W=1536,H=1024,FPS=30,FRAMES=240,TAU=Math.PI*2;
 const contexts=new WeakMap(),samples=new Map();
 function sample(shape){
  if(samples.has(shape.id))return samples.get(shape.id);
  let p=shape.start,result=[],distance=0;
  for(const c of shape.curves){
   const span=Math.hypot(c[0]-p[0],c[1]-p[1])+Math.hypot(c[2]-c[0],c[3]-c[1])+Math.hypot(c[4]-c[2],c[5]-c[3]),steps=Math.max(24,Math.ceil(span/3));
   for(let i=0;i<=steps;i++){
    if(result.length&&i===0)continue;
    const t=i/steps,u=1-t,x=u*u*u*p[0]+3*u*u*t*c[0]+3*u*t*t*c[2]+t*t*t*c[4],y=u*u*u*p[1]+3*u*u*t*c[1]+3*u*t*t*c[3]+t*t*t*c[5];
    const dx=3*u*u*(c[0]-p[0])+6*u*t*(c[2]-c[0])+3*t*t*(c[4]-c[2]),dy=3*u*u*(c[1]-p[1])+6*u*t*(c[3]-c[1])+3*t*t*(c[5]-c[3]),len=Math.hypot(dx,dy)||1;
    if(result.length){const q=result.at(-1);distance+=Math.hypot(x-q.x,y-q.y);}
    result.push({x,y,nx:-dy/len,ny:dx/len,s:distance});
   }p=[c[4],c[5]];
  }
  if(shape.returning){
   // Return the lanes around the tip instead of clipping them with a round mask.
   const original=result,radius=shape.width*.265,loop=[];
   for(const p of original)loop.push({x:p.x+p.nx*radius,y:p.y+p.ny*radius});
   const end=original.at(-1),start=original[0];
   for(let i=1;i<=40;i++){const a=i*Math.PI/40;loop.push({x:end.x+radius*(end.nx*Math.cos(a)+end.ny*Math.sin(a)),y:end.y+radius*(end.ny*Math.cos(a)-end.nx*Math.sin(a))});}
   for(const p of [...original].reverse().slice(1))loop.push({x:p.x-p.nx*radius,y:p.y-p.ny*radius});
   for(let i=1;i<=40;i++){const a=i*Math.PI/40;loop.push({x:start.x-radius*(start.nx*Math.cos(a)+start.ny*Math.sin(a)),y:start.y-radius*(start.ny*Math.cos(a)-start.nx*Math.sin(a))});}
   distance=0;
   result=loop.map((p,i)=>{const prev=loop[(i+loop.length-2)%(loop.length-1)],next=loop[(i+1)%(loop.length-1)];const dx=next.x-prev.x,dy=next.y-prev.y,len=Math.hypot(dx,dy)||1;if(i)distance+=Math.hypot(p.x-loop[i-1].x,p.y-loop[i-1].y);return {...p,nx:-dy/len,ny:dx/len,s:distance};});
  }
  for(let i=0;i<result.length;i++){
   const p=result[i],a=result[Math.max(0,i-2)],b=result[Math.min(result.length-1,i+2)];p.t=p.s/distance;
   p.curvature=(a.nx*b.ny-a.ny*b.nx)/Math.max(1,Math.hypot(a.x-b.x,a.y-b.y));
  }
  const curvatures=result.map(p=>p.curvature),closed=Math.hypot(result[0].x-result.at(-1).x,result[0].y-result.at(-1).y)<2;
  for(let i=0;i<result.length;i++){
   let sum=0,weight=0;
   for(let j=-18;j<=18;j++){let k=i+j;if(closed)k=(k+result.length-1)%(result.length-1);else k=Math.max(0,Math.min(result.length-1,k));const w=Math.exp(-j*j/110);sum+=curvatures[k]*w;weight+=w;}
   const t=result[i].t;result[i].curvature=sum/weight*(closed?1:Math.min(1,t*18,(1-t)*18));
  }
  samples.set(shape.id,result);return result;
 }
 function mesh(frame,amount=1,isolate=''){
  const phase=((frame%FRAMES)+FRAMES)%FRAMES/FRAMES*TAU,vertices=[];
  const add=(p,u,s,kind,curvature)=>vertices.push(p[0],p[1],p[2],u,s,kind,curvature);
  for(const shape of RibbonGeometry){
   if(isolate&&(shape.glyph||shape.id)!==isolate)continue;
   const points=sample(shape),cross=2;
   function at(p,u){
    const t=p.t,roll=Math.max(-1.08,Math.min(1.08,shape.roll[0]+shape.roll[1]*Math.sin(t*TAU+shape.phase)+shape.roll[2]*Math.sin(t*TAU*2+shape.phase*.7)+amount*shape.roll[3]*(Math.sin(phase*4-t*TAU+shape.phase)-Math.sin(-t*TAU+shape.phase))));
    const taper=shape.accent?Math.pow(Math.max(0,Math.sin(Math.PI*t)),.28):1;
    const width=shape.width*(shape.returning?.47:1)*taper*(1+.035*Math.sin(t*TAU*2+shape.phase));
    // A broad, nearly planar strip rolls locally. Its projection compresses the
    // parallel lanes while their depth changes continuously at real crossings.
    const lateral=u*width*.5*Math.cos(roll),z=u*width*.5*Math.sin(roll)+(shape.z||0)*(shape.accent?taper:1)+8*Math.sin(t*TAU+shape.phase);
    const ripple=amount*4*(Math.sin(phase*4-t*TAU*2+shape.phase)-Math.sin(-t*TAU*2+shape.phase))*Math.sin(Math.PI*t);
    return [p.x+p.nx*(lateral+ripple),p.y+p.ny*(lateral+ripple),z];
   }
   for(let j=0;j<points.length-1;j++)for(let k=0;k<cross;k++){
    const u0=k/cross*2-1,u1=(k+1)/cross*2-1,p=points[j],q=points[j+1];
    const a=at(p,u0),b=at(p,u1),c=at(q,u1),d=at(q,u0),kind=shape.returning?2:shape.accent?1:0;
    add(a,u0,p.t*TAU,kind,p.curvature);add(b,u1,p.t*TAU,kind,p.curvature);add(c,u1,q.t*TAU,kind,q.curvature);add(a,u0,p.t*TAU,kind,p.curvature);add(c,u1,q.t*TAU,kind,q.curvature);add(d,u0,q.t*TAU,kind,q.curvature);
   }
   const first=points[0],last=points.at(-1);
   if(!shape.accent&&Math.hypot(first.x-last.x,first.y-last.y)>2){
    for(const [p,sign]of [[first,-1],[last,1]]){
     const radius=shape.width*.5*(1+.035*Math.sin(p.t*TAU*2+shape.phase));
     function cap(a,r){const q=at(p,r*Math.sin(a));q[0]+=p.ny*sign*radius*r*Math.cos(a);q[1]-=p.nx*sign*radius*r*Math.cos(a);return q;}
     for(let j=0;j<48;j++){
      const a=-Math.PI/2+j*Math.PI/48,b=a+Math.PI/48,r0=0,r1=1;
      const aa=cap(a,r0),bb=cap(a,r1),cc=cap(b,r1),dd=cap(b,r0);
      add(aa,r0,p.t*TAU,3,Math.sin(a));add(bb,r1,p.t*TAU,3,Math.sin(a));add(cc,r1,p.t*TAU,3,Math.sin(b));add(aa,r0,p.t*TAU,3,Math.sin(a));add(cc,r1,p.t*TAU,3,Math.sin(b));add(dd,r0,p.t*TAU,3,Math.sin(b));
     }
    }
   }
  }
  return new Float32Array(vertices);
 }
 const vertex=`#version 300 es
 in vec3 position;in vec4 uv;uniform vec2 shadowOffset;uniform float shadowDepth;out vec4 v;
 void main(){v=uv;gl_Position=vec4((position.x+shadowOffset.x)/768.-1.,1.-(position.y+shadowOffset.y)/512.,-(position.z+shadowDepth)/400.,1.);}`;
 const fragment=`#version 300 es
 precision highp float;in vec4 v;uniform float phase;uniform float strength;uniform float shadow;uniform float flatMode;out vec4 color;
 float band(float x,float a,float b,float aa){return smoothstep(a-aa,a+aa,x)*(1.-smoothstep(b-aa,b+aa,x));}
 void main(){
  if(shadow>.5){color=vec4(.001,.003,.015,.66);return;}
  float u=v.x,s=v.y,kind=v.z;
  float bias=kind<.5?.19*tanh(v.w*100.):0.;
  float travel=.09*strength*(sin(s*2.-phase*6.)-sin(s*2.));
  float d=kind<.5?abs(u-bias):kind>2.5?abs(u):(u+1.)*.5;
  d+=travel*(1.-smoothstep(.7,1.,abs(u)));
  float aa=max(fwidth(d)*.65,.0004);
  float broad=kind<.5?smoothstep(-.12,.12,u):kind>2.5?smoothstep(-.6,.6,v.w):kind<1.5?1.:.5+.5*sin(s);
  float white=band(d,mix(.08,.04,broad),mix(.16,.28,broad),aa)
             +band(d,mix(.22,.37,broad),mix(.31,.62,broad),aa)
             +band(d,mix(.37,.72,broad),mix(.44,.86,broad),aa)
             +(1.-broad)*(band(d,.50,.61,aa)+band(d,.68,.75,aa));
  white=clamp(white,0.,1.);
  float edge=kind>2.5?d:abs(u);
  white*=1.-smoothstep(.93,.98,edge);
  vec3 blue=mix(vec3(.002,.10,.88),vec3(.002,.32,1.),.5+.5*cos(d*2.8));
  float hatch=pow(.5+.5*cos(d*188.),22.);blue*=1.-hatch*.22;
  vec3 ivory=vec3(.966,.956,.905);
  vec3 ink=mix(blue,ivory,white);
  ink=mix(ink,vec3(.001,.006,.024),smoothstep(.97,1.,edge)*.8);
  float light=.94+.06*cos(u*1.5);
  if(flatMode>.5){ink=vec3(.93,.93,.87);light=1.;}
  color=vec4(ink*light,1.);
 }`;
 function setup(target){
  if(contexts.has(target))return contexts.get(target);
  const gl=target.getContext('webgl2',{antialias:true,preserveDrawingBuffer:true,alpha:false});if(!gl)throw new Error('WebGL2 is required for the ribbon study.');
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));gl.useProgram(program);
  const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
  for(const [name,offset,size]of [['position',0,3],['uv',12,4]]){const loc=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,gl.FLOAT,false,28,offset);}
  const uniforms=Object.fromEntries(['phase','strength','shadow','shadowOffset','shadowDepth','flatMode'].map(n=>[n,gl.getUniformLocation(program,n)]));
  const state={gl,buffer,uniforms};contexts.set(target,state);return state;
 }
 function draw(target,frame=0,options={}){
  const {intensity=1,isolate='',flat=false}=options,f=intensity===0?0:frame;
  const {gl,uniforms:u}=setup(target),data=mesh(f,intensity,isolate);
  gl.viewport(0,0,target.width,target.height);gl.clearColor(.003,.015,.045,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);
  gl.bufferData(gl.ARRAY_BUFFER,data,gl.DYNAMIC_DRAW);gl.uniform1f(u.phase,((f%240)+240)%240/240*TAU);gl.uniform1f(u.strength,intensity);gl.uniform1f(u.flatMode,flat?1:0);
  gl.depthMask(false);gl.disable(gl.DEPTH_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.uniform1f(u.shadow,1);gl.uniform2f(u.shadowOffset,5,7);gl.uniform1f(u.shadowDepth,-5);gl.drawArrays(gl.TRIANGLES,0,data.length/7);
  gl.depthMask(true);gl.enable(gl.DEPTH_TEST);gl.disable(gl.BLEND);gl.uniform1f(u.shadow,0);gl.uniform2f(u.shadowOffset,0,0);gl.uniform1f(u.shadowDepth,0);gl.drawArrays(gl.TRIANGLES,0,data.length/7);
  return {triangles:data.length/21,error:gl.getError()};
 }
 function svg(){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024">${RibbonGeometry.map(s=>`<path id="${s.id}" d="M${s.start.join(' ')} ${s.curves.map(c=>'C'+c.join(' ')).join(' ')}" fill="none" stroke="#135dff" stroke-width="${s.width}" stroke-linecap="round"/>`).join('')}</svg>`;}
 return {draw,svg,mesh,W,H,FPS,FRAMES};
})();
