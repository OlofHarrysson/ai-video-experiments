/* Geometry-derived materials. The only textures are distance fields rasterized
   from the editable Bézier outlines; no generated-image pixels enter this file. */
window.WildRenderer = (() => {
  const W=1536,H=1024,padding=80,SCALE=2;
  let renderScale=2;
  const canvas=(w,h)=>Object.assign(document.createElement('canvas'),{width:w,height:h});
  const gpu=canvas(W*renderScale,H*renderScale),gl=gpu.getContext('webgl2',{alpha:true,premultipliedAlpha:false,preserveDrawingBuffer:true});
  if(!gl)throw new Error('WebGL 2 is required for the lettering materials.');
  const compile=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s};
  const vs=`#version 300 es
    in vec2 a; uniform vec4 box; uniform vec2 resolution, origin;uniform int baking; out vec2 uv;
    void main(){uv=a;vec2 p=box.xy+a*box.zw;vec2 clip=(p-origin)/resolution*2.-1.;if(baking==0)clip.y=-clip.y;gl_Position=vec4(clip,0.,1.);}`;
  const fs=`#version 300 es
    precision highp float;
    uniform sampler2D field, normalField, sideField; uniform vec2 size; uniform vec4 box;
    uniform float phase, palette, depth; uniform int material, renderPass, diagnostic, ornament;
    in vec2 uv; out vec4 color;
    vec4 sampleAt(sampler2D map,vec2 p,vec2 dim){
      vec2 pos=p*dim-.5;ivec2 ij=clamp(ivec2(floor(pos)),ivec2(0),ivec2(dim)-2);vec2 f=fract(pos);
      return mix(mix(texelFetch(map,ij,0),texelFetch(map,ij+ivec2(1,0),0),f.x),mix(texelFetch(map,ij+ivec2(0,1),0),texelFetch(map,ij+ivec2(1,1),0),f.x),f.y);
    }
    vec4 sampleTexture(sampler2D map,vec2 p){return sampleAt(map,p,size);}
    vec4 sampleField(vec2 p){return sampleTexture(field,p);}
    vec3 environment(vec3 n, vec2 p, bool gold){
      vec3 r=reflect(vec3(0.,0.,-1.),n);
      float a=phase*6.2831853;
      if(gold){
        float horizon=r.y*.78+r.x*.32;
        float upper=smoothstep(-.12,.08,horizon);
        vec3 c=mix(vec3(.39,.16,.035),vec3(1.,.78,.38),upper);
        float softbox=exp(-pow((horizon-.30-sin(a)*.24)/.24,2.));
        c=mix(c,vec3(1.,.98,.81),softbox*.95);
        float dark=exp(-pow((horizon+.38)/.16,2.));
        c*=1.-dark*.52;
        return c;
      }
      return vec3(0.);
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

      vec2 p=box.xy+uv*box.zw;
      if(renderPass==0 || renderPass==2){
        if(depth<.1)discard;
        vec2 normal;float z,coverage;
        if(renderPass==2){
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
        z=hi;vec2 at=depthUV(p,z);
        vec2 ds=vec2(2.)/box.zw;
        normal=vec2(sampleField(at+vec2(ds.x,0.)).g-sampleField(at-vec2(ds.x,0.)).g,sampleField(at+vec2(0.,ds.y)).g-sampleField(at-vec2(0.,ds.y)).g);
        normal=normalize(normal+vec2(.00001));
        color=vec4(normal,z,smoothstep(-.5,.5,best));return;
        }else{
          vec4 cached=sampleAt(sideField,uv,box.zw);normal=normalize(cached.xy+vec2(.00001));z=cached.z;coverage=cached.a;if(coverage<.001)discard;
        }
        float light=.5+.5*dot(normal,normalize(vec2(-.7,-.4)));
        float streak=pow(.5+.5*sin(normal.x*4.+normal.y*2.+sin(phase*6.2831853)*1.2),42.);
        vec3 side=mix(vec3(.022,.006,.038),vec3(.19,.07,.245),light);
        side+=streak*vec3(.27,.15,.32);
        float reflectedStrip=exp(-pow((sin(normal.x*2.+normal.y*1.2+(p.x+p.y*.3)*.003+sin(phase*6.2831853)*.18)-.5)/.13,2.));
        side+=reflectedStrip*vec3(.16,.085,.18);
        float copper=pow(max(0.,sin(normal.x*2.8-normal.y+.4+sin(phase*6.2831853)*.3)),10.)*(1.-z/max(depth,.01));
        side+=copper*vec3(.16,.055,.025);
        side*=1.-.38*z/max(depth,.01);
        float lip=smoothstep(1.7,2.8,z)*(1.-smoothstep(5.,7.,z));
        side=mix(side,vec3(.45,.025,.085)*(.5+light*.65),lip);
        side=mix(vec3(.016,.002,.012),side,smoothstep(.8,2.,z));
        side+=(1.-coverage)*vec3(.065,.025,.075);
        if(palette>.5)side=side*vec3(.65,.98,1.25);
        if(diagnostic==1)side=vec3(.6);if(diagnostic==2)side=vec3(normal*.5+.5,.5);color=vec4(side,coverage);return;
      }
      if(outer<-.6)discard;
      vec4 normals=sampleTexture(normalField,uv);
      vec2 grad=normals.xy,gradOuter=normals.zw;
      float s=d>0.?12.+d:12.*max(0.,outer)/max(.001,outer-d);
      float aa=max(.18,fwidth(s)*.60);
      vec2 unit=normalize(gradOuter+vec2(.000001));
      float a=phase*6.2831853;
      float facing=dot(unit,normalize(vec2(.60+sin(a)*.55,.8)));

      vec3 rgb;
      if(material==2){
        vec3 n=normalize(vec3(-grad*.95,1.));rgb=environment(n,p,true);
      }else{
        bool ivory=material==1;
        float goldStart=ivory?5.2:1.1;
        float goldEnd=11.;
        float goldT=clamp((s-goldStart)/(goldEnd-goldStart),0.,1.);
        float goldCore=pow(max(0.,sin(goldT*3.14159)),.6);
        vec3 gold=mix(mix(vec3(.64,.30,.064),vec3(1.,.76,.33),goldCore),goldProfile(goldT),.58);
        float goldSpec=exp(-pow((goldT-.34)/.16,2.));
        gold=mix(gold,vec3(1.,.985,.81),goldSpec*.80);
        vec3 goldNormal=normalize(vec3(-unit*cos(goldT*3.14159)*1.2,1.));
        vec3 goldEnv=environment(goldNormal,p,true);
        gold*=.66+.34*goldEnv;gold+=goldSpec*vec3(.16,.14,.09);
        if(palette>.5)gold=mix(vec3(.08,.15,.22),vec3(.94,.99,1.),dot(gold,vec3(.4,.4,.2)));
        vec3 red=mix(vec3(.23,.003,.025),vec3(.69,.025,.095),pow(max(0.,sin(clamp(s/4.5,0.,1.)*3.14159)),.7));
        if(palette>.5)red=vec3(.025,.10,.23)*(1.+sin(s));
        rgb=ivory?red:(palette>.5?vec3(.15,.22,.29):vec3(.45,.20,.05))*(.85+facing*.15);
        rgb=mix(rgb,(palette>.5?vec3(.002,.008,.018):vec3(.065,.003,.008)),smoothstep(goldStart-.7-aa,goldStart-.7+aa,s));
        rgb=mix(rgb,gold,smoothstep(goldStart-aa,goldStart+aa,s));
        rgb=mix(rgb,(palette>.5?vec3(.005,.04,.075):vec3(.16,.006,.014)),smoothstep(goldEnd-aa,goldEnd+aa,s));
        if(ivory){

          vec3 face=(palette>.5?vec3(.86,.94,.99):vec3(.973,.918,.810))*(1.+.012*sin(p.x*.008+p.y*.002));
          vec3 chamfer=mix(palette>.5?vec3(.43,.59,.69):vec3(.80,.67,.49),face*1.09,clamp(.60+facing*.58,0.,1.));
          rgb=mix(rgb,chamfer,smoothstep(11.6-aa,11.6+aa,s));
          rgb=mix(rgb,face,smoothstep(23.8-aa,23.8+aa,s));
          float inlineLight=exp(-pow((s-23.2)/.46,2.));
          float inlineShade=exp(-pow((s-24.2)/.50,2.));
          rgb+=inlineLight*.055;rgb-=inlineShade*.035;
        }else{
          float roundWidth=distances.a;
          float shoulder=clamp(d/roundWidth,0.,1.);
          vec3 n=normalize(vec3(-grad*pow(1.-shoulder,.8)*.90,1.));
          vec3 reflected=reflect(vec3(0.,0.,-1.),n);
          float modelling=clamp(.62+dot(n.xy,normalize(vec2(-.5,-.8)))*.62,0.,1.);
          vec3 face=mix(vec3(.85,.045,.285),vec3(1.,.17,.445),modelling);
          float sheenPhase=sin(a)*.24;
          float sheen=pow(.5+.5*sin(p.x*.007+p.y*.005+sheenPhase),8.);
          face=mix(face,vec3(1.,.29,.51),sheen*.18);
          if(palette>.5)face=vec3(.03,.58,.80)*(.85+.15*n.z);
          float env=reflected.x*.65+reflected.y*.75;
          float primary=exp(-pow((env+.62+sin(a)*.27)/.15,2.));
          // Taper the reflection through W's acute inner join instead of ending it as a square.
          float joinMask=exp(-pow((p.x-467.)/24.,4.))*exp(-pow((p.y-278.)/33.,4.));
          primary*=1.-joinMask*.94;
          float broad=exp(-pow((env+.53+sin(a)*.27)/.32,2.));
          face=mix(face,palette>.5?vec3(.34,.85,.96):vec3(1.,.43,.64),broad*.18);
          face=mix(face,vec3(1.,.97,.89),primary*.88);
          float secondary=exp(-pow((env-.7)/.25,2.));
          face=mix(face,palette>.5?vec3(.005,.12,.28):vec3(.67,.012,.18),secondary*.30);
          rgb=mix(rgb,face,smoothstep(12.-aa,12.+aa,s));
          float edgeSpec=exp(-pow((s-13.3)/.65,2.))*pow(max(0.,facing),1.5);
          rgb=mix(rgb,vec3(1.,.97,.85),edgeSpec*.60);
          float shine=distances.b*.09*smoothstep(12.,16.,s);
          rgb=mix(rgb,vec3(1.,.85,.85),shine);
          if(ornament==1){
            float goldWidth=24.;
            float rail=clamp(d/goldWidth,0.,1.);
            vec3 gilt=goldProfile(rail)*(.86+.14*goldEnv);
            vec3 inlay=mix(vec3(.24,.003,.027),vec3(.92,.025,.27),exp(-pow((p.x-706.)/110.,4.)));
            gilt=mix(gilt,inlay,smoothstep(.82,.94,rail));
            if(palette>.5)gilt=vec3(.55,.80,.95)*dot(gilt,vec3(.4,.4,.2));
            rgb=mix(rgb,gilt,smoothstep(11.8-aa,11.8+aa,s));
          }
        }
        float grain=fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453)-.5;
        rgb+=grain*(ivory?.003:.009);
      }
      color=vec4(rgb,smoothstep(-.5,.5,outer));
    }`;
  const program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,vs));gl.attachShader(program,compile(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));gl.useProgram(program);
  const loc=Object.fromEntries(['box','resolution','origin','baking','field','normalField','sideField','size','phase','ornament','material','palette','depth','renderPass','diagnostic'].map(n=>[n,gl.getUniformLocation(program,n)]));
  const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([0,0,1,0,0,1,0,1,1,0,1,1]),gl.STATIC_DRAW);const a=gl.getAttribLocation(program,'a');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);gl.uniform2f(loc.resolution,W,H);gl.uniform2f(loc.origin,0,0);
  gl.enable(gl.BLEND);gl.blendFuncSeparate(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA,gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
  function buildField(shape){
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg'),p=document.createElementNS(svg.namespaceURI,'path');p.setAttribute('d',shape.d);svg.append(p);document.body.append(svg);const b=p.getBBox();svg.remove();
    const x=Math.floor(b.x)-padding,y=Math.floor(b.y)-padding,w=Math.ceil(b.width)+padding*2,h=Math.ceil(b.height)+padding*2;
    const tw=w*SCALE,th=h*SCALE,c=canvas(tw,th),g=c.getContext('2d',{willReadFrequently:true});
    g.scale(SCALE,SCALE);g.translate(-x,-y);const path=new Path2D(shape.d);
    const outlines=VectorFields.contours(shape,shape.material==='gold'?0:12);
    const faceField=VectorFields.field(outlines.face,[x,y,w,h],SCALE),outerField=VectorFields.field(outlines.outer,[x,y,w,h],SCALE);
    const face=faceField.distance,outer=outerField.distance,field=new Float32Array(tw*th*4),normalData=new Float32Array(tw*th*4);
    for(let i=0;i<face.length;i++){normalData[i*4]=faceField.nx[i];normalData[i*4+1]=faceField.ny[i];normalData[i*4+2]=outerField.nx[i];normalData[i*4+3]=outerField.ny[i]}
    g.clearRect(x,y,w,h);
    if(shape.shine){g.lineWidth=6;g.lineJoin='round';g.lineCap='round';g.strokeStyle='white';g.filter='blur(9px)';g.stroke(new Path2D(shape.shine));g.filter='none';}
    const shine=g.getImageData(0,0,tw,th).data;
    // Local stroke width is geometry, so compute it once rather than ray-march every frame.
    const sampleDistance=(px,py)=>{
      px=Math.max(0,Math.min(tw-2,px));py=Math.max(0,Math.min(th-2,py));
      const ix=Math.floor(px),iy=Math.floor(py),fx=px-ix,fy=py-iy,j=iy*tw+ix;
      return (face[j]*(1-fx)+face[j+1]*fx)*(1-fy)+(face[j+tw]*(1-fx)+face[j+tw+1]*fx)*fy;
    };
    for(let i=0;i<face.length;i++){
      let width=face[i],previous=width;
      if(width>0&&width<38){
        const px=i%tw,py=Math.floor(i/tw),dx=faceField.nx[i]*3*SCALE,dy=faceField.ny[i]*3*SCALE;
        for(let step=1;step<=10;step++){const probe=sampleDistance(px+dx*step,py+dy*step);if(probe<previous)break;width=Math.max(width,probe);previous=probe}
      }
      field[i*4]=face[i];field[i*4+1]=outer[i];field[i*4+2]=shine[i*4+3]/255;field[i*4+3]=Math.min(32,Math.max(4,width*.86));
    }
    const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA32F,tw,th,0,gl.RGBA,gl.FLOAT,field);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    const normalTexture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,normalTexture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA32F,tw,th,0,gl.RGBA,gl.FLOAT,normalData);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    return {...shape,path:new Path2D(shape.d),box:[x,y,w,h],texture,normalTexture};
  }
  const shapes=WildGeometry.map(buildField);
  const lowerIds=['under-Hours','H','O','U','R','S'];
  const lowerParts=WildGeometry.filter(s=>lowerIds.includes(s.id));
  const lowerBody=buildField({id:'hours-body',material:'ivory',d:lowerParts.map(s=>s.d).join(' '),parts:lowerParts});
  if(!gl.getExtension('EXT_color_buffer_float'))throw new Error('Float render targets are required for the depth cache.');
  function bindShape(s){
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,s.texture);gl.uniform1i(loc.field,0);
    gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,s.normalTexture);gl.uniform1i(loc.normalField,1);
    gl.uniform4fv(loc.box,s.box);gl.uniform2f(loc.size,s.box[2]*SCALE,s.box[3]*SCALE);
  }
  function sideTexture(s,depth){
    if(s.sideDepth===depth)return s.sideTexture;
    if(s.sideTexture)gl.deleteTexture(s.sideTexture);
    const texture=gl.createTexture();gl.activeTexture(gl.TEXTURE2);gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA16F,s.box[2],s.box[3],0,gl.RGBA,gl.HALF_FLOAT,null);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    const fb=gl.createFramebuffer();gl.bindFramebuffer(gl.FRAMEBUFFER,fb);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,texture,0);
    if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE)throw new Error('Depth cache framebuffer is incomplete.');
    gl.viewport(0,0,s.box[2],s.box[3]);gl.disable(gl.BLEND);gl.clearBufferfv(gl.COLOR,0,new Float32Array(4));
    bindShape(s);gl.uniform2f(loc.resolution,s.box[2],s.box[3]);gl.uniform2f(loc.origin,s.box[0],s.box[1]);gl.uniform1f(loc.depth,depth);gl.uniform1i(loc.renderPass,2);gl.uniform1i(loc.baking,1);
    // The baking branch does not sample the cache; bind another texture to avoid a feedback loop.
    gl.uniform1i(loc.sideField,0);gl.drawArrays(gl.TRIANGLES,0,6);
    gl.uniform1i(loc.baking,0);gl.bindFramebuffer(gl.FRAMEBUFFER,null);gl.deleteFramebuffer(fb);gl.enable(gl.BLEND);
    gl.uniform2f(loc.resolution,W,H);gl.uniform2f(loc.origin,0,0);gl.viewport(0,0,W*renderScale,H*renderScale);
    s.sideTexture=texture;s.sideDepth=depth;return texture;
  }
  function gradient(g,x0,y0,x1,y1,stops){const gr=g.createLinearGradient(x0,y0,x1,y1);for(const [at,c]of stops)gr.addColorStop(at,c);return gr}
  const glintTracks=[
    {d:'M126 518 C201 411 276 301 291 196',start:.20,range:.60,size:26,offset:6},
    {d:'M643 522 C676 491 686 434 716 367 C744 302 768 231 799 218',start:.62,range:.30,size:24,offset:7},
    {d:'M1166 747 C1212 780 1296 820 1318 875',start:.20,range:.36,size:15,offset:8},
  ].map(track=>{const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',track.d);return {...track,path:p,length:p.getTotalLength()}});
  function movingGlints(frame){return glintTracks.map(t=>{const phase=frame/144*Math.PI*2,at=t.start+t.range*(.5-.5*Math.cos(phase)),p=t.path.getPointAtLength(at*t.length);return [p.x,p.y,t.size,t.offset]})}
  function draw(target,frame=0,options={}){
    const {flat=false,depth=34,palette=0,glyph=null,glints=true,diagnostic=0,quality=2}=options;
    const nextScale=Math.max(.5,Math.min(2,quality));
    if(renderScale!==nextScale){renderScale=nextScale;gpu.width=Math.round(W*renderScale);gpu.height=Math.round(H*renderScale)}
    frame=((frame%144)+144)%144;
    const g=target.getContext('2d');g.save();g.scale(target.width/W,target.height/H);g.fillStyle='#030104';g.fillRect(0,0,W,H);
    const visible=shapes.filter(s=>!glyph||s.id===glyph);
    if(flat){for(const s of visible){g.fillStyle=s.material==='pink'?'#ff2583':s.material==='ivory'?'#ffefcc':'#b88738';g.fill(s.path,'evenodd')}g.restore();return target}
    gl.viewport(0,0,W*renderScale,H*renderScale);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.useProgram(program);gl.uniform1f(loc.phase,frame/144);gl.uniform1f(loc.palette,palette);gl.uniform1f(loc.depth,depth);gl.uniform1i(loc.diagnostic,diagnostic);
    const lower=visible.filter(s=>['under-Hours','H','O','U','R','S','diamond-O','diamond-base'].includes(s.id));
    const upper=visible.filter(s=>!lower.includes(s));
    const draws=[...upper.flatMap(s=>[[s,0],[s,1]]),...(glyph?lower.map(s=>[s,0]):[[lowerBody,0]]),...lower.map(s=>[s,1])];
    const shapeDepth=s=>depth*(s.material==='pink'?1.25:s.material==='ivory'?.85:.55);
    for(const [s,pass]of draws)if(pass===0)sideTexture(s,shapeDepth(s));
    for(const [s,pass]of draws){
      bindShape(s);gl.uniform1i(loc.renderPass,pass);gl.uniform1i(loc.ornament,s.id==='under-Hours'?1:0);
      gl.uniform1i(loc.material,s.material==='pink'?0:s.material==='ivory'?1:2);gl.uniform1f(loc.depth,shapeDepth(s));
      gl.activeTexture(gl.TEXTURE2);gl.bindTexture(gl.TEXTURE_2D,s.sideTexture||s.texture);gl.uniform1i(loc.sideField,2);
      gl.drawArrays(gl.TRIANGLES,0,6);
    }
    g.drawImage(gpu,0,0,W,H);
    if(palette===0)for(const shape of visible){
      const facets=window.WildFacets?.[shape.id]||[];
      g.save();g.clip(shape.path,'evenodd');
      g.globalAlpha=.8+.2*Math.cos(frame/144*Math.PI*2);
      for(const facet of facets){g.fillStyle=gradient(g,...facet.from,...facet.to,facet.colors.map((c,i)=>[i/(facet.colors.length-1),c]));g.fill(new Path2D(facet.d));}
      g.restore();
    }
    if(visible.some(s=>s.id==='H')){
      g.save();g.clip(shapes.find(s=>s.id==='H').path,'evenodd');
      const warm=palette===0;
      g.fillStyle=gradient(g,340,704,347,741,[[0,warm?'#ac773d':'#50758f'],[.48,warm?'#fff9dd':'#f0ffff'],[1,warm?'#c6a978':'#809aa9']]);
      g.fill(new Path2D('M323 716 L414 697 L405 711 L330 729 L320 742 Z'));
      g.fillStyle=warm?'#fff8df':'#efffff';g.fill(new Path2D('M320 738 L416 714 L403 729 L324 749 Z'));
      g.restore();
    }
    // Four concave planes and a smaller inner jewel give the ornaments real cuts.
    function jewel(cx,cy,rx,up,down,small=false){
      const gain=.5+.5*Math.sin(frame/144*Math.PI*2+.4);
      g.save();g.translate(cx,cy);
      const planes=[
        [`M0 ${-up} Q${-rx*.25} -9 ${-rx} 0 L0 1 Z`, '#fff4c2','#b66419'],
        [`M0 ${-up} Q${rx*.3} -10 ${rx} 0 L0 1 Z`, '#a95712','#fff1a0'],
        [`M${-rx} 0 Q${-rx*.2} 12 0 ${down} L0 1 Z`, '#fff5c0','#bb6c1b'],
        [`M${rx} 0 Q${rx*.2} 14 0 ${down} L0 1 Z`, '#c88223','#6e2818'],
      ];
      const metal=c=>{if(palette===0)return c;const n=parseInt(c.slice(1),16),l=((n>>16)*.4+((n>>8)&255)*.4+(n&255)*.2);return `rgb(${Math.round(l*.82)},${Math.round(l*.96)},${Math.round(l)})`};
      for(const [d,c1,c2]of planes){g.fillStyle=gradient(g,-rx,-up,rx,down,[[0,metal(c1)],[.5,metal(c2)],[1,metal(c1)]]);g.fill(new Path2D(d))}
      if(!small){
        g.scale(.67,.65);
        const inner=`M0 ${-up} Q-4 -7 ${-rx} 0 Q-4 9 0 ${down} Q4 8 ${rx} 0 Q4 -8 0 ${-up} Z`;
        g.fillStyle=gradient(g,-rx,0,rx,0,(palette===0?[[0,'#fd287b'],[.38,'#ad133d'],[.48,'#fff8c5'],[.7,'#ffe67c'],[1,'#af231d']]:[[0,'#25dfff'],[.38,'#185b8c'],[.48,'#f2ffff'],[.7,'#b4e9ff'],[1,'#105170']]));g.fill(new Path2D(inner));
        g.strokeStyle=palette===0?'#fff1aa':'#d2f4ff';g.lineWidth=.8;g.globalAlpha=.6+gain*.4;g.stroke(new Path2D(inner));
      }
      g.restore();
    }
    if(visible.some(s=>s.id==='diamond-O'))jewel(598,718,29,75,93);
    if(visible.some(s=>s.id==='diamond-base'))jewel(707,879,31,61,52);
    if(visible.some(s=>s.id==='H'))jewel(264,735,18,20,21,true);
    if(visible.some(s=>s.id==='R'))jewel(974,710,17,23,23,true);
    if(glints){for(const [x,y,size,offset]of [[175,687,39,0],[809,38,35,1],[1373,111,35,2],[1060,385,23,3],[598,717,22,4],[707,879,24,5],[1282,949,29,9],...movingGlints(frame)]){
      if(glyph)continue;
      const gain=.40+.60*Math.pow(.5+.5*Math.cos(frame/144*Math.PI*2+offset*.8),3.);
      g.save();g.translate(x,y);g.globalAlpha=gain;
      const glow=g.createRadialGradient(0,0,0,0,0,size*2);glow.addColorStop(0,'#fff9e7');glow.addColorStop(.06,'#fff2cb');glow.addColorStop(.18,'#ffe1a060');glow.addColorStop(.5,'#ffc35514');glow.addColorStop(1,'#ff900000');g.fillStyle=glow;g.fillRect(-size*2,-size*2,size*4,size*4);
      g.fillStyle='#fffbe7';g.beginPath();g.moveTo(0,-size);g.lineTo(.65,-2.5);g.lineTo(2.5,-.65);g.lineTo(size*1.3,0);g.lineTo(2.5,.65);g.lineTo(.65,2.5);g.lineTo(0,size);g.lineTo(-.65,2.5);g.lineTo(-2.5,.65);g.lineTo(-size*1.3,0);g.lineTo(-2.5,-.65);g.lineTo(-.65,-2.5);g.closePath();g.fill();
      g.strokeStyle='#ffd979';g.lineWidth=.6;g.globalAlpha=gain*.55;g.beginPath();g.moveTo(-size*.43,-size*.43);g.lineTo(size*.43,size*.43);g.moveTo(-size*.43,size*.43);g.lineTo(size*.43,-size*.43);g.stroke();g.restore();
    }}
    g.restore();return target;
  }
  return {draw,width:W,height:H,shapes:shapes.map(({id,material,box})=>({id,material,box}))};
})();
