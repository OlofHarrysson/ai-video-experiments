/* Ordered authored masks partition a flattened plate without retracing its colors. */
window.splitArtworkPlate = (image, rig) => {
  if (image.width !== rig.width || image.height !== rig.height) throw Error('Rig/source dimensions differ');
  const {width:w,height:h}=rig,source=Object.assign(document.createElement('canvas'),{width:w,height:h}),g=source.getContext('2d',{willReadFrequently:true});
  g.drawImage(image,0,0);const pixels=g.getImageData(0,0,w,h).data,owned=new Uint8Array(w*h),layers=[];
  for(const spec of rig.layers){
    g.clearRect(0,0,w,h);g.fillStyle='white';g.fill(new Path2D(spec.path),'evenodd');if(spec.padding){g.strokeStyle='white';g.lineWidth=spec.padding*2;g.lineJoin='round';g.stroke(new Path2D(spec.path));}const mask=g.getImageData(0,0,w,h).data;
    let x0=w,y0=h,x1=0,y1=0,count=0;const indices=[];
    for(let i=0;i<w*h;i++)if(!owned[i]&&mask[i*4+3]>=128){owned[i]=1;indices.push(i);if(pixels[i*4]+pixels[i*4+1]+pixels[i*4+2]>0){const x=i%w,y=Math.floor(i/w);x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);count++;}}
    if(!count)throw Error('Empty visible layer '+spec.id);
    x0=Math.max(0,x0-2);y0=Math.max(0,y0-2);x1=Math.min(w-1,x1+2);y1=Math.min(h-1,y1+2);
    const c=Object.assign(document.createElement('canvas'),{width:x1-x0+1,height:y1-y0+1}),ctx=c.getContext('2d'),data=ctx.createImageData(c.width,c.height);
    for(const i of indices){const x=i%w,y=Math.floor(i/w);if(x<x0||x>x1||y<y0||y>y1)continue;const j=((y-y0)*c.width+x-x0)*4;data.data[j]=pixels[i*4];data.data[j+1]=pixels[i*4+1];data.data[j+2]=pixels[i*4+2];data.data[j+3]=255;}
    ctx.putImageData(data,0,0);
    layers.push({...spec,canvas:c,x:x0,y:y0,visiblePixels:count});
  }
  if(owned.some(x=>!x))throw Error('Rig does not assign every source pixel');
  return layers;
};
