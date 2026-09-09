import fs from 'node:fs/promises';
import sharp from 'sharp';
const ROOT='assets/paw-touch';
const W=512,H=512;
await fs.mkdir(`${ROOT}/cels`,{recursive:true});
await fs.mkdir('review/paw-touch',{recursive:true});
const raw=async p=>sharp(p).ensureAlpha().raw().toBuffer({resolveWithObject:true});
const save=async(data,path,w=W,h=H)=>sharp(data,{raw:{width:w,height:h,channels:4}}).png().toFile(path);
function keyWhite(data,w,h){
 const seen=new Uint8Array(w*h),q=new Int32Array(w*h);let a=0,b=0;
 const add=i=>{if(i<0||i>=w*h||seen[i])return;const k=i*4;if(Math.min(data[k],data[k+1],data[k+2])>230&&Math.max(data[k],data[k+1],data[k+2])-Math.min(data[k],data[k+1],data[k+2])<22){seen[i]=1;q[b++]=i;}};
 for(let x=0;x<w;x++){add(x);add((h-1)*w+x);}for(let y=0;y<h;y++){add(y*w);add(y*w+w-1);}
 while(a<b){const i=q[a++];data[i*4+3]=0;if(i%w)add(i-1);if(i%w<w-1)add(i+1);add(i-w);add(i+w);}
 return data;
}
const candidates=[];
for(let i=0;i<12;i++){
 const sheet=i<6?'keyposes':'inbetweens',cell=i%6;
 const {data}=await sharp(`${ROOT}/source/${sheet}.png`).extract({left:(cell%3)*W,top:Math.floor(cell/3)*H,width:W,height:H}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 keyWhite(data,W,H);candidates.push(data);await save(data,`${ROOT}/cels/raw-${i}.png`);
}
const master=candidates[0];
// Register unchanged head, near foreleg and rump. The acting foreleg is excluded.
const points=[];for(let y=60;y<458;y+=4)for(let x=50;x<465;x+=4){if((y<285||x>230)&&master[(y*W+x)*4+3]>240)points.push([x,y]);}
function cost(src,dx,dy){let sum=0;for(const[x,y]of points){const sx=x-dx,sy=y-dy;if(sx<0||sx>=W||sy<0||sy>=H){sum+=600;continue;}const k=(y*W+x)*4,j=(sy*W+sx)*4;for(let c=0;c<3;c++)sum+=Math.abs(master[k+c]-(src[j+3]?src[j+c]:255));}return sum/points.length;}
function aligned(src,dx,dy){const dst=Buffer.alloc(W*H*4);for(let y=0;y<H;y++)for(let x=0;x<W;x++){const sx=x-dx,sy=y-dy;if(sx>=0&&sx<W&&sy>=0&&sy<H)src.copy(dst,(y*W+x)*4,(sy*W+sx)*4,(sy*W+sx)*4+4);}return dst;}
const maskSvg=Buffer.from(`<svg width="512" height="512"><path d="M 20 295 L 160 295 L 196 307 L 207 330 L 211 347 L 198 385 L 191 475 L 20 475 Z" fill="white"/></svg>`);
const mask=await sharp(maskSvg).ensureAlpha().blur(1).raw().toBuffer();
const records=[];
for(let i=0;i<candidates.length;i++){
 let best={dx:0,dy:0,cost:Infinity};
 for(let dy=-12;dy<=52;dy+=2)for(let dx=-30;dx<=30;dx+=2){const c=cost(candidates[i],dx,dy);if(c<best.cost)best={dx,dy,cost:c};}
 const coarse={...best};for(let dy=coarse.dy-1;dy<=coarse.dy+1;dy++)for(let dx=coarse.dx-1;dx<=coarse.dx+1;dx++){const c=cost(candidates[i],dx,dy);if(c<best.cost)best={dx,dy,cost:c};}
 const src=aligned(candidates[i],best.dx,best.dy);await save(src,`${ROOT}/cels/aligned-${i}.png`);
 // Palette correction is measured on an unchanged, opaque shoulder region.
 const diffs=[[],[],[]];for(let y=260;y<335;y++)for(let x=240;x<310;x++){const k=(y*W+x)*4;if(src[k+3]>240&&master[k+3]>240)for(let c=0;c<3;c++)diffs[c].push(master[k+c]-src[k+c]);}
 const correction=diffs.map(v=>v.sort((a,b)=>a-b)[Math.floor(v.length/2)]||0);
 if(correction.some(v=>Math.abs(v)>15))throw new Error(`Pose ${i}: excessive color correction ${correction}`);
 const dst=Buffer.from(master);let preserved=0;
 for(let k=0;k<dst.length;k+=4){const m=mask[k+3]/255;if(!m){preserved++;continue;}const sa=src[k+3]/255,ma=master[k+3]/255,alpha=ma*(1-m)+sa*m;for(let c=0;c<3;c++){const corrected=Math.max(0,Math.min(255,src[k+c]+correction[c]));dst[k+c]=alpha?Math.round((master[k+c]*ma*(1-m)+corrected*sa*m)/alpha):0;}dst[k+3]=Math.round(alpha*255);}
 // Remove detached fragments of the other forepaw introduced by the local patch.
 const seen=new Uint8Array(W*H),groups=[];for(let seed=0;seed<W*H;seed++){if(seen[seed]||dst[seed*4+3]<16)continue;const group=[seed];seen[seed]=1;for(let n=0;n<group.length;n++){const q=group[n];for(const j of [q%W?q-1:-1,q%W<W-1?q+1:-1,q-W,q+W])if(j>=0&&j<W*H&&!seen[j]&&dst[j*4+3]>=16){seen[j]=1;group.push(j);}}groups.push(group);}
 groups.sort((a,b)=>b.length-a.length);for(const group of groups.slice(1))for(const j of group)if(mask[j*4+3])dst[j*4+3]=0;
 await save(dst,`${ROOT}/cels/locked-${i}.png`);records.push({id:i,...best,correction,unchangedPixels:preserved});
}
// Isolate the existing adult along its visible silhouette; do not regenerate it.
const adultMask=Buffer.from(`<svg width="1672" height="941"><path d="M0 0 H1170 V423 L1080 465 L1054 551 L1083 620 L1127 661 L1174 700 L1204 726 L1214 747 L1208 762 L1185 777 L1100 800 H0 Z" fill="white"/></svg>`);
await sharp('assets/source/settle-e.png').composite([{input:adultMask,blend:'dest-in'}]).png().toFile(`${ROOT}/cels/adult.png`);
await fs.writeFile(`${ROOT}/preparation.json`,JSON.stringify({source:'source/keyposes.png',width:W,height:H,records,mask:'acting foreleg only; all pixels outside mask copied from pose 0'},null,2));
const tiles=[];for(let i=0;i<candidates.length;i++){const p=await sharp(`${ROOT}/cels/locked-${i}.png`).flatten({background:'#eae4d7'}).resize(384,384).toBuffer();tiles.push({input:p,left:i%3*384,top:Math.floor(i/3)*420});const label=Buffer.from(`<svg width="384" height="36"><text x="18" y="26" font-family="Arial" font-size="18">Pose ${i}</text></svg>`);tiles.push({input:label,left:i%3*384,top:Math.floor(i/3)*420+384});}
await sharp({create:{width:1152,height:1680,channels:3,background:'#eae4d7'}}).composite(tiles).png().toFile('review/paw-touch/locked-keyposes.png');
console.log(records);
