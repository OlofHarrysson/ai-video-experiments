/* Original connected Wild lettering, drawn as cubic centreline paths. */
window.DrawnLettering=(()=>{
  const d='M118 415 C37 438 58 329 164 319 C232 313 291 233 284 155 C276 94 228 163 216 253 C202 361 223 480 275 482 C322 484 366 383 390 291 C365 381 358 478 401 472 C450 466 503 329 500 246 C505 321 509 384 530 412 C548 430 565 400 577 353 C577 392 574 442 594 441 C612 440 631 384 643 350 C697 233 717 108 678 157 C639 210 623 370 651 426 C677 477 723 422 750 370 C785 304 852 318 838 368 C822 425 774 461 754 432 C722 399 809 309 865 331 C874 286 899 168 928 172 C959 177 913 302 872 370 C851 406 847 456 888 440 C922 426 969 379 1000 361 C1087 305 1191 370 1127 442 C1103 470 1067 451 1080 432';
  const path=new Path2D(d),dot={x:587,y:292},maskCache=new Map();
  const svg=document.createElementNS('http://www.w3.org/2000/svg','path');svg.setAttribute('d',d);const length=svg.getTotalLength(),samples=[];
  for(let i=0;i<=length;i+=5){const p=svg.getPointAtLength(i);samples.push([p.x,p.y])}
  const surfaceSamples=[];for(let t=0;t<=length;t+=1){const p=svg.getPointAtLength(t);surfaceSamples.push([p.x,p.y])}
  const segments=surfaceSamples.slice(1).map((p,i)=>[...surfaceSamples[i],...p]);segments.push([dot.x,dot.y,dot.x,dot.y]);
  function geometry(g,stroke,width){g.save();g.lineJoin='round';g.lineCap='round';g.strokeStyle=stroke;g.lineWidth=width;g.stroke(path);g.fillStyle=stroke;g.beginPath();g.arc(dot.x,dot.y,width*.53,0,Math.PI*2);g.fill();g.restore()}
  function mask(width=34){if(maskCache.has(width))return maskCache.get(width);const c=Object.assign(document.createElement('canvas'),{width:1280,height:720});geometry(c.getContext('2d'),'#fff',width);maskCache.set(width,c);return c}
  function tube(g,state,frame){
    const col=state===2?'#69d5eb':'#f85b96';
    for(const[w,c]of [[25,'#24202a'],[19,state===1?'#66616c':col],[10,state===1?'#131019':'#ffe5eb'],[3,state===1?'#847380':'#fffaf4']])geometry(g,c,w);
    if(state===2){g.save();g.lineWidth=12;g.strokeStyle='#ed56a4';g.lineCap='round';g.setLineDash([120,220]);g.lineDashOffset=-Math.floor(frame/2)*17;g.stroke(path);g.restore()}
    if(state===3){g.save();g.strokeStyle='#24202b';g.lineWidth=18;g.lineCap='round';g.setLineDash([44,600]);g.lineDashOffset=-Math.floor(frame/4)*24;g.stroke(path);g.restore()}
    // Tube terminals, aligned to the entry and exit tangents.
    for(const[x,y]of [[118,415],[1080,432]]){g.fillStyle='#38323d';g.fillRect(x-5,y-10,10,20);g.fillStyle='#a08b96';g.fillRect(x-2,y-8,2,16)}
  }
  function ribbon(g,state,frame){
    const colors=state===1?['#e25c4c','#571847','#fed8af']:state===3?['#73bcbc','#685ac0','#e9ac71']:['#ead7ad','#424ca7','#fbf0d2'];
    g.save();g.translate(5,7);geometry(g,'#1c1a29',33);g.restore();
    if(state===2){geometry(g,'#d4c7b9',1.5);for(const[x,y]of samples.filter((_,i)=>i%13===0)){g.fillStyle='#9687a1';g.fillRect(x-2,y-2,4,4)}return}
    geometry(g,colors[1],30);
    for(let i=1;i<samples.length;i++){const [x,y]=samples[i-1],[ex,ey]=samples[i],dx=ex-x,dy=ey-y,len=Math.hypot(dx,dy)||1,nx=-dy/len*14,ny=dx/len*14;
      g.beginPath();g.moveTo(x+nx,y+ny);g.lineTo(ex+nx,ey+ny);g.lineTo(ex-nx,ey-ny);g.lineTo(x-nx,y-ny);g.closePath();g.fillStyle=colors[(Math.floor(i/90)+(state===3?Math.floor(frame/4):0))%2];g.fill();
      g.beginPath();g.moveTo(x+nx,y+ny);g.lineTo(ex+nx,ey+ny);g.lineTo(ex,ey);g.lineTo(x,y);g.closePath();g.fillStyle=colors[2];g.globalAlpha=.45;g.fill();g.globalAlpha=1;
    }
    g.fillStyle=colors[0];g.beginPath();g.arc(dot.x,dot.y,15,0,Math.PI*2);g.fill();
  }
  // Downstroke pressure gives the same original path a different silhouette from neon tubing.
  function ink(g,color,expansion=0){
    g.save();g.strokeStyle=color;g.fillStyle=color;g.lineCap='round';g.lineJoin='round';
    for(let i=1;i<samples.length;i++){
      const [x,y]=samples[i-1],[ex,ey]=samples[i],len=Math.hypot(ex-x,ey-y)||1;
      const vertical=Math.max(0,(ey-y)/len);
      g.lineWidth=5+29*Math.pow(vertical,1.6)+expansion;
      g.beginPath();g.moveTo(x,y);g.lineTo(ex,ey);g.stroke();
    }
    g.beginPath();g.ellipse(dot.x,dot.y,10+expansion/2,14+expansion/2,-.3,0,Math.PI*2);g.fill();g.restore();
  }
  function signature(g,state,frame){
    const schemes=[['#492264','#f551a1','#ffd07f','#f9f1da'],['#075764','#41d4cf','#263276','#f1eedf'],['#563320','#bc733a','#f3cd77','#1b1522'],['#3c1e74','#6d59d9','#d15b9e','#f6ddd0']];
    const colors=schemes[state%4];
    for(let i=18;i>0;i--){g.save();g.translate(i*.68,i*.88);ink(g,colors[0],15);g.restore()}
    ink(g,colors[1],15);ink(g,colors[2],7);ink(g,colors[3]);
    if(state===2||state===3){
      const c=Object.assign(document.createElement('canvas'),{width:1280,height:720}),q=c.getContext('2d');ink(q,'#fff');
      const pattern=Object.assign(document.createElement('canvas'),{width:1280,height:720}),p=pattern.getContext('2d');
      if(state===2){for(let y=0;y<720;y+=7){p.fillStyle=y%14?'#e3b35f':'#fce1a0';p.fillRect(0,y,1280,2)}}
      else {const offset=Math.floor(frame/3)*19;for(let x=-720;x<1700;x+=96){p.save();p.translate(x+offset%96,0);p.transform(1,0,-.35,1,0,0);p.fillStyle='#d680bd';p.fillRect(0,0,19,720);p.restore()}}
      q.globalCompositeOperation='source-in';q.drawImage(pattern,0,0);g.drawImage(c,0,0);
    }
  }
  return {path,svgPath:d,dot,geometry,mask,tube,ribbon,signature,samples,segments,length};
})();
