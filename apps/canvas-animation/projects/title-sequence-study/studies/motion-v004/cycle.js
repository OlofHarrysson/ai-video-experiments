window.RenderCycle=(()=>{
 const W=1280,H=544,make=()=>Object.assign(document.createElement('canvas'),{width:W,height:H});
 const colors=['#ed469e','#5e42a0','#639ed3','#9eefce'];
 const random=i=>{const x=Math.sin(i*127.1+311.7)*43758.5453;return x-Math.floor(x)};
 const layer=(g,dx,dy,fill,stroke,lw)=>DesignStudy.nightLayer(g,dx,dy,fill,stroke,lw);
 const mask=make(),mg=mask.getContext('2d');layer(mg,0,0,'#fff','#fff',2);const pixels=mg.getImageData(0,0,W,H).data;
 const maskPoints=[];for(let y=8;y<H;y+=10)for(let x=8;x<W;x+=10)if(pixels[(y*W+x)*4+3]>180)maskPoints.push([x,y]);
 const plates=Array.from({length:6},(_,id)=>{const c=make(),g=c.getContext('2d');g.fillStyle='#030305';g.fillRect(0,0,W,H);
  if(id===0)DesignStudy.render(0,0,c,true);
  if(id===1){[[15,13,'#6b4dab'],[9,7,'#ef4ca0'],[3,2,'#74b3dc']].forEach(([x,y,color])=>layer(g,x,y,null,color,13));layer(g,0,0,'#fff1dc','#4e183b',3)}
  if(id===2){[[12,9,'#6547c2'],[5,5,'#ef3b78'],[-3,-2,'#8cefcd']].forEach(([x,y,color])=>layer(g,x,y,null,color,3.2));layer(g,0,0,null,'#ffe9d7',1)}
  if(id===3){layer(g,0,0,null,'#e24892',15);layer(g,0,0,'#030305','#713579',9);layer(g,0,0,null,'#ffdabd',2)}
  if(id===4){layer(g,13,11,'#8c164d','#8c164d',8);layer(g,5,4,null,'#ffa1bc',8);layer(g,0,0,'#38173d','#9d6cb7',2)}
  if(id===5){layer(g,0,0,null,'#ef74b5',1);maskPoints.forEach(([x,y],i)=>{g.fillStyle=colors[Math.floor(y/80)%4];g.beginPath();g.arc(x,y,2.8,0,Math.PI*2);g.fill()})}
  return c;
 });
 // A fixed contour registers every treatment. Only material and surrounding stars change.
 function render(t,c,{hold=4,label=false,partner=true}={}){
  const frame=Math.floor(t*24+1e-7),treatment=Math.floor(frame/hold)%6,g=c.getContext('2d');g.resetTransform();g.globalCompositeOperation='source-over';g.globalAlpha=1;g.fillStyle='#030305';g.fillRect(0,0,c.width,c.height);
  g.globalAlpha=partner&&frame%2?0.88:1;g.drawImage(plates[treatment],0,0);g.globalAlpha=1;
  // Avoid placing new stars inside the letter silhouette. They move on paired frames.
  const seed=Math.floor(frame/2)*201;
  for(let i=0;i<72;i++){const x=Math.floor(18+random(seed+i)*1240),y=Math.floor(14+random(seed+i+101)*510);if(pixels[(y*W+x)*4+3]>0)continue;
   const r=2+random(seed+i+400)*6;g.save();g.translate(x,y);g.rotate(i);g.beginPath();for(let j=0;j<10;j++){const a=j*Math.PI/5,rr=j%2?r*.45:r;g.lineTo(Math.cos(a)*rr,Math.sin(a)*rr)}g.closePath();g.fillStyle=colors[i%4];g.globalAlpha=.65;g.fill();g.restore()}
  if(label){g.globalAlpha=1;g.fillStyle='#151515';g.fillRect(0,H,W,44);g.fillStyle='#eee';g.font='20px system-ui';g.fillText(`${hold===6?'Slower':hold===4?'Medium':'Faster'} · ${hold} frames per treatment · ${24/hold} changes/second`,22,H+29)}
  return {frame,treatment,hold};
 }
 return {W,H,render,names:['Lacquer','Cream and echoes','Contour echoes','Hollow bevel','Silhouette','Dot fill']};
})();
