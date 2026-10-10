/* One lighting model for comparison. Mesh mode contains no artwork texture. */
window.SurfaceRenderer=class SurfaceRenderer {
 constructor(canvas,width,height){
  this.canvas=canvas;this.width=width;this.height=height;
  const gl=this.gl=canvas.getContext('webgl2',{alpha:false,antialias:false,preserveDrawingBuffer:true});if(!gl)throw Error('WebGL 2 is required');gl.disable(gl.DITHER);
  const vertex=`#version 300 es
  in vec2 position;in vec3 color;uniform vec2 size;uniform float posScale;uniform float time;uniform float warp;out vec2 uv;out vec3 rgb;
  void main(){uv=position*posScale/size;rgb=color;vec2 p=uv;
  float e=sin(3.14159265*uv.x)*sin(3.14159265*uv.y);
  p.x+=warp*e*sin(uv.y*9.0+time*3.0)/size.x;p.y+=warp*e*cos(uv.x*8.0-time*2.0)/size.y;
  gl_Position=vec4(p.x*2.0-1.0,1.0-p.y*2.0,0,1);}`;
  const fragment=`#version 300 es
  precision highp float;in vec2 uv;in vec3 rgb;out vec4 outColor;
  uniform sampler2D artwork;uniform sampler2D masks;uniform int useTexture;uniform int kind;uniform float time;uniform float amount;uniform int maskView;
  float bell(float x,float center,float width){return exp(-pow((x-center)/width,2.0));}
  void main(){vec3 c=useTexture==1?texture(artwork,uv).rgb:rgb;vec3 m=texture(masks,uv).rgb;
   if(maskView==1){outColor=vec4(m,1);return;}
   if(amount==0.0){outColor=vec4(c,1);return;}
   float gain=0.0;
   if(kind==0){
    float front=mod(time*.58,1.55)-.2;
    float face=bell(uv.x+uv.y*.12,front,.16);
    float radial=length((uv-vec2(.5,.46))*vec2(1.0,.62));
    float wave=.5+.5*sin(radial*23.0-time*5.1);
    float ornament=(1.0-m.r)*(1.0-m.g)*(1.0-m.b);
    gain=m.r*(face*.50-.06)+ornament*(wave*.64-.25);
    float register=bell(time,1.65,.14);
    gain+=(m.g+m.b)*register*.48;
   }else{
    float front=mod(time*.58+.18,1.75)-.2;
    float enamel=bell(uv.x+uv.y*.30,front,.17);
    float gold=bell(uv.x-uv.y*.16,1.2-mod(time*.41,1.7),.115);
    gain=m.r*(enamel*.90-.13)+(1.0-m.r)*(gold*.72-.08);
   }
   // Exposure in linear light, with a soft shoulder. It cannot paint over small detail.
   vec3 lin=pow(max(c,vec3(0)),vec3(2.2));float exposure=exp2(amount*gain);
   vec3 lit=lin*exposure/(vec3(1)+lin*max(exposure-1.0,0.0));
   outColor=vec4(pow(max(lit,vec3(0)),vec3(1.0/2.2)),1);
  }`;
  const compile=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
  const program=this.program=gl.createProgram(),shaders=[compile(gl.VERTEX_SHADER,vertex),compile(gl.FRAGMENT_SHADER,fragment)];for(const shader of shaders)gl.attachShader(program,shader);gl.linkProgram(program);for(const shader of shaders)gl.deleteShader(shader);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
  this.uniforms=Object.fromEntries(['size','posScale','time','warp','artwork','masks','useTexture','kind','amount','maskView'].map(k=>[k,gl.getUniformLocation(program,k)]));
  gl.uniform2f(this.uniforms.size,width,height);gl.uniform1i(this.uniforms.artwork,0);gl.uniform1i(this.uniforms.masks,1);
  this.buffers=[];this.textures=[];this.setTexture(0,Object.assign(document.createElement('canvas'),{width:1,height:1}));this.setTexture(1,Object.assign(document.createElement('canvas'),{width:1,height:1}));
 }
 setTexture(unit,image){const gl=this.gl;gl.activeTexture(gl.TEXTURE0+unit);if(this.textures[unit])gl.deleteTexture(this.textures[unit]);const tex=gl.createTexture();this.textures[unit]=tex;gl.bindTexture(gl.TEXTURE_2D,tex);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);}
 setGeometry(data){const gl=this.gl;for(const b of this.buffers)gl.deleteBuffer(b);this.buffers=[];
  for(const [name,size,values] of [['position',2,data.positions],['color',3,data.colors]]){const b=gl.createBuffer();this.buffers.push(b);gl.bindBuffer(gl.ARRAY_BUFFER,b);const packed=name==='position'&&values instanceof Uint16Array;const arr=name==='color'?new Uint8Array(values):packed?values:new Float32Array(values);gl.bufferData(gl.ARRAY_BUFFER,arr,gl.STATIC_DRAW);const loc=gl.getAttribLocation(this.program,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,name==='color'?gl.UNSIGNED_BYTE:packed?gl.UNSIGNED_SHORT:gl.FLOAT,name==='color',0,0);if(name==='position')gl.uniform1f(this.uniforms.posScale,packed?.5:1);}
  const indices=gl.createBuffer();this.buffers.push(indices);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indices);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(data.triangles),gl.STATIC_DRAW);this.count=data.triangles.length;this.useTexture=false;
 }
 setArtwork(image){this.setGeometry({positions:[0,0,this.width,0,this.width,this.height,0,this.height],colors:[0,0,0,0,0,0,0,0,0,0,0,0],triangles:[0,1,2,0,2,3]});this.setTexture(0,image);this.useTexture=true;}
 setMasks(data,kind,{feather=3}={}){
  const colors=kind==='keep'?{enamel:'#ff0000'}:{face:'#ff0000',red:'#00ff00',blue:'#0000ff'};
  this.setTexture(1,ArtworkMasks.render(data,{colors,width:this.width,height:this.height,feather}));this.kind=kind==='keep'?1:0;
 }

 draw(seconds,{amount=1,warp=0,maskView=false}={}){const gl=this.gl;gl.useProgram(this.program);gl.viewport(0,0,this.canvas.width,this.canvas.height);gl.uniform1f(this.uniforms.time,seconds);gl.uniform1f(this.uniforms.amount,amount);gl.uniform1f(this.uniforms.warp,warp);gl.uniform1i(this.uniforms.kind,this.kind||0);gl.uniform1i(this.uniforms.maskView,maskView?1:0);gl.uniform1i(this.uniforms.useTexture,this.useTexture?1:0);gl.drawElements(gl.TRIANGLES,this.count,gl.UNSIGNED_INT,0);const error=gl.getError();if(error!==gl.NO_ERROR)throw Error('WebGL error '+error);}
 dispose(){const gl=this.gl;for(const b of this.buffers)gl.deleteBuffer(b);for(const t of this.textures)gl.deleteTexture(t);gl.deleteProgram(this.program);}
};
