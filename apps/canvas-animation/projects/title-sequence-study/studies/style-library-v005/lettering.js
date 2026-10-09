/* Original connected Wild lettering, drawn as cubic centreline paths. */
window.DrawnLettering=(()=>{
  const d='M118 415 C37 438 58 329 164 319 C232 313 291 233 284 155 C276 94 228 163 216 253 C202 361 223 480 275 482 C322 484 366 383 390 291 C365 381 358 478 401 472 C450 466 503 329 500 246 C505 321 509 384 530 412 C544 429 568 408 577 353 C560 390 541 443 566 443 C589 443 622 400 643 350 C697 233 717 108 678 157 C639 210 623 370 651 426 C677 477 723 422 750 370 C785 304 852 318 838 368 C822 425 774 461 754 432 C722 399 809 309 865 331 C874 286 899 168 928 172 C959 177 913 302 872 370 C851 406 847 456 888 440 C922 426 969 379 1000 361 C1087 305 1191 370 1127 442 C1103 470 1067 451 1080 432';
  const path=new Path2D(d),dot={x:587,y:292},maskCache=new Map();
  const svg=document.createElementNS('http://www.w3.org/2000/svg','path');svg.setAttribute('d',d);const length=svg.getTotalLength(),samples=[];
  for(let i=0;i<=length;i+=5){const p=svg.getPointAtLength(i);samples.push([p.x,p.y])}
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
  return {path,geometry,mask,tube,ribbon,samples,length};
})();
