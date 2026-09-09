import sharp from 'sharp';
import fs from 'node:fs/promises';
// Deterministic asset preparation for generated sheets whose checkerboard was baked in.
// Only neutral background connected to the sheet boundary is keyed; enclosed eye highlights survive.
for(const name of process.argv.slice(2)){
 const src=`assets/source/${name}.png`;
 const {data,info}=await sharp(src).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const {width:w,height:h}=info; const seen=new Uint8Array(w*h); const queue=new Int32Array(w*h);let a=0,b=0;
 const bg=i=>{const k=i*4;const r=data[k],g=data[k+1],bl=data[k+2];return Math.max(r,g,bl)-Math.min(r,g,bl)<24 && Math.min(r,g,bl)>85;};
 const add=i=>{if(i>=0&&i<w*h&&!seen[i]&&bg(i)){seen[i]=1;queue[b++]=i;}};
 for(let x=0;x<w;x++){add(x);add((h-1)*w+x)}
 for(let y=0;y<h;y++){add(y*w);add(y*w+w-1)}
 while(a<b){const i=queue[a++];data[i*4+3]=0;if(i%w)add(i-1);if(i%w<w-1)add(i+1);add(i-w);add(i+w)}
 await fs.copyFile(src,`assets/source/${name}-opaque-original.png`);
 await sharp(data,{raw:info}).png().toFile(`assets/source/${name}-extracted.png`);
 await fs.copyFile(`assets/source/${name}-extracted.png`,src);
 console.log(name,`${(100*b/(w*h)).toFixed(1)}% transparent; original preserved`);
}
