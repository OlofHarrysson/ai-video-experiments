/* Analytic segment distances and interpolated curve normals, generated on GPU.
   Clipper only resolves filled contours and creates the mitered outer rim. */
window.VectorFields=(()=>{
  const RADIUS=96,PRECISION=1000,FLATNESS=.025;
  const createCanvas=(w,h)=>Object.assign(document.createElement('canvas'),{width:w,height:h});
  const surface=createCanvas(1,1),gl=surface.getContext('webgl2',{preserveDrawingBuffer:true});
  if(!gl||!gl.getExtension('EXT_color_buffer_float'))throw new Error('Float render targets are required for vector distance fields.');
  const shader=(kind,src)=>{const s=gl.createShader(kind);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s};
  const program=gl.createProgram();
  gl.attachShader(program,shader(gl.VERTEX_SHADER,`#version 300 es
    in vec2 corner;in vec4 segment;in vec4 normals;uniform vec2 size;uniform float density;
    out vec2 position;flat out vec4 edge;flat out vec4 edgeNormals;
    void main(){vec2 lo=min(segment.xy,segment.zw)-96.;vec2 hi=max(segment.xy,segment.zw)+96.;position=mix(lo,hi,corner);edge=segment;edgeNormals=normals;gl_Position=vec4(position*density/size*2.-1.,0.,1.);}`));
  gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`#version 300 es
    precision highp float;in vec2 position;flat in vec4 edge;flat in vec4 edgeNormals;out vec4 field;
    void main(){vec2 v=edge.zw-edge.xy;float t=clamp(dot(position-edge.xy,v)/max(dot(v,v),.000001),0.,1.);float d=length(position-edge.xy-v*t);if(d>=96.)discard;
      vec2 delta=position-edge.xy-v*t;vec2 n=normalize(mix(edgeNormals.xy,edgeNormals.zw,t));if(dot(delta,n)<0.)n=-n;if((t<.00001||t>.99999)&&d>.00001)n=delta/d;gl_FragDepth=d/96.;field=vec4(d,n,1.);}`));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));gl.useProgram(program);
  const vao=gl.createVertexArray();gl.bindVertexArray(vao);
  const corners=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,corners);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([0,0,1,0,0,1,0,1,1,0,1,1]),gl.STATIC_DRAW);
  const a=gl.getAttribLocation(program,'corner');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
  const dataBuffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,dataBuffer);
  for(const [name,offset]of [['segment',0],['normals',16]]){const l=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(l);gl.vertexAttribPointer(l,4,gl.FLOAT,false,32,offset);gl.vertexAttribDivisor(l,1)}
  const sizeLocation=gl.getUniformLocation(program,'size'),densityLocation=gl.getUniformLocation(program,'density');
  const norm=(x,y)=>{const l=Math.hypot(x,y)||1;return[x/l,y/l]};
  function flatten(d){
    const tokens=d.match(/[MLCQZ]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?/g);let at=0,cmd='',p=[0,0],start=[0,0],contour=[],all=[];
    const next=()=>Number(tokens[at++]);
    function cubic(a,b,c,e,depth=0){
      const dx=e[0]-a[0],dy=e[1]-a[1],len=Math.hypot(dx,dy)||1;
      const flat=Math.max(Math.abs(dy*(b[0]-a[0])-dx*(b[1]-a[1])),Math.abs(dy*(c[0]-a[0])-dx*(c[1]-a[1])))/len;
      if(flat<FLATNESS||depth>16){contour.push(e);return}
      const mid=(p,q)=>[(p[0]+q[0])*.5,(p[1]+q[1])*.5],ab=mid(a,b),bc=mid(b,c),ce=mid(c,e),abc=mid(ab,bc),bce=mid(bc,ce),centre=mid(abc,bce);
      cubic(a,ab,abc,centre,depth+1);cubic(centre,bce,ce,e,depth+1);
    }
    while(at<tokens.length){if(/[MLCQZ]/.test(tokens[at]))cmd=tokens[at++];
      if(cmd==='M'){if(contour.length)all.push(contour);p=[next(),next()];start=p;contour=[p];cmd='L'}
      else if(cmd==='L'){p=[next(),next()];contour.push(p)}
      else if(cmd==='C'){const b=[next(),next()],c=[next(),next()],e=[next(),next()];cubic(p,b,c,e);p=e}
      else if(cmd==='Q'){const q=[next(),next()],e=[next(),next()];cubic(p,[p[0]+(q[0]-p[0])*2/3,p[1]+(q[1]-p[1])*2/3],[e[0]+(q[0]-e[0])*2/3,e[1]+(q[1]-e[1])*2/3],e);p=e}
      else if(cmd==='Z'){if(contour.length)all.push(contour);contour=[];p=start;cmd=''}
      else throw new Error('Unsupported vector command '+cmd);
    }if(contour.length)all.push(contour);
    return all.map(poly=>poly.map(([x,y])=>({X:Math.round(x*PRECISION),Y:Math.round(y*PRECISION)})));
  }
  const simplify=d=>ClipperLib.Clipper.SimplifyPolygons(flatten(d),ClipperLib.PolyFillType.pftEvenOdd);
  function contours(shape,rim){
    let face;
    if(shape.parts){const clipper=new ClipperLib.Clipper();for(const part of shape.parts)clipper.AddPaths(simplify(part.d),ClipperLib.PolyType.ptSubject,true);face=[];clipper.Execute(ClipperLib.ClipType.ctUnion,face,ClipperLib.PolyFillType.pftNonZero,ClipperLib.PolyFillType.pftNonZero)}
    else face=simplify(shape.d);
    let outer=face;
    if(rim){const offset=new ClipperLib.ClipperOffset(5,.025*PRECISION);offset.AddPaths(face,ClipperLib.JoinType.jtMiter,ClipperLib.EndType.etClosedPolygon);outer=[];offset.Execute(outer,rim*PRECISION)}
    const floats=polys=>polys.map(poly=>poly.map(p=>[p.X/PRECISION,p.Y/PRECISION]));return {face:floats(face),outer:floats(outer)};
  }
  function field(polygons,box,density){
    const [x,y,w,h]=box,tw=w*density,th=h*density;
    surface.width=tw;surface.height=th;gl.viewport(0,0,tw,th);gl.useProgram(program);gl.bindVertexArray(vao);
    const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA32F,tw,th,0,gl.RGBA,gl.FLOAT,null);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
    const fb=gl.createFramebuffer();gl.bindFramebuffer(gl.FRAMEBUFFER,fb);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,texture,0);
    const depth=gl.createRenderbuffer();gl.bindRenderbuffer(gl.RENDERBUFFER,depth);gl.renderbufferStorage(gl.RENDERBUFFER,gl.DEPTH_COMPONENT24,tw,th);gl.framebufferRenderbuffer(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.RENDERBUFFER,depth);
    if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE)throw new Error('Vector field framebuffer is incomplete');
    const data=[];
    for(const poly of polygons){
      const n=poly.length;
      const normals=poly.map((p,i)=>{const q=poly[(i+1)%n];return norm(-(q[1]-p[1]),q[0]-p[0])});
      for(let i=0;i<n;i++){const p=poly[i],q=poly[(i+1)%n],normal=normals[i],prev=normals[(i+n-1)%n],next=normals[(i+1)%n];
        const smooth=(a,b)=>a[0]*b[0]+a[1]*b[1]>.94?norm(a[0]+b[0],a[1]+b[1]):normal;
        const na=smooth(prev,normal),nb=smooth(normal,next);if(Math.hypot(q[0]-p[0],q[1]-p[1])<.001)continue;
        data.push(p[0]-x,p[1]-y,q[0]-x,q[1]-y,...na,...nb);
      }
    }
    gl.bindBuffer(gl.ARRAY_BUFFER,dataBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data),gl.STATIC_DRAW);
    gl.uniform2f(sizeLocation,tw,th);gl.uniform1f(densityLocation,density);gl.disable(gl.BLEND);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LESS);gl.clearDepth(1);gl.clearBufferfv(gl.COLOR,0,new Float32Array([RADIUS,0,0,0]));gl.clear(gl.DEPTH_BUFFER_BIT);gl.drawArraysInstanced(gl.TRIANGLES,0,6,data.length/8);
    const pixels=new Float32Array(tw*th*4);gl.readPixels(0,0,tw,th,gl.RGBA,gl.FLOAT,pixels);
    const inside=new Uint8Array(tw*th);
    for(let row=0;row<th;row++){
      const scanY=y+(row+.5)/density,hits=[];
      for(const poly of polygons)for(let i=0;i<poly.length;i++){
        const a=poly[i],b=poly[(i+1)%poly.length];
        if((a[1]<=scanY&&b[1]>scanY)||(b[1]<=scanY&&a[1]>scanY))hits.push(a[0]+(scanY-a[1])*(b[0]-a[0])/(b[1]-a[1]));
      }
      hits.sort((a,b)=>a-b);
      for(let i=0;i+1<hits.length;i+=2){const left=Math.max(0,Math.ceil((hits[i]-x)*density-.5)),right=Math.min(tw,Math.ceil((hits[i+1]-x)*density-.5));inside.fill(1,row*tw+left,row*tw+right)}
    }
    const distance=new Float32Array(tw*th),nx=new Float32Array(tw*th),ny=new Float32Array(tw*th);
    for(let i=0;i<distance.length;i++){const sign=inside[i]?1:-1;distance[i]=pixels[i*4]*sign;nx[i]=pixels[i*4+1]*sign;ny[i]=pixels[i*4+2]*sign}
    gl.deleteFramebuffer(fb);gl.deleteTexture(texture);gl.deleteRenderbuffer(depth);
    return {distance,nx,ny,segments:data.length/8};
  }
  return {contours,field};
})();
