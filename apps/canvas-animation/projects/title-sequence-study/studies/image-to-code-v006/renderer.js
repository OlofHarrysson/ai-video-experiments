/* Geometry-derived materials. The only textures are distance fields rasterized
   from the editable Bézier outlines; no generated-image pixels enter this file. */
window.WildRenderer = (() => {
  const W=1536,H=1024,padding=64,SCALE=3,RENDER_SCALE=2;
  const canvas=(w,h)=>Object.assign(document.createElement('canvas'),{width:w,height:h});
  const gpu=canvas(W*RENDER_SCALE,H*RENDER_SCALE),gl=gpu.getContext('webgl2',{alpha:true,premultipliedAlpha:false,preserveDrawingBuffer:true});
  if(!gl)throw new Error('WebGL 2 is required for the lettering materials.');
  const compile=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s};
  const vs=`#version 300 es
    in vec2 a; uniform vec4 box; uniform vec2 resolution; out vec2 uv;
    void main(){uv=a;vec2 p=box.xy+a*box.zw;gl_Position=vec4(p/resolution*vec2(2.,-2.)+vec2(-1.,1.),0.,1.);}`;
  const fs=`#version 300 es
    precision highp float;
    uniform sampler2D field; uniform vec2 size; uniform vec4 box;
    uniform float phase, bevel, palette, depth; uniform int material, renderPass;
    in vec2 uv; out vec4 color;
    vec4 sampleField(vec2 p){
      vec2 pos=p*size-.5;ivec2 ij=ivec2(floor(pos));vec2 f=fract(pos);
      return mix(mix(texelFetch(field,ij,0),texelFetch(field,ij+ivec2(1,0),0),f.x),mix(texelFetch(field,ij+ivec2(0,1),0),texelFetch(field,ij+ivec2(1,1),0),f.x),f.y);
    }
    vec3 environment(vec3 n, vec2 p, bool gold){
      vec3 r=reflect(vec3(0.,0.,-1.),n);
      float a=phase*6.2831853;
      if(gold){
        float horizon=r.y*.78+r.x*.32;
        float upper=smoothstep(-.12,.08,horizon);
        vec3 c=mix(vec3(.39,.16,.035),vec3(1.,.78,.38),upper);
        float softbox=exp(-pow((horizon-.30-sin(a)*.10)/.24,2.));
        c=mix(c,vec3(1.,.98,.81),softbox*.95);
        float dark=exp(-pow((horizon+.38)/.16,2.));
        c*=1.-dark*.52;
        return c;
      }
      if(material==1){
        float shade=.94+dot(-n.xy,normalize(vec2(.6,.8)))*.26+n.z*.06;
        vec3 c=vec3(.965,.909,.795)*shade;
        c*=.985+.015*sin(p.y*.012+p.x*.003);
        return c;
      }
      float directional=clamp(.55+dot(-n.xy,normalize(vec2(.4,.8)))*.72,0.,1.);
      float across=clamp((p.x*.3+p.y)/1250.,0.,1.);
      vec3 light=mix(vec3(1.,.095,.46),vec3(1.,.025,.37),across);
      vec3 dark=vec3(.76,.012,.24);
      if(palette>.5){light=vec3(.05,.67,.85);dark=vec3(.008,.14,.26);}
      vec3 c=mix(dark,light,directional);
      float band=r.x*.65+r.y*.75;
      float soft=exp(-pow((band-.19-sin(a)*.14)/.19,2.));
      float sharp=exp(-pow((band-.33-sin(a)*.14)/.05,2.));
      c=mix(c,vec3(1.,.70,.77),soft*.56);
      c+=sharp*vec3(.18,.17,.15);
      return c;
    }
    vec3 goldProfile(float t){
      vec3 c=vec3(1.,.97,.78);
      c=mix(c,vec3(.79,.46,.12),smoothstep(.04,.13,t));
      c=mix(c,vec3(.22,.047,.014),smoothstep(.13,.20,t));
      c=mix(c,vec3(1.,.96,.73),smoothstep(.21,.37,t));
      c=mix(c,vec3(.89,.62,.25),smoothstep(.40,.66,t));
      c=mix(c,vec3(1.,.89,.52),smoothstep(.68,.80,t));
      c=mix(c,vec3(.34,.071,.019),smoothstep(.87,1.,t));
      return c;
    }
    vec2 depthUV(vec2 p,float z){
      vec2 q=p-vec2(z*.60,z*.85);
      return (q-box.xy)/box.zw;
    }
    void main(){
      if(any(lessThan(uv*size,vec2(12.)))||any(lessThan((1.-uv)*size,vec2(12.))))discard;
      vec4 distances=sampleField(uv);
      float d=distances.r, outer=distances.g;
      vec2 step=4./size;
      vec2 p=box.xy+uv*box.zw;
      if(renderPass==0){
        if(depth<.1)discard;
        float best=outer, first=-1.;
        if(outer>=0.)first=0.;
        for(int i=1;i<=20;i++){
          float z=depth*float(i)/20.;vec2 at=depthUV(p,z);
          if(any(lessThan(at*size,vec2(4.))))continue;
          float dd=sampleField(at).g;best=max(best,dd);
          if(first<0.&&dd>=0.)first=z;
        }
        if(best<-.6)discard;
        if(first<0.)first=depth;
        float lo=max(0.,first-depth/20.),hi=first;
        for(int i=0;i<6;i++){float mid=(lo+hi)*.5;if(sampleField(depthUV(p,mid)).g>=0.)hi=mid;else lo=mid;}
        float z=hi;vec2 at=depthUV(p,z);
        vec2 normal=vec2(sampleField(at+vec2(step.x,0.)).g-sampleField(at-vec2(step.x,0.)).g,sampleField(at+vec2(0.,step.y)).g-sampleField(at-vec2(0.,step.y)).g)*.375;
        normal=normalize(normal+vec2(.00001));
        float light=.5+.5*dot(normal,normalize(vec2(-.7,-.4)));
        float streak=pow(.5+.5*sin(normal.x*4.+normal.y*2.+phase*1.2),18.);
        vec3 side=mix(vec3(.045,.012,.064),vec3(.23,.09,.30),light);
        side+=streak*vec3(.28,.16,.36);
        side*=.7+.3*z/max(depth,.01);
        float lip=1.-smoothstep(2.,10.,z);
        side=mix(side,vec3(.36,.009,.06)*(.5+light*.65),lip);
        side+=exp(-pow(best/.75,2.))*vec3(.18,.08,.19);
        color=vec4(side,smoothstep(-.5,.5,best));return;
      }
      if(outer<-.6)discard;
      vec2 grad=vec2(sampleField(uv+vec2(step.x,0.)).r-sampleField(uv-vec2(step.x,0.)).r,sampleField(uv+vec2(0.,step.y)).r-sampleField(uv-vec2(0.,step.y)).r)*.375;
      vec2 gradOuter=vec2(sampleField(uv+vec2(step.x,0.)).g-sampleField(uv-vec2(step.x,0.)).g,sampleField(uv+vec2(0.,step.y)).g-sampleField(uv-vec2(0.,step.y)).g)*.375;
      float s=d>0.?12.+d:12.*max(0.,outer)/max(.001,outer-d);
      float aa=max(.18,fwidth(s)*.60);
      vec2 unit=normalize(gradOuter+vec2(.000001));
      float a=phase*6.2831853;
      float facing=dot(unit,normalize(vec2(.60+sin(a)*.12,.8)));
      float lightWindow=pow(.5+.5*sin(p.y*.015+p.x*.003+a),3.);
      vec3 rgb;
      if(material==2){
        vec3 n=normalize(vec3(-grad*.95,1.));rgb=environment(n,p,true);
      }else{
        bool ivory=material==1;
        float goldStart=ivory?5.2:3.;
        float goldEnd=11.;
        float goldT=clamp((s-goldStart)/(goldEnd-goldStart),0.,1.);
        float goldCore=pow(max(0.,sin(goldT*3.14159)),.6);
        vec3 gold=mix(vec3(.64,.30,.064),vec3(1.,.86,.48),goldCore);
        float goldSpec=exp(-pow((goldT-.34)/.16,2.));
        gold=mix(gold,vec3(1.,.985,.81),goldSpec*.9);
        vec3 goldNormal=normalize(vec3(-unit*cos(goldT*3.14159)*1.2,1.));
        vec3 goldEnv=environment(goldNormal,p,true);
        gold*=.66+.34*goldEnv;
        vec3 red=mix(vec3(.23,.003,.025),vec3(.69,.025,.095),pow(max(0.,sin(clamp(s/4.5,0.,1.)*3.14159)),.7));
        rgb=ivory?red:vec3(.45,.20,.05)*(.85+facing*.15);
        rgb=mix(rgb,vec3(.065,.003,.008),smoothstep(goldStart-.7-aa,goldStart-.7+aa,s));
        rgb=mix(rgb,gold,smoothstep(goldStart-aa,goldStart+aa,s));
        rgb=mix(rgb,vec3(.16,.006,.014),smoothstep(goldEnd-aa,goldEnd+aa,s));
        if(ivory){
          float bevelLight=.98+facing*.13;
          vec3 face=vec3(.973,.918,.810);
          vec3 chamfer=face*bevelLight;
          rgb=mix(rgb,chamfer,smoothstep(11.6-aa,11.6+aa,s));
          rgb=mix(rgb,face,smoothstep(23.8-aa,23.8+aa,s));
          float inlineLight=exp(-pow((s-23.2)/.46,2.));
          float inlineShade=exp(-pow((s-24.2)/.50,2.));
          rgb+=inlineLight*.055;rgb-=inlineShade*.035;
        }else{
          float shoulder=clamp(d/62.,0.,1.);
          vec3 n=normalize(vec3(-grad*pow(1.-shoulder,.8)*.90,1.));
          vec3 reflected=reflect(vec3(0.,0.,-1.),n);
          vec3 face=vec3(1.,.055,.36)*(.94+.10*dot(n,normalize(vec3(-.4,-.6,1.))));
          face*=1.+.012*sin(p.y*.006+p.x*.002);
          if(palette>.5)face=vec3(.03,.58,.80)*(.85+.15*n.z);
          float env=reflected.x*.65+reflected.y*.75;
          float primary=exp(-pow((env+.62+sin(a)*.09)/.15,2.));
          float broad=exp(-pow((env+.53+sin(a)*.09)/.32,2.));
          face=mix(face,vec3(1.,.43,.64),broad*.18);
          face=mix(face,vec3(1.,.97,.89),primary*.88);
          float secondary=exp(-pow((env-.7)/.25,2.));
          face=mix(face,vec3(.67,.012,.18),secondary*.30);
          rgb=mix(rgb,face,smoothstep(12.-aa,12.+aa,s));
          float edgeSpec=exp(-pow((s-13.3)/.65,2.))*pow(max(0.,facing),1.5);
          rgb=mix(rgb,vec3(1.,.97,.85),edgeSpec*.60);
          float shine=distances.b*.09*smoothstep(12.,16.,s);
          rgb=mix(rgb,vec3(1.,.85,.85),shine);
        }
        float grain=fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453)-.5;
        rgb+=grain*.004;
      }
      color=vec4(rgb,smoothstep(-.5,.5,outer));
    }`;
  const program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,vs));gl.attachShader(program,compile(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));gl.useProgram(program);
  const loc=Object.fromEntries(['box','resolution','field','size','phase','bevel','material','palette','depth','renderPass'].map(n=>[n,gl.getUniformLocation(program,n)]));
  const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([0,0,1,0,0,1,0,1,1,0,1,1]),gl.STATIC_DRAW);const a=gl.getAttribLocation(program,'a');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);gl.uniform2f(loc.resolution,W,H);
  gl.enable(gl.BLEND);gl.blendFuncSeparate(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA,gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
  function distance(values,w,h){
    const len=Math.max(w,h),f=new Float64Array(len),out=new Float64Array(len),sites=new Int32Array(len),bounds=new Float64Array(len+1);
    function axis(n){let k=0;sites[0]=0;bounds[0]=-Infinity;bounds[1]=Infinity;for(let q=1;q<n;q++){let cross;while(true){const p=sites[k];cross=((f[q]+q*q)-(f[p]+p*p))/(2*(q-p));if(cross>bounds[k])break;k--}sites[++k]=q;bounds[k]=cross;bounds[k+1]=Infinity}k=0;for(let q=0;q<n;q++){while(bounds[k+1]<q)k++;out[q]=(q-sites[k])**2+f[sites[k]]}}
    for(let x=0;x<w;x++){for(let y=0;y<h;y++)f[y]=values[y*w+x];axis(h);for(let y=0;y<h;y++)values[y*w+x]=out[y]}
    for(let y=0;y<h;y++){for(let x=0;x<w;x++)f[x]=values[y*w+x];axis(w);for(let x=0;x<w;x++)values[y*w+x]=Math.sqrt(out[x])}return values;
  }
  function buildField(shape){
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg'),p=document.createElementNS(svg.namespaceURI,'path');p.setAttribute('d',shape.d);svg.append(p);document.body.append(svg);const b=p.getBBox();svg.remove();
    const x=Math.floor(b.x)-padding,y=Math.floor(b.y)-padding,w=Math.ceil(b.width)+padding*2,h=Math.ceil(b.height)+padding*2;
    const tw=w*SCALE,th=h*SCALE,c=canvas(tw,th),g=c.getContext('2d',{willReadFrequently:true});
    g.scale(SCALE,SCALE);g.translate(-x,-y);const path=new Path2D(shape.d);
    function makeDistance(stroke){
      g.clearRect(x,y,w,h);for(const part of shape.parts||[shape]){const pp=new Path2D(part.d);g.fill(pp,'evenodd');if(stroke){g.lineWidth=stroke;g.lineJoin='miter';g.miterLimit=5;g.stroke(pp)}}
      const pix=g.getImageData(0,0,tw,th).data,n=tw*th,inside=new Float32Array(n),outside=new Float32Array(n);
      for(let i=0;i<n;i++){const a=pix[i*4+3]/255;inside[i]=a===1?1e8:Math.max(0,a-.5)**2;outside[i]=a===0?1e8:Math.max(0,.5-a)**2}distance(inside,tw,th);distance(outside,tw,th);
      let field=new Float32Array(n);for(let i=0;i<n;i++)field[i]=(inside[i]-outside[i])/SCALE;
      for(let pass=0;pass<2;pass++){const hfield=new Float32Array(n),vfield=new Float32Array(n);hfield.fill(-padding);vfield.fill(-padding);for(let yy=2;yy<th-2;yy++)for(let xx=2;xx<tw-2;xx++){const i=yy*tw+xx;hfield[i]=(field[i-2]+field[i-1]*4+field[i]*6+field[i+1]*4+field[i+2])/16}for(let yy=2;yy<th-2;yy++)for(let xx=2;xx<tw-2;xx++){const i=yy*tw+xx;vfield[i]=(hfield[i-tw*2]+hfield[i-tw]*4+hfield[i]*6+hfield[i+tw]*4+hfield[i+tw*2])/16}field=vfield}
      return field;
    }
    const face=makeDistance(0),outer=makeDistance(shape.material==='gold'?0:24),field=new Float32Array(tw*th*4);
    g.clearRect(x,y,w,h);
    if(shape.shine){g.lineWidth=6;g.lineJoin='round';g.lineCap='round';g.strokeStyle='white';g.filter='blur(9px)';g.stroke(new Path2D(shape.shine));g.filter='none';}
    const shine=g.getImageData(0,0,tw,th).data;
    g.clearRect(x,y,w,h);
    if(shape.shine){g.lineWidth=1.3;g.stroke(new Path2D(shape.shine));}
    const hairline=g.getImageData(0,0,tw,th).data;
    for(let i=0;i<face.length;i++){field[i*4]=face[i];field[i*4+1]=outer[i];field[i*4+2]=shine[i*4+3]/255;field[i*4+3]=hairline[i*4+3]/255}
    const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA32F,tw,th,0,gl.RGBA,gl.FLOAT,field);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    return {...shape,path:new Path2D(shape.d),box:[x,y,w,h],texture};
  }
  const shapes=WildGeometry.map(buildField);
  const lowerIds=['under-Hours','H','O','U','R','S'];
  const lowerParts=WildGeometry.filter(s=>lowerIds.includes(s.id));
  const lowerBody=buildField({id:'hours-body',material:'ivory',d:lowerParts.map(s=>s.d).join(' '),parts:lowerParts});
  function gradient(g,x0,y0,x1,y1,stops){const gr=g.createLinearGradient(x0,y0,x1,y1);for(const [at,c]of stops)gr.addColorStop(at,c);return gr}
  function draw(target,frame=0,options={}){
    const {flat=false,depth=34,bevel=48,palette=0,glyph=null,glints=true}=options;
    const g=target.getContext('2d');g.save();g.scale(target.width/W,target.height/H);g.fillStyle='#030104';g.fillRect(0,0,W,H);
    const visible=shapes.filter(s=>!glyph||s.id===glyph);
    if(flat){for(const s of visible){g.fillStyle=s.material==='pink'?'#ff2583':s.material==='ivory'?'#ffefcc':'#b88738';g.fill(s.path,'evenodd')}g.restore();return target}
    gl.viewport(0,0,W*RENDER_SCALE,H*RENDER_SCALE);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.useProgram(program);gl.uniform1f(loc.phase,frame/144);gl.uniform1f(loc.bevel,bevel);gl.uniform1f(loc.palette,palette);gl.uniform1f(loc.depth,depth);
    const lower=visible.filter(s=>['under-Hours','H','O','U','R','S','diamond-O','diamond-base'].includes(s.id));
    const upper=visible.filter(s=>!lower.includes(s));
    const draws=[...upper.flatMap(s=>[[s,0],[s,1]]),...(glyph?lower.map(s=>[s,0]):[[lowerBody,0]]),...lower.map(s=>[s,1])];
    for(const [s,pass]of draws){gl.uniform1i(loc.renderPass,pass);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,s.texture);gl.uniform1i(loc.field,0);gl.uniform4fv(loc.box,s.box);gl.uniform2f(loc.size,s.box[2]*SCALE,s.box[3]*SCALE);gl.uniform1i(loc.material,s.material==='pink'?0:s.material==='ivory'?1:2);gl.uniform1f(loc.depth,depth*(s.material==='pink'?1.25:s.material==='ivory'?.85:.55));gl.drawArrays(gl.TRIANGLES,0,6)}
    g.drawImage(gpu,0,0,W,H);
    if(glints){for(const [x,y,size,offset]of [[175,687,34,0],[809,38,28,1],[1393,111,25,2],[1060,385,20,3],[590,717,16,4]]){
      if(glyph)continue;const gain=.35+.65*Math.max(0,Math.sin(frame/144*Math.PI*2+offset));g.save();g.translate(x,y);g.globalAlpha=gain;const glow=g.createRadialGradient(0,0,0,0,0,size*2.8);glow.addColorStop(0,'#fff9dc');glow.addColorStop(.07,'#ffe9aa');glow.addColorStop(.25,'#ffb54166');glow.addColorStop(1,'#ff900000');g.fillStyle=glow;g.fillRect(-size*3,-size*3,size*6,size*6);g.fillStyle='#fffbe7';g.beginPath();g.moveTo(0,-size);g.quadraticCurveTo(1,-1,size*.75,0);g.quadraticCurveTo(1,1,0,size);g.quadraticCurveTo(-1,1,-size*.75,0);g.quadraticCurveTo(-1,-1,0,-size);g.fill();g.restore();
    }}
    g.restore();return target;
  }
  return {draw,width:W,height:H,shapes:shapes.map(({id,material,box})=>({id,material,box}))};
})();
