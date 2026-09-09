import sharp from 'sharp';
import fs from 'node:fs/promises';
const root = new URL('../', import.meta.url);
const path = p => new URL(p,root).pathname;
const sets=process.argv.slice(2);
const meta={};
for (const name of sets){
 const src=path(`assets/source/${name}.png`);
 const m=await sharp(src).metadata();
 if(!m.hasAlpha) throw new Error(`${name} has no alpha; reject baked background`);
 const {data,info}=await sharp(src).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let clear=0; for(let p=3;p<data.length;p+=4)if(data[p]===0)clear++;
 console.log(name,m.width,m.height,'transparent fraction',clear/(m.width*m.height));
 if(clear/(m.width*m.height)<0.2)throw new Error(`${name}: insufficient clear alpha`);
 const cw=Math.floor(m.width/2),ch=Math.floor(m.height/2);
 for(let n=0;n<4;n++){
  const left=(n%2)*cw,top=Math.floor(n/2)*ch;
  let minX=cw,minY=ch,maxX=0,maxY=0;
  for(let y=0;y<ch;y++)for(let x=0;x<cw;x++){
   if(data[((top+y)*info.width+left+x)*4+3]>24){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}
  }
  let box={left:left+minX,top:top+minY,width:maxX-minX+1,height:maxY-minY+1};
  if(name==='rott-run' && n===0) box={left:26,top:51,width:774,height:337};
  if(name==='rott-run' && n===1) box={left:801,top:50,width:705,height:422};
  await sharp(src).extract(box).png().toFile(path(`assets/cels/${name}-${n}.png`));
  meta[`${name}-${n}`]={width:box.width,height:box.height,sourceCell:[left,top,cw,ch],bounds:[minX,minY,maxX,maxY]};
 }
}
let old={};try{old=JSON.parse(await fs.readFile(path('assets/cels/manifest.json')))}catch{}
await fs.writeFile(path('assets/cels/manifest.json'),JSON.stringify({...old,...meta},null,2));
