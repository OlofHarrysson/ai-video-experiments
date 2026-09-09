import fs from 'node:fs/promises';
import sharp from 'sharp';

const sequence=['000','001','mid01','002','003','b34','004','005','b56','006','007','009'];
const output='assets/dense-nuzzle/rife-input';
await fs.mkdir(output,{recursive:true});
const park=await sharp('assets/source/park.png').resize(1280,720).toBuffer();
for(const [i,id] of sequence.entries()){
 const cel=await sharp(`assets/dense-nuzzle/frames/${id}.png`).resize(1003,565).toBuffer();
 await sharp(park).composite([{input:cel,left:140,top:160}]).removeAlpha().png().toFile(`${output}/${String(i).padStart(6,'0')}.png`);
}
await fs.writeFile('assets/dense-nuzzle/sequence.json',JSON.stringify(sequence,null,2));
await fs.writeFile('assets/dense-nuzzle/rife-input-manifest.json',JSON.stringify({sequence,width:1280,height:720,sourceFps:6,multiplier:10,outputFps:60},null,2));
console.log('Prepared',sequence.length,'fixed-camera RGB anchors for 10x interpolation.');
