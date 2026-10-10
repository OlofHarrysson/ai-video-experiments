/* Generated silhouettes become editable vectors; every displayed pixel below
   is drawn from those paths. Reference PNGs are never loaded by this renderer. */
window.LetteringArt=(()=>{
 const W=768,H=512,D=2,canvas=(w,h)=>Object.assign(document.createElement('canvas'),{width:w,height:h});
 const hit=canvas(1,1).getContext('2d'),dotPositions=new Map();
 const gpu=canvas(W*D,H*D),gl=gpu.getContext('webgl2',{alpha:true,premultipliedAlpha:false,preserveDrawingBuffer:true});
 if(!gl)throw Error('WebGL 2 is required.');
 const shapes={};
 const namespace='http://www.w3.org/2000/svg';
 function movePath(d,s,tx,ty){let index=0;return d.replace(/[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?/g,n=>{const v=Number(n)*s+(index++%2?ty:tx);return v.toFixed(4)})}
 for(const [id,source]of Object.entries(CustomLettering)){
  const svg=document.createElementNS(namespace,'svg'),group=document.createElementNS(namespace,'g');svg.append(group);document.body.append(svg);
  const parts=source.paths.map(p=>{const v=(p.transform.match(/[-\d.]+/g)||[0,0]).map(Number);const d=movePath(p.d,1,v[0],v[1]);const el=document.createElementNS(namespace,'path');el.setAttribute('d',d);group.append(el);return {d,el}});
  const b=group.getBBox(),s=Math.min(690/b.width,434/b.height),tx=384-(b.x+b.width/2)*s,ty=248-(b.y+b.height/2)*s;
  const result=parts.map((p,index)=>{const b=p.el.getBBox();return {d:movePath(p.d,s,tx,ty),cx:(b.x+b.width/2)*s+tx,cy:(b.y+b.height/2)*s+ty,box:[b.x*s+tx,b.y*s+ty,b.width*s,b.height*s],index}});svg.remove();
  const d=result.map(p=>p.d).join(' ');shapes[id]={id,d,path:new Path2D(d),transform:[s,tx,ty],parts:result.map(p=>({...p,path:new Path2D(p.d)}))};
 }
 const highlights=Object.fromEntries(Object.entries(window.LetteringHighlights||{}).map(([k,paths])=>[k,paths.map(p=>{const [s,tx,ty]=shapes.script.transform,[x,y]=(p.transform.match(/[-\d.]+/g)||[0,0]).map(Number);return new Path2D(movePath(p.d,s,tx+x*s,ty+y*s));})]));
 const vs=`#version 300 es
 in vec2 a;out vec2 uv;void main(){uv=a;gl_Position=vec4(a.x*2.-1.,1.-a.y*2.,0.,1.);}`;
 const fs=`#version 300 es
 precision highp float;uniform sampler2D map;uniform float phase,variant;uniform int material;in vec2 uv;out vec4 outColor;
 const vec2 SIZE=vec2(1536.,1024.);
 vec4 field(vec2 p){vec2 pos=p*SIZE-.5;ivec2 ij=clamp(ivec2(floor(pos)),ivec2(0),ivec2(SIZE)-2);vec2 f=fract(pos);return mix(mix(texelFetch(map,ij,0),texelFetch(map,ij+ivec2(1,0),0),f.x),mix(texelFetch(map,ij+ivec2(0,1),0),texelFetch(map,ij+ivec2(1,1),0),f.x),f.y);}
 float line(float x,float center,float width){return exp(-pow((x-center)/width,2.));}
 vec3 bands(float t){
  vec3 c=vec3(.23,.0,.26);
  c=mix(c,vec3(.92,.01,.46),smoothstep(.01,.045,t));
  c=mix(c,vec3(1.,.12,.28),smoothstep(.17,.19,t));
  c=mix(c,vec3(1.,.36,.015),smoothstep(.35,.37,t));
  c=mix(c,vec3(1.,.69,.018),smoothstep(.53,.55,t));
  c=mix(c,vec3(1.,.91,.18),smoothstep(.71,.73,t));
  c=mix(c,vec3(1.,.985,.71),smoothstep(.88,.90,t));
  return c;
 }
 void main(){
  vec2 p=uv*vec2(768.,512.);vec4 f=field(uv);float d=f.x;float aa=max(.22,fwidth(d)*.6);if(d<-.6)discard;
  vec2 grad=f.yz;float width=max(2.,f.w);float t=clamp(d/width,0.,1.);vec2 unit=normalize(grad+vec2(.00001));
  float a=phase*6.283185;vec3 rgb;
  if(material==0){
   float shoulder=clamp((d-1.8)/max(2.,width-1.8),0.,1.);
   vec3 n=normalize(vec3(-grad*cos(shoulder*1.5708)*1.0,max(.10,sin(shoulder*1.5708))));
   vec3 r=reflect(vec3(0.,0.,-1.),n);float horizon=r.y*.82+r.x*.36;
   float facing=dot(n,normalize(vec3(-.4,-.6,.8)));
   rgb=mix(vec3(.13,.0004,.009),vec3(.96,.008,.018),clamp(.28+facing*.75,0.,1.));
   float broad=line(horizon,-.85+phase*1.70,.33);rgb=mix(rgb,vec3(1.,.06,.05),broad*.7);
   float shine=line(horizon,-.85+phase*1.70,.095);rgb=mix(rgb,vec3(1.,.70,.45),shine*.75);
   rgb*=1.-.65*line(horizon,.18,.12);rgb+=line(horizon,.61,.085)*vec3(.72,.07,.045);
   float top=clamp(.5+dot(unit,normalize(vec2(.55,.8)))*.5,0.,1.);
   vec3 gold=mix(vec3(.24,.07,.006),vec3(1.,.86,.27),top);gold=mix(gold,vec3(1.,.98,.81),line(d,.65,.32)*.95);
   rgb=mix(gold,rgb,smoothstep(2.0-aa,2.0+aa,d));
   if(variant>.5)rgb=mix(vec3(.015,.045,.12),vec3(.78,.93,1.),clamp(dot(rgb,vec3(.55,.3,.15)),0.,1.));
  }else if(material==1){
   float plane=floor((p.x+p.y*.85)/99.);float lime=step(.5,mod(plane,3.));
   vec3 silver=mix(vec3(.43,.48,.55),vec3(.92,.95,.97),clamp(.72-p.y*.00065+unit.y*.12,0.,1.));
   vec3 acid=mix(vec3(.40,.68,.015),vec3(.84,1.,.025),clamp(.7+unit.x*.22-unit.y*.1,0.,1.));
   rgb=mix(silver,acid,lime);
   float facet=step(.6,fract((p.x-p.y*.9+38.)/170.));rgb*=mix(.82,1.08,facet);
   float bevel=1.-smoothstep(.8,3.,d);rgb=mix(rgb,vec3(.9,.97,1.)*(.5+.5*dot(unit,normalize(vec2(.5,.7)))),bevel*.8);
   float seam=abs(mod(p.x+p.y*.93+phase*4.,154.)-77.);rgb=mix(rgb,vec3(1.,.34,.015),1.-smoothstep(1.0,2.2,seam));
   float sweep=line(p.x-p.y*.30,phase*950.-80.,60.);rgb+=sweep*.19;
   if(variant>.5){rgb=mix(vec3(.02,.035,.07),vec3(.96,.20,.035),lime*.8+.2);rgb+=bevel*.35;}
  }else if(material==2){
   rgb=vec3(1.,.947,.79);
   float edge=1.-smoothstep(.7,1.9,d);rgb=mix(rgb,vec3(.94,.065,.015),edge);
   float blue=line(d,3.7,.8);rgb=mix(rgb,vec3(.005,.15,.78),blue);
   if(variant>.5)rgb=mix(vec3(.005,.015,.04),vec3(1.,.44,.13),dot(rgb,vec3(.3,.5,.2)));
  }else{
   float ribbon=clamp(d/(30.-phase*14.),0.,1.);rgb=bands(ribbon);
   float seams=line(ribbon,.18,.012)+line(ribbon,.36,.012)+line(ribbon,.54,.012)+line(ribbon,.72,.012)+line(ribbon,.89,.012);
   rgb=mix(rgb,vec3(1.,.96,.65),seams*.45);
   if(variant>.5)rgb=rgb.bgr*vec3(.8,1.,1.);
  }
  outColor=vec4(clamp(rgb,0.,1.),smoothstep(-aa,aa,d));
 }`;
 const compile=(kind,source)=>{const s=gl.createShader(kind);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s};
 const program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,vs));gl.attachShader(program,compile(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
 const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([0,0,1,0,0,1,0,1,1,0,1,1]),gl.STATIC_DRAW);const attr=gl.getAttribLocation(program,'a');gl.enableVertexAttribArray(attr);gl.vertexAttribPointer(attr,2,gl.FLOAT,false,0,0);
 const locations=Object.fromEntries(['map','phase','variant','material'].map(n=>[n,gl.getUniformLocation(program,n)]));
 function prepare(id){
  const shape=shapes[id];if(shape.texture)return shape;
  const contours=VectorFields.contours({d:shape.d},0).face;
  const field=VectorFields.field(contours,[0,0,W,H],D),{distance,nx,ny}=field,tw=W*D,th=H*D;
  const sample=(x,y)=>distance[Math.max(0,Math.min(th-1,Math.round(y)))*tw+Math.max(0,Math.min(tw-1,Math.round(x)))];
  const data=new Float32Array(tw*th*4);
  for(let i=0;i<distance.length;i++){
   const x=i%tw,y=Math.floor(i/tw),d=distance[i];let width=d,previous=d;
   if(id==='script'&&d>0&&d<60){for(let step=1;step<=20;step++){const probe=sample(x+nx[i]*D*2*step,y+ny[i]*D*2*step);if(probe<previous)break;width=Math.max(width,probe);previous=probe;}}
   data[i*4]=d;data[i*4+1]=nx[i];data[i*4+2]=ny[i];data[i*4+3]=Math.max(2,width*.98);
  }
  const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA32F,tw,th,0,gl.RGBA,gl.FLOAT,data);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  shape.texture=texture;shape.segmentCount=field.segments;return shape;
 }
 function face(id,phase=0,variant=0){const shape=prepare(id);gl.viewport(0,0,W*D,H*D);gl.useProgram(program);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,shape.texture);gl.uniform1i(locations.map,0);gl.uniform1i(locations.material,Object.keys(shapes).indexOf(id));gl.uniform1f(locations.phase,phase);gl.uniform1f(locations.variant,variant);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.drawArrays(gl.TRIANGLES,0,6);return gpu;}
 function depth(g,id,phase,variant=0,drawPath=shapes[id].path){
  const shape=shapes[id],length={script:12,machine:15,tuscan:6,liquid:15}[id];
  for(let z=length;z>=1;z--){
   g.save();g.translate(z*.60,z*.9);
   const gr=g.createLinearGradient(70,40,580,500);
   const colors=id==='script'?['#210004','#5b0503','#1b0008']:id==='machine'?['#001296','#1248fd','#030322']:id==='tuscan'?['#231205','#ab6918','#2b0808']:['#18001e','#8b005b','#300329'];
   gr.addColorStop(0,colors[0]);gr.addColorStop(.48,colors[1]);gr.addColorStop(1,colors[2]);g.fillStyle=gr;g.fill(drawPath,'evenodd');g.restore();
  }
 }
 function machine(g,phase,variant=0,assembly=1,row=null){
  for(const part of shapes.machine.parts.filter(p=>!row||(row==='wild'?p.cy<250:p.cy>=250))){
   const [x,y,w,h]=part.box,acid=[1,4,7,10,13].includes(part.index);
   const progress=Math.max(0,Math.min(1,assembly*1.35-part.index%4*.10)),offset=Math.pow(1-progress,3)*140,direction=part.index%2?1:-1;
   g.save();g.translate(offset*direction,offset*direction);
   g.save();g.translate(7,9);g.fillStyle='#103bdf';g.fill(part.path,'evenodd');g.restore();
   g.clip(part.path,'evenodd');
   const grad=g.createLinearGradient(x,y,x+w,y+h);
   const colors=acid?(variant?['#ff8c10','#ff4200','#a61500']:['#e8ff86','#c6fa02','#82a400']):(variant?['#ecf7ff','#a2b6cc','#f6ffff']:['#fcffff','#c4cdd1','#f8ffff']);
   grad.addColorStop(0,colors[0]);grad.addColorStop(.52,colors[1]);grad.addColorStop(1,colors[2]);g.fillStyle=grad;g.fillRect(x-1,y-1,w+2,h+2);
   g.fillStyle=acid?'#617c0030':'#031a3522';g.beginPath();g.moveTo(x,y+h);g.lineTo(x+w,y+h);g.lineTo(x+w,y+h*.78);g.lineTo(x+w*.4,y+h*.78);g.closePath();g.fill();
   const sweep=g.createLinearGradient(x-70+phase*200,y,x+20+phase*200,y+h);sweep.addColorStop(0,'#ffffff00');sweep.addColorStop(.5,'#ffffff45');sweep.addColorStop(1,'#ffffff00');g.fillStyle=sweep;g.fillRect(x,y,w,h);
   g.lineWidth=1.4;g.strokeStyle=acid?'#f2ffa5':'#ffffff';g.stroke(part.path);
   g.restore();
  }
 }
 function scriptDetails(g,phase){
  g.save();g.clip(shapes.script.path,'evenodd');
  for(const [name,paths]of Object.entries(highlights)){
   const grad=g.createLinearGradient(80,40,690,420);
   const peak=.12+.76*phase;
   grad.addColorStop(0,name==='warm'?'#ff864820':'#fff9e980');grad.addColorStop(Math.max(.01,peak-.20),name==='warm'?'#ffb85350':'#fff9e9ac');grad.addColorStop(peak,name==='warm'?'#fff3b3a0':'#ffffed');grad.addColorStop(Math.min(.99,peak+.20),name==='warm'?'#ffa55350':'#fff9e9ac');grad.addColorStop(1,name==='warm'?'#ff673c20':'#fff9e980');g.fillStyle=grad;
   for(const p of paths)g.fill(p,'evenodd');
  }
  g.restore();
 }
 function card(target,id,phase=0,options={}){
  const {variant=0,flat=false,scale=1,x=0,y=0,angle=0,focus=[384,256],row=null,mode='material',assembly=1,background='#000',ink='#fff',clear=true}=options,g=target.getContext('2d');
  const selectedPath=row?new Path2D(shapes[id].parts.filter(p=>row==='wild'?p.cy<250:p.cy>=250).map(p=>p.d).join(' ')):shapes[id].path;
  g.save();g.setTransform(1,0,0,1,0,0);if(clear){g.fillStyle=background;g.fillRect(0,0,target.width,target.height);}
  const fit=Math.min(target.width/800,target.height/530)*scale;
  g.translate(target.width/2+x,target.height/2+y);g.rotate(angle);g.scale(fit,fit);g.translate(-focus[0],-focus[1]);
  if(flat||mode==='flat'){g.fillStyle=ink;g.fill(selectedPath,'evenodd');}
  else if(mode==='outline'){
   g.strokeStyle=ink;g.lineWidth=1.4;g.stroke(selectedPath);
  }else if(mode==='dots'){
   const key=id+':'+row;if(!dotPositions.has(key)){const points=[];for(let py=0;py<H;py+=14)for(let px=0;px<W;px+=14){if([[0,0],[-4.4,0],[4.4,0],[0,-4.4],[0,4.4]].every(([dx,dy])=>hit.isPointInPath(selectedPath,px+dx,py+dy,'evenodd')))points.push([px,py]);}dotPositions.set(key,points);}
   for(const [px,py]of dotPositions.get(key)){
    const hot=(px/14+py/7+Math.floor(phase*4))%7<2;g.fillStyle=hot?'#fb78ec':ink;g.beginPath();g.arc(px,py,4.4,0,Math.PI*2);g.fill();
   }
  }else if(mode==='wire'){
   const colors=['#fa3984','#ffe944','#39dbe8','#aa86eb','#ff6937','#52e9bf'];
   for(let i=5;i>=0;i--){
    g.save();g.translate(384,256);const a=(i-2.5)*(.026+.09*phase);g.transform(1,a*.24,a,1,0,(i-2.5)*4.5);g.translate(-384,-256);g.strokeStyle=colors[i];g.lineWidth=1.35+(i===0?.3:0);g.stroke(selectedPath);g.restore();
   }
  }else if(mode==='register'){
   const offset=Math.max(0,1-phase)*8;
   g.save();g.translate(-offset,-offset*.3);g.strokeStyle='#ff300d';g.lineWidth=5;g.stroke(selectedPath);g.restore();
   g.save();g.translate(offset,offset*.3);g.strokeStyle='#0066ff';g.lineWidth=3;g.stroke(selectedPath);g.restore();
   g.fillStyle='#fff1d0';g.fill(selectedPath,'evenodd');
  }else{
   if(id==='machine')machine(g,phase,variant,assembly,row);
   else{depth(g,id,phase,variant,selectedPath);g.save();if(row)g.clip(selectedPath,'evenodd');g.drawImage(face(id,phase,variant),0,0,W,H);if(id==='script'&&!variant)scriptDetails(g,phase);g.restore();}
  }
  g.restore();return target;
 }
 function hybrid(target,phase=0){
  card(target,'machine',phase,{row:'wild',focus:[384,167],scale:1.11,y:-target.height*.16,mode:'dots',ink:'#d817c4'});
  card(target,'script',phase,{row:'hours',focus:[384,317],scale:.70,x:target.width*.075,y:target.height*.15,mode:'flat',ink:'#fff6d7',clear:false});
  return target;
 }
 return {card,hybrid,face,depth,shapes,prepare,width:W,height:H};
})();
