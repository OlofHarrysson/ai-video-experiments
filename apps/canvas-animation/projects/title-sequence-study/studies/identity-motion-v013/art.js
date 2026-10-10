/* Ordered vectors are rendered once. Every motion layer comes from that drawing. */
window.IdentityMotion = (() => {
  const W=1600,H=900,FPS=24,N=96;
  const clamp=x=>Math.max(0,Math.min(1,x));
  const ease=x=>1-Math.pow(1-clamp(x),3);
  const canvas=()=>Object.assign(document.createElement('canvas'),{width:W,height:H});
  const assets={};
  function prepare(id,data){
    const plate=canvas(),g=plate.getContext('2d',{willReadFrequently:true});
    g.fillStyle='#000';g.fillRect(0,0,W,H);g.scale(W/data.width,H/data.height);
    for(const p of data.paths){const t=p.transform.match(/[-\d.]+/g)||[0,0];g.save();g.translate(+t[0],+t[1]);g.fillStyle=p.fill;g.fill(new Path2D(p.d));g.restore();}
    const pixels=g.getImageData(0,0,W,H);
    const types=id==='next'?['cool','face','red']:id==='billions'?['face','ornament','red','blue']:['red','gold','bright'];
    const layers=Object.fromEntries(types.map(k=>[k,canvas()]));
    const buffers=Object.fromEntries(types.map(k=>[k,new ImageData(W,H)]));
    for(let i=0;i<pixels.data.length;i+=4){
      const r=pixels.data[i],b=pixels.data[i+2],v=pixels.data[i+1];let k;
      if(id==='next')k=r>180&&v<80?'red':v>170&&r>160?'face':b>70?'cool':null;
      else if(id==='billions')k=r>80&&r>v*1.8?'red':b>40&&b>r*1.2?'blue':r>175&&v>135?'face':Math.max(r,v,b)>16?'ornament':null;
      else k=r>45&&r>v*2.1?'red':r>210&&v>180?'bright':Math.max(r,v,b)>20?'gold':null;
      if(k){const out=buffers[k].data;out[i]=r;out[i+1]=v;out[i+2]=b;out[i+3]=255;}
    }
    for(const k of types)layers[k].getContext('2d').putImageData(buffers[k],0,0);
    if(id==='next'){
      const src=buffers.face.data,edge=new ImageData(W,H);
      for(let y=3;y<H-3;y++)for(let x=3;x<W-3;x++){
        const i=(y*W+x)*4;if(!src[i+3])continue;
        if([[-3,0],[3,0],[0,-3],[0,3],[-2,-2],[2,2]].some(([dx,dy])=>!src[((y+dy)*W+x+dx)*4+3])){edge.data[i]=246;edge.data[i+1]=240;edge.data[i+2]=220;edge.data[i+3]=255;}
      }
      layers.outline=canvas();layers.outline.getContext('2d').putImageData(edge,0,0);
    }
    assets[id]={plate,layers};
  }
  const scratch=canvas();
  function ink(g,layer,color,alpha=1,dx=0,dy=0){
    const q=scratch.getContext('2d');q.clearRect(0,0,W,H);q.globalCompositeOperation='source-over';q.drawImage(layer,0,0);q.globalCompositeOperation='source-in';q.fillStyle=color;q.fillRect(0,0,W,H);q.globalCompositeOperation='source-over';
    g.save();g.globalAlpha=alpha;g.drawImage(scratch,dx,dy);g.restore();
  }
  function light(g,layer,x,width,color,strength,angle=.38){
    const q=scratch.getContext('2d');q.clearRect(0,0,W,H);q.globalCompositeOperation='source-over';q.drawImage(layer,0,0);q.globalCompositeOperation='source-in';
    const grad=q.createLinearGradient(x-width,-H*.2,x+width,H*angle);grad.addColorStop(0,'transparent');grad.addColorStop(.44,'transparent');grad.addColorStop(.5,color);grad.addColorStop(.56,'transparent');grad.addColorStop(1,'transparent');
    q.fillStyle=grad;q.fillRect(0,0,W,H);q.globalCompositeOperation='source-over';g.save();g.globalCompositeOperation='screen';g.globalAlpha=strength;g.drawImage(scratch,0,0);g.restore();
  }
  function reveal(g,layer,p,reverse=false){
    const x=-500+ease(p)*2200;g.save();g.beginPath();
    if(reverse){g.moveTo(W-x,0);g.lineTo(W,0);g.lineTo(W,H);g.lineTo(W-x-280,H);}
    else {g.moveTo(0,0);g.lineTo(x,0);g.lineTo(x+280,H);g.lineTo(0,H);}
    g.closePath();g.clip();g.drawImage(layer,0,0);g.restore();
  }
  function billions(g,f){
    const {plate,layers:l}=assets.billions;
    if(f<16){
      g.globalAlpha=.5+.5*ease(f/12);for(const k of ['ornament','red','blue'])g.drawImage(l[k],0,0);g.globalAlpha=1;
      // Short stepped registration and staggered vertical ink strips.
      const bounds=[0,316,449,610,779,898,1098,1310,1600];
      for(let i=0;i<bounds.length-1;i++){const p=ease((Math.floor(f/2)*2+5-i*.8)/12),x=bounds[i],w=bounds[i+1]-x;g.save();g.beginPath();g.rect(x,0,w,H);g.clip();g.drawImage(l.face,0,(i%2?1:-1)*(1-p)*95);g.restore();}
    }else g.drawImage(plate,0,0);
    const cycle=(f-14)/62;
    if(f>=14&&f<76){ink(g,l.ornament,'#5b3709',.35);light(g,l.ornament,-350+cycle*2300,600,'#ffe1a0',.95,.55);light(g,l.face,-500+cycle*2400,700,'#fff5d0',.24,.4);}
    if(f>=38&&f<46){const d=(46-f)/8;ink(g,l.red,'#ff2015',.85,d*12,0);ink(g,l.blue,'#074cff',.9,-d*12,0);}
    if(f>=76&&f<86){light(g,l.ornament,1800-(f-76)*190,500,'#f3c45b',1.1,-.4);}
  }
  function next(g,f){
    const {plate,layers:l}=assets.next;
    if(f<15){
      g.drawImage(l.cool,0,0);reveal(g,l.face,(f+5)/13);reveal(g,l.red,(f-2)/10,true);
    }else if(f>=36&&f<45){
      g.drawImage(l.cool,0,0);g.drawImage(l.red,0,0);
      // A single outline break, followed by an angled return of the face ink.
      g.drawImage(l.outline,0,0);
      reveal(g,l.face,(f-38)/6,true);
    }else g.drawImage(plate,0,0);
    if(f>=16&&f<33){light(g,l.cool,-200+(f-16)*120,700,'#67faff',1.0);}
    if(f>=49&&f<59){
      // Only foreground red ink shifts; main word remains planted.
      g.drawImage(plate,0,0);ink(g,l.red,'#000');const d=(1-ease((f-49)/10))*40;g.drawImage(l.red,d,-d*.25);
    }
    if(f>=65&&f<82){light(g,l.face,1900-(f-65)*135,650,'#ffffff',.8,-.5);light(g,l.red,-200+(f-65)*120,400,'#ffb6a0',.55);}
  }
  function glint(g,x,y,size,alpha,turn){
    g.save();g.translate(x,y);g.rotate(turn);g.globalCompositeOperation='screen';g.globalAlpha=alpha;
    const a=g.createRadialGradient(0,0,0,0,0,size*.7);a.addColorStop(0,'#fff6d7');a.addColorStop(.12,'#fac66b99');a.addColorStop(1,'#e3791700');g.fillStyle=a;g.fillRect(-size,-size,size*2,size*2);
    g.fillStyle='#fff5dc';g.beginPath();g.moveTo(-size,0);g.lineTo(-3,-2);g.lineTo(0,-size*.7);g.lineTo(3,-2);g.lineTo(size,0);g.lineTo(3,2);g.lineTo(0,size*.7);g.lineTo(-3,2);g.closePath();g.fill();g.restore();
  }
  function keep(g,f){
    const {plate,layers:l}=assets.keep;g.drawImage(plate,0,0);
    // Separate enamel and edging responses; highlights remain inside the artwork.
    const p=(f%64)/64;
    ink(g,l.red,'#180001',.12+.09*Math.sin(f*.065));
    light(g,l.red,-700+p*3300,1050,'#ffa659',.8,.65);
    light(g,l.gold,-250+p*2100,600,'#fff2bb',1.1,.2);
    light(g,l.bright,1800-p*2500,500,'#ffffff',.7,-.5);
    if(f>=22&&f<39)glint(g,323,138,18+34*Math.sin((f-22)/17*Math.PI),Math.sin((f-22)/17*Math.PI)*.75,.15);
    if(f>=54&&f<73)glint(g,1183,430,20+38*Math.sin((f-54)/19*Math.PI),Math.sin((f-54)/19*Math.PI)*.8,-.16);
  }
  function draw(c,n){
    n=((Math.floor(n)%288)+288)%288;const scene=Math.floor(n/N),f=n%N,g=c.getContext('2d');g.setTransform(c.width/W,0,0,c.height/H,0,0);g.globalCompositeOperation='source-over';g.globalAlpha=1;g.fillStyle='#000';g.fillRect(0,0,W,H);
    [billions,next,keep][scene](g,f);
  }
  return {prepare,draw,width:W,height:H,fps:FPS,frames:N*3,scenes:['BILLIONS','NEXT','KEEP UP']};
})();
