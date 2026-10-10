/* Reproducible screenprint plates and explicit-frame motion. All texture is
   computed here and stays attached to the pieces; the reference is never read. */
window.AcidPrint = (() => {
  const W=1536,H=1024,FPS=30,FRAMES=240;
  const PALETTE=['#d8fa24','#fc4322'],PAPER='#0a0b08';
  const canvas=()=>Object.assign(document.createElement('canvas'),{width:W,height:H});
  function random(seed){return ()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296;};}
  const cache=new Map();
  // Two cuts in each row: one fine upper fracture and the dominant descending seam.
  const seam=(row,x)=>row===0?145+x*.238:691+x*.216;
  function region(g,row,band){
    const top=row===0?0:519,bottom=row===0?517:1024;
    const overlap=band===0?.4:-.4,a=seam(row,-250)+overlap,b=seam(row,1800)+overlap;
    g.beginPath();
    if(band===0){g.moveTo(-250,top);g.lineTo(1800,top);g.lineTo(1800,b);g.lineTo(-250,a);}
    else {g.moveTo(-250,a);g.lineTo(1800,b);g.lineTo(1800,bottom);g.lineTo(-250,bottom);}
    g.closePath();
  }
  function buildPlates(texture=true){
    const key=String(texture);if(cache.has(key))return cache.get(key);
    const noise=canvas(),n=noise.getContext('2d'),r=random(91917);
    if(texture){
      // Printed ink loss: sharp pinholes with broad, deterministic density variation.
      const pixels=n.createImageData(W,H),d=pixels.data;
      for(let y=0;y<H;y++)for(let x=0;x<W;x++){
        const v=r(),wave=(Math.sin(x*.016+y*.008)+Math.sin(y*.041-x*.012)+Math.cos(x*.029-y*.022))/3;
        const density=.002+.004*(wave+1),i=(y*W+x)*4;
        d[i]=10;d[i+1]=11;d[i+2]=8;d[i+3]=v<density?80+Math.floor(r()*150):Math.floor(r()*21);
      }n.putImageData(pixels,0,0);
      for(let j=0;j<14500;j++){
        const x=r()*W,y=r()*H,row=y<519?0:1;
        const near=Math.exp(-Math.pow((y-seam(row,x))/66,2));
        if(r()>.18+.72*near)continue;
        n.fillStyle=`rgba(10,11,8,${.2+r()*.65})`;n.beginPath();n.ellipse(x,y,.45+r()*2.1,.4+r()*1.7,r()*3,0,Math.PI*2);n.fill();
      }
      // Selective halftone fields, each with an authored envelope rather than uniform grit.
      const fields=[[285,205,90,180],[568,845,70,180],[1246,317,90,98],[1400,910,148,94],[1040,830,66,140]];
      for(const [cx,cy,rx,ry]of fields)for(let y=cy-ry;y<cy+ry;y+=4.3)for(let x=cx-rx;x<cx+rx;x+=4.3){
        const weight=1-Math.pow((x-cx)/rx,2)-Math.pow((y-cy)/ry,2);if(weight<=0)continue;
        n.fillStyle=`rgba(10,11,8,${.55+r()*.4})`;n.beginPath();n.arc(x+(Math.round(y/4.3)%2)*2.15+(r()-.5)*.9,y+(r()-.5)*.9,Math.min(2.25,weight*(1.7+r())),0,Math.PI*2);n.fill();
      }
    }
    const plates=[];
    for(const shape of PrintGeometry){
      const path=new Path2D(shape.d);
      for(let band=0;band<2;band++){
        const layer=canvas(),g=layer.getContext('2d');
        g.save();g.clip(path,'evenodd');region(g,shape.row,band);g.clip();
        const ink=shape.ink,gradient=g.createLinearGradient(200,0,1300,1024);
        [0,.48,1].forEach((t,i)=>gradient.addColorStop(t,ink?['#f73e23','#ff5924','#f44320'][i]:['#e0fd32','#d6f627','#d2f42c'][i]));
        g.fillStyle=texture?gradient:PALETTE[ink];g.fillRect(0,0,W,H);
        const polygon=(d,color)=>{g.fillStyle=color;g.fill(new Path2D(d));};
        // Local ink changes follow the lettering rather than inverting every lower half.
        if(shape.id==='W'){
          polygon('M0 140 L208 190 L270 520 L60 520 Z',PALETTE[1]);
          polygon('M548 274 L631 295 L505 520 L492 520 Z',PALETTE[1]);
          polygon('M210 193 L556 276 L551 290 L210 208 Z',PAPER);
        }
        if(shape.id==='I')polygon('M580 284 L638 306 L580 471 Z',PAPER);
        if(shape.id==='L')polygon('M759 324 L818 338 L818 395 L759 376 Z',PAPER);
        if(shape.id==='D'){
          polygon('M1136 20 L1331 20 L1410 250 Z',PALETTE[1]);
          polygon('M1279 322 L1410 248 L1291 503 L1279 509 Z',PALETTE[1]);
          polygon('M900 375 L1410 248 L1281 324 L1027 394 Z',PAPER);
        }
        if(shape.id==='H'){
          polygon('M26 702 L126 723 L126 1024 L26 1024 Z',PALETTE[0]);
          polygon('M126 720 L236 744 L162 790 L126 790 Z',PAPER);
        }
        if(shape.id==='O')polygon('M310 752 L635 822 L635 830 L310 760 Z',PAPER);
        if(shape.id==='U')polygon('M639 888 L739 1024 L639 1024 Z',PALETTE[0]);
        if(shape.id==='R')polygon('M923 780 L951 786 L951 1024 L923 1024 Z',PALETTE[1]);
        if(shape.id==='S')polygon('M1224 899 L1367 997 L1224 997 Z',PALETTE[0]);
        // Comb notches and the integrated D fan belong to the plate and move with it.
        g.fillStyle=PAPER;
        if(shape.id==='I'||shape.id==='U'){
          const x=shape.id==='I'?625:810,y=shape.id==='I'?22:525;
          for(let k=0;k<4;k++){g.beginPath();g.moveTo(x+k*26,y);g.lineTo(x+12+k*26,y);g.lineTo(x+12+k*26,y+158-k*26);g.lineTo(x+k*26,y+174-k*26);g.closePath();g.fill();}
        }
        if(shape.id==='D'){
          const cx=1408,cy=248;g.save();g.clip(new Path2D('M1281 0 L1536 0 L1536 400 L1410 300 L1281 247 Z'));g.fillStyle=PAPER;g.fillRect(1281,0,255,400);
          for(let k=0;k<12;k++){
            const a=k*Math.PI/6;g.fillStyle=PALETTE[1];g.beginPath();g.moveTo(cx,cy);g.lineTo(cx+800*Math.cos(a),cy+800*Math.sin(a));g.lineTo(cx+800*Math.cos(a+.25),cy+800*Math.sin(a+.25));g.closePath();g.fill();
          }
          g.restore();
        }
        if(shape.id==='H'||shape.id==='R'){
          const x=shape.id==='H'?26:923;
          for(let yy=734;yy<1000;yy+=42){g.fillStyle=PAPER;g.fillRect(x+((yy-734)/42%2)*17,yy,17,41);}
        }
        if(texture)g.drawImage(noise,0,0);
        g.restore();
        if(texture){
          // Dry-ink flecks spread from authored polygon edges into nearby negative space.
          const edgeR=random(8153+PrintGeometry.indexOf(shape)*713),contours=shape.d.match(/M[^M]+/g);
          g.save();region(g,shape.row,band);g.clip();
          for(const contour of contours){
            const v=contour.match(/-?\d+(?:\.\d+)?/g).map(Number);
            for(let j=0;j<v.length;j+=2){
              const x0=v[j],y0=v[j+1],x1=v[(j+2)%v.length],y1=v[(j+3)%v.length],length=Math.hypot(x1-x0,y1-y0);
              for(let k=0;k<length*.9;k++){
                const t=edgeR(),spread=Math.pow(edgeR(),2)*15,angle=edgeR()*Math.PI*2;
                const x=x0+(x1-x0)*t+Math.cos(angle)*spread,y=y0+(y1-y0)*t+Math.sin(angle)*spread;
                if(g.isPointInPath(path,x,y,'evenodd'))continue;
                g.fillStyle=PALETTE[ink];g.globalAlpha=.1+edgeR()*.52;g.fillRect(x,y,.4+edgeR()*1.4,.4+edgeR()*1.4);
              }
            }
          }g.restore();
        }
        const coords=shape.d.match(/-?\d+(?:\.\d+)?/g).map(Number),xs=coords.filter((_,i)=>i%2===0),ys=coords.filter((_,i)=>i%2===1);
        const x=Math.max(0,Math.floor(Math.min(...xs))-18),y=Math.max(0,Math.floor(Math.min(...ys))-18);
        const width=Math.min(W-x,Math.ceil(Math.max(...xs))-x+18),height=Math.min(H-y,Math.ceil(Math.max(...ys))-y+18);
        const cropped=Object.assign(document.createElement('canvas'),{width,height});cropped.getContext('2d').drawImage(layer,x,y,width,height,0,0,width,height);
        const tint=Object.assign(document.createElement('canvas'),{width,height}),tg=tint.getContext('2d');tg.drawImage(cropped,0,0);tg.globalCompositeOperation='source-in';tg.fillStyle=PALETTE[1-ink];tg.fillRect(0,0,width,height);
        plates.push({canvas:cropped,tint,id:shape.id,path,row:shape.row,band,ink,x,y,cx:x+width/2,cy:y+height/2});
      }
    }
    const background=canvas(),b=background.getContext('2d'),rand=random(3301);b.fillStyle=PAPER;b.fillRect(0,0,W,H);
    if(texture)for(let i=0;i<21000;i++){const x=rand()*W,y=rand()*H;b.fillStyle=i%3?`rgba(159,183,33,${rand()*.15})`:`rgba(229,70,30,${rand()*.2})`;b.fillRect(x,y,rand()*1.5+.2,rand()*1.5+.2);}
    const result={plates,background,noise};cache.set(key,result);return result;
  }
  const motion=PrintMotion.sample;
  function offset(p,m,amount){
    const sign=p.band?1:-1;
    const index=PrintGeometry.findIndex(s=>s.id===p.id);
    const cut=p.row?m.bottom:m.top,stagger=p.row?m.bottomSt:m.topSt;
    const x=sign*cut*62*amount,y=x*.238+(index%2?1:-1)*stagger*55*amount;
    return {x,y,angle:sign*stagger*.018*amount};
  }
  function draw(target,frame=0,options={}){
    const {texture=true,intensity=1,still=false,isolate=''}=options;
    const {plates,background,noise}=buildPlates(texture),g=target.getContext('2d'),m=motion(still||intensity===0?0:frame);
    g.save();g.setTransform(target.width/W,0,0,target.height/H,0,0);g.clearRect(0,0,W,H);g.drawImage(background,0,0);
    for(const p of plates){
      if(isolate&&p.id!==isolate)continue;
      const o=offset(p,m,intensity);
      g.save();g.translate(p.cx+o.x,p.cy+o.y);g.rotate(o.angle);g.translate(-p.cx,-p.cy);
      // Full-opacity second ink plates leave crisp misregistration edges, not shadows.
      if(!still&&m.reg){
        g.drawImage(p.tint,p.x+(p.ink?1:-1)*m.reg*intensity*12,p.y+m.reg*intensity*3);
      }
      g.drawImage(p.canvas,p.x,p.y);
      if(p.id==='D'&&m.fan){
        g.save();g.clip(p.path,'evenodd');region(g,p.row,p.band);g.clip();g.clip(new Path2D('M1281 0 L1536 0 L1536 400 L1410 300 L1281 247 Z'));
        g.fillStyle=PAPER;g.fillRect(1281,0,255,400);g.fillStyle=PALETTE[1];
        for(let k=0;k<12;k++){const a=k*Math.PI/6+m.fan*Math.PI/12;g.beginPath();g.moveTo(1408,248);g.lineTo(1408+800*Math.cos(a),248+800*Math.sin(a));g.lineTo(1408+800*Math.cos(a+.25),248+800*Math.sin(a+.25));g.closePath();g.fill();}
        if(texture)g.drawImage(noise,0,0);g.restore();
      }
      if((p.id==='H'||p.id==='R')&&m.checker){
        const x=p.id==='H'?26:923;g.save();g.clip(p.path,'evenodd');region(g,p.row,p.band);g.clip();g.beginPath();g.rect(x,734,34,265);g.clip();
        g.fillStyle=PALETTE[p.id==='H'?0:1];g.fillRect(x,734,34,265);g.fillStyle=PAPER;
        for(let yy=692;yy<1050;yy+=42)g.fillRect(x+((yy-692)/42%2)*17,yy+(m.checker%2)*21,17,41);
        if(texture)g.drawImage(noise,0,0);g.restore();
      }
      g.restore();
    }
    g.restore();return m;
  }
  function svg(){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}"><rect width="1536" height="1024" fill="${PAPER}"/>${PrintGeometry.map(s=>`<path id="${s.id}" d="${s.d}" fill="${PALETTE[s.ink]}" fill-rule="evenodd"/>`).join('')}</svg>`;}
  return {draw,svg,motion,W,H,FPS,FRAMES};
})();
