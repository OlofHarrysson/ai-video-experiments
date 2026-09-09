import fs from 'node:fs/promises';
import sharp from 'sharp';

// Adjacent-cel inspection at the unchanged source coordinates.
const ids=process.argv.slice(2);
if(ids.length<2)throw new Error('Supply two or more prepared frame IDs');
const panels=[],metrics=[];
for(const id of ids){
 const input=`assets/dense-nuzzle/frames/${id}.png`;
 const {data,info}=await sharp(input).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let xSum=0,ySum=0,n=0;
 // Restricted nose region; a diagnostic landmark, not a semantic motion guarantee.
 for(let y=470;y<520;y++)for(let x=1060;x<1220;x++){
  const k=(y*info.width+x)*4;
  if(data[k+3]>200 && data[k]<70 && data[k+1]<65 && data[k+2]<60){xSum+=x;ySum+=y;n++;}
 }
 metrics.push({id,width:info.width,height:info.height,darkNoseRegion:{count:n,x:n?xSum/n:null,y:n?ySum/n:null}});
 const panel=await sharp(input).flatten({background:'#e8dfcc'}).resize(836,471).png().toBuffer();
 panels.push({input:panel,left:0,top:(panels.length)*495});
}
const stem=ids.join('-');
await sharp({create:{width:836,height:495*ids.length,channels:3,background:'#252b2b'}}).composite(panels).png().toFile(`review/dense-nuzzle/${stem}.png`);
await fs.writeFile(`review/dense-nuzzle/${stem}.json`,JSON.stringify(metrics,null,2));
console.log(JSON.stringify(metrics));
