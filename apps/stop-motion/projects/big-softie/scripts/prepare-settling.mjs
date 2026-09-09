import fs from 'node:fs/promises';
import sharp from 'sharp';
// Full-frame paired cels share a fixed ground line and adult body scale.
// Keep their canvas coordinates; bounding-box fitting would enlarge lying poses.
const ids=process.argv.slice(2);
const manifest=JSON.parse(await fs.readFile('assets/cels/manifest.json','utf8'));
for(const id of ids){
 const src=`assets/source/${id}.png`;
 const {data,info}=await sharp(src).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let clear=0;for(let i=3;i<data.length;i+=4)if(data[i]===0)clear++;
 if(clear/(info.width*info.height)<.2)throw new Error(`${id}: opaque background`);
 await fs.copyFile(src,`assets/cels/${id}.png`);
 manifest[id]={width:info.width,height:info.height,paired:true};
 console.log(id,info.width,info.height,'alpha clear',clear/(info.width*info.height));
}
await fs.writeFile('assets/cels/manifest.json',JSON.stringify(manifest,null,2));
