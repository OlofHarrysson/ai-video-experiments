/* CPU bevel/reflection study: a cached distance field turns a 2D mask into a surface.
   This is a lighting approximation, not a 3D mesh or physically based renderer. */
window.TypeSurface=(()=>{
  const fields=new Map(),renders=new Map(),lamps=new Map();
  const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
  function euclideanDistance(d,w,h){
    // Separable squared-distance envelopes; see SURFACE-NOTES.md for attribution.
    const length=Math.max(w,h),input=new Float64Array(length),result=new Float64Array(length),sites=new Int32Array(length),bounds=new Float64Array(length+1);
    function axis(size){
      let tail=0;sites[0]=0;bounds[0]=-Infinity;bounds[1]=Infinity;
      for(let q=1;q<size;q++){
        let cross;while(true){const p=sites[tail];cross=((input[q]+q*q)-(input[p]+p*p))/(2*(q-p));if(cross>bounds[tail])break;tail--}
        sites[++tail]=q;bounds[tail]=cross;bounds[tail+1]=Infinity;
      }
      let k=0;for(let q=0;q<size;q++){while(bounds[k+1]<q)k++;const delta=q-sites[k];result[q]=delta*delta+input[sites[k]]}
    }
    for(let x=0;x<w;x++){for(let y=0;y<h;y++)input[y]=d[y*w+x];axis(h);for(let y=0;y<h;y++)d[y*w+x]=result[y]}
    for(let y=0;y<h;y++){for(let x=0;x<w;x++)input[x]=d[y*w+x];axis(w);for(let x=0;x<w;x++)d[y*w+x]=Math.sqrt(result[x])}
    return d;
  }
  function field(key,mask){
    if(fields.has(key))return fields.get(key);
    const w=mask.width,h=mask.height,n=w*h,rgba=mask.getContext('2d').getImageData(0,0,w,h).data,d=new Float32Array(n),alpha=new Uint8Array(n);
    for(let i=0;i<n;i++){alpha[i]=rgba[i*4+3];d[i]=alpha[i]>127?1e5:0}
    euclideanDistance(d,w,h);
    // Smooth the distance gradients before lighting; raw grid distances create ribs.
    let smooth=d;
    for(let pass=0;pass<3;pass++){
      const horizontal=new Float32Array(n),vertical=new Float32Array(n);
      for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++){const i=y*w+x;horizontal[i]=(smooth[i-2]+4*smooth[i-1]+6*smooth[i]+4*smooth[i+1]+smooth[i+2])/16}
      for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++){const i=y*w+x;vertical[i]=(horizontal[i-2*w]+4*horizontal[i-w]+6*horizontal[i]+4*horizontal[i+w]+horizontal[i+2*w])/16}
      smooth=vertical;
    }
    const pixels=[];for(let y=1;y<h-1;y++)for(let x=1;x<w-1;x++){const i=y*w+x;if(!alpha[i])continue;const dx=(smooth[i+1]-smooth[i-1])*.5,dy=(smooth[i+w]-smooth[i-w])*.5;pixels.push([i,x,y,smooth[i],dx,dy,alpha[i]])}
    const value={w,h,pixels,distance:d};fields.set(key,value);if(fields.size>8)fields.delete(fields.keys().next().value);return value;
  }
  function mixStops(t,stops){for(let i=1;i<stops.length;i++)if(t<=stops[i][0]){const [a,ca]=stops[i-1],[b,cb]=stops[i],p=clamp((t-a)/(b-a));return ca.map((v,j)=>v+(cb[j]-v)*p)}return stops.at(-1)[1]}
  const chrome=[[0,[240,218,248]],[.22,[143,162,191]],[.39,[39,36,70]],[.48,[11,13,28]],[.505,[255,244,225]],[.57,[115,193,221]],[.73,[43,56,111]],[1,[246,214,226]]];
  const gold=[[0,[255,239,174]],[.28,[221,155,70]],[.47,[60,27,44]],[.5,[250,225,165]],[.62,[193,106,41]],[.81,[66,27,57]],[1,[255,233,176]]];
  function draw(g,key,mask,state,frame,{bevel=25}={}){
    const step=Math.floor(frame/4)%12,cacheKey=[key,state,step,bevel].join('|');
    if(renders.has(cacheKey)){g.drawImage(renders.get(cacheKey),0,0);return}
    const {w,h,pixels}=field(key,mask),c=Object.assign(document.createElement('canvas'),{width:w,height:h}),q=c.getContext('2d'),im=q.createImageData(w,h),out=im.data,angle=(step/12-.5)*.36;
    for(const [i,x,y,d,dx,dy,a]of pixels){
      const t=clamp(d/bevel),edge=1-t,nx=-dx*edge,ny=-dy*edge,nz=Math.sqrt(Math.max(.001,1-nx*nx-ny*ny)),rx=2*nz*nx,ry=2*nz*ny;
      const e=clamp(.5+ry*.42+rx*.11+angle),light=clamp(nx*-.3+ny*-.48+nz*.82),fresnel=Math.pow(1-nz,3);
      let rgb;
      if(state===1){const spec=Math.pow(clamp(nx*-.3+ny*-.6+nz*.72),24);rgb=[230,68,88].map((v,j)=>v*(.23+.7*light)+spec*230+fresnel*(j===2?60:30))}
      else if(state===3){const band=Math.sin((x+y*.3)*.042+step*.46);const base=band>0?[228,194,140]:[55,134,193];rgb=base.map(v=>v*(.24+light*.8)+Math.pow(light,18)*130)}
      else{rgb=mixStops(e,state===2?gold:chrome).map(v=>v*(.7+nz*.3)+fresnel*35)}
      out[i*4]=clamp(rgb[0],0,255);out[i*4+1]=clamp(rgb[1],0,255);out[i*4+2]=clamp(rgb[2],0,255);out[i*4+3]=a;
    }
    q.putImageData(im,0,0);g.drawImage(c,0,0);renders.set(cacheKey,c);if(renders.size>36)renders.delete(renders.keys().next().value);
  }
  function lampCenters(key,mask,spacing=14){
    const cacheKey=key+':'+spacing;if(lamps.has(cacheKey))return lamps.get(cacheKey);
    const {w,h,distance:d}=field(key,mask),candidates=[];
    for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++){
      const i=y*w+x,v=d[i];if(v<5)continue;
      if((v>=d[i-1]&&v>d[i+1])||(v>=d[i-w]&&v>d[i+w]))candidates.push([x,y,v]);
    }
    candidates.sort((a,b)=>b[2]-a[2]||a[1]-b[1]||a[0]-b[0]);
    const bins=new Map(),points=[],size=spacing;
    for(const [x,y]of candidates){const bx=Math.floor(x/size),by=Math.floor(y/size);let near=false;
      for(let dy=-1;dy<=1&&!near;dy++)for(let dx=-1;dx<=1&&!near;dx++)for(const p of bins.get((bx+dx)+','+(by+dy))||[])if(Math.hypot(x-p[0],y-p[1])<spacing){near=true;break}
      if(near)continue;const p=[x,y],k=bx+','+by;if(!bins.has(k))bins.set(k,[]);bins.get(k).push(p);points.push(p);
    }
    lamps.set(cacheKey,points);if(lamps.size>8)lamps.delete(lamps.keys().next().value);return points;
  }
  return {draw,lampCenters,euclideanDistance};
})();
